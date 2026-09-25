#!/usr/bin/env python3
"""Regression for the exact a=2 overlap ceiling and radial staircase."""
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


def c_light_interval(p: int) -> int:
    H = (p - 1) // 2
    h = (H + 1) // 2
    u = pow(2, -1, p)
    out = 0
    for c in range(1, p - 2):
        if all((u * k) % p <= p - h for k in range(2, 3 + c)):
            out = c
        else:
            break
    return out


def radial_oracle(p: int, c: int, D: int) -> int:
    u = pow(2, -1, p)
    best = 10**9
    # z determines q modulo p, so the exact one-dimensional oracle needs
    # only c+3 trials.
    for z in range(c + 3):
        q = (D - z) % p
        if q <= p - 2:
            best = min(best, z + q + 2 * ((u * q) % p))
    assert best < 10**9
    return best


def closed(c: int, D: int) -> int:
    L = max(D - c - 2, 0)
    q0 = L if L % 2 == 0 else L + 1
    return D + q0


def main() -> None:
    overlap_primes = 0
    radial_primes = 0
    radial_targets = 0

    for p in range(7, 1010):
        if not is_prime(p):
            continue
        overlap_primes += 1
        H = (p - 1) // 2
        got = c_light_interval(p)
        want = 2 * (H // 2)
        assert got == want, (p, got, want)
        if p % 4 == 1:
            assert want == H
        else:
            assert p % 4 == 3 and want == H - 1

    for p in range(7, 402):
        if not is_prime(p):
            continue
        radial_primes += 1
        H = (p - 1) // 2
        C = 2 * (H // 2)
        for c in range(1, C + 1):
            for D in range(1, p):
                got = radial_oracle(p, c, D)
                want = closed(c, D)
                assert got == want, (p, c, D, got, want)
                radial_targets += 1

    print(json.dumps({
        "status": "A2_EXACT_OVERLAP_RADIAL_STAIRCASE_GREEN",
        "overlap_primes_through_1009": overlap_primes,
        "radial_primes_through_401": radial_primes,
        "radial_targets_checked": radial_targets,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
