#!/usr/bin/env python3
"""Replay the finite local lemmas used by the dependent-triple argument.

This verifier is intentionally package-local.  It uses only the Python
standard library and the four-element, phase-free one-site Pauli algebra
defined below.  The computation corroborates the finite case analyses in the
manuscript; it does not replace the manuscript's analytic composition proof.
"""

from __future__ import annotations

import itertools
import json


LETTERS = range(4)
ANTICOMMUTING_BASES = tuple(
    (a, b)
    for a in (1, 2, 3)
    for b in (1, 2, 3)
    if a != b
)


def multiply(a: int, b: int) -> int:
    """Multiply phase-free Pauli letters encoded as I=0, X=1, Z=2, Y=3."""

    return a ^ b


def symplectic(a: int, b: int) -> int:
    """Return 1 exactly when the encoded one-site Pauli letters anticommute."""

    ax, az = a & 1, (a >> 1) & 1
    bx, bz = b & 1, (b >> 1) & 1
    return (ax * bz + az * bx) & 1


def weight(a: int) -> int:
    return int(a != 0)


def frame(a: int, b: int) -> tuple[int, int, int]:
    return a, b, multiply(a, b)


def raw_frame_cost(a: int, b: int, central: int) -> int:
    coefficients = [4, 4, 4]
    coefficients[central] = 2
    return sum(
        coefficients[index] * weight(letter)
        for index, letter in enumerate(frame(a, b))
    )


def restore_cost(targets: tuple[int, int, int], a: int, b: int) -> int:
    return sum(
        weight(multiply(targets[index], letter))
        for index, letter in enumerate(frame(a, b))
    )


def check_deletion() -> dict[str, object]:
    counts = {"commuting": 0, "anticommuting": 0}
    maxima = {"commuting": -999, "anticommuting": -999}
    minima = {"commuting": 999, "anticommuting": 999}
    total = 0
    for a, b in itertools.product(LETTERS, repeat=2):
        if a == b == 0:
            continue
        relation = "anticommuting" if symplectic(a, b) else "commuting"
        for targets in itertools.product(LETTERS, repeat=3):
            for central in range(3):
                old = raw_frame_cost(a, b, central) + restore_cost(targets, a, b)
                new = restore_cost(targets, 0, 0)
                delta = new - old
                total += 1
                counts[relation] += 1
                maxima[relation] = max(maxima[relation], delta)
                minima[relation] = min(minima[relation], delta)
    return {
        "rows": total,
        "relation_counts": counts,
        "minimum_delta": minima,
        "maximum_delta": maxima,
        "passes": (
            total == 2880
            and maxima["commuting"] == -4
            and maxima["anticommuting"] == -7
        ),
    }


def check_core_alignment() -> dict[str, object]:
    rows = 0
    frame_contribution_invariant = True
    maximum_restore_increase = -999
    maximum_frame_hamming_distance = -1
    for old_basis in ANTICOMMUTING_BASES:
        for new_basis in ANTICOMMUTING_BASES:
            old_frame = frame(*old_basis)
            new_frame = frame(*new_basis)
            for targets in itertools.product(LETTERS, repeat=3):
                for central in range(3):
                    frame_contribution_invariant &= (
                        raw_frame_cost(*old_basis, central) == 10
                        and raw_frame_cost(*new_basis, central) == 10
                    )
                    maximum_restore_increase = max(
                        maximum_restore_increase,
                        restore_cost(targets, *new_basis)
                        - restore_cost(targets, *old_basis),
                    )
                    maximum_frame_hamming_distance = max(
                        maximum_frame_hamming_distance,
                        sum(
                            int(old_frame[index] != new_frame[index])
                            for index in range(3)
                        ),
                    )
                    rows += 1
    return {
        "rows": rows,
        "frame_contribution_always_10": frame_contribution_invariant,
        "maximum_restore_increase": maximum_restore_increase,
        "maximum_frame_hamming_distance": maximum_frame_hamming_distance,
        "passes": (
            rows == 6912
            and frame_contribution_invariant
            and maximum_restore_increase == 3
        ),
    }


def labels(s0: int, s1: int, basis: tuple[int, int]) -> tuple[int, int]:
    a, b = basis
    return (
        2 * symplectic(s0, a) + symplectic(s1, a),
        2 * symplectic(s0, b) + symplectic(s1, b),
    )


def feasible_label_pair(value: tuple[int, int]) -> bool:
    return (
        value[0] in (1, 2, 3)
        and value[1] in (1, 2, 3)
        and value[0] != value[1]
    )


