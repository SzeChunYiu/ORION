#!/usr/bin/env python3
"""Exact finite checks for the FiberGuard R15 coverage-tax theory."""
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

SCHEMA = "ORION.FiberGuard.CoverageTax.R15.v1"
SOURCE_BASE_COMMIT = "29edf9936fe56cd3720d78e6be2542106f2671fd"
SEED = 20260826
TERMINAL = "FIBERGUARD_COVERAGE_TAX_R15_PASS"
getcontext().prec = 50


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compositions(total: int, parts: int) -> Iterable[tuple[int, ...]]:
    if parts == 1:
        yield (total,)
        return
    for first in range(1, total - parts + 2):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def mean_fraction(values: Iterable[int | Fraction]) -> Fraction:
    rows = tuple(Fraction(value) for value in values)
    return sum(rows, Fraction(0)) / len(rows)


def coverage_tax(
    seen: tuple[bool, ...],
    feature_cost: tuple[int, ...],
    fallback_regret: tuple[int, ...],
    deployed_regret: tuple[int, ...],
) -> dict[str, Fraction]:
    if not (len(seen) == len(feature_cost) == len(fallback_regret) == len(deployed_regret)):
        raise ValueError("all vectors must have one common length")
    if not seen:
        raise ValueError("nonempty subject required")
    if any(not flag and deployed_regret[i] != fallback_regret[i] for i, flag in enumerate(seen)):
        raise ValueError("unseen states must use the frozen fallback")
    n = len(seen)
    q = Fraction(sum(seen), n)
    deployed_total = mean_fraction(
        feature_cost[i] + deployed_regret[i] for i in range(n)
    )
    fallback_total = mean_fraction(fallback_regret)
    mean_cost = mean_fraction(feature_cost)
    covered_saving = mean_fraction(
        (fallback_regret[i] - deployed_regret[i]) if seen[i] else 0
        for i in range(n)
    )
    conditional_saving = (
        sum(
            Fraction(fallback_regret[i] - deployed_regret[i])
            for i in range(n)
            if seen[i]
        )
        / sum(seen)
        if any(seen)
        else Fraction(0)
    )
    if deployed_total - fallback_total != mean_cost - covered_saving:
        raise AssertionError("coverage-tax identity failed")
    if covered_saving != q * conditional_saving:
        raise AssertionError("conditional coverage identity failed")
    return {
        "coverage": q,
        "deployed_minus_fallback": deployed_total - fallback_total,
        "mean_feature_cost": mean_cost,
        "covered_saving": covered_saving,
        "conditional_saving": conditional_saving,
    }


def verify_random_tax() -> dict[str, int]:
    rng = random.Random(SEED)
    systems = 3000
    pointwise_unseen_strict = 0
    catastrophic_checks = 0
    necessary_bound_checks = 0
    for _ in range(systems):
        n = rng.randint(1, 20)
        seen = tuple(bool(rng.randrange(2)) for _ in range(n))
        cost = tuple(rng.randrange(0, 8) for _ in range(n))
        fallback = tuple(rng.randrange(0, 25) for _ in range(n))
        deployed = tuple(
            rng.randrange(0, 25) if seen[i] else fallback[i] for i in range(n)
        )
        row = coverage_tax(seen, cost, fallback, deployed)
        if any((not seen[i]) and cost[i] > 0 for i in range(n)):
            if not any(
                (not seen[i])
                and cost[i] + deployed[i] > fallback[i]
                for i in range(n)
            ):
                raise AssertionError("positive unseen acquisition cost was not a strict tax")
            pointwise_unseen_strict += 1

        threshold = rng.randrange(1, 25)
        fallback_bad = tuple(value >= threshold for value in fallback)
        deployed_bad = tuple(value >= threshold for value in deployed)
        reduction = Fraction(sum(fallback_bad) - sum(deployed_bad), n)
        coverage = row["coverage"]
        if reduction > coverage:
            raise AssertionError("catastrophic-rate reduction exceeded coverage")
        catastrophic_checks += 1

        maximum_saving = max(
            [fallback[i] - deployed[i] for i in range(n) if seen[i]] or [0]
        )
        if row["deployed_minus_fallback"] < 0:
            if row["coverage"] * maximum_saving <= row["mean_feature_cost"]:
                raise AssertionError("mean improvement violated necessary coverage bound")
        necessary_bound_checks += 1
    return {
        "systems": systems,
        "pointwise_unseen_strict_tax_systems": pointwise_unseen_strict,
        "catastrophic_bound_checks": catastrophic_checks,
        "necessary_mean_bound_checks": necessary_bound_checks,
    }


def atomic_coverage_formula(probability: tuple[Fraction, ...], n: int) -> Fraction:
    return sum(p * (1 - (1 - p) ** n) for p in probability)


