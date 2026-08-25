"""Generate or patch Orpheon documentation. Provenance is added in Python."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .classify_changes import Classification
from .generate_architecture import generate_architecture
from .llm_client import LLMError, LLMProvider
from .repo_context import RepoContext
from .textutil import (
    WORD_LIMITS,
    strip_frontmatter,
    today_iso,
    today_long,
    with_frontmatter,
    word_count,
)
from .update_build_log import ENTRY_PROMPT_HINTS, append_entry, enforce_entry_limit, import_entry

SYSTEM = """You write grounded engineering-journal documentation for Orpheon.

Rules:
- Distinguish repository facts from interpretation. Facts must be visible in the provided files, diffs, README, dependencies, or .orpheon.yml.
- .orpheon.yml is authoritative human metadata. Never contradict it.
- Never invent APIs, files, libraries, papers, benchmarks, dataset sizes, users, or business claims.
- Never include secrets, tokens, private URLs, or personal data.
- Do not use hype. Write like a careful lab notebook.
- Keep within the stated word limit.
- Use Markdown. Do not wrap the whole document in a code fence.
- Do not include YAML frontmatter; it is added later.
"""

ELI15_PROMPT = """Write the Explain Like I'm 15 page.

Target 400–700 words. Hard maximum {limit} words.
Cover: the problem, why it matters, what the product does, what goes in, what comes out,
a simple example, an analogy if useful, and who might use it.
Avoid unnecessary jargon.

Existing page (revise only if the product purpose changed; otherwise rewrite from current evidence):
{existing}

Evidence:
{bundle}

Return JSON: {{"markdown": "..."}}
"""

TECHNICAL_PROMPT = """Write the Technical Deep Dive.

Target 700–1000 words. Hard maximum {limit} words.
Include sections that the evidence supports among:
problem statement, architecture, system components, data flow, models/algorithms,
APIs, storage, important libraries, design decisions, tradeoffs, use cases,
limitations, setup instructions, demo instructions.
Do not embed a Mermaid diagram; architecture is stored separately.
Only mention files and APIs that appear in the evidence.

Existing page:
{existing}

Evidence:
{bundle}

Return JSON: {{"markdown": "..."}}
"""

REFERENCES_PROMPT = """Write the References & Ideas page.

Hard maximum {limit} words.

Structure:
## Used / Influenced This Project
Only items explicitly present in README, .orpheon.yml, comments, citations, commit messages, or existing docs.
If none are explicit, say so honestly. Never fabricate influence.

## Related Reading Discovered by Orpheon
Use ONLY the supplied discovered items. Label this section exactly:
Related Reading Discovered by Orpheon
If the list is empty, omit the section rather than inventing sources.

Each reference needs title, link, type, a short explanation, and which part of the project it relates to.

Trusted human references from .orpheon.yml:
{human_refs}

Discovered by Orpheon (may be empty):
{discovered}

Existing page:
{existing}

Evidence:
{bundle}

Return JSON: {{"markdown": "..."}}
"""

EVOLUTION_PROMPT = """If and only if this is a major architectural transition, write one evolution entry.

Shape:

Evolution #{number}
{date}

FROM
...

TO
...

Why it changed
...

Only use components supported by the repository evidence.
If this is not a true architectural transition, return {{"skip": true}}.

Existing evolution log:
{existing}

Evidence:
{bundle}

Return JSON: {{"skip": false, "markdown": "..."}} or {{"skip": true}}
"""

SHORTEN_PROMPT = """The following Markdown exceeds {limit} words ({count} words).
Rewrite it so it is under {limit} words without adding new claims.
Return JSON: {{"markdown": "..."}}

Text:
{text}
"""

BUILD_PROMPT = ENTRY_PROMPT_HINTS + """

Evidence:
{bundle}

