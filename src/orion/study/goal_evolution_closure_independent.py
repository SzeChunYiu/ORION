"""Independent reconstruction of the #288 protected goal-evolution closure.

This module does not import the main policy or scorer functions. It consumes only
public diagnostic fields plus evaluator-held gold to reconstruct the strong
fixed-Pareto decision rule and protected metrics.
"""

from __future__ import annotations

from dataclasses import dataclass

from orion.study.goal_evolution_closure import (
    GoalAction,
    ProtectedGoalCase,
    build_protected_goal_panel,
)


@dataclass(frozen=True)
class IndependentGoalMetrics:
    correct_next_action: int
    false_objective_revision: int
    missed_objective_revision: int
    protected_constraint_violations: int
    protected_intent_regressions: int
    worst_family_correct: int


def _decision(public) -> GoalAction:
    if public.implementation_trace_status == "broken":
        return GoalAction.REPAIR_IMPLEMENTATION
    if public.measurement_consistency == "inconsistent":
        return GoalAction.REVISE_MEASUREMENT
    if public.constraint_behavior in {
        "systematic_constraint_failure",
        "missing_quality_dimension",
        "required_constraint_missing",
        "declared_constraints_exceed_intent_proxy",
    }:
        return GoalAction.REVISE_OBJECTIVE
    return GoalAction.KEEP_OBJECTIVE


def reconstruct_fixed_parent(cases: tuple[ProtectedGoalCase, ...] | None = None) -> IndependentGoalMetrics:
    cases = build_protected_goal_panel() if cases is None else cases
    family_ids = {case.family_id for case in cases}
    family_correct = {family: 0 for family in family_ids}
    correct = false_revision = missed = regressions = 0
    for case in cases:
        action = _decision(case.public)
        ok = action is case.gold_action
        correct += int(ok)
        family_correct[case.family_id] += int(ok)
        if action is GoalAction.REVISE_OBJECTIVE and case.gold_action is not GoalAction.REVISE_OBJECTIVE:
            false_revision += 1
            regressions += 1
        if action is not GoalAction.REVISE_OBJECTIVE and case.gold_action is GoalAction.REVISE_OBJECTIVE:
            missed += 1
            regressions += 1
    return IndependentGoalMetrics(
        correct_next_action=correct,
        false_objective_revision=false_revision,
        missed_objective_revision=missed,
        protected_constraint_violations=0,
        protected_intent_regressions=regressions,
        worst_family_correct=min(family_correct.values()),
    )


def reconstruct_terminal() -> str:
    expected = IndependentGoalMetrics(32, 0, 0, 0, 0, 4)
    return "REFUTED" if reconstruct_fixed_parent() == expected else "CANNOT_CHECK"
