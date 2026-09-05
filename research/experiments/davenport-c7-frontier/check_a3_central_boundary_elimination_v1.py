#!/usr/bin/env python3
"""Regression for the a=3 central-boundary elimination."""
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


def c_light(p: int) -> int:
    H = (p - 1) // 2
    h = (H + 1) // 2
    u = pow(3, -1, p)
    out = 0
    for c in range(1, p - 3):
        if all((u * k) % p <= p - h for k in range(3, 4 + c)):
            out = c
        else:
            break
    return out


def radial_excess(c: int, D: int) -> int:
    return 2 * ((max(D - c - 3, 0) + 2) // 3)


def main() -> None:
    primes = 0
    rows = 0
    for p in range(7, 1010):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2
        m = 3 * H + 1
        for c in range(3, c_light(p) + 1, 2):
            e = (c + 1) // 2
            assert c == 2 * e - 1
            assert c <= H // 2
            q = (H + e + c - 1) // c
            assert q == (H + e + c - 1) // c
            R = q * c
            assert H + e <= R <= H + e + c - 1
            assert R < p
            assert R + q < p

            r = H + 1 - e
            t = p - e
            D = (2 * q * c) % p
            A = (2 * q * r) % p
            B = (2 * q * t) % p
            w = R - (H + e)
            assert 0 <= w <= c - 1
            assert D == c + 2 * w
            assert A == p - R <= r
            assert B == p - R - q <= t
            excess = radial_excess(c, D)
            assert excess <= 2 * c - 2 <= H - 2
            total = D + excess + A + B
            assert total <= m - 1
            rows += 1

    print(json.dumps({
        "status": "A3_CENTRAL_BOUNDARY_ELIMINATION_GREEN",
        "primes_through_1009": primes,
        "central_rows_checked": rows,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
