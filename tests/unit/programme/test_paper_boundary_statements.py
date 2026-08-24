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


def test_p4_states_the_finite_battery_estimand() -> None:
    """Intervals over an enumerated battery are not population inference."""
    text = _flat(PAPERS / "paper-04-verified-scientific-discovery/JOURNAL_READINESS.md")
    assert "estimand is the effect on this finite registered battery" in text
    assert "Artifacts are not population units" in text
    assert "Bridge identities are not population units" in text
    assert "there is no population from which the battery is a sample" in text


def test_p10_separates_unexecuted_hypotheses_from_the_earned_claim() -> None:
    """Not-executed is a fourth state, distinct from PASS, FAIL and CANNOT_CHECK."""
    text = _flat(PAPERS / "paper-10-structured-problem-solving/CLAIM_EVIDENCE_LEDGER.md")
    assert "PROSPECTIVE_NOT_EXECUTED" in text
    assert "discharges none of H1–H6" in text
    assert "they have not entered the outcome lifecycle" in text


def test_p10_refuses_open_ended_invention_language() -> None:
    text = _flat(PAPERS / "paper-10-structured-problem-solving/TOP_TIER_PROMOTION_V1.md")
    assert "unrestricted autonomous mathematical invention" in text
    assert "prospectively supplied by the experiment" in text
    assert "did not invent its own unbounded grammar" in text


def test_p10_preserves_the_zero_eligible_transition_result() -> None:
    """0 of 11,842 eligible: CANNOT_CHECK, and not convertible after the fact."""
    text = _flat(PAPERS / "paper-10-structured-problem-solving/TOP_TIER_PROMOTION_V1.md")
    assert "CANNOT_CHECK_NATIVE_STATE_COVERAGE" in text
    assert "zero eligible transitions out of 11,842 extracted transitions" in text
    assert "may not be converted into a positive native-state claim by relaxing eligibility post hoc" in text


def test_p7_keeps_denominators_cannot_checks_and_reopen_failures() -> None:
    """All three change classes, with the numbers a reader needs to check them."""
    text = _flat(PAPERS / "paper-07-epistemic-navigation-open-worlds/README.md")
    for denominator in ("14 frozen cases", "712 protected rows", "10 cells"):
        assert denominator in text, denominator
    for cannot_check in ("4 correct `CANNOT_CHECK`", "238 correct `CANNOT_CHECK`", "5 correct `CANNOT_CHECK`"):
        assert cannot_check in text, cannot_check
    for reopen in ("6 unnecessary reopens", "474 unnecessary reopens"):
        assert reopen in text, reopen


def test_p9_reports_its_positives_null_and_negative_together() -> None:
    """A positive shown without its null beside it is a selected result."""
    text = _flat(PAPERS / "paper-09-structured-epistemic-learning/README.md")
    assert "breast-cancer and digits are positive" in text
    assert "Wine is retained as a null cell" in text
    assert "authoritative negative, not repaired after the fact" in text


def test_p9_refuses_a_scalar_exchange_rate() -> None:
    text = _flat(PAPERS / "paper-09-structured-epistemic-learning/README.md")
    assert "I/A/C/M/R" in text
    assert "no scalar exchange rate across the resource vector" in text


def test_p12_refuses_a_cross_domain_scalar_exchange_rate() -> None:
    text = _flat(PAPERS / "paper-12-adaptive-state-reasoning/README.md")
    assert "no cross-domain scalar exchange rate between heterogeneous charged units" in text


def test_p5_baseline_and_ablation_table_is_explicit_cannot_check() -> None:
    """An absent table and an unrun arm look identical to a reader."""
    text = _flat(PAPERS / "paper-05-self-orion/JOURNAL_READINESS.md")
    assert "No baseline or ablation arm has been executed" in text
    for arm in ("no-edit control", "direct self-edit", "strongest runnable self-improvement baseline",
                "ADAS", "DGM", "ADIAS"):
        assert arm in text, arm
    assert "No cell is populated from a default" in text
    # the two reasons must stay distinct
    assert "not executed; no SWE-bench Verified run exists" in text
    assert "comparator unavailable; not replaced by a weak proxy" in text


def test_p1_frames_v2_2_4_as_frozen_generator_mechanism_evidence() -> None:
    """Two seeds test the draw; they do not widen the construction."""
    text = _flat(PAPERS / "paper-01-recursive-epistemic-reconstruction/JOURNAL_READINESS.md")
    assert "Both are runs of a frozen generator" in text
    assert "not 2,882 independent observations of scientific practice" in text
    assert "Replication across seeds is exactly as broad as the generator" in text
