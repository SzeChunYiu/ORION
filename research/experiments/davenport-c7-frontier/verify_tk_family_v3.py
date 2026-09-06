"""T_k(n) = e1^{(k-1)n-1} e2^{n-1} e3^{n-1} e12^{(n+1)/2} e13^{(n-1)/2} e23^{(n-1)/2}
Claim: |T_k| = ((2k+5)n-7)/2 and pk(T_k) = k-1, for every odd n and k >= 2."""
import sys
from functools import lru_cache
from itertools import product
P=[(1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,0,1),(0,1,1)]
def pk(n,pts,m,cutoff=12):
    k=len(pts)
    def zs(b): return all(sum(b[i]*pts[i][j] for i in range(k))%n==0 for j in range(3))
    zero=[b for b in product(*[range(x+1) for x in m]) if any(b) and zs(b)]
    leq=lambda a,b: all(a[i]<=b[i] for i in range(k))
    atoms=[b for b in zero if not any(c!=b and leq(c,b) for c in zero)]
    @lru_cache(maxsize=None)
    def pa(r,t):
        if t==0: return True
        return any(leq(b,r) and pa(tuple(r[i]-b[i] for i in range(k)),t-1) for b in atoms)
    j=0
    while j<cutoff and pa(tuple(m),j+1): j+=1
    return j,len(atoms)
def T(k,n): return P,[(k-1)*n-1,n-1,n-1,(n+1)//2,(n-1)//2,(n-1)//2]
if __name__=='__main__':
    for n in (3,5,7):
        for k in (2,3,4,5,6):
            pts,m=T(k,n); L=((2*k+5)*n-7)//2
            got,na=pk(n,pts,m)
            print(f"n={n} k={k}: len={sum(m):3d} (target {L:3d})  pk={got} (target {k-1})  atoms={na}  max_mult={max(m)}  {'OK' if (sum(m)==L and got==k-1) else 'MISMATCH'}")
            assert sum(m)==L and got==k-1, (n,k,sum(m),L,got)
    print("PASS: T_k(n) realises D_k(C_n^3) >= ((2k+5)n-5)/2")
