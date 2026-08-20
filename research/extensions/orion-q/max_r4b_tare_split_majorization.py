"""Deterministic checks for MAX-R4B TARE split majorization.

Scientific scope:
- verifies the frozen equal-size majorization theorem by exhaustive enumeration on
  small cases, including the hostile coefficient families frozen in the protocol;
- evaluates the theorem-optimal split on immutable public LiH coefficients copied
  from SNIPRS/hamiltonian simulation-LiH.ipynb;
- evaluates uniform and disordered Heisenberg coefficient controls.

This is not a compiled TARE/QSVT resource estimator.
"""

from __future__ import annotations

import itertools
import json
import math
import random
from statistics import mean, median

SEED = 20260820
TOL = 1e-11

# Public LiH non-identity coefficients printed by
# https://github.com/SNIPRS/hamiltonian/blob/master/simulation-LiH.ipynb
LIH = [
    -0.0013743761078958677, -0.0013743761078958677,
    -0.0013743761078958677, -0.0013743761078958677,
     0.002932996440950227,   0.002932996440950227,
     0.002932996440950227,   0.002932996440950227,
     0.011536413200774975,   0.011536413200774975,
     0.011536413200774975,   0.011536413200774975,
     0.012910780273117489,   0.012910780273117489,
     0.012910780273117489,   0.012910780273117489,
     0.08479609543670981,    0.12444770133137588,
     0.05706344223424907,    0.05706344223424907,
     0.054130445793298836,   0.054130445793298836,
     0.013243698330265952,   0.013243698330265966,
     0.1619947538800418,     0.1619947538800418,
]


def block_lambda(values: list[float]) -> float:
    m = len(values)
    return math.sqrt(m) * math.sqrt(sum(float(x) ** 2 for x in values))


def split_lambda(coeffs: list[float], groups: list[tuple[int, ...]]) -> float:
    return sum(block_lambda([abs(coeffs[i]) for i in group]) for group in groups)


def sorted_contiguous_groups(coeffs: list[float], m: int) -> list[tuple[int, ...]]:
    if len(coeffs) % m:
        raise ValueError("equal-size theorem requires m | L")
    order = sorted(range(len(coeffs)), key=lambda i: (-abs(coeffs[i]), i))
    return [tuple(order[i : i + m]) for i in range(0, len(order), m)]


def partitions_fixed_size(indices: tuple[int, ...], m: int):
    """Yield each unlabeled equal-size partition once."""
    if not indices:
        yield ()
        return
    first = indices[0]
    for companions in itertools.combinations(indices[1:], m - 1):
        group = (first,) + companions
        chosen = set(group)
        remaining = tuple(i for i in indices if i not in chosen)
        for tail in partitions_fixed_size(remaining, m):
            yield (group,) + tail


def exhaustive_case(coeffs: list[float], m: int) -> dict:
    sorted_value = split_lambda(coeffs, sorted_contiguous_groups(coeffs, m))
    optimum = math.inf
    evaluations = 0
    for partition in partitions_fixed_size(tuple(range(len(coeffs))), m):
        evaluations += 1
        optimum = min(optimum, split_lambda(coeffs, list(partition)))
    gap = sorted_value - optimum
    return {
        "L": len(coeffs),
        "m": m,
        "partition_evaluations": evaluations,
        "sorted_value": sorted_value,
        "brute_optimum": optimum,
        "gap": gap,
        "pass": gap <= TOL,
    }


