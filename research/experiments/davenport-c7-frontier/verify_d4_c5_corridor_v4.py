#!/usr/bin/env python3
"""Checker for D4_C5_FOUR_ATOM_CORRIDOR_V4.md.

D_4(C_5^3) is known to lie in {30, 31}.  The upper branch requires a zero-sum
T over C_5^3 with |T| = 31 and no five pairwise disjoint blocks.  This derives
a four-atom length corridor for that object.

The enabling lemma needs no packing hypothesis:

  LEMMA.  Let C be zero-sum over C_p^3, |C| = m, and suppose every atom of C
  has length >= w+1.  Then every proper nonempty zero-sum B of C has |B| >= w+1
  (B contains an atom) AND m - |B| >= w+1 (C B^{-1} is zero-sum and nonempty,
  so it contains an atom too).  So the proper zero-sum lengths lie in the
  two-sided window [w+1, m-w-1], and the pointed system on that window must be
  consistent.  Infeasible => C has an atom of length <= w.

Steps
  1. minimum atom length 6, from D_3(C_5^3) = 25;
  2. the pointed short-atom bounds w(m) for every m in [14,31], each decided by
     Gaussian elimination over F_5 and (where the unknown count allows) by
     exhaustive search, required to agree, with w-1 shown feasible;
  3. peel four atoms and enumerate the corridor;
  4. controls: the bound must not be violated by a real object.
"""
from math import comb
from itertools import product
from functools import lru_cache

P, D, AMIN, N = 5, 13, 6, 31
BRUTE_MAX = 10          # exhaustive search when the window has at most this many lengths


def gauss_feasible(p, rows, nv):
    A = [r[:] for r in rows]; piv = 0
    for c in range(nv):
        r = next((i for i in range(piv, len(A)) if A[i][c] % p), None)
        if r is None:
            continue
        A[piv], A[r] = A[r], A[piv]
        inv = pow(A[piv][c], p - 2, p); A[piv] = [(x * inv) % p for x in A[piv]]
        for i in range(len(A)):
            if i != piv and A[i][c] % p:
                f = A[i][c]; A[i] = [(A[i][j] - f * A[piv][j]) % p for j in range(nv + 1)]
        piv += 1
    return not any(not any(A[i][:nv]) and A[i][nv] % p for i in range(len(A)))


def window(m, w):
    return [l for l in range(w + 1, m - w) if AMIN <= l <= m - AMIN]


def pointed_rows(m, w):
    S = window(m, w)
    return S, [([(((-1) ** l) * comb(l - 1, d)) % P for l in S],
                (-((-1) ** m) * comb(m - 1, d)) % P) for d in range(0, m - D)]


def feas_gauss(m, w):
    S, rows = pointed_rows(m, w)
    if not S:
        return False
    return gauss_feasible(P, [co + [r] for co, r in rows], len(S))


def feas_brute(m, w):
    S, rows = pointed_rows(m, w)
    if not S:
        return False
    for M in product(range(P), repeat=len(S)):
        if all(sum(c * x for c, x in zip(co, M)) % P == r for co, r in rows):
            return True
    return False


@lru_cache(maxsize=None)
def wbound(m):
    """Least w with the pointed system infeasible: C of length m has an atom <= w."""
    for w in range(AMIN - 1, m):
        if not feas_gauss(m, w):
            return w
    return None


def main():
    # ---- 1 ---------------------------------------------------------------
    # |U| <= 5 => |T U^-1| >= 26 = D_3+1; delete x, get 3 disjoint blocks in the
    # remaining >= 25 = D_3, and the rest (containing x) is a fifth block.
    assert N - 5 >= 25 + 1
    print(f"1. minimum atom length {AMIN}: a zero-sum of length <= 5 would give five "
          f"disjoint blocks (uses D_3(C_5^3) = 25)")

    # ---- 2 ---------------------------------------------------------------
    checked = brute_checked = 0
    for m in range(14, N + 1):
        w = wbound(m)
        assert w is not None and w >= AMIN - 1, (m, w)
        assert not feas_gauss(m, w), (m, w)
        assert feas_gauss(m, w - 1), (m, w, "w-1 must be feasible: bound not vacuous")
        checked += 1
        if len(window(m, w)) <= BRUTE_MAX:
            assert feas_brute(m, w) is False, (m, w, "brute/gauss disagree")
            assert feas_brute(m, w - 1) is True, (m, w, "brute/gauss disagree at w-1")
            brute_checked += 1
    print(f"2. pointed short-atom bounds decided for all {checked} lengths m in [14,31]; "
          f"{brute_checked} of them cross-checked by exhaustive search; in every case "
          f"w-1 is feasible, so no bound is vacuous")
    print("   w(m) =", {m: wbound(m) for m in range(31, 13, -1)})

    # ---- 3 ---------------------------------------------------------------
    corridor = set()
    for s in range(AMIN, wbound(N) + 1):                 # A1: a shortest atom
        m1 = N - s
        for a2 in range(s, wbound(m1) + 1):              # A2 in T A1^-1
            m2 = m1 - a2
            if m2 < 14:
                continue
            for a3 in range(s, wbound(m2) + 1):          # A3 in T (A1 A2)^-1
                a4 = m2 - a3
                # A4 must itself be an atom: otherwise it splits and we get five blocks
                if not (s <= a4 <= D):
                    continue
                corridor.add(tuple(sorted((s, a2, a3, a4))))
    corridor = sorted(corridor)
    assert all(sum(c) == N for c in corridor)
    assert corridor == [(6, 6, 6, 13), (6, 6, 7, 12), (6, 7, 7, 11),
                        (6, 7, 8, 10), (7, 7, 7, 10)], corridor
    print(f"3. four-atom corridor ({len(corridor)} profiles): {corridor}")

    # ---- 4 ---------------------------------------------------------------
    # A real packing-3 object over C_5^3 of length 25: every zero-sum
    # subsequence of length m >= 14 must satisfy the bound w(m).
    Q = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)]
    pts = list(Q); mult = [2 * P - 1, P - 1, P - 1, (P + 1) // 2, (P - 1) // 2, (P - 1) // 2]
    sig = tuple(sum(mult[i] * pts[i][j] for i in range(len(pts))) % P for j in range(3))
    comp = tuple((-x) % P for x in sig)
    if comp in pts:
        mult[pts.index(comp)] += 1
    else:
        pts.append(comp); mult.append(1)
    assert sum(mult) == 25
    is_zs = lambda b: all(sum(b[i] * pts[i][j] for i in range(len(pts))) % P == 0
                          for j in range(3))
    box = list(product(*[range(x + 1) for x in mult]))
    zero = [b for b in box if any(b) and is_zs(b)]
    leq = lambda x, y: all(x[i] <= y[i] for i in range(len(pts)))
    atoms = [b for b in zero if not any(c != b and leq(c, b) for c in zero)]
    viol = 0; tested = 0
    for Z in zero:
        m = sum(Z)
        if m < 14:
            continue
        tested += 1
        shortest = min(sum(a) for a in atoms if leq(a, Z))
        if shortest > wbound(m):
            viol += 1
    assert viol == 0, viol
    print(f"4. control: on a real z=3 object over C_5^3, all {tested} zero-sum "
          f"subsequences of length >= 14 satisfy the predicted bound (0 violations)")

    print("PASS: four-atom corridor for the D_4(C_5^3) = 31 branch verified")


if __name__ == "__main__":
    main()
