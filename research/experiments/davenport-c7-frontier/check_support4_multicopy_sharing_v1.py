#!/usr/bin/env python3
"""Bounded regression for exact multi-copy sharing criteria.

The theorem is analytic.  This checker deliberately separates:
  * brute oracle-vs-interval equivalence on a finite prime set; and
  * cheap algebraic/singleton regression through p=401.
It does not perform the accidentally super-polynomial all-p<=401 brute loop
from the first draft.
"""

from __future__ import annotations

import json
from math import ceil


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


def rho_formula(p: int, a: int, x: tuple[int, int, int]) -> int:
    u = pow(a, -1, p)
    best = 10**9
    for t in range(p - a + 1):
        c1 = (x[0] + u * t) % p
        c2 = (x[1] + u * t) % p
        c3 = (x[2] - t) % p
        if c3 <= a:
            best = min(best, c1 + c2 + c3 + t)
    return best


def mul(r: int, x: tuple[int, int, int], p: int) -> tuple[int, int, int]:
    return tuple((r * y) % p for y in x)


def neg(x: tuple[int, int, int], p: int) -> tuple[int, int, int]:
    return tuple((-y) % p for y in x)


def brute_prefix_ok(p: int, a: int, j: int, side: str, c: int) -> bool:
    b = (p + 1) // 2 - j
    m = p + b
    u = pow(a, -1, p)
    s = (0, 0, 1) if side == "light" else ((-u) % p, (-u) % p, 1)
    for r in range(1, c + 1):
        if r + rho_formula(p, a, neg(mul(r, s, p), p)) < m:
            return False
    return True


def interval_prefix_ok(p: int, a: int, j: int, side: str, c: int) -> bool:
    b = (p + 1) // 2 - j
    h = ceil(b / 2)
    u = pow(a, -1, p)
    if side == "light":
        lo, hi = a, a + c
    else:
        lo, hi = a - c, a
    return all((u * k) % p <= p - h for k in range(lo, hi + 1))


def main() -> None:
    brute_primes = [5, 7, 11, 13, 17, 19, 23]
    brute_cases = 0

    # Complete oracle-vs-closed-form check on a deliberately bounded prime set.
    for p in brute_primes:
        for j in range(1, (p + 1) // 4 + 1):
            for a in range(1, (p - 1) // 2 + 1):
                for c in range(1, p - a):
                    assert brute_prefix_ok(p, a, j, "light", c) == interval_prefix_ok(
                        p, a, j, "light", c
                    )
                    brute_cases += 1
                for c in range(1, a):
                    assert brute_prefix_ok(p, a, j, "heavy", c) == interval_prefix_ok(
                        p, a, j, "heavy", c
                    )
                    brute_cases += 1

    # Cheap all-corridor endpoint algebra through p=401.
    broad_primes = [p for p in range(5, 402) if is_prime(p)]
    broad_rows = 0
    for p in broad_primes:
        for j in range(1, (p + 1) // 4 + 1):
            b = (p + 1) // 2 - j
            h = ceil(b / 2)
            for a in range(1, (p - 1) // 2 + 1):
                u = pow(a, -1, p)
                broad_rows += 1

                # Singleton cases of the interval theorem, equivalent to the
                # previously committed inverse selector.
                light_one = (p - 1 - a) >= 1 and ((u * (a + 1)) % p <= p - h)
                assert light_one == (u <= p - h - 1)
                if a > 1:
                    heavy_one = ((u * (a - 1)) % p <= p - h)
                    assert heavy_one == (u >= h + 1)

                # The interval endpoints always stay among nonzero residues.
                assert a + (p - 1 - a) == p - 1
                assert a - (a - 1) == 1

    # Frozen p=7, j=1 exact maxima.
    p, j = 7, 1
    frozen = []
    for a in (1, 2, 3):
        cl = 0
        for c in range(1, p - a):
            if interval_prefix_ok(p, a, j, "light", c):
                cl = c
            else:
                break
        ch = 0
        for c in range(1, a):
            if interval_prefix_ok(p, a, j, "heavy", c):
                ch = c
            else:
                break
        frozen.append((cl, ch))
    assert frozen == [(4, 0), (2, 1), (0, 2)]

    print(
        json.dumps(
            {
                "status": "SUPPORT4_MULTICOPY_SHARING_GREEN",
                "brute_primes": brute_primes,
                "brute_cases": brute_cases,
                "broad_max_prime": broad_primes[-1],
                "broad_type_corridor_rows": broad_rows,
                "p7_j1": frozen,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
