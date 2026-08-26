#!/usr/bin/env python3
"""Bounded independent controls for the all-group fusion-separation theorem."""
from __future__ import annotations

import itertools
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable

SCHEMA = "ORION.AB.GeneralFusionSeparationR9.Results.v1"
Element = tuple[int, ...]
State = tuple[Element, ...]


@dataclass(frozen=True)
class GroupCase:
    name: str
    moduli: tuple[int, ...]
    expected_zsf: int

    @property
    def zero(self) -> Element:
        return tuple(0 for _ in self.moduli)

    @property
    def elements(self) -> tuple[Element, ...]:
        return tuple(itertools.product(*(range(modulus) for modulus in self.moduli)))

    @property
    def nonzero(self) -> tuple[Element, ...]:
        return tuple(element for element in self.elements if element != self.zero)

    def add(self, left: Element, right: Element) -> Element:
        return tuple((a + b) % modulus for a, b, modulus in zip(left, right, self.moduli, strict=True))

    def total(self, state: State) -> Element:
        value = self.zero
        for letter in state:
            value = self.add(value, letter)
        return value


CASES = (
    GroupCase("C2", (2,), 1),
    GroupCase("C3", (3,), 2),
    GroupCase("C4", (4,), 3),
    GroupCase("C5", (5,), 4),
    GroupCase("C6", (6,), 5),
    GroupCase("C2^2", (2, 2), 2),
    GroupCase("C2^3", (2, 2, 2), 3),
    GroupCase("C2^4", (2, 2, 2, 2), 4),
    GroupCase("C2xC4", (2, 4), 4),
    GroupCase("C3^2", (3, 3), 4),
)


def legal_states(case: GroupCase, maximum_support: int) -> Iterable[State]:
    for support in range(1, maximum_support + 1):
        for state in itertools.combinations_with_replacement(case.nonzero, support):
            if case.total(state) != case.zero:
                yield state


def zero_sum_subset_exists(case: GroupCase, state: State) -> bool:
    for mask in range(1, 1 << len(state)):
        total = case.zero
        for index, letter in enumerate(state):
            if (mask >> index) & 1:
                total = case.add(total, letter)
        if total == case.zero:
            return True
    return False


def weak_terminal(case: GroupCase, state: State) -> bool:
    # Legal states have nonzero total, so every zero-sum subset is proper.
    return not zero_sum_subset_exists(case, state)


def fusion_successors(case: GroupCase, state: State) -> tuple[State, ...]:
    successors: set[State] = set()
    for left_index in range(len(state)):
        for right_index in range(left_index + 1, len(state)):
            merged = case.add(state[left_index], state[right_index])
            rest = [
                letter
                for index, letter in enumerate(state)
                if index not in (left_index, right_index)
            ]
            if merged != case.zero:
                rest.append(merged)
            successor = tuple(sorted(rest))
            assert successor, "a legal nonzero-total state cannot fuse to empty"
            successors.add(successor)
    return tuple(sorted(successors))


def audit_case(case: GroupCase) -> dict[str, object]:
    maximum_support = case.expected_zsf + 1

    @lru_cache(maxsize=None)
    def normal_forms(state: State) -> frozenset[State]:
        successors = fusion_successors(case, state)
        if not successors:
            return frozenset({state})
        result: set[State] = set()
        for successor in successors:
            result.update(normal_forms(successor))
        return frozenset(result)

    maximum_weak_terminal = 0
    saw_matching_terminal = False
    for state in legal_states(case, maximum_support):
        state_total = case.total(state)
        if weak_terminal(case, state):
            maximum_weak_terminal = max(maximum_weak_terminal, len(state))
            if len(state) == case.expected_zsf:
                saw_matching_terminal = True
        for successor in fusion_successors(case, state):
            assert len(successor) < len(state)
            assert case.total(successor) == state_total
        expected_normal_form: State = (state_total,)
        assert normal_forms(state) == frozenset({expected_normal_form})

    assert saw_matching_terminal
    assert maximum_weak_terminal == case.expected_zsf
    return {
        "group": case.name,
        "moduli": list(case.moduli),
        "expected_zero_sum_free_maximum": case.expected_zsf,
        "computed_weak_terminal_maximum": maximum_weak_terminal,
        "max_enumerated_support": maximum_support,
        "strong_intrinsic_support": 1,
        "certificate_waste": case.expected_zsf - 1,
        "all_fusion_paths_have_unique_singleton_normal_form": True,
        "all_moves_preserve_total_and_strictly_reduce_support": True,
        "status": "PASS",
    }


def main() -> None:
    groups = [audit_case(case) for case in CASES]
    result = {
        "schema": SCHEMA,
        "analytic_results": {
            "weak_terminal_complexity": "D(H)-1",
            "complete_fusion_intrinsic_support": 1,
            "certificate_waste": "D(H)-2",
            "elementary_two_group_family": "for C2^r the weak cap is r, the strong cap is 1, and waste is r-1",
            "confluence_reason": "strict termination plus the unique singleton containing the invariant total",
        },
        "bounded_controls": {
            "groups": groups,
            "group_count": len(groups),
            "weak_terminal_mismatches": 0,
            "semantic_preservation_mismatches": 0,
            "support_descent_mismatches": 0,
            "normal_form_mismatches": 0,
            "status": "PASS",
        },
        "authority": {
            "all_finite_group_theorem_is_analytic": True,
            "bounded_enumeration_is_implementation_corroboration": True,
            "complete_fusion_is_a_declared_production_capability": True,
            "applies_automatically_to_quantum_or_TARE_grammars": False,
            "external_replay": False,
            "grants_journal_authority": False,
        },
        "terminal": "AB_GENERAL_FUSION_SEPARATION__UNBOUNDED_CERTIFICATE_WASTE_THEOREM_AND_BOUNDED_CONTROLS_PASS",
    }
    output = Path(__file__).with_name("GENERAL_FUSION_SEPARATION_R9_RESULTS.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
