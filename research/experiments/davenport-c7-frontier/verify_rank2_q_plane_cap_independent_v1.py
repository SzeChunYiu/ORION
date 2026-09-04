#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from math import ceil


def det3(a, b, c, p: int) -> int:
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    ) % p


def canonical_shortest_zero_sum(p: int, q: int) -> int:
    # Canonical saturated-plane sequence:
    # e1^(p-1) e2^(p-1) (e1+e2)^(p-q).
    best = None
    for a in range(p):
        for b in range(p):
            for c in range(p - q + 1):
                if a == b == c == 0:
                    continue
                if (a + c) % p == 0 and (b + c) % p == 0:
                    length = a + b + c
                    best = length if best is None else min(best, length)
    assert best is not None
    return best


def conic_arc(p: int):
    points = [(1, t, (t * t) % p) for t in range(p)] + [(0, 0, 1)]
    assert len(set(points)) == p + 1
    for triple in itertools.combinations(points, 3):
        assert det3(*triple, p) != 0
    return points


def direction_floor_independent(p: int, m: int, q: int) -> tuple[int, int, int]:
    M = (5 * p - 5) // 2
    N = p * m + M + q
    raw = ceil(N / (p - 1))
    for r in range(raw, p * p + p + 2):
        delta = r * (p - 1) - N
        full_count_lower = r - delta  # each non-full direction costs >=1 deficit
        if full_count_lower > p + 1:
            continue
        if delta < q - 1 and r > p + 1:
            continue
        return raw, r, delta
    raise AssertionError


def main() -> int:
    shortest = []
    for p in (5, 7, 11, 13):
        conic_arc(p)
        for q in range(1, (p - 1) // 2 + 1):
            best = canonical_shortest_zero_sum(p, q)
            assert best == p + q
            shortest.append({'p': p, 'q': q, 'shortest_zero_sum': best})

    p7 = []
    for q, mmax in ((2, 8), (3, 6)):
        for m in range(3, mmax + 1):
            raw, new, delta = direction_floor_independent(7, m, q)
            p7.append({'q': q, 'm': m, 'old': raw, 'new': new, 'delta_at_new': delta})

    expected_new = {
        (2, 3): 7, (2, 4): 8, (2, 5): 9, (2, 6): 11, (2, 7): 12, (2, 8): 13,
        (3, 3): 7, (3, 4): 8, (3, 5): 10, (3, 6): 11,
    }
    assert {(row['q'], row['m']): row['new'] for row in p7} == expected_new

    # Directly hostile-check the four bumped old floors.
    for q, m in ((2, 6), (2, 7), (3, 5), (3, 6)):
        M = 15
        N = 7 * m + M + q
        old = ceil(N / 6)
        delta = old * 6 - N
        full = old - delta
        violates_full_arc = full > 8
        violates_small_delta_arc = delta < q - 1 and old > 8
        assert violates_full_arc or violates_small_delta_arc

    print(json.dumps({
        'status': 'RANK2_Q_PLANE_CAP_INDEPENDENT_GREEN',
        'canonical_extremal_cases': len(shortest),
        'conic_arc_primes': [5, 7, 11, 13],
        'p7_rows': p7,
        'p7_improved_slices': 4,
    }, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
