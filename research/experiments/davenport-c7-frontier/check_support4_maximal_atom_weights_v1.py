#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json

PRIMES=(5,7,11,13,17,19,23,29,31,37,41,43)
EXPECTED_DIGEST='a487c1a62edbd986963d7f72d2edccbacfdb2f9ea695c7f8020ad60db3876dc0'


def jump_set(p:int,a:int)->frozenset[int]:
    return frozenset(t for t in range(2,p) if (t*a)%p<a)


def patterns(p:int):
    target=set(range(2,p))
    out=[]
    for aa in itertools.combinations_with_replacement(range(1,p),4):
        if sum(aa)!=p+2:
            continue
        seen=set()
        ok=True
        for a in aa:
            c=jump_set(p,a)
            if seen.intersection(c):
                ok=False; break
            seen.update(c)
        if ok and seen==target:
            out.append(aa)
    return out


def expected(p:int):
    return sorted({tuple(sorted((1,1,a,p-a))) for a in range(1,(p-1)//2+1)})


def inv(x:int,p:int)->int:
    return pow(x,-1,p)


def main()->int:
    rows={}
    for p in PRIMES:
        got=patterns(p)
        exp=expected(p)
        assert got==exp,(p,got,exp)
        assert len(got)==(p-1)//2
        rows[str(p)]=got

        # For p>=11, replay the four odd reciprocal moment identities that
        # drive the analytic rational-function proof.
        if p>=11:
            for aa in got:
                xs=[inv(a,p) for a in aa]
                assert sum(aa)%p==2
                for k in (1,3,5,7):
                    assert sum(pow(x,k,p) for x in xs)%p==2

    digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert digest==EXPECTED_DIGEST,digest
    assert patterns(5)==[(1,1,1,4),(1,1,2,3)]
    assert patterns(7)==[(1,1,1,6),(1,1,2,5),(1,1,3,4)]

    print(json.dumps({
        'status':'SUPPORT4_MAXIMAL_ATOM_WEIGHTS_GREEN',
        'checked_primes':list(PRIMES),
        'canonical_a_pattern_digest':digest,
        'p5_patterns':len(rows['5']),
        'p7_patterns':len(rows['7']),
        'p43_patterns':len(rows['43']),
        'theorem_pattern':'{1,1,a,p-a} for deficits, equivalently {p-1,p-1,a,p-a} for multiplicities',
    },sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
