"""Shared filesystem locations for the Orpheon pipeline."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
STATE_DIR = ROOT / "state"
PROJECTS_CONFIG = CONFIG_DIR / "projects.yml"
SITE_CONFIG = CONFIG_DIR / "site.yml"
STATE_FILE = STATE_DIR / "repositories.json"
RESEARCH_CACHE_FILE = STATE_DIR / "research-cache.json"
CONTENT_DIR = ROOT / "src" / "content" / "projects"
