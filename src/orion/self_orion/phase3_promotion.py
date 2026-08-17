"""Empirical Phase-3 promotion assessment.

Issue #209 closes only when a machine-readable external promotion receipt
supports ``PHASE_3_GOVERNED_SELF_ORION_CLOSED``.  This module is the place that
receipt would be assessed.  It has no CLOSED/PASS/AUTHORIZED status.  Its
repository freeze records ``CANNOT_CHECK`` and names the exact missing trial.

Nothing here reads issue state, polls GitHub, or treats a protocol-prefreeze
merge as promotion evidence.  Cycle-count without bound receipt identity is
``INVALID``, not a pass — the same "identity, not count" lesson as the Phase-2
attack registry and the Phase-3 preflight.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.self_orion.phase3_preflight import (
    PHASE3_PROTOCOL_ID,
    PHASE3_UNCERTAINTY_POLICY,
    UNBOUND_DIGEST,
    Phase3PreflightStatus,
    Phase3ProtocolFreeze,
    assess_phase3_preflight,
    repository_phase3_protocol_freeze,
)
from orion.self_orion.readiness import EvidenceStatus

PHASE3_TERMINAL_CLAIM = "PHASE_3_GOVERNED_SELF_ORION_CLOSED"

# The prospective study frozen in phase3_preflight: ≥12 consecutive ordinary
# development cycles of ORION-as-primary-process versus the matched
# human-directed LLM-agent baseline, after #76 closes and a host binds
# identities.  No such live trial has been executed on any merged subject.
MISSING_PROMOTION_TRIAL_ID = "phase3:trial:governed-ordinary-development-promotion-v1"
MISSING_LONGITUDINAL_TRIAL_ID = "phase3:trial:longitudinal-stability-v1"

PROMOTION_RECEIPT_SCHEMA = "Phase3EmpiricalPromotionReceipt.v1"


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _is_bound_digest(value: str) -> bool:
    return _is_sha256(value) and value != UNBOUND_DIGEST


class Phase3PromotionStatus(str, Enum):
    """Outcomes of the empirical promotion assessment.

    Note what is absent: there is no ``CLOSED``, ``PASS``, ``AUTHORIZED`` or
    ``PROMOTED`` member.  The enum cannot express issue-#209 closure, so no
    caller can obtain one from this module.
    """

    CANNOT_CHECK = "CANNOT_CHECK"
    INVALID = "INVALID"


@dataclass(frozen=True)
class MissingTrial:
    """The live trial that would have to exist before promotion can be assessed."""

    trial_id: str
    description: str
    blocked_on: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.trial_id.strip() or not self.description.strip():
            raise ValueError("missing trial identity and description are required")
        if not self.blocked_on:
            raise ValueError("a missing trial must name at least one blocker")


MISSING_PROMOTION_TRIAL = MissingTrial(
    trial_id=MISSING_PROMOTION_TRIAL_ID,
    description=(
        "Prospective promotion study of at least "
        f"{PHASE3_UNCERTAINTY_POLICY.minimum_cycles} consecutive ordinary-development "
        "cycles in which ORION is the primary problem-solving process, compared "
        "against matched baseline phase3:baseline:human-directed-llm-agent-v1, "
        f"under frozen protocol {PHASE3_PROTOCOL_ID}, after issue #76 closes on "
        "merged Phase-2 evidence and a host binds the Phase-2 terminal subject, "
        "Phase-2 evidence receipt, external promotion-authority identity, "
        "protected custody lineage, sampling epoch and issue-pool fingerprint. "
        "No frozen live cycle receipts, baseline-comparison artifact, or "
        "independent fresh-transfer panel exist on any merged subject."
    ),
    blocked_on=(
        "issue_76_must_close_on_merged_phase2_evidence_first",
        "sampling_epoch_and_issue_pool_not_frozen",
        "no_frozen_live_governed_cycle_receipts",
        "no_matched_baseline_comparison_artifact",
        "no_independent_fresh_transfer_panel",
    ),
)


MISSING_LONGITUDINAL_TRIAL = MissingTrial(
    trial_id=MISSING_LONGITUDINAL_TRIAL_ID,
    description=(
        "Longitudinal stability trial required by issue #209 Step 6: an accepted "
        "governed change later used as a dependency of another governed cycle "
        "and remaining replayable; a previously rejected/harmful variant remaining "
        "queryable; halt/resume from immutable history; independent external replay "
        "of a promotion recommendation.  This trial cannot start until "
        f"{MISSING_PROMOTION_TRIAL_ID} has produced accepted-cycle receipts."
    ),
    blocked_on=(
        "depends_on:" + MISSING_PROMOTION_TRIAL_ID,
        "no_accepted_governed_change_receipts",
        "no_immutable_rejected_variant_index",
        "no_independent_external_replay_of_promotion_recommendation",
    ),
)


@dataclass(frozen=True)
class Phase3CycleReceiptClaim:
    """Candidate-supplied identity of one governed-cycle receipt.

    Presence of a SHA-256 string is not evidence.  An unbound sentinel, a
    duplicated hash, or a self-certified lineage is fabricated, not missing.
    """

    cycle_id: str
    receipt_hash: str
    subject_revision_hash: str = UNBOUND_DIGEST
    evaluator_artifact_hash: str = UNBOUND_DIGEST
    evaluation_epoch_id: str = ""
    producer_process_lineage_hash: str = UNBOUND_DIGEST
    verifier_process_lineage_hash: str = UNBOUND_DIGEST

    def __post_init__(self) -> None:
        if not self.cycle_id.strip():
            raise ValueError("cycle id is required")
        for digest in (
            self.receipt_hash,
            self.subject_revision_hash,
            self.evaluator_artifact_hash,
            self.producer_process_lineage_hash,
            self.verifier_process_lineage_hash,
        ):
            if not _is_sha256(digest):
                raise ValueError("cycle receipt digests must be SHA-256 or the unbound sentinel")


@dataclass(frozen=True)
class Phase3PromotionEvidence:
    """Host-visible empirical material.  The repository freeze supplies none."""

    protocol_id: str = PHASE3_PROTOCOL_ID
    cycle_receipts: tuple[Phase3CycleReceiptClaim, ...] = ()
    baseline_comparison_artifact_hash: str = UNBOUND_DIGEST
    independent_fresh_transfer_panel_hash: str = UNBOUND_DIGEST
    declared_consecutive_cycle_count: int = 0

    def __post_init__(self) -> None:
        if not self.protocol_id.strip():
            raise ValueError("protocol id is required")
        if self.declared_consecutive_cycle_count < 0:
            raise ValueError("declared cycle count cannot be negative")
        if not _is_sha256(self.baseline_comparison_artifact_hash):
            raise ValueError("baseline comparison hash must be SHA-256 or the unbound sentinel")
        if not _is_sha256(self.independent_fresh_transfer_panel_hash):
            raise ValueError("fresh-transfer panel hash must be SHA-256 or the unbound sentinel")


@dataclass(frozen=True)
class Phase3PromotionReport:
    status: Phase3PromotionStatus
    blockers: tuple[str, ...]
    missing_trials: tuple[MissingTrial, ...]
    protocol_id: str
    protocol_status: Phase3PreflightStatus
    evidence_status: EvidenceStatus
    measured_metric_ids: tuple[str, ...]
    unmeasured_metric_ids: tuple[str, ...]

    @property
    def grants_phase3_operating_authority(self) -> bool:
        return False

    @property
    def grants_governed_self_orion(self) -> bool:
        return False

    @property
    def closes_issue_209(self) -> bool:
        return False

    @property
    def emits_terminal_claim(self) -> bool:
        return False

    @property
    def terminal_claim(self) -> None:
        return None

    @property
    def primary_missing_trial_id(self) -> str:
        return self.missing_trials[0].trial_id if self.missing_trials else ""


def repository_phase3_promotion_evidence() -> Phase3PromotionEvidence:
    """The repository's empirical freeze: no live receipts, nothing fabricated."""

    return Phase3PromotionEvidence()


