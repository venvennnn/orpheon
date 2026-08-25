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
        mapping = {"eli15.md": "eli15", "technical.md": "technical", "references.md": "references"}
        minima = {"eli15": 400, "technical": 700, "references": 500}
        for name, kind in mapping.items():
            count = word_count(files[name])
            assert count <= WORD_LIMITS[kind], f"{folder.name}/{name} has {count} words"
            assert count >= minima[kind], f"{folder.name}/{name} has {count} words; target is {minima[kind]}+"
