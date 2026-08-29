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


def check_f2_restricted_bound() -> dict[str, object]:
    families = 0
    basis_equalities = 0
    for dimension in range(1, 4):
        nonzero = tuple(range(1, 1 << dimension))
        basis = {1 << index for index in range(dimension)}
        for mask in range(1 << len(nonzero)):
            alphabet = tuple(
                value for index, value in enumerate(nonzero) if (mask >> index) & 1
            )
            value = zsf_bruteforce(
                alphabet, lambda left, right: left ^ right, 0, dimension + 1
            )
            assert value <= dimension
            if basis.issubset(set(alphabet)):
                assert value == dimension
                basis_equalities += 1
            families += 1
    assert families == 138
    assert basis_equalities == 19
    return {
        "name": "restricted_F2_rank_bound",
        "status": "PASS",
        "scope": "all alphabets in F2^d for d=1,2,3",
        "families": families,
        "basis_equalities": basis_equalities,
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
        check_f2_restricted_bound(),
        check_cyclic_rank_boundary(),
        check_restore_sensitivity(),
        check_deletion_terminal_equivalence(),
        check_global_descent(),
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
