#!/usr/bin/env python3
"""Arithmetic regression for the prime-uniform maximal-atom corridor theorem."""

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


def corridors(p: int) -> list[tuple[int, int, int]]:
    half = (p + 1) // 2
    return [
        (p + j, p + half - j, 3 * p - 2)
        for j in range(1, (p + 1) // 4 + 1)
    ]


def check_prime(p: int) -> None:
    n3 = (11 * p - 3) // 2
    d2 = (9 * p - 5) // 2
    d1 = 3 * p - 2
    profiles = corridors(p)

    assert n3 - p == d2 + 1
    assert len(profiles) == (p + 1) // 4

    for j, (short_len, long_len, maximal_len) in enumerate(profiles, 1):
        b = (p + 1) // 2 - j

        assert short_len == p + j
        assert long_len == p + b
        assert maximal_len == d1
        assert 1 <= j <= b
        assert short_len <= long_len <= maximal_len
        assert short_len + long_len + maximal_len == n3
        assert j + b == (p + 1) // 2

        pair_len = long_len + maximal_len
        inherited_depth = p + b - 1
        assert pair_len == 4 * p + b - 2
        assert pair_len - inherited_depth == d1 + 1 == 3 * p - 1
        assert inherited_depth >= p

        delta = 5 * (p - 1) - pair_len
        assert delta == (p + 2 * j - 7) // 2

        if j <= 2:
            assert delta >= 0
            assert 5 + delta <= p
            assert 2 * delta <= p - 2

        if j == 3:
            assert 2 * delta == p - 1


def main() -> None:
    primes = [p for p in range(5, 402) if is_prime(p)]
    for p in primes:
        check_prime(p)

    expected = {
        5: [(6, 7, 13)],
        7: [(8, 10, 19), (9, 9, 19)],
        11: [(12, 16, 31), (13, 15, 31), (14, 14, 31)],
        13: [(14, 19, 37), (15, 18, 37), (16, 17, 37)],
    }
    for p, profiles in expected.items():
        assert corridors(p) == profiles

    print(
        json.dumps(
            {
                "status": "PRIME_UNIFORM_MAXIMAL_CORRIDOR_GREEN",
                "checked_primes": len(primes),
                "max_prime": primes[-1],
                "p7_corridors": corridors(7),
                "p11_corridors": corridors(11),
                "support_six_indices": [1, 2],
                "j3_boundary": "2*Delta=p-1",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
