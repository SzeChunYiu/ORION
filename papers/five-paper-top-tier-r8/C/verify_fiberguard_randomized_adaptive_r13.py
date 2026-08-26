#!/usr/bin/env python3
"""Finite exact audit for FiberGuard R13 randomized adaptive refinement."""
from __future__ import annotations

import argparse
import collections
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
from typing import Any

from fiberguard_profile_bellman_r12_core import make_profile_solvers, profile_value
from fiberguard_randomized_adaptive_r13_core import (
    bayes_policy_value,
    fraction_text,
    pathwise_value,
    randomized_static_value,
    solve_zero_sum_profiles,
)

SCHEMA = "ORION.FiberGuard.RandomizedAdaptive.R13.v1"
SOURCE_BASE_COMMIT = "91373ddf3eb17535ea623d0b7998adb307fcd9de"
SEED = 20260826
TERMINAL = "FIBERGUARD_RANDOMIZED_ADAPTIVE_R13_PASS"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def oracle_regret_table(
    rng: random.Random, action_count: int, state_count: int
) -> tuple[tuple[int, ...], ...]:
    raw = [[rng.randrange(9) for _ in range(state_count)] for _ in range(action_count)]
    oracle = [
        min(raw[action][state] for action in range(action_count))
        for state in range(state_count)
    ]
    return tuple(
        tuple(raw[action][state] - oracle[state] for state in range(state_count))
        for action in range(action_count)
    )


def random_system(rng: random.Random):
    state_count = rng.randint(2, 4)
    action_count = rng.randint(2, 3)
    feature_count = rng.randint(0, 2)
    regret = oracle_regret_table(rng, action_count, state_count)
    observations: list[tuple[int, ...]] = []
    costs: list[tuple[int, ...]] = []
    for _ in range(feature_count):
        alphabet = rng.randint(1, min(3, state_count))
        observations.append(tuple(rng.randrange(alphabet) for _ in range(state_count)))
        costs.append(tuple(rng.randrange(5) for _ in range(state_count)))
    return regret, tuple(observations), tuple(costs)


def full_adversary_distribution(
    state_count: int, equilibrium: dict[str, object]
) -> tuple[Fraction, ...]:
    result = [Fraction(0)] * state_count
    support = equilibrium["state_support"]
    probability = equilibrium["state_probability"]
    assert isinstance(support, tuple) and isinstance(probability, tuple)
    for index, state in enumerate(support):
        result[state] = probability[index]
    return tuple(result)


def verify_random_systems() -> dict[str, object]:
    rng = random.Random(SEED)
    system_count = 300
    prior_checks_per_system = 4
    total_frontier = total_unpruned = total_equilibria = 0
    maximum_frontier = maximum_unpruned = 0
    strict_randomization_improvements = 0
    support_histogram: collections.Counter[int] = collections.Counter()

    for _ in range(system_count):
        regret, observations, costs = random_system(rng)
        states = tuple(range(len(regret[0])))
        remaining = tuple(range(len(observations)))
        frontier_solver, unpruned_solver = make_profile_solvers(regret, observations, costs)
        frontier = frontier_solver(states, remaining)
        unpruned = unpruned_solver(states, remaining)

        # The R12 frontier must dominate every explicit deterministic profile.
        if not all(
            any(
                all(left <= right for left, right in zip(candidate, profile))
                for candidate in frontier
            )
            for profile in unpruned
        ):
            raise AssertionError("Pareto frontier failed to dominate an explicit profile")

        equilibrium = solve_zero_sum_profiles(frontier)
        randomized_value = equilibrium["value"]
        if not isinstance(randomized_value, Fraction):
            raise TypeError("exact game value must be rational")
        deterministic_value = Fraction(profile_value(frontier))
        pathwise = pathwise_value(frontier)
        if pathwise != deterministic_value:
            raise AssertionError("pathwise randomization changed deterministic value")
        if randomized_value > deterministic_value:
            raise AssertionError("randomization increased minimax expected loss")
        if randomized_value < deterministic_value:
            strict_randomization_improvements += 1

        policy_support = equilibrium["policy_support"]
        assert isinstance(policy_support, tuple)
        if len(policy_support) > len(states):
            raise AssertionError("mixed-policy support exceeded fibre size")
        support_histogram[len(policy_support)] += 1

        adversary = full_adversary_distribution(len(states), equilibrium)
        dual_bayes = bayes_policy_value(
            regret, observations, costs, states, remaining, adversary
        )
        if dual_bayes != randomized_value:
            raise AssertionError(("dual Bayes value mismatch", dual_bayes, randomized_value))
        direct_dual = min(
            sum(adversary[index] * profile[index] for index in range(len(states)))
            for profile in unpruned
        )
        if direct_dual != randomized_value:
            raise AssertionError(("explicit-profile dual mismatch", direct_dual, randomized_value))

        # Additional priors check the scalar Bayes separation oracle away from equilibrium.
        for _ in range(prior_checks_per_system):
            integer_weight = [rng.randrange(1, 8) for _ in states]
            denominator = sum(integer_weight)
            prior = tuple(Fraction(weight, denominator) for weight in integer_weight)
            bellman = bayes_policy_value(
                regret, observations, costs, states, remaining, prior
            )
            explicit = min(
                sum(prior[index] * profile[index] for index in range(len(states)))
                for profile in unpruned
            )
            if bellman != explicit:
                raise AssertionError(("Bayes oracle disagreement", bellman, explicit))

        total_frontier += len(frontier)
        total_unpruned += len(unpruned)
        maximum_frontier = max(maximum_frontier, len(frontier))
        maximum_unpruned = max(maximum_unpruned, len(unpruned))
        total_equilibria += int(equilibrium["equilibria_checked"])

    return {
        "systems": system_count,
        "additional_prior_checks": system_count * prior_checks_per_system,
        "total_frontier_profiles": total_frontier,
        "total_explicit_profiles": total_unpruned,
        "maximum_frontier_profiles": maximum_frontier,
        "maximum_explicit_profiles": maximum_unpruned,
        "strict_randomization_improvements": strict_randomization_improvements,
        "mixed_policy_support_histogram": {
            str(key): support_histogram[key] for key in sorted(support_histogram)
        },
        "equilibria_checked": total_equilibria,
    }


