"""Frozen candidate policies for the P1 R3 authority-value benchmark.

Policies consume only :class:`PublicAuthorityView`.  The full ORION arms call
P1's shipped ``request_action`` licensing path; parent/simple arms are separate
policy implementations and never consult protected gold.
"""

from __future__ import annotations

from dataclasses import dataclass

from .authority_value_cases import (
    ActionRequest,
    PublicAuthorityView,
    RepairProposal,
    ResponsibilityClass,
    TaskAction,
)
from .belief import ALL_AUTHORITY_CLASSES, AuthorityClass, replace_masses, uniform_unresolved
from .licensing import EpistemicAction, request_action


@dataclass(frozen=True)
class PolicyOutcome:
    arm_id: str
    applied_requests: tuple[ActionRequest, ...]
    reopened_ids: tuple[str, ...]
    blocked: bool
    cannot_check: bool
    negative_history_retained: bool = True
    notes: tuple[str, ...] = ()

    def to_payload(self) -> dict:
        return {
            "arm_id": self.arm_id,
            "applied_requests": [item.to_payload() for item in self.applied_requests],
            "reopened_ids": list(self.reopened_ids),
            "blocked": self.blocked,
            "cannot_check": self.cannot_check,
            "negative_history_retained": self.negative_history_retained,
            "notes": list(self.notes),
        }


_EXPECTED_ACTION = {
    ResponsibilityClass.EVIDENCE: TaskAction.ACQUIRE_EVIDENCE,
    ResponsibilityClass.EXECUTION: TaskAction.REPAIR_EXECUTION,
    ResponsibilityClass.FORMULATION: TaskAction.REWRITE_FORMULATION,
    ResponsibilityClass.SEARCH_UNIVERSE: TaskAction.EXPAND_SEARCH_UNIVERSE,
}

_TASK_TO_EPISTEMIC = {
    TaskAction.ACQUIRE_EVIDENCE: EpistemicAction.ACQUIRE_EVIDENCE,
    TaskAction.REPAIR_EXECUTION: EpistemicAction.REPAIR_EXECUTION,
    TaskAction.REWRITE_FORMULATION: EpistemicAction.REWRITE_FORMULATION,
    TaskAction.EXPAND_SEARCH_UNIVERSE: EpistemicAction.EXPAND_SEARCH_UNIVERSE,
    TaskAction.REWRITE_METHOD: EpistemicAction.REWRITE_METHOD,
    TaskAction.BROAD_WM_MUTATION: EpistemicAction.BROAD_WM_MUTATION,
}


def _matches_diagnosis(view: PublicAuthorityView, request: ActionRequest) -> bool:
    expected = _EXPECTED_ACTION.get(view.diagnosis.responsibility)
    if expected is None or request.action is not expected:
        return False
    if request.action in {
        TaskAction.REWRITE_FORMULATION,
        TaskAction.EXPAND_SEARCH_UNIVERSE,
    }:
        return request.coordinate == view.diagnosis.diagnosed_coordinate
    return True


def _candidate_proposal(view: PublicAuthorityView) -> RepairProposal | None:
    """Pick a plausible local-recovery proposal without consulting gold.

    Proposal order is part of the public frozen case.  Prediction is proposal
    metadata supplied equally to every arm, not a host label.
    """

    for proposal in view.proposals:
        if proposal.predicts_root_recovery and any(
            _matches_diagnosis(view, request) for request in proposal.requests
        ):
            return proposal
    return None


def _direct_reopen(view: PublicAuthorityView, coordinates: tuple[str, ...]) -> tuple[str, ...]:
    changed = set(coordinates)
    return tuple(
        closure.closure_id
        for closure in view.closures
        if changed.intersection(closure.dependency_coordinates)
    )


