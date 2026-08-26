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

PROBLEM_PROMPT = """Write the Problem section for this project page.

Target 120–280 words. Hard maximum {limit} words.
State the gap the repository is attacking. Do not pitch. Do not invent users or metrics.

Existing page:
{existing}

Evidence:
{bundle}

Return JSON: {{"markdown": "..."}}
"""

SUMMARY_PROMPT = """Write the Summary section for this project page.

Target 120–280 words. Hard maximum {limit} words.
Start with one or two paragraphs of what the product is.
Then add exactly three Markdown h3 takeaways (### Heading) with one or two sentences each.

Existing page:
{existing}

Evidence:
{bundle}

Return JSON: {{"markdown": "..."}}
"""

RESULTS_PROMPT = """Write the Results section for this project page.

Target 150–350 words. Hard maximum {limit} words.
Cover only what the evidence supports: what was built, how it is evaluated or demoed, and honest limits.
Do not invent benchmarks, users, or dataset sizes.
Do not embed a Mermaid diagram.

Existing page:
{existing}

Evidence:
{bundle}

Return JSON: {{"markdown": "..."}}
"""

EXAMPLES_PROMPT = """Write the Examples section for this project page.

Target 80–250 words. Hard maximum {limit} words.
Give one or two concrete use cases or walkthroughs supported by the repository.
Do not invent customers, logos, or unpublished numbers.

Existing page:
{existing}

Evidence:
{bundle}

Return JSON: {{"markdown": "..."}}
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


def generate_docs(
    context: RepoContext,
    classification: Classification,
    llm: LLMProvider,
    *,
    discovered: list[dict[str, Any]] | None = None,
) -> GeneratedBundle:
    del discovered
    updates = classification.documentation_updates
    existing = context.existing_docs
    bundle_out = GeneratedBundle()
    project_name = _name(context)

    sections = (
        ("problem", "problem.md", PROBLEM_PROMPT),
        ("summary", "summary.md", SUMMARY_PROMPT),
        ("results", "results.md", RESULTS_PROMPT),
        ("examples", "examples.md", EXAMPLES_PROMPT),
    )
    for kind, filename, prompt in sections:
        if context.bootstrap or getattr(updates, kind):
            body = _fit(
                llm,
                kind,
                _markdown_from(
                    llm,
                    prompt.format(
                        limit=WORD_LIMITS[kind],
                        existing=strip_frontmatter(existing.get(filename, "")) or "(none)",
                        bundle=context.to_prompt_bundle(),
                    ),
                ),
            )
            bundle_out.files[filename] = with_frontmatter(provenance(context), body)

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
        "github": context.html_url,
    }
    if not metadata["categories"]:
        metadata["categories"] = ["Unsorted"]
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
