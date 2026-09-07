"""Attack hypothesis (Z) with the POINTED identity.

Let C be a counterexample: zero-sum over C_7^3, |C| = 28, z(C) = 2, no atom of length <= 12.
Then its proper zero-sum lengths lie in {13,14,15}.  Fix an index i and apply the identity
with h = x_i * e_d(x_{-i}), multilinear of degree d+1 <= |C| - D = 9, so d <= 8:

    sum_{I ∋ i, sigma(I)=0} (-1)^{|I|} C(|I|-1, d)  ==  0   (mod 7).

The zero-sum sets containing i are the 13-, 14- and 15-sets through i (counts M13, M14, M15)
and C itself (length 28).  So for every d <= 8:

   -M13*C(12,d) + M14*C(13,d) - M15*C(14,d) + C(27,d)  ==  0  (mod 7).

Nine equations, three unknowns, per index i.
"""
from math import comb
p=7
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
    return [i for i in range(m) if not any(A[i][:nv]) and A[i][nv]%p]

print("Branch N_13 = 0 (all proper zero-sums have length 14): unknown M14 only")
rows=[]
for d in range(0,9):
    rows.append([comb(13,d)%p, (-comb(27,d))%p])
    print(f"   d={d}: C(13,{d}) = {comb(13,d)%p}  M14  =  {(-comb(27,d))%p}")
bad=solve(rows,1)
print("   -> INFEASIBLE" if bad else "   -> feasible")
print()
print("Full branch (lengths 13,14,15 all allowed): unknowns M13, M14, M15")
rows=[]
for d in range(0,9):
    rows.append([(-comb(12,d))%p, comb(13,d)%p, (-comb(14,d))%p, (-comb(27,d))%p])
bad=solve(rows,3)
print("   9 equations, 3 unknowns ->", "INFEASIBLE" if bad else "feasible")
if not bad:
    sols=[(a,b,c) for a in range(p) for b in range(p) for c in range(p)
          if all((r[0]*a+r[1]*b+r[2]*c-r[3])%p==0 for r in rows)]
    print("   solutions (M13,M14,M15) mod 7:", sols)
