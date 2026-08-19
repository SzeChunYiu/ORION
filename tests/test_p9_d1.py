from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.study.p9.d1 import (
    COMPARISON_COORDINATES,
    D1Domain,
    D1Label,
    D1View,
    classify_methods,
)
from orion.study.p9.d1_data_runtime import generate_d1_dataset, mutate_method
from orion.study.p9.d1_runtime import (
    D1FeatureFamily,
    exact_relational_comparator,
    features,
    run_d1,
)


PROTOCOL_V1 = Path("research/extensions/p9-structured-neural/D1_PROTOCOL_V1.json")
PROTOCOL_V11 = Path("research/extensions/p9-structured-neural/D1_PROTOCOL_V1_1.json")
PROTOCOL_V12 = Path("research/extensions/p9-structured-neural/D1_PROTOCOL_V1_2.json")


def test_d1_protocol_and_amendments_are_pre_outcome():
    v1 = json.loads(PROTOCOL_V1.read_text())
    v11 = json.loads(PROTOCOL_V11.read_text())
    v12 = json.loads(PROTOCOL_V12.read_text())
    assert v1["outcome_accessed"] is False
    assert v11["outcome_accessed"] is False
    assert v11["supersedes_for_execution"] == "P9.D1MethodTransferProtocol.v1"
    assert "dependency topology" in v11["reason"]
    assert v12["outcome_accessed"] is False
    assert v12["supersedes_for_execution"] == "P9.D1MethodTransferProtocol.v1.1"
    assert "no semantic mutation" in v12["review_finding"]


def test_d1_dataset_is_deterministic_domain_held_out_and_split_disjoint():
    first = generate_d1_dataset(
        seed="d1-test",
        train_instances_per_base_pair=6,
        dev_instances_per_base_pair=3,
        test_instances_per_base_pair=4,
    )
    replay = generate_d1_dataset(
        seed="d1-test",
        train_instances_per_base_pair=6,
        dev_instances_per_base_pair=3,
        test_instances_per_base_pair=4,
    )
    assert first == replay
    assert {row.domain for row in first.train} == {D1Domain.NUMERICAL, D1Domain.GRAPH}
    assert {row.domain for row in first.dev} == {D1Domain.NUMERICAL, D1Domain.GRAPH}
    assert {row.domain for row in first.test} == {D1Domain.WORKFLOW}
    train_ids = {row.instance_id for row in first.train}
    dev_ids = {row.instance_id for row in first.dev}
    test_ids = {row.instance_id for row in first.test}
    assert not train_ids & dev_ids
    assert not train_ids & test_ids
    assert not dev_ids & test_ids


def test_d1_train_has_single_corruptions_test_has_protected_double_corruptions():
    dataset = generate_d1_dataset(
        seed="d1-double",
        train_instances_per_base_pair=12,
        dev_instances_per_base_pair=4,
        test_instances_per_base_pair=8,
    )
    assert all(len(row.mutation_coordinates) <= 1 for row in (*dataset.train, *dataset.dev))
    assert any(len(row.mutation_coordinates) == 2 for row in dataset.test)


def test_dependency_mutation_is_never_a_semantic_noop():
    dataset = generate_d1_dataset(
        seed="d1-dependency",
        train_instances_per_base_pair=16,
        dev_instances_per_base_pair=2,
        test_instances_per_base_pair=2,
    )
    dependency_rows = [
        row for row in dataset.train if row.mutation_coordinates == ("dependencies",)
    ]
    assert dependency_rows
    for row in dependency_rows:
        assert row.label is D1Label.OBSTRUCTION
        left_topology = row.model_payload(D1View.TYPED)["left"]["dependencies"]
        right_topology = row.model_payload(D1View.TYPED)["right"]["dependencies"]
        assert left_topology != right_topology


def test_d1_exact_labels_include_aligned_obstruction_and_unresolved():
    dataset = generate_d1_dataset(
        seed="d1-labels",
        train_instances_per_base_pair=8,
        dev_instances_per_base_pair=2,
        test_instances_per_base_pair=4,
    )
    assert {row.label for row in dataset.train} == set(D1Label)
    assert {row.label for row in dataset.test} == set(D1Label)
    for row in (*dataset.train, *dataset.dev, *dataset.test):
        assert row.label is classify_methods(row.left, row.right)


