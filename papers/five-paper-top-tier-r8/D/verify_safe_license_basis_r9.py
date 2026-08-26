#!/usr/bin/env python3
"""Exact reduction and algorithm audit for the Minimum Safe License Basis problem."""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "ORION.TypedAuthority.SafeLicenseBasisR9.Results.v1"
INF = 10**9


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Rule:
    body: tuple[str, ...]
    head: str
    cap: frozenset[int]


@dataclass(frozen=True)
class TypedProgram:
    claims: tuple[str, ...]
    licenses: tuple[int, ...]
    seeds: dict[str, frozenset[int]]
    rules: tuple[Rule, ...]


def closure_for_license(program: TypedProgram, license_id: int) -> frozenset[str]:
    reached = {
        claim
        for claim, licenses in program.seeds.items()
        if license_id in licenses
    }
    changed = True
    while changed:
        changed = False
        for rule in program.rules:
            if license_id not in rule.cap or rule.head in reached:
                continue
            if all(premise in reached for premise in rule.body):
                reached.add(rule.head)
                changed = True
    return frozenset(reached)


def build_set_cover_program(universe_size: int, family: Sequence[int]) -> TypedProgram:
    claims = tuple(
        [f"seed_{index}" for index in range(len(family))]
        + [f"target_{element}" for element in range(universe_size)]
    )
    licenses = tuple(range(len(family)))
    seeds = {
        f"seed_{index}": frozenset({index})
        for index in range(len(family))
    }
    rules = []
    for index, subset_mask in enumerate(family):
        for element in range(universe_size):
            if (subset_mask >> element) & 1:
                rules.append(
                    Rule(
                        body=(f"seed_{index}",),
                        head=f"target_{element}",
                        cap=frozenset({index}),
                    )
                )
    return TypedProgram(claims, licenses, seeds, tuple(rules))


def coverage_from_program(
    program: TypedProgram,
    required_claims: Sequence[str],
    forbidden_claims: Sequence[str] = (),
) -> tuple[list[int], list[bool]]:
    required_index = {claim: index for index, claim in enumerate(required_claims)}
    forbidden = set(forbidden_claims)
    coverage: list[int] = []
    unsafe: list[bool] = []
    for license_id in program.licenses:
        reached = closure_for_license(program, license_id)
        mask = 0
        for claim in reached:
            index = required_index.get(claim)
            if index is not None:
                mask |= 1 << index
        coverage.append(mask)
        unsafe.append(bool(reached & forbidden))
    return coverage, unsafe


def exact_basis_dp(required_count: int, coverage: Sequence[int], unsafe: Sequence[bool]) -> int | None:
    full = (1 << required_count) - 1
    dp = [INF] * (1 << required_count)
    dp[0] = 0
    for mask, is_unsafe in zip(coverage, unsafe, strict=True):
        if is_unsafe:
            continue
        nxt = dp[:]
        for covered, value in enumerate(dp):
            if value == INF:
                continue
            merged = covered | mask
            if value + 1 < nxt[merged]:
                nxt[merged] = value + 1
        dp = nxt
    return None if dp[full] == INF else dp[full]


def exact_basis_bruteforce(
    required_count: int,
    coverage: Sequence[int],
    unsafe: Sequence[bool],
) -> int | None:
    full = (1 << required_count) - 1
    safe_indices = [index for index, flag in enumerate(unsafe) if not flag]
    for count in range(len(safe_indices) + 1):
        for chosen in itertools.combinations(safe_indices, count):
            covered = 0
            for index in chosen:
                covered |= coverage[index]
            if covered == full:
                return count
    return None


def greedy_basis_size(
    required_count: int,
    coverage: Sequence[int],
    unsafe: Sequence[bool],
) -> int | None:
    full = (1 << required_count) - 1
    remaining = full
    available = {index for index, flag in enumerate(unsafe) if not flag}
    chosen = 0
    while remaining:
        if not available:
            return None
        index = max(
            available,
            key=lambda candidate: ((coverage[candidate] & remaining).bit_count(), -candidate),
        )
        gain = coverage[index] & remaining
        if not gain:
            return None
        remaining &= ~gain
        available.remove(index)
        chosen += 1
    return chosen


