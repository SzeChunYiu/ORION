"""The canonical decision and the newest freeze addendum must name the same versions.

The failure this guards is not "someone wrote the wrong filename". It is "a
successor manuscript/ledger pair was adopted by a new canonical decision while
the freeze addendum still froze the predecessor pair" — which is what happened
on 2026-09-02, when three papers drifted that way and nothing compared the two
authority surfaces.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
CHECKER = ROOT / "scripts/check_freeze_canonical_agreement_v1.py"


def _load():
    spec = importlib.util.spec_from_file_location("_freeze_canonical", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod():
    return _load()


def _paper(tmp_path: Path, name: str, canonical: str, freezes: dict[str, str]) -> Path:
    """Build a minimal paper directory: one canonical file + freeze addenda."""
    paper = tmp_path / "papers" / name
    paper.mkdir(parents=True)
    (paper / "CANONICAL_SUBMISSION_V1.md").write_text(canonical, encoding="utf-8")
    for filename, text in freezes.items():
        (paper / filename).write_text(text, encoding="utf-8")
    return paper


def test_repository_is_true(mod):
    assert mod.main([]) == 0


def test_series_ordering(mod):
    base = mod.parse_name("MANUSCRIPT.md")
    revised = mod.parse_name("CLAIM_LEDGER_R2.md")
    versioned = mod.parse_name("CLAIM_LEDGER_V3.md")
    assert base and revised and versioned
    assert base[2] < revised[2] < versioned[2]
    assert versioned[0] == "CLAIM_LEDGER"
    assert revised[0] == "CLAIM_LEDGER"


def test_a_retraction_ledger_is_not_a_manuscript_family(mod):
    """Retraction ledgers are history surfaces, not the canonical/freeze pair being compared."""
    assert mod.parse_name("CLAIM_RETRACTION_LEDGER_V1.md") is None


def test_a_canonical_freeze_version_drift_is_a_finding(mod, tmp_path):
    _paper(
        tmp_path,
        "orion-x",
        canonical="Canonical manuscript is `MANUSCRIPT_V3.md` and ledger `CLAIM_LEDGER_V3.md`.",
        freezes={
            "PUBLICATION_FREEZE_ADDENDUM_V1.md": (
                "The content packet consists of `MANUSCRIPT_V2.md`, `CLAIM_LEDGER_R2.md`, "
                "and this addendum."
            )
        },
    )
    assert mod.main(["--papers", str(tmp_path / "papers")]) == 2


def test_superseded_mentions_do_not_count_as_current(mod, tmp_path):
    _paper(
        tmp_path,
        "orion-x",
        canonical="Canonical manuscript is `MANUSCRIPT_V3.md`.",
        freezes={
            "PUBLICATION_FREEZE_ADDENDUM_V1.md": (
                "Current manuscript is `MANUSCRIPT_V3.md`. "
                "`MANUSCRIPT_V2.md` is superseded for submission and remains immutable history."
            )
        },
    )
    assert mod.main(["--papers", str(tmp_path / "papers")]) == 0


def test_supersession_scope_is_the_sentence_not_the_line(mod, tmp_path):
    """The 2026-09-02 orion-02 pattern: packet declaration and history note share a line."""
    _paper(
        tmp_path,
        "orion-x",
        canonical="Canonical manuscript is `MANUSCRIPT_V3.md`.",
        freezes={
            "PUBLICATION_FREEZE_ADDENDUM_V1.md": (
                "The content packet consists of `MANUSCRIPT_V2.md` and this addendum. "
                "Historical records remain additive and immutable."
            )
        },
    )
    assert mod.main(["--papers", str(tmp_path / "papers")]) == 2


def test_unilateral_families_are_notes_not_failures(mod, tmp_path):
    _paper(
        tmp_path,
        "orion-x",
        canonical="Canonical manuscript is the LaTeX tree under manuscript/.",
        freezes={
            "PUBLICATION_FREEZE_ADDENDUM_V1.md": (
                "The content packet consists of `MANUSCRIPT_SHORT_V1.md` and this addendum."
            )
        },
    )
    assert mod.main(["--papers", str(tmp_path / "papers")]) == 0


def test_the_newest_freeze_addendum_is_the_freeze_side(mod, tmp_path):
    canonical = "Canonical manuscript is `MANUSCRIPT_V3.md`."
    _paper(
        tmp_path,
        "orion-x",
        canonical=canonical,
        freezes={
            "PUBLICATION_FREEZE_ADDENDUM_V1.md": "Packet is `MANUSCRIPT_V2.md`.",
            "PUBLICATION_FREEZE_ADDENDUM_V2.md": "Packet is `MANUSCRIPT_V3.md`.",
        },
    )
    assert mod.main(["--papers", str(tmp_path / "papers")]) == 0


def test_an_absent_papers_root_is_cannot_check(mod, tmp_path):
    assert mod.main(["--papers", str(tmp_path / "nope")]) == 3


def test_a_papers_root_with_nothing_to_compare_is_cannot_check(mod, tmp_path):
    """Vacuous scope is not a clean result; say so rather than bless it."""
    (tmp_path / "papers" / "orion-x").mkdir(parents=True)
    (tmp_path / "papers" / "orion-x" / "README.md").write_text("no surfaces", encoding="utf-8")
    assert mod.main(["--papers", str(tmp_path / "papers")]) == 3
