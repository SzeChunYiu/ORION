#!/usr/bin/env python3
"""Regression for the prime-uniform radial doubling interior reduction."""
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


def a1_radial_oracle(p: int, c: int) -> list[int]:
    """Target d*s from actual s^(c+1) and saturated f1,f2,g resources."""
    inf = 10**9
    best = [inf] * p
    for q in range(p):
        # q*g + q*e1 + q*e2 = q*s for a=1.
        for z in range(c + 2):
            d = (z + q) % p
            best[d] = min(best[d], z + 3 * q)
    return best


def a2_radial_oracle(p: int, c: int) -> list[int]:
    """Target d*s from s^(c+2), g^(p-2), e1^(p-1), e2^(p-1)."""
    inf = 10**9
    inv2 = pow(2, -1, p)
    best = [inf] * p
    for q in range(p - 1):  # 0 <= q <= p-2 copies of g
        axes = (inv2 * q) % p
        for z in range(c + 3):
            d = (z + q) % p
            best[d] = min(best[d], z + q + 2 * axes)
    return best


def a2_displayed_cost(c: int) -> int:
    if c == 1:
        return 2
    if c % 2 == 0:
        return 3 * c - 2
    return 3 * c - 1


def check_symbolic(limit: int = 1009) -> dict[str, int]:
    primes = 0
    a1_rows = 0
    a2_rows = 0
    for p in range(7, limit + 1, 2):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2
        m = 3 * H + 1

        # a=1 low-overlap range.
        low_cap = (H + 2) // 2
        for c in range(1, low_cap + 1):
            assert 2 * c < p
            dmax = (H + c - 1) // 2
            for d in range(c, dmax + 1):
                r = H + 1 - c + d
                t = 2 * H - d
                A = 2 * d - 2 * c + 1
                B = p - 2 * d - 2
                assert 1 <= A <= r
                assert 1 <= B <= t
                radial = 4 * c - 2
                length = radial + A + B
                assert length == p + 2 * c - 3
                assert length < m
                a1_rows += 1

        # a=2 exact light-overlap ceiling.
        cmax = 2 * (H // 2)
        for c in range(1, cmax + 1):
            assert 2 * c < p
            dmax = (H + c - 1) // 2
            for d in range(c, dmax + 1):
                r = H + 1 - c + d
                t = 2 * H - d
                A = 2 * d - 2 * c + 1
                B = p - 2 * d - 2
                assert 1 <= A <= r
                assert 1 <= B <= t
                radial = a2_displayed_cost(c)
                length = radial + A + B
                if c == 1:
                    assert length == p - 1
                elif c % 2 == 0:
                    assert length == p + c - 3
                else:
                    assert length == p + c - 2
                assert length < m
                a2_rows += 1

    return {
        "primes_through_1009": primes,
        "a1_interior_rows_checked": a1_rows,
        "a2_interior_rows_checked": a2_rows,
    }


def check_radial_oracles() -> dict[str, int]:
    a1_cases = 0
    a2_cases = 0
    for p in range(7, 62, 2):
        if not is_prime(p):
            continue
        H = (p - 1) // 2

        for c in range(1, (H + 2) // 2 + 1):
            exact = a1_radial_oracle(p, c)[2 * c]
            assert exact == 4 * c - 2
            a1_cases += 1

        for c in range(1, 2 * (H // 2) + 1):
            exact = a2_radial_oracle(p, c)[2 * c]
            assert exact == a2_displayed_cost(c)
            a2_cases += 1

    return {
        "a1_radial_oracle_cases": a1_cases,
        "a2_radial_oracle_cases": a2_cases,
    }


def main() -> None:
    out = {
        "status": "RADIAL_DOUBLING_INTERIOR_REDUCTION_GREEN",
        **check_symbolic(),
        **check_radial_oracles(),
        "a1_consequence": "d<c throughout c<=floor((p+3)/4)",
        "a2_consequence": "d<c for every c allowed by the exact light-overlap ceiling",
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
