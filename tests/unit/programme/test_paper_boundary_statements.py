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


def test_p5_names_its_three_residual_errors() -> None:
    """21/24 with three errors counted but unnamed is not checkable."""
    text = _flat(PAPERS / "paper-05-self-orion/JOURNAL_READINESS.md")
    for case in ("P5-HC-002", "P5-HC-012", "P5-HC-018"):
        assert case in text, f"{case} is a residual error but is not named"
    assert "RETRIEVAL_MISS" in text and "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE" in text
    assert "21/24" in text


def test_p6_reads_its_counts_with_their_multiplicity() -> None:
    """320/25/155/1,055 are loop repeats, not independent facts."""
    text = _flat(PAPERS / "paper-06-formal-epistemic-structures-and-mechanics/README.md")
    assert "Read with their multiplicity" in text
    assert "5 separations counted five times" in text
    assert "31 and 211 counted five times" in text
    assert "Only the **31** product countermodels are 31 distinct facts" in text


def test_p6_separates_donor_validity_from_scientific_standing() -> None:
    text = _flat(PAPERS / "paper-06-formal-epistemic-structures-and-mechanics/README.md")
    assert "laundering lower-level validity into unchanged scientific standing" in text
    assert "donor-owned lower-level objects" in text


def test_p14a_is_a_measurement_not_a_comparative_negative() -> None:
    """Gates unreachable under the frozen support: CANNOT_CHECK, not a loss."""
    text = _flat(PAPERS / "paper-14-orion-rse/MANUSCRIPT.md")
    assert "unreachable under its own frozen sampling support" in text
    assert "measurement that could not be taken rather than a comparative negative" in text


def test_p14b_is_marked_diagnostic_for_gold_reuse() -> None:
    text = _flat(PAPERS / "paper-14-orion-rse/MANUSCRIPT.md")
    assert "directly reuses its adjudication function" in text
    assert "removes that implementation circularity" in text


def test_p13_marks_its_safety_endpoint_as_self_entailed() -> None:
    """The endpoint could not move, so neither reading of it is licensed."""
    text = _flat(PAPERS / "paper-13-responsibility-carrying-state/PEER_REVIEW_READINESS.md")
    assert "zero opportunities, not zero movements" in text
    assert "incapable of showing one" in text
    assert "self-entailed endpoint cannot discriminate" in text


def test_p12_marks_prospective_certificate_availability_cannot_check() -> None:
    text = _flat(PAPERS / "paper-12-adaptive-state-reasoning/PEER_REVIEW_READINESS.md")
    assert "Prospective certificate availability and forward-time deployment are CANNOT_CHECK" in text


def test_p15_separates_all_six_execution_concepts() -> None:
    """Attestation is the one most easily read as scientific validity."""
    text = _flat(PAPERS / "paper-15-orion-research-harness/CLAIM_EVIDENCE_LEDGER_V1.md")
    assert "attribution, replay, agreement and attestation as evidence about" in text
    assert "The six are separate and none implies the next" in text
    assert "correct signature over a wrong result" in text
