from __future__ import annotations

import itertools

import pytest

from nq_engine_a.canonical import canonical_multiset
from nq_engine_a.group import GroupSpec, InputError


def test_group_encoding_covers_every_element_once() -> None:
    spec = GroupSpec(5, 3)
    elements = tuple(spec.elements())
    assert len(elements) == 125
    assert len(set(elements)) == 125
    assert [spec.encode(v) for v in elements] == list(range(125))
    assert all(spec.decode(spec.encode(v)) == v for v in elements)


def test_group_addition_and_sum_are_coordinatewise_mod_p() -> None:
    spec = GroupSpec(5, 3)
    assert spec.add((4, 3, 2), (2, 4, 3)) == (1, 2, 0)
    assert spec.sum_vectors([(4, 3, 2), (2, 4, 3), (4, 3, 0)]) == (0, 0, 0)


@pytest.mark.parametrize("p,d", [(1, 1), (4, 1), (5, 0), (True, 2)])
def test_group_spec_rejects_nonprime_or_malformed_parameters(p: object, d: object) -> None:
    with pytest.raises(InputError):
        GroupSpec(p, d)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "vector",
    [(), (0,), (0, 0, 5), (0, -1, 0), (0, 1.0, 0), "010"],
)
def test_group_rejects_hostile_vectors(vector: object) -> None:
    spec = GroupSpec(5, 3)
    with pytest.raises(InputError):
        spec.validate_vector(vector)


def test_rank_is_exact_over_the_declared_field() -> None:
    spec = GroupSpec(5, 3)
    assert spec.rank([]) == 0
    assert spec.rank([(1, 0, 0), (2, 0, 0), (0, 1, 0)]) == 2
    assert spec.rank([(1, 0, 0), (0, 1, 0), (0, 0, 1)]) == 3


def test_canonical_multiset_is_permutation_invariant_and_idempotent() -> None:
    spec = GroupSpec(5, 3)
    sequence = [(1, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)]
    canonical = canonical_multiset(spec, sequence)
    for perm in itertools.permutations(sequence):
        assert canonical_multiset(spec, perm) == canonical
    assert canonical_multiset(spec, canonical) == canonical


def test_canonical_multiset_is_invariant_under_invertible_linear_map() -> None:
    spec = GroupSpec(5, 3)
    sequence = [(1, 0, 0), (0, 1, 0), (1, 1, 1), (2, 3, 4), (0, 0, 0)]
    matrix = ((1, 1, 0), (0, 1, 1), (0, 0, 1))
    transformed = [spec.matvec(matrix, vector) for vector in sequence]
    assert canonical_multiset(spec, transformed) == canonical_multiset(spec, sequence)


def test_canonical_multiset_preserves_multiplicity_and_rank() -> None:
    spec = GroupSpec(3, 2)
    sequence = [(1, 0), (1, 0), (0, 1), (0, 0)]
    canonical = canonical_multiset(spec, sequence)
    assert len(canonical) == len(sequence)
    assert canonical.count((0, 0)) == 1
    assert spec.rank(canonical) == spec.rank(sequence)


def test_json_array_vectors_are_normalized_to_tuples() -> None:
    spec = GroupSpec(5, 3)
    assert spec.validate_vector([0, 1, 4]) == (0, 1, 4)
    assert spec.validate_sequence([[0, 1, 4], [1, 0, 0]]) == ((0, 1, 4), (1, 0, 0))


def test_additional_hostile_group_operations_fail_closed() -> None:
    spec = GroupSpec(3, 2)
    for encoded in (-1, spec.order, True, 1.5):
        with pytest.raises(InputError):
            spec.decode(encoded)
    for scalar in (True, 1.5):
        with pytest.raises(InputError):
            spec.scalar_mul(scalar, (1, 0))  # type: ignore[arg-type]
    assert spec.scalar_mul(4, (2, 1)) == (2, 1)
    for matrix in (None, ((1, 0),), ((1,), (0,)), ((1, 0), (0, 1.5))):
        with pytest.raises(InputError):
            spec.matvec(matrix, (1, 0))


def test_coordinate_solver_rejects_nonbasis_and_out_of_span_inputs() -> None:
    spec = GroupSpec(3, 2)
    assert spec.coordinates_in_basis((0, 0), ()) == ()
    with pytest.raises(InputError):
        spec.coordinates_in_basis((1, 0), ())
    with pytest.raises(InputError):
        spec.coordinates_in_basis((1, 0), ((1, 0), (2, 0)))
    with pytest.raises(InputError):
        spec.coordinates_in_basis((0, 1), ((1, 0),))


def test_canonicalization_handles_empty_zero_only_and_dependent_support_pairs() -> None:
    spec = GroupSpec(3, 2)
    assert canonical_multiset(spec, []) == ()
    assert canonical_multiset(spec, [(0, 0), (0, 0)]) == ((0, 0), (0, 0))
    sequence = [(1, 0), (2, 0), (0, 1)]
    assert canonical_multiset(spec, sequence) == canonical_multiset(spec, tuple(reversed(sequence)))
