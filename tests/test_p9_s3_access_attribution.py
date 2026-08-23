from __future__ import annotations

from dataclasses import replace
import inspect

from orion.study.p9.d1 import (
    COMPARISON_COORDINATES,
    D1Label,
    D1View,
    generate_d1_dataset,
)
from orion.study.p9.d1_experiment import exact_relational_comparator
from orion.study.p9.s3_access import (
    serialized_exact_generic_comparator,
    serialized_generic_binding_features,
)


def _sequence(instance) -> list[str]:
    payload = instance.model_payload(D1View.TYPED_SERIALIZED)
    sequence = payload["sequence"]
    assert isinstance(sequence, list)
    return list(map(str, sequence))


def _remint_semantic_values(sequence: list[str], *, one_side_only: bool = False) -> list[str]:
    """Replace scalar/list values while preserving paths and LEN metadata.

    The mapping is deterministic by original value.  When `one_side_only` is
    true, only right-side comparison-coordinate value tokens are reminted.
    Unknown-coordinate names are structural coordinate labels and are preserved.
    """

    out: list[str] = []
    mapping: dict[str, str] = {}
    counter = 0
    for token in sequence:
        if ":LEN=" in token or "=" not in token:
            out.append(token)
            continue
        path, value = token.split("=", 1)
        if ".unknown_coordinates[]" in path or path == "root.schema":
            out.append(token)
            continue
        if not any(f".{coordinate}" in path for coordinate in COMPARISON_COORDINATES):
            out.append(token)
            continue
        if one_side_only and not path.startswith("root.right."):
            out.append(token)
            continue
        if value not in mapping:
            mapping[value] = f"opaque_v_{counter}"
            counter += 1
        out.append(f"{path}={mapping[value]}")
    return out


def _historical_bag_features(sequence: list[str]) -> dict[str, object]:
    features: dict[str, object] = {"sequence_length": len(sequence)}
    for token in sequence:
        features[f"token:{token}"] = 1.0
    return features


def _path(token: str) -> str:
    if ":LEN=" in token:
        return token.split(":LEN=", 1)[0]
    return token.split("=", 1)[0]


def _block_key(token: str) -> str:
    path = _path(token)
    if path == "root.schema":
        return "schema"
    for side in ("left", "right"):
        side_prefix = f"root.{side}."
        if not path.startswith(side_prefix):
            continue
        remainder = path[len(side_prefix) :]
        if remainder.startswith("unknown_coordinates"):
            return f"{side}:unknown_coordinates"
        for coordinate in COMPARISON_COORDINATES:
            if remainder == coordinate or remainder.startswith(f"{coordinate}["):
                return f"{side}:{coordinate}"
    raise AssertionError(f"unclassified serialized token: {token}")


def _reorder_whole_coordinate_blocks(sequence: list[str]) -> list[str]:
    blocks: dict[str, list[str]] = {}
    order: list[str] = []
    for token in sequence:
        key = _block_key(token)
        if key not in blocks:
            blocks[key] = []
            order.append(key)
        blocks[key].append(token)
    out: list[str] = []
    for key in reversed(order):
        out.extend(blocks[key])
    return out


def test_adapter_core_accepts_only_serialized_sequence():
    signature = inspect.signature(serialized_generic_binding_features)
    assert tuple(signature.parameters) == ("sequence",)


def test_whole_coordinate_block_reordering_does_not_change_binding_features():
    dataset = generate_d1_dataset(train_instances_per_base_pair=2, dev_instances_per_base_pair=1, test_instances_per_base_pair=1)
    sequence = _sequence(dataset.train[1])
    reordered = _reorder_whole_coordinate_blocks(sequence)

    assert reordered != sequence
    assert serialized_generic_binding_features(sequence) == serialized_generic_binding_features(reordered)


def test_directed_dependency_child_order_is_semantic_and_changes_equality():
    dataset = generate_d1_dataset(train_instances_per_base_pair=16, dev_instances_per_base_pair=1, test_instances_per_base_pair=1)
    dependency_mutation = next(
        row for row in dataset.train if row.mutation_coordinates == ("dependencies",)
    )
    features = serialized_generic_binding_features(_sequence(dependency_mutation))

    assert features["dependencies:unknown"] is False
    assert features["dependencies:equal"] is False
    assert serialized_exact_generic_comparator(_sequence(dependency_mutation)) == D1Label.OBSTRUCTION.value


