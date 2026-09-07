#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from math import ceil


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


def griesmer_cap_small(p: int, q: int) -> int:
    plane_cap = 3 * p - q - 2
    d = 0
    while True:
        nxt = d + 1
        if ceil(nxt / p) + ceil(nxt / (p * p)) > plane_cap:
            return plane_cap + d
        d = nxt


def direction_floor(p: int, m: int, q: int) -> tuple[int, int]:
    M = (5 * p - 5) // 2
    N = p * m + M + q
    raw = ceil(N / (p - 1))
    if q == 1:
        return raw, raw
    for r in range(raw, p * p + p + 2):
        delta = r * (p - 1) - N
        # Full-multiplicity directions are an arc.
        if r - delta > p + 1:
            continue
        # If total deficit is below q-1, the entire support is an arc.
        if delta < q - 1 and r > p + 1:
            continue
        return raw, r
    raise AssertionError('no projective direction floor found')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-prime', type=int, default=401)
    args = ap.parse_args()

    primes = [p for p in range(5, args.max_prime + 1) if is_prime(p)]
    translated = 0
    for p in primes:
        for q in range(1, (p - 1) // 2 + 1):
            k = p - q
            h = p + q - 1
            forcing = 3 * p - q - 1
            cap = forcing - 1
            assert 0 <= k <= p - 1
            assert 2 * p - 1 - k == h
            assert 2 * p - 1 + k == forcing
            assert cap == 3 * p - q - 2

            # The canonical saturated plane contains an atom of exact length p+q.
            atom_a = q
            atom_b = q
            atom_c = p - q
            assert atom_a + atom_c == p
            assert atom_b + atom_c == p
            assert atom_a + atom_b + atom_c == p + q

            # First-failure complement after removing that atom lands exactly
            # on D_{m-1}; check symbolically for representative m values.
            M = (5 * p - 5) // 2
            for m in (3, 4, min(9, M + 1)):
                N = p * m + M + q
                assert N - (p + q) == (m - 1) * p + M

            # q-dependent Griesmer control. For p>=11 the ceiling layers are stable.
            if p >= 11:
                L = 3 * p * p - p * q - 2 * p - q - 2
                plane_cap = 3 * p - q - 2
                d = L - plane_cap
                assert d == p * (3 * p - q - 5)
                assert ceil(d / p) + ceil(d / (p * p)) <= plane_cap
                nxt = d + 1
                assert ceil(nxt / p) + ceil(nxt / (p * p)) > plane_cap
            translated += 1

    # Frozen exceptional small-prime Griesmer values.
    assert [griesmer_cap_small(5, q) for q in (1, 2)] == [62, 56]
    p7_griesmer = [griesmer_cap_small(7, q) for q in (1, 2, 3)]
    assert p7_griesmer == [123, 115, 114]

    p7_rows = []
    p = 7
    M = 15
    for q in (2, 3):
        mmax = M // q + 1
        for m in range(3, mmax + 1):
            N = p * m + M + q
            raw, new = direction_floor(p, m, q)
            p7_rows.append({'q': q, 'm': m, 'N': N, 'old': raw, 'new': new})

    expected = [
        {'q': 2, 'm': 3, 'N': 38, 'old': 7, 'new': 7},
        {'q': 2, 'm': 4, 'N': 45, 'old': 8, 'new': 8},
        {'q': 2, 'm': 5, 'N': 52, 'old': 9, 'new': 9},
        {'q': 2, 'm': 6, 'N': 59, 'old': 10, 'new': 11},
        {'q': 2, 'm': 7, 'N': 66, 'old': 11, 'new': 12},
        {'q': 2, 'm': 8, 'N': 73, 'old': 13, 'new': 13},
        {'q': 3, 'm': 3, 'N': 39, 'old': 7, 'new': 7},
        {'q': 3, 'm': 4, 'N': 46, 'old': 8, 'new': 8},
        {'q': 3, 'm': 5, 'N': 53, 'old': 9, 'new': 10},
        {'q': 3, 'm': 6, 'N': 60, 'old': 10, 'new': 11},
    ]
    assert p7_rows == expected
    improved = [row for row in p7_rows if row['new'] > row['old']]
    assert [(r['q'], r['m']) for r in improved] == [(2, 6), (2, 7), (3, 5), (3, 6)]

    print(json.dumps({
        'status': 'RANK2_Q_PLANE_CAP_GREEN',
        'checked_primes': len(primes),
        'translated_q_cases': translated,
        'p7_rows': p7_rows,
        'p7_improved_slices': len(improved),
        'p7_griesmer_caps': p7_griesmer,
    }, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
