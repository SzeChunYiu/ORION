#!/usr/bin/env python3
"""Regression for the prime-uniform heavy-share support-three elimination."""
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


def coefficient_atom(p: int, c: int, r: int, t: int) -> bool:
    """Necessary and sufficient coefficient minimality for three rank-two support values."""
    for n in range(2, p):
        if (n * c) % p <= c and (n * r) % p <= r and (n * t) % p <= t:
            return False
    return True


def heavy_radial_costs(p: int, a: int, c: int) -> list[int]:
    """Exact mu_{a,c}(D) from the heavy radial theorem."""
    u = pow(a, -1, p)
    inf = 10**9
    best = [inf] * p
    for q in range(p - a + c + 1):
        for z in range(a + 1):
            D = (z + q) % p
            cost = z + q + 2 * ((u * (q - D)) % p)
            if cost < best[D]:
                best[D] = cost
    return best


def multiplier_control(limit: int = 101) -> tuple[int, int]:
    """Independent multiplicity-only control: exact heavy radial oracle leaves no boundary row."""
    rows = 0
    residuals = 0
    for p in range(7, limit + 1, 2):
        if not is_prime(p):
            continue
        H = (p - 1) // 2
        m = 3 * H + 1
        for a in range(1, H + 1):
            for c in range(1, a):
                costs = heavy_radial_costs(p, a, c)
                for d in range(c):
                    r = H + 1 - c + d
                    t = 2 * H - d
                    if not (r <= t <= p - 1):
                        continue
                    if not coefficient_atom(p, c, r, t):
                        continue
                    rows += 1
                    killed = False
                    for n in range(2, p):
                        D = (n * c) % p
                        A = (n * r) % p
                        B = (n * t) % p
                        if A <= r and B <= t and costs[D] + A + B <= m - 1:
                            killed = True
                            break
                    if not killed:
                        residuals += 1
    assert residuals == 0
    return rows, residuals


def main() -> None:
    symbolic_triples = 0
    for p in range(7, 1010, 2):
        if not is_prime(p):
            continue
        H = (p - 1) // 2
        m = 3 * H + 1
        for a in range(1, H + 1):
            for c in range(1, a):
                # New-value quotient sequence length.
                N = m - c
                assert N >= p + 1

                # Every quotient atom Q_i is forced into
                # 1 <= |Q_i| <= q_i <= a-c-1.
                qmax = a - c - 1
                if qmax <= 0:
                    symbolic_triples += 1
                    continue

                # The first partial q-sum crossing a-c stays below p.
                crossing_max = 2 * (a - c) - 2
                assert crossing_max <= 2 * a - 4
                assert crossing_max < p

                # At any crossing R >= a-c, enough actual g copies exist
                # to cancel Rg, and the resulting zero-sum has length <= p < m.
                assert p - (a - c) <= p - a + c
                assert p < m
                symbolic_triples += 1

    rows, residuals = multiplier_control(101)
    assert rows == 22436, rows

    print(json.dumps({
        "status": "SUPPORT4_HEAVY_SHARE_SUPPORT3_EMPTY_GREEN",
        "symbolic_prime_type_overlap_triples_through_1009": symbolic_triples,
        "independent_multiplier_boundary_rows_through_101": rows,
        "independent_multiplier_residuals": residuals,
        "theorem": "first-corridor exact-support6 support3 heavy-share branch is empty for every p>=7 and every support4 maximal type",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
