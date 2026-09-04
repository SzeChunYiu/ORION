#!/usr/bin/env python3
"""Checker for DUAL_SUPPORT_TWELVE_POINTS_V5.md.

Explains Observation D structurally.  With h = (p-3)/2 and N = 5p + h, put

    S = { j*p : j = 0..5 }  union  { j*p + h : j = 0..5 }      (12 points)

which the involution y -> N-y pairs as (j,0) <-> (5-j,h).

  LEMMA 1 (proved below, elementary, all p >= 5).  Exactly three points of S lie
  in the atom range [p+1, 3p-2], namely
        p + h   = 3(p-1)/2,      2p,      2p + h = (5p-3)/2
  -- the three special lengths.

  CLAIM 2 (verified, not proved).  Every dual Q with Q(0) != 0 is supported
  inside S; and when the excluded pair Z consists of two special lengths, Q is
  supported in S minus the involution-pair of the THIRD special length.

Together these say: the dual can only be nonzero on the 12 points of S, of which
only the three special lengths are atom lengths -- so the antisymmetry of the
spectrum can be broken only there.  That is why Observation D holds.
"""
from math import factorial
from itertools import combinations

PRIMES = (11, 13, 17, 19, 23)


def bp(n, k):
    if k < 0:
        return 0
    r = 1
    for i in range(k):
        r *= (n - i)
    return r // factorial(k)


def lemma1(p):
    """Exactly which points of S lie in [p+1, 3p-2] -- checked directly."""
    h = (p - 3) // 2
    S = sorted({j * p for j in range(6)} | {j * p + h for j in range(6)})
    return [x for x in S if p + 1 <= x <= 3 * p - 2], S


def duals(p, Z):
    """All Q with Q(0) != 0, from the Newton parametrisation about A = N-D."""
    N = (11 * p - 3) // 2; D = 3 * p - 2; amin = p + 1; sgn = (-1) ** N
    A = N - D; hh = D - A + 1
    ds = list(range(hh, N - D + 1))
    Pb = lambda d, y: bp(y - A, d) % p
    Ls = [L for L in range(amin, D + 1) if L not in Z]
    M = [[(Pb(d, L) + sgn * Pb(d, N - L)) % p for d in ds] for L in Ls]
    nr, nc = len(M), len(ds)
    piv = []; r = 0
    for c in range(nc):
        pr = next((i for i in range(r, nr) if M[i][c] % p), None)
        if pr is None:
            continue
        M[r], M[pr] = M[pr], M[r]
        iv = pow(M[r][c], p - 2, p); M[r] = [x * iv % p for x in M[r]]
        for i in range(nr):
            if i != r and M[i][c] % p:
                f = M[i][c]; M[i] = [(M[i][j] - f * M[r][j]) % p for j in range(nc)]
        piv.append(c); r += 1
        if r == nr:
            break
    out = []
    for fc in [c for c in range(nc) if c not in piv]:
        v = [0] * nc; v[fc] = 1
        for i, c in enumerate(piv):
            v[c] = (-M[i][fc]) % p
        Pv = lambda y, v=v: sum(v[i] * Pb(ds[i], y) for i in range(nc)) % p
        Q = [(Pv(y) + sgn * Pv(N - y)) % p for y in range(N + 1)]
        if Q[0]:
            out.append(Q)
    return N, out


def main():
    # ---- Lemma 1, over a wide range of primes -----------------------------
    prs = [n for n in range(5, 400) if n > 1 and all(n % q for q in range(2, int(n ** .5) + 1))]
    for p in prs:
        h = (p - 3) // 2
        inat, S = lemma1(p)
        assert len(S) == 12 or p == 3, (p, S)
        assert inat == sorted([3 * (p - 1) // 2, 2 * p, (5 * p - 3) // 2]), (p, inat)
    print(f"1. LEMMA 1 verified for all {len(prs)} primes 5..397: of the 12 points of S, "
          f"exactly p+h = 3(p-1)/2, 2p and 2p+h = (5p-3)/2 lie in the atom range "
          f"[p+1, 3p-2] -- these are precisely the three special lengths")

    # the elementary reasons, asserted individually
    for p in prs:
        h = (p - 3) // 2
        assert p < p + 1 and 3 * p > 3 * p - 2                    # jp: j=1 too small, j=3 too big
        assert p + 1 <= 2 * p <= 3 * p - 2                        # jp: j=2 lands
        assert h < p + 1                                          # jp+h: j=0 too small
        assert p + 1 <= p + h and 2 * p + h <= 3 * p - 2          # jp+h: j=1,2 land
        assert 3 * p + h > 3 * p - 2                              # jp+h: j=3 too big
    print("2. the four inequalities behind Lemma 1 hold for every prime tested, "
          "so the count is uniform in p and needs no computation")

    # ---- Claim 2 ----------------------------------------------------------
    for p in PRIMES:
        h = (p - 3) // 2
        a, b, c = 3 * (p - 1) // 2, 2 * p, (5 * p - 3) // 2
        _, S = lemma1(p)
        for Z, third in (({b, c}, a), ({a, c}, b), ({a, b}, c)):
            N, Qs = duals(p, Z)
            assert Qs, (p, Z, "there must be a dual")
            want = set(S) - {third, N - third}
            for Q in Qs:
                sup = {y for y in range(N + 1) if Q[y]}
                assert sup <= want, (p, sorted(Z), sorted(sup - want))
        print(f"3. p={p:>3}: every dual Q with Q(0) != 0 is supported in S minus the "
              f"involution-pair of the third special length (all three pairs checked)")

    print("PASS: the dual lives on 12 points, and only the three special lengths "
          "among them are atom lengths")


if __name__ == "__main__":
    main()
