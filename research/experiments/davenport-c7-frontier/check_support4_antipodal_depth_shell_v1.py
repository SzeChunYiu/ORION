#!/usr/bin/env python3
"""Regression for the antipodal depth shell of support-four maximal atoms."""

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


def neg(v: tuple[int, int, int], p: int) -> tuple[int, int, int]:
    return tuple((-x) % p for x in v)


def rho_table(p: int, a: int) -> dict[tuple[int, int, int], int]:
    inv = pow(a, -1, p)
    out: dict[tuple[int, int, int], int] = {(0, 0, 0): 0}
    for x1 in range(p):
        for x2 in range(p):
            for x3 in range(p):
                x = (x1, x2, x3)
                if x == (0, 0, 0):
                    continue
                best = 10**9
                for t in range(p - a + 1):
                    c1 = (x1 + inv * t) % p
                    c2 = (x2 + inv * t) % p
                    c3 = (x3 - t) % p
                    if c3 <= a:
                        best = min(best, c1 + c2 + c3 + t)
                out[x] = best
    return out


def predicted_delta_p(p: int, a: int, x: tuple[int, int, int]) -> bool:
    x1, x2, x3 = x

    if x1 != 0 and x2 == 0 and x3 == 0:
        return True
    if x2 != 0 and x1 == 0 and x3 == 0:
        return True

    if x3 == 0:
        return False
    inv = pow(a, -1, p)
    g4 = ((-inv) % p, (-inv) % p, 1)
    r = x3
    if x == ((r * g4[0]) % p, (r * g4[1]) % p, r):
        return a <= r <= p - a

    return False


def main() -> None:
    primes = [p for p in range(5, 44) if is_prime(p)]
    checked_types = 0
    checked_targets = 0
    equality_targets = 0

    for p in primes:
        for a in range(1, (p - 1) // 2 + 1):
            checked_types += 1
            rho = rho_table(p, a)
            for x, d in rho.items():
                if x == (0, 0, 0):
                    continue
                checked_targets += 1
                delta = d + rho[neg(x, p)]
                assert delta >= p, (p, a, x, delta)
                predicted = predicted_delta_p(p, a, x)
                actual = delta == p
                assert actual == predicted, (p, a, x, delta, predicted)
                equality_targets += int(actual)

    print(
        json.dumps(
            {
                "status": "SUPPORT4_ANTIPODAL_DEPTH_SHELL_GREEN",
                "checked_primes": len(primes),
                "max_prime": primes[-1],
                "checked_types": checked_types,
                "checked_targets": checked_targets,
                "delta_p_targets": equality_targets,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
