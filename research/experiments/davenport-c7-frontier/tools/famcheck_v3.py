"""Exact packing number of the conjectured extremal families S_k(n) over C_n^3, any odd n."""
import sys
from functools import lru_cache
from itertools import product

def pk(n, pts, m):
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
    while pa(tuple(m), j+1): j+=1
    return j, len(atoms)

Q=[(1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,0,1),(0,1,1),(1,1,1)]
def S2(n): return Q[:6], [n-1,n-1,n-1,(n+1)//2,(n-1)//2,(n-1)//2]
def S3(n): return Q,      [n-1,n-1,n-1,n-1,(n+1)//2,(n-1)//2,(n+1)//2]
def S4(n): return Q+[(1,1,2)], [n-1,n-1,n-1,n-1,(n+1)//2,(n-1)//2,n-1,(n+3)//2]

if __name__=='__main__':
    for n in [int(x) for x in sys.argv[1:] if x.isdigit()]:
        for name,(pts,m),want,L in (("S_2",S2(n),1,(9*n-7)//2), ("S_3",S3(n),2,(11*n-7)//2), ("S_4",S4(n),3,(13*n-7)//2)):
            got,na=pk(n,pts,m)
            ok = (got==want and sum(m)==L)
            print(f"n={n:3d} {name}: len={sum(m):3d} (target {L:3d})  pk={got} (target {want})  atoms={na}  {'OK' if ok else 'MISMATCH'}")
            assert ok, (n,name)
    print("PASS")