def check_same_site_rigidity() -> dict[str, object]:
    rows = 0
    feasible_rows = 0
    counterexamples = 0
    for first_basis in ANTICOMMUTING_BASES:
        for second_basis in ANTICOMMUTING_BASES:
            for s0, s1 in itertools.product(LETTERS, repeat=2):
                first_labels = labels(s0, s1, first_basis)
                second_labels = labels(s0, s1, second_basis)
                feasible = (
                    first_labels == second_labels
                    and feasible_label_pair(first_labels)
                )
                rows += 1
                if feasible:
                    feasible_rows += 1
                    counterexamples += int(first_basis != second_basis)
    return {
        "rows": rows,
        "feasible_rows": feasible_rows,
        "different_basis_counterexamples": counterexamples,
        "passes": rows == 576 and counterexamples == 0,
    }


def check_distinct_site_tag_cost() -> dict[str, object]:
    two_site_letters = tuple(itertools.product(LETTERS, repeat=2))
    rows = 0
    basis_pair_minima: list[int] = []
    for first_basis in ANTICOMMUTING_BASES:
        for second_basis in ANTICOMMUTING_BASES:
            best = 999
            for s0 in two_site_letters:
                for s1 in two_site_letters:
                    first_labels = labels(s0[0], s1[0], first_basis)
                    second_labels = labels(s0[1], s1[1], second_basis)
                    rows += 1
                    if (
                        first_labels != second_labels
                        or not feasible_label_pair(first_labels)
                    ):
                        continue
                    cost = 2 * (
                        sum(weight(letter) for letter in s0)
                        + sum(weight(letter) for letter in s1)
                    )
                    best = min(best, cost)
            basis_pair_minima.append(best)
    return {
        "rows": rows,
        "basis_pairs": len(basis_pair_minima),
        "minimum_costs_observed": sorted(set(basis_pair_minima)),
        "passes": rows == 9216 and set(basis_pair_minima) == {8},
    }


def check_tag_floor() -> dict[str, object]:
    label_pairs = tuple(
        (c0, c1)
        for c0 in (1, 2, 3)
        for c1 in (1, 2, 3)
        if c0 != c1
    )
    both_rows_nonzero = True
    for c0, c1 in label_pairs:
        first_syndrome_row = ((c0 >> 1) & 1, (c1 >> 1) & 1)
        second_syndrome_row = (c0 & 1, c1 & 1)
        both_rows_nonzero &= (
            first_syndrome_row != (0, 0)
            and second_syndrome_row != (0, 0)
        )
    return {
        "ordered_distinct_nonzero_label_pairs": len(label_pairs),
        "both_syndrome_rows_nonzero": both_rows_nonzero,
        "tag_cost_floor": 4 if both_rows_nonzero else None,
        "passes": len(label_pairs) == 6 and both_rows_nonzero,
    }


def check_composition(
    same_site: dict[str, object],
    distinct_site: dict[str, object],
    tag_floor: dict[str, object],
) -> dict[str, object]:
    checks = {
        "deletion_credit_exceeds_alignment_cost": 4 > 3,
        "distinct_site_nonlocalized_case": 4 + 4 >= 8,
        "distinct_site_localized_case": distinct_site["passes"] is True,
        "same_site_tag_nonincrease": 4 <= 4,
        "same_site_alignment_is_payable": 4 >= 3,
        "same_site_rigidity": same_site["passes"] is True,
        "support_zero_infeasible_for_anticommutation": symplectic(0, 0) == 0,
        "tag_floor_is_four": tag_floor["tag_cost_floor"] == 4,
    }
    return {
        "arithmetic": {
            "deletion_credit_floor": 4,
            "alignment_cost_ceiling": 3,
            "old_tag_cost_floor": 4,
            "distinct_site_new_tag_cost": 8,
            "same_site_new_tag_cost": 4,
        },
        "checks": checks,
        "passes": all(checks.values()),
    }


def main() -> int:
    deletion = check_deletion()
    alignment = check_core_alignment()
    same_site = check_same_site_rigidity()
    distinct_site = check_distinct_site_tag_cost()
    tag_floor = check_tag_floor()
    composition = check_composition(same_site, distinct_site, tag_floor)
    sections = {
        "deletion": deletion,
        "core_alignment": alignment,
        "same_site_rigidity": same_site,
        "distinct_site_tag_cost": distinct_site,
        "tag_floor": tag_floor,
        "composition": composition,
    }
    result = {
        "schema": "certificate-versus-support.dependent-triple-replay.v1",
        "interpretation": (
            "Package-local replay of finite local lemmas; corroborates but does "
            "not replace the analytic composition proof."
        ),
        "sections": sections,
        "all_checks": all(section["passes"] is True for section in sections.values()),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
