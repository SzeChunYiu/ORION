#!/usr/bin/env python3
"""Regression for the a=1 shared-multiplicity-three elimination."""
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


def lam3(d: int) -> int:
    return d if d <= 4 else 3 * d - 8


def rho_a1(p: int, z: tuple[int, int, int]) -> int:
    r = tuple(v % p for v in z)
    s = sum(r)
    return s - 2 if all(r) else s


def certify(p: int, r: int, t: int, n: int) -> tuple[int, int, int, int]:
    q = (p - 1) // 2
    m = p + q
    d = (3 * n) % p
    a = (n * r) % p
    b = (n * t) % p
    length = lam3(d) + a + b
    assert 1 <= d <= p - 1
    assert a <= r and b <= t, (p, r, t, n, d, a, b)
    assert length <= m - 1, (p, r, t, n, d, a, b, length, m - 1)
    return d, a, b, length


def exact_radial_base(p: int, triples: list[tuple[int, int, int]]) -> dict[str, int]:
    q = (p - 1) // 2
    m = p + q
    out: dict[str, int] = {}
    for c, r, t in triples:
        inv_r = pow(r, -1, p)
        survivors = 0
        for y0 in range(p):
            for y1 in range(p):
                for y2 in range(p):
                    y = (y0, y1, y2)
                    if y == (0, 0, 0):
                        continue
                    x = tuple((-inv_r * (c + t * v)) % p for v in y)
                    if x == (0, 0, 0):
                        continue
                    ok = True
                    for v, multiplicity in ((x, r), (y, t)):
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
        assert survivors == 0, (p, c, r, t, survivors)
        out[f"{p}:{c},{r},{t}"] = survivors
    return out


def main() -> None:
    symbolic_cases = 0
    primes = 0

    for p in range(11, 1010, 2):
        if not is_prime(p):
            continue
        primes += 1
        q = (p - 1) // 2
        m = p + q
        for r in range(q - 2, p):
            t = m - 3 - r
            if not (r <= t <= p - 1):
                continue
            if p == 13 and r == q:
                continue

            if r >= q + 1:
                n = 2
                d, a, b, length = certify(p, r, t, n)
                assert (d, length) == (6, p + 3)
            elif r == q - 2:
                if p % 3 == 2:
                    n = (p + 1) // 3
                    d, a, b, _ = certify(p, r, t, n)
                    assert (d, a, b) == (1, (p - 5) // 6, (2 * p - 1) // 3)
                else:
                    n = (2 * p + 4) // 3
                    d, a, b, _ = certify(p, r, t, n)
                    assert (d, a, b) == (4, (p - 10) // 3, (p - 4) // 3)
            elif r == q - 1:
                if p % 3 == 1:
                    n = (p + 5) // 3
                    d, a, b, _ = certify(p, r, t, n)
                    assert (d, a, b) == (5, (p - 5) // 2, (p - 10) // 3)
                else:
                    n = (2 * p + 5) // 3
                    d, a, b, _ = certify(p, r, t, n)
                    assert (d, a, b) == (5, (p - 5) // 2, 2 * (p - 5) // 3)
            elif r == q:
                if p % 3 == 2:
                    n = (p + 4) // 3
                    d, a, b, _ = certify(p, r, t, n)
                    assert (d, a, b) == (4, (p - 2) // 3, p - 4)
                else:
                    assert p >= 19
                    n = (2 * p + 7) // 3
                    d, a, b, _ = certify(p, r, t, n)
                    assert (d, a, b) == (7, (p - 7) // 6, p - 7)
            else:
                raise AssertionError((p, r, t))
            symbolic_cases += 1

    bases = {}
    bases.update(exact_radial_base(7, [(3, 1, 6), (3, 2, 5), (3, 3, 4)]))
    bases.update(exact_radial_base(13, [(3, 6, 10)]))

    print(json.dumps({
        "status": "green",
        "primes_11_through_1009": primes,
        "symbolic_cases": symbolic_cases,
        "exact_base_survivors": bases,
        "theorem": "a=1 first-corridor support3 exact-support6 with v_e3(V)=3 is impossible for p>=7",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
