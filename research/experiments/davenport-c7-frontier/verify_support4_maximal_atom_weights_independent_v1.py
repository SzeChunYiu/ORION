#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json

PRIMES=(5,7,11,13,17,19,23,29,31,37,41,43)
EXPECTED_DIGEST='627be4b250b8d434ff67ea56849e13c44a5ee3b6977fc42ab3306f071c485332'


def primitive_weight_patterns(p:int):
    out=[]
    for ww in itertools.combinations_with_replacement(range(1,p),4):
        if sum(ww)!=3*p-2:
            continue
        primitive=True
        for t in range(2,p):
            rr=[(t*w)%p for w in ww]
            # rr is the unique positive count vector in the t-th kernel class.
            if all(r<=w for r,w in zip(rr,ww)):
                primitive=False
                break
        if primitive:
            out.append(ww)
    return out


def expected(p:int):
    return sorted({tuple(sorted((p-1,p-1,a,p-a))) for a in range(1,(p-1)//2+1)})


def main()->int:
    rows={}
    for p in PRIMES:
        got=primitive_weight_patterns(p)
        exp=expected(p)
        assert got==exp,(p,got,exp)
        rows[str(p)]=got

        # Hostile converse check: every displayed pattern really is primitive
        # against all p-2 nontrivial scalar kernel multiples.
        for ww in exp:
            for t in range(2,p):
                rr=[(t*w)%p for w in ww]
                assert any(r>w for r,w in zip(rr,ww))

    digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert digest==EXPECTED_DIGEST,digest

    print(json.dumps({
        'status':'SUPPORT4_MAXIMAL_ATOM_WEIGHTS_INDEPENDENT_GREEN',
        'method':'direct multiplicity-box primitive kernel scan',
        'checked_primes':list(PRIMES),
        'canonical_weight_digest':digest,
        'p7_weights':rows['7'],
    },sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
