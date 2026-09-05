#!/usr/bin/env python3
"""Regression and bounded discovery controls for the a=3 light-share face."""
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


def rho_support4(p: int, a: int, x: tuple[int, int, int]) -> int:
    u = pow(a, -1, p)
    x1, x2, x3 = x
    best = 10**9
    for t in range(p - a + 1):
        r3 = (x3 - t) % p
        if r3 <= a:
            best = min(best, (x1 + u * t) % p + (x2 + u * t) % p + r3 + t)
    return best


def rho_a3(p: int, x: tuple[int, int, int]) -> int:
    """Same depth specialized to a=3, with at most four candidate t values."""
    u = pow(3, -1, p)
    x1, x2, x3 = x
    best = 10**9
    for r3 in range(4):
        t = (x3 - r3) % p
        if t <= p - 3:
            best = min(best, (x1 + u * t) % p + (x2 + u * t) % p + r3 + t)
    return best


def radial_formula(p: int, q: int) -> int:
    assert 1 <= q <= p - 1
    if q <= p - 2 or p % 3 == 1:
        return q + 2 * ((q - 1) // 3)
    # p=3M+2 and q=p-1
    return (7 * p - 11) // 3


def c_light(p: int) -> int:
    H = (p - 1) // 2
    h = (H + 1) // 2
    u = pow(3, -1, p)
    out = 0
    for c in range(1, p - 3):
        if all((u * k) % p <= p - h for k in range(3, 3 + c + 1)):
            out = c
        else:
            break
    return out


def power_window_ok(p: int, multiplicity: int, v: tuple[int, int, int]) -> bool:
    H = (p - 1) // 2
    m = 3 * H + 1
    for j in range(1, multiplicity + 1):
        z = tuple((j * a) % p for a in v)
        nz = tuple((-a) % p for a in z)
        if rho_a3(p, z) < j:
            return False
        if j + rho_a3(p, nz) < m:
            return False
    return True


def check_radial_formula() -> int:
    checked = 0
    for p in range(7, 200):
        if not is_prime(p):
            continue
        for q in range(1, p):
            got = rho_support4(p, 3, (0, 0, q))
            assert got == radial_formula(p, q), (p, q, got, radial_formula(p, q))
            assert got == rho_a3(p, (0, 0, q))
            checked += 1
    return checked


def check_overlap_bound() -> tuple[int, int]:
    primes = 0
    max_ratio_num = 0
    for p in range(7, 1010):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2
        c = c_light(p)
        assert c <= H // 2, (p, c, H)
        max_ratio_num = max(max_ratio_num, 2 * c)
    return primes, max_ratio_num


def check_normal_form() -> int:
    checks = 0
    for p in (11, 13, 17, 19, 23):
        H = (p - 1) // 2
        m = 3 * H + 1
        for c in range(1, c_light(p) + 1):
            for d in range(c):
                e = c - d
                f = d + 1
                r = H + 1 - e
                t = p - f
                assert c + r + t == m
                tau = (-r * pow(t, -1, p)) % p
                assert tau != 1
                for zeta in range(2, p):
                    for alpha in (0, 1, p - 1):
                        beta = (-(c + r * alpha) * pow(t, -1, p)) % p
                        x = (1, zeta, alpha)
                        y = (tau, tau * zeta % p, beta)
                        total = tuple((c * (1 if j == 2 else 0) + r * x[j] + t * y[j]) % p for j in range(3))
                        assert total == (0, 0, 0)
                        checks += 1
    return checks


def discovery_power_only() -> dict[str, int]:
    primes = (11, 13, 17, 19, 23, 29, 31, 37, 41, 43)
    rows = 0
    parameters = 0
    survivors = 0
    for p in primes:
        H = (p - 1) // 2
        for c in range(1, c_light(p) + 1):
            for d in range(c):
                rows += 1
                e = c - d
                f = d + 1
                r = H + 1 - e
                t = p - f
                tau = (-r * pow(t, -1, p)) % p
                for zeta in range(2, p):
                    for alpha in range(p):
                        parameters += 1
                        beta = (-(c + r * alpha) * pow(t, -1, p)) % p
                        x = (1, zeta, alpha)
                        y = (tau, tau * zeta % p, beta)
                        if not power_window_ok(p, t, y):
                            continue
                        if power_window_ok(p, r, x):
                            survivors += 1
    assert survivors == 0
    return {
        "discovery_primes": len(primes),
        "discovery_rows": rows,
        "two_parameter_points": parameters,
        "power_window_survivors": survivors,
    }


def main() -> None:
    radial = check_radial_formula()
    prime_count, max_twice_c = check_overlap_bound()
    normal = check_normal_form()
    discovery = discovery_power_only()
    print(json.dumps({
        "status": "A3_LIGHT_TWO_PARAMETER_GREEN",
        "radial_points_checked": radial,
        "primes_through_1009": prime_count,
        "max_twice_c_light_seen": max_twice_c,
        "normal_form_checks": normal,
        **discovery,
        "authority": "radial formula, half-overlap bound, and two-parameter normal form are symbolic; bounded zero-survivor scan is discovery only",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
