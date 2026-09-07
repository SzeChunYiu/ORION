"""Factorization-closure of the atom-length set.

Let L be the set of atom lengths of an obstruction T and s = min L.  For every atom A of
length l:
  * if l <= 17 then |T A^{-1}| = 37-l >= 20 > D, so T A^{-1} is not an atom; z = 2 and it
    splits into two atoms, whose lengths lie in L.  So there are u,v in L with u+v = 37-l.
  * if l in {18,19} the complement has length 19 or 18 <= D and may itself be an atom, so the
    requirement is weaker: either 37-l in L, or u+v = 37-l for some u,v in L.
Moreover any 3-atom factorization CONTAINING an atom of the minimum length s must be a
corridor-1 triple (that is exactly what ATOM_LENGTH_CORRIDOR_V1's proof gives).
Finally L must contain 13 or 14 (atom-spectrum theorem).

Test all 548 feasible sets against these.
"""
from math import comb
from itertools import combinations
p, NT, D = 7, 37, 19
LENS=list(range(8,20))
C1={(8,10,19),(9,9,19),(9,10,18),(9,11,17),(9,12,16),(10,10,17)}

def feasible(L):
    zero=set(LENS)-set(L)
    cols=[]
    for l in LENS:
        if l in zero: continue
        cols.append(lambda d,l=l: (((-1)**l)*(comb(l,d)-comb(NT-l,d)))%p)
    for l in (18,19):
        if l in zero: continue
        cols.append(lambda d,l=l: (-((-1)**l)*comb(l,d))%p)
    rows=[[f(d) for f in cols]+[(-(comb(0,d)-comb(NT,d)))%p] for d in range(0,NT-D+1)]
    nv=len(cols); A=[r[:] for r in rows]; m=len(A); piv=0
    for c in range(nv):
        r=next((i for i in range(piv,m) if A[i][c]%p),None)
        if r is None: continue
        A[piv],A[r]=A[r],A[piv]
        inv=pow(A[piv][c],p-2,p); A[piv]=[(x*inv)%p for x in A[piv]]
        for i in range(m):
            if i!=piv and A[i][c]%p:
                f=A[i][c]; A[i]=[(A[i][j]-f*A[piv][j])%p for j in range(nv+1)]
        piv+=1
    return not any(not any(A[i][:nv]) and A[i][nv]%p for i in range(m))

def profiles_through(l, L, s):
    out=[]
    for u in L:
        v=NT-l-u
        if v in L and u<=v and u>=s and v>=s:
            out.append(tuple(sorted((l,u,v))))
    return set(out)

surv=[]
tested=0
for k in range(1,len(LENS)+1):
    for Lt in combinations(LENS,k):
        L=set(Lt)
        if not (13 in L or 14 in L): continue
        if not feasible(L): continue
        tested+=1
        s=min(L)
        ok=True
        for l in sorted(L):
            P=profiles_through(l,L,s)
            if not P:
                if l in (18,19) and (NT-l) in L: continue      # complement is itself an atom
                ok=False; break
        if not ok: continue
        # every profile containing the minimum length s must be a corridor-1 triple
        allP=set()
        for l in sorted(L): allP |= profiles_through(l,L,s)
        if any(s in P and tuple(sorted(P)) not in C1 for P in allP): continue
        if not any(set(P)<=L for P in C1): continue
        surv.append(sorted(L))
print(f"feasible sets containing 13 or 14: {tested}")
print(f"surviving factorization-closure + corridor-1 consistency: {len(surv)}")
for L in surv[:40]: print("   ",L)
if not surv:
    print()
    print("NO SET SURVIVES  ->  no obstruction exists  ->  D_3(C_7^3) = 36")
