from __future__ import annotations

import itertools

import pytest

from nq_engine_a.augmentation import (
    AugmentationStatus,
    ConstraintDecision,
    ConstraintProfile,
    canonical_parent,
    evaluate_constraints,
    extension_orbit_representatives,
    extension_orbits,
    generate_canonical_classes,
    has_short_zero_sum,
)
from nq_engine_a.canonical import canonical_multiset
from nq_engine_a.group import GroupSpec, InputError
from nq_engine_a.orderly import generate_canonical_multisets


def brute_gl_matrices(spec: GroupSpec) -> tuple[tuple[tuple[int, ...], ...], ...]:
    matrices = []
    for entries in itertools.product(range(spec.p), repeat=spec.d * spec.d):
        matrix = tuple(
            tuple(entries[row * spec.d + column] for column in range(spec.d))
            for row in range(spec.d)
        )
        if spec.rank(matrix) == spec.d:
            matrices.append(matrix)
    return tuple(matrices)


def brute_stabilizer_orbits(
    spec: GroupSpec, parent: tuple[tuple[int, ...], ...]
) -> tuple[frozenset[tuple[int, ...]], ...]:
    stabilizer = [
        matrix
        for matrix in brute_gl_matrices(spec)
        if tuple(sorted(spec.matvec(matrix, vector) for vector in parent)) == parent
    ]
    unseen = set(spec.elements())
    orbits = []
    while unseen:
        seed = min(unseen)
        orbit = frozenset(spec.matvec(matrix, seed) for matrix in stabilizer)
        orbits.append(orbit)
        unseen -= orbit
    return tuple(sorted(orbits, key=min))


def brute_short_zero_sum(
    spec: GroupSpec, sequence: tuple[tuple[int, ...], ...], cutoff: int
) -> bool:
    for size in range(1, min(cutoff, len(sequence)) + 1):
        for indices in itertools.combinations(range(len(sequence)), size):
            if spec.sum_vectors(sequence[index] for index in indices) == spec.zero:
                return True
    return False


def filtered_raw_records(
    spec: GroupSpec, length: int, profile: ConstraintProfile
) -> tuple[tuple[tuple[int, ...], ...], ...]:
    records = generate_canonical_multisets(spec, length).records
    accepted = []
    for record in records:
        decision = evaluate_constraints(spec, record, profile)
        assert decision is not ConstraintDecision.CANNOT_CHECK_RESOURCE_BOUND
        if decision is ConstraintDecision.ALLOW:
            accepted.append(record)
    return tuple(accepted)


