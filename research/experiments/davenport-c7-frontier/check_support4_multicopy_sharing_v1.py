#!/usr/bin/env python3
"""Regression for exact multi-copy sharing criteria from support-line depth."""

from __future__ import annotations

import json
from math import ceil


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
    u = pow(a, -1, p)
    best = 10**9
    for t in range(p - a + 1):
        c1 = (x[0] + u * t) % p
        c2 = (x[1] + u * t) % p
        c3 = (x[2] - t) % p
        if c3 <= a:
            best = min(best, c1 + c2 + c3 + t)
    return best


def mul(r: int, x: tuple[int, int, int], p: int) -> tuple[int, int, int]:
    return tuple((r * y) % p for y in x)


def neg(x: tuple[int, int, int], p: int) -> tuple[int, int, int]:
    return tuple((-y) % p for y in x)


def main() -> None:
    primes = [p for p in range(5, 402) if is_prime(p)]
    checked = 0

    for p in primes:
        for j in range(1, (p + 1) // 4 + 1):
            b = (p + 1) // 2 - j
            m = p + b
            h = ceil(b / 2)

            for a in range(1, (p - 1) // 2 + 1):
                u = pow(a, -1, p)
                e3 = (0, 0, 1)
                g4 = ((-u) % p, (-u) % p, 1)

                # Light sharing: exact equivalence for every possible c.
                prefix_ok = True
                for c in range(1, p - a):
                    prefix_ok = prefix_ok and ((u * (a + c)) % p <= p - h)
                    depth_ok = True
                    for r in range(1, c + 1):
                        d = rho_formula(p, a, neg(mul(r, e3, p), p))
                        if r + d < m:
                            depth_ok = False
                            break
                    assert depth_ok == prefix_ok, (p, j, a, "light", c)
                    checked += 1

                # Heavy sharing: exact equivalence for every possible c.
                prefix_ok = True
                for c in range(1, a):
                    prefix_ok = prefix_ok and ((u * (a - c)) % p <= p - h)
                    depth_ok = True
                    for r in range(1, c + 1):
                        d = rho_formula(p, a, neg(mul(r, g4, p), p))
                        if r + d < m:
                            depth_ok = False
                            break
                    assert depth_ok == prefix_ok, (p, j, a, "heavy", c)
                    checked += 1

                # Singleton endpoint thresholds.
                light_one = (p - 1 - a) >= 1 and ((u * (a + 1)) % p <= p - h)
                assert light_one == (u <= p - h - 1)
                if a > 1:
                    heavy_one = ((u * (a - 1)) % p <= p - h)
                    assert heavy_one == (u >= h + 1)

    # Frozen p=7, j=1 exact maxima.
    p, j = 7, 1
    b = (p + 1) // 2 - j
    h = ceil(b / 2)
    frozen = []
    for a in (1, 2, 3):
        u = pow(a, -1, p)
        cl = 0
        for c in range(1, p - a):
            if all((u * k) % p <= p - h for k in range(a, a + c + 1)):
                cl = c
            else:
                break
        ch = 0
        for c in range(1, a):
            if all((u * k) % p <= p - h for k in range(a - c, a + 1)):
                ch = c
            else:
                break
        frozen.append((cl, ch))
    assert frozen == [(4, 0), (2, 1), (0, 2)]

    print(
        json.dumps(
            {
                "status": "SUPPORT4_MULTICOPY_SHARING_GREEN",
                "checked_primes": len(primes),
                "max_prime": primes[-1],
                "checked_multiplicity_cases": checked,
                "p7_j1": frozen,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
