from dataclasses import replace

import pytest

from orion.study.p9.generated_worlds import (
    CorpusSplit,
    HostileFamily,
    generate_balanced_split,
    generate_corpus,
    generate_pair,
)
from orion.study.p9.m0 import (
    M0Baseline,
    evaluate_prediction,
    exact_semantic_oracle,
    predict_null,
    run_m0_harness,
)
from orion.study.p9.m0_tasks import GluingTask, MechanicRankingTask, build_task
from orion.study.p9.structural_world import GoldKind, GoldTarget, ViewMode


@pytest.mark.parametrize("family", list(HostileFamily))
def test_exact_oracle_reaches_correct_identity_without_reading_gold(family):
    pair = generate_pair(family, "oracle-world")
    for world in pair.worlds:
        task = build_task(world, mode=ViewMode.SEMANTIC, order_seed="p9-m0-order-a")
        prediction = exact_semantic_oracle(world, task)
        assert evaluate_prediction(task, prediction) is True


def test_exact_mechanic_oracle_is_invariant_to_falsified_evaluator_gold():
    world = generate_pair(HostileFamily.RELATION_SEMANTICS, "oracle-no-gold").worlds[0]
    task = build_task(world, mode=ViewMode.SEMANTIC, order_seed="o")
    assert isinstance(task, MechanicRankingTask)
    expected = exact_semantic_oracle(world, task)

    other_id = next(
        mechanic.mechanic_id for mechanic in world.mechanics if mechanic.mechanic_id != world.gold.value
    )
    falsified_world = replace(
        world,
        gold=GoldTarget(GoldKind.MECHANIC_SELECTION, other_id),
    )
    falsified_world.verify()
    falsified_task = build_task(falsified_world, mode=ViewMode.SEMANTIC, order_seed="o")

    assert exact_semantic_oracle(falsified_world, falsified_task) == expected
    assert evaluate_prediction(falsified_task, expected) is False


def test_exact_gluing_oracle_is_invariant_to_falsified_evaluator_gold():
    world = generate_pair(HostileFamily.TRANSPORT_GLUING, "oracle-glue-no-gold").worlds[0]
    task = build_task(world, mode=ViewMode.SEMANTIC, order_seed="ignored")
    assert isinstance(task, GluingTask)
    expected = exact_semantic_oracle(world, task)

    falsified_world = replace(
        world,
        gold=GoldTarget(GoldKind.GLUING, "OBSTRUCTION"),
    )
    falsified_world.verify()
    falsified_task = build_task(falsified_world, mode=ViewMode.SEMANTIC, order_seed="ignored")

    assert exact_semantic_oracle(falsified_world, falsified_task) == expected == "GLUE"
    assert evaluate_prediction(falsified_task, expected) is False


def test_oracle_mechanic_identity_survives_candidate_permutation():
    world = generate_pair(HostileFamily.FAILURE_HISTORY, "oracle-order").worlds[1]
    first = build_task(world, mode=ViewMode.SEMANTIC, order_seed="p9-m0-order-a")
    second = build_task(world, mode=ViewMode.SEMANTIC, order_seed="p9-m0-order-b")

    assert exact_semantic_oracle(world, first) == exact_semantic_oracle(world, second)


@pytest.mark.parametrize(
    "baseline",
    [
        M0Baseline.FIRST_CANDIDATE,
        M0Baseline.LAST_CANDIDATE,
        M0Baseline.LEXICOGRAPHIC_ID,
        M0Baseline.HASH_PARITY,
    ],
)
def test_candidate_null_baselines_are_deterministic_and_return_current_candidate(baseline):
    world = generate_pair(HostileFamily.RELATION_SEMANTICS, "null-candidate").worlds[0]
    task = build_task(world, mode=ViewMode.SURFACE, order_seed="o")
    assert isinstance(task, MechanicRankingTask)

    first = predict_null(task, baseline)
    second = predict_null(task, baseline)
    assert first == second
    assert first in {candidate.candidate_id for candidate in task.candidates}


