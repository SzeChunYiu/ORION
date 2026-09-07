#!/usr/bin/env python3
"""Regression for the a=1 shared-multiplicity-two elimination."""
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


def lam(c: int, d: int) -> int:
    return d if d <= c + 1 else 3 * d - 2 * c - 2


def rho_a1(p: int, z: tuple[int, int, int]) -> int:
    r = tuple(v % p for v in z)
    s = sum(r)
    return s - 2 if all(r) else s


def certify(p: int, c: int, r: int, t: int, n: int) -> tuple[int, int, int, int]:
    q = (p - 1) // 2
    m = p + q
    d = (n * c) % p
    a = (n * r) % p
    b = (n * t) % p
    length = lam(c, d) + a + b
    assert 1 <= d <= p - 1
    assert a <= r and b <= t, (p, c, r, t, n, d, a, b)
    assert length <= m - 1, (p, c, r, t, n, d, a, b, length, m - 1)
    return d, a, b, length


def p13_base() -> int:
    p = 13
    m = 19
    survivors = 0
    for y0 in range(p):
        for y1 in range(p):
            for y2 in range(p):
                y = (y0, y1, y2)
                if y == (0, 0, 0):
                    continue
                x = tuple((4 * (1 - v)) % p for v in y)
                if x == (0, 0, 0):
                    continue
                ok = True
                for v, multiplicity in ((x, 6), (y, 11)):
                    for j in range(1, multiplicity + 1):
                        z = tuple((j * a) % p for a in v)
                        nz = tuple((-a) % p for a in z)
                        if rho_a1(p, z) < j or rho_a1(p, nz) < m - j:
                            ok = False
                            break
                    if not ok:
                        break
                if ok:
                    survivors += 1
    assert survivors == 0
    return survivors


def main() -> None:
    primes = 0
    c2_cases = 0
    low_c_interior_checks = 0

    for p in range(7, 1010, 2):
        if not is_prime(p):
            continue
        primes += 1
        q = (p - 1) // 2
        m = p + q

        # General low-c interior doubling corollary.
        for c in range(2, p):
            if 4 * c > p + 3:
                continue
            for r in range(q + 1, p):
                t = m - c - r
                if not (r <= t <= p - 1):
                    continue
                d = 2 * c
                assert d < p and d > c + 1
                a = 2 * r - p
                b = 2 * t - p
                assert lam(c, d) + a + b == p + 2 * c - 3 <= m - 1
                low_c_interior_checks += 1

        # c=2 has r>=q-1. Interior is the preceding corollary.
        c = 2
        for r in range(q - 1, p):
            t = m - c - r
            if not (r <= t <= p - 1):
                continue
            c2_cases += 1
            if r >= q + 1:
                d, a, b, length = certify(p, c, r, t, 2)
                assert (d, length) == (4, p + 1)
            elif r == q - 1:
                if p % 4 == 3:
                    n = q + 1
                    d, a, b, _ = certify(p, c, r, t, n)
                    assert (d, a, b) == (1, (p - 3) // 4, q)
                else:
                    n = q + 2
                    d, a, b, _ = certify(p, c, r, t, n)
                    assert (d, a, b) == (3, (p - 9) // 4, q - 1)
            elif r == q:
                if p == 13:
                    continue
                if p % 4 == 3:
                    n = q + 2
                    d, a, b, _ = certify(p, c, r, t, n)
                    assert (d, a, b) == (3, (p - 3) // 4, p - 3)
                else:
                    assert p >= 17
                    n = q + 3
                    d, a, b, _ = certify(p, c, r, t, n)
                    assert (d, a, b) == (5, (p - 5) // 4, p - 5)
            else:
                raise AssertionError((p, r, t))

    base_survivors = p13_base()
    print(json.dumps({
        "status": "green",
        "primes_through_1009": primes,
        "c2_multiplicity_cases": c2_cases,
        "low_c_interior_checks": low_c_interior_checks,
        "p13_radial_survivors": base_survivors,
        "theorem": "a=1 first-corridor support3 exact-support6 with v_e3(V)=2 is impossible for p>=7",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