def family_masks(universe_size: int, max_family_size: int | None = None):
    subsets = tuple(range(1, 1 << universe_size))
    upper = len(subsets) if max_family_size is None else min(max_family_size, len(subsets))
    for size in range(upper + 1):
        for family in itertools.combinations(subsets, size):
            yield family


def check_instance(universe_size: int, family: Sequence[int]) -> dict[str, Any]:
    program = build_set_cover_program(universe_size, family)
    targets = tuple(f"target_{element}" for element in range(universe_size))
    coverage, unsafe = coverage_from_program(program, targets)
    assert coverage == list(family)
    assert unsafe == [False] * len(family)
    optimum_dp = exact_basis_dp(universe_size, coverage, unsafe)
    optimum_brute = exact_basis_bruteforce(universe_size, coverage, unsafe)
    assert optimum_dp == optimum_brute
    greedy = greedy_basis_size(universe_size, coverage, unsafe)
    if optimum_dp is None:
        assert greedy is None
    else:
        assert greedy is not None
        harmonic = sum(1.0 / index for index in range(1, universe_size + 1))
        assert greedy <= math.ceil(harmonic * optimum_dp + 1e-12)
    return {
        "feasible": optimum_dp is not None,
        "optimum": optimum_dp,
        "greedy": greedy,
    }


def exhaustive_panels() -> dict[str, Any]:
    panels = []
    total = feasible = infeasible = 0
    for universe_size, max_family_size in ((1, None), (2, None), (3, None), (4, 6)):
        rows = 0
        rows_feasible = 0
        optimum_histogram: dict[str, int] = {}
        for family in family_masks(universe_size, max_family_size):
            result = check_instance(universe_size, family)
            rows += 1
            rows_feasible += int(result["feasible"])
            key = "INFEASIBLE" if result["optimum"] is None else str(result["optimum"])
            optimum_histogram[key] = optimum_histogram.get(key, 0) + 1
        panel = {
            "universe_size": universe_size,
            "maximum_family_size": max_family_size,
            "set_systems_checked": rows,
            "feasible": rows_feasible,
            "infeasible": rows - rows_feasible,
            "optimum_histogram": dict(sorted(optimum_histogram.items())),
            "status": "FINITE_EXACT",
        }
        panels.append(panel)
        total += rows
        feasible += rows_feasible
        infeasible += rows - rows_feasible
    return {
        "panels": panels,
        "set_systems_checked": total,
        "feasible": feasible,
        "infeasible": infeasible,
        "reduction_mismatches": 0,
        "dp_bruteforce_mismatches": 0,
        "greedy_bound_violations": 0,
    }


def random_large_panel(seed: int = 20260826, count: int = 4000) -> dict[str, Any]:
    rng = random.Random(seed)
    feasible = 0
    maximum_gap = 0
    for _ in range(count):
        universe_size = rng.randint(5, 9)
        family_size = rng.randint(1, min(12, (1 << universe_size) - 1))
        family = tuple(
            rng.sample(range(1, 1 << universe_size), family_size)
        )
        program = build_set_cover_program(universe_size, family)
        targets = tuple(f"target_{element}" for element in range(universe_size))
        coverage, unsafe = coverage_from_program(program, targets)
        optimum = exact_basis_dp(universe_size, coverage, unsafe)
        brute = exact_basis_bruteforce(universe_size, coverage, unsafe)
        assert optimum == brute
        greedy = greedy_basis_size(universe_size, coverage, unsafe)
        if optimum is None:
            assert greedy is None
            continue
        feasible += 1
        assert greedy is not None
        harmonic = sum(1.0 / index for index in range(1, universe_size + 1))
        assert greedy <= math.ceil(harmonic * optimum + 1e-12)
        maximum_gap = max(maximum_gap, greedy - optimum)
    return {
        "seed": seed,
        "instances_checked": count,
        "feasible": feasible,
        "infeasible": count - feasible,
        "maximum_greedy_additive_gap": maximum_gap,
        "mismatches": 0,
        "status": "DETERMINISTIC_GENERATED_EXACT",
    }


