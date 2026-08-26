from __future__ import annotations

import itertools

import pytest

from nq_engine_a.factorization import (
    FactorizationCertificate,
    FactorizationStatus,
    assert_valid_certificate,
    find_disjoint_zero_sums,
    verify_factorization_certificate,
)
from nq_engine_a.group import GroupSpec, InputError


def brute_force_exists(spec: GroupSpec, sequence: tuple[tuple[int, ...], ...], k: int) -> bool:
    """Deliberately separate labelled-bin oracle for tiny domains."""
    for assignment in itertools.product(range(k + 1), repeat=len(sequence)):
        bins = [
            tuple(index for index, label in enumerate(assignment) if label == j + 1)
            for j in range(k)
        ]
        if any(not indices for indices in bins):
            continue
        if all(
            spec.sum_vectors(sequence[index] for index in indices) == spec.zero for indices in bins
        ):
            return True
    return False


@pytest.mark.parametrize(
    "p,d,max_length,k",
    [(2, 1, 6, 2), (3, 1, 4, 2), (2, 2, 3, 2)],
)
def test_exact_dp_equals_labelled_bruteforce_on_complete_tiny_domains(
    p: int, d: int, max_length: int, k: int
) -> None:
    spec = GroupSpec(p, d)
    elements = tuple(spec.elements())
    for length in range(max_length + 1):
        for sequence in itertools.combinations_with_replacement(elements, length):
            result = find_disjoint_zero_sums(spec, sequence, k)
            expected = brute_force_exists(spec, sequence, k)
            assert (result.status is FactorizationStatus.POSITIVE) is expected
            assert result.exhaustive
            if expected:
                assert result.certificate is not None
                assert verify_factorization_certificate(spec, sequence, k, result.certificate)
            else:
                assert result.status is FactorizationStatus.NEGATIVE
                assert result.certificate is None


def test_positive_negative_and_duplicate_heavy_controls() -> None:
    c2 = GroupSpec(2, 1)
    assert find_disjoint_zero_sums(c2, [(0,)], 1).status is FactorizationStatus.POSITIVE
    assert find_disjoint_zero_sums(c2, [], 1).status is FactorizationStatus.NEGATIVE
    duplicate_heavy = [(1,), (1,), (1,), (1,)]
    assert find_disjoint_zero_sums(c2, duplicate_heavy, 2).status is FactorizationStatus.POSITIVE
    assert find_disjoint_zero_sums(c2, duplicate_heavy, 3).status is FactorizationStatus.NEGATIVE


def test_permutation_invariance_preserves_verdict() -> None:
    spec = GroupSpec(3, 1)
    sequence = ((1,), (2,), (0,), (1,))
    verdicts = {
        find_disjoint_zero_sums(spec, perm, 2).status for perm in itertools.permutations(sequence)
    }
    assert verdicts == {FactorizationStatus.POSITIVE}


def test_certificate_contains_nonempty_disjoint_original_indices_with_zero_sums() -> None:
    spec = GroupSpec(5, 2)
    sequence = ((1, 0), (4, 0), (0, 1), (0, 4), (2, 2))
    result = find_disjoint_zero_sums(spec, sequence, 2)
    assert result.status is FactorizationStatus.POSITIVE
    assert result.certificate is not None
    flat = [index for indices in result.certificate.bins for index in indices]
    assert all(result.certificate.bins)
    assert len(flat) == len(set(flat))
    assert all(
        spec.sum_vectors(sequence[i] for i in indices) == spec.zero
        for indices in result.certificate.bins
    )


def test_mutated_certificates_are_rejected() -> None:
    spec = GroupSpec(3, 1)
    sequence = ((1,), (2,), (0,))
    hostile = (
        FactorizationCertificate(bins=((0, 1),)),  # wrong bin count
        FactorizationCertificate(bins=((0, 1), ())),  # empty
        FactorizationCertificate(bins=((0, 1), (1,))),  # overlap
        FactorizationCertificate(bins=((0, 1), (3,))),  # out of range
        FactorizationCertificate(bins=((0,), (2,))),  # first sum is nonzero
        FactorizationCertificate(bins=((0, 1), (2, 2))),  # repeated within bin
    )
    for certificate in hostile:
        assert not verify_factorization_certificate(spec, sequence, 2, certificate)
        with pytest.raises(ValueError):
            assert_valid_certificate(spec, sequence, 2, certificate)


def test_resource_bound_never_promotes_partial_search_to_negative() -> None:
    spec = GroupSpec(5, 2)
    sequence = tuple(spec.elements())[:8]
    result = find_disjoint_zero_sums(spec, sequence, 3, max_states=2)
    assert result.status is FactorizationStatus.CANNOT_CHECK_RESOURCE_BOUND
    assert not result.exhaustive
    assert result.certificate is None
    assert result.layers_completed < len(sequence)


@pytest.mark.parametrize("k", [0, -1, True, 1.5])
def test_invalid_bin_counts_are_rejected(k: object) -> None:
    with pytest.raises(InputError):
        find_disjoint_zero_sums(GroupSpec(2, 1), [(0,)], k)  # type: ignore[arg-type]


def test_hostile_sequence_shapes_are_rejected_before_search() -> None:
    spec = GroupSpec(3, 2)
    for sequence in (None, "00", [(0,)], [(0, 3)]):
        with pytest.raises(InputError):
            find_disjoint_zero_sums(spec, sequence, 1)


def test_json_decoded_array_input_is_accepted_consistently_with_schema() -> None:
    result = find_disjoint_zero_sums(GroupSpec(3, 1), [[1], [2], [0]], 2)
    assert result.status is FactorizationStatus.POSITIVE
