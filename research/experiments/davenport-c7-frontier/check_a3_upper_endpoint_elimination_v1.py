#!/usr/bin/env python3
"""Regression for the prime-uniform a=3 upper-endpoint elimination."""
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
        if all((u * k) % p <= p - h for k in range(3, 3 + c + 1)):
            out = c
        else:
            break
    return out


def radial_excess(c: int, D: int) -> int:
    L = max(D - c - 3, 0)
    return 2 * ((L + 2) // 3)


def main() -> None:
    primes = 0
    rows = 0
    c1_rows = 0
    constructed_rows = 0

    for p in range(7, 1010):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2
        m = 3 * H + 1
        # The theorem also covers hypothetical c=1 even when the overlap oracle forbids it.
        max_c = max(1, c_light(p))
        for c in range(1, max_c + 1):
            if c > c_light(p) and c != 1:
                continue
            rows += 1
            if c == 1:
                q = 1
                n = 3
                D = 3
                assert radial_excess(c, D) == 0
                A = (n * H) % p
                B = (n * (p - c)) % p
                assert A == H - 1 <= H
                assert B == p - 3 <= p - c
                total = D + radial_excess(c, D) + A + B
                assert total == m - 1
                c1_rows += 1
                continue

            assert c <= H // 2
            numerator = (c - 1) * p
            denominator = 2 * c
            q = (numerator + denominator - 1) // denominator
            assert 1 <= q <= H - 1
            assert q >= 2 * c - 1
            E = 2 * c * q - (c - 1) * p
            assert 1 <= E <= 2 * c - 1
            D = ((2 * q + 1) * c) % p
            assert D == c + E
            assert D < p and D >= c
            excess = radial_excess(c, D)
            assert excess <= 2 * c - 2 <= q - 1

            n = 2 * q + 1
            A = (n * H) % p
            B = (n * (p - c)) % p
            assert A == H - q <= H
            assert B == p - D <= p - c
            total = D + excess + A + B
            assert total <= m - 1
            constructed_rows += 1

    print(json.dumps({
        "status": "A3_UPPER_ENDPOINT_ELIMINATION_GREEN",
        "primes_through_1009": primes,
        "upper_rows_checked": rows,
        "c1_rows": c1_rows,
        "ceiling_constructed_rows": constructed_rows,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
