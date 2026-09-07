"""Do closure + complement systems kill ALL feasible spectra, WITHOUT the corridor theorem?

Inputs used here, all self-contained in this packet:
  - Olson D(C_7^3) = 19;
  - D_2(C_7^3) = 29 (proved in D2_UNIFORM_SELFCONTAINED_THEOREM_V3);
  - min atom length 8 (Lemma 2.2, proved from D_2);
  - the counting identity and the zero-sum multiset characterisation (validated).
NOT used: ATOM_LENGTH_CORRIDOR_V1 (which is donor-conditional).
"""
from math import comb
from itertools import combinations
p, NT, D, AMIN = 7, 37, 19, 8
LENS=list(range(AMIN,D+1))

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

def closed(L):
    for l in sorted(L):
        m=NT-l
        if any((u in L) and (m-u in L) and u>=AMIN and m-u>=AMIN for u in L): continue
        if l in (18,19) and m in L: continue
        return False
    return True

survivors=[]; nfeas=0; nclosed=0
for k in range(1,len(LENS)+1):
    for Lt in combinations(LENS,k):
        L=set(Lt)
        if not feas_T(L): continue
        nfeas+=1
        if not closed(L): continue
        nclosed+=1
        ok=True
        for l in sorted(L):
            m=NT-l
            S={x for x in L if AMIN<=x<=m-AMIN and (m-x) in L}
            if not feas_C(m,S): ok=False; break
        if ok: survivors.append(sorted(L))
print(f"feasible spectra (T-system):            {nfeas}")
print(f"  ... also factorization-closed:        {nclosed}")
print(f"  ... also surviving complement systems: {len(survivors)}")
for L in survivors[:20]: print("     ",L)
print()
if not survivors:
    print("NO SPECTRUM SURVIVES, WITHOUT USING THE CORRIDOR THEOREM.")
    print("=> no length-37 obstruction over C_7^3 exists => D_3(C_7^3) = 36.")
