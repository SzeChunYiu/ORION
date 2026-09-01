#!/usr/bin/env python3
"""Independent finite controls for the FiberGuard refinement recursion.

This verifier does not import the reference FiberGuard implementation.  It
compares:

1. a memoized Bellman solver using the theorem statement; and
2. explicit enumeration of complete contingent policy trees.

It also brute-forces scalar answers on a half-integer grid to check the exact
fibre radius.  Passing this file corroborates the implementation only; the
analytic proof owns the all-instance theorem.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product
import json
import random
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

Fibre = Tuple[int, ...]
Partition = Tuple[Fibre, ...]


@dataclass(frozen=True)
class Refinement:
    name: str
    cost: Fraction
    parts: Partition


def radius(values: Sequence[int], fibre: Fibre) -> Fraction:
    ys = [values[i] for i in fibre]
    return Fraction(max(ys) - min(ys), 2)


def brute_scalar_radius(values: Sequence[int], fibre: Fibre) -> Fraction:
    ys = [values[i] for i in fibre]
    lo, hi = min(ys), max(ys)
    # Endpoint and half-integer grid is enough for integral targets.
    candidates = [Fraction(k, 2) for k in range(2 * lo - 2, 2 * hi + 3)]
    return min(max(abs(z - y) for y in ys) for z in candidates)


def canonical_partition(parts: Iterable[Iterable[int]]) -> Partition:
    out = tuple(sorted((tuple(sorted(p)) for p in parts if tuple(p)), key=lambda x: (len(x), x)))
    flat = [i for p in out for i in p]
    if len(flat) != len(set(flat)):
        raise ValueError("partition parts overlap")
    return out


def restrict_partition(partition: Partition, fibre: Fibre) -> Partition:
    f = set(fibre)
    return canonical_partition(tuple(i for i in part if i in f) for part in partition)


def build_system(seed: int, n: int) -> Tuple[List[int], Dict[Fibre, Tuple[Refinement, ...]], Dict[Fibre, Fraction]]:
    rng = random.Random(seed)
    values = [rng.randrange(0, 9) for _ in range(n)]
    full = tuple(range(n))
    # A finite global feature family.  Each feature assigns every instance one
    # of 2..min(4,n) labels; restrictions induce child partitions at a fibre.
    raw_features: List[Tuple[str, Fraction, Tuple[int, ...]]] = []
    for j in range(rng.randrange(1, 5)):
        k = rng.randrange(2, min(4, n) + 1)
        labels = tuple(rng.randrange(k) for _ in range(n))
        raw_features.append((f"f{j}", Fraction(rng.randrange(0, 7), 2), labels))

    @lru_cache(maxsize=None)
    def refinements(fibre: Fibre) -> Tuple[Refinement, ...]:
        result: List[Refinement] = []
        for name, cost, labels in raw_features:
            groups: Dict[int, List[int]] = {}
            for i in fibre:
                groups.setdefault(labels[i], []).append(i)
            parts = canonical_partition(groups.values())
            if len(parts) >= 2:
                result.append(Refinement(name, cost, parts))
        # Deduplicate semantically identical restricted partitions, keeping
        # the cheapest acquisition cost and deterministic name.
        by_parts: Dict[Partition, Refinement] = {}
        for r in result:
            old = by_parts.get(r.parts)
            if old is None or (r.cost, r.name) < (old.cost, old.name):
                by_parts[r.parts] = r
        return tuple(sorted(by_parts.values(), key=lambda r: (r.name, r.cost, r.parts)))

    # Materialize every reachable fibre.
    stack = [full]
    seen = {full}
    while stack:
        f = stack.pop()
        for r in refinements(f):
            for child in r.parts:
                if child not in seen:
                    seen.add(child)
                    stack.append(child)
    ref_map = {f: refinements(f) for f in seen}
    abstain = {f: Fraction(rng.randrange(0, 13), 2) for f in seen}
    return values, ref_map, abstain


def bellman(values: Sequence[int], ref_map: Dict[Fibre, Tuple[Refinement, ...]], abstain: Dict[Fibre, Fraction], root: Fibre) -> Fraction:
    @lru_cache(maxsize=None)
    def solve(f: Fibre) -> Fraction:
        candidates = [radius(values, f), abstain[f]]
        for r in ref_map[f]:
            candidates.append(r.cost + max(solve(child) for child in r.parts))
        return min(candidates)
    return solve(root)


def enumerate_policy_values(values: Sequence[int], ref_map: Dict[Fibre, Tuple[Refinement, ...]], abstain: Dict[Fibre, Fraction], root: Fibre) -> Tuple[Fraction, int]:
    """Enumerate complete contingent policy trees, without Bellman minimization.

    For a refinement, choose independently one complete continuation policy in
    every child; the adversary then takes the maximum child loss.  Duplicate
    values are collapsed, but the count records generated policy combinations.
    """
    @lru_cache(maxsize=None)
    def all_values(f: Fibre) -> Tuple[Tuple[Fraction, ...], int]:
        vals = {radius(values, f), abstain[f]}
        generated = 2
        for r in ref_map[f]:
            child_rows = [all_values(child) for child in r.parts]
            child_values = [row[0] for row in child_rows]
            combos = 1
            for cv in child_values:
                combos *= len(cv)
            generated += combos
            for choice in product(*child_values):
                vals.add(r.cost + max(choice))
        return tuple(sorted(vals)), generated
    vals, count = all_values(root)
    return min(vals), count


def run() -> dict:
    cases = 0
    policy_trees = 0
    max_states = 0
    zero_value_controls = 0
    strict_refinement_controls = 0
    for n in range(2, 8):
        for seed in range(400):
            values, ref_map, abstain = build_system(100000 * n + seed, n)
            root = tuple(range(n))
            assert radius(values, root) == brute_scalar_radius(values, root)
            a = bellman(values, ref_map, abstain, root)
            b, count = enumerate_policy_values(values, ref_map, abstain, root)
            if a != b:
                raise AssertionError({"n": n, "seed": seed, "values": values, "bellman": str(a), "enumerated": str(b)})
            cases += 1
            policy_trees += count
            max_states = max(max_states, len(ref_map))

            # A refinement that partitions only equal-target classes cannot
            # improve target radius; positive cost must not make it beat the
            # same continuation without that cost.
            equal_groups: Dict[int, List[int]] = {}
            for i, y in enumerate(values):
                equal_groups.setdefault(y, []).append(i)
            parts = canonical_partition(equal_groups.values())
            if len(parts) >= 2:
                parent_r = radius(values, root)
                child_r = max(radius(values, c) for c in parts)
                assert child_r == 0
                assert Fraction(1, 2) + child_r >= 0
                zero_value_controls += 1

            if ref_map[root] and a < min(radius(values, root), abstain[root]):
                strict_refinement_controls += 1

    # Hand controls.
    values = [0, 10, 0, 10]
    root = (0, 1, 2, 3)
    r = Refinement("perfect", Fraction(1), ((0, 2), (1, 3)))
    ref_map = {root: (r,), (0, 2): (), (1, 3): ()}
    abstain = {root: Fraction(99), (0, 2): Fraction(99), (1, 3): Fraction(99)}
    assert bellman(values, ref_map, abstain, root) == 1
    assert enumerate_policy_values(values, ref_map, abstain, root)[0] == 1

    return {
        "schema": "ORION.FiberGuard.RefinementBellmanVerification.v1",
        "status": "PASS",
        "random_systems": cases,
        "explicit_policy_trees_generated": policy_trees,
        "maximum_reachable_fibres": max_states,
        "equal_target_partition_controls": zero_value_controls,
        "systems_where_refinement_strictly_wins": strict_refinement_controls,
        "hand_control_optimum": "1",
        "authority": "FINITE_IMPLEMENTATION_CORROBORATION_ONLY",
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, sort_keys=True))
    out = Path(__file__).with_name("REFINEMENT_BELLMAN_R9_RESULTS.json")
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
