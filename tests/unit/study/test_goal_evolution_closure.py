from __future__ import annotations

import json
from pathlib import Path

from orion.study.goal_evolution_closure import (
    GoalArm,
    build_goal_closure_report,
    build_protected_goal_panel,
)
from orion.study.goal_evolution_closure_independent import (
    IndependentGoalMetrics,
    reconstruct_fixed_parent,
    reconstruct_terminal,
)

ROOT = Path(__file__).resolve().parents[3]
EXPECTED = ROOT / "development" / "protected-goal-evolution-closure" / "EXPECTED_V1.json"
PROTOCOL = ROOT / "research" / "goal-evolution" / "PROTOCOL_V1.json"


def _expected() -> dict:
    return json.loads(EXPECTED.read_text())


def test_v1_protocol_remains_pre_outcome_and_immutable_in_scope() -> None:
    protocol = json.loads(PROTOCOL.read_text())
    assert protocol["protocol_status"] == "DESIGN_FROZEN"
    assert protocol["outcome_accessed"] is False
    assert protocol["v1_protocol_mutated"] is False
    assert protocol["max_revision_cycles"] == 3


def test_hidden_intent_panel_binds_exactly_the_eight_v1_families() -> None:
    protocol = json.loads(PROTOCOL.read_text())
    cases = build_protected_goal_panel()
    protocol_families = {item["family_id"] for item in protocol["benchmark"]["families"]}
    assert len(cases) == 32
    assert {case.family_id for case in cases} == protocol_families
    assert len({case.public.case_id for case in cases}) == 32
    for case in cases:
        assert not hasattr(case.public, "gold_action")
        assert not hasattr(case.public, "hidden_intent_score_old")
        assert not hasattr(case.public, "protected_constraints")


def test_main_report_matches_exact_pre_run_expectations() -> None:
    report = build_goal_closure_report()
    expected = _expected()
    assert expected["frozen_before_runner"] is True
    assert expected["outcome_accessed"] is False
    assert report.case_count == expected["case_count"]
    for arm, metrics in report.metrics:
        assert metrics.__dict__ == expected["expected_metrics"][arm]
    assert report.strong_parent_ties_orion is True
    assert report.candidate_terminal == expected["expected_terminal_if_reconstructed"]
    assert report.grants_scientific_authority is False
    assert report.grants_goal_mutation_authority is False
    assert report.grants_issue_closure_authority is False


def test_strong_fixed_pareto_parent_ties_orion_exactly() -> None:
    metrics = dict(build_goal_closure_report().metrics)
    assert metrics[GoalArm.FIXED_MULTI_OBJECTIVE_PARETO_PROTECTED.value] == metrics[
        GoalArm.ORION_PROTECTED_GOAL_EVOLUTION.value
    ]
    assert metrics[GoalArm.ORION_PROTECTED_GOAL_EVOLUTION.value].correct_next_action == 32
    assert metrics[GoalArm.ORION_PROTECTED_GOAL_EVOLUTION.value].protected_intent_regressions == 0


def test_unconstrained_goal_rewrite_exposes_proxy_and_constraint_failures() -> None:
    metrics = dict(build_goal_closure_report().metrics)
    saga = metrics[GoalArm.UNCONSTRAINED_SAGA_LIKE.value]
    assert saga.false_objective_revision == 12
    assert saga.protected_constraint_violations == 8
    assert saga.protected_intent_regressions == 12


def test_independent_reconstruction_confirms_negative_terminal() -> None:
    assert reconstruct_fixed_parent() == IndependentGoalMetrics(32, 0, 0, 0, 0, 4)
    assert reconstruct_terminal() == "REFUTED"
