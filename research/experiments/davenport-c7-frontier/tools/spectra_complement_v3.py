"""Test the eight surviving atom-length spectra against the COMPLEMENT systems, restricted.

For an atom A of length l in an obstruction T with atom-length set L, the complement
C = T A^{-1} has length m = 37-l, z(C) = 2, and its zero-sum sub-multisets are exactly
empty, C, and the atoms of C -- which are atoms of T, so their lengths lie in L, and they
pair up: l' is an atom length of C iff m - l' is too.  So the admissible atom lengths of C are
        S = { l' in L : 8 <= l' <= m-8  and  m - l' in L }.
The counting identity on C gives, for 0 <= d <= m - D,
        sum_{l' in S} (-1)^{l'} M_{l'} C(l',d) + [C(0,d) + (-1)^m C(m,d)] == 0  (mod 7),
with M_{l'} = M_{m-l'}.  If this is infeasible for even one l in L, the spectrum L is dead.
"""
from math import comb
p, NT, D = 7, 37, 19
SPECTRA=[
 {8,9,10,11,14,16,19},{8,9,10,12,14,16,19},{8,9,10,11,12,14,16,19},
 {8,9,10,11,14,16,17,19},{8,9,10,12,14,16,18,19},
 {9,10,11,12,13,16,17,18},{9,10,11,12,13,16,17,19},{9,10,11,12,13,16,17,18,19}]

def feasible_complement(m, S):
    if m <= D:            # complement may be a single atom; no equations to impose
        return True
    reps=sorted({min(l, m-l) for l in S})
    if not reps:
        # C must factor into two atoms, but no admissible lengths -> impossible
        return False
    rows=[]
    for d in range(0, m-D+1):
        row=[0]*len(reps)
        for l in S:
            r=reps.index(min(l,m-l))
            row[r]=(row[r]+((-1)**l)*comb(l,d))%p
        rhs=(-(comb(0,d)+((-1)**m)*comb(m,d)))%p
        rows.append(row+[rhs])
    nv=len(reps); A=[r[:] for r in rows]; mm=len(A); piv=0
    for c in range(nv):
        r=next((i for i in range(piv,mm) if A[i][c]%p),None)
        if r is None: continue
        A[piv],A[r]=A[r],A[piv]
        inv=pow(A[piv][c],p-2,p); A[piv]=[(x*inv)%p for x in A[piv]]
        for i in range(mm):
            if i!=piv and A[i][c]%p:
                f=A[i][c]; A[i]=[(A[i][j]-f*A[piv][j])%p for j in range(nv+1)]
        piv+=1
    return not any(not any(A[i][:nv]) and A[i][nv]%p for i in range(mm))

alive=[]
for L in SPECTRA:
    dead_at=[]
    for l in sorted(L):
        m=NT-l
        S={x for x in L if 8<=x<=m-8 and (m-x) in L}
        if not feasible_complement(m,S):
            dead_at.append((l,sorted(S)))
    if dead_at:
        print(f"L = {sorted(L)}")
        for l,S in dead_at:
            print(f"     KILLED by the complement of a {l}-atom (|C| = {NT-l}, admissible atom lengths {S})")
    else:
        alive.append(L)
        print(f"L = {sorted(L)}   survives all complement systems")
print()
print(f"spectra surviving: {len(alive)} of {len(SPECTRA)}")
for L in alive: print("   ",sorted(L))
if not alive:
    print()
    print("NO SPECTRUM SURVIVES  ->  no obstruction exists  ->  D_3(C_7^3) = 36")
