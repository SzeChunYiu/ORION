"""Exact joint-profile routines for AnonymizedMethod paired learned/fallback routing.

This module is intentionally standard-library only.  It enumerates the actual
legal learned/fallback pairs and route-observation maps, rather than inferring a
joint policy language from separate marginal action sets.
"""
from __future__ import annotations

import itertools
from fractions import Fraction
from typing import Iterable, Sequence

Profile = tuple[int | Fraction, ...]
Profiles = tuple[Profile, ...]
Pair = tuple[int, int]


def _solve_square(
    matrix: Sequence[Sequence[int | Fraction]],
    rhs: Sequence[int | Fraction],
) -> tuple[Fraction, ...] | None:
    """Solve one square rational system; return None when singular."""
    n = len(matrix)
    aug = [
        [Fraction(value) for value in row] + [Fraction(target)]
        for row, target in zip(matrix, rhs)
    ]
    for column in range(n):
        pivot = next(
            (row for row in range(column, n) if aug[row][column] != 0),
            None,
        )
        if pivot is None:
            return None
        aug[column], aug[pivot] = aug[pivot], aug[column]
        scale = aug[column][column]
        aug[column] = [value / scale for value in aug[column]]
        for row in range(n):
            if row == column:
                continue
            factor = aug[row][column]
            if factor:
                aug[row] = [
                    aug[row][index] - factor * aug[column][index]
                    for index in range(n + 1)
                ]
    return tuple(aug[index][-1] for index in range(n))


def pareto_prune(profiles: Iterable[Profile]) -> Profiles:
    """Return the componentwise nondominated deterministic profiles."""
    rows = sorted({tuple(Fraction(v) for v in row) for row in profiles})
    kept: list[Profile] = []
    for candidate in rows:
        if any(
            all(left <= right for left, right in zip(existing, candidate))
            for existing in rows
            if existing != candidate
        ):
            continue
        kept.append(candidate)
    return tuple(kept)


def route_cells(observation: Sequence[int]) -> tuple[int, ...]:
    """Canonical attained route-observation labels."""
    return tuple(sorted(set(observation)))


def enumerate_joint_route_profiles(
    learned: Sequence[Profile],
    fallback: Sequence[Profile],
    observation: Sequence[int],
    learned_acquisition: Sequence[int | Fraction],
    *,
    timing: str,
    legal_pairs: Iterable[Pair] | None = None,
) -> Profiles:
    """Enumerate every legal deterministic paired route profile.

    `timing="post"` means the learned representation was acquired before the
    route decision, so its charge is sunk on both learned and fallback paths.
    `timing="pre"` means fallback routing happens before learned acquisition,
    so a fallback path does not pay the learned acquisition charge.
    """
    if timing not in {"pre", "post"}:
        raise ValueError("timing must be 'pre' or 'post'")
    state_count = len(observation)
    if state_count == 0:
        raise ValueError("at least one state is required")
    if len(learned_acquisition) != state_count:
        raise ValueError("one learned acquisition charge is required per state")
    if any(len(row) != state_count for row in tuple(learned) + tuple(fallback)):
        raise ValueError("all profiles must have the observation dimension")

    pairs = (
        tuple(itertools.product(range(len(learned)), range(len(fallback))))
        if legal_pairs is None
        else tuple(sorted(set(legal_pairs)))
    )
    if not pairs:
        raise ValueError("at least one legal learned/fallback pair is required")
    labels = route_cells(observation)
    label_position = {label: index for index, label in enumerate(labels)}
    profiles: set[Profile] = set()
    for learned_index, fallback_index in pairs:
        if not (0 <= learned_index < len(learned)):
            raise ValueError("learned pair index out of range")
        if not (0 <= fallback_index < len(fallback)):
            raise ValueError("fallback pair index out of range")
        for route_bits in itertools.product((0, 1), repeat=len(labels)):
            row: list[Fraction] = []
            for state, label in enumerate(observation):
                use_fallback = route_bits[label_position[label]] == 1
                charge = Fraction(learned_acquisition[state])
                if use_fallback:
                    value = Fraction(fallback[fallback_index][state])
                    if timing == "post":
                        value += charge
                else:
                    value = charge + Fraction(learned[learned_index][state])
                row.append(value)
            profiles.add(tuple(row))
    return tuple(sorted(profiles))


def deterministic_value(profiles: Iterable[Profile]) -> Fraction:
    rows = tuple(tuple(Fraction(v) for v in row) for row in profiles)
    if not rows:
        raise ValueError("at least one profile is required")
    return min(max(row) for row in rows)


