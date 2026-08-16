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
from orion.self_orion.self_driving import (
    SelfDrivingCycleResult,
    SelfDrivingCycleStatus,
    ShadowSelfDrivingController,
)


def _sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


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
        control = self.cycle.change_control
        payload = {
            "case_id": self.case.case_id,
            "mechanic_id": self.case.mechanic_id,
            "subject_revision_hash": self.case.subject_revision_hash,
            "evaluation_epoch_id": self.case.evaluation_epoch_id,
            "split_id": self.case.split_id,
            "issue_id": self.case.issue.issue_id,
            "failure_episode_ids": list(self.case.issue.failure_episode_ids),
            "candidate_cause_ids": list(self.case.issue.candidate_cause_ids),
            "supported_cause_id": self.case.issue.supported_cause_id,
            "discriminator_evidence_ids": list(self.case.issue.discriminator_evidence_ids),
            "observed_failure_artifact_hash": self.case.observed_failure_artifact_hash,
            "discriminator_artifact_hash": self.case.discriminator_artifact_hash,
            "observed_failure_before_discriminator": self.case.observed_failure_before_discriminator,
            "discriminator_frozen_before_candidate": self.case.discriminator_frozen_before_candidate,
            "negative_alternative_ids": list(self.case.negative_alternative_ids),
            "cycle_status": self.cycle.status.value,
            "investigation_problem_id": self.cycle.investigation.problem_id,
            "investigation_evidence_ids": list(self.cycle.investigation.evidence_ids),
            "investigation_residual_ids": list(self.cycle.investigation.residual_ids),
            "change_control": (
                {
                    "proposal_id": control.proposal.proposal_id,
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
            "updated_intervention_ids": [
                item.intervention_id for item in self.updated_issue.interventions
            ],
            "blockers": list(self.blockers),
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


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

        cycle = self._controller.run_cycle(
            limit=1,
            evaluation_epoch_id=case.evaluation_epoch_id,
            split_id=case.split_id,
        )[0]
        if cycle.investigation.mechanic_id != case.mechanic_id:
            blockers.append("development_cycle_mechanic_mismatch")
        if cycle.status is SelfDrivingCycleStatus.RESEARCH_OPEN:
            blockers.append("development_cycle_stopped_before_candidate_execution")
        if cycle.change_control is None:
            blockers.append("development_cycle_missing_change_control")
            return ShadowDevelopmentTrialReport(case, cycle, case.issue, tuple(blockers))

        control = cycle.change_control
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
                "Phase-2 Shadow development trial; negative/harmful alternatives retained: "
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
]
