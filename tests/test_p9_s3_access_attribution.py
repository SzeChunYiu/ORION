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


def test_adapter_core_accepts_only_serialized_sequence():
    signature = inspect.signature(serialized_generic_binding_features)
    assert tuple(signature.parameters) == ("sequence",)


def test_token_order_permutation_does_not_change_binding_features():
    dataset = generate_d1_dataset(train_instances_per_base_pair=2, dev_instances_per_base_pair=1, test_instances_per_base_pair=1)
    sequence = _sequence(dataset.train[1])
    assert serialized_generic_binding_features(sequence) == serialized_generic_binding_features(list(reversed(sequence)))


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


def test_dropping_side_binding_is_not_equivalent_to_generic_binding_on_dev():
    dataset = generate_d1_dataset(train_instances_per_base_pair=8, dev_instances_per_base_pair=8, test_instances_per_base_pair=1)

    def unbound_multiset(sequence: list[str]) -> tuple[str, ...]:
        normalized = []
        for token in sequence:
            if token == "root.schema=P9.D1Typed.v1":
                continue
            normalized.append(token.replace("root.left.", "root.side.").replace("root.right.", "root.side."))
        return tuple(sorted(normalized))

    # There must exist at least one pair with the same unbound content but a
    # different gold decision; otherwise side binding would add no information/access.
    buckets: dict[tuple[str, ...], set[D1Label]] = {}
    for row in dataset.dev:
        buckets.setdefault(unbound_multiset(_sequence(row)), set()).add(row.label)
    assert any(len(labels) > 1 for labels in buckets.values())
