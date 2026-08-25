from __future__ import annotations

from scripts.detect_changes import decide
from scripts.orchestrator import process_project
from scripts.config import ProjectConfig
from scripts.llm_client import MockProvider


class BoomLLM(MockProvider):
    def generate(self, prompt: str, *, system: str | None = None, max_tokens: int = 4000) -> str:
        raise AssertionError("LLM must not be called for an unchanged repository")

    def generate_structured(self, prompt: str, *, system: str | None = None, max_tokens: int = 4000):
        raise AssertionError("LLM must not be called for an unchanged repository")


class FakeGitHub:
    def __init__(self, sha: str) -> None:
        self.sha = sha
        self.compare_called = False

    def head_sha(self, repository: str) -> str:
        return self.sha

    def snapshot(self, repository: str, sha: str | None = None):
        raise AssertionError("snapshot must not run when HEAD is unchanged")

    def compare(self, repository: str, base: str, head: str):
        self.compare_called = True
        raise AssertionError("compare must not run when HEAD is unchanged")


def test_unchanged_repo_skips_github_diff_and_llm():
    project = ProjectConfig(repository="venvennnn/aftermath", slug="aftermath", enabled=True)
    state = {
        "repositories": {
            "venvennnn/aftermath": {
                "last_processed_sha": "abc123",
                "last_processed_at": "2026-08-25T23:30:00+05:30",
            }
        }
    }
    outcome = process_project(
        project,
        client=FakeGitHub("abc123"),  # type: ignore[arg-type]
        llm=BoomLLM(),
        state=state,
    )
    assert outcome.status == "no changes"
    assert decide(project.repository, "abc123", "abc123").skip is True
