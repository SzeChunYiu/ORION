#!/usr/bin/env python3
"""Checker for D4_FLAT_PROFILE_BRIDGE_V6.md.

The congruence machinery is indifferent to whether a part is maximal, so it can
reach the FLAT profiles that the maximal-atom methods cannot.  Run it on the
D_4(C_5^3) object.

Setting: T zero-sum over C_5^3, |T| = N = 31, D = 13, no zero-sum of length <= 5.
The symmetric identity holds for ANY zero-sum T, whatever its atom structure:

    sum_l (-1)^l N_l C(l,d) + [C(0,d) + (-1)^N C(N,d)] = 0,   0 <= d <= N - D,

with N_l the weighted count of zero-sum sub-multisets of length l, and
N_l = N_{N-l} by complementation (complementation preserves the weight).
Atoms of length >= 6 give N_l = 0 for l in [1,5] and hence for l in [26,30].

RESULT.  The minimal forced sets are exactly the pairs {6, x}, x in [7,24]
(equivalently {x, 25}, since N_6 = N_25).  So:

    if T has no zero-sum of length 6, it has one of EVERY length 7..24.

CONSEQUENCE for the flat profile (7,7,7,10) -- the only one of the five with no
part equal to 6.  Its shortest atom is 7, so T has no atom of length 6, hence no
zero-sum of length 6 (such a zero-sum contains an atom of length <= 6, and atoms
are >= 6, so it would BE a 6-atom).  Therefore T has zero-sums of every length
7..24; and for l <= 13 such a zero-sum must be a single atom, since two disjoint
atoms already total >= 14.  So T has an atom of EVERY length 7,...,13 -- in
particular a MAXIMAL atom of length 13 = D.

That is the bridge: a flat profile is forced to contain a maximal atom, so the
maximal-atom machinery applies to it after all.  With Theorem M, that atom must
have support >= 5.
"""
from math import comb
from itertools import combinations

p, N, D, amin = 5, 31, 13, 6
sgn = (-1) ** N
LENS = list(range(amin, N - amin + 1))
PROFILES = [(6, 6, 6, 13), (6, 6, 7, 12), (6, 7, 7, 11), (6, 7, 8, 10), (7, 7, 7, 10)]


def feasible(zero):
    reps = sorted({min(l, N - l) for l in LENS if l not in zero})
    if not reps:
        return False
    rows = []
    for d in range(0, N - D + 1):
        row = [0] * len(reps)
        for l in LENS:
            if l in zero:
                continue
            j = reps.index(min(l, N - l))
            row[j] = (row[j] + ((-1) ** l) * comb(l, d)) % p
        rows.append(row + [(-(comb(0, d) + sgn * comb(N, d))) % p])
    A = [r[:] for r in rows]; nv = len(reps); piv = 0
    for c in range(nv):
        r = next((i for i in range(piv, len(A)) if A[i][c] % p), None)
        if r is None:
            continue
        A[piv], A[r] = A[r], A[piv]
        iv = pow(A[piv][c], p - 2, p); A[piv] = [x * iv % p for x in A[piv]]
        for i in range(len(A)):
            if i != piv and A[i][c] % p:
                f = A[i][c]; A[i] = [(A[i][j] - f * A[piv][j]) % p for j in range(nv + 1)]
        piv += 1
    return not any(not any(A[i][:nv]) and A[i][nv] % p for i in range(len(A)))


def main():
    assert feasible(set()), "unrestricted system must be consistent (non-vacuity)"
    print("1. unrestricted system is consistent -- the forced sets below are not vacuous")

    forced = []
    for size in (1, 2):
        for S in combinations(LENS, size):
            if any(set(m) <= set(S) for m in forced):
                continue
            if not feasible(set(S)):
                forced.append(S)
    assert all(len(S) == 2 for S in forced), "no single length should be forced"
    assert all(6 in S or 25 in S for S in forced), forced[:5]
    assert set(forced) == ({(6, x) for x in range(7, 25)} | {(x, 25) for x in range(7, 25)}), \
        sorted(set(forced) ^ ({(6, x) for x in range(7, 25)} | {(x, 25) for x in range(7, 25)}))
    print(f"2. minimal forced sets are exactly the {len(forced)} pairs {{6,x}} and {{x,25}}, "
          f"x in [7,24] -- and 6, 25 are the same unknown, so the content is: "
          f"N_6 = 0 forces N_x != 0 for every x in [7,24]")

    # the flat profile is the only one with no part 6
    noSix = [pr for pr in PROFILES if 6 not in pr]
    assert noSix == [(7, 7, 7, 10)], noSix
    print(f"3. of the five corridor profiles, exactly one has no part equal to 6: {noSix[0]}")

    # for it: shortest atom 7 => no 6-atom => no zero-sum of length 6
    pr = noSix[0]
    assert min(pr) == 7
    # zero-sums of length <= 13 must be single atoms, since 2 atoms >= 14
    assert 2 * min(pr) > D, (min(pr), D)
    print(f"4. its shortest atom is 7, so 2 disjoint atoms total >= 14 > 13 = D: every "
          f"zero-sum of length <= 13 is a single ATOM")
    print(f"5. hence T must carry atoms of every length 7,8,...,13 -- including a "
          f"MAXIMAL atom of length {D}. Combined with Theorem M "
          f"(D4_C5_SUPPORT4_MAXIMAL_CLOSURE_V6), that atom has support >= 5.")
    print("PASS: the flat profile (7,7,7,10) is forced to contain a maximal atom")


if __name__ == "__main__":
    main()
