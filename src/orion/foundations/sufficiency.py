"""Exact and approximate target-sufficiency results on finite spaces."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Hashable, Mapping, Sequence

from .model import Terminal


@dataclass(frozen=True)
class FiniteInterface:
    """A committed finite interface plus its protected-read declaration."""

    name: str
    observations: Mapping[str, Hashable]
    protected_target_reads: frozenset[str] = frozenset()

    @property
    def admissible(self) -> bool:
        return not self.protected_target_reads

    def observe(self, state_id: str) -> Hashable:
        return self.observations[state_id]


@dataclass(frozen=True)
class Collision:
    left_state: str
    right_state: str
    observation: Hashable
    left_terminal: Terminal
    right_terminal: Terminal


def fibres(states: Sequence[str], interface: FiniteInterface) -> dict[Hashable, tuple[str, ...]]:
    grouped: dict[Hashable, list[str]] = defaultdict(list)
    for state_id in states:
        grouped[interface.observe(state_id)].append(state_id)
    return {key: tuple(sorted(value)) for key, value in grouped.items()}


def minimal_collision(
    states: Sequence[str],
    interface: FiniteInterface,
    target: Mapping[str, Terminal],
) -> Collision | None:
    """Return the lexicographically first indistinguishable incompatible pair."""

    for left, right in combinations(sorted(states), 2):
        if interface.observe(left) != interface.observe(right):
            continue
        if target[left] == target[right]:
            continue
        return Collision(
            left_state=left,
            right_state=right,
            observation=interface.observe(left),
            left_terminal=target[left],
            right_terminal=target[right],
        )
    return None


def is_target_sufficient(
    states: Sequence[str],
    interface: FiniteInterface,
    target: Mapping[str, Terminal],
) -> bool:
    return minimal_collision(states, interface, target) is None


def synthesise_decision_rule(
    states: Sequence[str],
    interface: FiniteInterface,
    target: Mapping[str, Terminal],
) -> dict[Hashable, Terminal]:
    if not is_target_sufficient(states, interface, target):
        raise ValueError("target is not constant on every interface fibre")
    rule: dict[Hashable, Terminal] = {}
    for state_id in states:
        observation = interface.observe(state_id)
        rule.setdefault(observation, target[state_id])
    return rule


def verifies_factorisation(
    states: Sequence[str],
    interface: FiniteInterface,
    target: Mapping[str, Terminal],
    rule: Mapping[Hashable, Terminal],
) -> bool:
    return all(rule[interface.observe(state_id)] == target[state_id] for state_id in states)


def is_fully_abstract(
    states: Sequence[str],
    interface: FiniteInterface,
    target: Mapping[str, Terminal],
) -> bool:
    for left, right in combinations(sorted(states), 2):
        same_observation = interface.observe(left) == interface.observe(right)
        same_target = target[left] == target[right]
        if same_observation != same_target:
            return False
    return True


def bayes_risk(
    states: Sequence[str],
    interface: FiniteInterface,
    target: Mapping[str, Terminal],
    probability: Mapping[str, Fraction],
) -> Fraction:
    total = sum((probability[state_id] for state_id in states), Fraction(0))
    if total != 1:
        raise ValueError(f"probabilities must sum to one, got {total}")
    grouped: dict[Hashable, dict[Terminal, Fraction]] = defaultdict(lambda: defaultdict(Fraction))
    for state_id in states:
        grouped[interface.observe(state_id)][target[state_id]] += probability[state_id]
    correct_mass = sum((max(masses.values()) for masses in grouped.values()), Fraction(0))
    return Fraction(1) - correct_mass


def is_coarsening(
    states: Sequence[str],
    fine: FiniteInterface,
    coarse: FiniteInterface,
) -> bool:
    """A coarse observation must be a function of the fine observation."""

    induced: dict[Hashable, Hashable] = {}
    for state_id in states:
        fine_value = fine.observe(state_id)
        coarse_value = coarse.observe(state_id)
        previous = induced.setdefault(fine_value, coarse_value)
        if previous != coarse_value:
            return False
    return True


def data_processing_holds(
    states: Sequence[str],
    fine: FiniteInterface,
    coarse: FiniteInterface,
    target: Mapping[str, Terminal],
    probability: Mapping[str, Fraction],
) -> bool:
    if not is_coarsening(states, fine, coarse):
        raise ValueError("coarse interface is not a function of the fine interface")
    return bayes_risk(states, coarse, target, probability) >= bayes_risk(
        states, fine, target, probability
    )
