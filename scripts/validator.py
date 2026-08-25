"""Reject generated content that is empty, over-limit, secret-laden, or ungrounded."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

from .generate_architecture import looks_like_mermaid
from .security import contains_secret, looks_like_private_url
from .textutil import WORD_LIMITS, parse_frontmatter, word_count

REQUIRED_SECTIONS = {
    "eli15.md": [],
    "technical.md": [],
    "references.md": ["Used / Influenced This Project"],
}

FILE_REF_RE = re.compile(
    r"(?<!http://)(?<!https://)(?<!mailto:)(?:`|/)?((?:src|app|lib|backend|frontend|scripts|pkg|internal|cmd)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+)`?"
)
URL_RE = re.compile(r"https?://[^\s)\]>'\"<>]+")


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_bundle(
    files: dict[str, str],
    *,
    tree: list[str] | None = None,
    bootstrap: bool = False,
) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    tree_set = set(tree or [])

    required = ["metadata.json"]
    if bootstrap:
        required.extend(["eli15.md", "technical.md", "references.md", "architecture.mmd", "build-log.md"])
    for name in required:
        if name not in files:
            errors.append(f"missing required file {name}")

    if "metadata.json" in files:
        errors.extend(_validate_metadata(files["metadata.json"]))

    mapping = {
        "eli15.md": "eli15",
        "technical.md": "technical",
        "references.md": "references",
    }
    for filename, kind in mapping.items():
        if filename not in files:
            continue
        errors.extend(_validate_markdown(filename, files[filename], kind, tree_set))

    if "build-log.md" in files:
        errors.extend(_validate_build_log(files["build-log.md"]))

    if "architecture.mmd" in files:
        if not looks_like_mermaid(files["architecture.mmd"]):
            errors.append("architecture.mmd is not syntactically reasonable Mermaid")
        if contains_secret(files["architecture.mmd"]):
            errors.append("architecture.mmd contains secret-like content")

    if "evolution.md" in files:
        if contains_secret(files["evolution.md"]):
            errors.append("evolution.md contains secret-like content")
        meta, body = parse_frontmatter(files["evolution.md"])
        if not body.strip():
            errors.append("evolution.md is empty")

    return ValidationResult(ok=not errors, errors=errors, warnings=warnings)


def _validate_metadata(raw: str) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return [f"metadata.json is invalid JSON: {exc}"]
    for key in ("name", "slug", "repository", "status", "last_updated", "last_commit"):
        if not data.get(key):
            errors.append(f"metadata.json missing {key}")
    if "categories" in data and not isinstance(data["categories"], list):
        errors.append("metadata.json categories must be a list")
    return errors


def _validate_markdown(filename: str, raw: str, kind: str, tree: set[str]) -> list[str]:
    errors: list[str] = []
    try:
        meta, body = parse_frontmatter(raw)
    except Exception as exc:  # noqa: BLE001
        return [f"{filename} frontmatter is invalid: {exc}"]
    if not meta:
        errors.append(f"{filename} is missing YAML frontmatter")
    else:
        for key in ("generated_by", "generated_at", "source_repository", "source_commit", "project"):
            if key not in meta:
                errors.append(f"{filename} frontmatter missing {key}")
    if not body.strip():
        errors.append(f"{filename} is empty")
    if contains_secret(body) or contains_secret(raw):
        errors.append(f"{filename} contains secret-like content")
    count = word_count(raw)
    if count > WORD_LIMITS[kind]:
        errors.append(f"{filename} has {count} words; limit is {WORD_LIMITS[kind]}")
    for section in REQUIRED_SECTIONS.get(filename, []):
        if section.lower() not in body.lower():
            errors.append(f"{filename} missing required section: {section}")
    errors.extend(_validate_urls(filename, body))
    if tree:
        missing = _unknown_repo_files(body, tree)
        if missing:
            errors.append(f"{filename} references files not in the repository tree: {', '.join(missing[:8])}")
    return errors


def _validate_build_log(raw: str) -> list[str]:
    errors: list[str] = []
    meta, body = parse_frontmatter(raw)
    if not meta:
        errors.append("build-log.md is missing YAML frontmatter")
    if not body.strip():
        errors.append("build-log.md is empty")
    if contains_secret(raw):
        errors.append("build-log.md contains secret-like content")
    return errors


def _validate_urls(filename: str, body: str) -> list[str]:
    errors: list[str] = []
    for match in URL_RE.findall(body):
        url = match.rstrip(").,;\"'`")
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append(f"{filename} has invalid URL: {url}")
        elif looks_like_private_url(url):
            errors.append(f"{filename} has private URL: {url}")
    return errors


def _unknown_repo_files(body: str, tree: set[str]) -> list[str]:
    unknown: list[str] = []
    for match in FILE_REF_RE.findall(body):
        path = match.lstrip("/")
        if path not in tree and not any(entry.endswith(path) or entry == path for entry in tree):
            unknown.append(path)
    return unknown
