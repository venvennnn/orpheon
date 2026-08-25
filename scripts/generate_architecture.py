"""Generate or refresh a Mermaid architecture diagram."""

from __future__ import annotations

import re

from .llm_client import LLMError, LLMProvider
from .repo_context import RepoContext

SYSTEM = """You write a single Mermaid flowchart for a software project.
Use only components that appear in the repository (source, docs, or .orpheon.yml).
Do not invent services, databases, or APIs.
Prefer `graph LR` or `flowchart TD`.
No styling, no classDef, no click handlers, no HTML.
Node labels must be short.
"""

PROMPT = """Create a Mermaid architecture diagram for this repository.

Existing diagram (may be empty):
{existing}

Repository evidence:
{bundle}

Return JSON: {{"mermaid": "graph LR\\n..."}}
"""

MERMAID_START = re.compile(
    r"^\s*(graph|flowchart|sequenceDiagram|classDiagram|stateDiagram|erDiagram|mindmap)\b",
    re.IGNORECASE,
)


def looks_like_mermaid(text: str) -> bool:
    body = text.strip()
    body = re.sub(r"^```(?:mermaid)?\s*", "", body)
    body = re.sub(r"\s*```$", "", body)
    return bool(MERMAID_START.search(body))


def normalize_mermaid(text: str) -> str:
    body = text.strip()
    body = re.sub(r"^```(?:mermaid)?\s*", "", body)
    body = re.sub(r"\s*```$", "", body).strip()
    if not looks_like_mermaid(body):
        raise LLMError("Architecture output is not valid Mermaid")
    opens = body.count("[") + body.count("{") + body.count("(")
    closes = body.count("]") + body.count("}") + body.count(")")
    if abs(opens - closes) > 2:
        raise LLMError("Mermaid brackets look unbalanced")
    return body + "\n"


def generate_architecture(context: RepoContext, llm: LLMProvider, existing: str = "") -> str:
    payload = llm.generate_structured(
        PROMPT.format(existing=existing or "(none)", bundle=context.to_prompt_bundle()),
        system=SYSTEM,
        max_tokens=1200,
    )
    mermaid = payload.get("mermaid") or payload.get("diagram") or ""
    return normalize_mermaid(str(mermaid))
