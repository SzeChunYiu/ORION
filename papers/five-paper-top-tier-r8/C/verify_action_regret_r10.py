#!/usr/bin/env python3
"""Finite hostile controls for the FiberGuard action-regret extension.

The analytic proof owns the all-instance statements.  This script independently
corroborates the finite formulas by exhaustive policy enumeration, exact
rational LP-vertex enumeration, an independent two-action envelope solver, and
complete contingent-policy-tree enumeration for the Bellman recursion.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
import json
from pathlib import Path
import random
from typing import Iterable, Sequence

Fibre = tuple[int, ...]
Partition = tuple[Fibre, ...]
Matrix = tuple[tuple[Fraction, ...], ...]


@dataclass(frozen=True)
class Refinement:
    name: str
    cost: Fraction
    parts: Partition


def as_fraction_matrix(rows: Sequence[Sequence[int | Fraction]]) -> Matrix:
    matrix = tuple(tuple(Fraction(v) for v in row) for row in rows)
    if not matrix or not matrix[0]:
        raise ValueError("cost matrix needs at least one action and one state")
    if any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("ragged cost matrix")
    return matrix


def regret_matrix(costs: Matrix) -> Matrix:
    oracle = tuple(min(row[s] for row in costs) for s in range(len(costs[0])))
    return tuple(tuple(row[s] - oracle[s] for s in range(len(oracle))) for row in costs)


def action_losses(costs: Matrix, fibre: Fibre) -> tuple[Fraction, ...]:
    regrets = regret_matrix(costs)
    return tuple(max(row[s] for s in fibre) for row in regrets)


def deterministic_value(costs: Matrix, fibre: Fibre) -> Fraction:
    return min(action_losses(costs, fibre))


def safe_actions(costs: Matrix, fibre: Fibre, epsilon: Fraction) -> tuple[int, ...]:
    return tuple(i for i, loss in enumerate(action_losses(costs, fibre)) if loss <= epsilon)


def solve_square(a: list[list[Fraction]], b: list[Fraction]) -> tuple[Fraction, ...] | None:
    """Exact Gaussian elimination; return None for a singular active set."""
    n = len(b)
    aug = [row[:] + [rhs] for row, rhs in zip(a, b)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if aug[r][col]), None)
        if pivot is None:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        aug[col] = [v / scale for v in aug[col]]
        for r in range(n):
            if r == col or not aug[r][col]:
                continue
            factor = aug[r][col]
            aug[r] = [x - factor * y for x, y in zip(aug[r], aug[col])]
    return tuple(aug[i][-1] for i in range(n))


def randomized_value(costs: Matrix, fibre: Fibre) -> Fraction:
    """Solve the finite minimax LP by exact enumeration of all LP vertices."""
    regrets = regret_matrix(costs)
    action_count = len(costs)
    # Variables are p_0,...,p_(m-1),t.  Sum p=1 is always active.  A
    # vertex adds m active inequalities chosen from state and p_i >= 0 rows.
    constraints = [("state", s) for s in fibre] + [("zero", i) for i in range(action_count)]
    candidates: list[Fraction] = []
    for active in combinations(constraints, action_count):
        equations = [[Fraction(1)] * action_count + [Fraction(0)]]
        rhs = [Fraction(1)]
        for kind, index in active:
            if kind == "state":
                equations.append([regrets[a][index] for a in range(action_count)] + [Fraction(-1)])
            else:
                row = [Fraction(0)] * (action_count + 1)
                row[index] = Fraction(1)
                equations.append(row)
            rhs.append(Fraction(0))
        solution = solve_square(equations, rhs)
        if solution is None:
            continue
        probabilities, t = solution[:-1], solution[-1]
        if any(p < 0 for p in probabilities) or sum(probabilities) != 1:
            continue
        if any(
            sum(probabilities[a] * regrets[a][s] for a in range(action_count)) > t for s in fibre
        ):
            continue
        candidates.append(t)
    if not candidates:
        raise AssertionError("bounded minimax LP produced no feasible vertex")
    return min(candidates)


def two_action_envelope(costs: Matrix, fibre: Fibre) -> Fraction:
    """Independent exact solver for two actions using line intersections."""
    if len(costs) != 2:
        raise ValueError("two-action control requires exactly two actions")
    regrets = regret_matrix(costs)
    candidates = {Fraction(0), Fraction(1)}
    lines = [(regrets[1][s], regrets[0][s] - regrets[1][s]) for s in fibre]
    for (b1, m1), (b2, m2) in combinations(lines, 2):
        if m1 != m2:
            p = (b2 - b1) / (m1 - m2)
            if 0 <= p <= 1:
                candidates.add(p)
    return min(max(b + m * p for b, m in lines) for p in candidates)


def canonical_partition(parts: Iterable[Iterable[int]]) -> Partition:
    out = tuple(
        sorted((tuple(sorted(part)) for part in parts if tuple(part)), key=lambda x: (len(x), x))
    )
    flat = [i for part in out for i in part]
    if len(flat) != len(set(flat)):
        raise ValueError("partition parts overlap")
    return out


def deterministic_policy_enumeration(costs: Matrix, partition: Partition) -> Fraction:
    regrets = regret_matrix(costs)
    best: Fraction | None = None
    for policy in product(range(len(costs)), repeat=len(partition)):
        loss = max(regrets[action][s] for action, fibre in zip(policy, partition) for s in fibre)
        best = loss if best is None else min(best, loss)
    assert best is not None
    return best


def partition_value(costs: Matrix, partition: Partition, randomized: bool) -> Fraction:
    solver = randomized_value if randomized else deterministic_value
    return max(solver(costs, fibre) for fibre in partition)


def build_refinement_system(
    rng: random.Random, n: int, costs: Matrix
) -> tuple[dict[Fibre, tuple[Refinement, ...]], dict[Fibre, Fraction]]:
    full = tuple(range(n))
    raw = []
    for j in range(rng.randrange(1, 4)):
        labels = tuple(rng.randrange(2, min(4, n) + 1) for _ in range(n))
        raw.append((f"r{j}", Fraction(rng.randrange(0, 7), 2), labels))

    @lru_cache(maxsize=None)
    def refinements(fibre: Fibre) -> tuple[Refinement, ...]:
        by_parts: dict[Partition, Refinement] = {}
        for name, cost, labels in raw:
            groups: dict[int, list[int]] = {}
            for state in fibre:
                groups.setdefault(labels[state], []).append(state)
            parts = canonical_partition(groups.values())
            if len(parts) < 2:
                continue
            candidate = Refinement(name, cost, parts)
            old = by_parts.get(parts)
            if old is None or (candidate.cost, candidate.name) < (old.cost, old.name):
                by_parts[parts] = candidate
        return tuple(sorted(by_parts.values(), key=lambda row: (row.name, row.cost, row.parts)))

    stack = [full]
    seen = {full}
    while stack:
        fibre = stack.pop()
        for refinement in refinements(fibre):
            for child in refinement.parts:
                if child not in seen:
                    seen.add(child)
                    stack.append(child)
    ref_map = {fibre: refinements(fibre) for fibre in seen}
    defer = {fibre: Fraction(rng.randrange(0, 17), 2) for fibre in seen}
    return ref_map, defer


def bellman(
    costs: Matrix,
    ref_map: dict[Fibre, tuple[Refinement, ...]],
    defer: dict[Fibre, Fraction],
    root: Fibre,
) -> Fraction:
    @lru_cache(maxsize=None)
    def solve(fibre: Fibre) -> Fraction:
        candidates = [deterministic_value(costs, fibre), defer[fibre]]
        candidates.extend(
            refinement.cost + max(solve(child) for child in refinement.parts)
            for refinement in ref_map[fibre]
        )
        return min(candidates)

    return solve(root)


def enumerate_policy_trees(
    costs: Matrix,
    ref_map: dict[Fibre, tuple[Refinement, ...]],
    defer: dict[Fibre, Fraction],
    root: Fibre,
) -> tuple[Fraction, int]:
    @lru_cache(maxsize=None)
    def values(fibre: Fibre) -> tuple[tuple[Fraction, ...], int]:
        rows = set(action_losses(costs, fibre)) | {defer[fibre]}
        generated = len(costs) + 1
        for refinement in ref_map[fibre]:
            child_rows = [values(child)[0] for child in refinement.parts]
            combinations_count = 1
            for child_values in child_rows:
                combinations_count *= len(child_values)
            generated += combinations_count
            for continuation in product(*child_rows):
                rows.add(refinement.cost + max(continuation))
        return tuple(sorted(rows)), generated

    rows, generated = values(root)
    return min(rows), generated


def validate_common_unit(action_unit: str, acquisition_unit: str, defer_unit: str) -> None:
    if not action_unit or len({action_unit, acquisition_unit, defer_unit}) != 1:
        raise ValueError("action, acquisition, and defer costs require one frozen unit")


def run() -> dict[str, object]:
    rng = random.Random(20260826)
    policy_cases = 0
    lp_cases = 0
    monotonicity_cases = 0
    safe_set_cases = 0
    bellman_cases = 0
    policy_trees = 0

    # Formula versus complete deterministic policy enumeration, plus exact
    # randomized monotonicity and the safe-set equivalence.
    for n in range(2, 8):
        for _ in range(120):
            action_count = rng.randrange(2, 5)
            costs = as_fraction_matrix(
                [[rng.randrange(0, 12) for _state in range(n)] for _action in range(action_count)]
            )
            labels = [rng.randrange(0, min(3, n)) for _ in range(n)]
            groups: dict[int, list[int]] = {}
            for state, label in enumerate(labels):
                groups.setdefault(label, []).append(state)
            fine = canonical_partition(groups.values())
            coarse = (tuple(range(n)),)

            formula = partition_value(costs, fine, randomized=False)
            enumerated = deterministic_policy_enumeration(costs, fine)
            assert formula == enumerated
            policy_cases += 1

            assert partition_value(costs, fine, randomized=False) <= partition_value(
                costs, coarse, randomized=False
            )
            assert partition_value(costs, fine, randomized=True) <= partition_value(
                costs, coarse, randomized=True
            )
            monotonicity_cases += 2

            for fibre in fine:
                epsilon = Fraction(rng.randrange(0, 10), 2)
                assert bool(safe_actions(costs, fibre, epsilon)) == (
                    deterministic_value(costs, fibre) <= epsilon
                )
                safe_set_cases += 1

    # Independent two-action envelope cross-check of the generic LP solver.
    for n in range(2, 9):
        for _ in range(160):
            costs = as_fraction_matrix([[rng.randrange(0, 15) for _ in range(n)] for _ in range(2)])
            fibre = tuple(range(n))
            assert randomized_value(costs, fibre) == two_action_envelope(costs, fibre)
            lp_cases += 1

    # Complete contingent-policy enumeration for random acyclic refinements.
    for n in range(2, 7):
        for _ in range(100):
            costs = as_fraction_matrix(
                [
                    [rng.randrange(0, 10) for _state in range(n)]
                    for _action in range(rng.randrange(2, 5))
                ]
            )
            ref_map, defer = build_refinement_system(rng, n, costs)
            root = tuple(range(n))
            dynamic = bellman(costs, ref_map, defer, root)
            exhaustive, generated = enumerate_policy_trees(costs, ref_map, defer, root)
            assert dynamic == exhaustive
            bellman_cases += 1
            policy_trees += generated

    # Hostile hand controls: randomization strictly helps, three-action LP,
    # complete refinement removes regret at a price, and unit mismatch fails.
    matching_pennies = as_fraction_matrix([[0, 1], [1, 0]])
    assert deterministic_value(matching_pennies, (0, 1)) == 1
    assert randomized_value(matching_pennies, (0, 1)) == Fraction(1, 2)

    three_way = as_fraction_matrix([[0, 1, 1], [1, 0, 1], [1, 1, 0]])
    assert randomized_value(three_way, (0, 1, 2)) == Fraction(2, 3)

    root = (0, 1)
    refinement = Refinement("identity", Fraction(1, 4), ((0,), (1,)))
    ref_map = {root: (refinement,), (0,): (), (1,): ()}
    defer = {root: Fraction(9), (0,): Fraction(9), (1,): Fraction(9)}
    assert bellman(matching_pennies, ref_map, defer, root) == Fraction(1, 4)

    validate_common_unit("seconds", "seconds", "seconds")
    mismatch_rejected = False
    try:
        validate_common_unit("regret", "seconds", "regret")
    except ValueError:
        mismatch_rejected = True
    assert mismatch_rejected

    return {
        "schema": "ORION.FiberGuard.ActionRegretVerification.v1",
        "status": "PASS",
        "deterministic_policy_enumeration_cases": policy_cases,
        "randomized_lp_independent_crosschecks": lp_cases,
        "refinement_monotonicity_checks": monotonicity_cases,
        "safe_set_equivalence_checks": safe_set_cases,
        "bellman_policy_tree_cases": bellman_cases,
        "explicit_policy_trees_generated": policy_trees,
        "strict_randomization_control": "1/2<1",
        "three_action_control": "2/3",
        "unit_mismatch_rejected": mismatch_rejected,
        "authority": "FINITE_IMPLEMENTATION_CORROBORATION_ONLY",
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, sort_keys=True))
    output = Path(__file__).with_name("ACTION_REGRET_R10_RESULTS.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
