"""Exact rational minimax routines for randomized adaptive FiberGuard policies."""
from __future__ import annotations

import functools
import itertools
from fractions import Fraction
from typing import Iterable, Sequence

Profile = tuple[int | Fraction, ...]
Profiles = tuple[Profile, ...]
States = tuple[int, ...]
Remaining = tuple[int, ...]
Regret = tuple[tuple[int, ...], ...]
Table = tuple[tuple[int, ...], ...]


def fraction_text(value: Fraction) -> str:
    """Canonical exact text for one rational value."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _solve_square(
    matrix: Sequence[Sequence[int | Fraction]],
    right_hand_side: Sequence[int | Fraction],
) -> tuple[Fraction, ...] | None:
    """Solve one square rational system, returning None when singular."""
    size = len(matrix)
    augmented = [
        [Fraction(value) for value in row] + [Fraction(rhs)]
        for row, rhs in zip(matrix, right_hand_side)
    ]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if augmented[row][column] != 0),
            None,
        )
        if pivot is None:
            return None
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        augmented[column] = [value / pivot_value for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [
                    augmented[row][index] - factor * augmented[column][index]
                    for index in range(size + 1)
                ]
    return tuple(augmented[index][-1] for index in range(size))


def solve_zero_sum_profiles(profiles: Iterable[Profile]) -> dict[str, object]:
    """Solve min_mixture max_state expected loss exactly by support enumeration.

    The returned policy and adversary distributions form a primal/dual equilibrium.
    A basic optimal policy uses at most as many deterministic profiles as states.
    """
    rows = tuple(sorted({tuple(Fraction(value) for value in row) for row in profiles}))
    if not rows:
        raise ValueError("at least one deterministic profile is required")
    state_count = len(rows[0])
    if state_count == 0 or any(len(row) != state_count for row in rows):
        raise ValueError("profiles must have one common nonzero dimension")

    best: tuple[
        Fraction,
        tuple[int, ...],
        tuple[int, ...],
        tuple[Fraction, ...],
        tuple[Fraction, ...],
    ] | None = None
    equilibria_checked = 0
    maximum_support = min(len(rows), state_count)
    for support_size in range(1, maximum_support + 1):
        for policy_support in itertools.combinations(range(len(rows)), support_size):
            for state_support in itertools.combinations(range(state_count), support_size):
                primal_matrix = [
                    [rows[policy][state] for policy in policy_support] + [-1]
                    for state in state_support
                ]
                primal_matrix.append([1] * support_size + [0])
                primal_solution = _solve_square(
                    primal_matrix, [0] * support_size + [1]
                )
                if primal_solution is None:
                    continue
                policy_probability = primal_solution[:-1]
                upper_value = primal_solution[-1]
                if any(probability < 0 for probability in policy_probability):
                    continue

                dual_matrix = [
                    [rows[policy][state] for state in state_support] + [-1]
                    for policy in policy_support
                ]
                dual_matrix.append([1] * support_size + [0])
                dual_solution = _solve_square(
                    dual_matrix, [0] * support_size + [1]
                )
                if dual_solution is None:
                    continue
                state_probability = dual_solution[:-1]
                lower_value = dual_solution[-1]
                if any(probability < 0 for probability in state_probability):
                    continue
                if upper_value != lower_value:
                    continue

                if any(
                    sum(
                        policy_probability[index] * rows[policy][state]
                        for index, policy in enumerate(policy_support)
                    )
                    > upper_value
                    for state in range(state_count)
                ):
                    continue
                if any(
                    sum(
                        state_probability[index] * rows[policy][state]
                        for index, state in enumerate(state_support)
                    )
                    < lower_value
                    for policy in range(len(rows))
                ):
                    continue

                equilibria_checked += 1
                candidate = (
                    upper_value,
                    policy_support,
                    state_support,
                    policy_probability,
                    state_probability,
                )
                if best is None or (
                    candidate[0],
                    len(candidate[1]),
                    candidate[1],
                    candidate[2],
                ) < (best[0], len(best[1]), best[1], best[2]):
                    best = candidate

    if best is None:
        raise AssertionError("support enumeration found no zero-sum equilibrium")

    value, policy_support, state_support, policy_probability, state_probability = best
    expected_profile = tuple(
        sum(
            policy_probability[index] * rows[policy][state]
            for index, policy in enumerate(policy_support)
        )
        for state in range(state_count)
    )
    return {
        "value": value,
        "profiles": rows,
        "policy_support": policy_support,
        "policy_probability": policy_probability,
        "state_support": state_support,
        "state_probability": state_probability,
        "expected_profile": expected_profile,
        "equilibria_checked": equilibria_checked,
    }


def _partition(states: States, observations: Sequence[int]) -> tuple[States, ...]:
    groups: dict[int, list[int]] = {}
    for state in states:
        groups.setdefault(observations[state], []).append(state)
    return tuple(tuple(groups[value]) for value in sorted(groups))


def bayes_policy_value(
    regret: Regret,
    observations: Table,
    costs: Table,
    initial_states: States,
    initial_remaining: Remaining,
    initial_weight: tuple[Fraction, ...],
) -> Fraction:
    """Minimize expected total excess for one fixed adversarial state prior.

    Weights may be unnormalized. Linearity makes the recursion scalar even when
    worst-case state-dependent costs require the R12 profile state.
    """
    if len(initial_states) != len(initial_weight):
        raise ValueError("one weight is required for every initial state")

    @functools.lru_cache(maxsize=None)
    def value(
        states: States,
        remaining: Remaining,
        weight: tuple[Fraction, ...],
    ) -> Fraction:
        terminal = min(
            sum(weight[index] * action[state] for index, state in enumerate(states))
            for action in regret
        )
        best = terminal
        local = {state: index for index, state in enumerate(states)}
        for feature in remaining:
            rest = tuple(item for item in remaining if item != feature)
            acquisition = sum(
                weight[index] * costs[feature][state]
                for index, state in enumerate(states)
            )
            continuation = Fraction(0)
            for child in _partition(states, observations[feature]):
                child_weight = tuple(weight[local[state]] for state in child)
                continuation += value(child, rest, child_weight)
            best = min(best, acquisition + continuation)
        return best

    return value(initial_states, initial_remaining, initial_weight)


def randomized_static_value(
    regret: Regret,
    observations: Table,
    costs: Table,
    selected: tuple[int, ...],
) -> Fraction:
    """Exact robust expected value of one fixed static feature set."""
    state_count = len(regret[0])
    fibres: dict[tuple[int, ...], list[int]] = {}
    acquisition = [0] * state_count
    for state in range(state_count):
        signature = tuple(observations[feature][state] for feature in selected)
        fibres.setdefault(signature, []).append(state)
        acquisition[state] = sum(costs[feature][state] for feature in selected)

    values: list[Fraction] = []
    for fibre in fibres.values():
        profiles = tuple(
            tuple(acquisition[state] + action[state] for state in fibre)
            for action in regret
        )
        values.append(solve_zero_sum_profiles(profiles)["value"])
    return max(values)


def pathwise_value(profiles: Iterable[Profile]) -> Fraction:
    """Worst state and random-seed value; mixing cannot improve this quantity."""
    rows = tuple(tuple(Fraction(value) for value in row) for row in profiles)
    if not rows:
        raise ValueError("at least one profile is required")
    return min(max(row) for row in rows)
