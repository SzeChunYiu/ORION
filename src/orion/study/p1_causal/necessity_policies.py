"""Frozen candidate policies for P1 mutation-necessity v2.2.

Every runnable policy consumes only the public world through the budgeted
``NecessityInteractor``. Protected response matrices are host-only.  Donor
mechanics are implemented as first-class parents rather than weakened foils:
active diagnosis, causal replay, diagnosis-to-action admission, and dependency
rollback are all available to the relevant comparator arms.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .necessity_cases import RepairLevel
from .necessity_engine import NecessityInteractor, TestedRepair


@dataclass(frozen=True)
class NecessityPolicyOutcome:
    arm_id: str
    selected_repair_id: str | None
    reopened_ids: tuple[str, ...]
    tested_repair_ids: tuple[str, ...]
    tested_probe_ids: tuple[str, ...]
    spent_budget: float
    notes: tuple[str, ...] = ()

    def to_payload(self) -> dict:
        return asdict(self)


def _outcome(
    arm_id: str,
    session: NecessityInteractor,
    selected: str | None,
    *notes: str,
    reopened_ids: tuple[str, ...] = (),
) -> NecessityPolicyOutcome:
    tested_repairs = tuple(getattr(session, "tested_repair_ids", ()))
    tested_probes = tuple(getattr(session, "tested_probe_ids", ()))
    spent = float(getattr(session, "spent_budget", 0.0))
    return NecessityPolicyOutcome(
        arm_id=arm_id,
        selected_repair_id=selected,
        reopened_ids=tuple(reopened_ids),
        tested_repair_ids=tested_repairs,
        tested_probe_ids=tested_probes,
        spent_budget=spent,
        notes=tuple(notes),
    )


def _repairs_at(session: NecessityInteractor, level: RepairLevel):
    return tuple(item for item in session.public.repairs if item.level is level)


def _high_repairs(session: NecessityInteractor):
    return tuple(
        item
        for item in session.public.repairs
        if item.level in {RepairLevel.FORMULATION, RepairLevel.SEARCH_UNIVERSE}
    )


def _by_confidence(items):
    return tuple(
        sorted(items, key=lambda item: (-item.proposal_confidence, item.repair_id))
    )


def _by_cost(items):
    return tuple(
        sorted(
            items,
            key=lambda item: (
                item.declared_cost,
                -item.proposal_confidence,
                item.repair_id,
            ),
        )
    )


def _expected_impact(
    session: NecessityInteractor,
    coordinate: str,
) -> tuple[str, ...]:
    direct = {
        item.closure_id
        for item in session.public.dependencies
        if item.declared_coordinate == coordinate
    }
    selected = set(direct)
    changed = True
    while changed:
        changed = False
        for item in session.public.dependencies:
            if item.closure_id in selected:
                continue
            if any(parent in selected for parent in item.parent_ids):
                selected.add(item.closure_id)
                changed = True
    return tuple(
        item.closure_id
        for item in session.public.dependencies
        if item.closure_id in selected
    )


def _reopen_for_selected(
    session: NecessityInteractor,
    repair_id: str,
) -> tuple[str, ...]:
    repair = next(
        item for item in session.public.repairs if item.repair_id == repair_id
    )
    if repair.level not in {
        RepairLevel.FORMULATION,
        RepairLevel.SEARCH_UNIVERSE,
    }:
        return ()
    return _expected_impact(session, repair.coordinate)


def static_no_reframe(session: NecessityInteractor) -> NecessityPolicyOutcome:
    return _outcome("static_no_reframe", session, None, "no_intervention")


def immediate_outcome_flip_repair(
    session: NecessityInteractor,
) -> NecessityPolicyOutcome:
    for repair in _by_confidence(session.public.repairs):
        tested = session.test_repair(repair.repair_id)
        if tested is None:
            break
        if tested.response.target_success:
            return _outcome(
                "immediate_outcome_flip_repair",
                session,
                repair.repair_id,
                "first_target_flip",
                reopened_ids=_reopen_for_selected(session, repair.repair_id),
            )
    return _outcome(
        "immediate_outcome_flip_repair",
        session,
        None,
        "no_target_flip",
    )


def cost_greedy_repair(session: NecessityInteractor) -> NecessityPolicyOutcome:
    for repair in _by_cost(session.public.repairs):
        tested = session.test_repair(repair.repair_id)
        if tested is None:
            break
        if tested.response.target_success:
            return _outcome(
                "cost_greedy_repair",
                session,
                repair.repair_id,
                "cheapest_target_flip",
                reopened_ids=_reopen_for_selected(session, repair.repair_id),
            )
    return _outcome("cost_greedy_repair", session, None, "budget_exhausted")


def reflect_like_replay(session: NecessityInteractor) -> NecessityPolicyOutcome:
    candidates = _by_confidence(_high_repairs(session))
    if not candidates:
        return _outcome(
            "reflect_like_replay",
            session,
            None,
            "no_high_level_proposal",
        )
    tested = session.test_repair(candidates[0].repair_id)
    if tested is not None and tested.response.target_success:
        return _outcome(
            "reflect_like_replay",
            session,
            candidates[0].repair_id,
            "diagnosis_specific_replay_flip",
            reopened_ids=_reopen_for_selected(session, candidates[0].repair_id),
        )
    return _outcome(
        "reflect_like_replay",
        session,
        None,
        "replay_did_not_restore",
    )


def car_like_causal_replay(session: NecessityInteractor) -> NecessityPolicyOutcome:
    tested_successes: list[TestedRepair] = []
    for repair in _by_confidence(session.public.repairs):
        tested = session.test_repair(repair.repair_id)
        if tested is None:
            break
        if tested.response.target_success:
            tested_successes.append(tested)
    if not tested_successes:
        return _outcome(
            "car_like_causal_replay",
            session,
            None,
            "no_positive_intervention",
        )
    confidence = {
        item.repair_id: item.proposal_confidence
        for item in session.public.repairs
    }
    selected = max(
        tested_successes,
        key=lambda item: (confidence[item.repair_id], item.repair_id),
    )
    return _outcome(
        "car_like_causal_replay",
        session,
        selected.repair_id,
        "largest_observed_target_effect",
        reopened_ids=_reopen_for_selected(session, selected.repair_id),
    )


def _probe_by_prefix(session: NecessityInteractor, prefix: str):
    return next(
        item
        for item in session.public.diagnostic_probes
        if item.description.startswith(prefix)
    )


def active_voi_repair_parent(
    session: NecessityInteractor,
) -> NecessityPolicyOutcome:
    """Absorb active diagnosis as a strong parent.

    The arm identifies lower causal stages first.  If they are ruled out it
    spends the remaining budget on the strongest high-level proposal.  It has
    dependency rollback, but it does not prove protected mutation necessity by
    testing alternative target-flipping high-level proposals.
    """

    source_probe = _probe_by_prefix(
        session,
        "check whether the missing evidence",
    )
    source = session.run_probe(source_probe.probe_id)
    if source is None:
        return _outcome(
            "active_voi_repair_parent",
            session,
            None,
            "no_budget_source_probe",
        )
    if source.response.observation == "SOURCE_GAP":
        repair = _by_confidence(_repairs_at(session, RepairLevel.EVIDENCE))[0]
        tested = session.test_repair(repair.repair_id)
        selected = (
            repair.repair_id
            if tested and tested.response.target_success
            else None
        )
        return _outcome(
            "active_voi_repair_parent",
            session,
            selected,
            "source_probe",
        )

    exec_probe = _probe_by_prefix(
        session,
        "check whether the current implementation",
    )
    execution = session.run_probe(exec_probe.probe_id)
    if execution is None:
        return _outcome(
            "active_voi_repair_parent",
            session,
            None,
            "no_budget_execution_probe",
        )
    if execution.response.observation == "EXECUTION_GAP":
        repair = _by_confidence(_repairs_at(session, RepairLevel.EXECUTION))[0]
        tested = session.test_repair(repair.repair_id)
        selected = (
            repair.repair_id
            if tested and tested.response.target_success
            else None
        )
        return _outcome(
            "active_voi_repair_parent",
            session,
            selected,
            "execution_probe",
        )

    high = _by_confidence(_high_repairs(session))[0]
    tested = session.test_repair(high.repair_id)
    selected = (
        high.repair_id
        if tested
        and tested.response.target_success
        and tested.response.protected_sibling_ok
        else None
    )
    return _outcome(
        "active_voi_repair_parent",
        session,
        selected,
        "lower_levels_ruled_out",
        reopened_ids=(
            _reopen_for_selected(session, high.repair_id)
            if selected
            else ()
        ),
    )


def darc_r2act_dependency_parent(
    session: NecessityInteractor,
) -> NecessityPolicyOutcome:
    """Absorb diagnosis-to-action admission plus dependency rollback."""

    high = _by_confidence(_high_repairs(session))[0]
    if session.public.initial_high_level_confidence >= 0.80:
        tested = session.test_repair(high.repair_id)
        if (
            tested
            and tested.response.target_success
            and tested.response.protected_sibling_ok
        ):
            return _outcome(
                "darc_r2act_dependency_parent",
                session,
                high.repair_id,
                "high_confidence_admissible_repair",
                reopened_ids=_reopen_for_selected(session, high.repair_id),
            )
    for level in (RepairLevel.EVIDENCE, RepairLevel.EXECUTION):
        repair = _by_confidence(_repairs_at(session, level))[0]
        tested = session.test_repair(repair.repair_id)
        if tested is None:
            break
        if (
            tested.response.target_success
            and tested.response.protected_sibling_ok
        ):
            return _outcome(
                "darc_r2act_dependency_parent",
                session,
                repair.repair_id,
                "lower_level_recovery",
            )
    tested = session.test_repair(high.repair_id)
    if (
        tested
        and tested.response.target_success
        and tested.response.protected_sibling_ok
    ):
        return _outcome(
            "darc_r2act_dependency_parent",
            session,
            high.repair_id,
            "fallback_high_level_recovery",
            reopened_ids=_reopen_for_selected(session, high.repair_id),
        )
    return _outcome(
        "darc_r2act_dependency_parent",
        session,
        None,
        "no_admissible_repair",
    )


def _full_certificate(
    session: NecessityInteractor,
    *,
    arm_id: str,
    check_sibling: bool,
    bind_dependency_impact: bool,
) -> NecessityPolicyOutcome:
    for level in (RepairLevel.EVIDENCE, RepairLevel.EXECUTION):
        repair = _by_confidence(_repairs_at(session, level))[0]
        tested = session.test_repair(repair.repair_id)
        if tested is None:
            return _outcome(
                arm_id,
                session,
                None,
                "budget_before_lower_level_elimination",
            )
        if tested.response.target_success and (
            tested.response.protected_sibling_ok or not check_sibling
        ):
            return _outcome(
                arm_id,
                session,
                repair.repair_id,
                "lower_level_sufficient_high_level_not_necessary",
            )

    for repair in _by_confidence(_high_repairs(session)):
        tested = session.test_repair(repair.repair_id)
        if tested is None:
            break
        if not tested.response.target_success:
            continue
        if check_sibling and not tested.response.protected_sibling_ok:
            continue
        expected = _expected_impact(session, repair.coordinate)
        if bind_dependency_impact and (
            tuple(tested.response.observed_invalidated_ids) != expected
        ):
            continue
        reopened = expected if bind_dependency_impact else ()
        return _outcome(
            arm_id,
            session,
            repair.repair_id,
            "necessity_certificate_selected",
            reopened_ids=reopened,
        )
    return _outcome(
        arm_id,
        session,
        None,
        "necessity_certificate_incomplete",
    )


def orion_mutation_necessity(
    session: NecessityInteractor,
) -> NecessityPolicyOutcome:
    return _full_certificate(
        session,
        arm_id="orion_mutation_necessity",
        check_sibling=True,
        bind_dependency_impact=True,
    )


# Direct mechanism ablations.  Each removes exactly one registered component
# while retaining the same public world and scorer.
def orion_without_lower_level_exclusion(
    session: NecessityInteractor,
) -> NecessityPolicyOutcome:
    for repair in _by_confidence(_high_repairs(session)):
        tested = session.test_repair(repair.repair_id)
        if tested is None:
            break
        if tested.response.target_success and tested.response.protected_sibling_ok:
            return _outcome(
                "orion_without_lower_level_exclusion",
                session,
                repair.repair_id,
                "high_level_without_lower_level_exclusion",
                reopened_ids=_reopen_for_selected(session, repair.repair_id),
            )
    return _outcome(
        "orion_without_lower_level_exclusion",
        session,
        None,
        "no_high_level_repair",
    )


def orion_without_protected_sibling_check(
    session: NecessityInteractor,
) -> NecessityPolicyOutcome:
    return _full_certificate(
        session,
        arm_id="orion_without_protected_sibling_check",
        check_sibling=False,
        bind_dependency_impact=True,
    )


def orion_without_dependency_impact_binding(
    session: NecessityInteractor,
) -> NecessityPolicyOutcome:
    return _full_certificate(
        session,
        arm_id="orion_without_dependency_impact_binding",
        check_sibling=True,
        bind_dependency_impact=False,
    )


def orion_without_KWM_level_ordering(
    session: NecessityInteractor,
) -> NecessityPolicyOutcome:
    for repair in _by_confidence(session.public.repairs):
        tested = session.test_repair(repair.repair_id)
        if tested is None:
            break
        if tested.response.target_success and tested.response.protected_sibling_ok:
            return _outcome(
                "orion_without_KWM_level_ordering",
                session,
                repair.repair_id,
                "confidence_order_without_epistemic_level_order",
                reopened_ids=_reopen_for_selected(session, repair.repair_id),
            )
    return _outcome(
        "orion_without_KWM_level_ordering",
        session,
        None,
        "no_valid_repair",
    )


def orion_with_unlimited_intervention_budget(
    session: NecessityInteractor,
) -> NecessityPolicyOutcome:
    base = _full_certificate(
        session,
        arm_id="orion_with_unlimited_intervention_budget",
        check_sibling=True,
        bind_dependency_impact=True,
    )
    return base


RUNNABLE_ARMS = (
    static_no_reframe,
    immediate_outcome_flip_repair,
    cost_greedy_repair,
    reflect_like_replay,
    car_like_causal_replay,
    active_voi_repair_parent,
    darc_r2act_dependency_parent,
    orion_mutation_necessity,
)

ABLATION_ARMS = (
    orion_without_lower_level_exclusion,
    orion_without_protected_sibling_check,
    orion_without_dependency_impact_binding,
    orion_without_KWM_level_ordering,
    orion_with_unlimited_intervention_budget,
)


__all__ = [
    "ABLATION_ARMS",
    "NecessityPolicyOutcome",
    "RUNNABLE_ARMS",
    "active_voi_repair_parent",
    "car_like_causal_replay",
    "cost_greedy_repair",
    "darc_r2act_dependency_parent",
    "immediate_outcome_flip_repair",
    "orion_mutation_necessity",
    "orion_with_unlimited_intervention_budget",
    "orion_without_KWM_level_ordering",
    "orion_without_dependency_impact_binding",
    "orion_without_lower_level_exclusion",
    "orion_without_protected_sibling_check",
    "reflect_like_replay",
    "static_no_reframe",
]