def _recursive_reopen(view: PublicAuthorityView, coordinates: tuple[str, ...]) -> tuple[str, ...]:
    selected = set(_direct_reopen(view, coordinates))
    progress = True
    while progress:
        progress = False
        for closure in view.closures:
            if closure.closure_id in selected:
                continue
            if any(parent in selected for parent in closure.parent_ids):
                selected.add(closure.closure_id)
                progress = True
    return tuple(
        closure.closure_id for closure in view.closures if closure.closure_id in selected
    )


def _changed_coordinates(requests: tuple[ActionRequest, ...]) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            item.coordinate
            for item in requests
            if item.action
            in {TaskAction.REWRITE_FORMULATION, TaskAction.EXPAND_SEARCH_UNIVERSE}
            and item.coordinate
        )
    )


def _belief_for(view: PublicAuthorityView):
    responsibility = view.diagnosis.responsibility
    if responsibility is ResponsibilityClass.UNRESOLVED:
        return uniform_unresolved(evidence_ids=view.diagnosis.evidence_ids)
    target = AuthorityClass(responsibility.value)
    masses = {item: 0.05 for item in ALL_AUTHORITY_CLASSES}
    masses[target] = 0.8
    masses[AuthorityClass.UNRESOLVED] = 0.05
    return replace_masses(
        uniform_unresolved(evidence_ids=view.diagnosis.evidence_ids),
        masses,
        evidence_ids=view.diagnosis.evidence_ids,
        intervention_ids=("host-frozen-intervention",)
        if view.diagnosis.intervention_backed
        else (),
        intervention_backed=view.diagnosis.intervention_backed,
        support_ids={target: view.diagnosis.evidence_ids},
    )


def block_all_conservative(view: PublicAuthorityView) -> PolicyOutcome:
    return PolicyOutcome("block_all_conservative", (), (), True, False)


def unrestricted_outcome_flip_repair(view: PublicAuthorityView) -> PolicyOutcome:
    proposal = _candidate_proposal(view)
    if proposal is None:
        return PolicyOutcome("unrestricted_outcome_flip_repair", (), (), True, False)
    applied = proposal.requests
    return PolicyOutcome(
        "unrestricted_outcome_flip_repair",
        applied,
        (),
        False,
        False,
        notes=(f"proposal:{proposal.proposal_id}",),
    )


def reflect_like_local_repair(view: PublicAuthorityView) -> PolicyOutcome:
    proposal = _candidate_proposal(view)
    if proposal is None:
        return PolicyOutcome("reflect_like_local_repair", (), (), True, False)
    # Diagnosis-specific local replay applies the patch as proposed.  It has no
    # P1 scientific-authority projection and no dependency propagation.
    return PolicyOutcome(
        "reflect_like_local_repair",
        proposal.requests,
        (),
        False,
        False,
        notes=(f"proposal:{proposal.proposal_id}", "local_replay"),
    )


def reflect_evigraph_composite_parent(view: PublicAuthorityView) -> PolicyOutcome:
    proposal = _candidate_proposal(view)
    if proposal is None:
        return PolicyOutcome("reflect_evigraph_composite_parent", (), (), True, False)
    applied = proposal.requests
    reopened = _recursive_reopen(view, _changed_coordinates(applied))
    return PolicyOutcome(
        "reflect_evigraph_composite_parent",
        applied,
        reopened,
        False,
        False,
        notes=(f"proposal:{proposal.proposal_id}", "local_replay+recursive_downstream"),
    )


def class_conditioned_minimal_repair(view: PublicAuthorityView) -> PolicyOutcome:
    proposal = _candidate_proposal(view)
    if proposal is None:
        return PolicyOutcome("class_conditioned_minimal_repair", (), (), True, False)
    matching = tuple(request for request in proposal.requests if _matches_diagnosis(view, request))
    if not matching:
        return PolicyOutcome("class_conditioned_minimal_repair", (), (), True, False)
    reopened = _direct_reopen(view, _changed_coordinates(matching))
    return PolicyOutcome(
        "class_conditioned_minimal_repair",
        matching,
        reopened,
        False,
        False,
        notes=(f"proposal:{proposal.proposal_id}", "class_conditioned+direct_dependencies"),
    )


