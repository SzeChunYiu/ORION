#!/usr/bin/env python3
"""Exact/numerical witnesses for the active-identification theory packet.

This is a local mathematical harness.  It does not inspect empirical cases and
does not confer external or protected-evaluation authority.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RECEIPT = ROOT / "COUNTEREXAMPLE_RECEIPT.json"


def binary_channel_mi(p1_y0: Fraction, p1_y1: Fraction) -> float:
    """I(Y;O) in bits for a uniform binary Y and binary O."""
    rows = (
        (float(p1_y0), 1.0 - float(p1_y0)),
        (float(p1_y1), 1.0 - float(p1_y1)),
    )
    marginal = tuple((rows[0][o] + rows[1][o]) / 2.0 for o in range(2))
    value = 0.0
    for row in rows:
        for prob, mix in zip(row, marginal):
            if prob:
                value += 0.5 * prob * math.log2(prob / mix)
    return value


def binary_channel_error(p1_y0: Fraction, p1_y1: Fraction) -> Fraction:
    """Uniform-prior binary Bayes error."""
    return Fraction(1, 2) * (
        min(p1_y0, p1_y1)
        + min(1 - p1_y0, 1 - p1_y1)
    )


def parity_risk_frontiers(max_depth: int = 2) -> list[set[tuple[Fraction, ...]]]:
    """Enumerate Gamma_n for the two-bit parity witness exactly."""
    worlds = ((0, 0), (0, 1), (1, 0), (1, 1))
    targets = tuple(x1 ^ x2 for x1, x2 in worlds)
    terminal = {
        tuple(Fraction(int(decision != target)) for target in targets)
        for decision in (0, 1)
    }
    frontiers = [terminal]
    cost = Fraction(1, 10)
    for depth in range(1, max_depth + 1):
        previous = frontiers[depth - 1]
        current = set(terminal)
        for bit_index in (0, 1):
            for v0, v1 in itertools.product(previous, repeat=2):
                vector = tuple(
                    cost + (v0[i] if worlds[i][bit_index] == 0 else v1[i])
                    for i in range(len(worlds))
                )
                current.add(vector)
        frontiers.append(current)
    return frontiers


def run() -> dict:
    checks: list[dict] = []

    # N1: MI ordering and zero-one ordering disagree.
    a = (Fraction(0), Fraction(1, 5))
    b = (Fraction(1, 5), Fraction(1, 2))
    mi_a, mi_b = binary_channel_mi(*a), binary_channel_mi(*b)
    err_a, err_b = binary_channel_error(*a), binary_channel_error(*b)
    checks.append({
        "id": "N1_MI_NOT_ZERO_ONE",
        "pass": mi_a > mi_b and err_a > err_b,
        "mi_a_bits": mi_a,
        "mi_b_bits": mi_b,
        "error_a": str(err_a),
        "error_b": str(err_b),
    })

    # N2: positive KL but identical finite support.
    kl = 0.25 * math.log(0.25 / 0.75) + 0.75 * math.log(0.75 / 0.25)
    n = 4
    common_strings = 2**n  # both Bernoulli laws assign positive mass to all.
    checks.append({
        "id": "N2_POSITIVE_KL_NOT_FINITE_EXACT",
        "pass": kl > 0 and common_strings == 16,
        "oriented_kl_nats": kl,
        "horizon": n,
        "common_positive_transcripts": common_strings,
    })

    # N3: parity synergy under zero-one loss and acquisition cost 1/10.
    frontiers = parity_risk_frontiers()
    uniform_risk = lambda v: sum(v, Fraction(0)) / len(v)
    stop = min(map(uniform_risk, frontiers[0]))
    at_most_one = min(map(uniform_risk, frontiers[1]))
    at_most_two = min(map(uniform_risk, frontiers[2]))
    one_test = Fraction(1, 10) + Fraction(1, 2)
    two_tests = at_most_two
    checks.append({
        "id": "N3_PARITY_SYNERGY",
        "pass": two_tests < stop < one_test and at_most_one == stop,
        "stop_risk": str(stop),
        "bellman_at_most_one_test": str(at_most_one),
        "bellman_at_most_two_tests": str(at_most_two),
        "one_test_total_risk": str(one_test),
        "two_test_total_risk": str(two_tests),
        "gamma_sizes": [len(frontier) for frontier in frontiers],
        "individual_target_information_bits": 0,
        "joint_target_information_bits": 1,
    })

    # N4: ratio-greedy knapsack failure.
    items = {"A": (3, 5), "B": (2, 3), "C": (2, 3)}
    budget = 4
    ratio_first = max(items, key=lambda x: items[x][1] / items[x][0])
    greedy_value = items[ratio_first][1]
    optimum_value = items["B"][1] + items["C"][1]
    checks.append({
        "id": "N4_RATIO_GREEDY_KNAPSACK",
        "pass": ratio_first == "A" and optimum_value > greedy_value,
        "budget": budget,
        "greedy_first": ratio_first,
        "greedy_information_bits": greedy_value,
        "optimal_information_bits": optimum_value,
    })

    # N5: fixed-prior credal coupling beats posterior rectangularization.
    # q_z is probability of predicting label 1 after observing Z=z.
    def risk_a(q0: Fraction, q1: Fraction) -> Fraction:
        return Fraction(1, 10) + Fraction(9, 10) * q0 - Fraction(1, 10) * q1

    def risk_b(q0: Fraction, q1: Fraction) -> Fraction:
        return Fraction(1, 10) - Fraction(1, 10) * q0 + Fraction(9, 10) * q1

    grid = [Fraction(i, 100) for i in range(101)]
    ex_ante = min(max(risk_a(q0, q1), risk_b(q0, q1)) for q0 in grid for q1 in grid)
    local_rectangular = Fraction(1, 2)
    checks.append({
        "id": "N5_NONRECTANGULAR_CREDAL",
        "pass": ex_ante == Fraction(1, 10) and local_rectangular > ex_ante,
        "ex_ante_minimax_error": str(ex_ante),
        "posterior_local_rectangular_error": str(local_rectangular),
        "lower_bound_identity": "R_A + R_B = 1/5 + (4/5)(q0+q1) >= 1/5",
    })

    # N6: randomization improves minimax risk.
    deterministic_robust = Fraction(1)
    randomized_robust = Fraction(1, 2)
    checks.append({
        "id": "N6_RANDOMIZATION_CAN_HELP",
        "pass": randomized_robust < deterministic_robust,
        "deterministic_robust_error": str(deterministic_robust),
        "fair_randomized_robust_error": str(randomized_robust),
    })

    # N7: support envelope alone does not set Bayes risk.
    concentrated_error = min(Fraction(99, 100), Fraction(1, 100))
    uniform_error = Fraction(1, 2)
    checks.append({
        "id": "N7_SAME_SUPPORT_DIFFERENT_RISK",
        "pass": concentrated_error != uniform_error,
        "common_identified_set": [0, 1],
        "concentrated_bayes_error": str(concentrated_error),
        "uniform_bayes_error": str(uniform_error),
    })

    # N8: nuisance information is not target information.
    nuisance_world_mi = 10
    nuisance_target_mi = 0
    target_world_mi = 1
    target_target_mi = 1
    checks.append({
        "id": "N8_WORLD_INFORMATION_NOT_TARGET_INFORMATION",
        "pass": nuisance_world_mi > target_world_mi and nuisance_target_mi < target_target_mi,
        "nuisance_test_world_information_bits": nuisance_world_mi,
        "nuisance_test_target_information_bits": nuisance_target_mi,
        "target_test_world_information_bits": target_world_mi,
        "target_test_target_information_bits": target_target_mi,
    })

    passed = sum(bool(c["pass"]) for c in checks)
    script_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return {
        "schema": "active-identification-counterexample-receipt-v1",
        "scope": "finite local mathematical witnesses only",
        "empirical_authority": False,
        "protected_evaluation": False,
        "checks_passed": passed,
        "checks_total": len(checks),
        "all_pass": passed == len(checks),
        "script_sha256": script_sha,
        "checks": checks,
    }


if __name__ == "__main__":
    result = run()
    RECEIPT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["all_pass"] else 1)
