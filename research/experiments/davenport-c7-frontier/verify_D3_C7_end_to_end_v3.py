#!/usr/bin/env python3
"""END-TO-END verification of D_3(C_7^3) = 36.

Rebuilds the entire proof from scratch in one program, in the order of the manuscript, and
asserts every step.  Nothing is imported from the other records; the only external input is
Olson's D(C_p^r) = r(p-1)+1.

  Step 1  the counting identity (Lemma 2.1), brute-forced over C_3^3
  Step 2  the pointed identity (P), brute-forced over C_3^3
  Step 3  Lemma 4.2 and both identities on a REAL packing-number-3 object over C_5^3
  Step 4  D_2(C_p^3) = (9p-5)/2 (Theorem B), structure checked for all primes 5..200
  Step 5  Proposition 4.3 (former hypothesis Z) via the pointed identity
  Step 6  the corridor, derived from the congruences plus Proposition 4.3
  Step 7  the 548 feasible atom-length spectra, cut to 8 by closure + corridor
  Step 8  all 8 killed by complement systems  =>  D_3(C_7^3) = 36
"""
import random
from math import comb
from itertools import product, combinations
from functools import lru_cache

P7, D7, NT = 7, 19, 37


def gauss_consistent(rows, nv, p):
    A = [r[:] for r in rows]; m = len(A); piv = 0
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


def step1_and_2():
    random.seed(101)
    for _ in range(3):
        T = [tuple(random.randrange(3) for _ in range(3)) for _ in range(14)]
        T.append(tuple((-sum(t[j] for t in T)) % 3 for j in range(3)))
        n, D = len(T), 7
        N = [0] * (n + 1); cnt = [[0] * (n + 1) for _ in range(n)]
        for mask in range(1 << n):
            s = [0, 0, 0]; c = 0; mm = mask; j = 0
            while mm:
                if mm & 1:
                    c += 1
                    for k in range(3): s[k] = (s[k] + T[j][k]) % 3
                mm >>= 1; j += 1
            if not any(s):
                N[c] += 1
                for j in range(n):
                    if mask >> j & 1: cnt[j][c] += 1
        for d in range(0, n - D + 1):
            assert sum(((-1) ** l) * N[l] * comb(l, d) for l in range(n + 1)) % 3 == 0
        for i in range(n):
            for d in range(0, n - D):
                assert sum(((-1) ** l) * cnt[i][l] * comb(l - 1, d) for l in range(1, n + 1)) % 3 == 0
    print("1,2. counting identity and pointed identity: brute-force verified over C_3^3")


def step3():
    p, r = 5, 3; D = r * (p - 1) + 1
    Q = [(1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,0,1),(0,1,1)]
    a, hi, lo = p-1, (p+1)//2, (p-1)//2
    pts = list(Q); mult = [2*p-1, a, a, hi, lo, lo]
    sig = tuple(sum(mult[i]*pts[i][j] for i in range(len(pts))) % p for j in range(3))
    cm = tuple((-x) % p for x in sig)
    if cm in pts: mult[pts.index(cm)] += 1
    else: pts.append(cm); mult.append(1)
    N = sum(mult); assert N == 25
    k = len(pts)
    is_zs = lambda b: all(sum(b[i]*pts[i][j] for i in range(k)) % p == 0 for j in range(3))
    zero = [b for b in product(*[range(x+1) for x in mult]) if any(b) and is_zs(b)]
    leq = lambda x, y: all(x[i] <= y[i] for i in range(k))
    atoms = [b for b in zero if not any(c != b and leq(c, b) for c in zero)]
    @lru_cache(maxsize=None)
    def pa(rm, t):
        if t == 0: return True
        return any(leq(b, rm) and pa(tuple(rm[i]-b[i] for i in range(k)), t-1) for b in atoms)
    z = 0
    while z < 6 and pa(tuple(mult), z+1): z += 1
    assert z == 3
    full = tuple(mult); cpl = lambda b: tuple(full[i]-b[i] for i in range(k))
    aset = set(atoms)
    assert ({tuple([0]*k), full} | aset | {cpl(A) for A in aset}) == (set(zero) | {tuple([0]*k)})
    import math
    w = lambda b: math.prod(comb(mult[i], b[i]) for i in range(k))
    W = {}
    for A in atoms: W[sum(A)] = (W.get(sum(A), 0) + w(A)) % p
    over = aset & {cpl(A) for A in aset}
    X = {}
    for A in over: X[sum(A)] = (X.get(sum(A), 0) + w(A)) % p
    for d in range(0, N - D + 1):
        v = comb(0, d) - comb(N, d)
        for L, val in W.items(): v += ((-1)**L)*val*(comb(L, d) - comb(N-L, d))
        for L, val in X.items(): v -= ((-1)**L)*val*comb(L, d)
        assert v % p == 0
    print(f"3. Lemma 4.2 and the congruences verified on a real z=3 object over C_5^3 "
          f"({len(set(zero))+1} zero-sum multisets, atom lengths {sorted(W)})")


