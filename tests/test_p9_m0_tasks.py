from dataclasses import replace

import pytest

from orion.study.p9.generated_worlds import HostileFamily, generate_pair
from orion.study.p9.m0_tasks import (
    GluingTask,
    MechanicRankingTask,
    TaskKind,
    build_task,
)
from orion.study.p9.structural_world import GoldKind, GoldTarget, ViewMode


@pytest.mark.parametrize("mode", list(ViewMode))
def test_task_model_payload_excludes_evaluator_metadata(mode):
    pair = generate_pair(HostileFamily.RELATION_SEMANTICS, "task-metadata")
    task = build_task(pair.worlds[0], mode=mode, order_seed="order-a")

    serialized = repr(task.model_payload()).lower()
    for forbidden in (
        "gold",
        "pair_id",
        "hostile_family",
        "generator_seed",
        "split_namespace",
        "row_index",
        "task-metadata",
    ):
        assert forbidden not in serialized
    assert task.task_id not in serialized


def test_mechanic_task_candidates_are_current_world_mechanics_only():
    pair = generate_pair(HostileFamily.RELATION_SEMANTICS, "candidate-set")
    world = pair.worlds[0]
    task = build_task(world, mode=ViewMode.SEMANTIC, order_seed="order-a")

    assert isinstance(task, MechanicRankingTask)
    assert task.kind is TaskKind.MECHANIC_RANKING
    assert {candidate.candidate_id for candidate in task.candidates} == {
        mechanic.mechanic_id for mechanic in world.mechanics
    }
    assert task.target_candidate_id == world.gold.value


def test_candidate_order_permutation_changes_order_not_target_identity_or_candidate_payload_set():
    world = generate_pair(HostileFamily.FAILURE_HISTORY, "candidate-order").worlds[1]
    first = build_task(world, mode=ViewMode.SEMANTIC, order_seed="p9-m0-order-a")
    second = build_task(world, mode=ViewMode.SEMANTIC, order_seed="p9-m0-order-b")

    assert isinstance(first, MechanicRankingTask)
    assert isinstance(second, MechanicRankingTask)
    assert first.target_candidate_id == second.target_candidate_id == world.gold.value
    assert {repr(candidate.payload) for candidate in first.candidates} == {
        repr(candidate.payload) for candidate in second.candidates
    }
    assert first.model_payload() != second.model_payload()


def test_weaker_candidate_views_do_not_smuggle_typed_contracts():
    world = generate_pair(HostileFamily.RELATION_SEMANTICS, "candidate-fields").worlds[0]

    surface = build_task(world, mode=ViewMode.SURFACE, order_seed="o")
    topology = build_task(world, mode=ViewMode.TOPOLOGY, order_seed="o")
    typed = build_task(world, mode=ViewMode.TYPED, order_seed="o")

    assert isinstance(surface, MechanicRankingTask)
    assert isinstance(topology, MechanicRankingTask)
    assert isinstance(typed, MechanicRankingTask)

    for candidate in surface.candidates:
        assert set(candidate.payload) == {"candidate_id", "surface_label"}
    for candidate in topology.candidates:
        assert set(candidate.payload) == {
            "candidate_id",
            "read_atom_ids",
            "write_atom_ids",
        }
    for candidate in typed.candidates:
        assert {
            "preconditions",
            "effects",
            "failure_modes",
            "cost",
        } <= set(candidate.payload)


def test_history_is_visible_only_in_semantic_context():
    world = generate_pair(HostileFamily.FAILURE_HISTORY, "history-visibility").worlds[1]

    for mode in (ViewMode.SURFACE, ViewMode.TOPOLOGY, ViewMode.TYPED, ViewMode.CURRENT):
        task = build_task(world, mode=mode, order_seed="o")
        assert "history" not in repr(task.context).lower()

    semantic = build_task(world, mode=ViewMode.SEMANTIC, order_seed="o")
    assert "history" in semantic.context


def test_transport_values_are_absent_until_current_view():
    world = generate_pair(HostileFamily.TRANSPORT_GLUING, "transport-visibility").worlds[0]

    for mode in (ViewMode.SURFACE, ViewMode.TOPOLOGY, ViewMode.TYPED):
        task = build_task(world, mode=mode, order_seed="o")
        assert isinstance(task, GluingTask)
        assert "transports" not in task.context

    current = build_task(world, mode=ViewMode.CURRENT, order_seed="o")
    assert "transports" in current.context


def test_gluing_task_has_fixed_vocabulary_and_no_candidate_list():
    world = generate_pair(HostileFamily.TRANSPORT_GLUING, "gluing-task").worlds[0]
    task = build_task(world, mode=ViewMode.CURRENT, order_seed="ignored")

    assert isinstance(task, GluingTask)
    assert task.kind is TaskKind.GLUING
    assert task.target_label == world.gold.value
    assert task.allowed_labels == ("GLUE", "OBSTRUCTION", "UNKNOWN")
    assert "candidates" not in task.model_payload()


def test_task_target_is_evaluator_only_and_changing_gold_does_not_change_model_payload():
    world = generate_pair(HostileFamily.RELATION_SEMANTICS, "gold-separation").worlds[0]
    original = build_task(world, mode=ViewMode.TYPED, order_seed="o")
    alternate_id = next(
        mechanic.mechanic_id for mechanic in world.mechanics if mechanic.mechanic_id != world.gold.value
    )
    changed_world = replace(
        world,
        gold=GoldTarget(GoldKind.MECHANIC_SELECTION, alternate_id),
    )
    changed_world.verify()
    changed = build_task(changed_world, mode=ViewMode.TYPED, order_seed="o")

    assert original.model_payload() == changed.model_payload()
    assert original.target_candidate_id != changed.target_candidate_id


def test_build_task_rejects_empty_order_seed_for_mechanic_ranking():
    world = generate_pair(HostileFamily.RELATION_SEMANTICS, "missing-order-seed").worlds[0]
    with pytest.raises(ValueError, match="order seed"):
        build_task(world, mode=ViewMode.TYPED, order_seed="")
