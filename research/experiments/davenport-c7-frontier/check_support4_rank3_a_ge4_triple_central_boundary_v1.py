#!/usr/bin/env python3
"""Regression for the scalar-three rank3 a>=4 central-boundary theorem."""
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


def main() -> None:
    primes = 0
    theorem_rows = 0

    # Complete small-prime box regression. All-prime authority is the exact
    # symbolic coefficient identity, so a larger census would be redundant.
    for p in range(7, 152):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2
        m1 = 3 * H
        for a in range(4, H + 1):
            for c in range(1, a - 1):
                for d in range(1, a - 1 - c):
                    S = c + d
                    if S > a - 2:
                        continue
                    for k in range(S):
                        if 3 * k > H - 2:
                            continue
                        if 3 * (S - k) > 2 * H:
                            continue
                        if 2 * c > a:
                            continue
                        if 2 * d > p - a:
                            continue

                        theorem_rows += 1
                        r = H - k
                        t = p - S + k
                        R = (3 * r) % p
                        T = (3 * t) % p
                        assert R == H - 3 * k - 1
                        assert T == p - 3 * (S - k)
                        assert 1 <= R <= r
                        assert 1 <= T <= t
                        assert 3 * c <= a + c
                        assert 3 * d <= p - a + d
                        assert R + T + 3 * S == m1

    print(json.dumps({
        "status": "SUPPORT4_RANK3_A_GE4_TRIPLE_CENTRAL_GREEN",
        "primes_through_151": primes,
        "theorem_rows_checked": theorem_rows,
        "exact_length": "m-1 on every checked theorem row",
        "authority": "symbolic exact-m-minus-one theorem; loops are regression only",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
