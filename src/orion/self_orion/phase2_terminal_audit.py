from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from orion.self_orion.evidence_admission import (
    EvidenceAdmissionReport,
    Phase2EvidenceReceipt,
    verify_phase2_observation_bundle_artifacts,
)
from orion.self_orion.phase2_campaign import (
    Phase2CampaignEvidence,
    Phase2CampaignReport,
    assess_phase2_campaign,
)


class Phase2TerminalAuditStatus(str, Enum):
    CAMPAIGN_NOT_READY = "CAMPAIGN_NOT_READY"
    EXTERNAL_EVIDENCE_NOT_ADMITTED = "EXTERNAL_EVIDENCE_NOT_ADMITTED"
    ELIGIBLE_FOR_EXTERNAL_CLOSURE = "ELIGIBLE_FOR_EXTERNAL_CLOSURE"


@dataclass(frozen=True)
class Phase2TerminalAuditReport:
    status: Phase2TerminalAuditStatus
    blockers: tuple[str, ...]
    campaign: Phase2CampaignReport
    evidence_admission: EvidenceAdmissionReport | None

    @property
    def eligible_for_external_closure(self) -> bool:
        return (
            self.status is Phase2TerminalAuditStatus.ELIGIBLE_FOR_EXTERNAL_CLOSURE
            and not self.blockers
        )

    @property
    def grants_phase2_closure(self) -> bool:
        """External authority, not this process, owns the phase transition."""

        return False

    @property
    def grants_governed_self_orion(self) -> bool:
        return False


def audit_phase2_terminal(
    evidence: Phase2CampaignEvidence,
    receipt: Phase2EvidenceReceipt,
    artifact_root: str | Path,
) -> Phase2TerminalAuditReport:
    """Recompute campaign readiness and then verify result-bearing bytes.

    This is deliberately downstream of ``assess_phase2_campaign``.  A caller
    cannot submit a declaration saying that the campaign was ready: the
    campaign report is recomputed from the evidence object.  Even a campaign
    that reaches READY_FOR_TERMINAL_AUDIT remains non-authoritative until the
    host-visible external-observation artifacts are admitted byte-for-byte.
    """

    campaign = assess_phase2_campaign(evidence)
    if not campaign.ready_for_terminal_audit:
        blockers = campaign.blockers or ("phase2_campaign_not_ready",)
        return Phase2TerminalAuditReport(
            status=Phase2TerminalAuditStatus.CAMPAIGN_NOT_READY,
            blockers=tuple(f"campaign:{item}" for item in blockers),
            campaign=campaign,
            evidence_admission=None,
        )

    observations = evidence.external_observations
    if observations is None:
        # Defensive even though a ready campaign currently cannot reach here
        # without the bundle.  Terminal authority should not rely on that
        # upstream implementation fact remaining true forever.
        return Phase2TerminalAuditReport(
            status=Phase2TerminalAuditStatus.EXTERNAL_EVIDENCE_NOT_ADMITTED,
            blockers=("external_observation_bundle_missing_at_terminal_audit",),
            campaign=campaign,
            evidence_admission=None,
        )

    admission = verify_phase2_observation_bundle_artifacts(
        observations,
        receipt,
        artifact_root,
    )
    if not admission.admitted:
        return Phase2TerminalAuditReport(
            status=Phase2TerminalAuditStatus.EXTERNAL_EVIDENCE_NOT_ADMITTED,
            blockers=tuple(f"evidence:{item}" for item in admission.blockers),
            campaign=campaign,
            evidence_admission=admission,
        )

    return Phase2TerminalAuditReport(
        status=Phase2TerminalAuditStatus.ELIGIBLE_FOR_EXTERNAL_CLOSURE,
        blockers=(),
        campaign=campaign,
        evidence_admission=admission,
    )


__all__ = [
    "Phase2TerminalAuditReport",
    "Phase2TerminalAuditStatus",
    "audit_phase2_terminal",
]
