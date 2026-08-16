from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.self_orion.phase2_campaign import (
    Phase2CampaignCriterion,
    Phase2CampaignEvidence,
    Phase2CampaignReport,
    Phase2CampaignStage,
    assess_phase2_campaign,
)
from orion.self_orion.phase2_terminal_receipts import (
    FailureReplayReceipt,
    FinalIntegrationReceipt,
    FinalIntegrationStatus,
)


class Phase2TerminalStage(str, Enum):
    EARLIER_CAMPAIGN_GATE = "EARLIER_CAMPAIGN_GATE"
    COMPLETE_FAILURE_REPLAY = "COMPLETE_FAILURE_REPLAY"
    VERIFY_FINAL_INTEGRATION = "VERIFY_FINAL_INTEGRATION"
    HAND_BACK_EXTERNAL_EVIDENCE = "HAND_BACK_EXTERNAL_EVIDENCE"
    READY_FOR_TERMINAL_AUDIT = "READY_FOR_TERMINAL_AUDIT"
    INVALID = "INVALID"


@dataclass(frozen=True)
class Phase2TerminalEvidence:
    campaign: Phase2CampaignEvidence
    failure_replay: FailureReplayReceipt | None = None
    final_integration: FinalIntegrationReceipt | None = None
    failure_replay_file_blockers: tuple[str, ...] = ()
    final_integration_file_blockers: tuple[str, ...] = ()


@dataclass(frozen=True)
class Phase2TerminalReport:
    stage: Phase2TerminalStage
    blockers: tuple[str, ...]
    base_campaign_stage: Phase2CampaignStage
    packet_fingerprint: str | None
    live_trial_artifact_hash: str | None
    development_trial_artifact_hash: str | None
    authority_trial_artifact_hash: str | None
    authority_benchmark_panel_hash: str | None
    authority_campaign_artifact_hash: str | None
    failure_replay_artifact_hash: str | None
    final_integration_artifact_hash: str | None
    external_observation_bundle_hash: str | None

    @property
    def ready_for_terminal_audit(self) -> bool:
        return (
            self.stage is Phase2TerminalStage.READY_FOR_TERMINAL_AUDIT
            and not self.blockers
        )

    @property
    def grants_phase2_closure(self) -> bool:
        return False

    @property
    def grants_governed_self_orion(self) -> bool:
        return False


def _report(
    stage: Phase2TerminalStage,
    blockers: tuple[str, ...] | list[str],
    base: Phase2CampaignReport,
    *,
    failure_replay: FailureReplayReceipt | None = None,
    final_integration: FinalIntegrationReceipt | None = None,
) -> Phase2TerminalReport:
    return Phase2TerminalReport(
        stage=stage,
        blockers=tuple(dict.fromkeys(blockers)),
        base_campaign_stage=base.stage,
        packet_fingerprint=base.packet_fingerprint,
        live_trial_artifact_hash=base.live_trial_artifact_hash,
        development_trial_artifact_hash=base.development_trial_artifact_hash,
        authority_trial_artifact_hash=base.authority_trial_artifact_hash,
        authority_benchmark_panel_hash=base.authority_benchmark_panel_hash,
        authority_campaign_artifact_hash=base.authority_campaign_artifact_hash,
        failure_replay_artifact_hash=(
            failure_replay.artifact_hash if failure_replay is not None else None
        ),
        final_integration_artifact_hash=(
            final_integration.artifact_hash if final_integration is not None else None
        ),
        external_observation_bundle_hash=base.external_observation_bundle_hash,
    )


def _campaign_without_handback(
    evidence: Phase2CampaignEvidence,
) -> Phase2CampaignEvidence:
    return Phase2CampaignEvidence(
        preflight=evidence.preflight,
        live_trial=evidence.live_trial,
        baseline_bundle_hash=evidence.baseline_bundle_hash,
        development_trial=evidence.development_trial,
        authority_trial=evidence.authority_trial,
        authority_benchmark=evidence.authority_benchmark,
        external_observations=None,
        flagship_external_manifest=None,
    )


