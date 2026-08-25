"""Ignore rules, filename filters, and cheap pre-LLM triage."""

from __future__ import annotations

import fnmatch
from pathlib import PurePosixPath

DEFAULT_IGNORE = [
    "*.csv",
    "*.parquet",
    "*.pkl",
    "*.pickle",
    "*.bin",
    "*.npy",
    "*.npz",
    "*.lock",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Cargo.lock",
    "node_modules/**",
    ".venv/**",
    "venv/**",
    "outputs/**",
    "output/**",
    "data/**",
    "datasets/**",
    "dist/**",
    "build/**",
    ".next/**",
    "coverage/**",
    "__pycache__/**",
    ".git/**",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.webp",
    "*.ico",
    "*.mp3",
    "*.mp4",
    "*.wav",
    "*.woff",
    "*.woff2",
    "*.ttf",
    "*.otf",
    "*.pdf",
    "*.zip",
    "*.gz",
    "*.tar",
    "*.7z",
    "*.wasm",
    "*.so",
    "*.dylib",
    "*.exe",
    "*.dll",
]

TRIVIAL_ONLY_PATTERNS = [
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
    ".prettierrc",
    ".prettierrc.*",
    ".prettierignore",
    ".eslintrc",
    ".eslintrc.*",
    "eslint.config.*",
    ".nvmrc",
    ".python-version",
    "*.map",
    "LICENSE",
    "LICENSE.*",
]

CONTEXT_FILENAMES = {
    "readme.md",
    "readme",
    ".orpheon.yml",
    ".orpheon.yaml",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "cargo.toml",
    "go.mod",
    "composer.json",
    "gemfile",
    "pipfile",
    "environment.yml",
    "decisions.md",
    "architecture.md",
}

MAX_DIFF_CHARS = 80_000
MAX_FILE_CHARS = 12_000
MAX_FILES_IN_DIFF = 40
MAX_TREE_ENTRIES = 400


def normalize_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.lstrip("/")


def matches_any(path: str, patterns: list[str]) -> bool:
    normalized = normalize_path(path)
    name = PurePosixPath(normalized).name
    for pattern in patterns:
        if fnmatch.fnmatch(normalized, pattern) or fnmatch.fnmatch(name, pattern):
            return True
        if pattern.endswith("/**") and normalized.startswith(pattern[:-3]):
            return True
    return False


def should_ignore(path: str, extra: list[str] | None = None) -> bool:
    from .security import is_secret_path

    if is_secret_path(path):
        return True
    patterns = list(DEFAULT_IGNORE)
    if extra:
        patterns.extend(extra)
    return matches_any(path, patterns)


def is_trivial_path(path: str) -> bool:
    return matches_any(path, TRIVIAL_ONLY_PATTERNS) or should_ignore(path)


def remaining_after_filter(paths: list[str], extra_ignore: list[str] | None = None) -> list[str]:
    return [path for path in paths if not should_ignore(path, extra_ignore)]


def all_trivial(paths: list[str], extra_ignore: list[str] | None = None) -> bool:
    remaining = remaining_after_filter(paths, extra_ignore)
    if not remaining:
        return True
    return all(matches_any(path, TRIVIAL_ONLY_PATTERNS) for path in remaining)


def is_context_file(path: str) -> bool:
    name = PurePosixPath(path).name.lower()
    return name in CONTEXT_FILENAMES or name.startswith("readme")


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n\n[truncated after {limit} characters]"
