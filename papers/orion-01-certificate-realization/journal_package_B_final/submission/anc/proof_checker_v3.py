#!/usr/bin/env python3
"""Implementation-independent finite checker for ORION-01 bounded V3.

The checker is derived from the manuscript statements. It intentionally imports
no ORION package, PyZX module, production move registry, or parent experiment.
Finite enumeration corroborates definitions and case analysis; it does not
replace the analytic all-size proofs or the separately bound compiler witnesses.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Callable, Iterable, Sequence, TypeVar

T = TypeVar("T")


def nonempty_index_sets(length: int, *, proper: bool = False) -> Iterable[tuple[int, ...]]:
    upper = length - 1 if proper else length
    for size in range(1, upper + 1):
        yield from itertools.combinations(range(length), size)


def sequence_sum(
    sequence: Sequence[T], add: Callable[[T, T], T], zero: T
) -> T:
    total = zero
    for value in sequence:
        total = add(total, value)
    return total


def zero_sum_indices(
    sequence: Sequence[T],
    add: Callable[[T, T], T],
    zero: T,
    *,
    proper: bool = False,
) -> tuple[int, ...] | None:
    for indices in nonempty_index_sets(len(sequence), proper=proper):
        total = zero
        for index in indices:
            total = add(total, sequence[index])
        if total == zero:
            return indices
    return None


def is_zero_sum_free(
    sequence: Sequence[T], add: Callable[[T, T], T], zero: T
) -> bool:
    return zero_sum_indices(sequence, add, zero) is None


def zsf_bruteforce(
    alphabet: Sequence[T],
    add: Callable[[T, T], T],
    zero: T,
    forcing_length: int,
) -> int:
    """Return exact zsf when ``forcing_length`` is known to force a zero sum."""
    best = 0
    for length in range(1, forcing_length + 1):
        has_free_sequence = False
        for sequence in itertools.product(alphabet, repeat=length):
            if is_zero_sum_free(sequence, add, zero):
                has_free_sequence = True
                best = length
                break
        if not has_free_sequence:
            return best
    raise AssertionError("declared forcing length did not force a zero sum")


def delete_indices(sequence: Sequence[T], indices: Sequence[int]) -> tuple[T, ...]:
    removed = set(indices)
    return tuple(value for index, value in enumerate(sequence) if index not in removed)


def restore_functional(values: Sequence[int]) -> int:
    if values and values[0] != 0 and all(value == values[0] for value in values):
        return 1
    return sum(value != 0 for value in values)


PauliKey = tuple[int, int]


def pauli_weight(key: PauliKey) -> int:
    return (key[0] | key[1]).bit_count()


def pauli_product(left: PauliKey, right: PauliKey) -> PauliKey:
    """Multiply phase-quotiented Paulis in the binary symplectic encoding."""
    return left[0] ^ right[0], left[1] ^ right[1]


def pauli_symplectic(left: PauliKey, right: PauliKey) -> int:
    return (
        (left[0] & right[1]).bit_count()
        + (left[1] & right[0]).bit_count()
    ) & 1


def pauli_local_letter(key: PauliKey, coordinate: int) -> tuple[int, int]:
    return (key[0] >> coordinate) & 1, (key[1] >> coordinate) & 1


def restore_three(
    left: tuple[int, int], middle: tuple[int, int], right: tuple[int, int]
) -> int:
    if left == middle == right and left != (0, 0):
        return 1
    return sum(letter != (0, 0) for letter in (left, middle, right))


def r6m_acceptance(
    frames: Sequence[PauliKey], tag: PauliKey
) -> tuple[int, int] | None:
    if len(frames) != 6:
        raise ValueError("R6M requires exactly six frame Paulis")
    if any(
        pauli_symplectic(frames[2 * block], frames[2 * block + 1]) != 1
        for block in range(3)
    ):
        return None
    labels = (
        pauli_symplectic(tag, frames[0]),
        pauli_symplectic(tag, frames[1]),
    )
    if labels[0] == labels[1]:
        return None
    for block in (1, 2):
        if (
            pauli_symplectic(tag, frames[2 * block]),
            pauli_symplectic(tag, frames[2 * block + 1]),
        ) != labels:
            return None
    return labels


def r6m_objective(
    targets: Sequence[PauliKey],
    frames: Sequence[PauliKey],
    tag: PauliKey,
    centrals: Sequence[int],
    qubits: int,
) -> int:
    """Frozen unit-cost R6M objective used by the two-site obstruction."""
    raw_frame = 0
    for block in range(3):
        first_multiplier = 2 if centrals[block] == 0 else 4
        second_multiplier = 2 if centrals[block] == 1 else 4
        raw_frame += first_multiplier * pauli_weight(frames[2 * block])
        raw_frame += second_multiplier * pauli_weight(frames[2 * block + 1])
    restored = [
        pauli_product(target, frame) for target, frame in zip(targets, frames)
    ]
    restore_cost = 0
    for role in (0, 1):
        for coordinate in range(qubits):
            restore_cost += restore_three(
                pauli_local_letter(restored[role], coordinate),
                pauli_local_letter(restored[2 + role], coordinate),
                pauli_local_letter(restored[4 + role], coordinate),
            )
    return raw_frame + 2 * pauli_weight(tag) - 18 + restore_cost


def permute_target_pairs(
    target_pairs: Sequence[tuple[PauliKey, PauliKey]], permutations: Sequence[int]
) -> tuple[PauliKey, ...]:
    ordered: list[PauliKey] = []
    for pair, permutation in zip(target_pairs, permutations):
        ordered.extend(pair if permutation == 0 else (pair[1], pair[0]))
    return tuple(ordered)


def weight_at_most_one_paulis(qubits: int) -> tuple[PauliKey, ...]:
    keys: list[PauliKey] = [(0, 0)]
    for coordinate in range(qubits):
        bit = 1 << coordinate
        keys.extend(((bit, 0), (bit, bit), (0, bit)))
    return tuple(keys)


def all_paulis(qubits: int) -> tuple[PauliKey, ...]:
    return tuple(
        (x_mask, z_mask)
        for x_mask in range(1 << qubits)
        for z_mask in range(1 << qubits)
    )


def joint_active_column_support(left: PauliKey, right: PauliKey) -> int:
    """Count columns where either member of a Pauli frame pair is active."""
    return (left[0] | left[1] | right[0] | right[1]).bit_count()


def check_r6i_joint_column_statistic() -> dict[str, object]:
    """Keep the rank-five R6I word aligned with its block-column statistic.

    A rank-only R6I letter is created by zeroing both independent generators at
    one column.  Consequently its word length counts the union of the two
    support sets.  This is not, in general, the maximum of the two individual
    Pauli weights.  The rank-five production bindings are recorded as 10-bit
    integer vectors; this checker corroborates their formal rank and encoding
    boundary without claiming to reconstruct the production alphabet.
    """
    left = (1, 0)
    right = (2, 0)
    joint = joint_active_column_support(left, right)
    maximum_individual = max(pauli_weight(left), pauli_weight(right))
    block_a_basis = (1, 68, 136, 272, 544)
    block_b_basis = (2, 4, 8, 16, 32)
    basis_vectors_are_10_bit = all(
        0 <= value < (1 << 10) for value in block_a_basis + block_b_basis
    )
    block_a_rank = f2_span_rank(block_a_basis)
    block_b_rank = f2_span_rank(block_b_basis)
    assert joint == 2
    assert maximum_individual == 1
    assert joint != maximum_individual
    assert basis_vectors_are_10_bit
    assert block_a_rank == block_b_rank == 5
    return {
        "name": "r6i_joint_active_column_statistic",
        "status": "PASS",
        "scope": (
            "formal support-statistic identity plus rank of the two bound "
            "10-bit basis records; no production-alphabet reconstruction"
        ),
        "disjoint_example_joint_columns": joint,
        "disjoint_example_maximum_individual_weight": maximum_individual,
        "statistics_are_not_interchangeable": joint != maximum_individual,
        "block_a_basis_rank": block_a_rank,
        "block_b_basis_rank": block_b_rank,
        "basis_vectors_are_10_bit_encodings": basis_vectors_are_10_bit,
    }


def check_r6m_two_site_support_obstruction() -> dict[str, object]:
    """Recompute the frozen 5-versus-6 witness without ORION imports."""
    qubits = 2
    target_pairs: tuple[tuple[PauliKey, PauliKey], ...] = (
        ((0, 1), (0, 1)),
        ((0, 1), (0, 1)),
        ((0, 2), (2, 0)),
    )
    support_two_frames: tuple[PauliKey, ...] = (
        (0, 1),
        (1, 1),
        (0, 1),
        (1, 1),
        (0, 2),
        (3, 0),
    )
    support_two_tag = (0, 1)
    support_two_centrals = (0, 0, 1)
    support_two_permutations = (0, 0, 0)
    support_two_labels = r6m_acceptance(support_two_frames, support_two_tag)
    support_two_cost = r6m_objective(
        permute_target_pairs(target_pairs, support_two_permutations),
        support_two_frames,
        support_two_tag,
        support_two_centrals,
        qubits,
    )
    support_two_maximum = max(map(pauli_weight, support_two_frames))

    frame_keys = weight_at_most_one_paulis(qubits)
    tag_keys = all_paulis(qubits)
    central_choices = tuple(itertools.product((0, 1), repeat=3))
    permutation_choices = tuple(
        (0, second, third)
        for second in (0, 1)
        for third in (0, 1)
    )
    permuted_targets = {
        permutation: permute_target_pairs(target_pairs, permutation)
        for permutation in permutation_choices
    }
    frame_six_tuples_enumerated = 0
    feasible_frame_six_tuples = 0
    accepted_frame_tag_pairs = 0
    objective_evaluations = 0
    support_at_most_one_optimum: int | None = None
    for frames in itertools.product(frame_keys, repeat=6):
        frame_six_tuples_enumerated += 1
        if any(
            pauli_symplectic(frames[2 * block], frames[2 * block + 1]) != 1
            for block in range(3)
        ):
            continue
        feasible_frame_six_tuples += 1
        for tag in tag_keys:
            if r6m_acceptance(frames, tag) is None:
                continue
            accepted_frame_tag_pairs += 1
            for centrals in central_choices:
                for permutations in permutation_choices:
                    objective_evaluations += 1
                    value = r6m_objective(
                        permuted_targets[permutations],
                        frames,
                        tag,
                        centrals,
                        qubits,
                    )
                    if (
                        support_at_most_one_optimum is None
                        or value < support_at_most_one_optimum
                    ):
                        support_at_most_one_optimum = value

    assert support_two_labels == (0, 1)
    assert support_two_maximum == 2
    assert support_two_cost == 5
    assert frame_six_tuples_enumerated == len(frame_keys) ** 6 == 7**6
    assert feasible_frame_six_tuples == 12**3
    assert support_at_most_one_optimum == 6
    return {
        "name": "r6m_two_site_support_obstruction",
        "status": "PASS",
        "scope": "complete support-at-most-one family for the frozen n=2 witness",
        "support_two_cost": support_two_cost,
        "support_two_maximum_frame_support": support_two_maximum,
        "support_at_most_one_optimum": support_at_most_one_optimum,
        "strict_gap": support_at_most_one_optimum - support_two_cost,
        "frame_six_tuples_enumerated": frame_six_tuples_enumerated,
        "feasible_frame_six_tuples": feasible_frame_six_tuples,
        "tag_keys_enumerated": len(tag_keys),
        "accepted_frame_tag_pairs": accepted_frame_tag_pairs,
        "objective_evaluations": objective_evaluations,
        "complete_support_at_most_one_enumeration": True,
        "imports_orion": False,
    }


def f2_span_rank(alphabet: Sequence[int]) -> int:
    """Return the rank of integer-encoded binary vectors."""
    pivots: dict[int, int] = {}
    for original in alphabet:
        value = original
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def check_f2_generated_span_identity() -> dict[str, object]:
    families = 0
    ambient_spanning_alphabets = 0
    strict_inequality_cases = 0
    for dimension in range(1, 4):
        vectors = tuple(range(1 << dimension))
        for mask in range(1 << len(vectors)):
            alphabet = tuple(
                value for index, value in enumerate(vectors) if (mask >> index) & 1
            )
            rank = f2_span_rank(alphabet)
            value = zsf_bruteforce(
                alphabet, lambda left, right: left ^ right, 0, dimension + 1
            )
            assert value == rank
            if value < rank:
                strict_inequality_cases += 1
            if rank == dimension:
                ambient_spanning_alphabets += 1
            families += 1
    assert families == 276
    assert strict_inequality_cases == 0
    return {
        "name": "binary_generated_span_identity",
        "status": "PASS",
        "scope": "all alphabets, including zero, in F2^d for d=1,2,3",
        "families": families,
        "generated_span_equalities": families,
        "ambient_spanning_alphabets": ambient_spanning_alphabets,
        "strict_inequality_cases": strict_inequality_cases,
    }


def check_cyclic_rank_boundary() -> dict[str, object]:
    cases = 0
    for modulus in range(2, 11):
        add = lambda left, right, n=modulus: (left + right) % n
        value = zsf_bruteforce((1,), add, 0, modulus)
        assert value == modulus - 1
        cases += 1
    assert cases == 9
    return {
        "name": "cyclic_singleton_counterexample_to_general_rank_reading",
        "status": "PASS",
        "scope": "Z_n with alphabet {1}, n=2,...,10",
        "cases": cases,
    }


def check_restore_sensitivity() -> dict[str, object]:
    comparisons = 0
    sharpness_cases = 0
    paulis = (0, 1, 2, 3)  # identity plus three distinct nonidentity letters
    for arity in range(2, 8):
        for values in itertools.product(paulis, repeat=arity):
            before = restore_functional(values)
            for index in range(arity):
                for replacement in paulis:
                    changed = list(values)
                    changed[index] = replacement
                    delta = restore_functional(changed) - before
                    assert delta <= arity - 1
                    comparisons += 1
        witness = [1] * arity
        witness[0] = 2
        assert (
            restore_functional(witness) - restore_functional([1] * arity)
            == arity - 1
        )
        sharpness_cases += 1
    assert comparisons == 582528
    assert sharpness_cases == 6
    return {
        "name": "exact_one_argument_restore_sensitivity",
        "status": "PASS",
        "scope": "Pauli alphabet, b=2,...,7",
        "comparisons": comparisons,
        "sharpness_cases": sharpness_cases,
    }


def check_deletion_terminal_equivalence() -> dict[str, object]:
    fixtures: list[
        tuple[str, tuple[int, ...], Callable[[int, int], int], int, int, int]
    ] = [
        ("F2^2_full", (1, 2, 3), lambda left, right: left ^ right, 0, 2, 4),
        ("F2^3_basis", (1, 2, 4), lambda left, right: left ^ right, 0, 3, 5),
        ("Z5_singleton", (1,), lambda left, right: (left + right) % 5, 0, 4, 6),
    ]
    for _name, alphabet, add, zero, ceiling, maximum_length in fixtures:
        assert zsf_bruteforce(alphabet, add, zero, ceiling + 1) == ceiling
        for length in range(ceiling + 1, maximum_length + 1):
            for original in itertools.product(alphabet, repeat=length):
                original_total = sequence_sum(original, add, zero)
                if original_total == zero:
                    continue
                sequence = tuple(original)
                previous_length = len(sequence)
                while True:
                    indices = zero_sum_indices(sequence, add, zero, proper=True)
                    if indices is None:
                        break
                    sequence = delete_indices(sequence, indices)
                    assert len(sequence) < previous_length
                    assert sequence_sum(sequence, add, zero) == original_total
                    previous_length = len(sequence)
                assert is_zero_sum_free(sequence, add, zero)
                assert len(sequence) <= ceiling
    return {
        "name": "proper_deletion_and_zero_sum_free_terminal",
        "status": "PASS",
        "scope": "three exhaustive finite fixtures",
        "fixtures": len(fixtures),
    }


def check_global_descent() -> dict[str, object]:
    # Each fixture supplies two constrained generators. A deletion touches only
    # the selected generator, exactly matching the support-monotonicity premise.
    fixtures = [
        ((1, 1, 2), (1, 2, 2), 2, 2),
        ((1, 1, 2, 4), (1, 2, 4, 4), 3, 3),
        ((3, 3, 1, 2), (1, 1, 3), 2, 2),
    ]
    for left, right, left_ceiling, right_ceiling in fixtures:
        state = [tuple(left), tuple(right)]
        ceilings = [left_ceiling, right_ceiling]
        assert all(sequence_sum(sequence, lambda a, b: a ^ b, 0) != 0 for sequence in state)
        previous_phi = sum(map(len, state))
        steps = 0
        while True:
            violating = next(
                (
                    index
                    for index, sequence in enumerate(state)
                    if len(sequence) > ceilings[index]
                ),
                None,
            )
            if violating is None:
                break
            indices = zero_sum_indices(
                state[violating], lambda left, right: left ^ right, 0, proper=True
            )
            assert indices is not None
            other = 1 - violating
            unchanged_other = state[other]
            original_total = sequence_sum(
                state[violating], lambda left, right: left ^ right, 0
            )
            state[violating] = delete_indices(state[violating], indices)
            assert state[other] == unchanged_other
            assert (
                sequence_sum(state[violating], lambda left, right: left ^ right, 0)
                == original_total
            )
            phi = sum(map(len, state))
            assert phi < previous_phi
            previous_phi = phi
            steps += 1
            assert steps <= len(left) + len(right)
        assert all(
            len(sequence) <= ceiling for sequence, ceiling in zip(state, ceilings)
        )
    return {
        "name": "simultaneous_global_fixed_point_descent",
        "status": "PASS",
        "scope": "three two-generator fixtures under the monotonicity premise",
        "fixtures": len(fixtures),
    }


def check_soundness_and_product_arithmetic() -> dict[str, object]:
    fixtures = [
        # (kappa_1, beta_1, kappa_2, beta_2)
        (2, 2, 1, 5),
        (1, 5, 1, 5),
        (0, 0, 3, 4),
        (4, 7, 2, 2),
    ]
    for kappa_1, budget_1, kappa_2, budget_2 in fixtures:
        assert kappa_1 <= budget_1
        assert kappa_2 <= budget_2
        product_kappa = kappa_1 + kappa_2
        product_budget = budget_1 + budget_2
        assert product_kappa <= product_budget
    r6m = {"kappa": 2, "budget": 2}
    r6i = {"kappa": 1, "budget": 5}
    assert r6m["kappa"] == r6m["budget"]
    assert r6i["kappa"] < r6i["budget"]
    return {
        "name": "soundness_inequality_and_componentwise_arithmetic",
        "status": "PASS",
        "scope": "four arithmetic fixtures plus R6M/R6I statement consistency",
        "fixtures": len(fixtures),
    }


def run_checks() -> dict[str, object]:
    checks = [
        check_f2_generated_span_identity(),
        check_cyclic_rank_boundary(),
        check_restore_sensitivity(),
        check_deletion_terminal_equivalence(),
        check_global_descent(),
        check_r6m_two_site_support_obstruction(),
        check_r6i_joint_column_statistic(),
        check_soundness_and_product_arithmetic(),
    ]
    assert all(check["status"] == "PASS" for check in checks)
    return {
        "schema": "ORION.ORION01.IndependentProofCheck.v3",
        "checker_identity": "theorem-statements-only-v3",
        "implementation_independent": True,
        "imports_orion": False,
        "imports_pyzx": False,
        "analytic_all_size_authority": False,
        "production_witness_authority": False,
        "checks": checks,
        "all_passed": True,
        "terminal": "SUPPORTED_WITHIN_DECLARED_FINITE_SCOPE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_checks()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
