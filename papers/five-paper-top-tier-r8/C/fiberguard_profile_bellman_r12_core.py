"""Exact finite profile and offset Bellman routines for FiberGuard R12."""
from __future__ import annotations

import functools
import itertools
from typing import Iterable, Sequence

Profile = tuple[int, ...]
States = tuple[int, ...]
Remaining = tuple[int, ...]
Regret = tuple[tuple[int, ...], ...]
Table = tuple[tuple[int, ...], ...]


def pareto_prune(profiles: Iterable[Profile]) -> tuple[Profile, ...]:
    """Keep exactly the componentwise-undominated profiles."""
    unique = sorted(set(profiles), key=lambda row: (max(row), sum(row), row))
    kept: list[Profile] = []
    for candidate in unique:
        if any(
            all(left <= right for left, right in zip(existing, candidate))
            for existing in kept
        ):
            continue
        kept = [
            existing
            for existing in kept
            if not all(left <= right for left, right in zip(candidate, existing))
        ]
        kept.append(candidate)
    return tuple(sorted(kept))


def partition(states: States, observations: Sequence[int]) -> tuple[States, ...]:
    groups: dict[int, list[int]] = {}
    for state in states:
        groups.setdefault(observations[state], []).append(state)
    return tuple(tuple(groups[key]) for key in sorted(groups))


def make_profile_solvers(regret: Regret, observations: Table, costs: Table):
    """Return Pareto-frontier and unpruned explicit-profile solvers."""

    @functools.lru_cache(maxsize=None)
    def frontier(states: States, remaining: Remaining) -> tuple[Profile, ...]:
        candidates: set[Profile] = {
            tuple(action[state] for state in states) for action in regret
        }
        for feature in remaining:
            rest = tuple(item for item in remaining if item != feature)
            children = partition(states, observations[feature])
            child_profiles = [frontier(child, rest) for child in children]
            position = {
                state: (child_index, local_index)
                for child_index, child in enumerate(children)
                for local_index, state in enumerate(child)
            }
            for choices in itertools.product(*child_profiles):
                candidates.add(
                    tuple(
                        costs[feature][state]
                        + choices[position[state][0]][position[state][1]]
                        for state in states
                    )
                )
        return pareto_prune(candidates)

    @functools.lru_cache(maxsize=None)
    def unpruned(states: States, remaining: Remaining) -> tuple[Profile, ...]:
        candidates: set[Profile] = {
            tuple(action[state] for state in states) for action in regret
        }
        for feature in remaining:
            rest = tuple(item for item in remaining if item != feature)
            children = partition(states, observations[feature])
            child_profiles = [unpruned(child, rest) for child in children]
            position = {
                state: (child_index, local_index)
                for child_index, child in enumerate(children)
                for local_index, state in enumerate(child)
            }
            for choices in itertools.product(*child_profiles):
                candidates.add(
                    tuple(
                        costs[feature][state]
                        + choices[position[state][0]][position[state][1]]
                        for state in states
                    )
                )
        return tuple(sorted(candidates))

    return frontier, unpruned


def profile_value(profiles: Sequence[Profile]) -> int:
    return min(max(profile) for profile in profiles)


def offset_value(
    regret: Regret,
    observations: Table,
    costs: Table,
    initial_states: States,
    initial_remaining: Remaining,
) -> int:
    """Exact Bellman recursion retaining the statewise sunk-cost profile."""

    @functools.lru_cache(maxsize=None)
    def value(states: States, remaining: Remaining, offset: Profile) -> int:
        best = min(
            max(offset[index] + action[state] for index, state in enumerate(states))
            for action in regret
        )
        local = {state: index for index, state in enumerate(states)}
        for feature in remaining:
            rest = tuple(item for item in remaining if item != feature)
            branch_values = []
            for child in partition(states, observations[feature]):
                child_offset = tuple(
                    offset[local[state]] + costs[feature][state] for state in child
                )
                branch_values.append(value(child, rest, child_offset))
            best = min(best, max(branch_values))
        return best

    return value(initial_states, initial_remaining, (0,) * len(initial_states))


def scalar_cell_constant_value(
    regret: Regret,
    observations: Table,
    costs: Table,
    initial_states: States,
    initial_remaining: Remaining,
) -> int:
    """Exact scalar recursion when each observation child has one charge."""

    @functools.lru_cache(maxsize=None)
    def value(states: States, remaining: Remaining) -> int:
        best = min(max(action[state] for state in states) for action in regret)
        for feature in remaining:
            rest = tuple(item for item in remaining if item != feature)
            branch_values = []
            for child in partition(states, observations[feature]):
                charges = {costs[feature][state] for state in child}
                if len(charges) != 1:
                    raise ValueError("feature cost is not constant on its cell")
                branch_values.append(next(iter(charges)) + value(child, rest))
            best = min(best, max(branch_values))
        return best

    return value(initial_states, initial_remaining)


def naive_worst_charge_value(
    regret: Regret,
    observations: Table,
    costs: Table,
    initial_states: States,
    initial_remaining: Remaining,
) -> int:
    """Upper-bound comparator replacing a varying charge by its child maximum."""

    @functools.lru_cache(maxsize=None)
    def value(states: States, remaining: Remaining) -> int:
        best = min(max(action[state] for state in states) for action in regret)
        for feature in remaining:
            rest = tuple(item for item in remaining if item != feature)
            branch_values = []
            for child in partition(states, observations[feature]):
                charge = max(costs[feature][state] for state in child)
                branch_values.append(charge + value(child, rest))
            best = min(best, max(branch_values))
        return best

    return value(initial_states, initial_remaining)


def static_value(
    regret: Regret,
    observations: Table,
    costs: Table,
    selected: tuple[int, ...],
) -> int:
    """Exact robust value of one fixed static feature set."""
    state_count = len(regret[0])
    fibres: dict[tuple[int, ...], list[int]] = {}
    state_cost = [0] * state_count
    for state in range(state_count):
        signature = tuple(observations[feature][state] for feature in selected)
        fibres.setdefault(signature, []).append(state)
        state_cost[state] = sum(costs[feature][state] for feature in selected)
    return max(
        min(
            max(state_cost[state] + action[state] for state in fibre)
            for action in regret
        )
        for fibre in fibres.values()
    )
