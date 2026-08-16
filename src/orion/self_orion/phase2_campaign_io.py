from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from orion.self_orion.authority_trial import AuthorityTrialReport
from orion.self_orion.development_trial import ShadowDevelopmentTrialReport
from orion.self_orion.phase2_campaign import (
    Phase2CampaignCriterion,
    Phase2CampaignReport,
    Phase2ExternalObservation,
    Phase2ExternalObservationBundle,
    Phase2ExternalObservationStatus,
)


EXTERNAL_OBSERVATION_BUNDLE_SCHEMA = "Phase2ExternalObservationBundle.v1"
AUTHORITY_TRIAL_REPORT_SCHEMA = "AuthorityTrialReport.v1"
DEVELOPMENT_TRIAL_REPORT_SCHEMA = "ShadowDevelopmentTrialReport.v1"
CAMPAIGN_REPORT_SCHEMA = "Phase2CampaignReport.v1"


def _document_hash(payload: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def external_observation_bundle_to_dict(
    bundle: Phase2ExternalObservationBundle,
) -> dict[str, object]:
    return {
        "schema": EXTERNAL_OBSERVATION_BUNDLE_SCHEMA,
        "bundle_id": bundle.bundle_id,
        "bundle_artifact_hash": bundle.artifact_hash,
        "subject_revision_hash": bundle.subject_revision_hash,
        "evaluator_artifact_hash": bundle.evaluator_artifact_hash,
        "evaluation_epoch_id": bundle.evaluation_epoch_id,
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
            for item in bundle.observations
        ],
    }


def write_external_observation_bundle(
    bundle: Phase2ExternalObservationBundle, path: Path | str
) -> None:
    payload = external_observation_bundle_to_dict(bundle)
    payload["document_hash"] = _document_hash(payload)
    Path(path).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_external_observation_bundle(path: Path | str) -> Phase2ExternalObservationBundle:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema") != EXTERNAL_OBSERVATION_BUNDLE_SCHEMA:
        raise ValueError(
            f"Phase-2 observation schema must be {EXTERNAL_OBSERVATION_BUNDLE_SCHEMA}"
        )
    recorded_document_hash = raw.pop("document_hash", None)
    if (
        not isinstance(recorded_document_hash, str)
        or recorded_document_hash != _document_hash(raw)
    ):
        raise ValueError("Phase-2 observation bundle document hash mismatch")
    raw_observations = raw.get("observations")
    if not isinstance(raw_observations, list):
        raise ValueError("Phase-2 observations must be a JSON array")
    observations = tuple(
        Phase2ExternalObservation(
            criterion=Phase2CampaignCriterion(item["criterion"]),
            evidence_artifact_id=item["evidence_artifact_id"],
            evidence_artifact_hash=item["evidence_artifact_hash"],
            subject_revision_hash=item["subject_revision_hash"],
            evaluator_artifact_hash=item["evaluator_artifact_hash"],
            producer_process_lineage_hash=item["producer_process_lineage_hash"],
            verifier_process_lineage_hash=item["verifier_process_lineage_hash"],
            evaluation_epoch_id=item["evaluation_epoch_id"],
            split_id=item["split_id"],
            status=Phase2ExternalObservationStatus(item["status"]),
            frozen_before_candidate=item["frozen_before_candidate"],
            fresh_split=item["fresh_split"],
            note=item["note"],
        )
        for item in raw_observations
    )
    bundle = Phase2ExternalObservationBundle(
        bundle_id=raw["bundle_id"],
        subject_revision_hash=raw["subject_revision_hash"],
        evaluator_artifact_hash=raw["evaluator_artifact_hash"],
        evaluation_epoch_id=raw["evaluation_epoch_id"],
        observations=observations,
    )
    if raw.get("bundle_artifact_hash") != bundle.artifact_hash:
        raise ValueError("Phase-2 observation bundle artifact hash mismatch")
    return bundle


