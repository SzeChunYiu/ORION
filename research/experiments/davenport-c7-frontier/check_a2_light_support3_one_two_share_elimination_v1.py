#!/usr/bin/env python3
"""Primary replay for the a=2 light-share c=1,2 elimination."""
from __future__ import annotations

import hashlib
import json
from itertools import product


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


def coeff_atom(p: int, c: int, r: int, t: int) -> bool:
    for n in range(2, p):
        if (n * c) % p <= c and (n * r) % p <= r and (n * t) % p <= t:
            return False
    return True


def rho_a2(p: int, x: tuple[int, int, int]) -> int:
    u = pow(2, -1, p)
    best = 10**9
    for q in range(0, p - 1):
        c1 = (x[0] + u * q) % p
        c2 = (x[1] + u * q) % p
        c3 = (x[2] - q) % p
        if c3 <= 2:
            best = min(best, c1 + c2 + c3 + q)
    return best


def add(p: int, x: tuple[int, int, int], y: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple((a + b) % p for a, b in zip(x, y))  # type: ignore[return-value]


def mul(p: int, k: int, x: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(k * a % p for a in x)  # type: ignore[return-value]


def neg(p: int, x: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple((-a) % p for a in x)  # type: ignore[return-value]


def det(p: int, a: tuple[int, int, int], b: tuple[int, int, int], c: tuple[int, int, int]) -> int:
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    ) % p


def scalar(p: int, x: tuple[int, int, int], s: tuple[int, int, int]) -> bool:
    return any(x == mul(p, k, s) for k in range(1, p))


def p5_mutation_control() -> tuple[int, str]:
    p = 5
    m = 7
    c = 2
    u = pow(2, -1, p)
    e1, e2, s, g4 = (1, 0, 0), (0, 1, 0), (0, 0, 1), ((-u) % p, (-u) % p, 1)
    maximal_support = {e1, e2, s, g4}
    others = (e1, e2, g4)
    survivors: list[tuple[int, int, tuple[int, int, int], tuple[int, int, int]]] = []

    for r in range(1, p):
        t = m - c - r
        if not (1 <= t < p) or not coeff_atom(p, c, r, t):
            continue
        for x in product(range(p), repeat=3):
            if x == (0, 0, 0) or x in maximal_support or scalar(p, x, s):
                continue
            if any(det(p, s, x, q) == 0 for q in others):
                continue
            y = mul(p, -pow(t, -1, p), add(p, mul(p, c, s), mul(p, r, x)))
            if y == (0, 0, 0) or y in maximal_support or y in (x, s):
                continue
            if 1 + rho_a2(p, neg(p, x)) < m or 1 + rho_a2(p, neg(p, y)) < m:
                continue

            good = True
            for i in range(c + 1):
                for j in range(r + 1):
                    for k in range(t + 1):
                        length = i + j + k
                        if length in (0, m):
                            continue
                        z = add(p, add(p, mul(p, i, s), mul(p, j, x)), mul(p, k, y))
                        if length + rho_a2(p, neg(p, z)) < m:
                            good = False
                            break
                    if not good:
                        break
                if not good:
                    break
            if good:
                survivors.append((r, t, x, y))

    assert survivors == [
        (2, 3, (1, 3, 0), (1, 3, 1)),
        (2, 3, (3, 1, 0), (3, 1, 1)),
        (3, 2, (1, 3, 1), (1, 3, 0)),
        (3, 2, (3, 1, 1), (3, 1, 0)),
    ]
    payload = "".join(f"{r},{t}:{','.join(map(str,x))}:{','.join(map(str,y))}\n" for r,t,x,y in survivors)
    return len(survivors), hashlib.sha256(payload.encode()).hexdigest()


def main() -> None:
    primes = 0
    c1_rows = 0
    c2_rows = 0
    c2_nonatom_boundaries = 0

    for p in range(7, 1010, 2):
        if not is_prime(p):
            continue
        primes += 1
        h = (p - 1) // 2
        m = 3 * h + 1

        # c=1: r=h+d, t=2h-d.
        for d in range(h // 2 + 1):
            r, t = h + d, 2 * h - d
            assert 1 + r + t == m and r <= t <= p - 1
            c1_rows += 1
            if d == 0:
                n = 3
                C, R, T = (n % p), (n * r) % p, (n * t) % p
                assert (C, R, T) == (3, h - 1, p - 3)
                assert C + R + T == m - 1
            else:
                n = 2
                C, R, T = 2, (2 * r) % p, (2 * t) % p
                assert (C, R, T) == (2, 2 * d - 1, p - 2 * d - 2)
                assert C + R + T == p - 1 < m
            assert C <= 3 and R <= r and T <= t

        # c=2: r=h-1+d, t=2h-d.
        for d in range((h + 1) // 2 + 1):
            r, t = h - 1 + d, 2 * h - d
            assert 2 + r + t == m and r <= t <= p - 1
            c2_rows += 1
            if d >= 2:
                C, R, T = 4, 2 * d - 3, p - 2 * d - 2
                assert C + R + T == p - 1 < m
                assert C <= 4 and R <= r and T <= t
            elif d == 0 and p % 4 == 3:
                k = (p - 3) // 4
                n = h + 1
                C, R, T = (2 * n) % p, (n * r) % p, (n * t) % p
                assert (C, R, T) == (1, k, h)
                assert C <= 2 and R <= r and T <= t
                assert not coeff_atom(p, 2, r, t)
                c2_nonatom_boundaries += 1
            elif d == 0:
                assert p % 4 == 1 and p >= 13
                k = (p - 1) // 4
                n = h + 2
                C, R, T = (2 * n) % p, (n * r) % p, (n * t) % p
                assert (C, R, T) == (3, k - 2, h - 1)
                assert C + R + T == 3 * k < m
                assert C <= 4 and R <= r and T <= t
            elif p % 4 == 3:
                assert d == 1
                k = (p - 3) // 4
                n = h + 2
                C, R, T = (2 * n) % p, (n * r) % p, (n * t) % p
                assert (C, R, T) == (3, k, p - 3)
                assert C + R + T < m
                assert C <= 4 and R <= r and T <= t
            else:
                assert d == 1 and p % 4 == 1 and p >= 13
                k = (p - 1) // 4
                n = h + 3
                C, R, T = (2 * n) % p, (n * r) % p, (n * t) % p
                assert (C, R, T) == (5, k - 1, p - 5)
                # Realize 5s as 3 actual s plus 2g4+e1+e2=2s: cost 7.
                assert 7 + R + T == 5 * k + 2 < m
                assert R <= r and T <= t

    p5_count, p5_digest = p5_mutation_control()
    print(json.dumps({
        "status": "A2_LIGHT_SUPPORT3_C1_C2_PRIMARY_GREEN",
        "primes_through_1009": primes,
        "c1_rows": c1_rows,
        "c2_rows": c2_rows,
        "c2_nonatom_boundary_rows": c2_nonatom_boundaries,
        "p5_c2_exact_survivors": p5_count,
        "p5_c2_survivor_sha256": p5_digest,
        "theorem": "a=2 first-corridor exact-support6 light-share support3 companions have shared multiplicity at least 3 for every prime p>=7",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
