"""Boundary statements #1131 requires must be present in what a reader opens.

Each of these is a disclosure the paper owes about the limits of its own
headline number. The tests normalise whitespace before searching, because a
required phrase that happens to wrap across a line is still stated -- an
assertion that fails on line wrapping would be testing the formatter, not the
disclosure.
"""

from __future__ import annotations

from pathlib import Path

PAPERS = Path(__file__).resolve().parents[3] / "papers"


def _flat(path: Path) -> str:
    return " ".join(path.read_text().split())


def test_p7_frames_its_perfect_score_as_finite_conformance() -> None:
    """1.0 on enumerated cases is conformance, not transport to unseen ones."""
    text = _flat(PAPERS / "paper-07-epistemic-navigation-open-worlds/README.md")
    assert "not** universal regime transport" in text or "not universal regime transport" in text
    assert "finite, frozen contract" in text
    assert "No population is sampled here" in text


def test_p8_names_its_gold_as_same_programme() -> None:
    """Agreement with gold you authored is internal consistency."""
    text = _flat(PAPERS / "paper-08-epistemic-authority-autonomous-science/README.md")
    assert "same-programme gold" in text
    assert "not externally governed scientific adjudication" in text
    assert "share an author" in text


def test_p14_says_its_adjudication_specification_is_internally_authored() -> None:
    """Already stated; pinned so it cannot be lost in a manuscript rebuild."""
    text = _flat(PAPERS / "paper-14-orion-rse/MANUSCRIPT.md")
    assert "adjudication specification is still internally authored" in text


def test_p3_states_its_analysis_unit_for_v21() -> None:
    """The row cites 33 repeatedly; the unit must be unmistakable."""
    text = _flat(PAPERS / "paper-03-global-knowledge-portrait/THEORY_CLAIM_LEDGER_V1.md")
    assert "The analysis unit is one OAEI 2004 test-103 case" in text
    assert "no p value" in text