def authority_trial_report_to_dict(report: AuthorityTrialReport) -> dict[str, object]:
    return {
        "schema": AUTHORITY_TRIAL_REPORT_SCHEMA,
        "artifact_hash": report.artifact_hash,
        "binding": {
            "subject_revision_hash": report.binding.subject_revision_hash,
            "evaluator_artifact_hash": report.binding.evaluator_artifact_hash,
            "evaluation_epoch_id": report.binding.evaluation_epoch_id,
            "split_id": report.binding.split_id,
            "producer_process_lineage_hash": report.binding.producer_process_lineage_hash,
            "evaluator_process_lineage_hash": report.binding.evaluator_process_lineage_hash,
            "evaluator_frozen_before_candidate": report.binding.evaluator_frozen_before_candidate,
            "fresh_split": report.binding.fresh_split,
            "independent_evaluator": report.binding.independent_evaluator,
        },
        "all_attacks_executed": report.all_attacks_executed,
        "all_pass": report.all_pass,
        "correct_cannot_check_passed": report.correct_cannot_check_passed,
        "false_promotion_count": report.false_promotion_count,
        "blockers": list(report.blockers),
        "grants_phase2_closure": report.grants_phase2_closure,
        "grants_governed_self_orion": report.grants_governed_self_orion,
        "results": [
            {
                "attack_id": item.attack.attack_id,
                "description": item.attack.description,
                "expected_outcome": item.attack.expected_outcome.value,
                "execution": {
                    "subject_revision_hash": item.execution.subject_revision_hash,
                    "artifact_id": item.execution.artifact_id,
                    "artifact_hash": item.execution.artifact_hash,
                    "resource_units": item.execution.resource_units,
                    "observed_authority_outcome": item.execution.observed_authority_outcome,
                    "candidate_authority_increased": item.execution.candidate_authority_increased,
                    "note": item.execution.note,
                },
                "evaluation": {
                    "evaluator_artifact_hash": item.evaluation.evaluator_artifact_hash,
                    "evaluation_epoch_id": item.evaluation.evaluation_epoch_id,
                    "status": item.evaluation.status.value,
                    "expected_outcome_observed": item.evaluation.expected_outcome_observed,
                    "false_promotion_observed": item.evaluation.false_promotion_observed,
                    "tamper_or_leakage_detected": item.evaluation.tamper_or_leakage_detected,
                    "evidence_ids": list(item.evaluation.evidence_ids),
                    "note": item.evaluation.note,
                },
                "blockers": list(item.blockers),
            }
            for item in report.results
        ],
    }


def write_authority_trial_report(report: AuthorityTrialReport, path: Path | str) -> None:
    payload = authority_trial_report_to_dict(report)
    payload["document_hash"] = _document_hash(payload)
    Path(path).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


@dataclass(frozen=True)
class LoadedAuthorityTrialReport:
    binding: object
    blockers: tuple[str, ...]
    all_attacks_executed: bool
    correct_cannot_check_passed: bool
    false_promotion_count: int
    all_pass: bool
    artifact_hash: str
    grants_phase2_closure: bool
    grants_governed_self_orion: bool
    document_hash: str


def load_authority_trial_report(path: Path | str) -> LoadedAuthorityTrialReport:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema") != AUTHORITY_TRIAL_REPORT_SCHEMA:
        raise ValueError(f"authority trial schema must be {AUTHORITY_TRIAL_REPORT_SCHEMA}")
    recorded_document_hash = raw.pop("document_hash", None)
    if (
        not isinstance(recorded_document_hash, str)
        or recorded_document_hash != _document_hash(raw)
    ):
        raise ValueError("authority trial report document hash mismatch")
    binding = raw.get("binding")
    if not isinstance(binding, dict):
        raise ValueError("authority trial binding must be an object")
    for name in (
        "all_attacks_executed",
        "correct_cannot_check_passed",
        "all_pass",
        "grants_phase2_closure",
        "grants_governed_self_orion",
    ):
        if type(raw.get(name)) is not bool:
            raise ValueError(f"authority trial {name} must be boolean")
    if raw["grants_phase2_closure"] or raw["grants_governed_self_orion"]:
        raise ValueError("authority trial report cannot grant promotion/closure authority")
    blockers = raw.get("blockers")
    if not isinstance(blockers, list) or any(not isinstance(item, str) for item in blockers):
        raise ValueError("authority trial blockers must be strings")
    false_promotion_count = raw.get("false_promotion_count")
    if (
        isinstance(false_promotion_count, bool)
        or not isinstance(false_promotion_count, int)
        or false_promotion_count < 0
    ):
        raise ValueError("authority trial false promotion count is invalid")
    return LoadedAuthorityTrialReport(
        binding=SimpleNamespace(
            subject_revision_hash=binding["subject_revision_hash"],
            evaluator_artifact_hash=binding["evaluator_artifact_hash"],
            evaluation_epoch_id=binding["evaluation_epoch_id"],
        ),
        blockers=tuple(blockers),
        all_attacks_executed=raw["all_attacks_executed"],
        correct_cannot_check_passed=raw["correct_cannot_check_passed"],
        false_promotion_count=false_promotion_count,
        all_pass=raw["all_pass"],
        artifact_hash=raw["artifact_hash"],
        grants_phase2_closure=False,
        grants_governed_self_orion=False,
        document_hash=recorded_document_hash,
    )


