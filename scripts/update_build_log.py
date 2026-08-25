"""Append-only build history. Never rewrite previous entries."""

from __future__ import annotations

import re

from .textutil import WORD_LIMITS, today_long, word_count

IMPORT_ENTRY = """{date}

Project imported into Orpheon

The first journal entry records that this repository is now tracked.
Future runs will append real engineering notes from git history when you ask Orpheon to update.
Orpheon does not invent a backdated log from older commits.
"""

ENTRY_PROMPT_HINTS = """Write one build-history entry for today's accumulated commits.
Max {limit} words.
Use this shape:

{date}

Added:
- ...

Changed:
- ...

Fixed:
- ...

Why it matters:
...

Omit empty sections. Mention source commit SHAs when useful (short form).
Do not rewrite or mention older journal entries.
Do not invent metrics, users, or files.
Only describe what the diff and commit messages support.
"""


def append_entry(existing: str, entry: str) -> str:
    existing = existing.rstrip()
    entry = entry.strip()
    if not entry:
        raise ValueError("Refusing to append an empty build-log entry")
    if existing:
        return existing + "\n\n" + entry + "\n"
    return entry + "\n"


def import_entry(date: str | None = None) -> str:
    return IMPORT_ENTRY.format(date=date or today_long()).strip()


def enforce_entry_limit(entry: str) -> str:
    if word_count(entry) <= WORD_LIMITS["build_log_entry"]:
        return entry.strip()
    # Keep the date heading and trim from the end.
    lines = entry.strip().splitlines()
    kept: list[str] = []
    for line in lines:
        candidate = "\n".join(kept + [line])
        if word_count(candidate) > WORD_LIMITS["build_log_entry"] and kept:
            break
        kept.append(line)
    return "\n".join(kept).strip()


def parse_entries(text: str) -> list[str]:
    body = re.sub(r"^---.*?---\s*", "", text, count=1, flags=re.DOTALL).strip()
    if not body:
        return []
    chunks = re.split(r"\n(?=\d{1,2} [A-Z][a-z]+ \d{4}\n)", body)
    return [chunk.strip() for chunk in chunks if chunk.strip()]