def assess_phase2_terminal(
    evidence: Phase2TerminalEvidence,
) -> Phase2TerminalReport:
    """Require Gates E/F before the existing external handback can become terminal-ready."""

    campaign = evidence.campaign
    preflight = campaign.preflight
    pre_handback = assess_phase2_campaign(_campaign_without_handback(campaign))
    if pre_handback.stage is not Phase2CampaignStage.HAND_BACK_EXTERNAL_EVIDENCE:
        stage = (
            Phase2TerminalStage.INVALID
            if pre_handback.stage is Phase2CampaignStage.INVALID
            else Phase2TerminalStage.EARLIER_CAMPAIGN_GATE
        )
        return _report(stage, pre_handback.blockers, pre_handback)

    replay = evidence.failure_replay
    replay_blockers = list(evidence.failure_replay_file_blockers)
    if replay is None:
        replay_blockers.append("failure_replay_receipt_missing")
    else:
        if replay.subject_revision_hash != preflight.subject_revision_hash:
            replay_blockers.append("failure_replay_subject_mismatch")
        if replay.evaluator_artifact_hash != preflight.evaluator_artifact_hash:
            replay_blockers.append("failure_replay_evaluator_mismatch")
        if replay.evaluation_epoch_id != preflight.evaluation_epoch_id:
            replay_blockers.append("failure_replay_epoch_mismatch")
        if not replay.independently_verified:
            replay_blockers.append("failure_replay_self_verified")
    if replay_blockers:
        return _report(
            Phase2TerminalStage.COMPLETE_FAILURE_REPLAY,
            replay_blockers,
            pre_handback,
            failure_replay=replay,
        )

    integration = evidence.final_integration
    integration_blockers = list(evidence.final_integration_file_blockers)
    if integration is None:
        integration_blockers.append("final_integration_receipt_missing")
    else:
        if integration.subject_revision_hash != preflight.subject_revision_hash:
            integration_blockers.append("final_integration_subject_mismatch")
        if integration.evaluator_artifact_hash != preflight.evaluator_artifact_hash:
            integration_blockers.append("final_integration_evaluator_mismatch")
        if integration.evaluation_epoch_id != preflight.evaluation_epoch_id:
            integration_blockers.append("final_integration_epoch_mismatch")
        if not integration.independently_verified:
            integration_blockers.append("final_integration_self_verified")
        if integration.status is FinalIntegrationStatus.CANNOT_CHECK:
            integration_blockers.append("final_integration_cannot_check")
        elif integration.status is FinalIntegrationStatus.FAIL:
            integration_blockers.append("final_integration_failed")
        if integration.failure_replay_artifact_hash != replay.artifact_hash:
            integration_blockers.append("final_integration_failure_replay_mismatch")
    if integration_blockers:
        return _report(
            Phase2TerminalStage.VERIFY_FINAL_INTEGRATION,
            integration_blockers,
            pre_handback,
            failure_replay=replay,
            final_integration=integration,
        )

    observations = campaign.external_observations
    receipt_observation_blockers: list[str] = []
    if observations is None:
        receipt_observation_blockers.append("phase2_external_observation_bundle_missing")
    else:
        by_criterion = {
            observation.criterion: observation
            for observation in observations.observations
        }
        replay_observation = by_criterion.get(Phase2CampaignCriterion.FAILURE_REPLAY)
        if replay_observation is None:
            receipt_observation_blockers.append(
                "external_observation_missing:FAILURE_REPLAY"
            )
        elif replay_observation.evidence_artifact_hash != replay.artifact_hash:
            receipt_observation_blockers.append(
                "external_observation_artifact_mismatch:FAILURE_REPLAY"
            )
        integration_observation = by_criterion.get(
            Phase2CampaignCriterion.FINAL_INTEGRATION
        )
        if integration_observation is None:
            receipt_observation_blockers.append(
                "external_observation_missing:FINAL_INTEGRATION"
            )
        elif (
            integration_observation.evidence_artifact_hash
            != integration.artifact_hash
        ):
            receipt_observation_blockers.append(
                "external_observation_artifact_mismatch:FINAL_INTEGRATION"
            )
    if receipt_observation_blockers:
        return _report(
            Phase2TerminalStage.HAND_BACK_EXTERNAL_EVIDENCE,
            receipt_observation_blockers,
            pre_handback,
            failure_replay=replay,
            final_integration=integration,
        )

    base = assess_phase2_campaign(campaign)
    if base.stage is not Phase2CampaignStage.READY_FOR_TERMINAL_AUDIT:
        return _report(
            Phase2TerminalStage.HAND_BACK_EXTERNAL_EVIDENCE,
            base.blockers,
            base,
            failure_replay=replay,
            final_integration=integration,
        )
    return _report(
        Phase2TerminalStage.READY_FOR_TERMINAL_AUDIT,
        (),
        base,
        failure_replay=replay,
        final_integration=integration,
    )


__all__ = [
    "Phase2TerminalEvidence",
    "Phase2TerminalReport",
    "Phase2TerminalStage",
    "assess_phase2_terminal",
]
