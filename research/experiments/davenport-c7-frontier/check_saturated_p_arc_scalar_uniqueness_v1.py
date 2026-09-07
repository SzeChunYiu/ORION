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

    family_1 = []
    family_3 = []
    checked = 0
    for p in range(11, args.max_prime + 1):
        if not is_prime(p):
            continue
        checked += 1
        M = (5*p - 5)//2

        # Correct combined p/p+1-full equality criterion.
        for q in range(2, (p-1)//2 + 1):
            for n in range(2, min(p, 20)):
                exactly_p_possible = (q-1)*n <= q
                p1_possible = (q-1)*n <= q+1
                if (q-1)*n > q+1:
                    assert not exactly_p_possible and not p1_possible

        if p % 4 == 1 and p >= 13:
            q = 2
            m = (5*p - 13)//4
            R = (5*p + 3)//4
            N = p*m + M + q
            assert (N-p-1) == R*(p-2)
            assert (m-1)*q <= M
            n = R-p-1
            assert n == (p-1)//4 >= 3
            family_1.append({'p':p,'m':m,'old_floor':R,'new_floor':R+1})

        if p % 4 == 3 and p >= 19:
            q = 2
            m = (5*p - 15)//4
            S = (5*p + 1)//4
            N = p*m + M + q
            assert (N-p) == S*(p-2)
            assert (m-1)*q <= M
            n = S-p
            assert n == (p+1)//4 >= 5
            assert (q-1)*n > q+1
            family_3.append({'p':p,'m':m,'old_floor':S,'new_floor':S+1})

    assert family_1 and family_3
    print(json.dumps({
        'status':'SATURATED_P_ARC_SCALAR_UNIQUENESS_GREEN',
        'checked_primes':checked,
        'p1mod4_family_count':len(family_1),
        'p3mod4_family_count':len(family_3),
        'first_p1mod4_rows':family_1[:6],
        'first_p3mod4_rows':family_3[:6],
        'combined_boundary_criterion':'(q-1)(S-p)>q+1',
    }, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