def _fabricated_receipt_blockers(
    receipts: tuple[Phase3CycleReceiptClaim, ...],
) -> list[str]:
    """Identity, not count: twelve unbound hashes are not twelve cycles."""

    blockers: list[str] = []
    hashes = [item.receipt_hash for item in receipts]
    ids = [item.cycle_id for item in receipts]
    if len(ids) != len(set(ids)):
        blockers.append("duplicate_cycle_id")
    if len(hashes) != len(set(hashes)):
        blockers.append("duplicate_cycle_receipt_hash")
    for item in receipts:
        if not _is_bound_digest(item.receipt_hash):
            blockers.append("cycle_receipt_identity_unbound")
        if not _is_bound_digest(item.subject_revision_hash):
            blockers.append("cycle_receipt_subject_unbound")
        if not _is_bound_digest(item.evaluator_artifact_hash):
            blockers.append("cycle_receipt_evaluator_unbound")
        if not item.evaluation_epoch_id.strip():
            blockers.append("cycle_receipt_epoch_missing")
        if not _is_bound_digest(item.producer_process_lineage_hash) or not _is_bound_digest(
            item.verifier_process_lineage_hash
        ):
            blockers.append("cycle_receipt_lineage_unbound")
        elif item.producer_process_lineage_hash == item.verifier_process_lineage_hash:
            blockers.append("cycle_receipt_self_certified")
    return list(dict.fromkeys(blockers))


