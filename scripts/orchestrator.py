"""Nightly Orpheon orchestrator.

Deterministic change detection first. LLM only after a meaningful diff.
One broken repository must not stop the others.
"""

from __future__ import annotations

import argparse
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path

from .classify_changes import Classification, classify
from .config import ProjectConfig, enabled_projects, load_site_config
from .detect_changes import decide
from .generate_docs import generate_docs
from .github_client import GitHubClient, GitHubError
from .llm_client import LLMError, LLMProvider, get_provider
from .paths import CONTENT_DIR
from .repo_context import collect_bootstrap, collect_diff_context
from .research import discover, load_cache
from .state import last_processed_sha, load_state, save_state, update_processed
from .validator import validate_bundle

OK = "processed"
SKIP = "no changes"
TRIVIAL = "trivial; state only"
FAIL = "failed"


@dataclass
class ProjectOutcome:
    repository: str
    slug: str
    status: str
    detail: str
    wrote: bool = False


def process_project(
    project: ProjectConfig,
    *,
    client: GitHubClient,
    llm: LLMProvider,
    state: dict,
    dry_run: bool = False,
) -> ProjectOutcome:
    try:
        current_sha = client.head_sha(project.repository)
    except GitHubError as exc:
        return ProjectOutcome(project.repository, project.slug, FAIL, f"HEAD lookup failed: {exc}")

    last_sha = last_processed_sha(state, project.repository)
    decision = decide(project.repository, current_sha, last_sha)
    if decision.skip:
        return ProjectOutcome(project.repository, project.slug, SKIP, decision.reason)

    try:
        snapshot = client.snapshot(project.repository, current_sha)
        if decision.bootstrap:
            context = collect_bootstrap(client, project.repository, project.slug, snapshot)
        else:
            compare = client.compare(project.repository, last_sha or current_sha, current_sha)
            context = collect_diff_context(client, project.repository, project.slug, snapshot, compare)
        classification: Classification = classify(context, llm)
    except (GitHubError, LLMError, Exception) as exc:  # noqa: BLE001
        return ProjectOutcome(project.repository, project.slug, FAIL, f"analysis failed: {exc}")

    if not decision.bootstrap and not classification.needs_generation:
        if not dry_run:
            update_processed(state, project.repository, current_sha)
        return ProjectOutcome(project.repository, project.slug, TRIVIAL, classification.summary)

    try:
        discovered = discover(context, classification, llm)
        bundle = generate_docs(context, classification, llm, discovered=discovered)
        result = validate_bundle(bundle.files, tree=context.tree, bootstrap=context.bootstrap)
        if not result.ok:
            return ProjectOutcome(
                project.repository,
                project.slug,
                FAIL,
                "validation failed: " + "; ".join(result.errors),
            )
        if dry_run:
            return ProjectOutcome(
                project.repository,
                project.slug,
                OK,
                f"dry-run would write {', '.join(sorted(bundle.files))}",
                wrote=False,
            )
        _write_bundle(project.slug, bundle.files)
        update_processed(state, project.repository, current_sha)
        return ProjectOutcome(
            project.repository,
            project.slug,
            OK,
            classification.summary,
            wrote=True,
        )
    except (LLMError, Exception) as exc:  # noqa: BLE001
        return ProjectOutcome(project.repository, project.slug, FAIL, f"generation failed: {exc}")


def _write_bundle(slug: str, files: dict[str, str]) -> None:
    folder = CONTENT_DIR / slug
    folder.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        path = folder / name
        path.write_text(content if content.endswith("\n") else content + "\n", encoding="utf-8")


def run(
    *,
    only: str | None = None,
    dry_run: bool = False,
    client: GitHubClient | None = None,
    llm: LLMProvider | None = None,
    state_path: Path | None = None,
) -> int:
    site = load_site_config()
    projects = enabled_projects()
    if only:
        projects = [p for p in projects if p.slug == only or p.repository == only]
        if not projects:
            print(f"No enabled project matching {only}", file=sys.stderr)
            return 2

    state = load_state(state_path) if state_path else load_state()
    client = client or GitHubClient()
    llm = llm or get_provider()
    load_cache()  # ensure file exists

    outcomes: list[ProjectOutcome] = []
    print(f"Orpheon · {len(projects)} enabled project(s) · manual run")
    for project in projects:
        print(f"\n→ {project.repository}")
        try:
            outcome = process_project(project, client=client, llm=llm, state=state, dry_run=dry_run)
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            outcome = ProjectOutcome(project.repository, project.slug, FAIL, f"unhandled: {exc}")
        outcomes.append(outcome)
        mark = "✓" if outcome.status != FAIL else "✗"
        print(f"  {mark} {outcome.status}: {outcome.detail}")

    if not dry_run:
        save_state(state, state_path) if state_path else save_state(state)

    print("\nSummary")
    for outcome in outcomes:
        print(f"  {outcome.slug}: {outcome.status}")

    wrote = any(o.wrote for o in outcomes)
    failed = any(o.status == FAIL for o in outcomes)
    # Partial success is still a success for the workflow so other projects can publish.
    if wrote:
        print("Files changed; caller should commit.")
    else:
        print("No documentation files written.")
    return 1 if (failed and not wrote and not any(o.status in {SKIP, TRIVIAL, OK} for o in outcomes)) else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Orpheon journal pipeline (manual)")
    parser.add_argument("--project", help="Process a single slug or repository")
    parser.add_argument("--dry-run", action="store_true", help="Do not write files or update state")
    args = parser.parse_args(argv)
    return run(only=args.project, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
