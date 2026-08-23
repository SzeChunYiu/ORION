"""Test the structure claim DIRECTLY on the extremal D_2 witnesses themselves.

CLAIM (i): with m = D_2(G) - D(G), every sequence of length D_2(G)-1 having no
two disjoint nonempty zero-sums has minimum zero-sum length EXACTLY m.

Lemma A already gives >= m.  The content is <= m.  My earlier reduction
(|S| > f_m) is SUFFICIENT but not necessary, and it fails on C_2^4 -- so test the
witnesses directly."""
import itertools, sys
from collections import Counter
def group(dims):
    els=[e for e in itertools.product(*[range(d) for d in dims])]
    def add(a,b): return tuple((x+y)%d for x,y,d in zip(a,b,dims))
    return els, add, tuple(0 for _ in dims)
def minzs(seq, add, Z):
    n=len(seq)
    for r in range(1,n+1):
        for c in itertools.combinations(range(n),r):
            s=Z
            for i in c: s=add(s,seq[i])
            if s==Z: return r
    return None
def two_disjoint(seq, add, Z):
    k=2
    states={((Z,)*k,(False,)*k)}
    for e in seq:
        new=set(states)
        for sums,fl in states:
            for i in range(k):
                s2=list(sums); f2=list(fl); s2[i]=add(sums[i],e); f2[i]=True
                new.add((tuple(s2),tuple(f2)))
        states=new
    return ((Z,)*k,(True,)*k) in states
def study(dims, D, D2, cap=400000):
    els,add,Z=group(dims)
    nz=[e for e in els if e!=Z]
    m=D2-D; L=D2-1
    seen=Counter(); found=0; scanned=0
    for combo in itertools.combinations_with_replacement(nz, L):
        scanned+=1
        if scanned>cap: return None, m, L, scanned
        s=list(combo)
        if two_disjoint(s,add,Z): continue
        z=minzs(s,add,Z)
        seen[z]+=1; found+=1
    return seen, m, L, scanned
for dims,D,D2,name in [((2,2,2),4,7,"C_2^3"), ((3,3),5,8,"C_3^2"), ((2,2),3,5,"C_2^2")]:
    seen,m,L,sc=study(dims,D,D2)
    if seen is None:
        print(f"{name}: CANNOT_CHECK (scanned {sc} > cap)"); continue
    ok = set(seen)=={m}
    print(f"{name}: D={D} D_2={D2} m={m} witnesses len {L}: "
          f"min-zero-sum histogram {dict(sorted(seen.items()))}  "
          f"-> claim (min ZS == m exactly): {'HOLDS' if ok else 'FAILS'}   [{sum(seen.values())} witnesses]")