def development_trial_report_to_dict(
    report: ShadowDevelopmentTrialReport,
) -> dict[str, object]:
    control = report.cycle.change_control
    return {
        "schema": DEVELOPMENT_TRIAL_REPORT_SCHEMA,
        "artifact_hash": report.artifact_hash,
        "case_id": report.case.case_id,
        "mechanic_id": report.case.mechanic_id,
        "subject_revision_hash": report.case.subject_revision_hash,
        "evaluation_epoch_id": report.case.evaluation_epoch_id,
        "split_id": report.case.split_id,
        "issue_id": report.case.issue.issue_id,
        "failure_episode_ids": list(report.case.issue.failure_episode_ids),
        "candidate_cause_ids": list(report.case.issue.candidate_cause_ids),
        "supported_cause_id": report.case.issue.supported_cause_id,
        "discriminator_evidence_ids": list(report.case.issue.discriminator_evidence_ids),
        "observed_failure_artifact_hash": report.case.observed_failure_artifact_hash,
        "discriminator_artifact_hash": report.case.discriminator_artifact_hash,
        "observed_failure_before_discriminator": report.case.observed_failure_before_discriminator,
        "discriminator_frozen_before_candidate": report.case.discriminator_frozen_before_candidate,
        "negative_alternative_ids": list(report.case.negative_alternative_ids),
        "cycle_status": report.cycle.status.value,
        "process_demonstrated": report.process_demonstrated,
        "self_merge_authorized": report.self_merge_authorized,
        "host_promotion_recommended": report.host_promotion_recommended,
        "candidate_improved": report.candidate_improved,
        "blockers": list(report.blockers),
        "change_control": (
            {
                "verdict": control.verdict.value,
                "proposal_id": control.proposal.proposal_id,
                "execution_receipt_id": control.execution.receipt_id,
                "candidate_revision_hash": control.execution.candidate_revision_hash,
                "execution_artifact_ids": list(control.execution.artifact_ids),
                "assurance_receipt_id": control.assurance.receipt_id,
                "evaluator_artifact_hash": control.assurance.evaluator_artifact_hash,
                "evaluation_epoch_id": control.assurance.evaluation_epoch_id,
                "development_delta": control.assurance.development_delta,
                "fresh_assurance_delta": control.assurance.fresh_assurance_delta,
                "blocking_invariants_passed": control.assurance.blocking_invariants_passed,
                "evaluator_frozen_before_candidate": control.assurance.evaluator_frozen_before_candidate,
                "fresh_split": control.assurance.fresh_split,
                "resource_matched": control.assurance.resource_matched,
                "reasons": list(control.reasons),
            }
            if control is not None
            else None
        ),
        "recorded_interventions": [
            {
                "intervention_id": item.intervention_id,
                "candidate_id": item.candidate_id,
                "kind": item.kind.value,
                "evidence_ids": list(item.evidence_ids),
                "episode_ids": list(item.episode_ids),
                "fresh_transfer": item.fresh_transfer,
                "note": item.note,
            }
            for item in report.updated_issue.interventions
        ],
    }


def write_development_trial_report(
    report: ShadowDevelopmentTrialReport, path: Path | str
) -> None:
    payload = development_trial_report_to_dict(report)
    payload["document_hash"] = _document_hash(payload)
    Path(path).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


