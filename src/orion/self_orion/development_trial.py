from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from orion.self_orion.change_control import ChangeControlVerdict
from orion.self_orion.issue_state import (
    DevelopmentIssue,
    InterventionOutcome,
    InterventionOutcomeKind,
)
from orion.self_orion.research_loop import FrozenFailureInvestigationContext
from orion.self_orion.self_driving import (
    SelfDrivingCycleResult,
    SelfDrivingCycleStatus,
    ShadowSelfDrivingController,
)


def _sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _canonical_hash(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@dataclass(frozen=True)
class FrozenObservedFailureCase:
    """Host-frozen bridge from an observed failure into one Shadow repair trial."""

    case_id: str
    mechanic_id: str
    subject_revision_hash: str
    evaluation_epoch_id: str
    split_id: str
    issue: DevelopmentIssue
    observed_failure_artifact_hash: str
    discriminator_artifact_hash: str
    observed_failure_before_discriminator: bool
    discriminator_frozen_before_candidate: bool
    negative_alternative_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if any(
            not value.strip()
            for value in (
                self.case_id,
                self.mechanic_id,
                self.evaluation_epoch_id,
                self.split_id,
            )
        ):
            raise ValueError("Shadow development case identity/mechanic/epoch/split are required")
        for digest in (
            self.subject_revision_hash,
            self.observed_failure_artifact_hash,
            self.discriminator_artifact_hash,
        ):
            if not _sha256(digest):
                raise ValueError("Shadow development case bindings must be SHA-256")
        if not self.issue.failure_episode_ids:
            raise ValueError("Shadow development case requires preserved failure episodes")
        if len(self.issue.candidate_cause_ids) < 2:
            raise ValueError("Shadow development case requires competing responsibility hypotheses")
        if not self.issue.has_causal_attribution:
            raise ValueError("Shadow development case requires discriminator-backed causal attribution")
        if not self.negative_alternative_ids:
            raise ValueError("Shadow development case must preserve negative/harmful alternatives")

    @property
    def investigation_context(self) -> FrozenFailureInvestigationContext:
        return FrozenFailureInvestigationContext(
            work_id=f"phase2-observed-failure:{self.case_id}",
            mechanic_id=self.mechanic_id,
            development_issue_id=self.issue.issue_id,
            issue_title=self.issue.title,
            symptom_signature=self.issue.symptom_signature,
            observed_failure_artifact_hash=self.observed_failure_artifact_hash,
            candidate_cause_ids=self.issue.candidate_cause_ids,
            supported_cause_id=self.issue.supported_cause_id,
            discriminator_artifact_hash=self.discriminator_artifact_hash,
            discriminator_evidence_ids=self.issue.discriminator_evidence_ids,
            issue_evidence_ids=self.issue.evidence_ids,
            failure_episode_ids=self.issue.failure_episode_ids,
            negative_alternative_ids=self.negative_alternative_ids,
        )


@dataclass(frozen=True)
class ShadowDevelopmentTrialReport:
    case: FrozenObservedFailureCase
    cycle: SelfDrivingCycleResult
    updated_issue: DevelopmentIssue
    blockers: tuple[str, ...]

    @property
    def process_demonstrated(self) -> bool:
        return not self.blockers

    @property
    def self_merge_authorized(self) -> bool:
        return False

    @property
    def host_promotion_recommended(self) -> bool:
        return self.cycle.status is SelfDrivingCycleStatus.HOST_PROMOTION_RECOMMENDED

    @property
    def candidate_improved(self) -> bool:
        control = self.cycle.change_control
        return bool(
            control
            and control.assurance.development_delta > 0
            and control.assurance.fresh_assurance_delta > 0
        )

    @property
    def artifact_hash(self) -> str:
        return _canonical_hash(development_trial_artifact_payload(self))


def development_trial_artifact_payload(
    report: ShadowDevelopmentTrialReport,
) -> dict[str, object]:
    """Canonical causal evidence payload for one consequential Shadow repair trial."""

    control = report.cycle.change_control
    investigation = report.cycle.investigation
    request = control.request if control is not None else None
    return {
        "case": {
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
        },
        "investigation": {
            "work_id": investigation.work_id,
            "mechanic_id": investigation.mechanic_id,
            "problem_id": investigation.problem_id,
            "solution_status": investigation.solution_status.value,
            "evidence_ids": list(investigation.evidence_ids),
            "residual_ids": list(investigation.residual_ids),
            "root_episode_id": investigation.root_episode_id,
            "mechanic_episode_ids": list(investigation.mechanic_episode_ids),
            "proposal_only": investigation.proposal_only,
            "development_issue_id": investigation.development_issue_id,
            "observed_failure_artifact_hash": investigation.observed_failure_artifact_hash,
            "candidate_cause_ids": list(investigation.candidate_cause_ids),
            "supported_cause_id": investigation.supported_cause_id,
            "discriminator_artifact_hash": investigation.discriminator_artifact_hash,
            "discriminator_evidence_ids": list(investigation.discriminator_evidence_ids),
            "source_failure_episode_ids": list(investigation.source_failure_episode_ids),
            "negative_alternative_ids": list(investigation.negative_alternative_ids),
        },
        "change_request": (
            {
                "request_id": request.request_id,
                "mechanic_id": request.mechanic_id,
                "base_revision": request.base_revision,
                "evidence_ids": list(request.evidence_ids),
                "failure_episode_ids": list(request.failure_episode_ids),
                "development_issue_id": request.development_issue_id,
                "observed_failure_artifact_hash": request.observed_failure_artifact_hash,
                "candidate_cause_ids": list(request.candidate_cause_ids),
                "supported_cause_id": request.supported_cause_id,
                "discriminator_artifact_hash": request.discriminator_artifact_hash,
                "discriminator_evidence_ids": list(request.discriminator_evidence_ids),
                "negative_alternative_ids": list(request.negative_alternative_ids),
            }
            if request is not None
            else None
        ),
        "change_control": (
            {
                "proposal_id": control.proposal.proposal_id,
                "proposal_request_id": control.proposal.request_id,
                "proposal_base_revision": control.proposal.base_revision,
                "patch_artifact_hash": control.proposal.patch_artifact_hash,
                "candidate_revision_hash": control.execution.candidate_revision_hash,
                "execution_receipt_id": control.execution.receipt_id,
                "execution_artifact_ids": list(control.execution.artifact_ids),
                "verdict": control.verdict.value,
                "assurance_receipt_id": control.assurance.receipt_id,
                "evaluator_artifact_hash": control.assurance.evaluator_artifact_hash,
                "assurance_epoch_id": control.assurance.evaluation_epoch_id,
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
        "cycle_status": report.cycle.status.value,
        "updated_interventions": [
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
        "blockers": list(report.blockers),
    }


def _intervention_kind(cycle: SelfDrivingCycleResult) -> InterventionOutcomeKind:
    control = cycle.change_control
    if control is None:
        return InterventionOutcomeKind.BLOCKED
    if control.assurance.fresh_assurance_delta < 0:
        return InterventionOutcomeKind.REGRESSED
    if (
        control.assurance.development_delta > 0
        and control.assurance.fresh_assurance_delta > 0
    ):
        return InterventionOutcomeKind.IMPROVED
    if control.verdict is ChangeControlVerdict.REJECT:
        return InterventionOutcomeKind.BLOCKED
    if (
        control.assurance.development_delta == 0
        and control.assurance.fresh_assurance_delta == 0
    ):
        return InterventionOutcomeKind.NO_CHANGE
    return InterventionOutcomeKind.CANNOT_CHECK


class ShadowDevelopmentTrialRunner:
    """Run one real observed failure through the existing Shadow development controller."""

    def __init__(self, controller: ShadowSelfDrivingController) -> None:
        self._controller = controller

    def run(self, case: FrozenObservedFailureCase) -> ShadowDevelopmentTrialReport:
        blockers: list[str] = []
        if not case.observed_failure_before_discriminator:
            blockers.append("discriminator_preceded_observed_failure")
        if not case.discriminator_frozen_before_candidate:
            blockers.append("discriminator_not_frozen_before_candidate")

        cycle = self._controller.run_observed_failure(
            case.investigation_context,
            evaluation_epoch_id=case.evaluation_epoch_id,
            split_id=case.split_id,
        )
        investigation = cycle.investigation
        if investigation.mechanic_id != case.mechanic_id:
            blockers.append("development_cycle_mechanic_mismatch")
        if investigation.development_issue_id != case.issue.issue_id:
            blockers.append("development_cycle_issue_binding_mismatch")
        if investigation.observed_failure_artifact_hash != case.observed_failure_artifact_hash:
            blockers.append("development_cycle_failure_artifact_mismatch")
        if investigation.candidate_cause_ids != case.issue.candidate_cause_ids:
            blockers.append("development_cycle_candidate_causes_mismatch")
        if investigation.supported_cause_id != case.issue.supported_cause_id:
            blockers.append("development_cycle_supported_cause_mismatch")
        if investigation.discriminator_artifact_hash != case.discriminator_artifact_hash:
            blockers.append("development_cycle_discriminator_artifact_mismatch")
        if investigation.discriminator_evidence_ids != case.issue.discriminator_evidence_ids:
            blockers.append("development_cycle_discriminator_evidence_mismatch")
        if investigation.source_failure_episode_ids != case.issue.failure_episode_ids:
            blockers.append("development_cycle_failure_episode_mismatch")
        if investigation.negative_alternative_ids != case.negative_alternative_ids:
            blockers.append("development_cycle_negative_history_mismatch")
        if cycle.status is SelfDrivingCycleStatus.RESEARCH_OPEN:
            blockers.append("development_cycle_stopped_before_candidate_execution")
        if cycle.change_control is None:
            blockers.append("development_cycle_missing_change_control")
            return ShadowDevelopmentTrialReport(case, cycle, case.issue, tuple(blockers))

        control = cycle.change_control
        request = control.request
        if not request.observed_failure_bound:
            blockers.append("development_change_request_not_failure_bound")
        if request.development_issue_id != case.issue.issue_id:
            blockers.append("development_request_issue_binding_mismatch")
        if request.observed_failure_artifact_hash != case.observed_failure_artifact_hash:
            blockers.append("development_request_failure_artifact_mismatch")
        if request.discriminator_artifact_hash != case.discriminator_artifact_hash:
            blockers.append("development_request_discriminator_artifact_mismatch")
        if request.supported_cause_id != case.issue.supported_cause_id:
            blockers.append("development_request_supported_cause_mismatch")
        if request.candidate_cause_ids != case.issue.candidate_cause_ids:
            blockers.append("development_request_candidate_causes_mismatch")
        if request.discriminator_evidence_ids != case.issue.discriminator_evidence_ids:
            blockers.append("development_request_discriminator_evidence_mismatch")
        if request.negative_alternative_ids != case.negative_alternative_ids:
            blockers.append("development_request_negative_history_mismatch")
        if not set(case.issue.failure_episode_ids).issubset(request.failure_episode_ids):
            blockers.append("development_request_missing_source_failure_episode")

        assurance = control.assurance
        if assurance.evaluation_epoch_id != case.evaluation_epoch_id:
            blockers.append("development_assurance_epoch_mismatch")
        if not assurance.evaluator_frozen_before_candidate:
            blockers.append("development_evaluator_not_frozen")
        if not assurance.fresh_split:
            blockers.append("development_assurance_not_fresh")
        if not assurance.resource_matched:
            blockers.append("development_resources_not_matched")
        if cycle.self_merge_authorized or control.self_merge_authorized:
            blockers.append("shadow_cycle_exposed_self_merge_authority")

        evidence_ids = tuple(
            dict.fromkeys(
                (
                    assurance.receipt_id,
                    control.execution.receipt_id,
                    *control.execution.artifact_ids,
                    *cycle.investigation.evidence_ids,
                )
            )
        )
        outcome = InterventionOutcome(
            intervention_id=f"intervention:{case.case_id}:{control.proposal.proposal_id}",
            candidate_id=control.proposal.proposal_id,
            kind=_intervention_kind(cycle),
            evidence_ids=evidence_ids,
            episode_ids=tuple(
                dict.fromkeys(
                    (
                        *case.issue.failure_episode_ids,
                        *cycle.investigation.mechanic_episode_ids,
                    )
                )
            ),
            fresh_transfer=assurance.fresh_split,
            note=(
                "Phase-2 failure-driven Shadow development trial; negative/harmful alternatives retained: "
                + ",".join(case.negative_alternative_ids)
            ),
        )
        updated_issue = case.issue.record_intervention(outcome)
        return ShadowDevelopmentTrialReport(
            case=case,
            cycle=cycle,
            updated_issue=updated_issue,
            blockers=tuple(blockers),
        )


__all__ = [
    "FrozenObservedFailureCase",
    "ShadowDevelopmentTrialReport",
    "ShadowDevelopmentTrialRunner",
    "development_trial_artifact_payload",
]
