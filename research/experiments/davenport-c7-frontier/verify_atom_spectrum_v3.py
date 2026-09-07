#!/usr/bin/env python3
"""Checker for ATOM_SPECTRUM_CONGRUENCE_V3.md.

1. Brute-force the counting identity over C_3^3 (all 2^15 index subsets).
2. Validate Lemma 2.1 and the congruence on a REAL packing-number-3 object over C_5^3.
3. Recompute the p=7 forced atom-length sets and assert {13,14} is among them.
4. Check that no p=5 forced set is violated by the real object.
"""
import random
from math import comb
from itertools import product, combinations
from functools import lru_cache


def brute_identity(p, r, T):
    D = r * (p - 1) + 1
    n = len(T)
    N = [0] * (n + 1)
    for mask in range(1 << n):
        s = [0] * r; c = 0; mm = mask; i = 0
        while mm:
            if mm & 1:
                c += 1
                for j in range(r): s[j] = (s[j] + T[i][j]) % p
            mm >>= 1; i += 1
        if not any(s): N[c] += 1
    return [(d, sum(((-1) ** l) * N[l] * comb(l, d) for l in range(n + 1)) % p)
            for d in range(0, n - D + 1)]


def packing_data(p, r, pts, mult):
    def is_zs(b): return all(sum(b[i]*pts[i][j] for i in range(len(pts))) % p == 0 for j in range(r))
    box = list(product(*[range(x + 1) for x in mult]))
    zero = [b for b in box if any(b) and is_zs(b)]
    leq = lambda x, y: all(x[i] <= y[i] for i in range(len(pts)))
    atoms = [b for b in zero if not any(c != b and leq(c, b) for c in zero)]
    @lru_cache(maxsize=None)
    def pa(rm, t):
        if t == 0: return True
        return any(leq(b, rm) and pa(tuple(rm[i] - b[i] for i in range(len(pts))), t - 1) for b in atoms)
    pk = 0
    while pk < 6 and pa(tuple(mult), pk + 1): pk += 1
    return zero, atoms, pk


def feasible(p, NT, D, lens, zeroset, overlap_lens):
    cols = []
    for l in lens:
        if l in zeroset: continue
        cols.append(lambda d, l=l: (((-1) ** l) * (comb(l, d) - comb(NT - l, d))) % p)
    for l in overlap_lens:
        if l in zeroset: continue
        cols.append(lambda d, l=l: (-((-1) ** l) * comb(l, d)) % p)
    rows = [[f(d) for f in cols] + [(-(comb(0, d) - comb(NT, d))) % p] for d in range(0, NT - D + 1)]
    nv = len(cols); A = [r[:] for r in rows]; m = len(A); piv = 0
    for c in range(nv):
        r = next((i for i in range(piv, m) if A[i][c] % p), None)
        if r is None: continue
        A[piv], A[r] = A[r], A[piv]
        inv = pow(A[piv][c], p - 2, p); A[piv] = [(x * inv) % p for x in A[piv]]
        for i in range(m):
            if i != piv and A[i][c] % p:
                f = A[i][c]; A[i] = [(A[i][j] - f * A[piv][j]) % p for j in range(nv + 1)]
        piv += 1
    return not any(not any(A[i][:nv]) and A[i][nv] % p for i in range(m))


def main():
    # 1
    random.seed(7)
    for _ in range(3):
        T = [tuple(random.randrange(3) for _ in range(3)) for _ in range(14)]
        T.append(tuple((-sum(t[j] for t in T)) % 3 for j in range(3)))
        bad = [x for x in brute_identity(3, 3, T) if x[1]]
        assert not bad, bad
    print("1. counting identity: brute-force verified over C_3^3")

    # 2
    p, r = 5, 3
    Q = [(1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,0,1),(0,1,1)]
    a, hi, lo = p-1, (p+1)//2, (p-1)//2
    pts = list(Q); mult = [2*p-1, a, a, hi, lo, lo]
    sig = tuple(sum(mult[i]*pts[i][j] for i in range(len(pts))) % p for j in range(3))
    comp = tuple((-x) % p for x in sig)
    if comp in pts: mult[pts.index(comp)] += 1
    else: pts.append(comp); mult.append(1)
    NT = sum(mult); D = r*(p-1)+1
    assert NT == 25
    zero, atoms, pk = packing_data(p, r, pts, mult)
    assert pk == 3, pk
    full = tuple(mult)
    cpl = lambda b: tuple(full[i]-b[i] for i in range(len(pts)))
    aset = set(atoms)
    predicted = {tuple([0]*len(pts)), full} | aset | {cpl(A) for A in aset}
    actual = set(zero) | {tuple([0]*len(pts))}
    assert predicted == actual, (len(predicted), len(actual))
    weight = lambda b: eval("1") if False else __import__("math").prod(comb(mult[i], b[i]) for i in range(len(pts)))
    W = {}; X = {}
    over = aset & {cpl(A) for A in aset}
    for A in atoms: W[sum(A)] = (W.get(sum(A), 0) + weight(A)) % p
    for A in over:  X[sum(A)] = (X.get(sum(A), 0) + weight(A)) % p
    for d in range(0, NT - D + 1):
        v = comb(0, d) - comb(NT, d)
        for L, val in W.items(): v += ((-1)**L)*val*(comb(L, d) - comb(NT-L, d))
        for L, val in X.items(): v -= ((-1)**L)*val*comb(L, d)
        assert v % p == 0, (d, v % p)
    print(f"2. Lemma 2.1 + congruence verified on a real z=3 object over C_5^3 "
          f"({len(predicted)} zero-sum multisets, atom lengths {sorted(W)})")

    # 3
    p, NT, D = 7, 37, 19
    lens = list(range(8, 20))
    assert feasible(p, NT, D, lens, set(), (18, 19)), "unrestricted p=7 system should be consistent"
    forced = []
    for size in (1, 2):
        for S in combinations(lens, size):
            if any(set(m) <= set(S) for m in forced): continue
            if not feasible(p, NT, D, lens, set(S), (18, 19)): forced.append(S)
    assert (13, 14) in forced, forced
    print(f"3. p=7: unrestricted system consistent; {len(forced)} minimal forced pairs, "
          f"including {{13,14}} -> every obstruction has an atom of length 13 or 14")

    # 4
    p5, NT5, D5 = 5, 25, 13
    lens5 = list(range(NT5 - 20, D5 + 1))
    forced5 = []
    for size in (1, 2):
        for S in combinations(lens5, size):
            if any(set(m) <= set(S) for m in forced5): continue
            if not feasible(p5, NT5, D5, lens5, set(S), tuple(l for l in lens5 if 2*l >= NT5)):
                forced5.append(S)
    actual5 = set(W)
    bad = [S for S in forced5 if not (set(S) & actual5)]
    assert not bad, bad
    print(f"4. p=5: {len(forced5)} forced sets, none violated by the real object")
    print("PASS: atom-spectrum congruence record verified")


if __name__ == "__main__":
    main()
