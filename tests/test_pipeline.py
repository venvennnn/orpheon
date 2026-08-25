from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.detect_changes import decide
from scripts.filters import all_trivial, remaining_after_filter, should_ignore
from scripts.security import contains_secret, is_secret_path, sanitize_text
from scripts.textutil import word_count, with_frontmatter
from scripts.update_build_log import append_entry, import_entry
from scripts.validator import validate_bundle
from scripts.generate_architecture import looks_like_mermaid, normalize_mermaid
from scripts.classify_changes import bootstrap_classification, trivial_classification, validate_payload
from scripts.llm_client import MockProvider, parse_json_object


def test_skip_when_head_matches_last_sha():
    decision = decide("venvennnn/aftermath", "abc", "abc")
    assert decision.skip is True
    assert decision.bootstrap is False


def test_bootstrap_when_no_last_sha():
    decision = decide("venvennnn/aftermath", "abc", None)
    assert decision.skip is False
    assert decision.bootstrap is True


def test_inspect_when_sha_moved():
    decision = decide("venvennnn/aftermath", "xyz", "abc")
    assert decision.skip is False
    assert decision.bootstrap is False


def test_secret_paths_and_redaction():
    assert is_secret_path(".env")
    assert is_secret_path("secrets.yaml")
    assert is_secret_path("certs/prod.pem")
    text = sanitize_text("hello\nOPENAI_API_KEY=sk-secret\nworld")
    assert "sk-secret" not in text
    assert "REDACTED" in text
    assert contains_secret("GITHUB_TOKEN=abc")


def test_ignore_and_trivial_diffs():
    paths = ["package-lock.json", "src/app.ts", "data/foo.csv", "node_modules/x/index.js"]
    remaining = remaining_after_filter(paths)
    assert remaining == ["src/app.ts"]
    assert should_ignore("outputs/model.pkl")
    assert all_trivial(["yarn.lock", ".gitignore", "pnpm-lock.yaml"])
    assert not all_trivial(["src/engine.py"])


def test_word_count_skips_code_and_frontmatter():
    md = with_frontmatter({"project": "X"}, "Hello world.\n\n```\nalpha beta gamma\n```\n")
    assert word_count(md) == 2


def test_build_log_is_append_only():
    first = import_entry("25 August 2026")
    combined = append_entry(first, "26 August 2026\n\nAdded:\n- clustering\n")
    assert combined.startswith("25 August 2026")
    assert "26 August 2026" in combined
    assert combined.index("25 August 2026") < combined.index("26 August 2026")
    with pytest.raises(ValueError):
        append_entry(first, "   ")


def test_classification_schema_and_trivial_override():
    payload = {
        "summary": "Renamed a variable",
        "importance": "trivial",
        "categories": ["cosmetic"],
        "documentation_updates": {
            "eli15": True,
            "technical": True,
            "references": True,
            "architecture": True,
            "build_log": True,
        },
        "major_evolution": True,
    }
    result = validate_payload(payload)
    assert result.importance == "trivial"
    assert result.needs_generation is False
    assert result.major_evolution is False
    boot = bootstrap_classification()
    assert boot.documentation_updates.eli15 is True
    assert trivial_classification("lockfile").needs_generation is False


def test_json_fence_parsing():
    parsed = parse_json_object("sure\n```json\n{\"a\": 1}\n```")
    assert parsed == {"a": 1}


def test_validator_rejects_secrets_and_overlong_eli15():
    words = " ".join(["word"] * 720)
    files = {
        "metadata.json": json.dumps(
            {
                "name": "X",
                "slug": "x",
                "repository": "a/b",
                "status": "active",
                "last_updated": "2026-08-25",
                "last_commit": "abc",
                "categories": ["AI"],
            }
        ),
        "eli15.md": with_frontmatter(
            {
                "project": "X",
                "generated_by": "orpheon",
                "generated_at": "2026-08-25",
                "source_repository": "a/b",
                "source_commit": "abc",
            },
            words,
        ),
        "technical.md": with_frontmatter(
            {
                "project": "X",
                "generated_by": "orpheon",
                "generated_at": "2026-08-25",
                "source_repository": "a/b",
                "source_commit": "abc",
            },
            " ".join(["tech"] * 600),
        ),
        "references.md": with_frontmatter(
            {
                "project": "X",
                "generated_by": "orpheon",
                "generated_at": "2026-08-25",
                "source_repository": "a/b",
                "source_commit": "abc",
            },
            "## Used / Influenced This Project\n\nNone listed.\n",
        ),
        "architecture.mmd": "graph LR\nA --> B\n",
        "build-log.md": with_frontmatter(
            {
                "project": "X",
                "generated_by": "orpheon",
                "generated_at": "2026-08-25",
                "source_repository": "a/b",
                "source_commit": "abc",
            },
            "25 August 2026\n\nProject imported into Orpheon\n",
        ),
    }
    result = validate_bundle(files, tree=["src/app.ts"], bootstrap=True)
    assert result.ok is False
    assert any("700" in error for error in result.errors)

    files["eli15.md"] = with_frontmatter(
        {
            "project": "X",
            "generated_by": "orpheon",
            "generated_at": "2026-08-25",
            "source_repository": "a/b",
            "source_commit": "abc",
        },
        "This is a fine explanation of the product purpose and audience.\nOPENAI_API_KEY=sk-leak",
    )
    result = validate_bundle(files, tree=["src/app.ts"], bootstrap=True)
    assert result.ok is False
    assert any("secret" in error for error in result.errors)


def test_mermaid_normalization():
    assert looks_like_mermaid("graph LR\nA-->B")
    cleaned = normalize_mermaid("```mermaid\nflowchart TD\nA-->B\n```")
    assert cleaned.startswith("flowchart TD")
    with pytest.raises(Exception):
        normalize_mermaid("not a diagram")


def test_mock_provider_records_calls():
    llm = MockProvider(canned={"structured": {"ok": True}, "text": "hi"})
    assert llm.generate("hello") == "hi"
    assert llm.calls
