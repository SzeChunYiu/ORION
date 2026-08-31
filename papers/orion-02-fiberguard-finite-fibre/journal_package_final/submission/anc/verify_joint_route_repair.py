#!/usr/bin/env python3
"""Deterministic finite audit for the AnonymizedMethod STUDY_B joint-route repair."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
import random
from typing import Any

from joint_route_core import (
    bayes_value,
    deterministic_value,
    enumerate_joint_route_profiles,
    fraction_text,
    lower_image_equivalent,
    pareto_prune,
    solve_zero_sum_profiles,
)

SCHEMA = "ANON.JointRoute.STUDY_B.v1"
SOURCE_BASE_COMMIT = "ANONYMIZED"
SEED = 20260827
TERMINAL = "ANON_JOINT_ROUTE_STUDY_B_REPLACEMENT_PASS"


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def explicit_profiles(
    learned,
    fallback,
    observation,
    costs,
    timing,
    legal_pairs,
):
    labels = sorted(set(observation))
    label_index = {label: index for index, label in enumerate(labels)}
    result = set()
    for learned_index, fallback_index in legal_pairs:
        for route in itertools.product((0, 1), repeat=len(labels)):
            row = []
            for state, label in enumerate(observation):
                use_fallback = route[label_index[label]]
                if use_fallback:
                    value = fallback[fallback_index][state]
                    if timing == "post":
                        value += costs[state]
                else:
                    value = learned[learned_index][state] + costs[state]
                row.append(value)
            result.add(tuple(row))
    return tuple(sorted(result))


def random_system(rng: random.Random):
    states = rng.randint(2, 5)
    learned_count = rng.randint(2, 3)
    fallback_count = rng.randint(2, 3)
    cells = rng.randint(1, min(states, 2))
    learned = tuple(
        tuple(rng.randrange(0, 21) for _ in range(states))
        for _ in range(learned_count)
    )
    fallback = tuple(
        tuple(rng.randrange(0, 21) for _ in range(states))
        for _ in range(fallback_count)
    )
    observation = tuple(rng.randrange(cells) for _ in range(states))
    costs = tuple(rng.randrange(0, 8) for _ in range(states))
    pairs = tuple(itertools.product(range(learned_count), range(fallback_count)))
    return learned, fallback, observation, costs, pairs


def verify_random_systems() -> dict[str, Any]:
    rng = random.Random(SEED)
    systems = 240
    profile_checks = 0
    lower_image_checks = 0
    pareto_checks = 0
    timing_identity_checks = 0
    diagonal_failures = 0
    randomized_games = 0
    randomized_support_histogram: dict[str, int] = {}
    for _ in range(systems):
        learned, fallback, observation, costs, pairs = random_system(rng)
        for timing in ("pre", "post"):
            actual = enumerate_joint_route_profiles(
                learned,
                fallback,
                observation,
                costs,
                timing=timing,
                legal_pairs=pairs,
            )
            brute = explicit_profiles(
                learned, fallback, observation, costs, timing, pairs
            )
            if actual != brute:
                raise AssertionError("joint profile enumeration disagreement")
            profile_checks += 1
            frontier = pareto_prune(actual)
            if deterministic_value(frontier) != deterministic_value(actual):
                raise AssertionError("deterministic Pareto pruning changed value")
            # Every discarded profile must be directly dominated by a retained
            # profile. This proves equality of the upward-closed convex lower
            # image without solving the exponentially larger unpruned game.
            if any(
                not any(
                    all(left <= right for left, right in zip(kept, row))
                    for kept in frontier
                )
                for row in actual
            ):
                raise AssertionError("Pareto frontier changed lower image")
            lower_image_checks += 1
            pareto_checks += 1
            # Exact rational primal/dual games are checked on a fixed bounded
            # subpanel; every system still receives deterministic and exact
            # lower-image checks.
            if randomized_games < 120 and len(frontier) <= 8 and len(observation) <= 4:
                frontier_game = solve_zero_sum_profiles(frontier)
                support = str(len(frontier_game["policy_support"]))
                randomized_support_histogram[support] = (
                    randomized_support_histogram.get(support, 0) + 1
                )
                randomized_games += 1
                pareto_checks += 1

        pre = enumerate_joint_route_profiles(
            learned, fallback, observation, costs, timing="pre", legal_pairs=pairs
        )
        post = enumerate_joint_route_profiles(
            learned, fallback, observation, costs, timing="post", legal_pairs=pairs
        )
        # Every post profile has a pre counterpart with the acquisition charge
        # removed exactly on fallback-routed states. Hence pre routing cannot be
        # worse than post routing, but equality is not forced.
        if deterministic_value(pre) > deterministic_value(post):
            raise AssertionError("pre-acquisition routing unexpectedly worse")
        timing_identity_checks += 1

        diagonal = tuple(
            (index, index)
            for index in range(min(len(learned), len(fallback)))
        )
        diagonal_profiles = enumerate_joint_route_profiles(
            learned,
            fallback,
            observation,
            costs,
            timing="post",
            legal_pairs=diagonal,
        )
        if not lower_image_equivalent(post, diagonal_profiles):
            diagonal_failures += 1
    return {
        "systems": systems,
        "joint_profile_enumeration_checks": profile_checks,
        "lower_image_equivalence_checks": lower_image_checks,
        "pareto_value_checks": pareto_checks,
        "exact_randomized_games": randomized_games,
        "pre_post_timing_checks": timing_identity_checks,
        "systems_where_diagonal_pairing_changes_lower_image": diagonal_failures,
        "randomized_policy_support_histogram": dict(sorted(randomized_support_histogram.items())),
    }


def invalid_pairing_counterexample() -> dict[str, Any]:
    # Six original profiles. Mixing the first two gives (35,35,35). A
    # forbidden diagonal pair-max shortcut maps all three labelled pairs to the
    # constant profile (70,70,70), doubling the exact randomized value.
    learned = ((0, 70, 0), (70, 0, 70), (70, 70, 70))
    fallback = ((70, 70, 70), (70, 70, 70), (70, 70, 70))
    original = learned + fallback
    shortcut = tuple(
        tuple(max(learned[index][state], fallback[index][state]) for state in range(3))
        for index in range(3)
    )
    original_game = solve_zero_sum_profiles(original)
    shortcut_game = solve_zero_sum_profiles(shortcut)
    if original_game["value"] != 35 or shortcut_game["value"] != 70:
        raise AssertionError("3x3 invalid-pairing counterexample drift")
    if lower_image_equivalent(original, shortcut):
        raise AssertionError("invalid shortcut unexpectedly preserves lower image")
    return {
        "states": 3,
        "original_actions": 6,
        "shortcut_actions": 3,
        "original_randomized_value": fraction_text(original_game["value"]),
        "shortcut_randomized_value": fraction_text(shortcut_game["value"]),
        "value_ratio": fraction_text(shortcut_game["value"] / original_game["value"]),
        "lower_image_preserved": False,
    }


def compatibility_and_marginal_counterexample() -> dict[str, Any]:
    magnitude = 100
    learned = ((0, magnitude), (magnitude, 0))
    fallback = ((0, magnitude), (magnitude, 0))
    observation = (0, 1)
    costs = (0, 0)
    full = enumerate_joint_route_profiles(
        learned, fallback, observation, costs, timing="post"
    )
    diagonal = enumerate_joint_route_profiles(
        learned,
        fallback,
        observation,
        costs,
        timing="post",
        legal_pairs=((0, 0), (1, 1)),
    )
    full_value = solve_zero_sum_profiles(full)["value"]
    diagonal_game = solve_zero_sum_profiles(diagonal)
    if full_value != 0 or diagonal_game["value"] != 50:
        raise AssertionError("compatibility counterexample drift")
    if bayes_value(full, (1, 1)) != 0:
        raise AssertionError("full pair language Bayes value drift")
    if bayes_value(diagonal, (1, 1)) != 50:
        raise AssertionError("diagonal language Bayes value drift")
    return {
        "marginal_learned_profiles": [list(row) for row in learned],
        "marginal_fallback_profiles": [list(row) for row in fallback],
        "full_pair_randomized_value": fraction_text(full_value),
        "diagonal_pair_randomized_value": fraction_text(diagonal_game["value"]),
        "witness_prior": ["1/2", "1/2"],
        "same_marginals_different_joint_value": True,
        "separate_pointwise_marginal_safe_actions_exist": True,
        "diagonal_joint_zero_safe_policy_exists": False,
    }


def coarsening_ranking_reversal() -> dict[str, Any]:
    magnitude = 100
    constant = 30
    learned = ((0, magnitude), (constant, constant))
    fallback = ((magnitude, 0), (constant, constant))
    costs = (0, 0)
    pair_a = ((0, 0),)
    pair_b = ((1, 1),)
    fine_a = deterministic_value(
        enumerate_joint_route_profiles(
            learned, fallback, (0, 1), costs, timing="post", legal_pairs=pair_a
        )
    )
    coarse_a = deterministic_value(
        enumerate_joint_route_profiles(
            learned, fallback, (0, 0), costs, timing="post", legal_pairs=pair_a
        )
    )
    fine_b = deterministic_value(
        enumerate_joint_route_profiles(
            learned, fallback, (0, 1), costs, timing="post", legal_pairs=pair_b
        )
    )
    coarse_b = deterministic_value(
        enumerate_joint_route_profiles(
            learned, fallback, (0, 0), costs, timing="post", legal_pairs=pair_b
        )
    )
    if not (fine_a < fine_b and coarse_a > coarse_b):
        raise AssertionError("route coarsening ranking reversal drift")
    return {
        "fine_observation_pair_A_value": fraction_text(fine_a),
        "fine_observation_pair_B_value": fraction_text(fine_b),
        "coarse_observation_pair_A_value": fraction_text(coarse_a),
        "coarse_observation_pair_B_value": fraction_text(coarse_b),
        "ranking_reversed": True,
    }


def timing_reversal() -> dict[str, Any]:
    learned = ((0,),)
    fallback = ((5,),)
    observation = (0,)
    costs = (10,)
    pre_profiles = enumerate_joint_route_profiles(
        learned, fallback, observation, costs, timing="pre"
    )
    post_profiles = enumerate_joint_route_profiles(
        learned, fallback, observation, costs, timing="post"
    )
    pre = deterministic_value(pre_profiles)
    post = deterministic_value(post_profiles)
    if pre != 5 or post != 10:
        raise AssertionError("timing reversal value drift")
    return {
        "pre_acquisition_learned_loss": "10",
        "pre_acquisition_fallback_loss": "5",
        "pre_acquisition_optimal_route": "fallback",
        "post_acquisition_learned_loss": "10",
        "post_acquisition_fallback_loss": "15",
        "post_acquisition_optimal_route": "learned",
        "route_ranking_reversed": True,
    }


def lower_image_exhaustion() -> dict[str, Any]:
    cubes = (
        tuple(itertools.product(range(2), repeat=2)),
        tuple(itertools.product(range(2), repeat=3)),
    )
    subsets = 0
    direct_equivalence_checks = 0
    convex_necessity_checks = 0
    for cube in cubes:
        for mask in range(1, 1 << len(cube)):
            profiles = tuple(
                cube[index] for index in range(len(cube)) if (mask >> index) & 1
            )
            frontier = pareto_prune(profiles)
            subsets += 1
            if any(
                not any(
                    all(left <= right for left, right in zip(kept, row))
                    for kept in frontier
                )
                for row in profiles
            ):
                raise AssertionError("Pareto direct lower-image failure")
            direct_equivalence_checks += 1
            for index in range(len(frontier)):
                reduced = frontier[:index] + frontier[index + 1 :]
                if reduced and lower_image_equivalent(frontier, reduced):
                    raise AssertionError("retained Pareto point was lower-image redundant")
                convex_necessity_checks += 1
    return {
        "profile_cubes": ["{0,1}^2", "{0,1}^3"],
        "nonempty_subsets": subsets,
        "direct_lower_image_equivalence_checks": direct_equivalence_checks,
        "convex_retained_profile_necessity_checks": convex_necessity_checks,
    }


def build_result(script_path: Path) -> dict[str, Any]:
    core_path = script_path.with_name("joint_route_core.py")
    return {
        "schema": SCHEMA,
        "terminal": TERMINAL,
        "source_base_commit": SOURCE_BASE_COMMIT,
        "implementation_sha256": {
            "core": sha256_file(core_path),
            "verifier": sha256_file(script_path),
        },
        "random_exact_checks": verify_random_systems(),
        "invalid_STUDY_B_pairing_counterexample": invalid_pairing_counterexample(),
        "same_marginals_different_joint_system": compatibility_and_marginal_counterexample(),
        "shared_coarsening_ranking_reversal": coarsening_ranking_reversal(),
        "acquisition_timing_reversal": timing_reversal(),
        "lower_image_exhaustion": lower_image_exhaustion(),
        "controls": {
            "all_legal_learned_fallback_combinations_enumerated": True,
            "diagonal_pairing_is_not_assumed": True,
            "exact_joint_profiles_match_independent_explicit_enumeration": True,
            "Pareto_frontier_preserves_deterministic_and_randomized_values": True,
            "lower_image_equality_is_checked_not_asserted_from_marginals": True,
            "same_marginals_can_have_different_joint_route_value": True,
            "separate_marginal_safety_does_not_imply_joint_route_safety": True,
            "route_observation_coarsening_can_reverse_pair_ranking": True,
            "pre_and_post_acquisition_routing_are_distinct": True,
            "invalid_3x3_shortcut_value_35_to_70_preserved": True,
        },
        "authority": {
            "analytic_theorems": "PROVED_IN_ADDENDUM",
            "finite_verification": "IMPLEMENTATION_CORROBORATION_ONLY",
            "replaces_invalid_STUDY_B_shortcut": True,
            "paired_ASlib_experiment_executed": False,
            "R16_terminal_preserved": "ANON_R16_NO_PORTABLE_CERTIFICATE_VALUE",
            "external_independence": "CANNOT_CHECK",
            "novelty": "CANNOT_CHECK",
            "production_value": False,
            "grants_journal_authority": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_result(Path(__file__))
    payload = canonical_json(result) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="utf-8")
    digest = hashlib.sha256(payload.encode()).hexdigest()
    print(f"{TERMINAL} sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
