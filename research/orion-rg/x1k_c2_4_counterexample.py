"""C_2^4 is the decisive case: D=5, D_2=8, m=3, witnesses of length 7.
Here f_3(C_2^4) = 8 > D_2-2 = 6, so the sufficient condition FAILS -- there DO
exist length-7 sequences with min zero-sum > 3.  Do any of them have no two
disjoint zero-sums?  If yes the claim is refuted; if no it is stronger than the
reduction."""
import itertools
from collections import Counter
dims=(2,2,2,2); Z=(0,0,0,0)
def add(a,b): return tuple((x+y)%2 for x,y in zip(a,b))
nz=[e for e in itertools.product(*[range(d) for d in dims]) if e!=Z]
def minzs(seq):
    n=len(seq)
    for r in range(1,n+1):
        for c in itertools.combinations(range(n),r):
            s=Z
            for i in c: s=add(s,seq[i])
            if s==Z: return r
    return None
def two_disjoint(seq):
    states={((Z,Z),(False,False))}
    for e in seq:
        new=set(states)
        for sums,fl in states:
            for i in (0,1):
                s2=list(sums); f2=list(fl); s2[i]=add(sums[i],e); f2[i]=True
                new.add((tuple(s2),tuple(f2)))
        states=new
    return ((Z,Z),(True,True)) in states
L=7; m=3
hist=Counter(); n_wit=0; longminzs=0; scanned=0
for combo in itertools.combinations_with_replacement(nz,L):
    scanned+=1
    s=list(combo)
    z=minzs(s)
    if z is not None and z>m: longminzs+=1
    if two_disjoint(s): continue
    n_wit+=1; hist[z]+=1
print(f"C_2^4: scanned {scanned} multisets of length {L}")
print(f"  length-7 multisets with min zero-sum > m=3 (the sufficient condition's failure): {longminzs}")
print(f"  extremal D_2 witnesses (no two disjoint): {n_wit}")
print(f"  their min-zero-sum histogram: {dict(sorted(hist.items()))}")
print(f"  CLAIM (min ZS == m exactly): {'HOLDS' if set(hist)=={m} else 'FAILS'}")