def _special_coefficients(n: int) -> dict[str, list[float]]:
    repeated = [float(1 + (i // 2) % 3) for i in range(n)]
    zeros = [0.0 if i < n // 2 else float(i - n // 2 + 1) for i in range(n)]
    return {
        "all_equal": [1.0] * n,
        "repeated_magnitudes": repeated,
        "zeros": zeros,
        "one_dominant": [1.0e9] + [1.0] * (n - 1),
    }


def exhaustive_theorem_checks() -> dict:
    configs = [(6, 3, 30), (8, 4, 30), (8, 2, 30), (9, 3, 15)]
    random_ranges = [(-3.0, 2.0), (-9.0, 1.0), (-1.0, 1.0)]
    out = {}
    total_failures = 0
    total_evaluations = 0

    for n, m, trials in configs:
        rng = random.Random(SEED + n * 100 + m)
        failures = 0
        evaluations = 0
        max_abs_gap = 0.0
        random_cases = []
        for trial in range(trials):
            lo, hi = random_ranges[trial % len(random_ranges)]
            coeffs = [10 ** rng.uniform(lo, hi) for _ in range(n)]
            check = exhaustive_case(coeffs, m)
            evaluations += check["partition_evaluations"]
            max_abs_gap = max(max_abs_gap, abs(check["gap"]))
            if not check["pass"]:
                failures += 1
            random_cases.append({
                "dynamic_range_log10": [lo, hi],
                "gap": check["gap"],
                "pass": check["pass"],
            })

        hostile = {}
        for name, coeffs in _special_coefficients(n).items():
            check = exhaustive_case(coeffs, m)
            evaluations += check["partition_evaluations"]
            max_abs_gap = max(max_abs_gap, abs(check["gap"]))
            if not check["pass"]:
                failures += 1
            hostile[name] = check

        # Identity remint/permutation hostile: the objective and optimum must be
        # invariant to coefficient index identity. Use a deterministic nontrivial
        # permutation of the repeated/zero-rich case so ties are exercised too.
        remint_source = _special_coefficients(n)["zeros"]
        permutation = list(range(n))
        rng.shuffle(permutation)
        reminted = [remint_source[i] for i in permutation]
        original = exhaustive_case(remint_source, m)
        remint = exhaustive_case(reminted, m)
        evaluations += original["partition_evaluations"] + remint["partition_evaluations"]
        remint_pass = (
            original["pass"]
            and remint["pass"]
            and abs(original["sorted_value"] - remint["sorted_value"]) <= TOL
            and abs(original["brute_optimum"] - remint["brute_optimum"]) <= TOL
        )
        if not remint_pass:
            failures += 1
        hostile["identity_remint"] = {
            "permutation": permutation,
            "original_sorted_value": original["sorted_value"],
            "reminted_sorted_value": remint["sorted_value"],
            "original_brute_optimum": original["brute_optimum"],
            "reminted_brute_optimum": remint["brute_optimum"],
            "pass": remint_pass,
        }

        out[f"L{n}_m{m}"] = {
            "trials": trials,
            "random_dynamic_ranges_log10": [list(x) for x in random_ranges],
            "partition_evaluations": evaluations,
            "failures": failures,
            "max_abs_gap": max_abs_gap,
            "random_cases": random_cases,
            "hostile_cases": hostile,
        }
        total_failures += failures
        total_evaluations += evaluations

    return {
        "configs": out,
        "total_partition_evaluations": total_evaluations,
        "total_failures": total_failures,
        "all_hostile_and_random_checks_pass": total_failures == 0,
        "tolerance": TOL,
    }


def random_split_distribution(coeffs: list[float], m: int, draws: int, seed: int) -> list[float]:
    rng = random.Random(seed)
    base = list(range(len(coeffs)))
    vals = []
    for _ in range(draws):
        idx = base[:]
        rng.shuffle(idx)
        groups = [tuple(idx[i : i + m]) for i in range(0, len(idx), m)]
        vals.append(split_lambda(coeffs, groups))
    return vals


def quantile(sorted_values: list[float], q: float) -> float:
    if not 0 <= q <= 1:
        raise ValueError(q)
    if not sorted_values:
        raise ValueError("empty")
    x = (len(sorted_values) - 1) * q
    lo = int(math.floor(x))
    hi = int(math.ceil(x))
    if lo == hi:
        return sorted_values[lo]
    w = x - lo
    return sorted_values[lo] * (1 - w) + sorted_values[hi] * w


def lih_result() -> dict:
    coeffs = [abs(x) for x in LIH]
    m = 2  # 26 non-identity terms; equal-size theorem and TARE-admissible for n=4.
    optimum = split_lambda(coeffs, sorted_contiguous_groups(coeffs, m))
    random_values = sorted(random_split_distribution(coeffs, m, 100_000, SEED))
    l1 = sum(coeffs)
    return {
        "source": "SNIPRS/hamiltonian simulation-LiH.ipynb stdout, non-identity Pauli terms",
        "L": len(coeffs),
        "block_size": m,
        "pauli_l1": l1,
        "majorization_optimal_split_lambda": optimum,
        "optimal_split_overhead_vs_pauli_l1": optimum / l1 - 1.0,
        "random_split_draws": len(random_values),
        "random_split_mean": mean(random_values),
        "random_split_p05": quantile(random_values, 0.05),
        "random_split_p50": quantile(random_values, 0.50),
        "random_split_p95": quantile(random_values, 0.95),
        "optimal_reduction_vs_random_mean": 1.0 - optimum / mean(random_values),
    }


def uniform_heisenberg_control() -> dict:
    # 8-site 1D Heisenberg-style coefficient list with four equally weighted terms/site.
    coeffs = [0.5] * 32
    m = 8
    optimal = split_lambda(coeffs, sorted_contiguous_groups(coeffs, m))
    l1 = sum(coeffs)
    return {
        "L": len(coeffs),
        "block_size": m,
        "pauli_l1": l1,
        "majorization_optimal_split_lambda": optimal,
        "tie_expected": True,
        "exact_tie_to_l1": abs(optimal - l1) <= 1e-12,
    }


def disordered_heisenberg_panel() -> dict:
    # Physical-model synthetic control: four 8-term coupling/field sectors with
    # positive disorder spanning one decade. No empirical-result authority.
    reductions = []
    overheads = []
    for seed in range(61_000, 61_100):
        rng = random.Random(seed)
        coeffs = [0.5 * 10 ** rng.uniform(-1.0, 0.0) for _ in range(32)]
        m = 8
        optimal = split_lambda(coeffs, sorted_contiguous_groups(coeffs, m))
        random_vals = random_split_distribution(coeffs, m, 2_000, seed + 999)
        random_mean = mean(random_vals)
        reductions.append(1.0 - optimal / random_mean)
        overheads.append(optimal / sum(coeffs) - 1.0)
    return {
        "subjects": 100,
        "block_size": 8,
        "random_splits_per_subject": 2_000,
        "median_optimal_reduction_vs_random_mean": median(reductions),
        "min_optimal_reduction_vs_random_mean": min(reductions),
        "max_optimal_reduction_vs_random_mean": max(reductions),
        "median_optimal_overhead_vs_pauli_l1": median(overheads),
        "authority": "physical_model_synthetic_control_only",
    }


def main() -> dict:
    exhaustive = exhaustive_theorem_checks()
    theorem_gate_pass = exhaustive["all_hostile_and_random_checks_pass"]
    result = {
        "schema": "ORIONQ.MAXR4BTARESplitMajorizationResult.v1",
        "seed": SEED,
        "theorem": "equal-size sorted-contiguous coefficient partition minimizes split-TARE outer-LCU subnormalization",
        "exhaustive_checks": exhaustive,
        "lih_public_subject": lih_result(),
        "uniform_heisenberg_control": uniform_heisenberg_control(),
        "disordered_heisenberg_panel": disordered_heisenberg_panel(),
        "theorem_gate_pass": theorem_gate_pass,
        "terminal": (
            "R4B_TARE_SPLIT_MAJORISATION_THEOREM_SUPPORTED__COEFFICIENT_COORDINATE_ONLY"
            if theorem_gate_pass
            else "R4B_TARE_SPLIT_MAJORISATION_HOSTILE_CHECK_FAILED__THEOREM_NOT_PROMOTED"
        ),
        "authority": "proof_plus_deterministic_check; not compiled-resource or novelty authority",
        "hard_boundary": "Pauli/Restore structure can trade circuit cost against the coefficient-optimal Lambda; theorem does not claim total-resource optimality.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if not theorem_gate_pass:
        raise SystemExit(1)
    return result


if __name__ == "__main__":
    main()
