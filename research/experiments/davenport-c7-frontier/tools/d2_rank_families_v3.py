"""General-rank lower-bound construction for D_2(C_p^r).

Take e_1^{p-1} ... e_r^{p-1} and add vectors v (0/1 supports) with multiplicities m_v, subject to
  (i)  the supports {supp(v) : m_v > 0} are pairwise INTERSECTING, and
  (ii) every coordinate sum is <= 2p-1, i.e. sum_{v ∋ i} m_v <= p for every i.
Claim: the resulting sequence has packing number 1, so D_2(C_p^r) >= r(p-1) + sum m_v + 1.

Reason: a block using no added vector is a product of e_i's with each exponent = 0 mod p, needing
p copies of some e_i, but only p-1 are present.  So each block's coordinate set contains some
supp(v); (ii) makes each coordinate usable by at most one block, so two disjoint blocks would need
disjoint coordinate sets, hence disjoint supports, contradicting (i).
"""
import sys
from functools import lru_cache
from itertools import product, combinations

def packing(p, r, pts, m, cutoff=4):
    k = len(pts)
    def zs(b): return all(sum(b[i]*pts[i][j] for i in range(k)) % p == 0 for j in range(r))
    zero = [b for b in product(*[range(x+1) for x in m]) if any(b) and zs(b)]
    leq = lambda a,b: all(a[i] <= b[i] for i in range(k))
    atoms = [b for b in zero if not any(c != b and leq(c,b) for c in zero)]
    @lru_cache(maxsize=None)
    def pa(rem, t):
        if t == 0: return True
        return any(leq(b, rem) and pa(tuple(rem[i]-b[i] for i in range(k)), t-1) for b in atoms)
    j = 0
    while j < cutoff and pa(tuple(m), j+1): j += 1
    return j

def build(p, r, sets, mult):
    pts = [tuple(1 if i == j else 0 for j in range(r)) for i in range(r)]
    m = [p-1]*r
    for S, c in zip(sets, mult):
        pts.append(tuple(1 if j in S else 0 for j in range(r))); m.append(c)
    return pts, m

def intersecting(sets):
    return all(set(a) & set(b) for a, b in combinations(sets, 2))

def check(p, r, sets, mult, label):
    assert intersecting(sets), "supports not intersecting"
    pts, m = build(p, r, sets, mult)
    for i in range(r):
        cs = sum(m[j] for j in range(len(m)) if pts[j][i])
        assert cs <= 2*p-1, (i, cs)
    pk = packing(p, r, pts, m)
    print(f"  p={p} r={r} {label:34s} len={sum(m):4d}  added={sum(mult):3d}  pk={pk}  {'OK' if pk==1 else 'FAIL'}")
    return pk == 1, sum(m)

if __name__ == '__main__':
    print("Intersecting-family lower bound, verified by exact packing computation:")
    for p in (5, 7):
        h, l = (p+1)//2, (p-1)//2
        check(p, 2, [(0,1)], [p], "star K_2 (nu*=1)")
        check(p, 3, [(0,1),(0,2),(1,2)], [h,l,l], "triangle (nu*=3/2)")
        check(p, 4, [(0,1),(0,2),(1,2)], [h,l,l], "triangle inside r=4")
        check(p, 4, [(0,1,2),(0,1,3),(0,2,3),(1,2,3)], [ (p)//3+1, p//3, p//3, p//3 ], "all 3-sets of [4]")
        check(p, 5, [(0,1),(0,2),(1,2)], [h,l,l], "triangle inside r=5")
    print()
    print("Fano plane (r=7, 3-uniform, nu* = 7/3), p=7:")
    fano = [(0,1,2),(0,3,4),(0,5,6),(1,3,5),(1,4,6),(2,3,6),(2,4,5)]
    check(7, 7, fano, [2]*7, "Fano, m=2 each")
    check(7, 7, fano, [3]+[2]*6, "Fano, one line at 3")