def _orion_allowed_requests(view: PublicAuthorityView, proposal: RepairProposal) -> tuple[tuple[ActionRequest, ...], tuple[str, ...], bool]:
    state = _belief_for(view)
    applied: list[ActionRequest] = []
    notes: list[str] = []
    cannot_check = False
    for request in proposal.requests:
        decision = request_action(state, _TASK_TO_EPISTEMIC[request.action])
        if decision.cannot_check:
            cannot_check = True
        if not decision.granted:
            notes.append(
                f"denied:{request.action.value}:{decision.refusal.value if decision.refusal else 'REFUSED'}"
            )
            continue
        if request.action in {
            TaskAction.REWRITE_FORMULATION,
            TaskAction.EXPAND_SEARCH_UNIVERSE,
        } and request.coordinate != view.diagnosis.diagnosed_coordinate:
            notes.append(f"denied_coordinate:{request.coordinate}")
            continue
        applied.append(request)
    return tuple(applied), tuple(notes), cannot_check


def _orion_policy(view: PublicAuthorityView, *, recursive_reopen: bool, arm_id: str) -> PolicyOutcome:
    proposal = _candidate_proposal(view)
    if proposal is None:
        return PolicyOutcome(arm_id, (), (), True, False, notes=("no_recovery_proposal",))
    applied, notes, cannot_check = _orion_allowed_requests(view, proposal)
    expected = _EXPECTED_ACTION.get(view.diagnosis.responsibility)
    has_local_repair = expected is not None and any(
        request.action is expected and _matches_diagnosis(view, request)
        for request in applied
    )
    if not has_local_repair:
        return PolicyOutcome(
            arm_id,
            applied,
            (),
            True,
            cannot_check or view.diagnosis.responsibility is ResponsibilityClass.UNRESOLVED,
            notes=(*notes, "no_licensed_local_repair"),
        )
    coordinates = _changed_coordinates(applied)
    reopened = (
        _recursive_reopen(view, coordinates)
        if recursive_reopen
        else ()
    )
    return PolicyOutcome(
        arm_id,
        applied,
        reopened,
        False,
        cannot_check,
        notes=notes,
    )


def orion_typed_permission(view: PublicAuthorityView) -> PolicyOutcome:
    return _orion_policy(
        view,
        recursive_reopen=False,
        arm_id="orion_typed_permission",
    )


def orion_typed_permission_dependency_reopen(view: PublicAuthorityView) -> PolicyOutcome:
    return _orion_policy(
        view,
        recursive_reopen=True,
        arm_id="orion_typed_permission_dependency_reopen",
    )


def full_reset_after_repair(view: PublicAuthorityView) -> PolicyOutcome:
    base = _orion_policy(view, recursive_reopen=False, arm_id="full_reset_after_repair")
    if base.blocked:
        return base
    return PolicyOutcome(
        "full_reset_after_repair",
        base.applied_requests,
        tuple(closure.closure_id for closure in view.closures),
        False,
        base.cannot_check,
        notes=(*base.notes, "full_reset"),
    )


MATCHED_ARMS = (
    block_all_conservative,
    unrestricted_outcome_flip_repair,
    reflect_like_local_repair,
    reflect_evigraph_composite_parent,
    class_conditioned_minimal_repair,
    orion_typed_permission,
    orion_typed_permission_dependency_reopen,
    full_reset_after_repair,
)


__all__ = [
    "MATCHED_ARMS",
    "PolicyOutcome",
    "block_all_conservative",
    "class_conditioned_minimal_repair",
    "full_reset_after_repair",
    "orion_typed_permission",
    "orion_typed_permission_dependency_reopen",
    "reflect_evigraph_composite_parent",
    "reflect_like_local_repair",
    "unrestricted_outcome_flip_repair",
]