def brute_atomic_coverage(probability: tuple[Fraction, ...], n: int) -> Fraction:
    alphabet = tuple(range(len(probability)))
    total = Fraction(0)
    for training in itertools.product(alphabet, repeat=n):
        training_probability = Fraction(1)
        for symbol in training:
            training_probability *= probability[symbol]
        observed = set(training)
        for test in alphabet:
            if test in observed:
                total += training_probability * probability[test]
    return total


def verify_atomic_coverage() -> dict[str, int]:
    distributions = 0
    sample_sizes = 0
    exhaustive_terms = 0
    for categories in range(2, 5):
        for denominator in range(categories, 8):
            for counts in compositions(denominator, categories):
                probability = tuple(Fraction(value, denominator) for value in counts)
                distributions += 1
                for n in range(0, 5):
                    exact = atomic_coverage_formula(probability, n)
                    brute = brute_atomic_coverage(probability, n)
                    if exact != brute:
                        raise AssertionError((probability, n, exact, brute))
                    sample_sizes += 1
                    exhaustive_terms += categories ** (n + 1)
    return {
        "distributions": distributions,
        "distribution_sample_size_pairs": sample_sizes,
        "weighted_sequence_terms": exhaustive_terms,
    }


def verify_extension_impossibility() -> dict[str, int]:
    attacks = 0
    maximum_inserted_regret = 0
    for requested in range(1, 101):
        training_profiles = {"a": (0,), "b": (1,)}
        chosen = min(training_profiles, key=lambda action: max(training_profiles[action]))
        if chosen != "a" or max(training_profiles[chosen]) != 0:
            raise AssertionError("training certificate drift")
        extended_profiles = {"a": (0, requested), "b": (1, 0)}
        if training_profiles["a"] != extended_profiles["a"][:1]:
            raise AssertionError("extension changed training subject")
        if extended_profiles[chosen][1] != requested:
            raise AssertionError("requested adversarial regret not realized")
        attacks += 1
        maximum_inserted_regret = requested
    return {
        "same_signature_extensions": attacks,
        "maximum_inserted_regret": maximum_inserted_regret,
        "training_certificate_bytes_changed": 0,
    }


