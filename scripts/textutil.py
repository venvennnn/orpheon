"""Word counting, frontmatter helpers, and timezone dates."""

from __future__ import annotations

import re
from datetime import datetime
from zoneinfo import ZoneInfo

import yaml

WORD_LIMITS = {
    "eli15": 700,
    "technical": 1000,
    "references": 900,
    "build_log_entry": 250,
}

WORD_MINIMA = {
    "eli15": 350,
    "technical": 500,
    "references": 250,
}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
KOLKATA = ZoneInfo("Asia/Kolkata")


def word_count(text: str) -> int:
    body = strip_frontmatter(text)
    body = re.sub(r"```.*?```", " ", body, flags=re.DOTALL)
    body = re.sub(r"`[^`]+`", " ", body)
    body = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    body = re.sub(r"[#>*_\-|]", " ", body)
    words = re.findall(r"\b[\w']+\b", body)
    return len(words)


def strip_frontmatter(text: str) -> str:
    match = FRONTMATTER_RE.match(text)
    if match:
        return text[match.end() :].strip()
    return text.strip()


def parse_frontmatter(text: str) -> tuple[dict, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text.strip()
    data = yaml.safe_load(match.group(1)) or {}
    if not isinstance(data, dict):
        data = {}
    return data, text[match.end() :].lstrip()


def with_frontmatter(meta: dict, body: str) -> str:
    dumped = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{dumped}\n---\n\n{body.strip()}\n"


def today_kolkata() -> datetime:
    return datetime.now(KOLKATA)


def today_iso() -> str:
    return today_kolkata().date().isoformat()


def today_long() -> str:
    return today_kolkata().strftime("%d %B %Y").lstrip("0")


def within_limit(kind: str, text: str) -> bool:
    return word_count(text) <= WORD_LIMITS[kind]
