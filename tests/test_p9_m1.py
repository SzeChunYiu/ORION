from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.study.p9.generated_worlds import HostileFamily, generate_corpus, generate_pair
from orion.study.p9.m0_tasks import GluingTask, MechanicRankingTask, build_task
from orion.study.p9.m1_runtime import frozen_model_specs, run_m1
from orion.study.p9.m1_features import (
    FeatureFamily,
    gluing_features,
    is_opaque_identity,
    mechanic_features,
    opaque_feature_names,
)
from orion.study.p9.structural_world import ViewMode


PROTOCOL = Path("research/extensions/p9-structured-neural/M1_PROTOCOL_V1.json")
PROTOCOL_V11 = Path("research/extensions/p9-structured-neural/M1_PROTOCOL_V1_1.json")


def test_m1_protocol_is_pre_outcome_and_binds_current_m0():
    protocol = json.loads(PROTOCOL.read_text())
    amendment = json.loads(PROTOCOL_V11.read_text())
    assert protocol["schema"] == "P9.M1Protocol.v1"
    assert protocol["outcome_accessed"] is False
    assert protocol["dependencies"]["m0_merge"] == "077ecdc4e7905f5d9791cb9a57825417acddf4f4"
    assert protocol["corpus"]["test_pairs_per_family"] == 48
    assert protocol["selection"]["test_passes_per_selected_configuration"] == 1
    assert protocol["authority"]["model_promotion_authority"] is False
    assert amendment["schema"] == "P9.M1Protocol.v1.1"
    assert amendment["outcome_accessed"] is False
    assert amendment["supersedes_for_execution"] == "P9.M1Protocol.v1"
    assert amendment["diagnostic_curve_rule"]["protected_test_effect"] == "NONE"


def test_frozen_model_grid_matches_protocol_count_and_is_deterministic():
    specs = frozen_model_specs()
    assert len(specs) == 12
    assert specs == frozen_model_specs()
    assert len({spec.config_id for spec in specs}) == len(specs)


def test_generic_features_never_emit_raw_opaque_identity_in_feature_name():
    pair = generate_pair(HostileFamily.RELATION_SEMANTICS, "m1-no-id-leak")
    for mode in ViewMode:
        task = build_task(pair.worlds[0], mode=mode, order_seed="order")
        assert isinstance(task, MechanicRankingTask)
        for candidate in task.candidates:
            for family in (FeatureFamily.F0_FIELD_BAG, FeatureFamily.F1_PAIRWISE):
                row = mechanic_features(task, candidate, family)
                assert opaque_feature_names(row) == ()
                assert not any(candidate.candidate_id in name for name in row)


def test_pairwise_history_equality_uses_relation_not_raw_id():
    world = generate_pair(HostileFamily.FAILURE_HISTORY, "m1-history-equality").worlds[1]
    task = build_task(world, mode=ViewMode.SEMANTIC, order_seed="order")
    assert isinstance(task, MechanicRankingTask)
    failed_id = world.history[0].mechanic_id
    failed = next(candidate for candidate in task.candidates if candidate.candidate_id == failed_id)
    other = next(candidate for candidate in task.candidates if candidate.candidate_id != failed_id)

    failed_features = mechanic_features(task, failed, FeatureFamily.F1_PAIRWISE)
    other_features = mechanic_features(task, other, FeatureFamily.F1_PAIRWISE)
    assert failed_features["eq:candidate_id_occurs_in_context"] == 1.0
    assert other_features["eq:candidate_id_occurs_in_context"] == 0.0
    assert not any(failed_id in name for name in failed_features)


def test_weaker_history_view_has_no_candidate_history_equality_signal():
    world = generate_pair(HostileFamily.FAILURE_HISTORY, "m1-history-hidden").worlds[1]
    task = build_task(world, mode=ViewMode.CURRENT, order_seed="order")
    assert isinstance(task, MechanicRankingTask)
    for candidate in task.candidates:
        row = mechanic_features(task, candidate, FeatureFamily.F1_PAIRWISE)
        assert row["eq:candidate_id_occurs_in_context"] == 0.0


def test_cycle_features_expose_raw_visible_values_not_hand_composed_residual():
    world = generate_pair(HostileFamily.TRANSPORT_GLUING, "m1-cycle").worlds[0]
    task = build_task(world, mode=ViewMode.CURRENT, order_seed="ignored")
    assert isinstance(task, GluingTask)
    row = gluing_features(task, FeatureFamily.F2_CYCLE_NUMERIC)
    cycle_names = sorted(name for name in row if name.startswith("cycle:"))
    assert cycle_names == [
        "cycle:0:offset",
        "cycle:0:scale",
        "cycle:1:offset",
        "cycle:1:scale",
        "cycle:2:offset",
        "cycle:2:scale",
    ]
    forbidden = ("residual", "product", "composed", "identity_error")
    assert not any(any(word in name for word in forbidden) for name in row)


def test_cycle_feature_rejected_before_transport_values_are_visible():
    world = generate_pair(HostileFamily.TRANSPORT_GLUING, "m1-cycle-hidden").worlds[0]
    task = build_task(world, mode=ViewMode.TYPED, order_seed="ignored")
    assert isinstance(task, GluingTask)
    with pytest.raises(ValueError, match="CURRENT or SEMANTIC"):
        gluing_features(task, FeatureFamily.F2_CYCLE_NUMERIC)


def test_opaque_identity_detector_matches_generated_ids_but_not_structural_vocabulary():
    pair = generate_pair(HostileFamily.RELATION_SEMANTICS, "m1-opaque")
    assert is_opaque_identity(pair.worlds[0].atoms[0].atom_id)
    assert not is_opaque_identity("SUPPORTS")
    assert not is_opaque_identity("ASSIMILATE_EVIDENCE")


def test_m1_small_smoke_is_deterministic_non_authorizing_and_ceiling_safe():
    kwargs = dict(
        corpus_seed="p9-m1-smoke",
        train_pairs_per_family=8,
        dev_pairs_per_family=3,
        test_pairs_per_family=4,
        train_size_pairs_per_family=(2, 4, 6),
        train_order_seed="smoke-train",
        dev_order_seed="smoke-dev",
        test_order_seed="smoke-test",
        alternate_test_order_seed="smoke-test-alt",
        subject_sha="smoke",
    )
    first = run_m1(**kwargs)
    replay = run_m1(**kwargs)
    assert first == replay
    assert first["schema"] == "P9.M1Result.v1"
    assert first["scientific_authority"] == "NONE_DIAGNOSTIC_ONLY"
    assert first["grants_model_promotion"] is False
    for view in first["views"].values():
        assert view["test_overall"]["ceiling_violation"] is False
        for task in view["tasks"].values():
            assert task["test_row_permutation_invariance"]["invariant"] is True
            curve = task["train_size_curve_dev"]
            assert curve
            assert all(point["status"] in {"EVALUATED", "CONFIG_NOT_FIT_AT_SIZE"} for point in curve)
            if "candidate_order_invariance_test" in task:
                assert task["candidate_order_invariance_test"]["invariant"] is True


def test_generated_corpus_for_protocol_remains_split_disjoint():
    corpus = generate_corpus(
        seed="p9-m1-classical-v1",
        train_pairs_per_family=64,
        dev_pairs_per_family=24,
        test_pairs_per_family=48,
    )
    corpus.verify()
    train_ids = set(corpus.train.identity_tokens)
    dev_ids = set(corpus.dev.identity_tokens)
    test_ids = set(corpus.test.identity_tokens)
    assert not train_ids & dev_ids
    assert not train_ids & test_ids
    assert not dev_ids & test_ids