def solve_zero_sum_profiles(profiles: Iterable[Profile]) -> dict[str, object]:
    """Solve min_mixture max_state expected loss exactly.

    Support enumeration returns matching primal and dual rational certificates.
    Some optimal basic policy uses at most the number of states profiles.
    """
    rows = tuple(sorted({tuple(Fraction(v) for v in row) for row in profiles}))
    if not rows:
        raise ValueError("at least one profile is required")
    m = len(rows[0])
    if m == 0 or any(len(row) != m for row in rows):
        raise ValueError("profiles must share one nonzero dimension")

    best: tuple[
        Fraction,
        tuple[int, ...],
        tuple[int, ...],
        tuple[Fraction, ...],
        tuple[Fraction, ...],
    ] | None = None
    equilibria = 0
    for support_size in range(1, min(len(rows), m) + 1):
        for policy_support in itertools.combinations(range(len(rows)), support_size):
            for state_support in itertools.combinations(range(m), support_size):
                primal_matrix = [
                    [rows[policy][state] for policy in policy_support] + [-1]
                    for state in state_support
                ]
                primal_matrix.append([1] * support_size + [0])
                primal = _solve_square(primal_matrix, [0] * support_size + [1])
                if primal is None:
                    continue
                policy_probability = primal[:-1]
                upper = primal[-1]
                if any(value < 0 for value in policy_probability):
                    continue

                dual_matrix = [
                    [rows[policy][state] for state in state_support] + [-1]
                    for policy in policy_support
                ]
                dual_matrix.append([1] * support_size + [0])
                dual = _solve_square(dual_matrix, [0] * support_size + [1])
                if dual is None:
                    continue
                state_probability = dual[:-1]
                lower = dual[-1]
                if any(value < 0 for value in state_probability):
                    continue
                if lower != upper:
                    continue
                if any(
                    sum(
                        policy_probability[index] * rows[policy][state]
                        for index, policy in enumerate(policy_support)
                    )
                    > upper
                    for state in range(m)
                ):
                    continue
                if any(
                    sum(
                        state_probability[index] * rows[policy][state]
                        for index, state in enumerate(state_support)
                    )
                    < lower
                    for policy in range(len(rows))
                ):
                    continue
                equilibria += 1
                candidate = (
                    upper,
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
        raise AssertionError("no exact equilibrium found")
    value, policy_support, state_support, policy_probability, state_probability = best
    expected = tuple(
        sum(
            policy_probability[index] * rows[policy][state]
            for index, policy in enumerate(policy_support)
        )
        for state in range(m)
    )
    return {
        "value": value,
        "profiles": rows,
        "policy_support": policy_support,
        "policy_probability": policy_probability,
        "state_support": state_support,
        "state_probability": state_probability,
        "expected_profile": expected,
        "equilibria_checked": equilibria,
    }


def convexly_dominates(profiles: Iterable[Profile], target: Profile) -> bool:
    """Whether a convex combination of `profiles` is <= `target` coordinatewise."""
    rows = tuple(sorted({tuple(Fraction(v) for v in row) for row in profiles}))
    target_row = tuple(Fraction(v) for v in target)
    if not rows:
        return False
    m = len(target_row)
    if any(len(row) != m for row in rows):
        raise ValueError("dimension mismatch")
    maximum_support = min(len(rows), m + 1)
    for support_size in range(1, maximum_support + 1):
        for support in itertools.combinations(range(len(rows)), support_size):
            if support_size == 1:
                probability = (Fraction(1),)
                active_sets = ((),)
            else:
                active_sets = itertools.combinations(range(m), support_size - 1)
            for active in active_sets:
                if support_size == 1:
                    solution = probability
                else:
                    matrix = [[1] * support_size]
                    rhs = [1]
                    for state in active:
                        matrix.append([rows[index][state] for index in support])
                        rhs.append(target_row[state])
                    solution = _solve_square(matrix, rhs)
                    if solution is None:
                        continue
                if any(value < 0 for value in solution):
                    continue
                mixture = tuple(
                    sum(solution[index] * rows[policy][state] for index, policy in enumerate(support))
                    for state in range(m)
                )
                if all(left <= right for left, right in zip(mixture, target_row)):
                    return True
    return False


def lower_image_equivalent(left: Iterable[Profile], right: Iterable[Profile]) -> bool:
    """Exact equality of conv(P)+R_+^F for two finite profile sets."""
    left_rows = tuple(sorted({tuple(Fraction(v) for v in row) for row in left}))
    right_rows = tuple(sorted({tuple(Fraction(v) for v in row) for row in right}))
    return all(convexly_dominates(right_rows, row) for row in left_rows) and all(
        convexly_dominates(left_rows, row) for row in right_rows
    )


def bayes_value(profiles: Iterable[Profile], prior: Sequence[int | Fraction]) -> Fraction:
    """Exact lower envelope under one nonnegative state prior."""
    weights = tuple(Fraction(v) for v in prior)
    if sum(weights) <= 0 or any(v < 0 for v in weights):
        raise ValueError("prior weights must be nonnegative and nonzero")
    return min(
        sum(weight * Fraction(value) for weight, value in zip(weights, row))
        for row in profiles
    ) / sum(weights)


def fraction_text(value: int | Fraction) -> str:
    rational = Fraction(value)
    if rational.denominator == 1:
        return str(rational.numerator)
    return f"{rational.numerator}/{rational.denominator}"
