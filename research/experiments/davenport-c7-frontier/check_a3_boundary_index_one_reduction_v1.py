#!/usr/bin/env python3
"""Regression for the a=3 boundary index-one donor reduction."""
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
    """Exact lambda_{3,c}(D) from the one-dimensional radial formula."""
    u = pow(3, -1, p)
    best = 10**9
    for z in range(c + 4):
        q = (D - z) % p
        if q <= p - 3:
            best = min(best, z + q + 2 * ((u * q) % p))
    assert best < 10**9
    return best


def augmented_coeffs(p: int, c: int, d: int) -> tuple[int, int, int, int, int, int]:
    H = (p - 1) // 2
    e = c - d
    f = d + 1
    r = H + 1 - e
    t = p - f
    return e, f, c, r, t, H + 1


def minimal_length_four(p: int, coeffs: tuple[int, int, int, int]) -> bool:
    assert sum(coeffs) == 2 * p
    for i in range(4):
        for j in range(i + 1, 4):
            if coeffs[i] + coeffs[j] == p:
                return False
    return True


def index_one_rows(p: int, coeffs: tuple[int, int, int, int]) -> list[tuple[int, int, int, int, int]]:
    out = []
    for n in range(1, p):
        residues = tuple((n * a) % p for a in coeffs)
        if sum(residues) == p:
            out.append((n, *residues))
    return out


def symbolic_regression() -> tuple[int, int, int]:
    primes = 0
    nonupper_rows = 0
    upper_controls = 0
    for p in range(7, 1010):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2
        for c in range(1, c_light(p) + 1):
            assert c <= H // 2
            for d in range(c):
                e, f, cc, r, t, half = augmented_coeffs(p, c, d)
                coeffs = (cc, r, t, half)
                assert sum(coeffs) == 2 * p
                if e == 1:
                    assert cc + t == p
                    assert r + half == p
                    assert not minimal_length_four(p, coeffs)
                    upper_controls += 1
                    continue

                assert minimal_length_four(p, coeffs)
                idx = index_one_rows(p, coeffs)
                # Donor theorem predicts nonemptiness; this is only a regression check.
                assert idx, (p, c, d, coeffs)
                for n, D, A, B, L in idx:
                    F = (n * f) % p
                    assert B == p - F
                    assert F == D + A + L
                    assert (B <= t) == (F >= f)
                    assert (A <= r) == (F - D - L <= H + 1 - e)
                nonupper_rows += 1
    return primes, nonupper_rows, upper_controls


def bounded_usable_scan() -> tuple[int, int, int]:
    rows = 0
    usable = 0
    index_one_total = 0
    for p in range(7, 200):
        if not is_prime(p):
            continue
        H = (p - 1) // 2
        m = 3 * H + 1
        for c in range(1, c_light(p) + 1):
            for d in range(c):
                e, f, cc, r, t, half = augmented_coeffs(p, c, d)
                if e == 1:
                    continue
                rows += 1
                found = False
                for n, D, A, B, L in index_one_rows(p, (cc, r, t, half)):
                    index_one_total += 1
                    F = (n * f) % p
                    if F < f:
                        continue
                    if A > r or B > t:
                        continue
                    lam = radial_cost(p, c, D)
                    assert (lam + A + B <= m - 1) == (lam - D <= H + L - 1)
                    if lam + A + B <= m - 1:
                        found = True
                        break
                assert found, (p, c, d, r, t)
                usable += 1
    assert usable == rows
    return rows, usable, index_one_total


def main() -> None:
    primes, nonupper, upper = symbolic_regression()
    rows, usable, idx_total = bounded_usable_scan()
    print(json.dumps({
        "status": "A3_BOUNDARY_INDEX_ONE_REDUCTION_GREEN",
        "primes_through_1009": primes,
        "nonupper_rows_checked": nonupper,
        "upper_endpoint_nonminimal_controls": upper,
        "bounded_discovery_rows_through_199": rows,
        "bounded_usable_rows": usable,
        "index_one_multipliers_examined_bounded": idx_total,
        "authority": "minimality and capacity identities are symbolic; index-one existence is donor-owned; bounded usable scan is discovery only",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
