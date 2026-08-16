from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from orion.self_orion.development_trial import (
    ShadowDevelopmentTrialReport,
    development_trial_artifact_payload,
)


DEVELOPMENT_TRIAL_REPORT_V2_SCHEMA = "ShadowDevelopmentTrialReport.v2"


def _canonical_hash(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _dict(value: object, name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"development trial V2 {name} must be an object")
    return value


def _string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"development trial V2 {name} must be a non-empty string")
    return value


def _strings(value: object, name: str, *, nonempty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ValueError(f"development trial V2 {name} must be an array of non-empty strings")
    if nonempty and not value:
        raise ValueError(f"development trial V2 {name} cannot be empty")
    return tuple(value)


def _boolean(value: object, name: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"development trial V2 {name} must be boolean")
    return value


def _number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"development trial V2 {name} must be numeric")
    return float(value)


def _append_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def development_trial_report_v2_to_dict(
    report: ShadowDevelopmentTrialReport,
) -> dict[str, object]:
    artifact_payload = development_trial_artifact_payload(report)
    artifact_hash = _canonical_hash(artifact_payload)
    if artifact_hash != report.artifact_hash:
        raise ValueError("development trial V2 artifact payload diverges from report hash")
    return {
        "schema": DEVELOPMENT_TRIAL_REPORT_V2_SCHEMA,
        "artifact_hash": artifact_hash,
        "artifact_payload": artifact_payload,
    }


def write_development_trial_report_v2(
    report: ShadowDevelopmentTrialReport,
    path: Path | str,
) -> None:
    payload = development_trial_report_v2_to_dict(report)
    payload["document_hash"] = _canonical_hash(payload)
    Path(path).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


@dataclass(frozen=True)
class LoadedDevelopmentTrialReportV2:
    case: object
    cycle: object
    blockers: tuple[str, ...]
    process_demonstrated: bool
    self_merge_authorized: bool
    artifact_hash: str
    document_hash: str


