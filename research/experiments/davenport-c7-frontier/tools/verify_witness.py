"""Independent verifier: given p, support points and multiplicities, and a claimed packing number k,
check (a) there exist k pairwise disjoint nonempty zero-sum sub-multisets, and (b) no k+1 exist.
Method: enumerate all zero-sum sub-vectors; a t-packing exists iff some zero-sum b has (m-b) admitting a (t-1)-packing (memoised)."""
import sys
from functools import lru_cache
from itertools import product

def run(p, pts, m, k):
    n=len(pts)
    def zs(b): return all(sum(b[i]*pts[i][j] for i in range(n))%p==0 for j in range(3))
    zero=[b for b in product(*[range(x+1) for x in m]) if any(b) and zs(b)]
    # atoms suffice for packings
    def leq(a,b): return all(a[i]<=b[i] for i in range(n))
    atoms=[b for b in zero if not any(c!=b and leq(c,b) for c in zero)]
    @lru_cache(maxsize=None)
    def pack(r, t):
        if t==0: return True
        for b in atoms:
            if leq(b, r) and pack(tuple(r[i]-b[i] for i in range(n)), t-1): return True
        return False
    ok_k = pack(tuple(m), k); ok_k1 = pack(tuple(m), k+1)
    return len(zero), len(atoms), ok_k, ok_k1

if __name__=='__main__':
    p=int(sys.argv[1]); k=int(sys.argv[2]); toks=sys.argv[3:]
    pts=[]; m=[]
    for t in toks:
        v,mu=t.split('^'); pts.append(tuple(int(x) for x in v.strip('()').split(','))); m.append(int(mu))
    nz,na,a,b=run(p,pts,m,k)
    print(f"p={p} len={sum(m)} zero-sum subvectors={nz} atoms={na} has_{k}_packing={a} has_{k+1}_packing={b}")
    assert a and not b, "packing number is not exactly k"
    print("PASS: packing number exactly", k)
