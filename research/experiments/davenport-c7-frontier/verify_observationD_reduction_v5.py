#!/usr/bin/env python3
"""Checker for OBSERVATION_D_REDUCTION_V5.md.

Reduces Observation D from an opaque rank computation to a statement about one
symmetric function.  Dualising the atom-spectrum system gives an integer-valued
P with deg P <= N-D such that

    P(L) + (-1)^N P(N-L) = 0     for every atom length L in [p+1, 3p-2] \\ Z
    P(L) = 0                     for L in the overlap range [N-D, D]
    P(0) + (-1)^N P(N) != 0.

Put Q(y) = P(y) + (-1)^N P(N-y).  Then Q is the object of interest:

  (1) P vanishes on the whole INTEGER INTERVAL [N-D, D], whose length is exactly
      (p-3)/2 -- the low base-p digit of N = (5, (p-3)/2)_p;
  (2) Q(N-y) = (-1)^N Q(y): Q is (-1)^N-symmetric about N/2;
  (3) Q vanishes on the atom range EXCEPT at the two excluded lengths, and is
      nonzero at BOTH of them: Z is exactly the failure set of the antisymmetry;
  (4) Q(0) != 0: the antisymmetry fails at 0 as well.

So "the pair Z is forced" says: the antisymmetry of the spectrum can be broken
at exactly the two lengths of Z and at 0, and nowhere else.  That is why the
special lengths are special.
"""
from math import comb

PRIMES = (11, 13, 17, 19, 23)


def params(p):
    return (11 * p - 3) // 2, 3 * p - 2, p + 1


def dual(p, Z):
    """Some lambda killing every column and not the right-hand side."""
    N, D, amin = params(p); sgn = (-1) ** N
    Ws = [L for L in range(amin, D + 1) if L not in Z]
    ov = [L for L in range(max(N - D, amin), D + 1) if L not in Z and N - L not in Z]
    nd = N - D + 1
    cols = [[(((-1) ** L) * (comb(L, d) + sgn * comb(N - L, d))) % p for d in range(nd)]
            for L in Ws]
    cols += [[(-((-1) ** L) * comb(L, d)) % p for d in range(nd)] for L in ov]
    b = [(-(comb(0, d) + sgn * comb(N, d))) % p for d in range(nd)]
    M = [c[:] for c in cols]; nr = len(M); piv = []; r = 0
    for c in range(nd):
        pr = next((i for i in range(r, nr) if M[i][c] % p), None)
        if pr is None:
            continue
        M[r], M[pr] = M[pr], M[r]
        iv = pow(M[r][c], p - 2, p); M[r] = [x * iv % p for x in M[r]]
        for i in range(nr):
            if i != r and M[i][c] % p:
                f = M[i][c]; M[i] = [(M[i][j] - f * M[r][j]) % p for j in range(nd)]
        piv.append(c); r += 1
        if r == nr:
            break
    for fc in [c for c in range(nd) if c not in piv]:
        v = [0] * nd; v[fc] = 1
        for i, c in enumerate(piv):
            v[c] = (-M[i][fc]) % p
        if sum(v[d] * b[d] for d in range(nd)) % p:
            return v
    return None


def main():
    for p in PRIMES:
        N, D, amin = params(p); sgn = (-1) ** N
        a, b, c = 3 * (p - 1) // 2, 2 * p, (5 * p - 3) // 2
        assert D - (N - D) + 1 == (p - 3) // 2, p
        for Z in ({b, c}, {a, c}, {a, b}):
            lam = dual(p, Z)
            assert lam is not None, (p, Z, "the pair must be forced")
            Pv = lambda y: sum(lam[d] * comb(y, d) for d in range(len(lam))) % p
            Qv = lambda y: (Pv(y) + sgn * Pv(N - y)) % p
            assert all(Pv(y) == 0 for y in range(N - D, D + 1)), (p, Z, 1)
            assert all(Qv(N - y) == sgn * Qv(y) % p for y in range(N + 1)), (p, Z, 2)
            assert all(Qv(L) == 0 for L in range(amin, D + 1) if L not in Z), (p, Z, 3)
            assert all(Qv(L) != 0 for L in Z), (p, Z, "3b: nonzero at BOTH excluded lengths")
            assert Qv(0) != 0, (p, Z, 4)
        print(f"p={p:>3}: N={N} D={D}; middle interval [{N-D},{D}] has length "
              f"{(p-3)//2} = (p-3)/2 = low base-p digit of N; all four structural "
              f"claims hold for each of the three special pairs")
    print("PASS: Observation D reduces to one (-1)^N-symmetric function Q whose "
          "only nonzeros on the atom range are the two excluded lengths")


if __name__ == "__main__":
    main()
