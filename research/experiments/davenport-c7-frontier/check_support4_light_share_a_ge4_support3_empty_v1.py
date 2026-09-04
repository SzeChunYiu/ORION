#!/usr/bin/env python3
"""Regression for the first-corridor light-share a>=4 elimination."""
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


def c_light(p: int, a: int) -> int:
    H = (p - 1) // 2
    h = (H + 1) // 2
    u = pow(a, -1, p)
    out = 0
    for c in range(1, p - a):
        if (u * (a + c)) % p > p - h:
            break
        out = c
    return out


def rho_light_line(p: int, a: int, q: int) -> int:
    """Exact rho_U(q*s) from the support-four one-parameter formula."""
    u = pow(a, -1, p)
    best = 10**9
    for t in range(p - a + 1):
        z = (q - t) % p
        if z <= a:
            best = min(best, z + t + 2 * ((u * t) % p))
    assert best < 10**9
    return best


def coefficient_atom(p: int, c: int, r: int, t: int) -> bool:
    for n in range(2, p):
        if (n * c) % p <= c and (n * r) % p <= r and (n * t) % p <= t:
            return False
    return True


def light_radial_costs(p: int, a: int, c: int) -> list[int]:
    u = pow(a, -1, p)
    inf = 10**9
    best = [inf] * p
    for q in range(p - a + 1):
        for z in range(a + c + 1):
            D = (z + q) % p
            cost = z + q + 2 * ((u * q) % p)
            if cost < best[D]:
                best[D] = cost
    return best


def multiplier_control(limit: int = 101) -> tuple[int, int]:
    rows = 0
    residuals = 0
    for p in range(7, limit + 1, 2):
        if not is_prime(p):
            continue
        H = (p - 1) // 2
        m = 3 * H + 1
        for a in range(4, H + 1):
            cm = c_light(p, a)
            for c in range(1, cm + 1):
                costs = light_radial_costs(p, a, c)
                for d in range(c):
                    r = H + 1 - c + d
                    t = 2 * H - d
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
    overlap_checks = 0
    shell_checks = 0

    # Large cheap check: the overlap ceiling is always below a for a>=4.
    for p in range(11, 1010, 2):
        if not is_prime(p):
            continue
        H = (p - 1) // 2
        for a in range(4, H + 1):
            assert c_light(p, a) <= a - 1
            overlap_checks += 1

    # Exact depth check of the complete m-shell on a bounded prime universe.
    for p in range(11, 200, 2):
        if not is_prime(p):
            continue
        H = (p - 1) // 2
        m = 3 * H + 1
        for a in range(4, H + 1):
            cm = c_light(p, a)
            expected = set(range(1, cm + 1)) | set(range(p - cm, p))
            observed = set()
            for q in range(1, p):
                delta = rho_light_line(p, a, q) + rho_light_line(p, a, p - q)
                if delta >= m:
                    observed.add(q)
                shell_checks += 1
            assert observed == expected, (p, a, cm, sorted(observed), sorted(expected))

    rows, residuals = multiplier_control(101)
    assert rows == 2452, rows

    print(json.dumps({
        "status": "SUPPORT4_LIGHT_SHARE_A_GE4_SUPPORT3_EMPTY_GREEN",
        "overlap_ceiling_checks_through_1009": overlap_checks,
        "exact_light_m_shell_scalar_checks_through_199": shell_checks,
        "independent_multiplier_boundary_rows_through_101": rows,
        "independent_multiplier_residuals": residuals,
        "theorem": "first-corridor exact-support6 support3 light-share branch is empty for every support4 maximal type a>=4",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
