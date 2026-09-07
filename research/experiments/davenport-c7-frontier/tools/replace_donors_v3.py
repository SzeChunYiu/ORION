"""Can the corridor theorem's two donor inputs be replaced by this packet's own machinery?

ATOM_LENGTH_CORRIDOR_V1 uses:
  (i)  Zhao Lemma 4.4 on B (|B|=37) -> a zero-sum subsequence of length <= 10;
  (ii) Zhao again on C (|C|=29, |C|=27) -> an atom of length <= 10;
  (iii) Zhang's s_{<=12}(C_7^3)=26 on C (|C|=28) -> an atom of length <= 12.

Each is a "short zero-sum exists" statement. Test each with the packet's own congruence
systems: if forbidding the short lengths is INFEASIBLE, the statement follows without donors.
"""
from math import comb
p, D = 7, 19

def solve(rows,nv):
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

def general_short(N, w):
    """Every zero-sum seq of length N has a zero-sum subsequence of length <= w?
    Forbid lengths 1..w and (by complementation) N-w..N-1; infeasible => statement holds."""
    forb=set(range(1,w+1))|set(range(N-w,N))
    allowed=[l for l in range(N+1) if l not in forb]
    idx={}
    for l in allowed:
        if 0<l<N: idx.setdefault(min(l,N-l),len(idx))
    rows=[]
    for d in range(0,N-D+1):
        coef=[0]*len(idx); rhs=0
        for l in allowed:
            c=((-1)**l)*comb(l,d)
            if l in (0,N): rhs-=c
            else: coef[idx[min(l,N-l)]]=(coef[idx[min(l,N-l)]]+c)
        rows.append([x%p for x in coef]+[rhs%p])
    return not solve(rows,len(idx))

def pk2_short(m, w):
    """C zero-sum with z(C)=2 (so its proper zero-sums are atoms, paired to m).
    Does C have an atom of length <= w?  Forbid atom lengths <= w: admissible lengths are
    [w+1, m-w-1]; infeasible => an atom of length <= w must exist."""
    S=[l for l in range(w+1, m-w) if 8<=l<=m-8]
    reps=sorted({min(l,m-l) for l in S})
    if not reps: return True                     # nothing admissible at all
    rows=[]
    for d in range(0,m-D+1):
        row=[0]*len(reps)
        for l in S:
            r=reps.index(min(l,m-l)); row[r]=(row[r]+((-1)**l)*comb(l,d))%p
        rows.append(row+[(-(comb(0,d)+((-1)**m)*comb(m,d)))%p])
    return not solve(rows,len(reps))

print("(i)   |B| = 37, zero-sum of length <= 10 :", general_short(37,10))
print("      (control: length <= 9 should NOT be derivable:", general_short(37,9), ")")
print("(ii)  |C| = 29, z=2, atom of length <= 10 :", pk2_short(29,10))
print("(ii') |C| = 27, z=2, atom of length <= 10 :", pk2_short(27,10))
print("(iii) |C| = 28, z=2, atom of length <= 12 :", pk2_short(28,12))
print()
ok = general_short(37,10) and pk2_short(29,10) and pk2_short(27,10) and pk2_short(28,12)
print("All three donor inputs reproducible from this packet's congruences:", ok)