@dataclass(frozen=True)
class LoadedDevelopmentTrialReport:
    case: object
    cycle: object
    blockers: tuple[str, ...]
    process_demonstrated: bool
    self_merge_authorized: bool
    artifact_hash: str
    document_hash: str


def load_development_trial_report(path: Path | str) -> LoadedDevelopmentTrialReport:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema") != DEVELOPMENT_TRIAL_REPORT_SCHEMA:
        raise ValueError(
            f"development trial schema must be {DEVELOPMENT_TRIAL_REPORT_SCHEMA}"
        )
    recorded_document_hash = raw.pop("document_hash", None)
    if (
        not isinstance(recorded_document_hash, str)
        or recorded_document_hash != _document_hash(raw)
    ):
        raise ValueError("development trial report document hash mismatch")
    for name in ("process_demonstrated", "self_merge_authorized"):
        if type(raw.get(name)) is not bool:
            raise ValueError(f"development trial {name} must be boolean")
    if raw["self_merge_authorized"]:
        raise ValueError("development trial report cannot authorize self-merge")
    blockers = raw.get("blockers")
    if not isinstance(blockers, list) or any(not isinstance(item, str) for item in blockers):
        raise ValueError("development trial blockers must be strings")
    control = raw.get("change_control")
    loaded_control = None
    if control is not None:
        if not isinstance(control, dict):
            raise ValueError("development trial change_control must be an object")
        loaded_control = SimpleNamespace(
            assurance=SimpleNamespace(
                evaluator_artifact_hash=control["evaluator_artifact_hash"],
                evaluation_epoch_id=control["evaluation_epoch_id"],
            )
        )
    return LoadedDevelopmentTrialReport(
        case=SimpleNamespace(
            subject_revision_hash=raw["subject_revision_hash"],
            evaluation_epoch_id=raw["evaluation_epoch_id"],
        ),
        cycle=SimpleNamespace(change_control=loaded_control),
        blockers=tuple(blockers),
        process_demonstrated=raw["process_demonstrated"],
        self_merge_authorized=False,
        artifact_hash=raw["artifact_hash"],
        document_hash=recorded_document_hash,
    )


def campaign_report_to_dict(report: Phase2CampaignReport) -> dict[str, object]:
    return {
        "schema": CAMPAIGN_REPORT_SCHEMA,
        "stage": report.stage.value,
        "blockers": list(report.blockers),
        "packet_fingerprint": report.packet_fingerprint,
        "live_trial_artifact_hash": report.live_trial_artifact_hash,
        "development_trial_artifact_hash": report.development_trial_artifact_hash,
        "authority_trial_artifact_hash": report.authority_trial_artifact_hash,
        "authority_benchmark_panel_hash": report.authority_benchmark_panel_hash,
        "authority_campaign_artifact_hash": report.authority_campaign_artifact_hash,
        "external_observation_bundle_hash": report.external_observation_bundle_hash,
        "ready_for_terminal_audit": report.ready_for_terminal_audit,
        "grants_phase2_closure": report.grants_phase2_closure,
        "grants_governed_self_orion": report.grants_governed_self_orion,
    }


def write_campaign_report(report: Phase2CampaignReport, path: Path | str) -> None:
    payload = campaign_report_to_dict(report)
    payload["document_hash"] = _document_hash(payload)
    Path(path).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


__all__ = [
    "AUTHORITY_TRIAL_REPORT_SCHEMA",
    "CAMPAIGN_REPORT_SCHEMA",
    "DEVELOPMENT_TRIAL_REPORT_SCHEMA",
    "EXTERNAL_OBSERVATION_BUNDLE_SCHEMA",
    "LoadedAuthorityTrialReport",
    "LoadedDevelopmentTrialReport",
    "authority_trial_report_to_dict",
    "campaign_report_to_dict",
    "development_trial_report_to_dict",
    "external_observation_bundle_to_dict",
    "load_authority_trial_report",
    "load_development_trial_report",
    "load_external_observation_bundle",
    "write_authority_trial_report",
    "write_campaign_report",
    "write_development_trial_report",
    "write_external_observation_bundle",
]