Return JSON: {{"markdown": "..."}}
"""


@dataclass
class GeneratedBundle:
    files: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


def provenance(context: RepoContext, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    project = (context.orpheon.get("project") or {}) if context.orpheon else {}
    name = project.get("name") or context.slug.replace("-", " ").title()
    meta = {
        "project": name,
        "generated_by": "orpheon",
        "generated_at": today_iso(),
        "source_repository": context.repository,
        "source_commit": context.sha,
    }
    if extra:
        meta.update(extra)
    return meta


def _markdown_from(llm: LLMProvider, prompt: str) -> str:
    payload = llm.generate_structured(prompt, system=SYSTEM, max_tokens=3500)
    markdown = payload.get("markdown")
    if not markdown or not str(markdown).strip():
        raise LLMError("Model returned empty markdown")
    return str(markdown).strip()


def _fit(llm: LLMProvider, kind: str, text: str) -> str:
    limit = WORD_LIMITS[kind]
    count = word_count(text)
    if count <= limit:
        return text.strip()
    shortened = _markdown_from(
        llm,
        SHORTEN_PROMPT.format(limit=limit, count=count, text=text),
    )
    if word_count(shortened) > limit:
        raise LLMError(f"{kind} still exceeds {limit} words after rewrite ({word_count(shortened)})")
    return shortened.strip()


def _name(context: RepoContext) -> str:
    project = context.orpheon.get("project") or {}
    return str(project.get("name") or context.slug.replace("-", " ").title())


def _categories(context: RepoContext) -> list[str]:
    raw = context.orpheon.get("category") or []
    if isinstance(raw, str):
        return [raw]
    return [str(item) for item in raw]


def _status(context: RepoContext) -> str:
    return str(context.orpheon.get("status") or "active")


def _tagline(context: RepoContext) -> str:
    project = context.orpheon.get("project") or {}
    tagline = project.get("tagline") or context.description or ""
    return str(tagline).strip()


def _demo(context: RepoContext) -> str | None:
    demo = context.orpheon.get("demo") or {}
    if isinstance(demo, dict) and demo.get("url"):
        return str(demo["url"])
    return context.homepage or None


def _count_references(markdown: str) -> int:
    return markdown.count("http://") + markdown.count("https://")


def generate_docs(
    context: RepoContext,
    classification: Classification,
    llm: LLMProvider,
    *,
    discovered: list[dict[str, Any]] | None = None,
) -> GeneratedBundle:
    updates = classification.documentation_updates
    existing = context.existing_docs
    bundle_out = GeneratedBundle()
    project_name = _name(context)

    if context.bootstrap or updates.eli15:
        body = _fit(
            llm,
            "eli15",
            _markdown_from(
                llm,
                ELI15_PROMPT.format(
                    limit=WORD_LIMITS["eli15"],
                    existing=strip_frontmatter(existing.get("eli15.md", "")) or "(none)",
                    bundle=context.to_prompt_bundle(),
                ),
            ),
        )
        bundle_out.files["eli15.md"] = with_frontmatter(provenance(context), body)

    if context.bootstrap or updates.technical:
        body = _fit(
            llm,
            "technical",
            _markdown_from(
                llm,
                TECHNICAL_PROMPT.format(
                    limit=WORD_LIMITS["technical"],
                    existing=strip_frontmatter(existing.get("technical.md", "")) or "(none)",
                    bundle=context.to_prompt_bundle(),
                ),
            ),
        )
        bundle_out.files["technical.md"] = with_frontmatter(provenance(context), body)

    if context.bootstrap or updates.references:
        body = _fit(
            llm,
            "references",
            _markdown_from(
                llm,
                REFERENCES_PROMPT.format(
                    limit=WORD_LIMITS["references"],
                    human_refs=context.orpheon.get("references") or "(none listed)",
                    discovered=discovered or [],
                    existing=strip_frontmatter(existing.get("references.md", "")) or "(none)",
                    bundle=context.to_prompt_bundle(include_diff=not context.bootstrap),
                ),
            ),
        )
        bundle_out.files["references.md"] = with_frontmatter(provenance(context), body)

    if context.bootstrap or updates.architecture:
        existing_mmd = existing.get("architecture.mmd", "")
        mermaid = generate_architecture(context, llm, existing_mmd)
        bundle_out.files["architecture.mmd"] = mermaid

    if context.bootstrap:
        entry = import_entry()
        previous = existing.get("build-log.md", "")
        bundle_out.files["build-log.md"] = with_frontmatter(
            provenance(context),
            append_entry(strip_frontmatter(previous), entry) if previous else entry,
        )
    elif updates.build_log:
        raw = _markdown_from(
            llm,
            BUILD_PROMPT.format(limit=WORD_LIMITS["build_log_entry"], date=today_long(), bundle=context.to_prompt_bundle(include_docs=False)),
        )
        entry = enforce_entry_limit(raw)
        previous = strip_frontmatter(existing.get("build-log.md", ""))
        bundle_out.files["build-log.md"] = with_frontmatter(provenance(context), append_entry(previous, entry))

    if classification.major_evolution or updates.evolution:
        payload = llm.generate_structured(
            EVOLUTION_PROMPT.format(
                number=_next_evolution_number(existing.get("evolution.md", "")),
                date=today_long(),
                existing=strip_frontmatter(existing.get("evolution.md", "")) or "(none)",
                bundle=context.to_prompt_bundle(),
            ),
            system=SYSTEM,
            max_tokens=1200,
        )
        if not payload.get("skip"):
            evo = str(payload.get("markdown") or "").strip()
            if evo:
                previous = strip_frontmatter(existing.get("evolution.md", ""))
                body = (previous + "\n\n" + evo).strip() if previous else evo
                bundle_out.files["evolution.md"] = with_frontmatter(provenance(context), body)

    references_md = bundle_out.files.get("references.md") or existing.get("references.md") or ""
    metadata = {
        "name": project_name,
        "slug": context.slug,
        "repository": context.repository,
        "status": _status(context),
        "categories": _categories(context),
        "tagline": _tagline(context),
        "description": str((context.orpheon.get("project") or {}).get("description") or context.description or ""),
        "demo": _demo(context),
        "last_updated": today_iso(),
        "last_commit": context.sha,
        "commit_count": max(context.ahead_by, len(context.commits), 0),
        "reference_count": _count_references(references_md),
        "github": context.html_url,
    }
    if not metadata["categories"]:
        metadata["categories"] = ["Unsorted"]
    # Preserve previous commit_count by adding ahead_by if we have existing metadata.
    previous_meta = existing.get("metadata.json")
    if previous_meta and not context.bootstrap:
        try:
            import json

            prev = json.loads(previous_meta)
            prior = int(prev.get("commit_count") or 0)
            metadata["commit_count"] = prior + max(context.ahead_by, 1)
        except (ValueError, TypeError):
            pass
    if context.bootstrap:
        metadata["commit_count"] = max(len(context.commits), 1)

    bundle_out.metadata = metadata
    bundle_out.files["metadata.json"] = _dump_json(metadata)
    return bundle_out


def _dump_json(data: dict[str, Any]) -> str:
    import json

    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def _next_evolution_number(existing: str) -> int:
    import re

    numbers = [int(n) for n in re.findall(r"Evolution #(\d+)", existing)]
    return (max(numbers) + 1) if numbers else 1
