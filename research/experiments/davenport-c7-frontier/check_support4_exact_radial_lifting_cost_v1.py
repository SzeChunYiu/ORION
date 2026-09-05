#!/usr/bin/env python3
"""Regression for the exact support-four radial lifting cost theorem."""
from __future__ import annotations

import json
from math import inf


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


def radial_formula(p: int, a: int, c: int) -> list[int]:
    u = pow(a, -1, p)
    best = [10**9] * p
    for q in range(p - a + 1):
        uq = (u * q) % p
        for z in range(a + c + 1):
            D = (z + q) % p
            best[D] = min(best[D], z + q + 2 * uq)
    return best


def add_term_dp(p: int, dp: list[int], term: tuple[int, int, int]) -> list[int]:
    """0/1 occurrence update over all C_p^3 states."""
    N = p**3
    old = dp
    out = old.copy()
    tx, ty, tz = term
    for idx in range(N):
        cost = old[idx]
        if cost >= 10**8:
            continue
        x = idx // (p * p)
        y = (idx // p) % p
        z = idx % p
        nx = (x + tx) % p
        ny = (y + ty) % p
        nz = (z + tz) % p
        nid = (nx * p + ny) * p + nz
        if cost + 1 < out[nid]:
            out[nid] = cost + 1
    return out


def radial_occurrence_dp(p: int, a: int, c: int) -> list[int]:
    """Independent occurrence-level shortest-cost table from actual resources."""
    N = p**3
    dp = [10**9] * N
    dp[0] = 0
    u = pow(a, -1, p)
    e1 = (1, 0, 0)
    e2 = (0, 1, 0)
    s = (0, 0, 1)
    g = ((-u) % p, (-u) % p, 1)
    for _ in range(p - 1):
        dp = add_term_dp(p, dp, e1)
    for _ in range(p - 1):
        dp = add_term_dp(p, dp, e2)
    for _ in range(a + c):
        dp = add_term_dp(p, dp, s)
    for _ in range(p - a):
        dp = add_term_dp(p, dp, g)
    return [dp[D] for D in range(p)]  # enc((0,0,D)) == D


def bounded_occurrence_replay() -> dict[str, int]:
    # Full independent occurrence-DP comparison on deliberately small primes.
    cases = 0
    targets = 0
    for p in (5, 7, 11):
        H = (p - 1) // 2
        for a in range(1, H + 1):
            # Test all overlap counts that can occur without saturating s.
            for c in range(0, p - a):
                formula = radial_formula(p, a, c)
                brute = radial_occurrence_dp(p, a, c)
                assert brute == formula, (p, a, c, brute, formula)
                cases += 1
                targets += p
    return {
        "occurrence_dp_cases": cases,
        "occurrence_dp_radial_targets": targets,
    }


def large_formula_regression(limit: int = 101) -> dict[str, int]:
    triples = 0
    a1_targets = 0
    a2_targets = 0
    doubling_pass = 0
    for p in range(5, limit + 1, 2):
        if not is_prime(p):
            continue
        H = (p - 1) // 2
        m = 3 * H + 1
        for a in range(1, H + 1):
            for c in range(0, p - a):
                vals = radial_formula(p, a, c)
                assert vals[0] == 0
                assert all(v < 10**9 for v in vals)
                triples += 1

        if p >= 7:
            # Recover exact a=1 target cost in the low-overlap range.
            for c in range(1, (p + 3) // 4 + 1):
                if 2 * c >= p:
                    continue
                got = radial_formula(p, 1, c)[2 * c]
                assert got == 4 * c - 2
                assert got + p - 2 * c - 1 < m
                a1_targets += 1
                doubling_pass += 1

            # Recover exact a=2 target costs throughout its exact overlap ceiling.
            cmax = 2 * (H // 2)
            for c in range(1, cmax + 1):
                got = radial_formula(p, 2, c)[2 * c]
                expected = 2 if c == 1 else (3 * c - 2 if c % 2 == 0 else 3 * c - 1)
                assert got == expected, (p, c, got, expected)
                assert got + p - 2 * c - 1 < m
                a2_targets += 1
                doubling_pass += 1

    return {
        "formula_parameter_triples_through_101": triples,
        "a1_exact_target_checks": a1_targets,
        "a2_exact_target_checks": a2_targets,
        "doubling_discriminator_checks": doubling_pass,
    }


def main() -> None:
    out = {
        "status": "SUPPORT4_EXACT_RADIAL_LIFTING_COST_GREEN",
        **bounded_occurrence_replay(),
        **large_formula_regression(),
        "theorem": "lambda_ac(D)=min(z+q+2[a^{-1}q]_p) over radial resource box",
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
