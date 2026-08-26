#!/usr/bin/env python3
"""Finite controls for FiberGuard R13 risk-complete profile frontiers.

The Markdown proofs own the theorem authority. This verifier independently checks
finite Pareto-separation, exact primal/dual randomized minimax certificates,
unsupported robust profiles, adaptive-profile integration, and deterministic vs
randomized/pathwise gap controls.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
from fractions import Fraction
from pathlib import Path
from typing import Callable, Iterable, Sequence

from fiberguard_profile_bellman_r12_core import make_profile_solvers, pareto_prune

SCHEMA = "ORION.FiberGuard.RiskCompleteFrontier.R13.v1"
SEED = 20260826
Profile = tuple[int, ...]


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def solve_square(
    a: Sequence[Sequence[Fraction]], b: Sequence[Fraction]
) -> tuple[Fraction, ...] | None:
    n = len(a)
    if n == 0 or len(b) != n or any(len(row) != n for row in a):
        raise ValueError("expected a nonempty square system")
    aug = [list(row) + [rhs] for row, rhs in zip(a, b)]
    for col in range(n):
        pivot = next((row for row in range(col, n) if aug[row][col] != 0), None)
        if pivot is None:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        aug[col] = [entry / scale for entry in aug[col]]
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            if factor:
                aug[row] = [
                    left - factor * right for left, right in zip(aug[row], aug[col])
                ]
    return tuple(aug[row][-1] for row in range(n))


def expected_profile(
    profiles: Sequence[Profile], support: Sequence[int], weights: Sequence[Fraction]
) -> tuple[Fraction, ...]:
    states = len(profiles[0])
    return tuple(
        sum(weights[k] * profiles[j][i] for k, j in enumerate(support))
        for i in range(states)
    )


def randomized_minimax_primal(profiles: Sequence[Profile]) -> dict[str, object]:
    if not profiles:
        raise ValueError("empty profile set")
    m, n = len(profiles), len(profiles[0])
    best: tuple[
        Fraction, tuple[int, ...], tuple[Fraction, ...], tuple[Fraction, ...]
    ] | None = None
    for size in range(1, min(m, n) + 1):
        for support in itertools.combinations(range(m), size):
            for active_states in itertools.combinations(range(n), size):
                matrix: list[list[Fraction]] = [
                    [Fraction(1)] * size + [Fraction(0)]
                ]
                rhs = [Fraction(1)]
                for state in active_states:
                    matrix.append(
                        [Fraction(profiles[j][state]) for j in support]
                        + [Fraction(-1)]
                    )
                    rhs.append(Fraction(0))
                solution = solve_square(matrix, rhs)
                if solution is None:
                    continue
                weights, value = solution[:-1], solution[-1]
                if any(weight < 0 for weight in weights) or sum(weights) != 1:
                    continue
                exp = expected_profile(profiles, support, weights)
                if any(loss > value for loss in exp) or max(exp) != value:
                    continue
                candidate = (value, support, weights, exp)
                if best is None or candidate < best:
                    best = candidate
    if best is None:
        raise AssertionError("no primal basic feasible solution found")
    value, support, weights, exp = best
    return {
        "value": value,
        "support": support,
        "weights": weights,
        "expected_profile": exp,
    }


def randomized_minimax_dual(profiles: Sequence[Profile]) -> dict[str, object]:
    if not profiles:
        raise ValueError("empty profile set")
    m, n = len(profiles), len(profiles[0])
    best: tuple[
        Fraction, tuple[int, ...], tuple[Fraction, ...], tuple[Fraction, ...]
    ] | None = None
    for size in range(1, min(m, n) + 1):
        for state_support in itertools.combinations(range(n), size):
            for active_policies in itertools.combinations(range(m), size):
                matrix: list[list[Fraction]] = [
                    [Fraction(1)] * size + [Fraction(0)]
                ]
                rhs = [Fraction(1)]
                for policy in active_policies:
                    matrix.append(
                        [
                            Fraction(profiles[policy][state])
                            for state in state_support
                        ]
                        + [Fraction(-1)]
                    )
                    rhs.append(Fraction(0))
                solution = solve_square(matrix, rhs)
                if solution is None:
                    continue
                weights, value = solution[:-1], solution[-1]
                if any(weight < 0 for weight in weights) or sum(weights) != 1:
                    continue
                policy_losses = tuple(
                    sum(
                        weights[k] * profiles[policy][state]
                        for k, state in enumerate(state_support)
                    )
                    for policy in range(m)
                )
                if any(loss < value for loss in policy_losses) or min(
                    policy_losses
                ) != value:
                    continue
                candidate = (value, state_support, weights, policy_losses)
                if best is None or candidate > best:
                    best = candidate
    if best is None:
        raise AssertionError("no dual basic feasible solution found")
    value, state_support, weights, policy_losses = best
    return {
        "value": value,
        "state_support": state_support,
        "weights": weights,
        "policy_losses": policy_losses,
    }


def fraction_text(value: Fraction) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def fraction_list(values: Iterable[Fraction]) -> list[str]:
    return [fraction_text(value) for value in values]


def separator(anchor: Profile, profile: Profile) -> int:
    return max(max(0, right - left) for left, right in zip(anchor, profile))


def monotone_risk_panel(dimension: int) -> tuple[Callable[[Profile], int], ...]:
    risks: list[Callable[[Profile], int]] = [max, sum]
    for weights in itertools.product(range(1, 4), repeat=dimension):
        risks.append(lambda p, w=weights: sum(a * b for a, b in zip(w, p)))
    for threshold in range(4):
        risks.append(lambda p, t=threshold: sum(max(0, x - t) for x in p))
    return tuple(risks)


def exhaustive_frontier_controls() -> dict[str, int]:
    sets_checked = 0
    pareto_points_checked = 0
    risk_equalities_checked = 0
    grids = [
        tuple(itertools.product(range(3), repeat=2)),
        tuple(itertools.product(range(2), repeat=3)),
    ]
    for grid in grids:
        dimension = len(grid[0])
        risks = monotone_risk_panel(dimension)
        for mask in range(1, 1 << len(grid)):
            profiles = tuple(
                grid[index] for index in range(len(grid)) if mask & (1 << index)
            )
            frontier = pareto_prune(profiles)
            sets_checked += 1
            for point in frontier:
                assert separator(point, point) == 0
                assert all(
                    separator(point, other) > 0
                    for other in profiles
                    if other != point
                )
                pareto_points_checked += 1
            for risk in risks:
                assert min(map(risk, profiles)) == min(map(risk, frontier))
                risk_equalities_checked += 1
    return {
        "profile_sets_checked": sets_checked,
        "pareto_points_with_strict_separator": pareto_points_checked,
        "monotone_risk_equalities_checked": risk_equalities_checked,
    }


def generated_game_controls() -> dict[str, int]:
    rng = random.Random(SEED)
    games = 0
    primal_dual_equalities = 0
    support_bound_checks = 0
    pareto_convex_hull_equalities = 0
    for _ in range(300):
        states = rng.randint(2, 4)
        policies = rng.randint(2, 6)
        profiles = tuple(
            sorted(
                {
                    tuple(rng.randint(0, 8) for _ in range(states))
                    for _ in range(policies)
                }
            )
        )
        if len(profiles) < 2:
            continue
        frontier = pareto_prune(profiles)
        primal = randomized_minimax_primal(profiles)
        dual = randomized_minimax_dual(profiles)
        frontier_primal = randomized_minimax_primal(frontier)
        assert primal["value"] == dual["value"]
        assert primal["value"] == frontier_primal["value"]
        assert len(primal["support"]) <= states
        games += 1
        primal_dual_equalities += 1
        support_bound_checks += 1
        pareto_convex_hull_equalities += 1
    return {
        "generated_games": games,
        "primal_dual_equalities": primal_dual_equalities,
        "support_bound_checks": support_bound_checks,
        "pareto_convex_hull_equalities": pareto_convex_hull_equalities,
    }


def generated_adaptive_controls() -> dict[str, int]:
    rng = random.Random(SEED + 1)
    systems = 0
    attempts = 0
    full_vs_frontier_randomized_equalities = 0
    universal_separator_checks = 0
    while systems < 60 and attempts < 1000:
        attempts += 1
        state_count = rng.randint(2, 3)
        action_count = rng.randint(2, 4)
        feature_count = rng.randint(0, 2)
        regret = tuple(
            tuple(rng.randint(0, 8) for _ in range(state_count))
            for _ in range(action_count)
        )
        observations = tuple(
            tuple(rng.randint(0, 2) for _ in range(state_count))
            for _ in range(feature_count)
        )
        costs = tuple(
            tuple(rng.randint(0, 3) for _ in range(state_count))
            for _ in range(feature_count)
        )
        frontier_solver, unpruned_solver = make_profile_solvers(
            regret, observations, costs
        )
        states = tuple(range(state_count))
        remaining = tuple(range(feature_count))
        frontier = frontier_solver(states, remaining)
        unpruned = unpruned_solver(states, remaining)
        # Keep the exact LP differential bounded and deterministic. Larger finite
        # systems are covered by the analytic dominance proof in R12/R13.
        if len(unpruned) > 12:
            continue
        assert set(frontier) == set(pareto_prune(unpruned))
        assert randomized_minimax_primal(frontier)[
            "value"
        ] == randomized_minimax_primal(unpruned)["value"]
        for point in frontier:
            assert all(
                separator(point, other) > 0
                for other in unpruned
                if other != point
            )
            universal_separator_checks += 1
        systems += 1
        full_vs_frontier_randomized_equalities += 1
    assert systems == 60
    return {
        "generated_adaptive_systems": systems,
        "generation_attempts": attempts,
        "maximum_unpruned_profiles_admitted": 12,
        "full_vs_frontier_randomized_equalities": (
            full_vs_frontier_randomized_equalities
        ),
        "adaptive_frontier_separator_checks": universal_separator_checks,
    }


def hostile_examples() -> dict[str, object]:
    unsupported = ((0, 3), (3, 0), (2, 2))
    deterministic_value = min(max(profile) for profile in unsupported)
    primal = randomized_minimax_primal(unsupported)
    dual = randomized_minimax_dual(unsupported)
    assert deterministic_value == 2
    assert primal["value"] == dual["value"] == Fraction(3, 2)
    assert set(primal["support"]) == {0, 1}
    for numerator in range(101):
        w = Fraction(numerator, 100)
        weighted = tuple(w * p[0] + (1 - w) * p[1] for p in unsupported)
        assert weighted[2] > min(weighted[0], weighted[1])

    gaps = []
    for states in range(1, 13):
        profiles = tuple(
            tuple(1 if i == j else 0 for i in range(states))
            for j in range(states)
        )
        deterministic = min(max(profile) for profile in profiles)
        assert deterministic == 1
        # Every mixture has coordinate sum one, so its maximum coordinate is at
        # least 1/n; the uniform mixture attains equality. Use the exact LP solver
        # through n=6 as an independent finite control, then the displayed identity.
        if states <= 6:
            mixed = randomized_minimax_primal(profiles)
            assert mixed["value"] == Fraction(1, states)
            assert len(mixed["support"]) == states
        else:
            mixed = {
                "value": Fraction(1, states),
                "support": tuple(range(states)),
                "weights": tuple(Fraction(1, states) for _ in range(states)),
            }
        pathwise = min(max(profile) for profile in profiles)
        assert pathwise == deterministic
        gaps.append(
            {
                "states": states,
                "deterministic_value": deterministic,
                "worst_state_expected_randomized_value": fraction_text(
                    mixed["value"]
                ),
                "pathwise_randomized_value": pathwise,
                "ratio": states,
            }
        )
    return {
        "unsupported_profile_set": [list(row) for row in unsupported],
        "unsupported_deterministic_minimax_value": deterministic_value,
        "unsupported_randomized_value": fraction_text(primal["value"]),
        "unsupported_primal_policy_support": list(primal["support"]),
        "unsupported_primal_weights": fraction_list(primal["weights"]),
        "unsupported_dual_state_support": list(dual["state_support"]),
        "unsupported_dual_weights": fraction_list(dual["weights"]),
        "weighted_sum_grid_points_rejecting_robust_profile": 101,
        "randomization_gap_family": gaps,
    }


def run() -> dict[str, object]:
    result: dict[str, object] = {
        "schema": SCHEMA,
        "status": "FIBERGUARD_RISK_COMPLETE_FRONTIER_R13_PASS",
        "frontier_controls": exhaustive_frontier_controls(),
        "game_controls": generated_game_controls(),
        "adaptive_controls": generated_adaptive_controls(),
        "hostile_examples": hostile_examples(),
        "authority": {
            "analytic_theorems_from_computation": False,
            "finite_controls_exact": True,
            "generic_pareto_theory_claimed_novel": False,
            "generic_minimax_duality_claimed_novel": False,
            "randomized_pathwise_certificate_improvement": False,
            "adaptive_aslib_experiment_executed": False,
            "external_novelty_review_complete": False,
            "journal_authority": False,
        },
    }
    payload = canonical_json(result).encode()
    result["content_sha256"] = hashlib.sha256(payload).hexdigest()
    return result


def main() -> None:
    result = run()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    output = Path(__file__).with_name("RISK_COMPLETE_FRONTIER_R13_RESULTS.json")
    output.write_text(text, encoding="utf-8")
    print("FIBERGUARD_RISK_COMPLETE_FRONTIER_R13_PASS")
    print(text, end="")


if __name__ == "__main__":
    main()
