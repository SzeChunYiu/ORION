#!/usr/bin/env python3
"""Independent verifier for the packing-defect core arithmetic.

This implementation uses a sieve, generating-function dynamic programming and
direct atom-length enumeration rather than the recursive partition generator in
the primary checker.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import defaultdict
from fractions import Fraction
from typing import DefaultDict, Dict, Iterable, List, Sequence, Tuple


def primes_through(limit: int) -> List[int]:
    sieve = [True] * (limit + 1)
    if limit >= 0:
        sieve[0] = False
    if limit >= 1:
        sieve[1] = False
    for value in range(2, int(limit**0.5) + 1):
        if sieve[value]:
            for multiple in range(value * value, limit + 1, value):
                sieve[multiple] = False
    return [value for value in range(5, limit + 1) if sieve[value]]


def bounded_partition_distribution(total: int, maximum: int) -> Dict[int, int]:
    """Count partitions by number of parts using a generating-function DP."""

    dp: DefaultDict[Tuple[int, int], int] = defaultdict(int)
    dp[(0, 0)] = 1
    for part in range(1, maximum + 1):
        updated = defaultdict(int, dp)
        for current_total in range(total + 1):
            for current_parts in range(total + 1):
                count = dp.get((current_total, current_parts), 0)
                if not count:
                    continue
                copies = 1
                while current_total + copies * part <= total:
                    updated[(current_total + copies * part, current_parts + copies)] += count
                    copies += 1
        dp = updated
    return {
        parts: dp[(total, parts)]
        for parts in range(1, total + 1)
        if dp[(total, parts)]
    }


def direct_corridors() -> List[Tuple[int, int, int]]:
    out = []
    for a, short_bound in ((8, 10), (9, 12), (10, 10)):
        for b in range(a, 20):
            for c in range(b, 20):
                if a + b + c == 37 and b <= short_bound:
                    out.append((a, b, c))
    return sorted(out)


def compositions(total: int, parts: int, low: int, high: int) -> Iterable[Tuple[int, ...]]:
    """Ordered compositions, used only for independent cost-move identities."""

    if parts == 0:
        if total == 0:
            yield ()
        return
    for first in range(low, high + 1):
        rest = total - first
        if (parts - 1) * low <= rest <= (parts - 1) * high:
            for tail in compositions(rest, parts - 1, low, high):
                yield (first,) + tail


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-prime", type=int, default=401)
    parser.add_argument("--max-m", type=int, default=80)
    parser.add_argument("--max-q", type=int, default=80)
    args = parser.parse_args()

    primes = primes_through(args.max_prime)
    arithmetic_checks = 0

    for p in primes:
        M = Fraction(5 * p - 5, 2)
        assert M.denominator == 1
        M_int = int(M)
        assert Fraction(9 * p - 5, 2) - 2 * p == M
        assert 3 * p - 2 - p <= M

        for m in range(3, args.max_m + 1):
            for q in range(1, args.max_q + 1):
                N = p * m + M_int + q

                # Brute the only two support values that matter to the theorem.
                for support in (m + 2, m + 3):
                    deficit = support * (p - 1) - N
                    if support == m + 2:
                        assert deficit < 0
                    else:
                        expected = (p - 1) // 2 - m - q
                        assert deficit == expected
                        if deficit >= 0:
                            complement = support * p - N
                            assert complement == support + deficit
                            assert complement <= p
                            assert 2 * deficit <= p - 2

                # Check the displayed projective-direction formula with exact rationals.
                ratio = Fraction(N, p - 1)
                displayed = Fraction(m, 1) + Fraction(5, 2) + Fraction(m + q, p - 1)
                assert ratio == displayed
                direction_floor = (ratio.numerator + ratio.denominator - 1) // ratio.denominator
                assert direction_floor >= m + 3
                arithmetic_checks += 1

    expected_distribution = {
        3: 19,
        4: 33,
        5: 37,
        6: 35,
        7: 28,
        8: 22,
        9: 15,
        10: 11,
        11: 7,
        12: 5,
        13: 3,
        14: 2,
        15: 1,
        16: 1,
    }
    full_distribution = bounded_partition_distribution(total=16, maximum=12)
    distribution = {parts: count for parts, count in full_distribution.items() if parts >= 3}
    assert distribution == expected_distribution
    assert sum(distribution.values()) == 219

    # Directly enumerate the m=3 atom lengths rather than excess partitions.
    raw_triples = [
        triple
        for triple in itertools.combinations_with_replacement(range(8, 20), 3)
        if sum(triple) == 37
    ]
    assert len(raw_triples) == 19

    expected_corridors = [
        (8, 10, 19),
        (9, 9, 19),
        (9, 10, 18),
        (9, 11, 17),
        (9, 12, 16),
        (10, 10, 17),
    ]
    assert direct_corridors() == expected_corridors
    assert set(expected_corridors) <= set(raw_triples)

    # Independent finite stress test of c^T g = -p 1^T g.  Two atomic
    # factorizations of the same term length define a kernel move at the
    # length-row level; the excess-cost difference must be exactly -p times
    # the gain in factorization length.
    move_checks = 0
    for p in (5, 7, 11, 13):
        low, high = p + 1, 3 * p - 2
        for total in range(2 * low, 3 * high + 1):
            factorizations: Dict[int, List[Tuple[int, ...]]] = {}
            for parts in range(2, 5):
                rows = list(compositions(total, parts, low, high))
                if rows:
                    # A bounded prefix is enough: this checks the identity, not coverage.
                    factorizations[parts] = rows[:8]
            for old_parts, old_rows in factorizations.items():
                for new_parts, new_rows in factorizations.items():
                    if new_parts <= old_parts:
                        continue
                    for old in old_rows:
                        for new in new_rows:
                            old_cost = sum(length - p for length in old)
                            new_cost = sum(length - p for length in new)
                            assert new_cost - old_cost == -p * (new_parts - old_parts)
                            move_checks += 1

    canonical = {
        "p7_q1_signature_distribution": distribution,
        "p7_q1_total_signatures": 219,
        "p7_m3_raw_signatures": raw_triples,
        "p7_m3_donor_corridors": expected_corridors,
    }
    digest = hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    print(
        json.dumps(
            {
                "status": "PACKING_DEFECT_CORE_INDEPENDENT_GREEN",
                "checked_primes": len(primes),
                "symbolic_parameter_cases": arithmetic_checks,
                "cost_move_checks": move_checks,
                "p7_q1_total_signatures": 219,
                "p7_m3_raw_signatures": 19,
                "p7_m3_donor_corridors": 6,
                "canonical_sha256": digest,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
