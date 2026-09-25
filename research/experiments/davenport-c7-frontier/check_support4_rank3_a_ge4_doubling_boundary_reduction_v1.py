#!/usr/bin/env python3
"""Regression for rank-three a>=4 doubling boundary reduction."""
from __future__ import annotations

import json


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def main() -> None:
    primes = 0
    types = 0
    overlap_pairs = 0
    doubled_endpoint_checks = 0
    boundary_boxes = 0

    # Complete small-prime regression. The theorem itself is the symbolic
    # p-1 identity, so large-prime exhaustive box enumeration is redundant.
    for p in range(7, 102):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2
        m = 3 * H + 1

        for a in range(4, H + 1):
            types += 1
            for c in range(1, a - 1):
                for d in range(1, a - 1 - c):
                    S = c + d
                    if S > a - 2:
                        continue
                    overlap_pairs += 1
                    assert 2 * c <= a + c
                    assert d < p - a
                    assert 2 * d <= p - a + d

                    rem = m - S
                    max_r = rem // 2
                    if max_r > H:
                        # The doubled identities are affine in r, so checking
                        # both endpoints guards the complete above-H interval.
                        for r in sorted({H + 1, max_r}):
                            t = rem - r
                            assert H < r <= t < p
                            R = 2 * r - p
                            T = 2 * t - p
                            assert 1 <= R <= r
                            assert 1 <= T <= t
                            length = R + T + 2 * S
                            assert length == p - 1
                            doubled_endpoint_checks += 1

                    for k in range(S):
                        boundary_boxes += 1
                        r = H - k
                        t = p - S + k
                        assert H + 1 - S <= r <= H
                        assert r <= t <= p - 1
                        assert r + t == rem

    print(json.dumps({
        "status": "SUPPORT4_RANK3_A_GE4_DOUBLING_BOUNDARY_GREEN",
        "primes_through_101": primes,
        "types_a_ge4_checked": types,
        "positive_overlap_pairs_under_sum_bound": overlap_pairs,
        "doubled_interval_endpoint_checks": doubled_endpoint_checks,
        "boundary_boxes_checked": boundary_boxes,
        "authority": "symbolic p-1 doubling theorem; finite loops are regression only",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
