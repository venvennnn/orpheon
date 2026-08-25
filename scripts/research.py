"""Optional related-reading discovery. Cached. Never implied as original sources."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .classify_changes import Classification
from .llm_client import LLMProvider
from .paths import RESEARCH_CACHE_FILE
from .repo_context import RepoContext
from .security import looks_like_private_url

ALLOWED_TYPES = {
    "research paper",
    "technical documentation",
    "algorithm",
    "framework",
    "dataset",
    "blog/article",
    "concept",
    "news/event",
}

SYSTEM = """You suggest related reading for a software project.
These are discoveries by Orpheon, NOT claims that the author used them.
Only suggest well-known, real resources you are confident exist.
Prefer official docs, canonical papers, and standard algorithms.
Return JSON.
"""

PROMPT = """Suggest up to 5 related readings for this project.
Do not repeat anything already listed as used/influenced.
Do not fabricate URLs. If unsure of a URL, omit the item.

Already known titles:
{known}

Project evidence:
{bundle}

Return JSON:
{{
  "items": [
    {{
      "title": "",
      "url": "https://...",
      "type": "research paper|technical documentation|algorithm|framework|dataset|blog/article|concept|news/event",
      "explanation": "one or two sentences",
      "relates_to": "which part of the project"
    }}
  ]
}}
"""


def load_cache(path: Path = RESEARCH_CACHE_FILE) -> dict[str, Any]:
    if not path.exists():
        return {"references": {}}
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    data.setdefault("references", {})
    return data


def save_cache(cache: dict[str, Any], path: Path = RESEARCH_CACHE_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _valid_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    if looks_like_private_url(url):
        return False
    return True


def discover(
    context: RepoContext,
    classification: Classification,
    llm: LLMProvider,
    cache: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not classification.needs_research:
        return []
    cache = cache if cache is not None else load_cache()
    existing = cache.get("references", {}).get(context.repository, [])
    known_titles = {str(item.get("title", "")).lower() for item in existing}
    used = context.orpheon.get("references") or []
    known_titles.update(str(item.get("title", "")).lower() for item in used if isinstance(item, dict))

    payload = llm.generate_structured(
        PROMPT.format(known="\n".join(sorted(t for t in known_titles if t)) or "(none)", bundle=context.to_prompt_bundle(include_diff=False)),
        system=SYSTEM,
        max_tokens=1500,
    )
    fresh: list[dict[str, Any]] = []
    for item in payload.get("items") or []:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        url = str(item.get("url") or "").strip()
        kind = str(item.get("type") or "concept").strip().lower()
        if not title or title.lower() in known_titles:
            continue
        if not _valid_url(url):
            continue
        if kind not in ALLOWED_TYPES:
            kind = "concept"
        record = {
            "title": title,
            "url": url,
            "type": kind,
            "explanation": str(item.get("explanation") or "").strip(),
            "relates_to": str(item.get("relates_to") or "").strip(),
        }
        fresh.append(record)
        known_titles.add(title.lower())

    merged = existing + fresh
    cache.setdefault("references", {})[context.repository] = merged
    save_cache(cache)
    return fresh
