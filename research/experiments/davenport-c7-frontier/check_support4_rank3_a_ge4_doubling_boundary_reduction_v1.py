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
    doubled_boxes = 0
    boundary_boxes = 0

    for p in range(7, 2004):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2
        m = 3 * H + 1

        for a in range(4, H + 1):
            types += 1
            for c in range(1, a - 1):
                for d in range(1, a - 1 - c):
                    if c + d > a - 2:
                        continue
                    overlap_pairs += 1
                    S = c + d
                    assert 2 * c <= a + c
                    assert d < p - a
                    assert 2 * d <= p - a + d

                    # Every admissible r,t pair is either killed by doubling
                    # above H or lands in the claimed boundary parameterization.
                    rem = m - S
                    for r in range(1, p):
                        t = rem - r
                        if t < r or t <= 0 or t >= p:
                            continue
                        if r > H:
                            doubled_boxes += 1
                            R = 2 * r - p
                            T = 2 * t - p
                            assert 1 <= R <= r
                            assert 1 <= T <= t
                            length = R + T + 2 * S
                            assert length == p - 1
                            assert length <= m - 1
                        else:
                            boundary_boxes += 1
                            k = H - r
                            assert 0 <= k <= S - 1
                            assert r == H - k
                            assert t == p - S + k

    print(json.dumps({
        "status": "SUPPORT4_RANK3_A_GE4_DOUBLING_BOUNDARY_GREEN",
        "primes_through_2003": primes,
        "types_a_ge4_checked": types,
        "positive_overlap_pairs_under_sum_bound": overlap_pairs,
        "doubled_boxes_checked": doubled_boxes,
        "boundary_boxes_checked": boundary_boxes,
        "authority": "symbolic p-1 doubling theorem; finite loops are regression only",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