def test_consistent_semantic_value_reminting_preserves_generic_equality_features():
    dataset = generate_d1_dataset(train_instances_per_base_pair=2, dev_instances_per_base_pair=1, test_instances_per_base_pair=1)
    aligned = next(row for row in dataset.train if row.label is D1Label.ALIGNED)
    sequence = _sequence(aligned)
    reminted = _remint_semantic_values(sequence)

    assert serialized_generic_binding_features(sequence) == serialized_generic_binding_features(reminted)


def test_one_side_value_reminting_flips_at_least_one_coordinate_equality():
    dataset = generate_d1_dataset(train_instances_per_base_pair=2, dev_instances_per_base_pair=1, test_instances_per_base_pair=1)
    aligned = next(row for row in dataset.train if row.label is D1Label.ALIGNED)
    sequence = _sequence(aligned)
    reminted_right = _remint_semantic_values(sequence, one_side_only=True)

    original = serialized_generic_binding_features(sequence)
    changed = serialized_generic_binding_features(reminted_right)
    assert all(original[f"{coordinate}:equal"] for coordinate in COMPARISON_COORDINATES)
    assert any(not changed[f"{coordinate}:equal"] for coordinate in COMPARISON_COORDINATES)


def test_unknown_coordinate_is_recovered_from_serialization_only():
    dataset = generate_d1_dataset(train_instances_per_base_pair=2, dev_instances_per_base_pair=1, test_instances_per_base_pair=1)
    unresolved = next(row for row in dataset.train if row.label is D1Label.UNRESOLVED)
    features = serialized_generic_binding_features(_sequence(unresolved))

    assert features["reconstruction_map:unknown"] is True
    assert serialized_exact_generic_comparator(_sequence(unresolved)) == D1Label.UNRESOLVED.value


def test_every_gold_coordinate_has_recoverable_left_and_right_serialized_tokens():
    dataset = generate_d1_dataset(train_instances_per_base_pair=2, dev_instances_per_base_pair=1, test_instances_per_base_pair=1)
    sequence = _sequence(dataset.train[0])
    for coordinate in COMPARISON_COORDINATES:
        assert any(token.startswith(f"root.left.{coordinate}") for token in sequence), coordinate
        assert any(token.startswith(f"root.right.{coordinate}") for token in sequence), coordinate


def test_serialized_exact_comparator_matches_historical_exact_comparator_on_train_and_dev_only():
    dataset = generate_d1_dataset(
        seed="p9-d1-method-transfer-v1",
        train_instances_per_base_pair=48,
        dev_instances_per_base_pair=16,
        test_instances_per_base_pair=32,
    )
    # Deliberately no dataset.test access in this pre-protected hostile test.
    for row in (*dataset.train, *dataset.dev):
        assert serialized_exact_generic_comparator(_sequence(row)) == exact_relational_comparator(row)


def test_binding_features_do_not_depend_on_instance_label_or_mutation_metadata():
    dataset = generate_d1_dataset(train_instances_per_base_pair=2, dev_instances_per_base_pair=1, test_instances_per_base_pair=1)
    row = dataset.train[1]
    sequence = _sequence(row)
    expected = serialized_generic_binding_features(sequence)
    corrupted_metadata = replace(
        row,
        label=D1Label.ALIGNED if row.label is not D1Label.ALIGNED else D1Label.OBSTRUCTION,
        mutation_coordinates=("not_a_real_coordinate",),
    )
    # The adapter receives the already-projected serialized sequence, so evaluator
    # metadata mutation cannot change it or the resulting generic features.
    assert serialized_generic_binding_features(sequence) == expected
    assert corrupted_metadata.label != row.label or corrupted_metadata.mutation_coordinates != row.mutation_coordinates


def test_generic_comparison_is_value_remint_invariant_while_historical_bag_is_not():
    """V1.1 correction: diagnose inductive/access bias, not information loss."""

    dataset = generate_d1_dataset(train_instances_per_base_pair=2, dev_instances_per_base_pair=2, test_instances_per_base_pair=1)
    aligned = next(row for row in dataset.dev if row.label is D1Label.ALIGNED)
    sequence = _sequence(aligned)
    reminted = _remint_semantic_values(sequence)

    assert _historical_bag_features(sequence) != _historical_bag_features(reminted)
    assert serialized_generic_binding_features(sequence) == serialized_generic_binding_features(reminted)
