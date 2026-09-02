"""The index must be true, and the checker must notice when it stops being true.

The failure this guards is not "someone wrote the wrong path". It is "a successor
was adopted and the index was left behind" — which is what happened on
2026-09-02, when four manuscripts were adopted in one day and two of them ended
up referenced by no document at all.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
CHECKER = ROOT / "scripts/check_current_manuscript_index_v1.py"


def _load():
    spec = importlib.util.spec_from_file_location("_manuscript_index", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture(scope="module")
def index(mod):
    if not mod.INDEX.is_file():
        pytest.skip("no committed index")
    return json.loads(mod.INDEX.read_text(encoding="utf-8"))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "index.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_repository_index_is_true(mod):
    assert mod.main([]) == 0


def test_version_ordering(mod):
    assert mod.version_key("FINAL.md") == (1, 0)
    assert mod.version_key("FINAL_V3.md") == (3, 0)
    assert mod.version_key("FINAL_V2_1.md") == (2, 1)
    assert mod.version_key("MANUSCRIPT_V2.md") == (2, 0)
    assert mod.version_key("FINAL_V2_1.md") < mod.version_key("FINAL_V3.md")
    assert mod.version_key("NOTES.md") is None


def test_an_unlisted_newer_manuscript_is_a_finding(mod, index, tmp_path):
    """The real failure mode: adopt a successor, forget the index."""
    stale = json.loads(json.dumps(index))
    entry = stale["papers"]["ORION-16"]
    entry["current_manuscript"] = entry["current_manuscript"].replace(
        "FINAL_V6.md", "FINAL_V4.md"
    )
    assert mod.main(["--index", str(_write(tmp_path, stale))]) == 2


def test_a_missing_manuscript_is_a_finding(mod, index, tmp_path):
    broken = json.loads(json.dumps(index))
    broken["papers"]["ORION-17"]["current_manuscript"] = (
        "papers/orion-17-epistemic-navigation-open-worlds/manuscript/FINAL_V99.md"
    )
    assert mod.main(["--index", str(_write(tmp_path, broken))]) == 2


def test_an_unversioned_name_cannot_be_decided_and_says_so(mod, index, tmp_path):
    odd = json.loads(json.dumps(index))
    odd["papers"]["ORION-16"]["current_manuscript"] = (
        "papers/orion-16-formal-epistemic-structures-and-mechanics/README.md"
    )
    assert mod.main(["--index", str(_write(tmp_path, odd))]) == 2


def test_an_absent_index_is_cannot_check_not_clean(mod, tmp_path):
    assert mod.main(["--index", str(tmp_path / "nope.json")]) == 3


def test_an_empty_index_is_cannot_check(mod, tmp_path):
    assert mod.main(["--index", str(_write(tmp_path, {"papers": {}}))]) == 3


def test_a_malformed_index_is_cannot_check(mod, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    assert mod.main(["--index", str(bad)]) == 3


def test_every_declared_manuscript_records_why_it_superseded(mod, index):
    """An index entry without provenance is a pointer nobody can audit."""
    for paper, entry in index["papers"].items():
        assert entry.get("adopted_by"), f"{paper} does not record what adopted it"
        assert entry.get("superseded"), f"{paper} does not record what it replaced"
