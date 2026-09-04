#!/usr/bin/env python3
"""Regression for the simultaneous light-heavy overlap sum bound."""
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


def ceilings(p: int, a: int) -> tuple[int, int]:
    H = (p - 1) // 2
    h = (H + 1) // 2
    u = pow(a, -1, p)

    cl = 0
    for c in range(1, p - a):
        if all((u * k) % p <= p - h for k in range(a, a + c + 1)):
            cl = c
        else:
            break

    ch = 0
    for c in range(1, a):
        if all((u * k) % p <= p - h for k in range(a - c, a + 1)):
            ch = c
        else:
            break
    return cl, ch


def residue_formula(p: int, a: int, k: int) -> int:
    u = pow(a, -1, p)
    ell = (a * u - 1) // p
    r = (ell * k) % a
    return (r * p + k) // a


def main() -> None:
    primes = 0
    types = 0
    simultaneous = 0
    residue_checks = 0
    a4_even_H = 0
    a4_odd_H = 0
    min_gap = None

    for p in range(7, 2004):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2
        for a in range(4, H + 1):
            types += 1
            cl, ch = ceilings(p, a)
            if cl and ch:
                simultaneous += 1
                gap = (a - 2) - (cl + ch)
                assert gap >= 0, (p, a, cl, ch)
                min_gap = gap if min_gap is None else min(min_gap, gap)
                if a == 4:
                    if H % 2:
                        a4_odd_H += 1
                    else:
                        a4_even_H += 1

    # Bounded all-k check of the closed residue formula used by the proof.
    for p in range(7, 202):
        if not is_prime(p):
            continue
        H = (p - 1) // 2
        for a in range(4, H + 1):
            u = pow(a, -1, p)
            ell = (a * u - 1) // p
            assert 1 <= ell <= a - 1
            for k in range(1, p):
                got = residue_formula(p, a, k)
                assert got == (u * k) % p, (p, a, k, got, (u * k) % p)
                residue_checks += 1

    print(json.dumps({
        "status": "SUPPORT4_SIMULTANEOUS_OVERLAP_SUM_GREEN",
        "primes_through_2003": primes,
        "types_a_ge4_checked": types,
        "types_with_both_overlaps": simultaneous,
        "minimum_gap_to_a_minus_2": min_gap,
        "a4_even_H_controls": a4_even_H,
        "a4_odd_H_controls": a4_odd_H,
        "bounded_residue_formula_checks": residue_checks,
        "authority": "symbolic residue-block theorem; finite checks are regression only",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
