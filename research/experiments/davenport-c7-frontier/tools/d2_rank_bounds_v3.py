"""Push the digit/congruence method to other ranks.

For G = C_p^r, D = r(p-1)+1.  If T is zero-sum of length N with packing number <= 2, then
every proper nonempty zero-sum U of T has both U and T U^{-1} an atom, so
    N - D <= |U| <= D.
Feed that window into the polynomial-method congruences and test consistency mod p.
The least N whose system is INCONSISTENT gives  D_2(C_p^r) <= N - 1.
Controls: r=2 (published D_2 = 3p-1) and r=3 (published/this packet, D_2 = (9p-5)/2).
"""
import sys
from math import comb

def consistent(p, r, N):
    D = r*(p-1)+1
    lo, hi = max(1, N-D), min(D, N-1)
    allowed = [0] + list(range(lo, hi+1)) + [N] if lo <= hi else [0, N]
    idx = {}
    for l in allowed:
        if 0 < l < N: idx.setdefault(min(l, N-l), len(idx))
    rows = []
    for d in range(N - D + 1):
        coef = {}; rhs = 0
        for l in allowed:
            c = ((-1)**l) * comb(l, d)
            if l in (0, N): rhs -= c
            else:
                k = idx[min(l, N-l)]; coef[k] = coef.get(k, 0) + c
        rows.append((coef, rhs))
    n = len(idx); m = len(rows)
    A = [[0]*(n+1) for _ in rows]
    for i,(coef,rhs) in enumerate(rows):
        for k,c in coef.items(): A[i][k] = c % p
        A[i][n] = rhs % p
    rr = 0
    for c in range(n):
        piv = next((i for i in range(rr, m) if A[i][c]), None)
        if piv is None: continue
        A[rr], A[piv] = A[piv], A[rr]
        inv = pow(A[rr][c], p-2, p); A[rr] = [(x*inv) % p for x in A[rr]]
        for i in range(m):
            if i != rr and A[i][c]:
                f = A[i][c]; A[i] = [(A[i][j]-f*A[rr][j]) % p for j in range(n+1)]
        rr += 1
        if rr == m: break
    for i in range(m):
        if not any(A[i][:n]) and A[i][n]: return False
    return True

def threshold(p, r, cap=None):
    D = r*(p-1)+1
    cap = cap or 3*D
    for N in range(D+1, cap):
        if not consistent(p, r, N):
            return N
    return None

if __name__ == '__main__':
    print("rank r, prime p:  N* = least N with an inconsistent system  ->  D_2(C_p^r) <= N*-1")
    print(f"{'r':>2} {'p':>4} {'D':>5} {'N*':>5} {'D_2 <=':>7}   known / comparison")
    known = {2: lambda p: 3*p-1, 3: lambda p: (9*p-5)//2}
    for r in (2,3,4,5,6):
        for p in (5,7,11,13):
            D = r*(p-1)+1
            N = threshold(p, r)
            if N is None: print(f"{r:>2} {p:>4} {D:>5} {'-':>5} {'-':>7}   no inconsistency found"); continue
            ub = N-1
            k = f"D_2 = {known[r](p)}" if r in known else ""
            mark = ""
            if r in known:
                mark = "  MATCHES" if ub == known[r](p) else f"  (gap {ub-known[r](p)})"
            print(f"{r:>2} {p:>4} {D:>5} {N:>5} {ub:>7}   {k}{mark}")
