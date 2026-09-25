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


def check_endpoint(p: int, a: int, c: int, d: int) -> None:
    H = (p - 1) // 2
    m = 3 * H + 1
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
    elif 2 * k <= H:
        assert c <= H // 2 + 1
        assert total <= m - 1
    else:
        assert c > H // 2 + 1


def bounded_full_regression(limit: int = 251) -> dict[str, int]:
    """Exhaust every meaningful (p,a,c), checking both d endpoints."""
    triples = 0
    endpoint_checks = 0
    for p in range(7, limit + 1, 2):
        if not is_prime(p):
            continue
        H = (p - 1) // 2
        for a in range(1, H + 1):
            for c in range(1, H):
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
        "full_parameter_triples_through_251": triples,
        "d_endpoint_checks_through_251": endpoint_checks,
    }


def large_symbolic_control(limit: int = 1009) -> dict[str, int]:
    """Check only the load-bearing worst-case inequalities at large primes."""
    primes = 0
    for p in range(7, limit + 1, 2):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2

        # Worst a>=2 interior radial quotient occurs at a=2, c=H-1.
        worst_k = (H - 2) // 2
        assert 2 * worst_k <= H

        # a=1 discriminator is exactly 2(c-1)<=H.
        last_killed_c = H // 2 + 1
        assert 2 * (last_killed_c - 1) <= H
        assert 2 * last_killed_c > H

        # Any interior has c<=H-1, hence 2c<p and dmax<=H-1.
        assert 2 * (H - 1) < p
        assert (H + (H - 1) - 1) // 2 <= H - 1

    return {
        "prime_level_symbolic_controls_through_1009": primes,
    }


def main() -> None:
    print(json.dumps({
        "status": "SUPPORT4_ALLTYPE_LIGHT_INTERIOR_ELIMINATION_GREEN",
        **bounded_full_regression(),
        **large_symbolic_control(),
        "theorem": "all light-share interior rows d>=c are impossible for every canonical support4 type a>=2",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
