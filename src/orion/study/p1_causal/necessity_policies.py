"""Frozen candidate policies for P1 mutation-necessity v2.2.

Every runnable policy consumes only the public world through the budgeted
``NecessityInteractor``. Protected response matrices are host-only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .necessity_cases import RepairLevel
from .necessity_engine import NecessityInteractor, TestedRepair


@dataclass(frozen=True)
class NecessityPolicyOutcome:
    arm_id: str
    selected_repair_id: str | None
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
) -> NecessityPolicyOutcome:
    # FrozenWorldSession exposes these audit properties; Protocol implementations
    # used in tests carry the same narrow surface.
    tested_repairs = tuple(getattr(session, "tested_repair_ids", ()))
    tested_probes = tuple(getattr(session, "tested_probe_ids", ()))
    spent = float(getattr(session, "spent_budget", 0.0))
    return NecessityPolicyOutcome(
        arm_id,
        selected,
        tested_repairs,
        tested_probes,
        spent,
        tuple(notes),
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
    return tuple(sorted(items, key=lambda item: (-item.proposal_confidence, item.repair_id)))


def _by_cost(items):
    return tuple(sorted(items, key=lambda item: (item.declared_cost, -item.proposal_confidence, item.repair_id)))


def static_no_reframe(session: NecessityInteractor) -> NecessityPolicyOutcome:
    return _outcome("static_no_reframe", session, None, "no_intervention")


def immediate_outcome_flip_repair(session: NecessityInteractor) -> NecessityPolicyOutcome:
    ranked = _by_confidence(session.public.repairs)
    for repair in ranked:
        tested = session.test_repair(repair.repair_id)
        if tested is None:
            break
        if tested.response.target_success:
            return _outcome(
                "immediate_outcome_flip_repair",
                session,
                repair.repair_id,
                "first_target_flip",
            )
    return _outcome("immediate_outcome_flip_repair", session, None, "no_target_flip")


def cost_greedy_repair(session: NecessityInteractor) -> NecessityPolicyOutcome:
    for repair in _by_cost(session.public.repairs):
        tested = session.test_repair(repair.repair_id)
        if tested is None:
            break
        if tested.response.target_success:
            return _outcome("cost_greedy_repair", session, repair.repair_id, "cheapest_target_flip")
    return _outcome("cost_greedy_repair", session, None, "budget_exhausted")


def reflect_like_replay(session: NecessityInteractor) -> NecessityPolicyOutcome:
    # One-shot diagnosis is represented by the most confident high-level
    # proposal. REFLECT-like replay tests that diagnosis-specific change and
    # accepts an outcome flip; it does not prove necessity.
    candidates = _by_confidence(_high_repairs(session))
    if not candidates:
        return _outcome("reflect_like_replay", session, None, "no_high_level_proposal")
    tested = session.test_repair(candidates[0].repair_id)
    if tested is not None and tested.response.target_success:
        return _outcome("reflect_like_replay", session, candidates[0].repair_id, "diagnosis_specific_replay_flip")
    return _outcome("reflect_like_replay", session, None, "replay_did_not_restore")


def car_like_causal_replay(session: NecessityInteractor) -> NecessityPolicyOutcome:
    # Use the budget on the most confident intervention candidates and select
    # the strongest observed target effect. With binary target outcomes, ties
    # remain in frozen confidence order.
    tested_successes: list[TestedRepair] = []
    for repair in _by_confidence(session.public.repairs):
        tested = session.test_repair(repair.repair_id)
        if tested is None:
            break
        if tested.response.target_success:
            tested_successes.append(tested)
    if not tested_successes:
        return _outcome("car_like_causal_replay", session, None, "no_positive_intervention")
    confidence = {item.repair_id: item.proposal_confidence for item in session.public.repairs}
    selected = max(tested_successes, key=lambda item: (confidence[item.repair_id], item.repair_id))
    return _outcome("car_like_causal_replay", session, selected.repair_id, "largest_observed_target_effect")


def _probe_by_prefix(session: NecessityInteractor, prefix: str):
    return next(item for item in session.public.diagnostic_probes if item.description.startswith(prefix))


def active_voi_repair_parent(session: NecessityInteractor) -> NecessityPolicyOutcome:
    # Credential-free active-diagnosis parent: sequentially test the two lower
    # causal stages, stopping when one is identified. If both are ruled out,
    # use the remaining budget on the most confident high-level proposal.
    source_probe = _probe_by_prefix(session, "check whether the missing evidence")
    source = session.run_probe(source_probe.probe_id)
    if source is None:
        return _outcome("active_voi_repair_parent", session, None, "no_budget_source_probe")
    if source.response.observation == "SOURCE_GAP":
        repair = _by_confidence(_repairs_at(session, RepairLevel.EVIDENCE))[0]
        tested = session.test_repair(repair.repair_id)
        selected = repair.repair_id if tested and tested.response.target_success else None
        return _outcome("active_voi_repair_parent", session, selected, "source_probe")

    exec_probe = _probe_by_prefix(session, "check whether the current implementation")
    execution = session.run_probe(exec_probe.probe_id)
    if execution is None:
        return _outcome("active_voi_repair_parent", session, None, "no_budget_execution_probe")
    if execution.response.observation == "EXECUTION_GAP":
        repair = _by_confidence(_repairs_at(session, RepairLevel.EXECUTION))[0]
        tested = session.test_repair(repair.repair_id)
        selected = repair.repair_id if tested and tested.response.target_success else None
        return _outcome("active_voi_repair_parent", session, selected, "execution_probe")

    high = _by_confidence(_high_repairs(session))[0]
    tested = session.test_repair(high.repair_id)
    selected = high.repair_id if tested and tested.response.target_success else None
    return _outcome("active_voi_repair_parent", session, selected, "lower_levels_ruled_out")


def darc_r2act_dependency_parent(session: NecessityInteractor) -> NecessityPolicyOutcome:
    # Strong operational parent: confidence-gated diagnosis-to-action with
    # response-aware validity. It accepts a high-level repair if it restores the
    # motivating task and does not visibly break a protected sibling, but it
    # does not ask whether that mutation was *necessary* because a lower-level
    # repair could also have worked.
    high = _by_confidence(_high_repairs(session))[0]
    if session.public.initial_high_level_confidence >= 0.80:
        tested = session.test_repair(high.repair_id)
        if tested and tested.response.target_success and tested.response.protected_sibling_ok:
            return _outcome("darc_r2act_dependency_parent", session, high.repair_id, "high_confidence_admissible_repair")
    for level in (RepairLevel.EVIDENCE, RepairLevel.EXECUTION):
        repair = _by_confidence(_repairs_at(session, level))[0]
        tested = session.test_repair(repair.repair_id)
        if tested is None:
            break
        if tested.response.target_success and tested.response.protected_sibling_ok:
            return _outcome("darc_r2act_dependency_parent", session, repair.repair_id, "lower_level_recovery")
    tested = session.test_repair(high.repair_id)
    if tested and tested.response.target_success and tested.response.protected_sibling_ok:
        return _outcome("darc_r2act_dependency_parent", session, high.repair_id, "fallback_high_level_recovery")
    return _outcome("darc_r2act_dependency_parent", session, None, "no_admissible_repair")


def orion_mutation_necessity(session: NecessityInteractor) -> NecessityPolicyOutcome:
    # Lower-level repair executions are themselves causal discriminators. A
    # high-level mutation is attempted only after both lower levels fail.
    for level in (RepairLevel.EVIDENCE, RepairLevel.EXECUTION):
        repair = _by_confidence(_repairs_at(session, level))[0]
        tested = session.test_repair(repair.repair_id)
        if tested is None:
            return _outcome("orion_mutation_necessity", session, None, "budget_before_lower_level_elimination")
        if tested.response.target_success and tested.response.protected_sibling_ok:
            return _outcome("orion_mutation_necessity", session, repair.repair_id, "lower_level_sufficient_high_level_not_necessary")

    for repair in _by_confidence(_high_repairs(session)):
        tested = session.test_repair(repair.repair_id)
        if tested is None:
            break
        if not tested.response.target_success:
            continue
        if not tested.response.protected_sibling_ok:
            continue
        expected = _expected_impact(session, repair.coordinate)
        if tuple(tested.response.observed_invalidated_ids) != expected:
            continue
        return _outcome(
            "orion_mutation_necessity",
            session,
            repair.repair_id,
            "lower_levels_excluded+target_effect+protected_preservation+impact_binding",
        )
    return _outcome("orion_mutation_necessity", session, None, "necessity_certificate_incomplete")


def _expected_impact(session: NecessityInteractor, coordinate: str) -> tuple[str, ...]:
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
        item.closure_id for item in session.public.dependencies if item.closure_id in selected
    )


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


__all__ = [
    "NecessityPolicyOutcome",
    "RUNNABLE_ARMS",
    "active_voi_repair_parent",
    "car_like_causal_replay",
    "cost_greedy_repair",
    "darc_r2act_dependency_parent",
    "immediate_outcome_flip_repair",
    "orion_mutation_necessity",
    "reflect_like_replay",
    "static_no_reframe",
]
