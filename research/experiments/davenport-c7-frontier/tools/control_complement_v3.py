"""NEGATIVE CONTROL: run the complement-system test against the REAL p=5 object.

That object exists (packing number 3, length 25, atom lengths {5,7,8,9,10,11,12,13}), so
every complement system must come out FEASIBLE.  If the machinery kills it, the machinery is
wrong and the p=7 conclusion is void.
"""
from math import comb
from itertools import product
from functools import lru_cache
p, r = 5, 3
D = r*(p-1)+1
Q=[(1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,0,1),(0,1,1)]
a,hi,lo=p-1,(p+1)//2,(p-1)//2
pts=list(Q); mult=[2*p-1,a,a,hi,lo,lo]
sig=tuple(sum(mult[i]*pts[i][j] for i in range(len(pts)))%p for j in range(3))
cmp_=tuple((-x)%p for x in sig)
if cmp_ in pts: mult[pts.index(cmp_)]+=1
else: pts.append(cmp_); mult.append(1)
NT=sum(mult)
def is_zs(b): return all(sum(b[i]*pts[i][j] for i in range(len(pts)))%p==0 for j in range(3))
zero=[b for b in product(*[range(x+1) for x in mult]) if any(b) and is_zs(b)]
leq=lambda x,y: all(x[i]<=y[i] for i in range(len(pts)))
atoms=[b for b in zero if not any(c!=b and leq(c,b) for c in zero)]
L=sorted({sum(A) for A in atoms})
amin=min(L)
print(f"real object: |T|={NT}, D={D}, atom lengths L={L}")

def feasible_complement(m,S,p,D):
    if m<=D: return True
    reps=sorted({min(l,m-l) for l in S})
    if not reps: return False
    rows=[]
    for d in range(0,m-D+1):
        row=[0]*len(reps)
        for l in S:
            rr=reps.index(min(l,m-l))
            row[rr]=(row[rr]+((-1)**l)*comb(l,d))%p
        rows.append(row+[(-(comb(0,d)+((-1)**m)*comb(m,d)))%p])
    nv=len(reps); A=[x[:] for x in rows]; mm=len(A); piv=0
    for c in range(nv):
        rr=next((i for i in range(piv,mm) if A[i][c]%p),None)
        if rr is None: continue
        A[piv],A[rr]=A[rr],A[piv]
        inv=pow(A[piv][c],p-2,p); A[piv]=[(x*inv)%p for x in A[piv]]
        for i in range(mm):
            if i!=piv and A[i][c]%p:
                f=A[i][c]; A[i]=[(A[i][j]-f*A[piv][j])%p for j in range(nv+1)]
        piv+=1
    return not any(not any(A[i][:nv]) and A[i][nv]%p for i in range(mm))

bad=[]
for l in L:
    m=NT-l
    S={x for x in L if amin<=x<=m-amin and (m-x) in L}
    ok=feasible_complement(m,S,p,D)
    print(f"   atom length {l:2d}: |C|={m:2d}, admissible {sorted(S)}, {'feasible' if ok else 'KILLED'}")
    if not ok: bad.append(l)
print()
if bad:
    print(f"*** MACHINERY IS WRONG: it kills the real object at atom lengths {bad} ***")
else:
    print("CONTROL PASSED: the real p=5 object survives every complement system.")
