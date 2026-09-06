#!/usr/bin/env python3
"""Self-contained verification of CLOSED_FORM_CONJECTURE_V7.md.

The conjecture is

    D_k(C_p^r) = (3/2) r(p-1) + (k-2) p + 2        (k >= 2, p an odd prime)

Nothing here proves it.  What is asserted is the arithmetic: that its three constants are
forced by the rank-two formula alone, that it then agrees with every exact value this packet
or the literature supplies, that it differs from the naive formula precisely where the naive
one is known to fail, and that the construction reaches it at 10 of 13 computed points and
falls exactly one short at the other three.

  Step 1  the constants (3/2, 1, 2) are the unique solution forced by rank two
  Step 2  agreement with all 24 known exact values
  Step 3  the naive formula fails at exactly the points where this one is tested
  Step 4  the construction lower bound r(p-1) + M* + 1 against the conjecture
  Step 5  the conjecture respects the proved bracket D+1 <= D_2 <= 2D
  Step 6  k=1 behaves as Freeze-Schmid requires: exact at r=2, wrong for r>=3
"""
from fractions import Fraction as F


def conj(p, r, k):
    return F(3, 2) * r * (p - 1) + (k - 2) * p + 2


def naive(p, r, k):
    """the standard guess, known false for elementary p-groups of rank >= 3"""
    return r * (p - 1) + (k - 1) * p + 1


def rank2(p, k):
    """literature: D_k(C_m + C_n) = m + kn - 1 for m | n; here m = n = p"""
    return p + k * p - 1


def D(p, r):
    return r * (p - 1) + 1


# recorded construction optima over 0/1-indicator families, WITNESS_CRITERION_V6.md sections 6, 6b
MSTAR = {(2, 3): 3, (2, 5): 5, (2, 7): 7, (3, 3): 4, (3, 5): 7, (3, 7): 10,
         (4, 3): 5, (4, 5): 9, (4, 7): 12, (5, 3): 6, (5, 5): 10, (6, 3): 7, (7, 3): 7}

KNOWN = ([(p, 2, k, rank2(p, k), "rank-2 formula (literature)") for p in (3, 5, 7, 11)
          for k in (2, 3, 4, 5)]
         + [(p, 3, 2, (9 * p - 5) // 2, "packet theorem (9p-5)/2") for p in (3, 5, 7, 11)]
         + [(5, 3, 3, 25, "packet, exhaustive L=25"),
            (7, 3, 3, 36, "packet, corridor + Hypothesis (Z)"),
            (5, 3, 4, 30, "packet, Theorem T, 5.9e9 nodes"),
            (3, 5, 2, 17, "packet, 2.7e9-node sweep")])


def step1():
    pts = [(3, 2), (3, 3), (5, 2)]
    M = [[F(2 * (p - 1)), F(p * (k - 2)), F(1), F(rank2(p, k))] for p, k in pts]
    n = 3
    for c in range(n):
        piv = next(i for i in range(c, n) if M[i][c] != 0)
        M[c], M[piv] = M[piv], M[c]
        d = M[c][c]
        M[c] = [x / d for x in M[c]]
        for i in range(n):
            if i != c and M[i][c] != 0:
                f = M[i][c]
                M[i] = [M[i][j] - f * M[c][j] for j in range(n + 1)]
    alpha, beta, gamma = M[0][3], M[1][3], M[2][3]
    assert (alpha, beta, gamma) == (F(3, 2), F(1), F(2)), (alpha, beta, gamma)
    for p in (3, 5, 7, 11, 13):
        for k in (1, 2, 3, 4, 5, 9):
            assert alpha * 2 * (p - 1) + beta * p * (k - 2) + gamma == rank2(p, k)
    print("1. the constants are forced: solving at rank two gives (alpha, beta, gamma) =")
    print("   (3/2, 1, 2) uniquely, and that fits D_k(C_p^2) = p + kp - 1 for every p and k")
    print("   tested -- so ranks 3 and 5 below are predictions, not fits")


def step2():
    for p, r, k, val, _ in KNOWN:
        assert conj(p, r, k) == val, (p, r, k, val, conj(p, r, k))
    ranks = sorted({r for _, r, _, _, _ in KNOWN})
    ks = sorted({k for _, _, k, _, _ in KNOWN})
    print(f"2. all {len(KNOWN)} known exact values matched, ranks {ranks}, k in {ks} --")
    print("   including the four hardest: D_3(C_5^3)=25, D_3(C_7^3)=36, D_4(C_5^3)=30,")
    print("   D_2(C_3^5)=17, none of which could have been used to fix the constants")


def step3():
    miss = [(p, r, k, val) for p, r, k, val, _ in KNOWN if naive(p, r, k) != val]
    hit = len(KNOWN) - len(miss)
    assert all(r >= 3 for p, r, k, _ in miss), "naive should only fail at rank >= 3"
    assert all(naive(p, 2, k) == rank2(p, k) for p in (3, 5, 7) for k in (2, 3, 4))
    print(f"3. the naive formula r(p-1)+(k-1)p+1 agrees at all {hit} rank-2 points and fails")
    print(f"   at all {len(miss)} points of rank >= 3 -- the documented failure of the rank-2")
    print("   shape for elementary p-groups is exactly what this conjecture repairs")


def step4():
    achieve, short = [], []
    for (r, p), m in sorted(MSTAR.items()):
        lb = r * (p - 1) + m + 1
        d = conj(p, r, 2) - lb
        assert d >= 0, (r, p, d)
        (achieve if d == 0 else short).append((r, p, int(d)))
    assert len(achieve) == 10 and len(short) == 3
    assert all(d == 1 for _, _, d in short)
    assert sorted((r, p) for r, p, _ in short) == [(4, 7), (5, 5), (7, 3)]
    print(f"4. the construction r(p-1)+M*+1 reaches the conjecture at {len(achieve)} of "
          f"{len(MSTAR)} computed")
    print("   (r,p) and falls short by exactly 1 at the other three: (7,3), (4,7), (5,5).")
    print("   M* is an optimum over a family class, so a shortfall does not refute the")
    print("   conjecture -- but three shortfalls of exactly one is the open tension")


def step5():
    for (r, p) in MSTAR:
        c = conj(p, r, 2)
        assert D(p, r) + 1 <= c <= 2 * D(p, r), (r, p)
    print("5. the conjecture lies inside the proved bracket D+1 <= D_2 <= 2D at every")
    print("   computed (r,p) -- it is consistent with the complement lemma and Olson")


def step6():
    for p in (3, 5, 7, 11):
        assert conj(p, 2, 1) == D(p, 2) == rank2(p, 1)
    bad = [(p, r) for p in (3, 5, 7) for r in (3, 4, 5) if conj(p, r, 1) != D(p, r)]
    assert len(bad) == 9
    print("6. at k=1 the formula is exact for r=2 and wrong for every r>=3 tested -- the")
    print("   arithmetic progression is only eventual, as Freeze-Schmid's theorem requires")


if __name__ == "__main__":
    step1(); step2(); step3(); step4(); step5(); step6()
    print()
    print("CONJECTURE ARITHMETIC VERIFIED.  D_k(C_p^r) = (3/2) r(p-1) + (k-2) p + 2 agrees")
    print("with all 24 known exact values.  It is a conjecture, not a theorem.")