def assess_phase3_empirical_promotion(
    evidence: Phase3PromotionEvidence,
    freeze: Phase3ProtocolFreeze | None = None,
) -> Phase3PromotionReport:
    """Assess live promotion evidence.  Never emit the terminal claim.

    Empty evidence is ``CANNOT_CHECK`` and names the missing trial.  Present
    but unbound/self-certified evidence is ``INVALID``.  A protocol-prefreeze
    merge is not evidence of either kind.
    """

    freeze = freeze if freeze is not None else repository_phase3_protocol_freeze()
    preflight = assess_phase3_preflight(freeze)
    metric_ids = tuple(metric.metric_id for metric in freeze.metrics)
    missing = (MISSING_PROMOTION_TRIAL, MISSING_LONGITUDINAL_TRIAL)

    def _report(
        status: Phase3PromotionStatus,
        blockers: tuple[str, ...],
        *,
        evidence_status: EvidenceStatus,
    ) -> Phase3PromotionReport:
        return Phase3PromotionReport(
            status=status,
            blockers=tuple(dict.fromkeys(blockers)),
            missing_trials=missing,
            protocol_id=freeze.protocol_id,
            protocol_status=preflight.status,
            evidence_status=evidence_status,
            measured_metric_ids=(),
            unmeasured_metric_ids=metric_ids,
        )

    blockers: list[str] = []
    if evidence.protocol_id != freeze.protocol_id:
        blockers.append("promotion_evidence_protocol_id_mismatch")
    if evidence.declared_consecutive_cycle_count and not evidence.cycle_receipts:
        blockers.append("declared_cycle_count_without_receipt_identities")
    if (
        evidence.declared_consecutive_cycle_count
        and evidence.cycle_receipts
        and evidence.declared_consecutive_cycle_count != len(evidence.cycle_receipts)
    ):
        blockers.append("declared_cycle_count_does_not_match_receipt_identities")
    if evidence.cycle_receipts:
        blockers.extend(_fabricated_receipt_blockers(evidence.cycle_receipts))
    if _is_bound_digest(evidence.baseline_comparison_artifact_hash) and not evidence.cycle_receipts:
        blockers.append("baseline_comparison_without_cycle_receipts")
    if (
        _is_bound_digest(evidence.independent_fresh_transfer_panel_hash)
        and not evidence.cycle_receipts
    ):
        blockers.append("fresh_transfer_panel_without_cycle_receipts")

    if blockers:
        return _report(
            Phase3PromotionStatus.INVALID,
            tuple(blockers),
            evidence_status=EvidenceStatus.FAIL,
        )

    cannot_check: list[str] = []
    if preflight.status is Phase3PreflightStatus.INVALID:
        return _report(
            Phase3PromotionStatus.INVALID,
            preflight.blockers,
            evidence_status=EvidenceStatus.FAIL,
        )
    if preflight.status is not Phase3PreflightStatus.REQUEST_EXTERNAL_PHASE3_AUTHORIZATION:
        cannot_check.extend(preflight.blockers)
    if not evidence.cycle_receipts:
        cannot_check.append("no_frozen_live_governed_cycle_receipts")
    if not _is_bound_digest(evidence.baseline_comparison_artifact_hash):
        cannot_check.append("no_matched_baseline_comparison_artifact")
    if not _is_bound_digest(evidence.independent_fresh_transfer_panel_hash):
        cannot_check.append("no_independent_fresh_transfer_panel")
    if len(evidence.cycle_receipts) < freeze.uncertainty.minimum_cycles:
        cannot_check.append(
            "consecutive_cycle_count_below_predeclared_minimum:"
            + str(freeze.uncertainty.minimum_cycles)
        )

    return _report(
        Phase3PromotionStatus.CANNOT_CHECK,
        tuple(cannot_check),
        evidence_status=EvidenceStatus.CANNOT_CHECK,
    )


def phase3_promotion_receipt_to_dict(report: Phase3PromotionReport) -> dict[str, object]:
    """Serialize the empirical receipt.  The terminal claim is never a field value."""

    return {
        "schema": PROMOTION_RECEIPT_SCHEMA,
        "protocol_id": report.protocol_id,
        "status": report.status.value,
        "evidence_status": report.evidence_status.value,
        "protocol_status": report.protocol_status.value,
        "blockers": list(report.blockers),
        "missing_trials": [
            {
                "trial_id": trial.trial_id,
                "description": trial.description,
                "blocked_on": list(trial.blocked_on),
            }
            for trial in report.missing_trials
        ],
        "primary_missing_trial_id": report.primary_missing_trial_id,
        "measured_metric_ids": list(report.measured_metric_ids),
        "unmeasured_metric_ids": list(report.unmeasured_metric_ids),
        "grants_phase3_operating_authority": report.grants_phase3_operating_authority,
        "grants_governed_self_orion": report.grants_governed_self_orion,
        "closes_issue_209": report.closes_issue_209,
        "emits_terminal_claim": report.emits_terminal_claim,
        "terminal_claim": report.terminal_claim,
        "phase_3_governed_self_orion_closed": False,
    }


__all__ = [
    "MISSING_LONGITUDINAL_TRIAL",
    "MISSING_LONGITUDINAL_TRIAL_ID",
    "MISSING_PROMOTION_TRIAL",
    "MISSING_PROMOTION_TRIAL_ID",
    "PHASE3_TERMINAL_CLAIM",
    "PROMOTION_RECEIPT_SCHEMA",
    "MissingTrial",
    "Phase3CycleReceiptClaim",
    "Phase3PromotionEvidence",
    "Phase3PromotionReport",
    "Phase3PromotionStatus",
    "assess_phase3_empirical_promotion",
    "phase3_promotion_receipt_to_dict",
    "repository_phase3_promotion_evidence",
]
