#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from itertools import combinations

P=7
M=15
CORRIDORS={
    (8,10,19), (9,9,19), (9,10,18),
    (9,11,17), (9,12,16), (10,10,17),
}


def signatures(total,parts,lo,hi):
    values=list(range(lo,hi+1))
    counts=[0]*len(values)
    out=[]
    def visit(idx,left_parts,left_sum):
        if idx==len(values):
            if left_parts==0 and left_sum==0:
                row=[]
                for value,count in zip(values,counts):
                    row.extend([value]*count)
                out.append(tuple(row))
            return
        value=values[idx]
        for count in range(min(left_parts,left_sum//value)+1):
            counts[idx]=count
            visit(idx+1,left_parts-count,left_sum-count*value)
        counts[idx]=0
    visit(0,parts,total)
    return out


def main()->int:
    # Independently rebuild the coding-refined p7 shell and current donor filters.
    L=123
    K=15
    rows=[]
    for m in range(3,K+1):
        qmax=min(M//(m-1),L-P*m-M)
        for q in range(1,qmax+1):
            for e in signatures(M+q,m,q,12):
                rows.append((m,q,e))
    assert len(rows)==321

    current=[]
    for m,q,e in rows:
        if q>3: continue
        if min(e)>5: continue
        if m==3 and q==1:
            lengths=tuple(P+x for x in e)
            if lengths not in CORRIDORS: continue
        current.append((m,q,e))
    assert len(current)==286

    q_counts=Counter()
    forced_pairs=0
    total_pairs=0
    violations=[]
    for m,q,e in current:
        threshold=P-q-3
        all_forced=True
        for i,j in combinations(range(m),2):
            total_pairs+=1
            if e[i]+e[j] > threshold:
                forced_pairs+=1
            else:
                all_forced=False
        q_counts[(q,all_forced)]+=1
        if q>=2 and not all_forced:
            violations.append((m,q,e))
    assert not violations

    # q=1,m=3 exact corridors: every displayed pair is rank-three-forced.
    corridor_count=0
    for m,q,e in current:
        if (m,q)==(3,1):
            assert tuple(P+x for x in e) in CORRIDORS
            assert all(e[i]+e[j]>3 for i,j in combinations(range(3),2))
            corridor_count+=1
    assert corridor_count==6

    # Direct endpoint arithmetic: q>=2 inverse extremal sum is nonzero.
    endpoint=[]
    for p in (5,7,11,13):
        for q in range(2,(p-1)//2+1):
            coeff=(-q-1)%p
            assert coeff!=0
            endpoint.append((p,q,coeff))

    print(json.dumps({
        'status':'FIRST_FAILURE_PAIR_RANK_FORCING_INDEPENDENT_GREEN',
        'p7_current_signatures':len(current),
        'p7_q2_q3_rank3_violations':len(violations),
        'p7_exact_q1_m3_corridors':corridor_count,
        'pair_checks':total_pairs,
        'forced_pair_checks':forced_pairs,
        'signature_full_rank3_distribution':{f'q{q}_{flag}':n for (q,flag),n in sorted(q_counts.items())},
        'rank2_extremal_nonzero_sum_controls':len(endpoint),
    }, sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