@pytest.mark.parametrize(
    ("baseline", "expected"),
    [
        (M0Baseline.ALWAYS_GLUE, "GLUE"),
        (M0Baseline.ALWAYS_OBSTRUCTION, "OBSTRUCTION"),
        (M0Baseline.ALWAYS_UNKNOWN, "UNKNOWN"),
    ],
)
def test_gluing_null_baselines_are_fixed_and_valid(baseline, expected):
    world = generate_pair(HostileFamily.TRANSPORT_GLUING, "null-gluing").worlds[0]
    task = build_task(world, mode=ViewMode.SURFACE, order_seed="ignored")
    assert isinstance(task, GluingTask)

    assert predict_null(task, baseline) == expected


def test_inapplicable_null_baseline_is_rejected():
    mechanic_world = generate_pair(HostileFamily.RELATION_SEMANTICS, "null-wrong-task").worlds[0]
    gluing_world = generate_pair(HostileFamily.TRANSPORT_GLUING, "null-wrong-task").worlds[0]
    mechanic_task = build_task(mechanic_world, mode=ViewMode.SURFACE, order_seed="o")
    gluing_task = build_task(gluing_world, mode=ViewMode.SURFACE, order_seed="o")

    with pytest.raises(ValueError, match="not applicable"):
        predict_null(mechanic_task, M0Baseline.ALWAYS_GLUE)
    with pytest.raises(ValueError, match="not applicable"):
        predict_null(gluing_task, M0Baseline.FIRST_CANDIDATE)


def test_evaluator_rejects_invalid_candidate_and_gluing_predictions():
    mechanic_world = generate_pair(HostileFamily.RELATION_SEMANTICS, "invalid-prediction").worlds[0]
    gluing_world = generate_pair(HostileFamily.TRANSPORT_GLUING, "invalid-prediction").worlds[0]
    mechanic_task = build_task(mechanic_world, mode=ViewMode.SEMANTIC, order_seed="o")
    gluing_task = build_task(gluing_world, mode=ViewMode.SEMANTIC, order_seed="o")

    with pytest.raises(ValueError, match="unknown candidate"):
        evaluate_prediction(mechanic_task, "not-a-candidate")
    with pytest.raises(ValueError, match="invalid gluing prediction"):
        evaluate_prediction(gluing_task, "MAYBE")


def test_m0_harness_replays_and_oracle_is_perfect_on_frozen_protocol_corpus():
    corpus = generate_corpus(
        seed="p9-m0-task-harness-v0",
        train_pairs_per_family=32,
        dev_pairs_per_family=8,
        test_pairs_per_family=16,
    )
    first = run_m0_harness(
        corpus=corpus,
        mode=ViewMode.SEMANTIC,
        order_seed="p9-m0-order-a",
    )
    replay = run_m0_harness(
        corpus=corpus,
        mode=ViewMode.SEMANTIC,
        order_seed="p9-m0-order-a",
    )

    assert first == replay
    assert first["schema"] == "P9.M0HarnessResult.v0"
    assert first["authority"] == "NO_SCIENTIFIC_AUTHORITY"
    assert first["test"]["oracle"]["accuracy"] == pytest.approx(1.0)
    assert first["test"]["oracle"]["invalid_prediction_count"] == 0


def test_m0_harness_reports_view_ceiling_and_never_promotes_nulls():
    split = generate_balanced_split(
        seed="p9-m0-task-harness-v0",
        split=CorpusSplit.TEST,
        pairs_per_family=16,
    )
    corpus = generate_corpus(
        seed="p9-m0-task-harness-v0",
        train_pairs_per_family=32,
        dev_pairs_per_family=8,
        test_pairs_per_family=16,
    )
    result = run_m0_harness(
        corpus=corpus,
        mode=ViewMode.TYPED,
        order_seed="p9-m0-order-a",
    )

    assert result["test"]["view_deterministic_accuracy_ceiling"] == pytest.approx(2 / 3)
    assert result["test"]["world_count"] == len(split.worlds)
    assert result["terminal"] == "M0_TASK_HARNESS_VALIDATED_ONLY"
    assert result["grants_model_promotion"] is False
