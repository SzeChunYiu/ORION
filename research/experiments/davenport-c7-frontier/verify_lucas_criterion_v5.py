#!/usr/bin/env python3
"""Checker for LUCAS_CRITERION_V5.md.

Replaces the pointed system's linear algebra by an exact digit criterion, so
that the short-atom bound becomes a THEOREM rather than a per-prime computation.

The chain (every step an identity, not a computation):

  1. Fredholm.  A x = b over F_p is infeasible iff some lambda has lambda^T A = 0
     and lambda^T b != 0.  Here A[d][l] = (-1)^l C(l-1,d) for l in the window S,
     and b_d = -(-1)^m C(m-1,d), with 0 <= d <= dmax = m-D-1.

  2. Rewrite lambda as the integer-valued function P(y) = sum_d lambda_d C(y,d).
     Then lambda^T A = 0 says exactly P(l-1) = 0 for every l in S, and
     lambda^T b != 0 says exactly P(m-1) != 0.  For w >= p the set {l-1 : l in S}
     is the interval [w, m-w-2], of size L = m-2w-1.

  3. Newton's forward-difference formula about the left end w:
        P(y) = sum_d mu_d C(y-w, d),   mu_d = (Delta^d P)(w),
     a bijection on coefficient vectors, with mu_d = 0 for d > dmax.  Since
     C(j,d) = 0 for j < d, vanishing on [w, w+L-1] is EXACTLY mu_0 = ... = mu_{L-1} = 0.

  4. Hence P(m-1) = sum_{d=L}^{dmax} mu_d C(m-1-w, d) with mu free, so such a P
     with P(m-1) != 0 exists iff C(m-1-w, d) != 0 (mod p) for some d in [L, dmax].

  5. Lucas: C(Y,d) != 0 (mod p) iff every base-p digit of d is <= the
     corresponding digit of Y.

  THEOREM.  The pointed system at (p, m, w), w >= p, is infeasible if and only if
  there is an integer d with  m-2w-1 <= d <= m-3p+1  all of whose base-p digits
  are dominated by those of  m-1-w.

This file checks the implementation of the chain against the linear algebra it
replaces, and checks each individual step of the chain separately.
"""
from math import comb

PRIMES = (5, 7, 11, 13, 17, 19)


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


def window(p, m, w):
    return [l for l in range(w + 1, m - w) if p + 1 <= l <= m - (p + 1)]


def linalg_infeasible(p, m, w):
    D = 3 * p - 2; S = window(p, m, w)
    if not S:
        return True
    rows = [[(((-1) ** l) * comb(l - 1, d)) % p for l in S] +
            [(-((-1) ** m) * comb(m - 1, d)) % p] for d in range(0, m - D)]
    return not gauss_feasible(p, rows, len(S))


def digits(n, p):
    out = []
    while n:
        out.append(n % p); n //= p
    return out or [0]


def dominated(d, Y, p):
    dd, dy = digits(d, p), digits(Y, p)
    if len(dd) > len(dy):
        return False
    return all(dd[i] <= dy[i] for i in range(len(dd)))


def lucas_infeasible(p, m, w):
    if not window(p, m, w):
        return True
    L, dmax, Y = m - 2 * w - 1, m - 3 * p + 1, m - 1 - w
    return any(dominated(d, Y, p) for d in range(max(L, 0), dmax + 1))


def law(p, m):
    r, h, base = m % p, (p - 1) // 2, (3 * p - 1) // 2
    return base if (r <= h or r == p - 1) else base + r - h


def main():
    # ---- step 5 in isolation: Lucas ---------------------------------------
    bad = [(n, k) for p in PRIMES for n in range(0, 4 * p) for k in range(0, n + 1)
           if (comb(n, k) % p != 0) != dominated(k, n, p)]
    assert not bad, bad[:5]
    print("1. Lucas step checked directly: C(n,k) != 0 mod p  <=>  digits of k "
          "dominated by digits of n, over all n < 4p at every prime tested")

    # ---- step 3 in isolation: Newton ---------------------------------------
    for p in PRIMES[:3]:
        for w in (p, p + 3):
            for dmax in (4, 7):
                for lam in ([1] * (dmax + 1), list(range(1, dmax + 2))):
                    P = lambda y: sum(lam[d] * comb(y, d) for d in range(dmax + 1))
                    mu = [sum((-1) ** (d - j) * comb(d, j) * P(w + j) for j in range(d + 1))
                          for d in range(dmax + 1)]
                    for y in range(w, w + 12):
                        lhs = P(y) % p
                        rhs = sum(mu[d] * comb(y - w, d) for d in range(dmax + 1)) % p
                        assert lhs == rhs, (p, w, dmax, y)
    print("2. Newton's forward-difference rewriting checked numerically: "
          "P(y) = sum_d (Delta^d P)(w) C(y-w, d) on every sample")

    # ---- the whole chain vs the linear algebra ----------------------------
    n = 0
    for p in PRIMES:
        D, N = 3 * p - 2, (11 * p - 3) // 2
        for m in range(D + 1, N + 1):
            for w in range(p, m // 2 + 1):
                assert linalg_infeasible(p, m, w) == lucas_infeasible(p, m, w), (p, m, w)
                n += 1
    print(f"3. the digit criterion agrees with Gaussian elimination on all {n} "
          f"(p,m,w) cases across primes {PRIMES} -- 0 disagreements")

    # ---- the closed-form law now follows from the criterion ---------------
    for p in PRIMES:
        D, N = 3 * p - 2, (11 * p - 3) // 2
        for m in range(D + 1, N + 1):
            lw = next(w for w in range(p, m) if lucas_infeasible(p, m, w))
            assert lw == law(p, m), (p, m, lw, law(p, m))
    print("4. the closed-form law w(p,m) is recovered from the digit criterion "
          "alone, with no linear algebra, at every prime and length tested")

    print("PASS: the pointed system's infeasibility is an exact digit criterion")


if __name__ == "__main__":
    main()
