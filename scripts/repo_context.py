"""Collect bounded repository context for classification and generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .filters import (
    CONTEXT_FILENAMES,
    MAX_DIFF_CHARS,
    MAX_FILE_CHARS,
    MAX_FILES_IN_DIFF,
    is_context_file,
    remaining_after_filter,
    should_ignore,
    truncate,
)
from .github_client import CompareResult, GitHubClient, RepoSnapshot
from .paths import CONTENT_DIR
from .security import is_secret_path, sanitize_text
from .textutil import strip_frontmatter


@dataclass
class RepoContext:
    repository: str
    slug: str
    sha: str
    bootstrap: bool
    description: str | None
    homepage: str | None
    html_url: str
    tree: list[str]
    commit_messages: list[str]
    commits: list[dict[str, Any]]
    changed_files: list[str]
    diff: str
    files: dict[str, str] = field(default_factory=dict)
    orpheon: dict[str, Any] = field(default_factory=dict)
    existing_docs: dict[str, str] = field(default_factory=dict)
    extra_ignore: list[str] = field(default_factory=list)
    ahead_by: int = 0

    def to_prompt_bundle(self, *, include_diff: bool = True, include_docs: bool = True) -> str:
        parts = [
            f"Repository: {self.repository}",
            f"Commit: {self.sha}",
            f"Mode: {'bootstrap' if self.bootstrap else 'diff'}",
            f"GitHub: {self.html_url}",
        ]
        if self.description:
            parts.append(f"GitHub description: {self.description}")
        if self.homepage:
            parts.append(f"Homepage: {self.homepage}")
        if self.orpheon:
            parts.append("Trusted .orpheon.yml (authoritative, never override):\n" + yaml.safe_dump(self.orpheon, sort_keys=False))
        parts.append("Repository tree (filtered):\n" + "\n".join(self.tree[:300]))
        if self.commit_messages:
            parts.append("Commit messages:\n" + "\n---\n".join(self.commit_messages[:40]))
        if include_diff and self.diff:
            parts.append("Git diff:\n" + self.diff)
        if self.files:
            file_blob = []
            for path, content in self.files.items():
                file_blob.append(f"FILE {path}\n{content}")
            parts.append("Selected files:\n\n" + "\n\n".join(file_blob))
        if include_docs and self.existing_docs:
            docs = []
            for name, content in self.existing_docs.items():
                docs.append(f"EXISTING {name}\n{strip_frontmatter(content)[:8000]}")
            parts.append("Existing Orpheon documentation:\n\n" + "\n\n".join(docs))
        return sanitize_text("\n\n".join(parts))


def parse_orpheon_yml(text: str | None) -> dict[str, Any]:
    if not text:
        return {}
    try:
        data = yaml.safe_load(text) or {}
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def extra_ignore_from_orpheon(data: dict[str, Any]) -> list[str]:
    ignore = data.get("ignore") or []
    return [str(item) for item in ignore]


def load_existing_docs(slug: str) -> dict[str, str]:
    folder = CONTENT_DIR / slug
    if not folder.is_dir():
        return {}
    docs: dict[str, str] = {}
    for name in (
        "problem.md",
        "summary.md",
        "results.md",
        "examples.md",
        "build-log.md",
        "architecture.mmd",
        "metadata.json",
    ):
        path = folder / name
        if path.exists():
            docs[name] = path.read_text(encoding="utf-8")
    return docs


def _pick_bootstrap_files(tree: list[str]) -> list[str]:
    chosen: list[str] = []
    for path in tree:
        if is_context_file(path):
            chosen.append(path)
    sourcey = [p for p in tree if _looks_like_source(p) and p not in chosen]
    chosen.extend(sourcey[:18])
    return chosen[:30]


def _looks_like_source(path: str) -> bool:
    lowered = path.lower()
    if any(part in lowered.split("/") for part in ("test", "tests", "docs", "examples", "vendor")):
        return False
    return lowered.endswith(
        (".py", ".ts", ".tsx", ".js", ".go", ".rs", ".java", ".kt", ".swift", ".rb", ".cs")
    )


def _orpheon_path(tree: list[str]) -> str | None:
    for candidate in (".orpheon.yml", ".orpheon.yaml"):
        if candidate in tree:
            return candidate
    return None


def collect_bootstrap(client: GitHubClient, repository: str, slug: str, snapshot: RepoSnapshot) -> RepoContext:
    orpheon_file = _orpheon_path(snapshot.tree)
    orpheon_text = client.file_text(repository, orpheon_file, snapshot.sha) if orpheon_file else None
    orpheon = parse_orpheon_yml(orpheon_text)
    extra = extra_ignore_from_orpheon(orpheon)
    tree = [path for path in snapshot.tree if not should_ignore(path, extra)]
    files: dict[str, str] = {}
    if orpheon_file and orpheon_text:
        files[orpheon_file] = orpheon_text
    for path in _pick_bootstrap_files(tree):
        if path in files:
            continue
        text = client.file_text(repository, path, snapshot.sha)
        if text:
            files[path] = truncate(text, MAX_FILE_CHARS)
    commits = client.recent_commits(repository, snapshot.sha, limit=20)
    return RepoContext(
        repository=repository,
        slug=slug,
        sha=snapshot.sha,
        bootstrap=True,
        description=snapshot.description,
        homepage=snapshot.homepage,
        html_url=snapshot.html_url,
        tree=tree,
        commit_messages=[c["message"] for c in commits if c.get("message")],
        commits=commits,
        changed_files=[],
        diff="",
        files=files,
        orpheon=orpheon,
        existing_docs=load_existing_docs(slug),
        extra_ignore=extra,
    )


def collect_diff_context(
    client: GitHubClient,
    repository: str,
    slug: str,
    snapshot: RepoSnapshot,
    compare: CompareResult,
) -> RepoContext:
    orpheon_file = _orpheon_path(snapshot.tree)
    orpheon_text = client.file_text(repository, orpheon_file, snapshot.sha) if orpheon_file else None
    orpheon = parse_orpheon_yml(orpheon_text)
    extra = extra_ignore_from_orpheon(orpheon)

    changed = remaining_after_filter([f.filename for f in compare.files], extra)
    files_meta = [f for f in compare.files if f.filename in set(changed)][:MAX_FILES_IN_DIFF]

    diff_parts = []
    for item in files_meta:
        header = f"--- {item.filename} ({item.status})"
        diff_parts.append(header + "\n" + (item.patch or ""))
    diff = truncate("\n\n".join(diff_parts), MAX_DIFF_CHARS)

    files: dict[str, str] = {}
    if orpheon_file and orpheon_text:
        files[orpheon_file] = orpheon_text
    for filename in list(CONTEXT_FILENAMES):
        match = next((p for p in snapshot.tree if p.lower().endswith(filename) or p.lower() == filename), None)
        if match and match not in files:
            text = client.file_text(repository, match, snapshot.sha)
            if text:
                files[match] = truncate(text, MAX_FILE_CHARS)

    for item in files_meta[:12]:
        if item.filename in files or should_ignore(item.filename, extra) or is_secret_path(item.filename):
            continue
        if item.status == "removed":
            continue
        text = client.file_text(repository, item.filename, snapshot.sha)
        if text:
            files[item.filename] = truncate(text, MAX_FILE_CHARS)

    return RepoContext(
        repository=repository,
        slug=slug,
        sha=snapshot.sha,
        bootstrap=False,
        description=snapshot.description,
        homepage=snapshot.homepage,
        html_url=snapshot.html_url,
        tree=[path for path in snapshot.tree if not should_ignore(path, extra)],
        commit_messages=[c["message"] for c in compare.commits if c.get("message")],
        commits=compare.commits,
        changed_files=changed,
        diff=diff,
        files=files,
        orpheon=orpheon,
        existing_docs=load_existing_docs(slug),
        extra_ignore=extra,
        ahead_by=compare.ahead_by,
    )


def project_dir(slug: str) -> Path:
    return CONTENT_DIR / slug
