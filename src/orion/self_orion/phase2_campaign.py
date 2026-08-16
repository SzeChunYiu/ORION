from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum

from orion.benchmarks.external_evidence import ExternalEvidenceManifest
from orion.self_orion.authority_trial import AuthorityTrialReport
from orion.self_orion.development_trial import ShadowDevelopmentTrialReport
from orion.self_orion.live_trial import ShadowLiveTrialReport
from orion.self_orion.phase2_preflight import (
    Phase2ClosurePreflight,
    Phase2PreflightStatus,
    assess_phase2_preflight,
    build_frozen_live_trial_packet,
)


class Phase2CampaignStage(str, Enum):
    BIND_EXTERNALS = "BIND_EXTERNALS"
    EXECUTE_LIVE_TRIAL = "EXECUTE_LIVE_TRIAL"
    EXECUTE_SHADOW_DEVELOPMENT = "EXECUTE_SHADOW_DEVELOPMENT"
    EXECUTE_AUTHORITY_TRIAL = "EXECUTE_AUTHORITY_TRIAL"
    HAND_BACK_EXTERNAL_EVIDENCE = "HAND_BACK_EXTERNAL_EVIDENCE"
    READY_FOR_TERMINAL_AUDIT = "READY_FOR_TERMINAL_AUDIT"
    INVALID = "INVALID"


class Phase2CampaignCriterion(str, Enum):
    LIVE_TRIAL = "LIVE_TRIAL"
    MATCHED_BASELINE = "MATCHED_BASELINE"
    SHADOW_DEVELOPMENT = "SHADOW_DEVELOPMENT"
    AUTHORITY_BATTERY = "AUTHORITY_BATTERY"
    FAILURE_REPLAY = "FAILURE_REPLAY"
    FINAL_INTEGRATION = "FINAL_INTEGRATION"


class Phase2ExternalObservationStatus(str, Enum):
    COMPLETE = "COMPLETE"
    BLOCKING_FAILURE = "BLOCKING_FAILURE"


def _sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


@dataclass(frozen=True)
class Phase2ExternalObservation:
    criterion: Phase2CampaignCriterion
    evidence_artifact_id: str
    evidence_artifact_hash: str
    subject_revision_hash: str
    evaluator_artifact_hash: str
    producer_process_lineage_hash: str
    verifier_process_lineage_hash: str
    evaluation_epoch_id: str
    split_id: str
    status: Phase2ExternalObservationStatus
    frozen_before_candidate: bool
    fresh_split: bool
    note: str

    def __post_init__(self) -> None:
        if any(
            not value.strip()
            for value in (
                self.evidence_artifact_id,
                self.evaluation_epoch_id,
                self.split_id,
                self.note,
            )
        ):
            raise ValueError("Phase-2 external observation identity/epoch/split/note are required")
        for digest in (
            self.evidence_artifact_hash,
            self.subject_revision_hash,
            self.evaluator_artifact_hash,
            self.producer_process_lineage_hash,
            self.verifier_process_lineage_hash,
        ):
            if not _sha256(digest):
                raise ValueError("Phase-2 external observation bindings must be SHA-256")

    @property
    def independently_verified(self) -> bool:
        return self.producer_process_lineage_hash != self.verifier_process_lineage_hash


