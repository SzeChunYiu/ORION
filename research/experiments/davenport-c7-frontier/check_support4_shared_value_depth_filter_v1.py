#!/usr/bin/env python3
"""Regression for modular-inverse shared-value depth filters."""

from __future__ import annotations

import json
from fractions import Fraction


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


def rho_formula(p: int, a: int, x: tuple[int, int, int]) -> int:
    inv = pow(a, -1, p)
    best = 10**9
    for t in range(p - a + 1):
        c1 = (x[0] + inv * t) % p
        c2 = (x[1] + inv * t) % p
        c3 = (x[2] - t) % p
        if c3 <= a:
            best = min(best, c1 + c2 + c3 + t)
    return best


def main() -> None:
    primes = [p for p in range(5, 402) if is_prime(p)]
    rows = 0
    low = middle = high = 0

    for p in primes:
        for j in range(1, (p + 1) // 4 + 1):
            b = (p + 1) // 2 - j
            m = p + b
            L = Fraction(p + 5 - 2 * j, 4)
            R = Fraction(3 * p + 2 * j - 5, 4)
            assert L <= R

            for a in range(1, (p - 1) // 2 + 1):
                rows += 1
                u = pow(a, -1, p)
                inv = u
                e3 = (0, 0, 1)
                g4 = ((-inv) % p, (-inv) % p, 1)
                minus_e3 = (0, 0, p - 1)
                minus_g4 = tuple((-x) % p for x in g4)

                d_light = rho_formula(p, a, minus_e3)
                d_heavy = rho_formula(p, a, minus_g4)

                assert d_light == 3 * p - 3 - 2 * u
                assert d_heavy == p + 2 * u - 3

                light_ok = d_light >= m - 1
                heavy_ok = d_heavy >= m - 1

                assert light_ok == (Fraction(u, 1) <= R)
                assert heavy_ok == (Fraction(u, 1) >= L)

                if u < L:
                    low += 1
                    assert light_ok and not heavy_ok
                elif u > R:
                    high += 1
                    assert heavy_ok and not light_ok
                else:
                    middle += 1
                    assert light_ok and heavy_ok

    # Frozen p=7, j=1 type split.
    p = 7
    j = 1
    L = Fraction(p + 3, 4)
    R = Fraction(3 * (p - 1), 4)
    classes = []
    for a in (1, 2, 3):
        u = pow(a, -1, p)
        classes.append("low" if u < L else "high" if u > R else "middle")
    assert classes == ["low", "middle", "high"]

    print(
        json.dumps(
            {
                "status": "SUPPORT4_SHARED_VALUE_DEPTH_FILTER_GREEN",
                "checked_primes": len(primes),
                "max_prime": primes[-1],
                "checked_type_corridor_rows": rows,
                "inverse_regimes": {"low": low, "middle": middle, "high": high},
                "p7_j1": classes,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
