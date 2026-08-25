"""GitHub REST client. Reads public (and optionally private) repositories."""

from __future__ import annotations

import base64
import os
import time
from dataclasses import dataclass, field
from typing import Any

import requests

from .filters import MAX_TREE_ENTRIES, should_ignore, truncate
from .security import is_secret_path, sanitize_text


class GitHubError(RuntimeError):
    pass


@dataclass
class ChangedFile:
    filename: str
    status: str
    patch: str
    previous_filename: str | None = None


@dataclass
class CompareResult:
    base_sha: str
    head_sha: str
    ahead_by: int
    commits: list[dict[str, Any]]
    files: list[ChangedFile]
    truncated: bool = False


@dataclass
class RepoSnapshot:
    full_name: str
    default_branch: str
    sha: str
    description: str | None
    html_url: str
    homepage: str | None
    tree: list[str] = field(default_factory=list)


class GitHubClient:
    def __init__(
        self,
        token: str | None = None,
        api_url: str | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.token = token or os.environ.get("ORPHEON_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
        self.api_url = (api_url or os.environ.get("GITHUB_API_URL") or "https://api.github.com").rstrip("/")
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "orpheon-journal",
            }
        )
        if self.token:
            self.session.headers["Authorization"] = f"Bearer {self.token}"

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = path if path.startswith("http") else f"{self.api_url}{path}"
        last_error: Exception | None = None
        for attempt in range(4):
            try:
                response = self.session.request(method, url, timeout=60, **kwargs)
            except requests.RequestException as exc:
                last_error = exc
                time.sleep(2**attempt)
                continue
            if response.status_code in {502, 503, 504, 429}:
                time.sleep(2**attempt)
                last_error = GitHubError(f"{response.status_code} {response.text[:200]}")
                continue
            if response.status_code >= 400:
                raise GitHubError(f"GitHub {response.status_code} for {path}: {response.text[:400]}")
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        raise GitHubError(str(last_error) if last_error else f"request failed: {path}")

    def repo(self, repository: str) -> dict[str, Any]:
        return self._request("GET", f"/repos/{repository}")

    def head_sha(self, repository: str, ref: str | None = None) -> str:
        info = self.repo(repository)
        branch = ref or info.get("default_branch") or "main"
        data = self._request("GET", f"/repos/{repository}/commits/{branch}")
        return data["sha"]

    def snapshot(self, repository: str, sha: str | None = None) -> RepoSnapshot:
        info = self.repo(repository)
        commit_sha = sha or self.head_sha(repository, info.get("default_branch"))
        tree = self.git_tree(repository, commit_sha)
        return RepoSnapshot(
            full_name=info["full_name"],
            default_branch=info.get("default_branch") or "main",
            sha=commit_sha,
            description=info.get("description"),
            html_url=info.get("html_url") or f"https://github.com/{repository}",
            homepage=info.get("homepage"),
            tree=tree,
        )

    def git_tree(self, repository: str, sha: str) -> list[str]:
        data = self._request("GET", f"/repos/{repository}/git/trees/{sha}", params={"recursive": "1"})
        paths: list[str] = []
        for item in data.get("tree", []):
            if item.get("type") != "blob":
                continue
            path = item.get("path") or ""
            if should_ignore(path) or is_secret_path(path):
                continue
            paths.append(path)
            if len(paths) >= MAX_TREE_ENTRIES:
                break
        return paths

    def file_text(self, repository: str, path: str, ref: str) -> str | None:
        if should_ignore(path) or is_secret_path(path):
            return None
        try:
            data = self._request("GET", f"/repos/{repository}/contents/{path}", params={"ref": ref})
        except GitHubError:
            return None
        if not isinstance(data, dict) or data.get("type") != "file":
            return None
        if data.get("encoding") == "base64" and data.get("content"):
            raw = base64.b64decode(data["content"])
            if b"\x00" in raw:
                return None
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                return None
            return sanitize_text(truncate(text, 20_000))
        return None

    def compare(self, repository: str, base: str, head: str) -> CompareResult:
        data = self._request("GET", f"/repos/{repository}/compare/{base}...{head}")
        files: list[ChangedFile] = []
        raw_files = data.get("files") or []
        for item in raw_files:
            filename = item.get("filename") or ""
            if should_ignore(filename) or is_secret_path(filename):
                continue
            patch = sanitize_text(item.get("patch") or "")
            files.append(
                ChangedFile(
                    filename=filename,
                    status=item.get("status") or "modified",
                    patch=truncate(patch, 16_000),
                    previous_filename=item.get("previous_filename"),
                )
            )
        commits = []
        for commit in data.get("commits") or []:
            message = (commit.get("commit") or {}).get("message") or ""
            commits.append(
                {
                    "sha": commit.get("sha"),
                    "message": sanitize_text(message),
                    "author": ((commit.get("commit") or {}).get("author") or {}).get("name"),
                    "date": ((commit.get("commit") or {}).get("author") or {}).get("date"),
                }
            )
        return CompareResult(
            base_sha=base,
            head_sha=head,
            ahead_by=int(data.get("ahead_by") or 0),
            commits=commits,
            files=files,
            truncated=len(raw_files) >= 300,
        )

    def recent_commits(self, repository: str, sha: str, limit: int = 20) -> list[dict[str, Any]]:
        data = self._request(
            "GET",
            f"/repos/{repository}/commits",
            params={"sha": sha, "per_page": limit},
        )
        out = []
        for commit in data or []:
            message = (commit.get("commit") or {}).get("message") or ""
            out.append(
                {
                    "sha": commit.get("sha"),
                    "message": sanitize_text(message),
                    "author": ((commit.get("commit") or {}).get("author") or {}).get("name"),
                    "date": ((commit.get("commit") or {}).get("author") or {}).get("date"),
                }
            )
        return out
