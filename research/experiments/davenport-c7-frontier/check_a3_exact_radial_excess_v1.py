#!/usr/bin/env python3
"""Regression for the exact a=3 radial-excess theorem."""
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


def radial_oracle(p: int, c: int, D: int) -> int:
    u = pow(3, -1, p)
    best = 10**9
    for z in range(c + 4):
        for q in range(p - 2):
            if (z + q - D) % p == 0:
                best = min(best, z + q + 2 * ((u * q) % p))
    assert best < 10**9
    return best


def closed(p: int, c: int, D: int) -> int:
    L = max(D - c - 3, 0)
    return D + 2 * ((L + 2) // 3)


def main() -> None:
    primes = 0
    checks = 0
    for p in range(7, 402):
        if not is_prime(p):
            continue
        primes += 1
        for c in range(1, c_light(p) + 1):
            for D in range(1, p):
                got = radial_oracle(p, c, D)
                want = closed(p, c, D)
                assert got == want, (p, c, D, got, want)
                checks += 1
    print(json.dumps({
        "status": "A3_EXACT_RADIAL_EXCESS_GREEN",
        "primes_through_401": primes,
        "targets_checked": checks,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
