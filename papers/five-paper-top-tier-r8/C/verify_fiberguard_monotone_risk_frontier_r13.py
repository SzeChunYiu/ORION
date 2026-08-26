#!/usr/bin/env python3
"""Finite controls for the FiberGuard monotone-risk frontier theorem.

The Markdown proof owns the all-finite theorem. This verifier exhausts complete
small profile universes, checks strict isotone separators, validates preservation
for a deterministic panel of monotone risks, and replays the unsupported robust
profile that no weighted sum can select.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
from pathlib import Path
from typing import Callable

from fiberguard_profile_bellman_r12_core import make_profile_solvers, pareto_prune

SCHEMA = "ORION.FiberGuard.MonotoneRiskFrontier.R13.v1"
SEED = 20260826
Profile = tuple[int, ...]


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def separator(anchor: Profile, profile: Profile) -> int:
    return max(max(0, right - left) for left, right in zip(anchor, profile))


def risk_panel(dimension: int) -> tuple[Callable[[Profile], int], ...]:
    risks: list[Callable[[Profile], int]] = [max, sum]
    for weights in itertools.product(range(1, 4), repeat=dimension):
        risks.append(
            lambda profile, w=weights: sum(a * b for a, b in zip(w, profile))
        )
    for threshold in range(4):
        risks.append(
            lambda profile, t=threshold: sum(
                max(0, value - t) for value in profile
            )
        )
    return tuple(risks)


def exhaustive_profile_controls() -> dict[str, int]:
    profile_sets = 0
    strict_separators = 0
    risk_equalities = 0
    grids = (
        tuple(itertools.product(range(3), repeat=2)),
        tuple(itertools.product(range(2), repeat=3)),
    )
    for grid in grids:
        risks = risk_panel(len(grid[0]))
        for mask in range(1, 1 << len(grid)):
            profiles = tuple(
                grid[index] for index in range(len(grid)) if mask & (1 << index)
            )
            frontier = pareto_prune(profiles)
            profile_sets += 1
            for anchor in frontier:
                assert separator(anchor, anchor) == 0
                assert all(
                    separator(anchor, profile) > 0
                    for profile in profiles
                    if profile != anchor
                )
                strict_separators += 1
            for risk in risks:
                assert min(map(risk, profiles)) == min(map(risk, frontier))
                risk_equalities += 1
    return {
        "profile_sets": profile_sets,
        "strict_isotone_separators": strict_separators,
        "monotone_risk_equalities": risk_equalities,
    }


def adaptive_profile_controls() -> dict[str, int]:
    rng = random.Random(SEED)
    systems = 0
    attempts = 0
    risk_equalities = 0
    while systems < 80 and attempts < 2000:
        attempts += 1
        states = rng.randint(2, 3)
        actions = rng.randint(2, 4)
        features = rng.randint(0, 2)
        regret = tuple(
            tuple(rng.randint(0, 8) for _ in range(states))
            for _ in range(actions)
        )
        observations = tuple(
            tuple(rng.randint(0, 2) for _ in range(states))
            for _ in range(features)
        )
        costs = tuple(
            tuple(rng.randint(0, 3) for _ in range(states))
            for _ in range(features)
        )
        frontier_solver, unpruned_solver = make_profile_solvers(
            regret, observations, costs
        )
        subject = tuple(range(states))
        remaining = tuple(range(features))
        frontier = frontier_solver(subject, remaining)
        unpruned = unpruned_solver(subject, remaining)
        if len(unpruned) > 18:
            continue
        assert set(frontier) == set(pareto_prune(unpruned))
        for risk in risk_panel(states):
            assert min(map(risk, unpruned)) == min(map(risk, frontier))
            risk_equalities += 1
        systems += 1
    assert systems == 80
    return {
        "adaptive_systems": systems,
        "generation_attempts": attempts,
        "maximum_unpruned_profiles": 18,
        "monotone_risk_equalities": risk_equalities,
    }


def unsupported_scalarization_control() -> dict[str, object]:
    profiles = ((0, 3), (3, 0), (2, 2))
    robust_values = tuple(max(profile) for profile in profiles)
    assert robust_values == (3, 3, 2)
    rejected_weights = 0
    for numerator in range(101):
        weight = numerator / 100
        values = tuple(
            weight * profile[0] + (1 - weight) * profile[1]
            for profile in profiles
        )
        assert values[2] > min(values[0], values[1])
        rejected_weights += 1
    return {
        "profiles": [list(profile) for profile in profiles],
        "deterministic_robust_values": list(robust_values),
        "unique_robust_optimum_index": 2,
        "weighted_sum_grid_points_rejecting_robust_optimum": rejected_weights,
    }


def run() -> dict[str, object]:
    result: dict[str, object] = {
        "schema": SCHEMA,
        "status": "FIBERGUARD_MONOTONE_RISK_FRONTIER_R13_PASS",
        "exhaustive_profile_controls": exhaustive_profile_controls(),
        "adaptive_profile_controls": adaptive_profile_controls(),
        "unsupported_scalarization_control": unsupported_scalarization_control(),
        "authority": {
            "universal_theorem_from_computation": False,
            "finite_controls_exact": True,
            "generic_pareto_theory_claimed_novel": False,
            "randomized_minimax_claimed_here": False,
            "heldout_transfer_established": False,
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
    Path(__file__).with_name("MONOTONE_RISK_FRONTIER_R13_RESULTS.json").write_text(
        text, encoding="utf-8"
    )
    print("FIBERGUARD_MONOTONE_RISK_FRONTIER_R13_PASS")
    print(text, end="")


if __name__ == "__main__":
    main()
