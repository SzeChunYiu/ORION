from __future__ import annotations

from orion.benchmarks.degeneracy import (
    CouplingKind,
    DegeneracyStatus,
    LabeledRecord,
    probe_records,
)


def _rec(i, label, **feat):
    return LabeledRecord(record_id=f"r{i}", features=feat, label=label)


def test_a_clean_panel_is_clean() -> None:
    recs = [_rec(i, lab, score=s) for i, (lab, s) in enumerate(
        [("A", 0.9), ("B", 0.2), ("A", 0.7), ("B", 0.4), ("A", 0.3), ("B", 0.8)])]
    assert probe_records(recs).status is DegeneracyStatus.CLEAN


def test_an_identifier_carrying_the_label_is_degenerate() -> None:
    """The case ORION hand-rolled twice: the answer written into the case id."""

    recs = [_rec(i, lab, case_id=f"case-{i}-{lab.lower()}") for i, lab in enumerate(
        ["PREDICTION_NOT_MECHANISM", "MECHANISM", "PREDICTION_NOT_MECHANISM", "MECHANISM"])]
    report = probe_records(recs)
    assert report.status is DegeneracyStatus.DEGENERATE
    assert report.findings[0].coupling is CouplingKind.AUTHORED_FROM_LABEL
    assert not report.permits_score_as_evidence


def test_a_deterministic_non_identifier_feature_is_suspect_not_degenerate() -> None:
    """A hard rule may be legitimate; it is flagged, not condemned."""

    recs = [_rec(i, lab, regime=r) for i, (lab, r) in enumerate(
        [("A", "hot"), ("B", "cold"), ("A", "hot"), ("B", "cold")])]
    report = probe_records(recs)
    assert report.status is DegeneracyStatus.SUSPECT
    assert report.findings[0].coupling is CouplingKind.DETERMINISTIC


def test_a_blind_responder_beating_baseline_is_degenerate() -> None:
    recs = [_rec(i, lab, meta=lab) for i, lab in enumerate(["A", "B", "A", "B", "A", "B"])]
    report = probe_records(
        recs, blind_responders={"metadata_only": lambda r: r.features["meta"]}
    )
    assert report.status is DegeneracyStatus.DEGENERATE
    assert any(f.probe == "blind_responder_ceiling" for f in report.findings)


def test_a_single_label_panel_is_cannot_check_never_clean() -> None:
    """Any responder scores 1.0 on it, so nothing is measured."""

    recs = [_rec(i, "A", x=i) for i in range(4)]
    report = probe_records(recs)
    assert report.status is DegeneracyStatus.CANNOT_CHECK
    assert not report.permits_score_as_evidence


def test_an_empty_panel_is_cannot_check() -> None:
    assert probe_records([]).status is DegeneracyStatus.CANNOT_CHECK


def test_a_continuous_measurement_is_not_mistaken_for_an_identifier() -> None:
    """RAKL's negative history: near-unique values flagged every real-valued
    feature. Identifier-ness is about the field name, never uniqueness alone."""

    recs = [_rec(i, lab, score=float(i) / 10) for i, lab in enumerate(["A", "B", "A", "B"])]
    report = probe_records(recs)
    assert report.status is not DegeneracyStatus.DEGENERATE
