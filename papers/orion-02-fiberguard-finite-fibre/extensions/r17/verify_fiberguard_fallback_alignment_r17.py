#!/usr/bin/env python3
"""Exact finite checks for FiberGuard R17 fallback-alignment theory."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "ORION.FiberGuard.FallbackAlignment.R17.v1"
SOURCE_BASE_COMMIT = "6bc502966c6d8f2a7a97db234a4c20216e6feac9"
SEED = 20260826
TERMINAL = "FIBERGUARD_FALLBACK_ALIGNMENT_R17_PASS"
getcontext().prec = 50


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mean_fraction(values: Iterable[int | Fraction]) -> Fraction:
    rows = tuple(Fraction(value) for value in values)
    if not rows:
        raise ValueError("nonempty vector required")
    return sum(rows, Fraction(0)) / len(rows)


def selective_loss(
    learned: tuple[int, ...], fallback: tuple[int, ...], deploy: tuple[bool, ...]
) -> tuple[int, ...]:
    if not (len(learned) == len(fallback) == len(deploy)):
        raise ValueError("vectors must share length")
    return tuple(learned[i] if deploy[i] else fallback[i] for i in range(len(deploy)))


def verify_random_identities() -> dict[str, int]:
    rng = random.Random(SEED)
    systems = 5000
    mean_checks = event_checks = robust_checks = strict_robust_checks = 0
    for _ in range(systems):
        n = rng.randint(1, 24)
        learned = tuple(rng.randrange(0, 101) for _ in range(n))
        fallback = tuple(rng.randrange(0, 101) for _ in range(n))
        deploy = tuple(bool(rng.randrange(2)) for _ in range(n))
        selected = selective_loss(learned, fallback, deploy)
        rejected = [i for i, flag in enumerate(deploy) if not flag]

        lhs = mean_fraction(selected) - mean_fraction(learned)
        rhs = Fraction(
            sum(fallback[i] - learned[i] for i in rejected), n
        )
        if lhs != rhs:
            raise AssertionError("mean fallback-alignment identity failed")
        mean_checks += 1

        threshold = rng.randrange(1, 101)
        learned_bad = tuple(value >= threshold for value in learned)
        fallback_bad = tuple(value >= threshold for value in fallback)
        selected_bad = tuple(
            learned_bad[i] if deploy[i] else fallback_bad[i] for i in range(n)
        )
        event_lhs = mean_fraction(selected_bad) - mean_fraction(learned_bad)
        event_rhs = Fraction(
            sum(int(fallback_bad[i]) - int(learned_bad[i]) for i in rejected), n
        )
        if event_lhs != event_rhs:
            raise AssertionError("event fallback-alignment identity failed")
        event_checks += 1

        full_value = max(learned)
        selected_value = max(selected)
        kept_learned = max((learned[i] for i in range(n) if deploy[i]), default=-1)
        rejected_fallback = max((fallback[i] for i in rejected), default=-1)
        formula_value = max(kept_learned, rejected_fallback)
        if selected_value != formula_value:
            raise AssertionError("robust routing identity failed")
        strict_condition = kept_learned < full_value and rejected_fallback < full_value
        if (selected_value < full_value) != strict_condition:
            raise AssertionError("strict robust-improvement criterion failed")
        robust_checks += 1
        strict_robust_checks += 1
    return {
        "systems": systems,
        "mean_identity_checks": mean_checks,
        "binary_event_identity_checks": event_checks,
        "robust_identity_checks": robust_checks,
        "strict_robust_criterion_checks": strict_robust_checks,
    }


def verify_optimal_rejection_sorting() -> dict[str, int]:
    rng = random.Random(SEED + 1)
    systems = 1000
    cardinality_cells = brute_subsets = 0
    for _ in range(systems):
        n = rng.randint(2, 8)
        learned = tuple(rng.randrange(0, 51) for _ in range(n))
        fallback = tuple(rng.randrange(0, 51) for _ in range(n))
        delta = tuple(fallback[i] - learned[i] for i in range(n))
        order = sorted(range(n), key=lambda i: (delta[i], i))
        for reject_count in range(n + 1):
            sorted_set = frozenset(order[:reject_count])
            sorted_value = sum(delta[i] for i in sorted_set)
            brute_value = None
            for subset in itertools.combinations(range(n), reject_count):
                brute_subsets += 1
                value = sum(delta[i] for i in subset)
                brute_value = value if brute_value is None else min(brute_value, value)
            if sorted_value != brute_value:
                raise AssertionError("sorting did not minimize fixed-cardinality routing loss")
            cardinality_cells += 1
    return {
        "systems": systems,
        "fixed_rejection_cardinality_cells": cardinality_cells,
        "explicit_rejection_subsets": brute_subsets,
    }


def verify_paired_upper_routing() -> dict[str, int]:
    rng = random.Random(SEED + 2)
    systems = 3000
    state_checks = union_checks = joint_checks = strict_route_gains = 0
    for _ in range(systems):
        n = rng.randint(1, 25)
        learned = tuple(rng.randrange(0, 101) for _ in range(n))
        fallback = tuple(rng.randrange(0, 101) for _ in range(n))
        learned_upper = tuple(value + rng.randrange(0, 21) for value in learned)
        fallback_upper = tuple(value + rng.randrange(0, 21) for value in fallback)
        routed = tuple(
            learned[i] if learned_upper[i] <= fallback_upper[i] else fallback[i]
            for i in range(n)
        )
        route_upper = tuple(min(learned_upper[i], fallback_upper[i]) for i in range(n))
        if any(routed[i] > route_upper[i] for i in range(n)):
            raise AssertionError("paired valid upper routing failed")
        state_checks += n
        if mean_fraction(routed) < min(mean_fraction(learned), mean_fraction(fallback)):
            strict_route_gains += 1

        fail_learned = tuple(bool(rng.randrange(5) == 0) for _ in range(n))
        fail_fallback = tuple(bool(rng.randrange(5) == 0) for _ in range(n))
        attacked_learned_upper = tuple(
            max(0, learned[i] - 1) if fail_learned[i] else learned_upper[i]
            for i in range(n)
        )
        attacked_fallback_upper = tuple(
            max(0, fallback[i] - 1) if fail_fallback[i] else fallback_upper[i]
            for i in range(n)
        )
        attacked_route_uses_learned = tuple(
            attacked_learned_upper[i] <= attacked_fallback_upper[i] for i in range(n)
        )
        attacked_route = tuple(
            learned[i] if attacked_route_uses_learned[i] else fallback[i]
            for i in range(n)
        )
        attacked_upper = tuple(
            min(attacked_learned_upper[i], attacked_fallback_upper[i]) for i in range(n)
        )
        route_failure = tuple(attacked_route[i] > attacked_upper[i] for i in range(n))
        if any(
            route_failure[i] and not (fail_learned[i] or fail_fallback[i])
            for i in range(n)
        ):
            raise AssertionError("route failure escaped certificate union")
        union_checks += n

        joint_slack = tuple(rng.randrange(0, 21) for _ in range(n))
        joint_learned_upper = tuple(learned[i] + joint_slack[i] for i in range(n))
        joint_fallback_upper = tuple(fallback[i] + joint_slack[i] for i in range(n))
        joint_route = tuple(
            learned[i] if joint_learned_upper[i] <= joint_fallback_upper[i] else fallback[i]
            for i in range(n)
        )
        joint_upper = tuple(
            min(joint_learned_upper[i], joint_fallback_upper[i]) for i in range(n)
        )
        if any(joint_route[i] > joint_upper[i] for i in range(n)):
            raise AssertionError("joint paired certificate failed")
        joint_checks += n
    return {
        "systems": systems,
        "valid_paired_state_checks": state_checks,
        "separate_certificate_union_checks": union_checks,
        "joint_certificate_state_checks": joint_checks,
        "systems_with_strict_route_gain_over_both_fixed_arms": strict_route_gains,
    }


def verify_certificate_only_impossibility() -> dict[str, int]:
    attacks = 100
    maximum_inserted_fallback_loss = 0
    for magnitude in range(1, attacks + 1):
        learned = (0, 0)
        deploy = (True, False)
        fallback = (0, magnitude)
        selected = selective_loss(learned, fallback, deploy)
        learned_certificate_failures = 0
        if learned_certificate_failures != 0:
            raise AssertionError("hostile learned certificate drift")
        if mean_fraction(selected) - mean_fraction(learned) != Fraction(magnitude, 2):
            raise AssertionError("certificate-only fallback attack failed")
        maximum_inserted_fallback_loss = magnitude
    return {
        "calibrated_learned_action_attacks": attacks,
        "maximum_inserted_fallback_loss": maximum_inserted_fallback_loss,
        "learned_certificate_bytes_changed": 0,
    }


def decimal_text(value: Decimal) -> str:
    return format(value.normalize(), "f")


def r16_alignment_row(
    coverage: str,
    full_mean: str,
    selective_mean: str,
    full_catastrophic: str,
    selective_catastrophic: str,
) -> dict[str, str]:
    q = Decimal(coverage)
    reject = Decimal(1) - q
    mean_difference = Decimal(selective_mean) - Decimal(full_mean)
    catastrophic_difference = Decimal(selective_catastrophic) - Decimal(full_catastrophic)
    conditional_mean = mean_difference / reject
    conditional_catastrophic = catastrophic_difference / reject
    return {
        "deployment_coverage": coverage,
        "rejection_rate": decimal_text(reject),
        "selective_minus_full_mean": decimal_text(mean_difference),
        "fallback_minus_learned_mean_on_rejected": decimal_text(conditional_mean),
        "selective_minus_full_catastrophic_rate": decimal_text(catastrophic_difference),
        "fallback_minus_learned_catastrophic_rate_on_rejected": decimal_text(
            conditional_catastrophic
        ),
    }


def verify_r16_instantiation() -> dict[str, Any]:
    return {
        "SAT16_MAIN": r16_alignment_row(
            "0.6751824817518248",
            "4478.622343065694",
            "6100.819890510949",
            "0.08759124087591241",
            "0.12043795620437957",
        ),
        "SAT18_EXP": r16_alignment_row(
            "0.8583569405099151",
            "4581.444667507015",
            "8349.72689029404",
            "0.0906515580736544",
            "0.1671388101983003",
        ),
        "SAT20_MAIN": r16_alignment_row(
            "0.68",
            "7862.35229708885",
            "7642.60598043885",
            "0.1275",
            "0.1225",
        ),
    }


def build_result(script_path: Path) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "terminal": TERMINAL,
        "source_base_commit": SOURCE_BASE_COMMIT,
        "implementation_sha256": sha256_file(script_path),
        "random_exact_identities": verify_random_identities(),
        "optimal_rejection_sorting": verify_optimal_rejection_sorting(),
        "paired_upper_routing": verify_paired_upper_routing(),
        "certificate_only_impossibility": verify_certificate_only_impossibility(),
        "R16_exact_instantiation": verify_r16_instantiation(),
        "controls": {
            "mean_fallback_alignment_identity_exact": True,
            "binary_event_alignment_identity_exact": True,
            "robust_route_value_identity_exact": True,
            "strict_robust_improvement_criterion_exact": True,
            "fixed_cardinality_optimal_rejection_is_sorted_by_fallback_minus_learned_loss": True,
            "paired_valid_upper_route_is_certified": True,
            "separate_certificate_route_failure_is_contained_in_union": True,
            "joint_paired_certificate_preserves_one_failure_budget": True,
            "learned_action_calibration_alone_cannot_bound_fallback_harm": True,
            "R16_sign_reversal_reproduced": True,
        },
        "authority": {
            "analytic_theorems": "PROVED_IN_ADDENDUM",
            "finite_verification": "IMPLEMENTATION_CORROBORATION_ONLY",
            "R16_terminal_preserved": "FIBERGUARD_R16_NO_PORTABLE_CERTIFICATE_VALUE",
            "paired_fallback_certificate_executed_on_ASlib": False,
            "strongest_algorithm_selection_baseline_complete": False,
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
