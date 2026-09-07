#!/usr/bin/env python3
"""Arithmetic regression for the prime-uniform short-free support barrier.

The proof is symbolic and lives in SHORTFREE_COMPLEMENT_SUPPORT_BARRIER_V1.md.
This script checks the parity, capacity, complement-length, coordinate-embedding,
and projective-direction formulas over a broad finite parameter grid.
"""

from __future__ import annotations

import argparse
import json
from typing import List


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 1
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-prime", type=int, default=401)
    parser.add_argument("--max-k", type=int, default=80)
    args = parser.parse_args()

    primes: List[int] = [p for p in range(5, args.max_prime + 1) if is_prime(p)]
    cases = 0

    for p in primes:
        for k in range(2, args.max_k + 1):
            lower_numerator = (2 * k + 5) * p - 5
            assert lower_numerator % 2 == 0
            lower_line = lower_numerator // 2
            critical_length = lower_line + 1
            assert critical_length == ((2 * k + 5) * p - 3) // 2

            # Supports at most k+2 cannot carry the critical length at all.
            capacity_k_plus_2 = (k + 2) * (p - 1)
            assert critical_length - capacity_k_plus_2 == (p + 2 * k + 1) // 2
            assert capacity_k_plus_2 < critical_length

            # At support k+3, either capacity already fails or the p-complement
            # is an embedded zero-sum of forbidden length (p+3)/2.
            delta_numerator = p - 2 * k - 3
            assert delta_numerator % 2 == 0
            delta = delta_numerator // 2
            capacity_k_plus_3 = (k + 3) * (p - 1)
            assert capacity_k_plus_3 - critical_length == delta
            if delta < 0:
                assert capacity_k_plus_3 < critical_length
            else:
                complement_length = (k + 3) * p - critical_length
                assert complement_length == (p + 3) // 2
                assert complement_length <= p
                max_complement_multiplicity = delta + 1
                min_original_multiplicity = p - 1 - delta
                assert max_complement_multiplicity <= min_original_multiplicity
                assert 2 * delta <= p - 2

            # Every projective direction contains at most p-1 terms.
            direction_floor = (critical_length + p - 2) // (p - 1)
            if p >= 2 * k + 3:
                assert direction_floor == k + 3
            else:
                assert p <= 2 * k + 1
                assert direction_floor >= k + 4

            cases += 1

    # The two C_7^3 pair products in the length-19 corridors receive a bonus
    # support-six lower bound from the same complement lemma.
    p = 7
    corridor_checks = {}
    for label, length, short_threshold in (
        ("8,10,19_pair_10_plus_19", 29, 9),
        ("9,9,19_pair_9_plus_19", 28, 8),
    ):
        support = 5
        delta = support * (p - 1) - length
        complement_length = support * p - length
        assert delta >= 0
        assert complement_length == support + delta
        assert complement_length <= short_threshold
        assert 2 * delta <= p - 2
        corridor_checks[label] = {
            "pair_length": length,
            "short_free_through": short_threshold,
            "support_5_deficit": delta,
            "embedded_complement_length": complement_length,
            "conclusion": "support_at_least_6",
        }

    print(
        json.dumps(
            {
                "checked_primes": len(primes),
                "largest_prime": primes[-1] if primes else None,
                "checked_k_values_per_prime": max(0, args.max_k - 1),
                "parameter_cases": cases,
                "corridor_checks": corridor_checks,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