def unsafe_controls() -> dict[str, Any]:
    # Licenses 0..3 cover required targets as listed. License 0 also reaches the forbidden claim.
    claims = tuple([f"seed_{i}" for i in range(4)] + [f"target_{i}" for i in range(4)] + ["forbidden"])
    licenses = tuple(range(4))
    seeds = {f"seed_{i}": frozenset({i}) for i in licenses}
    rule_rows = [
        (0, "target_0"),
        (0, "target_1"),
        (0, "forbidden"),
        (1, "target_0"),
        (2, "target_1"),
        (3, "target_2"),
        (3, "target_3"),
    ]
    rules = tuple(
        Rule((f"seed_{license_id}",), head, frozenset({license_id}))
        for license_id, head in rule_rows
    )
    program = TypedProgram(claims, licenses, seeds, rules)
    targets = tuple(f"target_{i}" for i in range(4))
    coverage, unsafe = coverage_from_program(program, targets, ("forbidden",))
    safe_optimum = exact_basis_dp(4, coverage, unsafe)
    unsafe_ignored = exact_basis_dp(4, coverage, [False] * 4)
    assert coverage == [0b0011, 0b0001, 0b0010, 0b1100]
    assert unsafe == [True, False, False, False]
    assert safe_optimum == 3
    assert unsafe_ignored == 2

    impossible_program = TypedProgram(
        claims=("seed", "target", "forbidden"),
        licenses=(0,),
        seeds={"seed": frozenset({0})},
        rules=(
            Rule(("seed",), "target", frozenset({0})),
            Rule(("seed",), "forbidden", frozenset({0})),
        ),
    )
    impossible_coverage, impossible_unsafe = coverage_from_program(
        impossible_program, ("target",), ("forbidden",)
    )
    assert exact_basis_dp(1, impossible_coverage, impossible_unsafe) is None
    return {
        "unsafe_filter_changes_optimum": True,
        "optimum_ignoring_forbidden": unsafe_ignored,
        "safe_optimum": safe_optimum,
        "only_unsafe_cover_is_infeasible": True,
        "status": "PASS",
    }


def main() -> None:
    exhaustive = exhaustive_panels()
    generated = random_large_panel()
    controls = unsafe_controls()
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "problem": {
            "name": "MINIMUM_SAFE_LICENSE_BASIS",
            "input": "finite positive typed authority graph, candidate licenses, required and forbidden operational claims, and budget k",
            "question": "is there a set of at most k licenses whose typed closures cover every required claim and no forbidden claim",
            "full_map_compression": False,
            "operational_portfolio_compression": True,
        },
        "analytic_results": {
            "decision_complexity": "NP_COMPLETE",
            "hardness_restriction": "acyclic depth-one unary rules, singleton caps, no refutations, and no forbidden claims",
            "membership_certificate": "selected license IDs; each selected projection is checked by linear Horn closure",
            "exact_equivalence": "discard licenses reaching a forbidden claim, then solve set cover on required-claim reachability sets",
            "greedy_approximation": "H_m for m required claims",
            "exact_parameterized_algorithm": "O(|Lambda| M + |Lambda| 2^m) time and O(2^m) memory after closure construction",
        },
        "exhaustive_controls": exhaustive,
        "generated_controls": generated,
        "forbidden_claim_controls": controls,
        "prior_art_boundary": {
            "set_cover_np_completeness_is_established": True,
            "greedy_harmonic_approximation_is_established": True,
            "generic_set_cover_hardness_is_not_claimed_as_novel": True,
            "residual_claim": "typed noninterference identifies the operational license-basis problem exactly with safe set cover and supplies typed certificates and fail-closed forbidden filtering",
        },
        "authority": {
            "analytic_theorem_all_finite_positive_programs": True,
            "bounded_verifier_corroborates_reduction_and_algorithms": True,
            "external_complexity_review": False,
            "real_policy_utility": False,
            "grants_journal_authority": False,
        },
        "terminal": "D_SAFE_LICENSE_BASIS_NP_COMPLETE__EXACT_SET_COVER_REDUCTION_AND_BOUNDED_AUDIT_PASS",
    }
    result["content_sha256"] = digest(result)
    output = Path(__file__).with_name("SAFE_LICENSE_BASIS_R9_RESULTS.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
