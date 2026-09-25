#!/usr/bin/env python3
"""Regression and bounded discovery for the a=3 upper endpoint odd-multiplier reduction."""
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


def radial_cost(p: int, c: int, D: int) -> int:
    u = pow(3, -1, p)
    best = 10**9
    for z in range(c + 4):
        q = (D - z) % p
        if q <= p - 3:
            best = min(best, z + q + 2 * ((u * q) % p))
    assert best < 10**9
    return best


def main() -> None:
    primes = 0
    algebra_checks = 0
    discovery_rows = 0
    discovery_survivors = 0
    literal_only_residuals = 0

    for p in range(7, 1010):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2
        m = 3 * H + 1
        for c in range(1, c_light(p) + 1):
            # Even multipliers: x coefficient always exceeds H.
            for q in range(1, H + 1):
                A = (2 * q * H) % p
                assert A == p - q
                assert A > H
                algebra_checks += 1

            # Odd multipliers: exact coefficient and short-zero identities.
            for q in range(0, H):
                n = 2 * q + 1
                D = (n * c) % p
                A = (n * H) % p
                B = (n * (p - c)) % p
                assert A == H - q
                assert B == p - D
                assert (B <= p - c) == (D >= c)
                lam = radial_cost(p, c, D)
                total = lam + A + B
                assert (total <= m - 1) == (lam - D <= q - 1)
                algebra_checks += 1

    for p in range(7, 402):
        if not is_prime(p):
            continue
        H = (p - 1) // 2
        for c in range(1, c_light(p) + 1):
            discovery_rows += 1
            found = False
            literal_found = False
            for q in range(1, H):
                D = ((2 * q + 1) * c) % p
                if D < c:
                    continue
                lam = radial_cost(p, c, D)
                if c <= D <= c + 3:
                    assert lam == D
                    literal_found = True
                if lam - D <= q - 1:
                    found = True
                    break
            if not literal_found:
                literal_only_residuals += 1
            if not found:
                discovery_survivors += 1

    assert discovery_survivors == 0
    assert literal_only_residuals > 0

    print(json.dumps({
        "status": "A3_UPPER_ENDPOINT_ODD_MULTIPLIER_GREEN",
        "primes_through_1009": primes,
        "algebra_checks": algebra_checks,
        "bounded_endpoint_rows_through_401": discovery_rows,
        "bounded_exact_criterion_residuals": discovery_survivors,
        "literal_only_residual_rows": literal_only_residuals,
        "authority": "odd/even scalar reduction symbolic; bounded zero-residual scan discovery only",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
