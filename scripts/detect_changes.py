"""HEAD comparison — no LLM, no network beyond the caller."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChangeDecision:
    repository: str
    current_sha: str
    last_processed_sha: str | None
    bootstrap: bool
    skip: bool
    reason: str


def decide(repository: str, current_sha: str, last_sha: str | None) -> ChangeDecision:
    if not current_sha:
        return ChangeDecision(
            repository=repository,
            current_sha=current_sha,
            last_processed_sha=last_sha,
            bootstrap=False,
            skip=True,
            reason="missing current SHA",
        )
    if last_sha is None:
        return ChangeDecision(
            repository=repository,
            current_sha=current_sha,
            last_processed_sha=None,
            bootstrap=True,
            skip=False,
            reason="no last_processed_sha; bootstrap",
        )
    if last_sha == current_sha:
        return ChangeDecision(
            repository=repository,
            current_sha=current_sha,
            last_processed_sha=last_sha,
            bootstrap=False,
            skip=True,
            reason="HEAD identical to last_processed_sha",
        )
    return ChangeDecision(
        repository=repository,
        current_sha=current_sha,
        last_processed_sha=last_sha,
        bootstrap=False,
        skip=False,
        reason="HEAD moved; inspect diff",
    )
