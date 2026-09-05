#!/usr/bin/env python3
"""Regression for the prime-uniform a=1 one-share support-three elimination."""
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


def radial_rigid_sorted(p: int) -> list[tuple[int, int, int]]:
    """Enumerate sorted positive weights satisfying S_j=p+j for every j."""
    out: list[tuple[int, int, int]] = []
    for a in range(1, p):
        for b in range(a, p):
            c = p + 1 - a - b
            if not (b <= c < p):
                continue
            if all((j * a) % p + (j * b) % p + (j * c) % p == p + j for j in range(1, p)):
                out.append((a, b, c))
    return out


def main() -> None:
    radial_primes = 0
    radial_patterns = 0
    for p in range(7, 102, 2):
        if not is_prime(p):
            continue
        radial_primes += 1
        got = radial_rigid_sorted(p)
        expected_count = (p - 1) // 2
        assert len(got) == expected_count, (p, len(got), expected_count)
        assert all(a == 1 and a + b + c == p + 1 for a, b, c in got), (p, got)
        radial_patterns += len(got)

    interior_cases = 0
    terminal_primes = 0
    for p in range(7, 1010, 2):
        if not is_prime(p):
            continue
        q = (p - 1) // 2
        m = (3 * p - 1) // 2

        # Interior c=1 multiplicity split: doubling gives a p-1 zero-sum.
        target = 3 * (p - 1) // 2
        for r in range(q + 1, p):
            t = target - r
            if not (r <= t <= p - 1):
                continue
            interior_cases += 1
            rx = 2 * r - p
            ty = 2 * t - p
            assert 1 <= rx <= r
            assert 1 <= ty <= t
            assert 2 + rx + ty == p - 1 < m

        # Boundary c=1: after radial rigidity only x=(0,3,1) remains.
        j0 = (q + 4) // 3  # ceil((q+2)/3)
        assert 1 <= j0 <= q
        assert 3 * j0 >= q + 2
        assert 3 * j0 < p
        rho_negative = 2 * p - 4 * j0
        assert rho_negative < m - j0
        terminal_primes += 1

    print(json.dumps({
        "status": "green",
        "radial_primes_through_101": radial_primes,
        "radial_patterns": radial_patterns,
        "interior_cases_through_1009": interior_cases,
        "terminal_primes_through_1009": terminal_primes,
        "theorem": "a=1 first-corridor support3 exact-support6 with v_e3(V)=1 is impossible for p>=7",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