def regret_from_costs(costs: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    state_count = len(costs[0])
    oracle = tuple(min(action[state] for action in costs) for state in range(state_count))
    return tuple(
        tuple(action[state] - oracle[state] for state in range(state_count))
        for action in costs
    )


def lipschitz_constant(values: tuple[int, ...], coordinates: tuple[int, ...]) -> Fraction:
    best = Fraction(0)
    for left in range(len(values)):
        for right in range(left + 1, len(values)):
            distance = abs(coordinates[left] - coordinates[right])
            if distance:
                best = max(best, Fraction(abs(values[left] - values[right]), distance))
    return best


def lipschitz_upper(
    action_regret: tuple[int, ...],
    coordinates: tuple[int, ...],
    training: tuple[int, ...],
    state: int,
    constant: Fraction,
) -> Fraction:
    return min(
        Fraction(action_regret[index])
        + constant * abs(coordinates[state] - coordinates[index])
        for index in training
    )


def verify_lipschitz_certificates() -> dict[str, int]:
    rng = random.Random(SEED + 1)
    systems = 500
    action_state_bounds = 0
    monotonic_training_checks = 0
    cost_to_regret_checks = 0
    strict_underestimate_failures = 0
    for _ in range(systems):
        state_count = rng.randint(3, 10)
        action_count = rng.randint(2, 5)
        coordinates = tuple(sorted(rng.sample(range(0, 40), state_count)))
        slopes = [rng.randint(1, 5) for _ in range(action_count)]
        centers = [rng.choice(coordinates) for _ in range(action_count)]
        offsets = [rng.randint(0, 7) for _ in range(action_count)]
        costs = tuple(
            tuple(
                offsets[action] + slopes[action] * abs(x - centers[action])
                for x in coordinates
            )
            for action in range(action_count)
        )
        regret = regret_from_costs(costs)
        oracle = tuple(min(action[state] for action in costs) for state in range(state_count))
        oracle_lipschitz = lipschitz_constant(oracle, coordinates)
        training_size = rng.randint(1, state_count - 1)
        training = tuple(sorted(rng.sample(range(state_count), training_size)))
        larger = tuple(sorted(set(training) | {rng.randrange(state_count)}))
        for action in range(action_count):
            cost_lipschitz = lipschitz_constant(costs[action], coordinates)
            certified_constant = cost_lipschitz + oracle_lipschitz
            actual_regret_lipschitz = lipschitz_constant(regret[action], coordinates)
            if actual_regret_lipschitz > certified_constant:
                raise AssertionError("cost-to-regret Lipschitz conversion failed")
            cost_to_regret_checks += 1
            for state in range(state_count):
                upper = lipschitz_upper(
                    regret[action], coordinates, training, state, certified_constant
                )
                if Fraction(regret[action][state]) > upper:
                    raise AssertionError("Lipschitz upper certificate failed")
                upper_larger = lipschitz_upper(
                    regret[action], coordinates, larger, state, certified_constant
                )
                if upper_larger > upper:
                    raise AssertionError("adding training states worsened a certificate")
                action_state_bounds += 1
                monotonic_training_checks += 1

    coordinates = (0, 1)
    action_regret = (0, 2)
    training = (0,)
    valid = lipschitz_upper(action_regret, coordinates, training, 1, Fraction(2))
    invalid = lipschitz_upper(action_regret, coordinates, training, 1, Fraction(1))
    if valid != 2 or invalid != 1 or invalid >= action_regret[1]:
        raise AssertionError("underestimated-L hostile control drift")
    strict_underestimate_failures += 1
    return {
        "systems": systems,
        "action_state_upper_bounds": action_state_bounds,
        "training_monotonicity_checks": monotonic_training_checks,
        "cost_to_regret_lipschitz_checks": cost_to_regret_checks,
        "underestimated_constant_hostile_failures": strict_underestimate_failures,
    }


def decimal_text(value: Decimal) -> str:
    return format(value.normalize(), "f")


def r14_row(
    seen: int,
    total: int,
    feature_cost: str,
    fallback_mean: str,
    deployed_mean: str,
    fallback_catastrophic: str,
    deployed_catastrophic: str,
) -> dict[str, str | int]:
    q = Decimal(seen) / Decimal(total)
    aggregate_action_saving = Decimal(fallback_mean) + Decimal(feature_cost) - Decimal(deployed_mean)
    conditional_saving = aggregate_action_saving / q
    catastrophic_reduction = Decimal(fallback_catastrophic) - Decimal(deployed_catastrophic)
    if catastrophic_reduction > q:
        raise AssertionError("R14 catastrophic reduction exceeds exact-signature coverage")
    return {
        "seen": seen,
        "total": total,
        "coverage": decimal_text(q),
        "mean_feature_cost": feature_cost,
        "deployed_mean": deployed_mean,
        "fallback_mean": fallback_mean,
        "mean_improvement": decimal_text(Decimal(fallback_mean) - Decimal(deployed_mean)),
        "coverage_weighted_action_saving": decimal_text(aggregate_action_saving),
        "conditional_action_saving_on_seen_signatures": decimal_text(conditional_saving),
        "catastrophic_rate_reduction": decimal_text(catastrophic_reduction),
    }


def verify_r14_instantiation() -> dict[str, Any]:
    return {
        "official_cv": r14_row(
            52,
            1614,
            "22.974684014869887",
            "5448.31466542751",
            "5380.232187112763",
            "0.45291201982651796",
            "0.4454770755885997",
        ),
        "leave_family_out": r14_row(
            82,
            1614,
            "22.773909541511774",
            "5448.31466542751",
            "5341.5854337050805",
            "0.45291201982651796",
            "0.4423791821561338",
        ),
    }


def build_result(script_path: Path) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "terminal": TERMINAL,
        "source_base_commit": SOURCE_BASE_COMMIT,
        "implementation_sha256": sha256_file(script_path),
        "random_coverage_tax": verify_random_tax(),
        "atomic_missing_mass": verify_atomic_coverage(),
        "sample_only_extension_attack": verify_extension_impossibility(),
        "lipschitz_transfer_certificate": verify_lipschitz_certificates(),
        "R14_exact_instantiation": verify_r14_instantiation(),
        "controls": {
            "coverage_tax_identity_exact": True,
            "unseen_positive_cost_is_pointwise_tax": True,
            "catastrophic_improvement_bounded_by_coverage": True,
            "atomic_recurrence_formula_matches_exhaustive_sampling": True,
            "sample_only_certificate_has_unbounded_same_signature_extension": True,
            "cost_lipschitz_constants_induce_valid_regret_constants": True,
            "valid_lipschitz_upper_certificates_hold": True,
            "underestimated_lipschitz_constant_fails_hostile_control": True,
            "adding_training_states_cannot_worsen_lipschitz_upper_bound": True,
        },
        "authority": {
            "analytic_theorems": "PROVED_IN_ADDENDUM",
            "finite_verification": "IMPLEMENTATION_CORROBORATION_ONLY",
            "R14_terminal_preserved": "FIBERGUARD_ASLIB_HELDOUT_R14_PARTIAL_MEAN_ONLY",
            "neighborhood_metric_selected": False,
            "lipschitz_constant_externally_validated": False,
            "cross_scenario_transfer": False,
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
