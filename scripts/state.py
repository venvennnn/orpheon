"""SHA tracking for processed repositories."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import STATE_FILE


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load_state(path: Path = STATE_FILE) -> dict[str, Any]:
    if not path.exists():
        return {"repositories": {}}
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    data.setdefault("repositories", {})
    return data


def save_state(state: dict[str, Any], path: Path = STATE_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(state, indent=2, ensure_ascii=False) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == serialized:
        return
    path.write_text(serialized, encoding="utf-8")


def last_processed_sha(state: dict[str, Any], repository: str) -> str | None:
    record = state.get("repositories", {}).get(repository) or {}
    sha = record.get("last_processed_sha")
    return str(sha) if sha else None


def update_processed(
    state: dict[str, Any],
    repository: str,
    sha: str,
    processed_at: str | None = None,
) -> None:
    repos = state.setdefault("repositories", {})
    repos[repository] = {
        "last_processed_sha": sha,
        "last_processed_at": processed_at or _now_iso(),
    }
