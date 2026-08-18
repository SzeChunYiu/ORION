"""Non-authorizing Self-ORION control composition for T1–T6 receipts.

The controller is deliberately read-only. It composes already-bound formal
reports and recommends only the *class of next step*. It cannot execute a tool,
mutate scientific state, adopt a revision, promote a claim, merge code, or close
a global research task.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from orion.self_orion.revision_gate import RevisionGateReport, RevisionGateStatus
from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.epistemic_computation import (
    ComputationSelectionReport,
    ComputationSelectionStatus,
)
from orion.transfer.v2.social_evidence import (
    SocialEvidenceIndependenceReport,
    SocialEvidenceIndependenceStatus,
)
from orion.transfer.v2.uncertainty_containment import (
    ContainmentReport,
    ContainmentStatus,
)


class EpistemicControlStatus(str, Enum):
    COMPUTATION_REQUIRED = "COMPUTATION_REQUIRED"
    COMPUTATION_RECOMMENDED = "COMPUTATION_RECOMMENDED"
    COMPUTATION_AMBIGUOUS = "COMPUTATION_AMBIGUOUS"
    SOCIAL_EVIDENCE_REQUIRED = "SOCIAL_EVIDENCE_REQUIRED"
    CONTAINED = "CONTAINED"
    REVISION_CANDIDATE = "REVISION_CANDIDATE"
    REVISION_AMBIGUOUS = "REVISION_AMBIGUOUS"
    LOCAL_COMPUTATION_STOP = "LOCAL_COMPUTATION_STOP"
    NO_ADMISSIBLE_ACTION = "NO_ADMISSIBLE_ACTION"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class EpistemicControlDecision:
    claim_id: str
    status: EpistemicControlStatus
    revision_digest: str
    computation_digest: str
    containment_digest: str | None
    social_evidence_digests: tuple[str, ...]
    selected_computation_action_id: str | None
    selected_computation_action_digest: str | None
    selected_revision_mechanic_id: str | None
    selected_revision_mechanic_digest: str | None
    reasons: tuple[str, ...]
    digest: str

    @property
    def grants_scientific_authority(self) -> bool:
        return False

    @property
    def grants_revision_authority(self) -> bool:
        return False

    @property
    def grants_adoption_authority(self) -> bool:
        return False

    @property
    def grants_promotion_authority(self) -> bool:
        return False

    @property
    def grants_merge_authority(self) -> bool:
        return False

    @property
    def grants_global_task_stop_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "SelfOrionEpistemicControlDecision.v1",
            "claim_id": self.claim_id,
            "status": self.status.value,
            "revision_digest": self.revision_digest,
            "computation_digest": self.computation_digest,
            "containment_digest": self.containment_digest,
            "social_evidence_digests": list(self.social_evidence_digests),
            "selected_computation_action_id": self.selected_computation_action_id,
            "selected_computation_action_digest": self.selected_computation_action_digest,
            "selected_revision_mechanic_id": self.selected_revision_mechanic_id,
            "selected_revision_mechanic_digest": self.selected_revision_mechanic_digest,
            "reasons": list(self.reasons),
            "grants_scientific_authority": False,
            "grants_revision_authority": False,
            "grants_adoption_authority": False,
            "grants_promotion_authority": False,
            "grants_merge_authority": False,
            "grants_global_task_stop_authority": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("epistemic control decision digest mismatch")
        computation_selected = self.status in {
            EpistemicControlStatus.COMPUTATION_REQUIRED,
            EpistemicControlStatus.COMPUTATION_RECOMMENDED,
        }
        revision_selected = self.status is EpistemicControlStatus.REVISION_CANDIDATE
        if computation_selected:
            if self.selected_computation_action_id is None or self.selected_computation_action_digest is None:
                raise ValueError("computation control decision requires selected action")
        elif self.selected_computation_action_id is not None or self.selected_computation_action_digest is not None:
            raise ValueError("non-computation decision cannot select computation action")
        if revision_selected:
            if self.selected_revision_mechanic_id is None or self.selected_revision_mechanic_digest is None:
                raise ValueError("revision control decision requires selected mechanic")
        elif self.selected_revision_mechanic_id is not None or self.selected_revision_mechanic_digest is not None:
            raise ValueError("non-revision decision cannot select revision mechanic")


def _decision(
    *,
    claim_id: str,
    status: EpistemicControlStatus,
    revision: RevisionGateReport,
    computation: ComputationSelectionReport,
    containment: ContainmentReport | None,
    social_evidence: Sequence[SocialEvidenceIndependenceReport],
    selected_computation_action_id: str | None = None,
    selected_computation_action_digest: str | None = None,
    selected_revision_mechanic_id: str | None = None,
    selected_revision_mechanic_digest: str | None = None,
    reasons: Sequence[str] = (),
) -> EpistemicControlDecision:
    reason_tuple = tuple(sorted(set(map(str, reasons))))
    social_digests = tuple(sorted(report.digest for report in social_evidence))
    payload = {
        "version": "SelfOrionEpistemicControlDecision.v1",
        "claim_id": claim_id,
        "status": status.value,
        "revision_digest": revision.digest,
        "computation_digest": computation.digest,
        "containment_digest": None if containment is None else containment.digest,
        "social_evidence_digests": list(social_digests),
        "selected_computation_action_id": selected_computation_action_id,
        "selected_computation_action_digest": selected_computation_action_digest,
        "selected_revision_mechanic_id": selected_revision_mechanic_id,
        "selected_revision_mechanic_digest": selected_revision_mechanic_digest,
        "reasons": list(reason_tuple),
        "grants_scientific_authority": False,
        "grants_revision_authority": False,
        "grants_adoption_authority": False,
        "grants_promotion_authority": False,
        "grants_merge_authority": False,
        "grants_global_task_stop_authority": False,
    }
    decision = EpistemicControlDecision(
        claim_id=claim_id,
        status=status,
        revision_digest=revision.digest,
        computation_digest=computation.digest,
        containment_digest=payload["containment_digest"],
        social_evidence_digests=social_digests,
        selected_computation_action_id=selected_computation_action_id,
        selected_computation_action_digest=selected_computation_action_digest,
        selected_revision_mechanic_id=selected_revision_mechanic_id,
        selected_revision_mechanic_digest=selected_revision_mechanic_digest,
        reasons=reason_tuple,
        digest=content_digest(payload),
    )
    decision.verify()
    return decision


def compose_epistemic_control(
    *,
    revision: RevisionGateReport,
    computation: ComputationSelectionReport,
    containment: ContainmentReport | None = None,
    social_evidence: Sequence[SocialEvidenceIndependenceReport] = (),
    require_independent_social_evidence: bool = False,
) -> EpistemicControlDecision:
    """Compose T1–T6 formal receipts into one non-authorizing next-step decision."""

    revision.verify()
    computation.verify()
    if containment is not None:
        containment.verify()
    for report in social_evidence:
        report.verify()

    claim_id = revision.claim_id
    if computation.claim_id != claim_id:
        raise ValueError("epistemic control composition is claim-relative")
    if containment is not None and containment.claim_id != claim_id:
        raise ValueError("epistemic control composition is claim-relative")
    if any(report.claim_id != claim_id for report in social_evidence):
        raise ValueError("epistemic control composition is claim-relative")

    # Stage 1: hard computation obligations are non-compensatory.
    if computation.active_hard_obligations:
        if computation.status is ComputationSelectionStatus.SELECTED:
            return _decision(
                claim_id=claim_id,
                status=EpistemicControlStatus.COMPUTATION_REQUIRED,
                revision=revision,
                computation=computation,
                containment=containment,
                social_evidence=social_evidence,
                selected_computation_action_id=computation.selected_action_id,
                selected_computation_action_digest=computation.selected_action_digest,
                reasons=("HARD_COMPUTATION_OBLIGATION_PRECEDENCE",),
            )
        if computation.status is ComputationSelectionStatus.MULTIPLE_OPTIMA:
            return _decision(
                claim_id=claim_id,
                status=EpistemicControlStatus.COMPUTATION_AMBIGUOUS,
                revision=revision,
                computation=computation,
                containment=containment,
                social_evidence=social_evidence,
                reasons=("HARD_COMPUTATION_OBLIGATION_HAS_MULTIPLE_OPTIMA",),
            )
        if computation.status is ComputationSelectionStatus.NO_ADMISSIBLE:
            return _decision(
                claim_id=claim_id,
                status=EpistemicControlStatus.NO_ADMISSIBLE_ACTION,
                revision=revision,
                computation=computation,
                containment=containment,
                social_evidence=social_evidence,
                reasons=("HARD_COMPUTATION_OBLIGATION_UNCOVERED",),
            )
        return _decision(
            claim_id=claim_id,
            status=EpistemicControlStatus.UNRESOLVED,
            revision=revision,
            computation=computation,
            containment=containment,
            social_evidence=social_evidence,
            reasons=("HARD_COMPUTATION_OBLIGATION_UNRESOLVED",),
        )

    # Stage 2: explicitly required independent social evidence is a hard evidence condition.
    if require_independent_social_evidence:
        if not social_evidence:
            return _decision(
                claim_id=claim_id,
                status=EpistemicControlStatus.SOCIAL_EVIDENCE_REQUIRED,
                revision=revision,
                computation=computation,
                containment=containment,
                social_evidence=social_evidence,
                reasons=("SOCIAL_EVIDENCE_MISSING",),
            )
        nonindependent = [
            report for report in social_evidence
            if report.status is not SocialEvidenceIndependenceStatus.INDEPENDENT
        ]
        if nonindependent:
            reasons = [f"SOCIAL_EVIDENCE_NOT_INDEPENDENT:{report.status.value}" for report in nonindependent]
            return _decision(
                claim_id=claim_id,
                status=EpistemicControlStatus.SOCIAL_EVIDENCE_REQUIRED,
                revision=revision,
                computation=computation,
                containment=containment,
                social_evidence=social_evidence,
                reasons=reasons,
            )

    # Stage 3: containment governs material action scope, not truth.
    if containment is not None:
        if containment.status is ContainmentStatus.BLOCKED:
            return _decision(
                claim_id=claim_id,
                status=EpistemicControlStatus.CONTAINED,
                revision=revision,
                computation=computation,
                containment=containment,
                social_evidence=social_evidence,
                reasons=("CURRENT_CONTEXT_OUTSIDE_VALIDITY_ENVELOPE",),
            )
        if containment.status is ContainmentStatus.UNRESOLVED:
            return _decision(
                claim_id=claim_id,
                status=EpistemicControlStatus.UNRESOLVED,
                revision=revision,
                computation=computation,
                containment=containment,
                social_evidence=social_evidence,
                reasons=("CURRENT_CONTEXT_VALIDITY_UNRESOLVED",),
            )

    # Stage 4: an already admissible bounded revision beats optional computation.
    if revision.status is RevisionGateStatus.CANDIDATE_SELECTED:
        return _decision(
            claim_id=claim_id,
            status=EpistemicControlStatus.REVISION_CANDIDATE,
            revision=revision,
            computation=computation,
            containment=containment,
            social_evidence=social_evidence,
            selected_revision_mechanic_id=revision.selected_mechanic_id,
            selected_revision_mechanic_digest=revision.selected_mechanic_digest,
            reasons=("BOUNDED_REVISION_ALREADY_SELECTABLE",),
        )
    if revision.status is RevisionGateStatus.MULTIPLE_MINIMA:
        return _decision(
            claim_id=claim_id,
            status=EpistemicControlStatus.REVISION_AMBIGUOUS,
            revision=revision,
            computation=computation,
            containment=containment,
            social_evidence=social_evidence,
            reasons=("MULTIPLE_MINIMAL_REVISIONS",),
        )

    # Stage 5: when revision is not selectable, optional compute may gather more evidence.
    if computation.status is ComputationSelectionStatus.SELECTED:
        return _decision(
            claim_id=claim_id,
            status=EpistemicControlStatus.COMPUTATION_RECOMMENDED,
            revision=revision,
            computation=computation,
            containment=containment,
            social_evidence=social_evidence,
            selected_computation_action_id=computation.selected_action_id,
            selected_computation_action_digest=computation.selected_action_digest,
            reasons=("REVISION_NOT_YET_SELECTABLE_OPTIONAL_COMPUTE_AVAILABLE",),
        )
    if computation.status is ComputationSelectionStatus.MULTIPLE_OPTIMA:
        return _decision(
            claim_id=claim_id,
            status=EpistemicControlStatus.COMPUTATION_AMBIGUOUS,
            revision=revision,
            computation=computation,
            containment=containment,
            social_evidence=social_evidence,
            reasons=("REVISION_NOT_YET_SELECTABLE_MULTIPLE_COMPUTE_OPTIMA",),
        )
    if computation.status is ComputationSelectionStatus.UNRESOLVED:
        return _decision(
            claim_id=claim_id,
            status=EpistemicControlStatus.UNRESOLVED,
            revision=revision,
            computation=computation,
            containment=containment,
            social_evidence=social_evidence,
            reasons=("COMPUTATION_SELECTION_UNRESOLVED",),
        )

    # Stage 6: residual non-authorizing terminals.
    if revision.status in {RevisionGateStatus.NO_ADMISSIBLE, RevisionGateStatus.INTERFACE_REPAIR_REQUIRED}:
        return _decision(
            claim_id=claim_id,
            status=EpistemicControlStatus.NO_ADMISSIBLE_ACTION,
            revision=revision,
            computation=computation,
            containment=containment,
            social_evidence=social_evidence,
            reasons=(f"REVISION_GATE:{revision.status.value}", f"COMPUTATION:{computation.status.value}"),
        )
    if revision.status is RevisionGateStatus.UNRESOLVED and computation.status is ComputationSelectionStatus.LOCAL_COMPUTATION_STOP:
        return _decision(
            claim_id=claim_id,
            status=EpistemicControlStatus.LOCAL_COMPUTATION_STOP,
            revision=revision,
            computation=computation,
            containment=containment,
            social_evidence=social_evidence,
            reasons=("NO_POSITIVE_LOCAL_COMPUTATION_VALUE", "GLOBAL_TASK_REMAINS_OPEN"),
        )
    return _decision(
        claim_id=claim_id,
        status=EpistemicControlStatus.UNRESOLVED,
        revision=revision,
        computation=computation,
        containment=containment,
        social_evidence=social_evidence,
        reasons=(f"REVISION_GATE:{revision.status.value}", f"COMPUTATION:{computation.status.value}"),
    )


__all__ = [
    "EpistemicControlDecision",
    "EpistemicControlStatus",
    "compose_epistemic_control",
]
