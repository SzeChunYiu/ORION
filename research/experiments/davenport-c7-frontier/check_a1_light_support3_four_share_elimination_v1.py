#!/usr/bin/env python3
"""Primary regression for the a=1 shared-multiplicity-four elimination."""
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


def lam4(d: int) -> int:
    return d if d <= 5 else 3 * d - 10


def rho_a1(p: int, z: tuple[int, int, int]) -> int:
    residues = tuple(v % p for v in z)
    total = sum(residues)
    return total - 2 if all(residues) else total


def certify(p: int, r: int, t: int, n: int) -> tuple[int, int, int, int]:
    q = (p - 1) // 2
    m = p + q
    d = (4 * n) % p
    a = (n * r) % p
    b = (n * t) % p
    length = lam4(d) + a + b
    assert 1 <= d <= p - 1
    assert a <= r and b <= t, (p, r, t, n, d, a, b)
    assert length <= m - 1, (p, r, t, n, d, a, b, length, m - 1)
    return d, a, b, length


def n_endpoint_low(p: int) -> int:
    # r=q-3, t=p-1. The correction is the signed representative of p mod 5.
    correction = {1: -4, 2: 2, 3: -2, 4: 4}[p % 5]
    return (4 * p + correction) // 5


def n_endpoint_high(p: int) -> int:
    # r=q, t=p-4. Again use the signed representative of p mod 5.
    correction = {1: 1, 2: -3, 3: 3, 4: -1}[p % 5]
    return (4 * p + correction) // 5


def n_inner_low(p: int) -> int:
    # r=q-2, t=p-2.
    return (p - 1) // 3 if p % 3 == 1 else (p + 1) // 3


def n_inner_high(p: int) -> int:
    # r=q-1, t=p-3.
    return (p - 4) // 3 if p % 3 == 1 else (p - 2) // 3


def exact_radial_base(p: int, c: int, r: int, t: int) -> int:
    q = (p - 1) // 2
    m = p + q
    inv_r = pow(r, -1, p)
    survivors = 0
    for y0 in range(p):
        for y1 in range(p):
            for y2 in range(p):
                y = (y0, y1, y2)
                if y == (0, 0, 0):
                    continue
                x = tuple((-inv_r * (c + t * value)) % p for value in y)
                if x == (0, 0, 0):
                    continue
                ok = True
                for vector, multiplicity in ((x, r), (y, t)):
                    for j in range(1, multiplicity + 1):
                        z = tuple((j * value) % p for value in vector)
                        nz = tuple((-value) % p for value in z)
                        if rho_a1(p, z) < j or rho_a1(p, nz) < m - j:
                            ok = False
                            break
                    if not ok:
                        break
                if ok:
                    survivors += 1
    assert survivors == 0, (p, c, r, t, survivors)
    return survivors


def main() -> None:
    residuals = {(7, 1, 5), (13, 3, 12), (17, 8, 13)}
    small_multipliers = {
        (7, 2, 4): 4,
        (7, 3, 3): 3,
        (11, 2, 10): 6,
        (11, 5, 7): 7,
        (11, 6, 6): 4,
        (13, 5, 10): 8,
        (19, 9, 15): 11,
    }

    primes = 0
    symbolic_cases = 0
    observed_residuals: set[tuple[int, int, int]] = set()

    for p in range(7, 1010, 2):
        if not is_prime(p):
            continue
        primes += 1
        q = (p - 1) // 2
        m = p + q
        for r in range(1, p):
            t = m - 4 - r
            if not (r <= t <= p - 1):
                continue
            key = (p, r, t)
            if key in residuals:
                observed_residuals.add(key)
                continue

            if key in small_multipliers:
                certify(p, r, t, small_multipliers[key])
            elif r >= q + 1:
                assert p >= 13, key
                d, _, _, length = certify(p, r, t, 2)
                assert (d, length) == (8, p + 5)
            elif r == q - 3:
                certify(p, r, t, n_endpoint_low(p))
            elif r == q - 2:
                certify(p, r, t, n_inner_low(p))
            elif r == q - 1:
                certify(p, r, t, n_inner_high(p))
            elif r == q:
                certify(p, r, t, n_endpoint_high(p))
            else:
                raise AssertionError((p, q, r, t))
            symbolic_cases += 1

    assert observed_residuals == residuals
    base_survivors = {
        f"{p}:4,{r},{t}": exact_radial_base(p, 4, r, t)
        for p, r, t in sorted(residuals)
    }

    print(json.dumps({
        "status": "green",
        "primes_7_through_1009": primes,
        "symbolic_or_explicit_multiplier_cases": symbolic_cases,
        "relation_multiplier_residuals": [list(item) for item in sorted(residuals)],
        "exact_base_survivors": base_survivors,
        "theorem": "a=1 first-corridor support3 exact-support6 with v_e3(V)=4 is impossible for p>=7",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
