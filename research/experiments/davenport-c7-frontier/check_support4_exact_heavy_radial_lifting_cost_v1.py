#!/usr/bin/env python3
"""Regression for the exact heavy-direction radial lifting cost theorem."""
from __future__ import annotations

import json

INF = 10**9


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


def heavy_formula(p: int, a: int, c: int) -> list[int]:
    u = pow(a, -1, p)
    best = [INF] * p
    for D in range(p):
        for q in range(p - a + c + 1):
            z = (D - q) % p
            if z > a:
                continue
            value = z + q + 2 * ((u * (q - D)) % p)
            best[D] = min(best[D], value)
    return best


def add_term_dp(p: int, dp: list[int], term: tuple[int, int, int]) -> list[int]:
    out = dp.copy()
    tx, ty, tz = term
    for idx, cost in enumerate(dp):
        if cost >= INF:
            continue
        x = idx // (p * p)
        y = (idx // p) % p
        z = idx % p
        nx = (x + tx) % p
        ny = (y + ty) % p
        nz = (z + tz) % p
        nid = (nx * p + ny) * p + nz
        out[nid] = min(out[nid], cost + 1)
    return out


def heavy_occurrence_dp(p: int, a: int, c: int) -> list[int]:
    N = p**3
    dp = [INF] * N
    dp[0] = 0
    u = pow(a, -1, p)
    e1 = (1, 0, 0)
    e2 = (0, 1, 0)
    s = (0, 0, 1)
    g = ((-u) % p, (-u) % p, 1)
    for term, count in (
        (e1, p - 1),
        (e2, p - 1),
        (s, a),
        (g, p - a + c),
    ):
        for _ in range(count):
            dp = add_term_dp(p, dp, term)

    out = []
    for D in range(p):
        target = ((-D * u) % p, (-D * u) % p, D)
        idx = (target[0] * p + target[1]) * p + target[2]
        out.append(dp[idx])
    return out


def bounded_occurrence_replay() -> dict[str, int]:
    cases = 0
    targets = 0
    for p in (5, 7, 11):
        H = (p - 1) // 2
        for a in range(1, H + 1):
            for c in range(0, a):
                formula = heavy_formula(p, a, c)
                brute = heavy_occurrence_dp(p, a, c)
                assert formula == brute, (p, a, c, formula, brute)
                cases += 1
                targets += p
    return {
        "occurrence_dp_cases": cases,
        "occurrence_dp_targets": targets,
    }


def literal_double_control(limit: int = 401) -> dict[str, int]:
    checks = 0
    for p in range(5, limit + 1, 2):
        if not is_prime(p):
            continue
        H = (p - 1) // 2
        for a in range(1, H + 1):
            for c in range(1, a):
                assert c <= p - a
                assert 2 * c <= p - a + c
                got = heavy_formula(p, a, c)[2 * c]
                assert got <= 2 * c
                checks += 1
    return {
        "literal_double_controls_through_401": checks,
    }


def main() -> None:
    print(json.dumps({
        "status": "SUPPORT4_EXACT_HEAVY_RADIAL_LIFTING_COST_GREEN",
        **bounded_occurrence_replay(),
        **literal_double_control(),
        "theorem": "mu_ac(D)=min(z+q+2[a^{-1}(q-D)]_p) over heavy radial resources",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