def test_support_basis_stabilizer_orbits_equal_full_gl_reference_on_c2_squared() -> None:
    spec = GroupSpec(2, 2)
    sources = (
        [(1, 0)],
        [(1, 0), (1, 0)],
        [(1, 0), (0, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
    )
    for source in sources:
        parent = canonical_multiset(spec, source)
        observed = extension_orbits(spec, parent)
        expected = brute_stabilizer_orbits(spec, parent)
        assert observed == expected
        assert extension_orbit_representatives(spec, parent) == tuple(map(min, expected))


def test_support_basis_stabilizer_orbits_equal_full_gl_reference_on_c3_squared() -> None:
    spec = GroupSpec(3, 2)
    sources = (
        [(1, 0)],
        [(1, 0), (1, 0), (0, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1), (2, 1)],
    )
    for source in sources:
        parent = canonical_multiset(spec, source)
        observed = extension_orbits(spec, parent)
        expected = brute_stabilizer_orbits(spec, parent)
        assert observed == expected


def test_rank_deficient_parent_has_one_complete_outside_span_orbit() -> None:
    spec = GroupSpec(5, 3)
    parent = canonical_multiset(spec, [(1, 0, 0), (1, 0, 0)])
    orbits = extension_orbits(spec, parent)
    outside = [orbit for orbit in orbits if any(vector[1:] != (0, 0) for vector in orbit)]
    assert len(outside) == 1
    assert len(outside[0]) == spec.order - spec.p
    assert set().union(*map(set, orbits)) == set(spec.elements())
    assert sum(map(len, orbits)) == spec.order


def test_canonical_parent_is_orbit_invariant_and_strictly_shorter() -> None:
    spec = GroupSpec(5, 3)
    sequence = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (2, 3, 4)]
    matrix = ((1, 1, 0), (0, 1, 1), (0, 0, 1))
    transformed = [spec.matvec(matrix, vector) for vector in reversed(sequence)]
    assert canonical_parent(spec, ()) is None
    assert canonical_parent(spec, transformed) == canonical_parent(spec, sequence)
    assert len(canonical_parent(spec, sequence) or ()) == len(sequence) - 1


@pytest.mark.parametrize(
    "p,d,length",
    [(2, 1, 6), (2, 2, 5), (3, 2, 4), (2, 3, 4), (5, 3, 2)],
)
def test_unpruned_augmentation_exactly_equals_complete_raw_generator(
    p: int, d: int, length: int
) -> None:
    spec = GroupSpec(p, d)
    run = generate_canonical_classes(spec, length)
    raw = generate_canonical_multisets(spec, length)
    assert run.coverage.status is AugmentationStatus.COMPLETE
    assert run.records == raw.records
    assert len(run.records) == len(set(run.records))
    assert all(record == canonical_multiset(spec, record) for record in run.records)


@pytest.mark.augmentation_equivalence
def test_largest_tractable_unpruned_panel_c5_squared_length_four_matches_raw() -> None:
    spec = GroupSpec(5, 2)
    run = generate_canonical_classes(spec, 4)
    raw = generate_canonical_multisets(spec, 4)
    assert run.records == raw.records
    assert run.coverage.status is AugmentationStatus.COMPLETE


@pytest.mark.augmentation_equivalence
def test_largest_tractable_ambient_panel_c5_cubed_length_three_matches_raw() -> None:
    spec = GroupSpec(5, 3)
    run = generate_canonical_classes(spec, 3)
    raw = generate_canonical_multisets(spec, 3)
    assert run.records == raw.records
    assert run.coverage.status is AugmentationStatus.COMPLETE
    assert len(run.records) == len(set(run.records))


def test_short_zero_sum_dp_equals_subset_bruteforce_on_complete_small_panel() -> None:
    for spec, max_length, cutoff in (
        (GroupSpec(3, 1), 6, 3),
        (GroupSpec(2, 2), 5, 3),
    ):
        elements = tuple(spec.elements())
        for length in range(max_length + 1):
            for sequence in itertools.combinations_with_replacement(elements, length):
                assert has_short_zero_sum(spec, sequence, cutoff) is brute_short_zero_sum(
                    spec, sequence, cutoff
                )


@pytest.mark.parametrize(
    "spec,length,profile",
    [
        (GroupSpec(3, 2), 5, ConstraintProfile(short_zero_sum_cutoff=2)),
        (GroupSpec(2, 3), 5, ConstraintProfile(forbid_k_disjoint=2)),
        (
            GroupSpec(3, 2),
            5,
            ConstraintProfile(short_zero_sum_cutoff=2, forbid_k_disjoint=2),
        ),
    ],
)
def test_hereditary_pruning_exactly_equals_independently_filtered_raw_records(
    spec: GroupSpec, length: int, profile: ConstraintProfile
) -> None:
    run = generate_canonical_classes(spec, length, profile=profile)
    assert run.coverage.status is AugmentationStatus.COMPLETE
    assert run.records == filtered_raw_records(spec, length, profile)
    assert len(run.records) == len(set(run.records))


def test_every_child_has_declared_parent_and_no_level_contains_duplicate_orbit() -> None:
    spec = GroupSpec(3, 2)
    run = generate_canonical_classes(spec, 5)
    for level_index, level in enumerate(run.levels):
        assert len(level) == len(set(level))
        assert all(record == canonical_multiset(spec, record) for record in level)
        if level_index:
            prior = set(run.levels[level_index - 1])
            assert all(canonical_parent(spec, record) in prior for record in level)


def test_resource_bound_discards_partial_level_and_never_reports_complete() -> None:
    run = generate_canonical_classes(GroupSpec(5, 3), 4, max_candidate_edges=1)
    assert run.coverage.status is AugmentationStatus.CANNOT_CHECK_RESOURCE_BOUND
    assert run.coverage.levels_completed == 0
    assert len(run.levels) == 1
    assert not run.coverage.full_target_coverage
    with pytest.raises(RuntimeError):
        _ = run.records


def test_factorization_resource_bound_propagates_without_negative_promotion() -> None:
    profile = ConstraintProfile(forbid_k_disjoint=3, max_factor_states=1)
    run = generate_canonical_classes(GroupSpec(5, 2), 3, profile=profile)
    assert run.coverage.status is AugmentationStatus.CANNOT_CHECK_RESOURCE_BOUND
    assert not run.coverage.full_target_coverage


def test_hostile_profiles_ranges_and_noncanonical_parents_are_rejected() -> None:
    for kwargs in (
        {"short_zero_sum_cutoff": 0},
        {"forbid_k_disjoint": 0},
        {"max_factor_states": 0},
    ):
        with pytest.raises(InputError):
            ConstraintProfile(**kwargs)
    with pytest.raises(InputError):
        generate_canonical_classes(GroupSpec(2, 2), -1)
    with pytest.raises(InputError):
        generate_canonical_classes(GroupSpec(2, 2), 2, max_candidate_edges=0)
    spec = GroupSpec(3, 2)
    noncanonical = ((1, 0), (0, 1), (2, 0))
    assert noncanonical != canonical_multiset(spec, noncanonical)
    with pytest.raises(InputError):
        extension_orbits(spec, noncanonical)


def test_augmentation_coverage_hook_is_schema_valid_for_complete_and_resource_runs() -> None:
    import json
    from pathlib import Path

    import jsonschema

    schema = json.loads(
        (
            Path(__file__).resolve().parents[1] / "schemas" / "augmentation-coverage.schema.json"
        ).read_text()
    )
    jsonschema.Draft202012Validator.check_schema(schema)
    complete = generate_canonical_classes(GroupSpec(2, 2), 3).coverage.to_dict()
    bounded = generate_canonical_classes(
        GroupSpec(5, 3), 4, max_candidate_edges=1
    ).coverage.to_dict()
    jsonschema.validate(complete, schema)
    jsonschema.validate(bounded, schema)
    assert complete["full_target_coverage"] is True
    assert bounded["status"] == "CANNOT_CHECK_RESOURCE_BOUND"
    assert bounded["full_target_coverage"] is False


def test_frozen_augmentation_control_receipt_is_schema_valid_and_preserves_boundaries() -> None:
    import json
    from pathlib import Path

    import jsonschema

    root = Path(__file__).resolve().parents[1]
    receipt = json.loads((root / "CANONICAL_AUGMENTATION_CONTROLS.json").read_text())
    schema = json.loads(
        (root / "schemas" / "canonical-augmentation-controls.schema.json").read_text()
    )
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(receipt, schema)
    assert receipt["full_census_executed"] is False
    assert receipt["published_full_counts_used_as_acceptance"] is False
    assert receipt["algorithm_terminal"] == ("CANONICAL_AUGMENTATION_SMALL_DOMAIN_EQUIVALENCE_PASS")
    assert receipt["full_execution_terminal"] == "NOT_EXECUTED__CANNOT_CHECK"
    assert receipt["hostile_controls"]["full_gl_stabilizer_orbit_mismatches"] == 0
    assert all(panel["mismatches"] == 0 for panel in receipt["panels"])
    assert all(panel["duplicates_in_output"] == 0 for panel in receipt["panels"])
