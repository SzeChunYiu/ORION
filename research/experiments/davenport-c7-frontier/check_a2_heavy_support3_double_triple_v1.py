#!/usr/bin/env python3
"""Regression for the prime-uniform a=2 heavy three-support elimination."""
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
    checked = 0
    boundary = 0
    interior = 0
    for p in range(5, 1010, 2):
        if not is_prime(p):
            continue
        m = (3 * p - 1) // 2
        target_sum = 3 * (p - 1) // 2
        for r in range(1, p):
            t = target_sum - r
            if not (r <= t <= p - 1):
                continue
            checked += 1
            assert r >= (p - 1) // 2
            if r == (p - 1) // 2:
                boundary += 1
                assert t == p - 1
                rx = (3 * r) % p
                ty = (3 * t) % p
                assert rx == (p - 3) // 2 <= r
                assert ty == p - 3 <= t
                assert 3 + rx + ty == m - 1
                assert p - 2 >= 3
            else:
                interior += 1
                assert r >= (p + 1) // 2
                assert t >= (p + 1) // 2
                rx = (2 * r) % p
                ty = (2 * t) % p
                assert rx == 2 * r - p <= r
                assert ty == 2 * t - p <= t
                assert 2 + rx + ty == p - 1 <= m - 1
                assert p - 2 >= 2

    print(json.dumps({
        "status": "A2_HEAVY_SUPPORT3_DOUBLE_TRIPLE_GREEN",
        "checked_pairs": checked,
        "boundary_pairs": boundary,
        "interior_pairs": interior,
        "max_prime": 1009,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
