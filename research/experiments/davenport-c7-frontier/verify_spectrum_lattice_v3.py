"""Complete characterisation of the possible atom-length SETS of a D_3(C_7^3) obstruction.

For every subset L of {8,...,19}, test the atom-spectrum system with W_l = 0 for l outside L.
Infeasible means: no obstruction has all its atom lengths inside L.  The MAXIMAL infeasible
sets, equivalently the MINIMAL feasible ones, characterise what is possible from counting.
Then intersect with the two corridors: the atom-length set must contain some P1 in corridor 1
and some P2 in corridor 2.
"""
from math import comb
from itertools import combinations
p, NT, D = 7, 37, 19
LENS=list(range(8,20))
C1=[(8,10,19),(9,9,19),(9,10,18),(9,11,17),(9,12,16),(10,10,17)]
C2=[(9,13,15),(9,14,14),(10,13,14),(11,12,14),(11,13,13),(12,12,13)]

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

feas=[]
for k in range(0,len(LENS)+1):
    for L in combinations(LENS,k):
        if feasible(L): feas.append(set(L))
minimal=[L for L in feas if not any(M<L for M in feas)]
print(f"feasible atom-length sets: {len(feas)} of {2**len(LENS)}")
print(f"minimal feasible sets ({len(minimal)}):")
for L in sorted(minimal,key=lambda x:(len(x),sorted(x))): print("   ",sorted(L))
print()
ok=[]
for L in feas:
    if any(set(P1)<=L for P1 in C1) and any(set(P2)<=L for P2 in C2):
        ok.append(L)
mins=[L for L in ok if not any(M<L for M in ok)]
print(f"feasible AND containing a corridor-1 and a corridor-2 profile: {len(ok)}")
print(f"minimal such sets ({len(mins)}):")
for L in sorted(mins,key=lambda x:(len(x),sorted(x))):
    p1=[P for P in C1 if set(P)<=L]; p2=[P for P in C2 if set(P)<=L]
    print(f"    {sorted(L)}   P1 in {p1}, P2 in {p2}")
