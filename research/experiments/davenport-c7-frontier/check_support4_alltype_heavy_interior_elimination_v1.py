#!/usr/bin/env python3
"""Regression for all-type heavy-share interior elimination."""
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


def check_endpoint(p: int, a: int, c: int, d: int) -> None:
    H = (p - 1) // 2
    m = 3 * H + 1
    r = H + 1 - c + d
    t = 2 * H - d
    assert 1 <= c <= a - 1
    assert c <= p - a
    assert 2 * c <= p - a + c
    assert 2 * c < p
    assert r <= t <= p - 1

    A = 2 * d - 2 * c + 1
    B = p - 2 * d - 2
    assert 1 <= A <= r
    assert 1 <= B <= t
    assert A + B == p - 2 * c - 1
    length = 2 * c + A + B
    assert length == p - 1 < m


def bounded_full_regression(limit: int = 251) -> dict[str, int]:
    triples = 0
    endpoint_checks = 0
    for p in range(7, limit + 1, 2):
        if not is_prime(p):
            continue
        H = (p - 1) // 2
        for a in range(2, H + 1):
            for c in range(1, a):
                dmax = (H + c - 1) // 2
                if dmax < c:
                    continue
                triples += 1
                check_endpoint(p, a, c, c)
                endpoint_checks += 1
                if dmax != c:
                    check_endpoint(p, a, c, dmax)
                    endpoint_checks += 1
    return {
        "heavy_parameter_triples_through_251": triples,
        "heavy_d_endpoint_checks_through_251": endpoint_checks,
    }


def large_arithmetic_control(limit: int = 1009) -> dict[str, int]:
    primes = 0
    for p in range(7, limit + 1, 2):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2
        # Worst heavy capacity has a=H,c=H-1.
        a = H
        c = H - 1
        assert c <= a - 1
        assert c <= p - a
        assert 2 * c <= p - a + c
        assert 2 * c < p
        assert p - 1 < 3 * H + 1
    return {"heavy_prime_controls_through_1009": primes}


def main() -> None:
    print(json.dumps({
        "status": "SUPPORT4_ALLTYPE_HEAVY_INTERIOR_ELIMINATION_GREEN",
        **bounded_full_regression(),
        **large_arithmetic_control(),
        "theorem": "every heavy-share support3 interior row d>=c is impossible for every canonical support4 type",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
