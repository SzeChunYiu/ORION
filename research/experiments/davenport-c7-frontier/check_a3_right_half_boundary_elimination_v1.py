#!/usr/bin/env python3
"""Regression for the a=3 right-half boundary elimination."""
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
    c1_rows = 0
    for p in range(7, 1010):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2
        m = 3 * H + 1
        max_c = max(1, c_light(p))
        for c in range(1, max_c + 1):
            if c > c_light(p) and c != 1:
                continue
            for d in range(c):
                e = c - d
                f = d + 1
                if e > f:
                    continue
                r = H + 1 - e
                t = p - f
                rows += 1

                if c == 1:
                    assert e == f == 1
                    D, A, B = 3, H - 1, p - 3
                    assert D + A + B == m - 1
                    assert radial_excess(c, D) == 0
                    c1_rows += 1
                    continue

                assert c <= H // 2
                j = (p - c) // (2 * c)
                assert j >= 1
                n = p - 2 * j
                q = H - j
                assert n == 2 * q + 1
                q2 = ((c - 1) * p + 2 * c - 1) // (2 * c)
                assert q == q2
                assert q >= 2 * c - 1

                a = 2 * e - 1
                assert a <= c
                D = (n * c) % p
                A = (n * r) % p
                B = (n * t) % p
                assert D == p - 2 * j * c
                assert c <= D < 3 * c
                assert A == j * a <= r
                assert B == 2 * j * f <= t
                assert D + A + B == p + j == m - q
                excess = radial_excess(c, D)
                assert excess <= 2 * c - 2 <= q - 1
                assert D + A + B + excess <= m - 1

    print(json.dumps({
        "status": "A3_RIGHT_HALF_BOUNDARY_ELIMINATION_GREEN",
        "primes_through_1009": primes,
        "rows_checked": rows,
        "c1_rows": c1_rows,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
