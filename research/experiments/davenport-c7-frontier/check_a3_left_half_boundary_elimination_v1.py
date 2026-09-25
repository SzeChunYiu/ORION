#!/usr/bin/env python3
"""Regression for the prime-uniform a=3 left-half boundary elimination."""
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


def radial_excess(c: int, D: int) -> int:
    return 2 * ((max(D - c - 3, 0) + 2) // 3)


def main() -> None:
    primes = 0
    rows = 0
    quotient_rows = 0
    pminus3_rows = 0
    min_slack = None

    for p in range(7, 1010):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2
        m_minus_1 = 3 * H

        # Broader than the exact c_light range: every c allowed by the proved
        # half-overlap bound is checked.
        for c in range(1, H // 2 + 1):
            for d in range(c):
                e = c - d
                f = d + 1
                if e <= f:
                    continue
                rows += 1

                assert e + f == c + 1
                r = H + 1 - e
                t = p - f
                alpha = 2 * e - 1
                delta = e - f
                assert alpha == c + delta > c
                assert 2 * r == p - alpha
                assert c + r + t == 3 * H + 1

                if r >= alpha:
                    quotient_rows += 1
                    j = r // alpha
                    assert j >= 1
                    w = r - j * alpha
                    assert 0 <= w <= alpha - 1
                    assert p == (2 * j + 1) * alpha + 2 * w
                    n = p - 2 * j
                    assert 1 <= n < p

                    D = (n * c) % p
                    A = (n * r) % p
                    B = (n * t) % p
                    assert 2 * j * c < p
                    assert D == p - 2 * j * c
                    assert A == j * alpha <= r
                    assert 2 * f <= c < alpha
                    assert B == 2 * j * f <= t
                    assert D + A + B == p + j
                    assert D - c - 3 == 2 * w + (2 * j + 1) * delta - 3

                    excess = radial_excess(c, D)
                    budget = H - j - 1
                    assert budget >= 0
                    assert excess <= budget, (p, c, e, f, j, w, D, excess, budget)
                    length = D + A + B + excess
                    assert length <= m_minus_1
                    slack = m_minus_1 - length
                else:
                    pminus3_rows += 1
                    n = p - 3
                    assert H + 2 < 3 * e
                    assert 3 * r < p
                    assert 3 * c < p
                    assert 2 * f <= c <= H // 2

                    D = (n * c) % p
                    A = (n * r) % p
                    B = (n * t) % p
                    assert D == p - 3 * c
                    assert A == p - 3 * r
                    assert A <= r
                    assert B == 3 * f <= t
                    assert c + r - f == H
                    assert D + A + B == H + 2

                    excess = radial_excess(c, D)
                    assert excess <= 2 * H - 2
                    length = D + A + B + excess
                    assert length <= m_minus_1
                    slack = m_minus_1 - length

                min_slack = slack if min_slack is None else min(min_slack, slack)

    assert rows == quotient_rows + pminus3_rows
    print(json.dumps({
        "status": "A3_LEFT_HALF_BOUNDARY_ELIMINATION_GREEN",
        "primes_through_1009": primes,
        "left_half_rows_checked": rows,
        "quotient_scalar_rows": quotient_rows,
        "p_minus_3_rows": pminus3_rows,
        "minimum_short_zero_slack": min_slack,
        "authority": "symbolic theorem; exhaustive regression over the broader c<=floor(H/2) range",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
