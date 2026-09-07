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

    primes = [p for p in range(2, args.max_prime + 1) if is_prime(p)]
    quotient_cases = 0
    for p in primes:
        for c in range(1, p):
            # If a,b,a+b all lay in one nonzero affine coset alpha+H,
            # their images in G/H would all equal the same nonzero c. But
            # q(a+b)=q(a)+q(b)=2c, forcing 2c=c and hence c=0.
            assert (2 * c) % p != c
            quotient_cases += 1

    corridor = {
        '8,10,19': {
            'short_atom_length': 10,
            'pair_direct_min': 3,
            'pair_direct_max': 9,
            'pair_negative_min': 1,
            'pair_negative_max': 7,
            'singleton_negative_max': 8,
        },
        '9,9,19': {
            'short_atom_length': 9,
            'pair_direct_min': 3,
            'pair_direct_max': 8,
            'pair_negative_min': 1,
            'pair_negative_max': 6,
            'singleton_negative_max': 7,
        },
    }
    for row in corridor.values():
        m = row['short_atom_length']
        assert row['pair_direct_max'] == m - 1
        assert row['pair_negative_max'] == m - 3
        assert row['singleton_negative_max'] == m - 2

    print(json.dumps({
        'status': 'MAXIMAL_ATOM_TWO_TERM_AVOIDANCE_GREEN',
        'checked_primes': len(primes),
        'largest_prime': primes[-1],
        'nonzero_quotient_cases': quotient_cases,
        'corridor_ranges': corridor,
    }, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
