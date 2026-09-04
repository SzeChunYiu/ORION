#!/usr/bin/env python3
"""Regression for the all-type light-share interior elimination."""
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
    alltype_rows = 0
    a1_rows_killed = 0
    a1_rows_outside = 0

    for p in range(7, 1010, 2):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2
        m = 3 * H + 1

        for a in range(1, H + 1):
            for c in range(1, H):  # an interior can exist only here
                dmax = (H + c - 1) // 2
                if dmax < c:
                    continue
                for d in range(c, dmax + 1):
                    r = H + 1 - c + d
                    t = 2 * H - d
                    assert r <= t <= p - 1

                    k = (c - 1) // a
                    q = k * a
                    z = 2 * c - q
                    assert q <= c - 1 <= H - 2
                    assert q <= p - a
                    assert 0 <= z <= a + c
                    assert (pow(a, -1, p) * q) % p == k

                    A = 2 * d - 2 * c + 1
                    B = p - 2 * d - 2
                    assert 1 <= A <= r
                    assert 1 <= B <= t
                    radial_cost = z + q + 2 * k
                    assert radial_cost == 2 * c + 2 * k
                    total = radial_cost + A + B
                    assert total == p + 2 * k - 1 == 2 * H + 2 * k

                    if a >= 2:
                        assert 2 * k <= H
                        assert total <= m - 1
                        alltype_rows += 1
                    elif 2 * k <= H:
                        assert c <= H // 2 + 1
                        assert total <= m - 1
                        a1_rows_killed += 1
                    else:
                        assert c > H // 2 + 1
                        a1_rows_outside += 1

    print(json.dumps({
        "status": "SUPPORT4_ALLTYPE_LIGHT_INTERIOR_ELIMINATION_GREEN",
        "primes_through_1009": primes,
        "a_ge_2_interior_rows_checked": alltype_rows,
        "a1_low_overlap_interior_rows_checked": a1_rows_killed,
        "a1_high_overlap_rows_outside_theorem": a1_rows_outside,
        "theorem": "all light-share interior rows d>=c are impossible for every canonical support4 type a>=2",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
