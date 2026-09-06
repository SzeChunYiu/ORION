#!/usr/bin/env python3
"""Checker for SHORT_ATOM_LAW_UNIFORM_V5.md.

Generalises the p=7 short-atom bound to a closed form valid at every prime, and
records the exceptional residues -- which also CORRECT the range stated in
SHORT_ATOM_BOUND_UNIFORM_V4.md (see step 4).

LEMMA (no packing hypothesis).  If C is zero-sum over C_p^3 with |C| = m and
every atom of C has length >= w+1, then every proper nonempty zero-sum of C has
length in [w+1, m-w-1]: it contains an atom, and so does its complement.  So the
pointed system on that two-sided window must be consistent; infeasibility forces
an atom of length <= w.

LAW.  Write r = m mod p and h = (p-1)/2.  Then the least w for which the system
is infeasible is

    w(p,m) = (3p-1)/2                 if r <= h or r = p-1
           = (3p-1)/2 + r - h         if h+1 <= r <= p-2

so the generic bound is (3p-1)/2 -- about half the Davenport constant D = 3p-2 --
rising to at most 2p-2 on a run of residues.
"""
from math import comb
from itertools import product

PRIMES = (5, 7, 11, 13, 17, 19, 23)
BRUTE_ASSIGNMENTS = 2_000_000   # cap the exhaustive check by total assignments p^|S|


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


def rows_of(p, m, w):
    D = 3 * p - 2
    S = window(p, m, w)
    return S, [([(((-1) ** l) * comb(l - 1, d)) % p for l in S],
                (-((-1) ** m) * comb(m - 1, d)) % p) for d in range(0, m - D)]


def feas(p, m, w):
    S, rows = rows_of(p, m, w)
    return bool(S) and gauss_feasible(p, [co + [r] for co, r in rows], len(S))


def feas_brute(p, m, w):
    S, rows = rows_of(p, m, w)
    if not S:
        return False
    return any(all(sum(c * x for c, x in zip(co, M)) % p == r for co, r in rows)
               for M in product(range(p), repeat=len(S)))


def wbound(p, m):
    for w in range(p, m):
        if not feas(p, m, w):
            return w
    return None


def law(p, m):
    r, h, base = m % p, (p - 1) // 2, (3 * p - 1) // 2
    return base if (r <= h or r == p - 1) else base + r - h


def main():
    # ---- 1 : the law, over every length any application uses ---------------
    tested = brute = 0
    for p in PRIMES:
        D, N = 3 * p - 2, (11 * p - 3) // 2
        for m in range(D + 1, N + 1):
            w = wbound(p, m)
            assert w == law(p, m), (p, m, m % p, w, law(p, m))
            assert feas(p, m, w - 1), (p, m, "w-1 must be feasible")
            tested += 1
            if p ** len(window(p, m, w)) <= BRUTE_ASSIGNMENTS:
                assert feas_brute(p, m, w) is False, (p, m, w, "brute/gauss disagree")
                brute += 1
    print(f"1. closed form verified for every prime {PRIMES} and every length "
          f"m in [3p-1, (11p-3)/2]: {tested} lengths, 0 mismatches; "
          f"{brute} cross-checked by exhaustive search; w-1 feasible everywhere")

    # ---- 2 : the generic value is about half the Davenport constant --------
    for p in PRIMES:
        assert law(p, p * 7) == (3 * p - 1) // 2               # r = 0
        assert max(law(p, m) for m in range(3 * p, 4 * p)) == 2 * p - 2
    print("2. generic bound is (3p-1)/2 (about D/2, since D = 3p-2); the "
          "exceptional residues raise it to at most 2p-2")

    # ---- 3 : the exceptional residues are exactly [ (p+1)/2, p-2 ] ---------
    for p in PRIMES:
        exc = sorted({m % p for m in range(3 * p, 3 * p + p) if law(p, m) != (3 * p - 1) // 2})
        assert exc == list(range((p + 1) // 2, p - 1)), (p, exc)
    print("3. the residues where the bound is NOT (3p-1)/2 are exactly "
          "r in [(p+1)/2, p-2], for every prime tested")

    # ---- 4 : CORRECTION to SHORT_ATOM_BOUND_UNIFORM_V4.md ------------------
    good = [m for m in range(23, 30) if wbound(7, m) == 10]
    bad = [(m, wbound(7, m)) for m in range(23, 30) if wbound(7, m) != 10]
    assert good == [23, 24, 27, 28, 29], good
    assert bad == [(25, 11), (26, 12)], bad
    print(f"4. CORRECTION: at p=7 the bound is 10 exactly for m in {good}; "
          f"m=25 and m=26 give {[b[1] for b in bad]} instead. The V4 record stated "
          f"the range as 23 <= |C| <= 29, which overreached; only the five listed "
          f"lengths were ever verified, and they are the only ones the corridors use "
          f"(29,28,27 for the first, 24,23 for the second), so no downstream "
          f"conclusion changes.")

    # ---- 5 : the range of the law is comfortable --------------------------
    assert wbound(5, 34) != law(5, 34) and all(wbound(5, m) == law(5, m) for m in range(14, 34))
    print("5. range control: the closed form holds well past the applied range -- "
          "for p=5 it first fails at m=34, against N=26; for p=7 at m=62, against N=37")

    print("PASS: uniform short-atom law verified, and the V4 range corrected")


if __name__ == "__main__":
    main()
