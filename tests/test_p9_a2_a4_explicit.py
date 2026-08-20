from __future__ import annotations

from dataclasses import replace

import pytest

from orion.study.p9.a2_a4_explicit import AMBIGUOUS, predict_history_explicit, predict_relation_explicit, run_a2_a4_explicit
from orion.study.p9.generated_worlds import HostileFamily, generate_pair
from orion.study.p9.m0_tasks import MechanicRankingTask, build_task
from orion.study.p9.structural_world import GoldKind, GoldTarget, ViewMode


def test_relation_selector_is_ambiguous_without_typed_relation_and_effects():
    world = generate_pair(HostileFamily.RELATION_SEMANTICS, "a2-weak").worlds[0]
    for mode in (ViewMode.SURFACE, ViewMode.TOPOLOGY):
        task = build_task(world, mode=mode, order_seed="o")
        assert isinstance(task, MechanicRankingTask)
        assert predict_relation_explicit(task) == AMBIGUOUS


def test_relation_selector_is_exact_at_typed_and_invariant_to_candidate_order():
    pair = generate_pair(HostileFamily.RELATION_SEMANTICS, "a2-typed")
    for world in pair.worlds:
        first = build_task(world, mode=ViewMode.TYPED, order_seed="o1")
        second = build_task(world, mode=ViewMode.TYPED, order_seed="o2")
        assert isinstance(first, MechanicRankingTask) and isinstance(second, MechanicRankingTask)
        assert predict_relation_explicit(first) == world.gold.value
        assert predict_relation_explicit(second) == world.gold.value


def test_relation_selector_does_not_read_gold():
    world = generate_pair(HostileFamily.RELATION_SEMANTICS, "a2-gold").worlds[0]
    task = build_task(world, mode=ViewMode.TYPED, order_seed="o")
    assert isinstance(task, MechanicRankingTask)
    expected = predict_relation_explicit(task)
    other = next(m.mechanic_id for m in world.mechanics if m.mechanic_id != world.gold.value)
    changed_world = replace(world, gold=GoldTarget(GoldKind.MECHANIC_SELECTION, other)); changed_world.verify()
    changed = build_task(changed_world, mode=ViewMode.TYPED, order_seed="o")
    assert isinstance(changed, MechanicRankingTask)
    assert predict_relation_explicit(changed) == expected
    assert expected != changed.target_candidate_id


def test_history_selector_uses_admitted_failure_only_when_visible():
    clean, negative = generate_pair(HostileFamily.FAILURE_HISTORY, "a4-history").worlds
    clean_semantic = build_task(clean, mode=ViewMode.SEMANTIC, order_seed="o")
    negative_semantic = build_task(negative, mode=ViewMode.SEMANTIC, order_seed="o")
    assert isinstance(clean_semantic, MechanicRankingTask) and isinstance(negative_semantic, MechanicRankingTask)
    assert predict_history_explicit(clean_semantic) == clean.gold.value
    assert predict_history_explicit(negative_semantic) == negative.gold.value
    clean_current = build_task(clean, mode=ViewMode.CURRENT, order_seed="o")
    negative_current = build_task(negative, mode=ViewMode.CURRENT, order_seed="o")
    assert isinstance(clean_current, MechanicRankingTask) and isinstance(negative_current, MechanicRankingTask)
    assert clean_current.model_payload() == negative_current.model_payload()
    assert predict_history_explicit(clean_current) == predict_history_explicit(negative_current)


def test_history_selector_is_candidate_order_invariant_at_semantic():
    world = generate_pair(HostileFamily.FAILURE_HISTORY, "a4-order").worlds[1]
    first = build_task(world, mode=ViewMode.SEMANTIC, order_seed="o1")
    second = build_task(world, mode=ViewMode.SEMANTIC, order_seed="o2")
    assert isinstance(first, MechanicRankingTask) and isinstance(second, MechanicRankingTask)
    assert predict_history_explicit(first) == predict_history_explicit(second) == world.gold.value


def test_full_a2_a4_small_run_is_deterministic_and_bounded():
    first = run_a2_a4_explicit(seed="a2-a4-smoke", relation_pairs=24, history_pairs=24, subject_sha="smoke")
    replay = run_a2_a4_explicit(seed="a2-a4-smoke", relation_pairs=24, history_pairs=24, subject_sha="smoke")
    assert first == replay
    assert first["terminal"] == "A2_A4_D0_EXPLICIT_INFERENCE_SUFFICIENT"
    assert first["relation_views"]["SURFACE"]["coverage"] == pytest.approx(0.0)
    assert first["relation_views"]["TYPED"]["full_task_accuracy"] == pytest.approx(1.0)
    assert first["history_views"]["SEMANTIC"]["full_task_accuracy"] == pytest.approx(1.0)
    assert first["history_views"]["CURRENT"]["hidden_view_pair_prediction_equal"] is True
    assert first["scientific_authority"] == "NONE_DIAGNOSTIC_ONLY"
    assert first["grants_neural_escalation"] is False
