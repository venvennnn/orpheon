from __future__ import annotations

from pathlib import Path

from scripts.paths import CONTENT_DIR
from scripts.textutil import WORD_LIMITS, word_count
from scripts.validator import validate_bundle


def test_shipped_journals_pass_validation_and_word_limits():
    for folder in CONTENT_DIR.iterdir():
        if not folder.is_dir():
            continue
        files = {
            path.name: path.read_text(encoding="utf-8")
            for path in folder.iterdir()
            if path.is_file()
        }
        result = validate_bundle(files, tree=[], bootstrap=True)
        assert result.ok, f"{folder.name}: {result.errors}"
        mapping = {
            "problem.md": "problem",
            "summary.md": "summary",
            "results.md": "results",
            "examples.md": "examples",
        }
        for name, kind in mapping.items():
            count = word_count(files[name])
            assert count <= WORD_LIMITS[kind], f"{folder.name}/{name} has {count} words"
            assert count >= 20, f"{folder.name}/{name} is empty"