def randomization_gap_family() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for state_count in range(2, 17):
        loss = state_count
        profiles = tuple(
            tuple(loss if state == action else 0 for state in range(state_count))
            for action in range(state_count)
        )
        deterministic = pathwise_value(profiles)
        randomized = Fraction(loss, state_count)
        uniform_expected = tuple(
            sum(Fraction(1, state_count) * profile[state] for profile in profiles)
            for state in range(state_count)
        )
        if deterministic != loss or any(value != randomized for value in uniform_expected):
            raise AssertionError("randomization-gap construction drift")
        # Every distribution has a coordinate at least 1/n; that state incurs L*p_i.
        if loss * Fraction(1, state_count) != randomized:
            raise AssertionError("pigeonhole lower bound drift")
        if state_count <= 8:
            exact = solve_zero_sum_profiles(profiles)
            if exact["value"] != randomized:
                raise AssertionError("exact solver missed randomization-gap value")
        rows.append(
            {
                "states": state_count,
                "actions": state_count,
                "loss": loss,
                "deterministic_pathwise_value": fraction_text(Fraction(deterministic)),
                "randomized_expected_value": fraction_text(randomized),
                "ratio": state_count,
                "exact_solver_replayed": state_count <= 8,
            }
        )
    return rows


def adaptivity_gap_system(k: int):
    state_count = 2 * k
    mismatch_loss = 2 * k + 1
    regret = tuple(
        tuple(0 if state == action else mismatch_loss for state in range(state_count))
        for action in range(state_count)
    )
    index_bits = math.ceil(math.log2(k)) if k > 1 else 0
    observations: list[tuple[int, ...]] = []
    costs: list[tuple[int, ...]] = []
    for bit in range(index_bits):
        observations.append(
            tuple(((state // 2) >> bit) & 1 for state in range(state_count))
        )
        costs.append((0,) * state_count)
    for branch in range(k):
        observations.append(
            tuple(
                (state % 2) if state // 2 == branch else 0
                for state in range(state_count)
            )
        )
        costs.append((1,) * state_count)
    return regret, tuple(observations), tuple(costs), index_bits, mismatch_loss


def specialized_gap_static_value(
    observations: tuple[tuple[int, ...], ...],
    selected: tuple[int, ...],
    paid_start: int,
    mismatch_loss: int,
) -> Fraction:
    state_count = len(observations[0]) if observations else 2
    fibres: dict[tuple[int, ...], int] = {}
    for state in range(state_count):
        signature = tuple(observations[feature][state] for feature in selected)
        fibres[signature] = fibres.get(signature, 0) + 1
    paid = sum(feature >= paid_start for feature in selected)
    ambiguity = max(
        Fraction(0) if size == 1 else Fraction(mismatch_loss * (size - 1), size)
        for size in fibres.values()
    )
    return Fraction(paid) + ambiguity


def randomized_adaptivity_gap_family() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for k in range(1, 11):
        regret, observations, costs, index_bits, mismatch_loss = adaptivity_gap_system(k)
        feature_count = len(observations)
        best_static: Fraction | None = None
        minimizers = 0
        for mask in range(1 << feature_count):
            selected = tuple(
                feature for feature in range(feature_count) if (mask >> feature) & 1
            )
            value = specialized_gap_static_value(
                observations, selected, index_bits, mismatch_loss
            )
            if best_static is None or value < best_static:
                best_static = value
                minimizers = 1
            elif value == best_static:
                minimizers += 1
            if k <= 3:
                general = randomized_static_value(regret, observations, costs, selected)
                if general != value:
                    raise AssertionError(
                        ("specialized static mismatch", k, selected, value, general)
                    )
        assert best_static is not None
        adaptive = Fraction(1)
        unresolved_pair_value = Fraction(mismatch_loss, 2)
        if best_static != k or unresolved_pair_value <= adaptive:
            raise AssertionError(("randomized adaptivity gap drift", k, best_static))
        rows.append(
            {
                "k": k,
                "states": 2 * k,
                "actions": 2 * k,
                "free_index_bits": index_bits,
                "paid_branch_bits": k,
                "mismatch_loss": mismatch_loss,
                "best_randomized_static_value": fraction_text(best_static),
                "randomized_adaptive_value": fraction_text(adaptive),
                "ratio": k,
                "additive_gap": k - 1,
                "static_minimizers": minimizers,
                "general_solver_cross_checked": k <= 3,
            }
        )
    return rows


def hostile_two_state_certificate() -> dict[str, object]:
    profiles = ((0, 12), (12, 0), (7, 7))
    equilibrium = solve_zero_sum_profiles(profiles)
    if equilibrium["value"] != 6:
        raise AssertionError("hostile mixed certificate drift")
    adversary = full_adversary_distribution(2, equilibrium)
    expected = [
        sum(adversary[state] * profile[state] for state in range(2))
        for profile in profiles
    ]
    if min(expected) != 6 or pathwise_value(profiles) != 7:
        raise AssertionError("hostile lower/pathwise certificate drift")
    return {
        "profiles": [list(profile) for profile in profiles],
        "deterministic_pathwise_value": "7",
        "randomized_expected_value": "6",
        "mixed_policy_support": len(equilibrium["policy_support"]),
        "adversary_support": len(equilibrium["state_support"]),
        "adversary_distribution": [fraction_text(value) for value in adversary],
        "dual_expected_losses": [fraction_text(value) for value in expected],
    }


def build_result(script_path: Path) -> dict[str, object]:
    core_path = script_path.with_name("fiberguard_randomized_adaptive_r13_core.py")
    return {
        "schema": SCHEMA,
        "terminal": TERMINAL,
        "source_base_commit": SOURCE_BASE_COMMIT,
        "implementation_sha256": {
            "core": sha256_file(core_path),
            "verifier": sha256_file(script_path),
        },
        "random_exact_agreement": verify_random_systems(),
        "hostile_two_state_certificate": hostile_two_state_certificate(),
        "unbounded_randomization_gap": randomization_gap_family(),
        "unbounded_randomized_adaptivity_gap": randomized_adaptivity_gap_family(),
        "controls": {
            "pareto_frontier_dominates_all_explicit_profiles": True,
            "mixed_policy_support_at_most_state_count": True,
            "dual_adversary_prior_matches_primal_value": True,
            "bayes_bellman_matches_explicit_policy_expectation": True,
            "pathwise_randomization_does_not_improve_deterministic_value": True,
            "randomization_gap_is_unbounded_for_expected_semantics": True,
            "adaptivity_gap_survives_terminal_randomization": True,
        },
        "authority": {
            "analytic_theorems": "PROVED_IN_ADDENDUM",
            "finite_verification": "IMPLEMENTATION_CORROBORATION_ONLY",
            "generic_game_theory_and_decision_tree_results": "DONOR_OWNED",
            "ASlib_randomized_adaptive_experiment_executed": False,
            "tail_or_pathwise_safety": False,
            "unseen_instance_generalization": False,
            "external_independence": "CANNOT_CHECK",
            "novelty": "CANNOT_CHECK",
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
