"""The full chain with a SELF-CONTAINED corridor 1.

Self-contained corridor derivation (no Zhao, no Zhang):
  every atom has length >= 8            [from D_2 = 29, proved in this packet]
  |B|=37 zero-sum has a zero-sum of length <= 10   [congruence system, verified]
     => the shortest atom length s is in {8,9,10}
  C = B A^{-1} for a shortest atom A has length 37-s in {27,28,29} > D, so z(C)=2 and every
  atom W of C pairs with C W^{-1}, both atoms of B, so |W| >= s and 37-s-|W| <= 19.
  Congruences on C give an atom of length <= 10 (|C|=29), <= 14 (|C|=28), <= 10 (|C|=27).
     s=8 : |W| >= 10 (since 29-|W| <= 19) and <= 10  -> (8,10,19)
     s=9 : |W| in [9,14]                             -> (9,9,19),(9,10,18),(9,11,17),
                                                        (9,12,16),(9,13,15),(9,14,14)
     s=10: |W| >= 10 and <= 10                       -> (10,10,17)
"""
from math import comb
from itertools import combinations
p, NT, D, AMIN = 7, 37, 19, 8
LENS=list(range(AMIN,D+1))
C1_SELF={(8,10,19),(9,9,19),(9,10,18),(9,11,17),(9,12,16),(9,13,15),(9,14,14),(10,10,17)}

def _solve(rows,nv):
    A=[r[:] for r in rows]; m=len(A); piv=0
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

def feas_T(L):
    zero=set(LENS)-set(L); cols=[]
    for l in LENS:
        if l in zero: continue
        cols.append(lambda d,l=l: (((-1)**l)*(comb(l,d)-comb(NT-l,d)))%p)
    for l in (18,19):
        if l in zero: continue
        cols.append(lambda d,l=l: (-((-1)**l)*comb(l,d))%p)
    rows=[[f(d) for f in cols]+[(-(comb(0,d)-comb(NT,d)))%p] for d in range(0,NT-D+1)]
    return _solve(rows,len(cols))

def feas_C(m,S):
    if m<=D: return True
    reps=sorted({min(l,m-l) for l in S})
    if not reps: return False
    rows=[]
    for d in range(0,m-D+1):
        row=[0]*len(reps)
        for l in S:
            r=reps.index(min(l,m-l)); row[r]=(row[r]+((-1)**l)*comb(l,d))%p
        rows.append(row+[(-(comb(0,d)+((-1)**m)*comb(m,d)))%p])
    return _solve(rows,len(reps))

def profiles_through(l,L,s):
    out=set()
    for u in L:
        v=NT-l-u
        if v in L and u<=v and u>=s and v>=s: out.add(tuple(sorted((l,u,v))))
    return out

surv=[]
for k in range(1,len(LENS)+1):
    for Lt in combinations(LENS,k):
        L=set(Lt)
        if not feas_T(L): continue
        s=min(L)
        if s>10: continue                                   # shortest atom <= 10
        # closure
        bad=False
        for l in sorted(L):
            if profiles_through(l,L,s): continue
            if l in (18,19) and (NT-l) in L: continue
            bad=True; break
        if bad: continue
        # corridor-1 consistency, self-contained version
        allP=set()
        for l in sorted(L): allP|=profiles_through(l,L,s)
        if any(s in P and P not in C1_SELF for P in allP): continue
        if not any(set(P)<=L for P in C1_SELF): continue
        # complement systems
        ok=True
        for l in sorted(L):
            m=NT-l
            S={x for x in L if AMIN<=x<=m-AMIN and (m-x) in L}
            if not feas_C(m,S): ok=False; break
        if ok: surv.append(sorted(L))
print(f"spectra surviving the FULLY SELF-CONTAINED chain: {len(surv)}")
for L in surv: print("   ",L)
print()
if not surv:
    print("NO SPECTRUM SURVIVES -> no length-37 obstruction over C_7^3 -> D_3(C_7^3) = 36,")
    print("with no donor input beyond Olson's D(C_7^3) = 19.")
