"""Classify a day's accumulated diffs before any expensive generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from pydantic import BaseModel, Field, ValidationError

from .filters import all_trivial
from .llm_client import LLMError, LLMProvider
from .repo_context import RepoContext

SCHEMA_PATH = Path(__file__).resolve().parent / "schemas" / "classification.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)

CATEGORIES = {
    "cosmetic",
    "documentation",
    "bugfix",
    "performance",
    "dependency",
    "new_feature",
    "architecture",
    "model_change",
    "data_change",
    "deployment",
    "research",
    "refactor",
    "other",
}

RESEARCH_CATEGORIES = {"research", "model_change", "architecture", "new_feature"}

SYSTEM = """You classify software repository changes for Orpheon, an engineering journal.
Return JSON only. Be conservative: do not mark documentation for update unless the change
actually affects how the project should be explained.
Never invent files, APIs, papers, metrics, or users.
Human metadata in .orpheon.yml is authoritative.
"""

PROMPT = """Classify the following repository changes.

Allowed categories: {categories}

Importance: trivial | minor | meaningful | major

documentation_updates flags:
- eli15: product purpose/audience changed
- technical: internals, APIs, data flow, setup changed
- references: new papers, algorithms, libraries, or research concepts
- architecture: components or data flow changed
- build_log: anything non-cosmetic worth recording
- evolution: only for a major architectural transition

If importance is trivial, set every documentation_updates flag to false.

Changes to classify:
{bundle}
"""


class ChangeItem(BaseModel):
    type: str
    importance: str
    summary: str


class DocumentationUpdates(BaseModel):
    eli15: bool = False
    technical: bool = False
    references: bool = False
    architecture: bool = False
    build_log: bool = False
    evolution: bool = False


class Classification(BaseModel):
    summary: str
    importance: str
    categories: list[str] = Field(default_factory=list)
    documentation_updates: DocumentationUpdates
    major_evolution: bool = False
    changes: list[ChangeItem] = Field(default_factory=list)

    @property
    def needs_generation(self) -> bool:
        updates = self.documentation_updates
        return any(
            [
                updates.eli15,
                updates.technical,
                updates.references,
                updates.architecture,
                updates.build_log,
                updates.evolution,
                self.major_evolution,
            ]
        )

    @property
    def needs_research(self) -> bool:
        if not self.needs_generation:
            return False
        if not self.documentation_updates.references:
            return False
        return any(cat in RESEARCH_CATEGORIES for cat in self.categories)


def trivial_classification(reason: str) -> Classification:
    return Classification(
        summary=reason,
        importance="trivial",
        categories=["cosmetic"],
        documentation_updates=DocumentationUpdates(),
        major_evolution=False,
        changes=[],
    )


def bootstrap_classification() -> Classification:
    return Classification(
        summary="Repository imported into Orpheon; generate the initial journal.",
        importance="major",
        categories=["other"],
        documentation_updates=DocumentationUpdates(
            eli15=True,
            technical=True,
            references=True,
            architecture=True,
            build_log=True,
            evolution=False,
        ),
        major_evolution=False,
        changes=[
            ChangeItem(
                type="other",
                importance="major",
                summary="Initial import into Orpheon",
            )
        ],
    )


def validate_payload(payload: dict[str, Any]) -> Classification:
    errors = sorted(VALIDATOR.iter_errors(payload), key=lambda e: list(e.path))
    if errors:
        messages = "; ".join(error.message for error in errors[:6])
        raise LLMError(f"Classification failed schema validation: {messages}")
    try:
        model = Classification.model_validate(payload)
    except ValidationError as exc:
        raise LLMError(str(exc)) from exc
    model.categories = [c for c in model.categories if c in CATEGORIES]
    if model.importance == "trivial":
        model.documentation_updates = DocumentationUpdates()
        model.major_evolution = False
    if model.major_evolution:
        model.documentation_updates.evolution = True
        model.documentation_updates.architecture = True
        model.documentation_updates.technical = True
        model.documentation_updates.build_log = True
    return model


def classify(context: RepoContext, llm: LLMProvider) -> Classification:
    if context.bootstrap:
        return bootstrap_classification()
    if all_trivial(context.changed_files, context.extra_ignore):
        return trivial_classification("All changed files are ignored or cosmetic.")
    prompt = PROMPT.format(categories=", ".join(sorted(CATEGORIES)), bundle=context.to_prompt_bundle(include_docs=False))
    payload = llm.generate_structured(prompt, system=SYSTEM, max_tokens=1200)
    return validate_payload(payload)
