"""Non-authorizing, claim-relative epistemic computation allocation.

This is a bounded rational-metareasoning substrate.  Caller-declared action kinds
remain descriptive.  Expected value can rank eligible computation, but hard
obligations and authority requirements are non-compensatory and no selection
can authorize a scientific mutation or claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Mapping, Sequence

from .canonical import content_digest


class ComputationActionState(str, Enum):
    SATISFIED = "SATISFIED"
    VIOLATED = "VIOLATED"
    UNRESOLVED = "UNRESOLVED"


class ComputationAssessmentStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    BLOCKED = "BLOCKED"
    UNRESOLVED = "UNRESOLVED"


class ComputationSelectionStatus(str, Enum):
    SELECTED = "SELECTED"
    MULTIPLE_OPTIMA = "MULTIPLE_OPTIMA"
    LOCAL_COMPUTATION_STOP = "LOCAL_COMPUTATION_STOP"
    NO_ADMISSIBLE = "NO_ADMISSIBLE"
    UNRESOLVED = "UNRESOLVED"


def _uniq(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values}))


@dataclass(frozen=True)
class EpistemicComputationAction:
    action_id: str
    claim_id: str
    kind: str
    expected_decision_value: float
    cost: float
    hard_requirements: tuple[str, ...]
    discharges_obligations: tuple[str, ...]
    required_authorities: tuple[str, ...]
    digest: str

    @property
    def net_value(self) -> float:
        return self.expected_decision_value - self.cost

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "EpistemicComputationAction.v1",
            "action_id": self.action_id,
            "claim_id": self.claim_id,
            "kind": self.kind,
            "expected_decision_value": self.expected_decision_value,
            "cost": self.cost,
            "hard_requirements": list(self.hard_requirements),
            "discharges_obligations": list(self.discharges_obligations),
            "required_authorities": list(self.required_authorities),
            "can_self_authorize": False,
        }

    def verify(self) -> None:
        if not self.action_id or not self.claim_id or not self.kind:
            raise ValueError("computation action identities are required")
        if not isfinite(self.expected_decision_value) or not isfinite(self.cost):
            raise ValueError("computation value/cost must be finite")
        if self.cost < 0:
            raise ValueError("computation cost must be non-negative")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("computation action digest mismatch")


def build_computation_action(
    *,
    action_id: str,
    claim_id: str,
    kind: str,
    expected_decision_value: float,
    cost: float,
    hard_requirements: Sequence[str] = (),
    discharges_obligations: Sequence[str] = (),
    required_authorities: Sequence[str] = (),
) -> EpistemicComputationAction:
    payload = {
        "version": "EpistemicComputationAction.v1",
        "action_id": str(action_id),
        "claim_id": str(claim_id),
        "kind": str(kind),
        "expected_decision_value": float(expected_decision_value),
        "cost": float(cost),
        "hard_requirements": list(_uniq(hard_requirements)),
        "discharges_obligations": list(_uniq(discharges_obligations)),
        "required_authorities": list(_uniq(required_authorities)),
        "can_self_authorize": False,
    }
    action = EpistemicComputationAction(
        action_id=payload["action_id"],
        claim_id=payload["claim_id"],
        kind=payload["kind"],
        expected_decision_value=payload["expected_decision_value"],
        cost=payload["cost"],
        hard_requirements=tuple(payload["hard_requirements"]),
        discharges_obligations=tuple(payload["discharges_obligations"]),
        required_authorities=tuple(payload["required_authorities"]),
        digest=content_digest(payload),
    )
    action.verify()
    return action


@dataclass(frozen=True)
class ComputationActionAssessment:
    action_digest: str
    status: ComputationAssessmentStatus
    reasons: tuple[str, ...]
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "EpistemicComputationActionAssessment.v1",
            "action_digest": self.action_digest,
            "status": self.status.value,
            "reasons": list(self.reasons),
            "grants_scientific_authority": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("computation assessment digest mismatch")


def assess_computation_action(
    action: EpistemicComputationAction,
    *,
    requirement_states: Mapping[str, ComputationActionState | str],
    available_authorities: Sequence[str] = (),
) -> ComputationActionAssessment:
    action.verify()
    states = {
        str(key): value if isinstance(value, ComputationActionState) else ComputationActionState(value)
        for key, value in requirement_states.items()
    }
    reasons: list[str] = []
    unresolved: list[str] = []
    for requirement in action.hard_requirements:
        state = states.get(requirement, ComputationActionState.UNRESOLVED)
        if state is ComputationActionState.VIOLATED:
            reasons.append(f"REQUIREMENT_VIOLATED:{requirement}")
        elif state is ComputationActionState.UNRESOLVED:
            unresolved.append(f"REQUIREMENT_UNRESOLVED:{requirement}")
    missing_authority = sorted(set(action.required_authorities) - set(map(str, available_authorities)))
    reasons.extend(f"MISSING_AUTHORITY:{authority}" for authority in missing_authority)
    if reasons:
        status = ComputationAssessmentStatus.BLOCKED
        final_reasons = tuple(sorted(set(reasons + unresolved)))
    elif unresolved:
        status = ComputationAssessmentStatus.UNRESOLVED
        final_reasons = tuple(sorted(set(unresolved)))
    else:
        status = ComputationAssessmentStatus.ELIGIBLE
        final_reasons = ()
    payload = {
        "version": "EpistemicComputationActionAssessment.v1",
        "action_digest": action.digest,
        "status": status.value,
        "reasons": list(final_reasons),
        "grants_scientific_authority": False,
    }
    assessment = ComputationActionAssessment(
        action_digest=action.digest,
        status=status,
        reasons=final_reasons,
        digest=content_digest(payload),
    )
    assessment.verify()
    return assessment


@dataclass(frozen=True)
class ComputationSelectionReport:
    claim_id: str
    status: ComputationSelectionStatus
    selected_action_id: str | None
    selected_action_digest: str | None
    optimal_action_ids: tuple[str, ...]
    active_hard_obligations: tuple[str, ...]
    reasons: tuple[str, ...]
    action_digests: tuple[str, ...]
    assessment_digests: tuple[str, ...]
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

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "EpistemicComputationSelection.v1",
            "claim_id": self.claim_id,
            "status": self.status.value,
            "selected_action_id": self.selected_action_id,
            "selected_action_digest": self.selected_action_digest,
            "optimal_action_ids": list(self.optimal_action_ids),
            "active_hard_obligations": list(self.active_hard_obligations),
            "reasons": list(self.reasons),
            "action_digests": list(self.action_digests),
            "assessment_digests": list(self.assessment_digests),
            "grants_scientific_authority": False,
            "grants_revision_authority": False,
            "grants_adoption_authority": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("computation selection digest mismatch")
        if self.status is ComputationSelectionStatus.SELECTED:
            if self.selected_action_id is None or self.selected_action_digest is None:
                raise ValueError("selected computation requires an action")
        elif self.selected_action_id is not None or self.selected_action_digest is not None:
            raise ValueError("non-selected computation cannot nominate an action")


def _selection(
    *,
    claim_id: str,
    status: ComputationSelectionStatus,
    actions: Sequence[EpistemicComputationAction],
    assessments: Sequence[ComputationActionAssessment],
    active: Sequence[str],
    selected: EpistemicComputationAction | None = None,
    optima: Sequence[EpistemicComputationAction] = (),
    reasons: Sequence[str] = (),
) -> ComputationSelectionReport:
    payload = {
        "version": "EpistemicComputationSelection.v1",
        "claim_id": claim_id,
        "status": status.value,
        "selected_action_id": None if selected is None else selected.action_id,
        "selected_action_digest": None if selected is None else selected.digest,
        "optimal_action_ids": sorted(action.action_id for action in optima),
        "active_hard_obligations": sorted(set(map(str, active))),
        "reasons": sorted(set(map(str, reasons))),
        "action_digests": sorted(action.digest for action in actions),
        "assessment_digests": sorted(assessment.digest for assessment in assessments),
        "grants_scientific_authority": False,
        "grants_revision_authority": False,
        "grants_adoption_authority": False,
    }
    report = ComputationSelectionReport(
        claim_id=claim_id,
        status=status,
        selected_action_id=payload["selected_action_id"],
        selected_action_digest=payload["selected_action_digest"],
        optimal_action_ids=tuple(payload["optimal_action_ids"]),
        active_hard_obligations=tuple(payload["active_hard_obligations"]),
        reasons=tuple(payload["reasons"]),
        action_digests=tuple(payload["action_digests"]),
        assessment_digests=tuple(payload["assessment_digests"]),
        digest=content_digest(payload),
    )
    report.verify()
    return report


def select_epistemic_computation(
    actions: Sequence[EpistemicComputationAction],
    assessments: Sequence[ComputationActionAssessment],
    *,
    active_hard_obligations: Sequence[str] = (),
) -> ComputationSelectionReport:
    if not actions:
        raise ValueError("at least one computation action is required")
    for action in actions:
        action.verify()
    for assessment in assessments:
        assessment.verify()
    ids = [action.action_id for action in actions]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate computation action")
    claims = {action.claim_id for action in actions}
    if len(claims) != 1:
        raise ValueError("computation selection is claim-relative")
    claim_id = next(iter(claims))
    action_by_digest = {action.digest: action for action in actions}
    assessment_by_digest = {assessment.action_digest: assessment for assessment in assessments}
    if set(action_by_digest) != set(assessment_by_digest) or len(assessment_by_digest) != len(assessments):
        raise ValueError("assessment set must match actions exactly")

    eligible = [
        action
        for action in actions
        if assessment_by_digest[action.digest].status is ComputationAssessmentStatus.ELIGIBLE
    ]
    unresolved = [
        action
        for action in actions
        if assessment_by_digest[action.digest].status is ComputationAssessmentStatus.UNRESOLVED
    ]
    active = tuple(sorted(set(map(str, active_hard_obligations))))

    if active:
        uncovered: list[str] = []
        unresolved_coverage: list[str] = []
        for obligation in active:
            if any(obligation in action.discharges_obligations for action in eligible):
                continue
            if any(obligation in action.discharges_obligations for action in unresolved):
                unresolved_coverage.append(obligation)
            else:
                uncovered.append(obligation)
        if unresolved_coverage:
            return _selection(
                claim_id=claim_id,
                status=ComputationSelectionStatus.UNRESOLVED,
                actions=actions,
                assessments=assessments,
                active=active,
                reasons=[f"HARD_OBLIGATION_COVERAGE_UNRESOLVED:{item}" for item in unresolved_coverage],
            )
        if uncovered:
            return _selection(
                claim_id=claim_id,
                status=ComputationSelectionStatus.NO_ADMISSIBLE,
                actions=actions,
                assessments=assessments,
                active=active,
                reasons=[f"HARD_OBLIGATION_UNCOVERED:{item}" for item in uncovered],
            )
        mandatory = [
            action
            for action in eligible
            if set(action.discharges_obligations) & set(active)
        ]
        max_coverage = max(len(set(action.discharges_obligations) & set(active)) for action in mandatory)
        coverage_best = [
            action for action in mandatory
            if len(set(action.discharges_obligations) & set(active)) == max_coverage
        ]
        max_net = max(action.net_value for action in coverage_best)
        optima = [action for action in coverage_best if action.net_value == max_net]
        if len(optima) > 1:
            return _selection(
                claim_id=claim_id,
                status=ComputationSelectionStatus.MULTIPLE_OPTIMA,
                actions=actions,
                assessments=assessments,
                active=active,
                optima=optima,
                reasons=("HARD_OBLIGATION_PRECEDENCE", "EQUAL_BOUNDED_OPTIMA"),
            )
        return _selection(
            claim_id=claim_id,
            status=ComputationSelectionStatus.SELECTED,
            actions=actions,
            assessments=assessments,
            active=active,
            selected=optima[0],
            optima=optima,
            reasons=("HARD_OBLIGATION_PRECEDENCE",),
        )

    if not eligible:
        if unresolved:
            return _selection(
                claim_id=claim_id,
                status=ComputationSelectionStatus.UNRESOLVED,
                actions=actions,
                assessments=assessments,
                active=(),
                reasons=("ONLY_UNRESOLVED_COMPUTATION_REMAINS",),
            )
        return _selection(
            claim_id=claim_id,
            status=ComputationSelectionStatus.NO_ADMISSIBLE,
            actions=actions,
            assessments=assessments,
            active=(),
            reasons=("ALL_COMPUTATION_ACTIONS_BLOCKED",),
        )

    max_net = max(action.net_value for action in eligible)
    if max_net <= 0:
        return _selection(
            claim_id=claim_id,
            status=ComputationSelectionStatus.LOCAL_COMPUTATION_STOP,
            actions=actions,
            assessments=assessments,
            active=(),
            reasons=("NO_POSITIVE_NET_COMPUTATION_VALUE",),
        )
    optima = [action for action in eligible if action.net_value == max_net]
    if len(optima) > 1:
        return _selection(
            claim_id=claim_id,
            status=ComputationSelectionStatus.MULTIPLE_OPTIMA,
            actions=actions,
            assessments=assessments,
            active=(),
            optima=optima,
            reasons=("EQUAL_BOUNDED_OPTIMA",),
        )
    return _selection(
        claim_id=claim_id,
        status=ComputationSelectionStatus.SELECTED,
        actions=actions,
        assessments=assessments,
        active=(),
        selected=optima[0],
        optima=optima,
        reasons=("POSITIVE_NET_COMPUTATION_VALUE",),
    )


__all__ = [
    "ComputationActionAssessment",
    "ComputationActionState",
    "ComputationAssessmentStatus",
    "ComputationSelectionReport",
    "ComputationSelectionStatus",
    "EpistemicComputationAction",
    "assess_computation_action",
    "build_computation_action",
    "select_epistemic_computation",
]