def _derive_blockers(artifact: dict[str, object]) -> tuple[str, ...]:
    blockers: list[str] = []
    case = _dict(artifact.get("case"), "artifact_payload.case")
    investigation = _dict(
        artifact.get("investigation"), "artifact_payload.investigation"
    )
    request_raw = artifact.get("change_request")
    control_raw = artifact.get("change_control")

    case_mechanic = _string(case.get("mechanic_id"), "case.mechanic_id")
    case_issue = _string(case.get("issue_id"), "case.issue_id")
    case_failure = _string(
        case.get("observed_failure_artifact_hash"),
        "case.observed_failure_artifact_hash",
    )
    case_causes = _strings(
        case.get("candidate_cause_ids"), "case.candidate_cause_ids", nonempty=True
    )
    if len(case_causes) < 2:
        raise ValueError("development trial V2 requires competing cause hypotheses")
    case_supported = _string(case.get("supported_cause_id"), "case.supported_cause_id")
    if case_supported not in case_causes:
        raise ValueError("development trial V2 supported cause is outside candidate causes")
    case_discriminator = _string(
        case.get("discriminator_artifact_hash"), "case.discriminator_artifact_hash"
    )
    case_discriminator_evidence = _strings(
        case.get("discriminator_evidence_ids"),
        "case.discriminator_evidence_ids",
        nonempty=True,
    )
    case_episodes = _strings(
        case.get("failure_episode_ids"), "case.failure_episode_ids", nonempty=True
    )
    case_negatives = _strings(
        case.get("negative_alternative_ids"),
        "case.negative_alternative_ids",
        nonempty=True,
    )
    case_epoch = _string(case.get("evaluation_epoch_id"), "case.evaluation_epoch_id")

    if not _boolean(
        case.get("observed_failure_before_discriminator"),
        "case.observed_failure_before_discriminator",
    ):
        _append_unique(blockers, "discriminator_preceded_observed_failure")
    if not _boolean(
        case.get("discriminator_frozen_before_candidate"),
        "case.discriminator_frozen_before_candidate",
    ):
        _append_unique(blockers, "discriminator_not_frozen_before_candidate")

    comparisons = (
        (
            investigation.get("mechanic_id"),
            case_mechanic,
            "development_cycle_mechanic_mismatch",
        ),
        (
            investigation.get("development_issue_id"),
            case_issue,
            "development_cycle_issue_binding_mismatch",
        ),
        (
            investigation.get("observed_failure_artifact_hash"),
            case_failure,
            "development_cycle_failure_artifact_mismatch",
        ),
        (
            tuple(_strings(investigation.get("candidate_cause_ids"), "investigation.candidate_cause_ids")),
            case_causes,
            "development_cycle_candidate_causes_mismatch",
        ),
        (
            investigation.get("supported_cause_id"),
            case_supported,
            "development_cycle_supported_cause_mismatch",
        ),
        (
            investigation.get("discriminator_artifact_hash"),
            case_discriminator,
            "development_cycle_discriminator_artifact_mismatch",
        ),
        (
            tuple(_strings(investigation.get("discriminator_evidence_ids"), "investigation.discriminator_evidence_ids")),
            case_discriminator_evidence,
            "development_cycle_discriminator_evidence_mismatch",
        ),
        (
            tuple(_strings(investigation.get("source_failure_episode_ids"), "investigation.source_failure_episode_ids")),
            case_episodes,
            "development_cycle_failure_episode_mismatch",
        ),
        (
            tuple(_strings(investigation.get("negative_alternative_ids"), "investigation.negative_alternative_ids")),
            case_negatives,
            "development_cycle_negative_history_mismatch",
        ),
    )
    for actual, expected, blocker in comparisons:
        if actual != expected:
            _append_unique(blockers, blocker)

    if artifact.get("cycle_status") == "RESEARCH_OPEN":
        _append_unique(blockers, "development_cycle_stopped_before_candidate_execution")
    _boolean(investigation.get("proposal_only"), "investigation.proposal_only")
    if investigation.get("proposal_only") is not True:
        _append_unique(blockers, "development_investigation_exposed_promotion_authority")

    if request_raw is None:
        _append_unique(blockers, "development_cycle_missing_change_control")
        loaded_request = None
    else:
        loaded_request = _dict(request_raw, "artifact_payload.change_request")
        request_failure = loaded_request.get("observed_failure_artifact_hash")
        if not request_failure:
            _append_unique(blockers, "development_change_request_not_failure_bound")
        request_comparisons = (
            (loaded_request.get("mechanic_id"), case_mechanic, "development_request_mechanic_mismatch"),
            (loaded_request.get("development_issue_id"), case_issue, "development_request_issue_binding_mismatch"),
            (request_failure, case_failure, "development_request_failure_artifact_mismatch"),
            (tuple(_strings(loaded_request.get("candidate_cause_ids"), "change_request.candidate_cause_ids")), case_causes, "development_request_candidate_causes_mismatch"),
            (loaded_request.get("supported_cause_id"), case_supported, "development_request_supported_cause_mismatch"),
            (loaded_request.get("discriminator_artifact_hash"), case_discriminator, "development_request_discriminator_artifact_mismatch"),
            (tuple(_strings(loaded_request.get("discriminator_evidence_ids"), "change_request.discriminator_evidence_ids")), case_discriminator_evidence, "development_request_discriminator_evidence_mismatch"),
            (tuple(_strings(loaded_request.get("negative_alternative_ids"), "change_request.negative_alternative_ids")), case_negatives, "development_request_negative_history_mismatch"),
        )
        for actual, expected, blocker in request_comparisons:
            if actual != expected:
                _append_unique(blockers, blocker)
        request_episodes = set(
            _strings(
                loaded_request.get("failure_episode_ids"),
                "change_request.failure_episode_ids",
            )
        )
        if not set(case_episodes).issubset(request_episodes):
            _append_unique(blockers, "development_request_missing_source_failure_episode")

    loaded_control = None
    if control_raw is None:
        _append_unique(blockers, "development_cycle_missing_change_control")
    else:
        loaded_control = _dict(control_raw, "artifact_payload.change_control")
        control_epoch = _string(
            loaded_control.get("assurance_epoch_id"), "change_control.assurance_epoch_id"
        )
        if control_epoch != case_epoch:
            _append_unique(blockers, "development_assurance_epoch_mismatch")
        if not _boolean(
            loaded_control.get("evaluator_frozen_before_candidate"),
            "change_control.evaluator_frozen_before_candidate",
        ):
            _append_unique(blockers, "development_evaluator_not_frozen")
        if not _boolean(loaded_control.get("fresh_split"), "change_control.fresh_split"):
            _append_unique(blockers, "development_assurance_not_fresh")
        if not _boolean(
            loaded_control.get("resource_matched"), "change_control.resource_matched"
        ):
            _append_unique(blockers, "development_resources_not_matched")
        _boolean(
            loaded_control.get("blocking_invariants_passed"),
            "change_control.blocking_invariants_passed",
        )
        _number(loaded_control.get("development_delta"), "change_control.development_delta")
        _number(
            loaded_control.get("fresh_assurance_delta"),
            "change_control.fresh_assurance_delta",
        )
        _string(
            loaded_control.get("evaluator_artifact_hash"),
            "change_control.evaluator_artifact_hash",
        )
        if loaded_request is not None:
            if loaded_control.get("proposal_request_id") != loaded_request.get("request_id"):
                _append_unique(blockers, "proposal_request_binding_mismatch")
            if loaded_control.get("proposal_base_revision") != loaded_request.get("base_revision"):
                _append_unique(blockers, "proposal_base_revision_mismatch")

    interventions = artifact.get("updated_interventions")
    if not isinstance(interventions, list) or not interventions:
        _append_unique(blockers, "development_intervention_not_recorded")
    else:
        final_intervention = _dict(interventions[-1], "updated_interventions[-1]")
        episode_ids = set(
            _strings(final_intervention.get("episode_ids"), "intervention.episode_ids")
        )
        if not set(case_episodes).issubset(episode_ids):
            _append_unique(blockers, "development_intervention_missing_source_failure_episode")
        if loaded_control is not None:
            if final_intervention.get("fresh_transfer") is not loaded_control.get("fresh_split"):
                _append_unique(blockers, "development_intervention_fresh_transfer_mismatch")

    recorded = _strings(artifact.get("blockers"), "artifact_payload.blockers")
    for blocker in recorded:
        _append_unique(blockers, blocker)
    return tuple(blockers)


