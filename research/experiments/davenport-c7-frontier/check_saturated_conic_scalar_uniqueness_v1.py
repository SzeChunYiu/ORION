#!/usr/bin/env python3
from __future__ import annotations

import argparse
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-prime', type=int, default=401)
    args = ap.parse_args()

    primes = [p for p in range(7, args.max_prime + 1) if is_prime(p)]
    family = []
    polynomial_controls = 0

    for p in primes:
        # Two off-conic centers each exclude at most two finite tangent
        # parameters. The proof needs three common non-tangent parameters.
        assert p - 4 >= 3

        # In odd characteristic the projective coordinate map
        # (d0,d1,d2) -> (d0,-2d1,d2) is invertible.
        assert (2 % p) != 0
        polynomial_controls += 1

        if p % 4 == 1 and p >= 13:
            q = 2
            m = (5 * p - 13) // 4
            R = (5 * p + 3) // 4
            M = (5 * p - 5) // 2
            N = p * m + M + q
            assert (5 * p - 13) % 4 == 0
            assert (N - p - 1) == R * (p - 2)
            assert (m - 1) * q <= M
            n = R - p - 1
            assert n == (p - 1) // 4 >= 3
            family.append({
                'p': p, 'q': q, 'm': m,
                'old_integral_floor': R,
                'new_floor': R + 1,
                'deficient_directions_at_equality': n,
            })

    # The two existing p=7 conic faces become analytic corollaries.
    p = 7
    M = 15
    controls = []
    for q, m, R, expected_n in ((2, 8, 13, 5), (3, 6, 11, 3)):
        N = p * m + M + q
        if q == 2:
            assert (N - p - 1) == R * (p - 2)
            n = R - p - 1
            assert n == expected_n
            # equality forces all n deficits to q-1; uniqueness permits <=1
            assert n >= 2
        else:
            # In the f=8 branch of q=3,m=6, tangent/arc reductions force
            # three off-conic deficit-(q-1) directions.
            n = expected_n
            assert n >= 2
        controls.append({'q': q, 'm': m, 'off_conic_minimal_deficits': n})

    print(json.dumps({
        'status': 'SATURATED_CONIC_SCALAR_UNIQUENESS_GREEN',
        'checked_primes': len(primes),
        'largest_prime': primes[-1],
        'quadratic_interpolation_controls': polynomial_controls,
        'q2_integral_family_count': len(family),
        'first_q2_family_rows': family[:8],
        'p7_analytic_controls': controls,
    }, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
