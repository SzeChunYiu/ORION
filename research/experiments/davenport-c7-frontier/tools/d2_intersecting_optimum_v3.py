"""Exact value of M(r,p) = max { sum_A m_A : supp(m) intersecting, sum_{A ∋ i} m_A <= p }.

For r <= 5 we enumerate every maximal intersecting family (choose one of each complementary
pair {A, comp A}, keep the intersecting ones), then solve the small integer program on each by
branch and bound.  M(r,p) is the max over families.
"""
import sys
from itertools import combinations

def masks(r): return [1 << i for i in range(r)]

def maximal_families(r):
    full = (1 << r) - 1
    subsets = list(range(1, 1 << r))
    pairs = []
    seen = set()
    for A in subsets:
        B = full ^ A
        if B == 0:            # A = full, its complement is empty: full is always allowed
            continue
        key = frozenset((A, B))
        if key in seen: continue
        seen.add(key); pairs.append((A, B))
    out = []
    for bits in range(1 << len(pairs)):
        fam = [full]
        ok = True
        for k, (A, B) in enumerate(pairs):
            fam.append(A if (bits >> k) & 1 else B)
        for a, b in combinations(fam, 2):
            if a & b == 0: ok = False; break
        if ok: out.append(tuple(sorted(fam)))
    return sorted(set(out))

def solve_ip(fam, r, p):
    """max sum m_A s.t. for each coordinate i, sum_{A ∋ i} m_A <= p."""
    fam = list(fam)
    n = len(fam)
    best = [0]
    cap = [p]*r
    def bnd(k, cur, cap):
        # optimistic: each remaining set can take min over its coordinates of remaining capacity
        extra = 0
        for j in range(k, n):
            extra += min(cap[i] for i in range(r) if fam[j] >> i & 1)
        return cur + extra
    def rec(k, cur, cap):
        if cur > best[0]: best[0] = cur
        if k == n: return
        if bnd(k, cur, cap) <= best[0]: return
        hi = min(cap[i] for i in range(r) if fam[k] >> i & 1)
        for m in range(hi, -1, -1):
            nc = cap[:]
            for i in range(r):
                if fam[k] >> i & 1: nc[i] -= m
            rec(k+1, cur+m, nc)
    rec(0, 0, cap)
    return best[0]

if __name__ == '__main__':
    print(f"{'r':>2} {'p':>4} {'M(r,p)':>8} {'triangle':>9} {'length = r(p-1)+M':>18} {'D_2 >=':>8} {'UB (Thm 1)':>11}")
    for r in range(2, 6):
        fams = maximal_families(r)
        for p in (5, 7, 11, 13):
            M = max(solve_ip(f, r, p) for f in fams)
            tri = (3*p-1)//2 if r >= 3 else p
            D = r*(p-1)+1
            ub = (3*D+1)//2 if r % 2 else (3*D+r-1)//2
            L = r*(p-1) + M
            print(f"{r:>2} {p:>4} {M:>8} {tri:>9} {L:>18} {L+1:>8} {ub:>11}"
                  + ("   TIGHT" if L+1 == ub else f"   gap {ub-(L+1)}"))
        print(f"   ({len(fams)} maximal intersecting families on [{r}])")