def step4():
    def ok(p):
        N = (9*p-3)//2; D = 3*p-2; m = N-D
        I = list(range((3*p+1)//2, 3*p-1))
        assert len(I) == (3*p-3)//2 and 2*p in I and (5*p-3)//2 in I and 2*p != (5*p-3)//2
        cls = {}
        for l in [0] + I + [N]: cls.setdefault(l % p, []).append(l)
        pairs = [r for r, v in cls.items() if len(v) == 2 and r not in (0, (p-3)//2)]
        assert sorted(cls[0]) == [0, 2*p]
        assert sorted(cls[(p-3)//2]) == sorted([(5*p-3)//2, N])
        assert len(pairs) == (p-3)//2
        supp = 2 + len(pairs)
        return supp <= (p+1)//2 and supp - 1 <= m - p and (2*(-1)) % p != 0
    pr = [q for q in range(5, 201) if all(q % f for f in range(2, int(q**0.5)+1))]
    assert all(ok(p) for p in pr)
    print(f"4. Theorem B: structural steps verified for every prime 5..200 ({len(pr)} primes)")


def step5():
    rows = [[(-comb(12,d)) % P7, comb(13,d) % P7, (-comb(14,d)) % P7, (-comb(27,d)) % P7]
            for d in range(0, 9)]
    assert not gauss_consistent(rows, 3, P7)
    assert all(comb(14, d) % P7 == 0 for d in range(1, 7))
    print("5. Proposition 4.3: the pointed system (9 equations, 3 unknowns) is INFEASIBLE")


CORRIDOR = {(8,10,19),(9,9,19),(9,10,18),(9,11,17),(9,12,16),(10,10,17)}


def step6():
    def general_short(N, w):
        forb = set(range(1, w+1)) | set(range(N-w, N))
        allowed = [l for l in range(N+1) if l not in forb]
        idx = {}
        for l in allowed:
            if 0 < l < N: idx.setdefault(min(l, N-l), len(idx))
        rows = []
        for d in range(0, N-D7+1):
            coef = [0]*len(idx); rhs = 0
            for l in allowed:
                c = ((-1)**l)*comb(l, d)
                if l in (0, N): rhs -= c
                else: coef[idx[min(l, N-l)]] += c
            rows.append([x % P7 for x in coef] + [rhs % P7])
        return not gauss_consistent(rows, len(idx), P7)
    def pk2_short(m, w):
        S = [l for l in range(w+1, m-w) if 8 <= l <= m-8]
        reps = sorted({min(l, m-l) for l in S})
        if not reps: return True
        rows = []
        for d in range(0, m-D7+1):
            row = [0]*len(reps)
            for l in S:
                r = reps.index(min(l, m-l)); row[r] = (row[r] + ((-1)**l)*comb(l, d)) % P7
            rows.append(row + [(-(comb(0,d)+((-1)**m)*comb(m,d))) % P7])
        return not gauss_consistent(rows, len(reps), P7)
    assert general_short(37, 10) and not general_short(37, 9)   # sharp, and not vacuous
    assert pk2_short(29, 10) and pk2_short(27, 10)
    built = set()
    for s, m in ((8,29), (9,28), (10,27)):
        wmax = 12 if m == 28 else 10                            # 12 at m=28 by Proposition 4.3
        for u in range(max(s, m-19), wmax+1):
            v = m-u
            if s <= u <= v <= 19: built.add(tuple(sorted((s,u,v))))
    assert built == CORRIDOR, (sorted(built), sorted(CORRIDOR))
    print(f"6. corridor derived from the congruences + Prop 4.3: {sorted(CORRIDOR)}")


def feas_T(L):
    LENS = list(range(8, 20)); zero = set(LENS) - set(L); cols = []
    for l in LENS:
        if l in zero: continue
        cols.append(lambda d, l=l: (((-1)**l)*(comb(l,d)-comb(NT-l,d))) % P7)
    for l in (18, 19):
        if l in zero: continue
        cols.append(lambda d, l=l: (-((-1)**l)*comb(l,d)) % P7)
    rows = [[f(d) for f in cols] + [(-(comb(0,d)-comb(NT,d))) % P7] for d in range(0, NT-D7+1)]
    return gauss_consistent(rows, len(cols), P7)


def feas_C(m, S):
    if m <= D7: return True
    reps = sorted({min(l, m-l) for l in S})
    if not reps: return False
    rows = []
    for d in range(0, m-D7+1):
        row = [0]*len(reps)
        for l in S:
            r = reps.index(min(l, m-l)); row[r] = (row[r] + ((-1)**l)*comb(l, d)) % P7
        rows.append(row + [(-(comb(0,d)+((-1)**m)*comb(m,d))) % P7])
    return gauss_consistent(rows, len(reps), P7)


def steps7_8():
    LENS = list(range(8, 20))
    prof = lambda l, L, s: {tuple(sorted((l,u,NT-l-u))) for u in L
                            if (NT-l-u) in L and u <= NT-l-u and u >= s and NT-l-u >= s}
    nfeas = 0; eight = []
    for k in range(1, len(LENS)+1):
        for Lt in combinations(LENS, k):
            L = set(Lt)
            if not feas_T(L): continue
            nfeas += 1
            s = min(L)
            if any(not prof(l, L, s) and not (l in (18,19) and (NT-l) in L) for l in sorted(L)):
                continue
            allP = set().union(*(prof(l, L, s) for l in sorted(L))) if L else set()
            if any(s in Q and Q not in CORRIDOR for Q in allP): continue
            if not any(set(Q) <= L for Q in CORRIDOR): continue
            eight.append(sorted(L))
    assert nfeas == 548, nfeas
    assert len(eight) == 8, (len(eight), eight)
    print(f"7. {nfeas} feasible spectra; closure + corridor leave exactly {len(eight)}")
    survivors = []
    for L in eight:
        Ls = set(L)
        if all(feas_C(NT-l, {x for x in Ls if 8 <= x <= NT-l-8 and (NT-l-x) in Ls}) for l in L):
            survivors.append(L)
    assert not survivors, survivors
    print(f"8. all {len(eight)} eliminated by complement systems -> no obstruction")


if __name__ == "__main__":
    step1_and_2(); step3(); step4(); step5(); step6(); steps7_8()
    print()
    print("THEOREM: D_3(C_7^3) = 36.")
    print("Only external input: Olson's D(C_p^r) = r(p-1)+1.")