def test_unresolved_is_explicit_unknown_not_competing_fabricated_value():
    dataset = generate_d1_dataset(
        seed="d1-unknown",
        train_instances_per_base_pair=3,
        dev_instances_per_base_pair=1,
        test_instances_per_base_pair=2,
    )
    unresolved = next(row for row in dataset.train if row.label is D1Label.UNRESOLVED)
    assert unresolved.right.reconstruction_map is None
    assert "reconstruction_map" in unresolved.right.unknown_coordinates
    assert exact_relational_comparator(unresolved) == D1Label.UNRESOLVED.value


def test_transcript_payload_is_opaque_and_has_no_domain_mutation_or_gold_metadata():
    row = generate_d1_dataset(
        seed="d1-transcript",
        train_instances_per_base_pair=2,
        dev_instances_per_base_pair=1,
        test_instances_per_base_pair=1,
    ).train[0]
    payload = row.model_payload(D1View.TRANSCRIPT)
    serialized = repr(payload).lower()
    for forbidden in (
        row.domain.value.lower(),
        row.label.value.lower(),
        "mutation",
        "split",
        "bisection",
        "threshold_calibration",
        "queue_bfs",
    ):
        assert forbidden not in serialized
    assert all(str(token).startswith("s") for token in payload["left_actions"])


def test_typed_and_serialized_views_carry_same_semantic_value_tokens():
    row = generate_d1_dataset(
        seed="d1-same-info",
        train_instances_per_base_pair=2,
        dev_instances_per_base_pair=1,
        test_instances_per_base_pair=1,
    ).train[0]
    typed = row.model_payload(D1View.TYPED)
    serialized = row.model_payload(D1View.TYPED_SERIALIZED)
    text = "\n".join(serialized["sequence"])
    for coordinate in COMPARISON_COORDINATES:
        assert coordinate in text
    for side in ("left", "right"):
        for coordinate in (
            "preconditions",
            "invariants",
            "effects",
            "failure_modes",
        ):
            for value in typed[side][coordinate]:
                assert str(value) in text


def test_typed_relational_features_are_domain_agnostic_comparison_operators():
    row = generate_d1_dataset(
        seed="d1-relational-features",
        train_instances_per_base_pair=2,
        dev_instances_per_base_pair=1,
        test_instances_per_base_pair=1,
    ).test[0]
    row_features = features(row, D1FeatureFamily.TYPED_RELATIONAL)
    assert not any(row.domain.value in name for name in row_features)
    assert not any(row.instance_id in name for name in row_features)
    assert all(f"{coordinate}:equal" in row_features for coordinate in COMPARISON_COORDINATES)
    assert all(f"{coordinate}:unknown" in row_features for coordinate in COMPARISON_COORDINATES)


def test_exact_typed_relational_comparator_is_perfect_on_whole_domain_and_double_holdout():
    dataset = generate_d1_dataset(
        seed="d1-oracle",
        train_instances_per_base_pair=6,
        dev_instances_per_base_pair=2,
        test_instances_per_base_pair=7,
    )
    predictions = [exact_relational_comparator(row) for row in dataset.test]
    assert predictions == [row.label.value for row in dataset.test]
    double_rows = [row for row in dataset.test if len(row.mutation_coordinates) == 2]
    assert double_rows
    assert all(exact_relational_comparator(row) == D1Label.OBSTRUCTION.value for row in double_rows)


def test_d1_small_smoke_is_deterministic_and_non_authorizing():
    kwargs = dict(
        seed="d1-smoke",
        train_instances_per_base_pair=6,
        dev_instances_per_base_pair=3,
        test_instances_per_base_pair=4,
        subject_sha="smoke",
    )
    first = run_d1(**kwargs)
    replay = run_d1(**kwargs)
    assert first == replay
    assert first["schema"] == "P9.D1MethodTransferResult.v1"
    assert first["protocol"] == "P9.D1MethodTransferProtocol.v1.2"
    assert first["exact_typed_relational_comparator"]["accuracy"] == pytest.approx(1.0)
    assert first["scientific_authority"] == "NONE_UNTIL_INDEPENDENT_VERIFICATION"
    assert first["grants_paper_readiness"] is False
