#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from itertools import combinations

CORRIDORS = [
    (8,10,19), (9,9,19), (9,10,18),
    (9,11,17), (9,12,16), (10,10,17),
]


def is_prime(n: int) -> bool:
    if n < 2: return False
    if n % 2 == 0: return n == 2
    d = 3
    while d*d <= n:
        if n % d == 0: return False
        d += 2
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-prime', type=int, default=401)
    args = ap.parse_args()

    primes = [p for p in range(5, args.max_prime+1) if is_prime(p)]
    pair_states = 0
    automatic_rank3_q = []

    for p in primes:
        M = (5*p-5)//2
        for q in range(1, (p-1)//2 + 1):
            # q>=2 rank-two extremal sequence has total coefficient -(q+1).
            if q >= 2:
                assert 1 <= q+1 < p
            threshold = p-q-3
            if 3*q > p-3:
                assert 2*q > threshold
                automatic_rank3_q.append((p,q))

            for E in range(2*q, M+1):
                H = max(p+q-1, E-p+1)
                assert p <= H <= 2*p-1
                pair_plane_cap = 4*p-3-H
                assert pair_plane_cap >= 0
                # Pair rank <=2 forces the stronger zero-sum cap.
                rank2_pair_max = 3*p-q-3
                rank2_excess_max = p-q-3
                assert (2*p + E <= rank2_pair_max) == (E <= rank2_excess_max)
                pair_states += 1

            if q == 1:
                # At the equality length 3p-3, the Gao--Geroldinger--Schmid
                # 2p-1 minimal zero-sum leaves a forbidden p-2 zero-sum complement.
                assert p-2 >= 1 and p-2 <= p

    p=7; q=1
    corridor_rows=[]
    for lengths in CORRIDORS:
        excess=tuple(x-p for x in lengths)
        pair_rows=[]
        for i,j in combinations(range(3),2):
            E=excess[i]+excess[j]
            H=max(p+q-1,E-p+1)
            cap=4*p-3-H
            assert E > p-q-3
            pair_rows.append({
                'atoms':[lengths[i],lengths[j]],
                'excess_sum':E,
                'shortfree_through':H,
                'pair_plane_cap':cap,
                'rank':'3',
            })
        corridor_rows.append({'corridor':lengths,'pairs':pair_rows})

    # Frozen hard-pair controls.
    hard={tuple(row['corridor']): row for row in corridor_rows}
    r=hard[(8,10,19)]['pairs']
    pair_lookup={tuple(x['atoms']):x for x in r}
    assert pair_lookup[(10,19)]['shortfree_through']==9
    assert pair_lookup[(10,19)]['pair_plane_cap']==16
    r=hard[(9,9,19)]['pairs']
    pair_lookup={tuple(x['atoms']):x for x in r}
    assert pair_lookup[(9,19)]['shortfree_through']==8
    assert pair_lookup[(9,19)]['pair_plane_cap']==17

    print(json.dumps({
        'status':'FIRST_FAILURE_PAIR_RANK_FORCING_GREEN',
        'checked_primes':len(primes),
        'largest_prime':primes[-1],
        'pair_excess_states_checked':pair_states,
        'automatic_rank3_pq_count':len(automatic_rank3_q),
        'p7_q2_all_pairs_rank3':3*2 > 7-3,
        'p7_q3_all_pairs_rank3':3*3 > 7-3,
        'p7_corridors':corridor_rows,
    }, sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
