#!/usr/bin/env python3
"""Finite implementation audit for the FiberGuard R12 profile Bellman theory."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import random

from fiberguard_profile_bellman_r12_core import (
    make_profile_solvers,
    naive_worst_charge_value,
    offset_value,
    profile_value,
    scalar_cell_constant_value,
    static_value,
)

SCHEMA = "ORION.FiberGuard.ProfileBellman.R12.v1"
SOURCE_BASE_COMMIT = "6f0b9a354c0f71ca744596252c74e2bf8b4a6f5b"
SEED = 20260826
TERMINAL = "FIBERGUARD_PROFILE_BELLMAN_R12_PASS"


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def oracle_regret_table(
    rng: random.Random, action_count: int, state_count: int
) -> tuple[tuple[int, ...], ...]:
    raw = [[rng.randrange(10) for _ in range(state_count)] for _ in range(action_count)]
    minima = [
        min(raw[action][state] for action in range(action_count))
        for state in range(state_count)
    ]
    return tuple(
        tuple(raw[action][state] - minima[state] for state in range(state_count))
        for action in range(action_count)
    )


def random_system(rng: random.Random, cell_constant: bool):
    state_count = rng.randint(2, 5)
    action_count = rng.randint(2, 3)
    feature_count = rng.randint(1, 3)
    regret = oracle_regret_table(rng, action_count, state_count)
    observations: list[tuple[int, ...]] = []
    costs: list[tuple[int, ...]] = []
    for _ in range(feature_count):
        alphabet = rng.randint(1, min(3, state_count))
        obs = tuple(rng.randrange(alphabet) for _ in range(state_count))
        observations.append(obs)
        if cell_constant:
            by_observation = {value: rng.randrange(5) for value in set(obs)}
            costs.append(tuple(by_observation[value] for value in obs))
        else:
            costs.append(tuple(rng.randrange(5) for _ in range(state_count)))
    return regret, tuple(observations), tuple(costs)


def verify_random_agreement() -> dict[str, int]:
    rng = random.Random(SEED)
    general_cases = 240
    cell_constant_cases = 240
    frontier_count = 0
    unpruned_count = 0
    for _ in range(general_cases):
        regret, observations, costs = random_system(rng, False)
        states = tuple(range(len(regret[0])))
        remaining = tuple(range(len(observations)))
        frontier, unpruned = make_profile_solvers(regret, observations, costs)
        front = frontier(states, remaining)
        brute = unpruned(states, remaining)
        values = (
            profile_value(front),
            profile_value(brute),
            offset_value(regret, observations, costs, states, remaining),
        )
        if len(set(values)) != 1:
            raise AssertionError(("profile/explicit/offset disagreement", values))
        frontier_count += len(front)
        unpruned_count += len(brute)
    for _ in range(cell_constant_cases):
        regret, observations, costs = random_system(rng, True)
        states = tuple(range(len(regret[0])))
        remaining = tuple(range(len(observations)))
        frontier, _ = make_profile_solvers(regret, observations, costs)
        exact = profile_value(frontier(states, remaining))
        scalar = scalar_cell_constant_value(
            regret, observations, costs, states, remaining
        )
        if exact != scalar:
            raise AssertionError(("cell-constant scalar disagreement", exact, scalar))
    return {
        "general_systems": general_cases,
        "cell_constant_systems": cell_constant_cases,
        "frontier_profiles_at_roots": frontier_count,
        "unpruned_profiles_at_roots": unpruned_count,
    }


def verify_scalar_criterion() -> dict[str, int]:
    cost_profiles = constant = nonconstant = counterexamples = continuations = 0
    for dimension in (2, 3):
        losses = list(itertools.product(range(4), repeat=dimension))
        continuations += len(losses)
        for cost in itertools.product(range(3), repeat=dimension):
            cost_profiles += 1
            kappa = max(cost)
            exact_for_all = all(
                max(c + loss[index] for index, c in enumerate(cost))
                == kappa + max(loss)
                for loss in losses
            )
            is_constant = len(set(cost)) == 1
            if exact_for_all != is_constant:
                raise AssertionError(("scalar criterion mismatch", cost))
            if is_constant:
                constant += 1
            else:
                nonconstant += 1
                if not any(
                    max(c + loss[index] for index, c in enumerate(cost))
                    != kappa + max(loss)
                    for loss in losses
                ):
                    raise AssertionError(("missing counterexample", cost))
                counterexamples += 1
    return {
        "cost_profiles": cost_profiles,
        "constant_profiles": constant,
        "nonconstant_profiles": nonconstant,
        "nonconstant_counterexamples": counterexamples,
        "continuation_profile_denominator": continuations,
    }


def hostile_counterexample() -> dict[str, object]:
    regret = ((0, 2, 100), (100, 100, 0), (3, 3, 3))
    observations = ((0, 0, 1),)
    costs = ((2, 0, 0),)
    states = (0, 1, 2)
    remaining = (0,)
    frontier, _ = make_profile_solvers(regret, observations, costs)
    exact = profile_value(frontier(states, remaining))
    offset = offset_value(regret, observations, costs, states, remaining)
    naive = naive_worst_charge_value(regret, observations, costs, states, remaining)
    immediate = min(max(action) for action in regret)
    if (exact, offset, naive, immediate) != (2, 2, 3, 3):
        raise AssertionError(("hostile counterexample drift", exact, offset, naive))
    return {
        "states": 3,
        "actions": 3,
        "features": 1,
        "exact_profile_value": exact,
        "exact_offset_value": offset,
        "naive_worst_charge_scalar_value": naive,
        "immediate_action_value": immediate,
        "exact_root_choice": "refine",
        "naive_root_choice": "act",
    }


def gap_system(k: int):
    state_count = 2 * k
    loss = k + 1
    regret = tuple(
        tuple(0 if state == action else loss for state in range(state_count))
        for action in range(state_count)
    )
    bit_count = math.ceil(math.log2(k)) if k > 1 else 0
    observations: list[tuple[int, ...]] = []
    costs: list[tuple[int, ...]] = []
    for bit in range(bit_count):
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
    return regret, tuple(observations), tuple(costs), bit_count, loss


def verify_gap() -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for k in range(1, 11):
        regret, observations, costs, bit_count, loss = gap_system(k)
        feature_count = len(observations)
        best_static = min(
            static_value(
                regret,
                observations,
                costs,
                tuple(
                    feature
                    for feature in range(feature_count)
                    if (mask >> feature) & 1
                ),
            )
            for mask in range(1 << feature_count)
        )
        adaptive = scalar_cell_constant_value(
            regret,
            observations,
            costs,
            tuple(range(2 * k)),
            tuple(range(feature_count)),
        )
        if best_static != k or adaptive != 1:
            raise AssertionError(("adaptivity-gap drift", k, best_static, adaptive))
        rows.append(
            {
                "k": k,
                "states": 2 * k,
                "actions": 2 * k,
                "zero_cost_index_bits": bit_count,
                "paid_branch_bits": k,
                "terminal_mismatch_loss": loss,
                "best_static_value": best_static,
                "adaptive_value": adaptive,
                "ratio": k,
                "additive_gap": k - 1,
            }
        )
    return rows


def build_result(script_path: Path) -> dict[str, object]:
    core_path = script_path.with_name("fiberguard_profile_bellman_r12_core.py")
    return {
        "schema": SCHEMA,
        "terminal": TERMINAL,
        "source_base_commit": SOURCE_BASE_COMMIT,
        "implementation_sha256": {
            "core": sha256_file(core_path),
            "verifier": sha256_file(script_path),
        },
        "random_exact_agreement": verify_random_agreement(),
        "scalar_decomposition_criterion": verify_scalar_criterion(),
        "hostile_state_dependent_cost": hostile_counterexample(),
        "adaptivity_gap_family": verify_gap(),
        "controls": {
            "pareto_frontier_matches_unpruned_policy_profiles": True,
            "offset_bellman_matches_profile_frontier": True,
            "cell_constant_scalar_bellman_matches_exact_value": True,
            "nonconstant_cost_requires_profile_state": True,
            "naive_worst_charge_recursion_changes_root_decision": True,
            "static_policy_is_strictly_dominated_in_gap_family": True,
        },
        "authority": {
            "analytic_theorems": "PROVED_IN_ADDENDUM",
            "finite_verification": "IMPLEMENTATION_CORROBORATION_ONLY",
            "ASlib_adaptive_experiment_executed": False,
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