def load_development_trial_report_v2(
    path: Path | str,
) -> LoadedDevelopmentTrialReportV2:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema") != DEVELOPMENT_TRIAL_REPORT_V2_SCHEMA:
        raise ValueError(
            f"development trial closure evidence must use {DEVELOPMENT_TRIAL_REPORT_V2_SCHEMA}"
        )
    recorded_document_hash = raw.pop("document_hash", None)
    if (
        not isinstance(recorded_document_hash, str)
        or recorded_document_hash != _canonical_hash(raw)
    ):
        raise ValueError("development trial V2 document hash mismatch")
    artifact = _dict(raw.get("artifact_payload"), "artifact_payload")
    artifact_hash = _canonical_hash(artifact)
    if raw.get("artifact_hash") != artifact_hash:
        raise ValueError("development trial V2 artifact hash mismatch")

    case = _dict(artifact.get("case"), "artifact_payload.case")
    control = artifact.get("change_control")
    loaded_control = None
    if control is not None:
        control_dict = _dict(control, "artifact_payload.change_control")
        loaded_control = SimpleNamespace(
            assurance=SimpleNamespace(
                evaluator_artifact_hash=_string(
                    control_dict.get("evaluator_artifact_hash"),
                    "change_control.evaluator_artifact_hash",
                ),
                evaluation_epoch_id=_string(
                    control_dict.get("assurance_epoch_id"),
                    "change_control.assurance_epoch_id",
                ),
            )
        )
    blockers = _derive_blockers(artifact)
    return LoadedDevelopmentTrialReportV2(
        case=SimpleNamespace(
            subject_revision_hash=_string(
                case.get("subject_revision_hash"), "case.subject_revision_hash"
            ),
            evaluation_epoch_id=_string(
                case.get("evaluation_epoch_id"), "case.evaluation_epoch_id"
            ),
        ),
        cycle=SimpleNamespace(change_control=loaded_control),
        blockers=blockers,
        process_demonstrated=not blockers,
        self_merge_authorized=False,
        artifact_hash=artifact_hash,
        document_hash=recorded_document_hash,
    )


__all__ = [
    "DEVELOPMENT_TRIAL_REPORT_V2_SCHEMA",
    "LoadedDevelopmentTrialReportV2",
    "development_trial_report_v2_to_dict",
    "load_development_trial_report_v2",
    "write_development_trial_report_v2",
]
