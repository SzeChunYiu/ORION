from __future__ import annotations

from itertools import product

import pytest

import engine_b as eb


def test_c5_cubed_encoding_and_addition_are_componentwise() -> None:
    assert len(eb.GROUP_ELEMENTS) == 125
    assert len(set(eb.GROUP_ELEMENTS)) == 125
    for coordinates in product(range(5), repeat=3):
        element = eb.encode_element(coordinates)
        assert eb.decode_element(element) == coordinates
        assert eb.add(element, eb.negate(element)) == eb.ZERO

    a = eb.encode_element((4, 2, 1))
    b = eb.encode_element((3, 4, 4))
    assert eb.decode_element(eb.add(a, b)) == (2, 1, 0)


def test_sequence_sum_uses_only_primitive_addition() -> None:
    basis = eb.encode_element((1, 0, 0))
    assert eb.sum_elements(()) == eb.ZERO
    assert eb.sum_elements((basis,) * 5) == eb.ZERO
    assert eb.sum_elements((basis,) * 4) == eb.encode_element((4, 0, 0))


@pytest.mark.parametrize("bad", (-1, 125, True, 1.0, "1"))
def test_group_operations_reject_noncanonical_elements(bad: object) -> None:
    with pytest.raises((TypeError, ValueError), match="group element"):
        eb.add(bad, eb.ZERO)  # type: ignore[arg-type]


def test_sat_encoding_matches_every_explicit_bin_assignment_on_small_control() -> None:
    e1 = eb.encode_element((1, 0, 0))
    sequence = (e1, eb.negate(e1), eb.ZERO)
    encoded = eb.build_factorization_cnf(sequence, required_bins=2)

    for labels in product((-1, 0, 1), repeat=len(sequence)):
        model = encoded.model_for_labels(labels)
        observed = eb.evaluate_cnf(encoded.cnf, model)
        bins = tuple(
            tuple(index for index, label in enumerate(labels) if label == bin_index)
            for bin_index in range(2)
        )
        expected = all(bins) and all(
            eb.sum_elements(sequence[index] for index in selected) == eb.ZERO for selected in bins
        )
        assert observed is expected


def test_dpll_control_solver_finds_and_rejects_exact_factorizations() -> None:
    e1 = eb.encode_element((1, 0, 0))
    positive = (e1, eb.negate(e1), e1, eb.negate(e1))
    negative = (e1, eb.negate(e1), e1)

    positive_encoding = eb.build_factorization_cnf(positive, required_bins=2)
    positive_model = eb.solve_cnf_dpll(positive_encoding.cnf)
    assert positive_model is not None
    witness = positive_encoding.extract_witness(positive_model)
    eb.verify_witness(positive, required_bins=2, bins=witness)

    negative_encoding = eb.build_factorization_cnf(negative, required_bins=2)
    assert eb.solve_cnf_dpll(negative_encoding.cnf) is None


def test_zero_and_duplicate_heavy_controls_have_exact_semantics() -> None:
    e1 = eb.encode_element((1, 0, 0))
    assert eb.has_k_disjoint_zero_sums_bruteforce((eb.ZERO,), 1)
    assert not eb.has_k_disjoint_zero_sums_bruteforce((), 1)
    assert eb.has_k_disjoint_zero_sums_bruteforce((e1,) * 10, 2)
    assert not eb.has_k_disjoint_zero_sums_bruteforce((e1,) * 9, 2)


def test_permutation_does_not_change_factorization_decision() -> None:
    e1 = eb.encode_element((1, 0, 0))
    e2 = eb.encode_element((0, 1, 0))
    sequence = (e1, eb.negate(e1), e2, eb.negate(e2), e1)
    reversed_sequence = tuple(reversed(sequence))
    assert eb.has_k_disjoint_zero_sums_bruteforce(sequence, 2)
    assert eb.has_k_disjoint_zero_sums_bruteforce(reversed_sequence, 2)
    assert (eb.solve_cnf_dpll(eb.build_factorization_cnf(sequence, 2).cnf) is not None) == (
        eb.solve_cnf_dpll(eb.build_factorization_cnf(reversed_sequence, 2).cnf) is not None
    )


def test_encoding_digest_is_deterministic_and_sequence_bound() -> None:
    first = eb.build_factorization_cnf((0, 1, 2), 2)
    second = eb.build_factorization_cnf((0, 1, 2), 2)
    different = eb.build_factorization_cnf((0, 2, 1), 2)
    assert first.cnf_sha256 == second.cnf_sha256
    assert first.cnf_sha256 != different.cnf_sha256


def test_sat_witness_certificate_is_hash_bound_and_tamper_evident() -> None:
    e1 = eb.encode_element((1, 0, 0))
    sequence = (e1, eb.negate(e1), e1, eb.negate(e1))
    encoded = eb.build_factorization_cnf(sequence, 2)
    model = eb.solve_cnf_dpll(encoded.cnf)
    assert model is not None
    certificate = eb.build_sat_certificate(
        record_id="control-1",
        encoded=encoded,
        model=model,
        solver_identity="CONTROL_DPLL",
    )
    eb.verify_certificate(sequence, required_bins=2, certificate=certificate)
    certificate["witness_bins"][0][0] = 999
    with pytest.raises(eb.CertificateMismatch):
        eb.verify_certificate(sequence, required_bins=2, certificate=certificate)


def test_factorization_encoder_rejects_out_of_scope_shapes() -> None:
    with pytest.raises(ValueError, match="nonempty"):
        eb.build_factorization_cnf((), 1)
    with pytest.raises(ValueError, match="31"):
        eb.build_factorization_cnf((0,) * 32, 1)
    with pytest.raises(ValueError, match="one through four"):
        eb.build_factorization_cnf((0,), 5)
