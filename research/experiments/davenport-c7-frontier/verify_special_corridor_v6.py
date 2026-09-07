#!/usr/bin/env python3
"""Checker for COMBINED_COMPLETION_MAP_V6.md.

Combines two proved results from this lane into a new uniform corridor:

  Theorem J        every obstruction has atoms of at least TWO of the three
                   special lengths a = 3(p-1)/2, b = 2p, c = (5p-3)/2;
  short-atom law   a zero-sum C over C_p^3 whose atoms all exceed p has an atom
                   of length <= w(p,|C|), generically (3p-1)/2.

Peeling a present special length A gives C = T A^{-1} of length N-L, which has an
atom E with |E| <= w(p, N-L); and F = C E^{-1} must be an atom, since otherwise
A, E and two blocks of F are four disjoint blocks.  So T has a three-atom
factorization through EVERY special length it carries -- and it carries at least
two of them.
"""
PRIMES = (7, 11, 13, 17, 19, 23, 29, 31)


def law(p, m):
    r, h, base = m % p, (p - 1) // 2, (3 * p - 1) // 2
    return base if (r <= h or r == p - 1) else base + r - h


def rows(p):
    N, D, amin = (11 * p - 3) // 2, 3 * p - 2, p + 1
    out = {}
    for L in (3 * (p - 1) // 2, 2 * p, (5 * p - 3) // 2):
        m = N - L
        assert m > D, (p, L)               # the complement always exceeds D
        w = law(p, m)
        out[L] = [(L, u, m - u) for u in range(max(amin, m - D), w + 1)
                  if u <= m - u <= D]
        assert out[L], (p, L, "row must be nonempty")
    return out


def main():
    for p in PRIMES:
        D = 3 * p - 2
        R = rows(p)
        for L, trips in R.items():
            for (x, u, v) in trips:
                assert x + u + v == (11 * p - 3) // 2
                assert p + 1 <= u <= v <= D
        withmax = {L: sum(1 for t in R[L] if D in t) for L in R}
        tot = sum(len(v) for v in R.values())
        a, b, c = sorted(R)
        print(f"p={p:>3}: special-length corridor has {tot} triples "
              f"({len(R[a])}/{len(R[b])}/{len(R[c])} through a/b/c); triples "
              f"containing a maximal atom: {withmax[a]}/{withmax[b]}/{withmax[c]}")
    print()
    # p = 7 must reproduce the recorded corridors
    R7 = rows(7)
    assert R7[9] == [(9, 9, 19), (9, 10, 18)], R7[9]
    print("1. at p=7 the a-row is exactly {(9,9,19), (9,10,18)} -- the two "
          "non-(8,10,19) triples of the tightened first corridor")
    # the b and c rows carry no maximal atom for p >= 11
    for p in PRIMES:
        if p < 11:
            continue
        D = 3 * p - 2
        R = rows(p)
        b, c = 2 * p, (5 * p - 3) // 2
        assert not any(D in t for t in R[b]), (p, "b-row")
        assert not any(D in t for t in R[c]), (p, "c-row")
    print("2. for every prime p >= 11 tested, NO triple through b = 2p or "
          "c = (5p-3)/2 contains a maximal atom -- so the maximal-atom support "
          "machinery cannot reach those rows at all")
    print("PASS: special-length corridor verified")


if __name__ == "__main__":
    main()