@dataclass(frozen=True)
class Phase2ExternalObservationBundle:
    bundle_id: str
    subject_revision_hash: str
    evaluator_artifact_hash: str
    evaluation_epoch_id: str
    observations: tuple[Phase2ExternalObservation, ...]

    def __post_init__(self) -> None:
        if not self.bundle_id.strip() or not self.evaluation_epoch_id.strip():
            raise ValueError("Phase-2 observation bundle identity/epoch are required")
        if not _sha256(self.subject_revision_hash) or not _sha256(self.evaluator_artifact_hash):
            raise ValueError("Phase-2 observation bundle subject/evaluator must be SHA-256")

    @property
    def artifact_hash(self) -> str:
        payload = {
            "bundle_id": self.bundle_id,
            "subject_revision_hash": self.subject_revision_hash,
            "evaluator_artifact_hash": self.evaluator_artifact_hash,
            "evaluation_epoch_id": self.evaluation_epoch_id,
            "observations": [
                {
                    "criterion": item.criterion.value,
                    "evidence_artifact_id": item.evidence_artifact_id,
                    "evidence_artifact_hash": item.evidence_artifact_hash,
                    "subject_revision_hash": item.subject_revision_hash,
                    "evaluator_artifact_hash": item.evaluator_artifact_hash,
                    "producer_process_lineage_hash": item.producer_process_lineage_hash,
                    "verifier_process_lineage_hash": item.verifier_process_lineage_hash,
                    "evaluation_epoch_id": item.evaluation_epoch_id,
                    "split_id": item.split_id,
                    "status": item.status.value,
                    "frozen_before_candidate": item.frozen_before_candidate,
                    "fresh_split": item.fresh_split,
                    "note": item.note,
                }
                for item in self.observations
            ],
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


@dataclass(frozen=True)
class Phase2CampaignEvidence:
    preflight: Phase2ClosurePreflight
    live_trial: ShadowLiveTrialReport | None = None
    baseline_bundle_hash: str = ""
    development_trial: ShadowDevelopmentTrialReport | None = None
    authority_trial: AuthorityTrialReport | None = None
    external_observations: Phase2ExternalObservationBundle | None = None
    flagship_external_manifest: ExternalEvidenceManifest | None = None


@dataclass(frozen=True)
class Phase2CampaignReport:
    stage: Phase2CampaignStage
    blockers: tuple[str, ...]
    packet_fingerprint: str | None
    live_trial_artifact_hash: str | None
    development_trial_artifact_hash: str | None
    authority_trial_artifact_hash: str | None
    external_observation_bundle_hash: str | None

    @property
    def ready_for_terminal_audit(self) -> bool:
        return self.stage is Phase2CampaignStage.READY_FOR_TERMINAL_AUDIT and not self.blockers

    @property
    def grants_phase2_closure(self) -> bool:
        return False

    @property
    def grants_governed_self_orion(self) -> bool:
        return False


def _report(
    stage: Phase2CampaignStage,
    blockers: list[str],
    *,
    packet_fingerprint: str | None = None,
    live: ShadowLiveTrialReport | None = None,
    development: ShadowDevelopmentTrialReport | None = None,
    authority: AuthorityTrialReport | None = None,
    observations: Phase2ExternalObservationBundle | None = None,
) -> Phase2CampaignReport:
    return Phase2CampaignReport(
        stage=stage,
        blockers=tuple(dict.fromkeys(blockers)),
        packet_fingerprint=packet_fingerprint,
        live_trial_artifact_hash=live.evidence_artifact_hash if live is not None else None,
        development_trial_artifact_hash=development.artifact_hash if development is not None else None,
        authority_trial_artifact_hash=authority.artifact_hash if authority is not None else None,
        external_observation_bundle_hash=observations.artifact_hash if observations is not None else None,
    )


def assess_phase2_campaign(evidence: Phase2CampaignEvidence) -> Phase2CampaignReport:
    preflight_report = assess_phase2_preflight(evidence.preflight)
    if preflight_report.status is Phase2PreflightStatus.INVALID:
        return _report(Phase2CampaignStage.INVALID, list(preflight_report.blockers))
    if preflight_report.status is not Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL:
        return _report(Phase2CampaignStage.BIND_EXTERNALS, list(preflight_report.blockers))

    packet = build_frozen_live_trial_packet(evidence.preflight)
    live = evidence.live_trial
    if live is None:
        return _report(
            Phase2CampaignStage.EXECUTE_LIVE_TRIAL,
            ["live_trial_artifact_missing"],
            packet_fingerprint=packet.fingerprint,
        )
    live_blockers: list[str] = []
    if live.packet_id != packet.packet_id:
        live_blockers.append("live_trial_packet_id_mismatch")
    if live.packet_fingerprint != packet.fingerprint:
        live_blockers.append("live_trial_packet_fingerprint_mismatch")
    if not live.raw_search_trace_retained:
        live_blockers.append("raw_search_trace_not_retained_for_every_task")
    if not live.all_resource_matched:
        live_blockers.append("live_trial_resources_not_matched")
    if not live.all_failures_recordable:
        live_blockers.append("live_trial_failure_history_incomplete")
    if live.wide_task_count < 1 or live.deep_task_count < 1:
        live_blockers.append("wide_and_deep_live_trials_required")
    if not _sha256(evidence.baseline_bundle_hash):
        live_blockers.append("matched_baseline_bundle_missing_or_unbound")
    if live.grants_self_promotion:
        live_blockers.append("live_trial_exposed_self_promotion")
    if live_blockers:
        return _report(
            Phase2CampaignStage.EXECUTE_LIVE_TRIAL,
            live_blockers,
            packet_fingerprint=packet.fingerprint,
            live=live,
        )

    development = evidence.development_trial
    if development is None:
        return _report(
            Phase2CampaignStage.EXECUTE_SHADOW_DEVELOPMENT,
            ["observed_failure_shadow_development_trial_missing"],
            packet_fingerprint=packet.fingerprint,
            live=live,
        )
    development_blockers: list[str] = list(development.blockers)
    if development.case.subject_revision_hash != evidence.preflight.subject_revision_hash:
        development_blockers.append("development_trial_subject_mismatch")
    if development.case.evaluation_epoch_id != evidence.preflight.evaluation_epoch_id:
        development_blockers.append("development_trial_epoch_mismatch")
    control = development.cycle.change_control
    if control is None:
        development_blockers.append("development_trial_missing_protected_change_control")
    else:
        if control.assurance.evaluator_artifact_hash != evidence.preflight.evaluator_artifact_hash:
            development_blockers.append("development_trial_evaluator_mismatch")
        if control.assurance.evaluation_epoch_id != evidence.preflight.evaluation_epoch_id:
            development_blockers.append("development_trial_assurance_epoch_mismatch")
    if not development.process_demonstrated:
        development_blockers.append("shadow_development_process_not_demonstrated")
    if development.self_merge_authorized:
        development_blockers.append("shadow_development_self_merge_authorized")
    if development_blockers:
        return _report(
            Phase2CampaignStage.EXECUTE_SHADOW_DEVELOPMENT,
            development_blockers,
            packet_fingerprint=packet.fingerprint,
            live=live,
            development=development,
        )

    authority = evidence.authority_trial
    if authority is None:
        return _report(
            Phase2CampaignStage.EXECUTE_AUTHORITY_TRIAL,
            ["hostile_authority_trial_missing"],
            packet_fingerprint=packet.fingerprint,
            live=live,
            development=development,
        )
    authority_blockers: list[str] = list(authority.blockers)
    if authority.binding.subject_revision_hash != evidence.preflight.subject_revision_hash:
        authority_blockers.append("authority_trial_subject_mismatch")
    if authority.binding.evaluator_artifact_hash != evidence.preflight.evaluator_artifact_hash:
        authority_blockers.append("authority_trial_evaluator_mismatch")
    if authority.binding.evaluation_epoch_id != evidence.preflight.evaluation_epoch_id:
        authority_blockers.append("authority_trial_epoch_mismatch")
    if not authority.all_attacks_executed:
        authority_blockers.append("ten_frozen_authority_attacks_not_all_executed")
    if not authority.correct_cannot_check_passed:
        authority_blockers.append("correct_cannot_check_attack_not_passed")
    if authority.false_promotion_count:
        authority_blockers.append("false_authority_promotion_observed")
    if not authority.all_pass:
        authority_blockers.append("hostile_authority_battery_not_clean")
    if authority_blockers:
        return _report(
            Phase2CampaignStage.EXECUTE_AUTHORITY_TRIAL,
            authority_blockers,
            packet_fingerprint=packet.fingerprint,
            live=live,
            development=development,
            authority=authority,
        )

    observations = evidence.external_observations
    if observations is None:
        return _report(
            Phase2CampaignStage.HAND_BACK_EXTERNAL_EVIDENCE,
            ["phase2_external_observation_bundle_missing"],
            packet_fingerprint=packet.fingerprint,
            live=live,
            development=development,
            authority=authority,
        )
    external_blockers: list[str] = []
    if observations.subject_revision_hash != evidence.preflight.subject_revision_hash:
        external_blockers.append("external_observation_subject_mismatch")
    if observations.evaluator_artifact_hash != evidence.preflight.evaluator_artifact_hash:
        external_blockers.append("external_observation_evaluator_mismatch")
    if observations.evaluation_epoch_id != evidence.preflight.evaluation_epoch_id:
        external_blockers.append("external_observation_epoch_mismatch")
    by_criterion: dict[Phase2CampaignCriterion, list[Phase2ExternalObservation]] = {}
    for observation in observations.observations:
        by_criterion.setdefault(observation.criterion, []).append(observation)
    for criterion in Phase2CampaignCriterion:
        matches = by_criterion.get(criterion, [])
        if len(matches) != 1:
            external_blockers.append(f"external_observation_not_uniquely_bound:{criterion.value}")
            continue
        observation = matches[0]
        if observation.subject_revision_hash != observations.subject_revision_hash:
            external_blockers.append(f"external_observation_subject_mismatch:{criterion.value}")
        if observation.evaluator_artifact_hash != observations.evaluator_artifact_hash:
            external_blockers.append(f"external_observation_evaluator_mismatch:{criterion.value}")
        if observation.evaluation_epoch_id != observations.evaluation_epoch_id:
            external_blockers.append(f"external_observation_epoch_mismatch:{criterion.value}")
        if not observation.independently_verified:
            external_blockers.append(f"external_observation_self_verified:{criterion.value}")
        if not observation.frozen_before_candidate:
            external_blockers.append(f"external_observation_posthoc:{criterion.value}")
        if not observation.fresh_split:
            external_blockers.append(f"external_observation_nonfresh:{criterion.value}")
        if observation.status is Phase2ExternalObservationStatus.BLOCKING_FAILURE:
            external_blockers.append(f"external_observation_blocking_failure:{criterion.value}")

    manifest = evidence.flagship_external_manifest
    if manifest is None:
        external_blockers.append("flagship_external_manifest_missing")
    else:
        if manifest.subject_revision_hash != evidence.preflight.subject_revision_hash:
            external_blockers.append("flagship_manifest_subject_mismatch")
        if manifest.evaluator_artifact_hash != evidence.preflight.evaluator_artifact_hash:
            external_blockers.append("flagship_manifest_evaluator_mismatch")
        if manifest.evaluation_epoch_id != evidence.preflight.evaluation_epoch_id:
            external_blockers.append("flagship_manifest_epoch_mismatch")
        if not manifest.records:
            external_blockers.append("flagship_manifest_has_no_external_records")
        for record in manifest.records:
            if not record.independently_verified:
                external_blockers.append(f"flagship_record_self_verified:{record.criterion.value}")
            if not record.frozen_before_candidate:
                external_blockers.append(f"flagship_record_posthoc:{record.criterion.value}")
            if not record.fresh_split:
                external_blockers.append(f"flagship_record_nonfresh:{record.criterion.value}")
            if record.subject_revision_hash != manifest.subject_revision_hash:
                external_blockers.append(f"flagship_record_subject_mismatch:{record.criterion.value}")
            if record.evaluator_artifact_hash != manifest.evaluator_artifact_hash:
                external_blockers.append(f"flagship_record_evaluator_mismatch:{record.criterion.value}")
            if record.evaluation_epoch_id != manifest.evaluation_epoch_id:
                external_blockers.append(f"flagship_record_epoch_mismatch:{record.criterion.value}")

    if external_blockers:
        return _report(
            Phase2CampaignStage.HAND_BACK_EXTERNAL_EVIDENCE,
            external_blockers,
            packet_fingerprint=packet.fingerprint,
            live=live,
            development=development,
            authority=authority,
            observations=observations,
        )

    return _report(
        Phase2CampaignStage.READY_FOR_TERMINAL_AUDIT,
        [],
        packet_fingerprint=packet.fingerprint,
        live=live,
        development=development,
        authority=authority,
        observations=observations,
    )


__all__ = [
    "Phase2CampaignCriterion",
    "Phase2CampaignEvidence",
    "Phase2CampaignReport",
    "Phase2CampaignStage",
    "Phase2ExternalObservation",
    "Phase2ExternalObservationBundle",
    "Phase2ExternalObservationStatus",
    "assess_phase2_campaign",
]
