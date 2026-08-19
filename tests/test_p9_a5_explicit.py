from __future__ import annotations

from dataclasses import replace

import pytest

from orion.study.p9.a5_explicit import predict_explicit_gluing, run_a5_explicit
from orion.study.p9.generated_worlds import HostileFamily, generate_pair
from orion.study.p9.m0_tasks import GluingTask, build_task
from orion.study.p9.structural_world import GoldKind, GoldTarget, ViewMode


def _task(seed: str, index: int, mode: ViewMode) -> tuple[object, GluingTask]:
    world = generate_pair(HostileFamily.TRANSPORT_GLUING, seed).worlds[index]
    task = build_task(world, mode=mode, order_seed="unused")
    assert isinstance(task, GluingTask)
    return world, task


def test_a5_typed_missing_values_returns_unknown():
    _, task = _task("a5-missing", 0, ViewMode.TYPED)
    assert predict_explicit_gluing(task) == "UNKNOWN"


def test_a5_current_exact_inverse_glues_and_perturbation_obstructs():
    _, clean = _task("a5-known", 0, ViewMode.CURRENT)
    _, obstructed = _task("a5-known", 1, ViewMode.CURRENT)
    assert predict_explicit_gluing(clean) == "GLUE"
    assert predict_explicit_gluing(obstructed) == "OBSTRUCTION"


def test_a5_prediction_does_not_read_evaluator_gold():
    world, task = _task("a5-gold", 0, ViewMode.CURRENT)
    expected = predict_explicit_gluing(task)
    changed_world = replace(world, gold=GoldTarget(GoldKind.GLUING, "OBSTRUCTION"))
    changed_world.verify()
    changed = build_task(changed_world, mode=ViewMode.CURRENT, order_seed="unused")
    assert isinstance(changed, GluingTask)
    assert predict_explicit_gluing(changed) == expected == "GLUE"
    assert changed.target_label == "OBSTRUCTION"


def test_a5_transport_record_permutation_is_invariant():
    _, task = _task("a5-order", 1, ViewMode.CURRENT)
    context = dict(task.context)
    context["transports"] = list(reversed(context["transports"]))
    changed = replace(task, context=context)
    changed.verify()
    assert predict_explicit_gluing(changed) == predict_explicit_gluing(task)


def test_a5_duplicate_visible_map_fails_closed_unknown():
    _, task = _task("a5-duplicate", 0, ViewMode.CURRENT)
    context = dict(task.context)
    context["transports"] = [*context["transports"], context["transports"][0]]
    changed = replace(task, context=context)
    changed.verify()
    assert predict_explicit_gluing(changed) == "UNKNOWN"


def test_a5_broken_cycle_fails_closed_unknown():
    _, task = _task("a5-cycle", 0, ViewMode.CURRENT)
    context = dict(task.context)
    relations = [list(row) for row in context["relations"]]
    relations = relations[:-1]
    context["relations"] = relations
    changed = replace(task, context=context)
    changed.verify()
    assert predict_explicit_gluing(changed) == "UNKNOWN"


def test_a5_full_small_run_is_deterministic_non_authorizing_and_perfect_when_values_visible():
    first = run_a5_explicit(seed="a5-smoke", transport_pairs=24, subject_sha="smoke")
    replay = run_a5_explicit(seed="a5-smoke", transport_pairs=24, subject_sha="smoke")
    assert first == replay
    assert first["terminal"] == "A5_D0_EXPLICIT_INFERENCE_SUFFICIENT"
    assert first["views"]["TYPED"]["unknown_rate"] == pytest.approx(1.0)
    assert first["views"]["CURRENT"]["accuracy"] == pytest.approx(1.0)
    assert first["views"]["SEMANTIC"]["accuracy"] == pytest.approx(1.0)
    assert first["scientific_authority"] == "NONE_DIAGNOSTIC_ONLY"
    assert first["grants_neural_escalation"] is False
