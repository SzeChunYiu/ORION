#!/usr/bin/env python3
"""Exact small-group differential oracle for generalized Davenport engines."""
from __future__ import annotations

import itertools
import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

SCHEMA = "ORION.NQ.EngineBSmallGroupOracleR9.Results.v1"
Element = tuple[int, ...]


@dataclass(frozen=True)
class Group:
    name: str
    moduli: tuple[int, ...]

    @property
    def zero(self) -> Element:
        return tuple(0 for _ in self.moduli)

    @property
    def elements(self) -> tuple[Element, ...]:
        return tuple(itertools.product(*(range(modulus) for modulus in self.moduli)))

    def add(self, left: Element, right: Element) -> Element:
        return tuple((a + b) % modulus for a, b, modulus in zip(left, right, self.moduli, strict=True))


@dataclass(frozen=True)
class BoundaryCase:
    group: Group
    k: int
    expected_dk: int


CASES = (
    BoundaryCase(Group("C2", (2,)), 1, 2),
    BoundaryCase(Group("C2", (2,)), 2, 4),
    BoundaryCase(Group("C2", (2,)), 3, 6),
    BoundaryCase(Group("C3", (3,)), 1, 3),
    BoundaryCase(Group("C3", (3,)), 2, 6),
    BoundaryCase(Group("C3", (3,)), 3, 9),
    BoundaryCase(Group("C2^2", (2, 2)), 1, 3),
    BoundaryCase(Group("C2^2", (2, 2)), 2, 5),
    BoundaryCase(Group("C2^2", (2, 2)), 3, 7),
    BoundaryCase(Group("C3^2", (3, 3)), 1, 5),
    BoundaryCase(Group("C3^2", (3, 3)), 2, 8),
)


def zero_sum_masks(group: Group, sequence: tuple[Element, ...]) -> tuple[int, ...]:
    subset_sums: list[Element] = [group.zero] * (1 << len(sequence))
    result: list[int] = []
    for mask in range(1, 1 << len(sequence)):
        bit = mask & -mask
        index = bit.bit_length() - 1
        subset_sums[mask] = group.add(subset_sums[mask ^ bit], sequence[index])
        if subset_sums[mask] == group.zero:
            result.append(mask)
    return tuple(result)


def packing_solver_a(length: int, hyperedges: tuple[int, ...]) -> int:
    by_position: list[list[int]] = [[] for _ in range(length)]
    for edge in hyperedges:
        for position in range(length):
            if (edge >> position) & 1:
                by_position[position].append(edge)

    @lru_cache(maxsize=None)
    def solve(available: int) -> int:
        if available == 0:
            return 0
        first_bit = available & -available
        first_position = first_bit.bit_length() - 1
        best = solve(available ^ first_bit)
        for edge in by_position[first_position]:
            if edge & available == edge:
                best = max(best, 1 + solve(available ^ edge))
        return best

    return solve((1 << length) - 1)


def packing_solver_b(length: int, hyperedges: tuple[int, ...]) -> int:
    full = (1 << length) - 1
    dp = [0] * (full + 1)
    for available in range(1, full + 1):
        first_bit = available & -available
        best = dp[available ^ first_bit]
        for edge in hyperedges:
            if edge & available == edge:
                best = max(best, 1 + dp[available ^ edge])
        dp[available] = best
    return dp[full]


def sequence_multisets(group: Group, length: int):
    elements = group.elements
    for indices in itertools.combinations_with_replacement(range(len(elements)), length):
        yield tuple(elements[index] for index in indices)


def minimum_packing_at_length(group: Group, length: int) -> tuple[int, int]:
    minimum = length + 1
    checked = 0
    for sequence in sequence_multisets(group, length):
        hyperedges = zero_sum_masks(group, sequence)
        value_a = packing_solver_a(length, hyperedges)
        value_b = packing_solver_b(length, hyperedges)
        assert value_a == value_b
        minimum = min(minimum, value_a)
        checked += 1
    expected = math.comb(len(group.elements) + length - 1, length)
    assert checked == expected
    return minimum, checked


def audit_boundary(case: BoundaryCase) -> dict[str, object]:
    lower_length = case.expected_dk - 1
    upper_length = case.expected_dk
    lower_minimum, lower_checked = minimum_packing_at_length(case.group, lower_length)
    upper_minimum, upper_checked = minimum_packing_at_length(case.group, upper_length)
    assert lower_minimum == case.k - 1
    assert upper_minimum == case.k
    return {
        "group": case.group.name,
        "moduli": list(case.group.moduli),
        "k": case.k,
        "expected_D_k": case.expected_dk,
        "lower_length": lower_length,
        "lower_minimum_packing": lower_minimum,
        "lower_sequence_multisets_checked": lower_checked,
        "upper_length": upper_length,
        "upper_minimum_packing": upper_minimum,
        "upper_sequence_multisets_checked": upper_checked,
        "total_sequence_multisets_checked": lower_checked + upper_checked,
        "solver_disagreements": 0,
        "status": "FINITE_EXACT",
    }


def main() -> None:
    boundaries = [audit_boundary(case) for case in CASES]
    result = {
        "schema": SCHEMA,
        "method": {
            "sequence_space": "all multisets over all group elements, including zero",
            "hypergraph_vertices": "labeled sequence positions",
            "hyperedges": "all nonempty zero-sum position subsets",
            "solver_a": "memoized first-position hyperedge branching with unused positions allowed",
            "solver_b": "independent full available-mask dynamic programming over zero-sum submasks",
            "boundary_rule": "D_k is certified by a k-1 lower minimum at length D_k-1 and a k upper minimum at length D_k",
        },
        "boundaries": boundaries,
        "summary": {
            "boundary_cases": len(boundaries),
            "sequence_multisets_checked": sum(int(row["total_sequence_multisets_checked"]) for row in boundaries),
            "solver_disagreements": 0,
            "boundary_mismatches": 0,
            "status": "PASS",
        },
        "authority": {
            "exact_on_registered_small_groups": True,
            "structurally_independent_of_complement_extension_architecture": True,
            "independent_C5_3_replay": False,
            "D3_C5_3_authority": False,
            "D4_C5_3_authority": False,
            "external_replay": False,
            "grants_journal_authority": False,
        },
        "terminal": "NQ_ENGINE_B_SMALL_GROUP_ORACLE__COMPLETE_BOUNDARY_AND_DUAL_PACKING_AUDIT_PASS",
    }
    output = Path(__file__).with_name("ENGINE_B_SMALL_GROUP_ORACLE_R9_RESULTS.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
