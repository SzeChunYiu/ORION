"""Empirical promotion assessment for issue #209.

The repository freeze must name the exact missing trial and must not be
goaded into emitting PHASE_3_GOVERNED_SELF_ORION_CLOSED by fabricated
receipt counts.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from orion.self_orion.phase3_preflight import (
    PHASE3_METRICS,
    PHASE3_PROTOCOL_ID,
    UNBOUND_DIGEST,
    Phase3PreflightStatus,
)
from orion.self_orion.phase3_promotion import (
    MISSING_LONGITUDINAL_TRIAL_ID,
    MISSING_PROMOTION_TRIAL,
    MISSING_PROMOTION_TRIAL_ID,
    PHASE3_TERMINAL_CLAIM,
    PROMOTION_RECEIPT_SCHEMA,
    Phase3CycleReceiptClaim,
    Phase3PromotionEvidence,
    Phase3PromotionStatus,
    assess_phase3_empirical_promotion,
    phase3_promotion_receipt_to_dict,
    repository_phase3_promotion_evidence,
)
from orion.self_orion.readiness import EvidenceStatus

CANONICAL_RECEIPT_PATH = (
    Path(__file__).resolve().parents[3]
    / "development"
    / "phase3"
    / "PHASE3_EMPIRICAL_PROMOTION_CANNOT_CHECK_v1.json"
)

BOUND_A = "a" * 64
BOUND_B = "b" * 64
BOUND_C = "c" * 64
BOUND_D = "d" * 64


def _bound_receipt(cycle_id: str, receipt_hash: str) -> Phase3CycleReceiptClaim:
    return Phase3CycleReceiptClaim(
        cycle_id=cycle_id,
        receipt_hash=receipt_hash,
        subject_revision_hash=BOUND_A,
        evaluator_artifact_hash=BOUND_B,
        evaluation_epoch_id="phase3:epoch:fabricated",
        producer_process_lineage_hash=BOUND_C,
        verifier_process_lineage_hash=BOUND_D,
    )


def test_repository_evidence_is_cannot_check_and_names_the_exact_missing_trial() -> None:
    report = assess_phase3_empirical_promotion(repository_phase3_promotion_evidence())
    assert report.status is Phase3PromotionStatus.CANNOT_CHECK
    assert report.evidence_status is EvidenceStatus.CANNOT_CHECK
    assert report.protocol_status is Phase3PreflightStatus.BIND_PHASE2_TERMINAL_EVIDENCE
    assert report.primary_missing_trial_id == MISSING_PROMOTION_TRIAL_ID
    assert report.missing_trials[0] == MISSING_PROMOTION_TRIAL
    assert report.missing_trials[1].trial_id == MISSING_LONGITUDINAL_TRIAL_ID
    assert "no_frozen_live_governed_cycle_receipts" in report.blockers
    assert "issue_76_must_close_on_merged_phase2_evidence_first" in report.blockers
    assert PHASE3_TERMINAL_CLAIM not in report.blockers
    assert report.measured_metric_ids == ()
    assert report.unmeasured_metric_ids == tuple(metric.metric_id for metric in PHASE3_METRICS)


def test_repository_assessment_grants_nothing_and_cannot_close_issue_209() -> None:
    report = assess_phase3_empirical_promotion(repository_phase3_promotion_evidence())
    assert not report.grants_phase3_operating_authority
    assert not report.grants_governed_self_orion
    assert not report.closes_issue_209
    assert not report.emits_terminal_claim
    assert report.terminal_claim is None


def test_the_status_enum_cannot_express_closure_or_promotion() -> None:
    assert set(Phase3PromotionStatus) == {
        Phase3PromotionStatus.CANNOT_CHECK,
        Phase3PromotionStatus.INVALID,
    }
    for forbidden in ("CLOSED", "PASS", "AUTHORIZED", "PROMOTED", "READY"):
        assert forbidden not in Phase3PromotionStatus.__members__
    payload = phase3_promotion_receipt_to_dict(
        assess_phase3_empirical_promotion(repository_phase3_promotion_evidence())
    )
    dumped = json.dumps(payload)
    assert PHASE3_TERMINAL_CLAIM not in dumped
    assert payload["terminal_claim"] is None
    assert payload["phase_3_governed_self_orion_closed"] is False
    assert payload["closes_issue_209"] is False
    assert payload["schema"] == PROMOTION_RECEIPT_SCHEMA
    assert payload["primary_missing_trial_id"] == MISSING_PROMOTION_TRIAL_ID


def test_twelve_unbound_cycle_hashes_are_invalid_not_a_pass() -> None:
    """Identity, not count: a declared dozen of sentinels is fabrication."""

    hashes = tuple(UNBOUND_DIGEST for _ in range(12))
    evidence = Phase3PromotionEvidence(
        cycle_receipts=tuple(
            Phase3CycleReceiptClaim(cycle_id=f"cycle-{index}", receipt_hash=item)
            for index, item in enumerate(hashes)
        ),
        declared_consecutive_cycle_count=12,
    )
    report = assess_phase3_empirical_promotion(evidence)
    assert report.status is Phase3PromotionStatus.INVALID
    assert "cycle_receipt_identity_unbound" in report.blockers
    assert not report.closes_issue_209
    assert not report.emits_terminal_claim
    # The missing trial is still named so a fabricated count cannot hide it.
    assert report.primary_missing_trial_id == MISSING_PROMOTION_TRIAL_ID


def test_declared_count_without_receipts_is_invalid() -> None:
    evidence = Phase3PromotionEvidence(declared_consecutive_cycle_count=12)
    report = assess_phase3_empirical_promotion(evidence)
    assert report.status is Phase3PromotionStatus.INVALID
    assert "declared_cycle_count_without_receipt_identities" in report.blockers
    clean = assess_phase3_empirical_promotion(repository_phase3_promotion_evidence())
    assert clean.status is Phase3PromotionStatus.CANNOT_CHECK


def test_self_certified_cycle_receipt_is_invalid() -> None:
    receipt = _bound_receipt("cycle-1", "e" * 64)
    receipt = dataclasses.replace(
        receipt,
        verifier_process_lineage_hash=receipt.producer_process_lineage_hash,
    )
    report = assess_phase3_empirical_promotion(
        Phase3PromotionEvidence(cycle_receipts=(receipt,), declared_consecutive_cycle_count=1)
    )
    assert report.status is Phase3PromotionStatus.INVALID
    assert "cycle_receipt_self_certified" in report.blockers
    clean = _bound_receipt("cycle-1", "e" * 64)
    # Independence of lineages is not sufficient: one receipt is still below
    # the predeclared minimum, so the honest path remains CANNOT_CHECK.
    honest = assess_phase3_empirical_promotion(
        Phase3PromotionEvidence(cycle_receipts=(clean,), declared_consecutive_cycle_count=1)
    )
    assert honest.status is Phase3PromotionStatus.CANNOT_CHECK
    assert "consecutive_cycle_count_below_predeclared_minimum:12" in honest.blockers


def test_duplicate_receipt_hashes_are_invalid() -> None:
    first = _bound_receipt("cycle-1", "e" * 64)
    second = _bound_receipt("cycle-2", "e" * 64)
    report = assess_phase3_empirical_promotion(
        Phase3PromotionEvidence(
            cycle_receipts=(first, second),
            declared_consecutive_cycle_count=2,
        )
    )
    assert report.status is Phase3PromotionStatus.INVALID
    assert "duplicate_cycle_receipt_hash" in report.blockers


def test_protocol_id_mismatch_is_invalid() -> None:
    report = assess_phase3_empirical_promotion(
        Phase3PromotionEvidence(protocol_id="phase3-governed-self-orion-prefreeze-v2")
    )
    assert report.status is Phase3PromotionStatus.INVALID
    assert "promotion_evidence_protocol_id_mismatch" in report.blockers
    assert PHASE3_PROTOCOL_ID == repository_phase3_promotion_evidence().protocol_id


def test_baseline_comparison_without_cycles_is_invalid() -> None:
    report = assess_phase3_empirical_promotion(
        Phase3PromotionEvidence(baseline_comparison_artifact_hash=BOUND_A)
    )
    assert report.status is Phase3PromotionStatus.INVALID
    assert "baseline_comparison_without_cycle_receipts" in report.blockers


def test_committed_cannot_check_receipt_matches_the_code_owned_assessment() -> None:
    committed = json.loads(CANONICAL_RECEIPT_PATH.read_text(encoding="utf-8"))
    derived = phase3_promotion_receipt_to_dict(
        assess_phase3_empirical_promotion(repository_phase3_promotion_evidence())
    )
    assert committed == derived
    assert committed["primary_missing_trial_id"] == MISSING_PROMOTION_TRIAL_ID
    assert committed["status"] == "CANNOT_CHECK"
    assert committed["closes_issue_209"] is False


def test_grants_fields_cannot_be_replaced_true() -> None:
    report = assess_phase3_empirical_promotion(repository_phase3_promotion_evidence())
    with pytest.raises(AttributeError):
        report.closes_issue_209 = True  # type: ignore[misc]
    with pytest.raises(TypeError):
        dataclasses.replace(report, grants_governed_self_orion=True)  # type: ignore[call-arg]
