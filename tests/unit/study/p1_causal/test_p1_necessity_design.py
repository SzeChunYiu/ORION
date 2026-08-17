from __future__ import annotations

from collections import defaultdict

from orion.study.p1_causal.necessity_cases import candidate_view_leaks
from orion.study.p1_causal.necessity_cases_v2 import generate_necessity_worlds_v2
from orion.study.p1_causal.necessity_engine import FrozenWorldSession
from orion.study.p1_causal.necessity_policies import ABLATION_ARMS, RUNNABLE_ARMS
from orion.study.p1_causal.necessity_scoring import (
    aggregate_necessity_scores,
    score_necessity_world,
)
from orion.study.p1_causal.necessity_statistics import analyze_necessity_campaign


def _development_worlds():
    # Deliberately different from the frozen confirmatory seed 202608172211.
    return generate_necessity_worlds_v2(seed=30303, hidden_shift_n=80, control_n=80)


def _run(policies, *, unlimited: bool = False):
    rows = []
    by_arm = defaultdict(list)
    for world in _development_worlds():
        for policy in policies:
            budget = 99.0 if unlimited and policy.__name__ == "orion_with_unlimited_intervention_budget" else 4.0
            session = FrozenWorldSession(world.public, world.protected, budget=budget)
            outcome = policy(session)
            score = score_necessity_world(world, outcome.to_payload())
            rows.append(score.to_payload())
            by_arm[score.arm_id].append(score)
    return rows, {arm: aggregate_necessity_scores(tuple(scores)) for arm, scores in by_arm.items()}


def test_v2_worlds_are_balanced_opaque_and_leak_free() -> None:
    worlds = _development_worlds()
    assert len(worlds) == 160
    assert sum(item.protected.hidden_shift for item in worlds) == 80
    assert sum(item.protected.negative_control for item in worlds) == 80
    assert all(not candidate_view_leaks(item.public) for item in worlds)
    assert len({item.public.task_id for item in worlds}) == len(worlds)
    assert {repair.declared_cost for item in worlds for repair in item.public.repairs} == {1.0}


def test_full_certificate_beats_both_strong_parents_on_development_hidden_shift() -> None:
    rows, summary = _run(RUNNABLE_ARMS)
    full = summary["orion_mutation_necessity"]
    active = summary["active_voi_repair_parent"]
    darc = summary["darc_r2act_dependency_parent"]

    assert full["hidden_shift_protected_root_task_success_rate"] >= 0.95
    assert full["hidden_shift_protected_root_task_success_rate"] - active["hidden_shift_protected_root_task_success_rate"] >= 0.20
    assert full["hidden_shift_protected_root_task_success_rate"] - darc["hidden_shift_protected_root_task_success_rate"] >= 0.20
    assert full["negative_control_unnecessary_high_level_reframe_rate"] == 0.0
    assert full["protected_sibling_regression_rate"] == 0.0
    assert full["forbidden_high_level_mutation_rate"] == 0.0

    result = analyze_necessity_campaign(
        rows,
        full_arm="orion_mutation_necessity",
        h1_parents=("active_voi_repair_parent", "darc_r2act_dependency_parent"),
        control_parent="active_voi_repair_parent",
        parameters={
            "bootstrap_seed": 1701,
            "bootstrap_resamples": 1000,
            "H1_superiority_margin_each_parent": 0.10,
            "H2_control_protected_success_noninferiority_margin": 0.02,
            "total_protected_success_noninferiority_margin": 0.02,
            "cost_noninferiority_margin_units": 1.0,
        },
    )
    assert result["all_support_gates_pass"] is True


def test_registered_ablations_move_the_mechanism_not_just_the_label() -> None:
    _, primary = _run(RUNNABLE_ARMS)
    _, ablations = _run(ABLATION_ARMS, unlimited=True)
    full = primary["orion_mutation_necessity"]

    assert ablations["orion_without_protected_sibling_check"]["hidden_shift_protected_root_task_success_rate"] < full["hidden_shift_protected_root_task_success_rate"]
    assert ablations["orion_without_dependency_impact_binding"]["hidden_shift_protected_root_task_success_rate"] < full["hidden_shift_protected_root_task_success_rate"]
    assert ablations["orion_without_lower_level_exclusion"]["negative_control_unnecessary_high_level_reframe_rate"] > full["negative_control_unnecessary_high_level_reframe_rate"]
    assert ablations["orion_without_KWM_level_ordering"]["negative_control_unnecessary_high_level_reframe_rate"] > full["negative_control_unnecessary_high_level_reframe_rate"]
    assert ablations["orion_with_unlimited_intervention_budget"]["protected_root_task_success_rate"] >= full["protected_root_task_success_rate"]


def test_selected_repair_must_have_been_executed() -> None:
    world = next(item for item in _development_worlds() if item.protected.hidden_shift)
    safe_id = world.protected.gold_minimal_repair_ids[0]
    score = score_necessity_world(
        world,
        {
            "arm_id": "planted_unexecuted_choice",
            "selected_repair_id": safe_id,
            "reopened_ids": list(world.protected.gold_dependency_impact_ids),
            "tested_repair_ids": [],
            "tested_probe_ids": [],
            "spent_budget": 0.0,
        },
    )
    assert score.selected_repair_tested is False
    assert score.protected_root_task_success is False


def test_target_flip_without_protected_sibling_preservation_fails() -> None:
    world = next(
        item
        for item in _development_worlds()
        if item.protected.hidden_shift
        and any(
            response.target_success and not response.protected_sibling_ok
            for _, response in item.protected.response_by_repair
        )
    )
    bad_id = next(
        repair_id
        for repair_id, response in world.protected.response_by_repair
        if response.target_success and not response.protected_sibling_ok
    )
    score = score_necessity_world(
        world,
        {
            "arm_id": "planted_target_flip_only",
            "selected_repair_id": bad_id,
            "reopened_ids": list(world.protected.repair_response(bad_id).observed_invalidated_ids),
            "tested_repair_ids": [bad_id],
            "tested_probe_ids": [],
            "spent_budget": 1.0,
        },
    )
    assert score.target_success is True
    assert score.protected_sibling_regression is True
    assert score.protected_root_task_success is False
