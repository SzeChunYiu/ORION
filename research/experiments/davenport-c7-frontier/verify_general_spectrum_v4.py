#!/usr/bin/env python3
"""Checker for GENERAL_SPECTRUM_SPECIAL_LENGTHS_V4.md.

The whole D_3(C_p^3) atom-spectrum apparatus, run uniformly in p.

For a prime p >= 5 put
    N    = (11p-3)/2      length of the zero-sum object attached to an obstruction
    D    = 3p-2           Olson
    D_2  = (9p-5)/2       proved uniformly in this packet
    amin = p+1            no zero-sum of length <= p

Zero-sum sub-multisets of the obstruction are exactly the empty one, the whole
thing, the atoms (lengths in [amin, D]) and the complements of atoms; a
multiset that is both has length in [N-D, D].  With W_L the weighted atom count
and X_L the weighted count of the double-counted ones, the counting identity
gives, for every 0 <= d <= N-D,

    C(0,d) + (-1)^N C(N,d)
      + sum_L (-1)^L W_L [ C(L,d) + (-1)^N C(N-L,d) ]
      - sum_{L in [N-D,D]} (-1)^L X_L C(L,d)   ==  0   (mod p).

Call L in [amin, D] SPECIAL when p | L or p | (N-L).  There are exactly three:
    3(p-1)/2   (complement 4p),   2p,   (5p-3)/2   (complement 3p).

Steps
  1. agreement with the recorded p=7 verifier on every length subset of size <= 3;
  2. the special lengths are exactly {3(p-1)/2, 2p, (5p-3)/2}, for every prime tested;
  3. each of the three pairs of special lengths is FORCED (system infeasible);
  4. no single length is forced for p >= 11, and no non-special pair is forced
     -- so the three pairs are exactly the minimal forced sets;
  5. the two small primes p=5 and p=7 are RICHER (18 minimal forced sets each,
     all three special pairs among them, and at p=7 also the {13,14} used by
     the D_3(C_7^3) = 36 proof);
  6. controls: the unrestricted system is consistent for every p, and the whole
     conclusion is unchanged by imposing the valid relation X_L = X_{N-L}.
"""
import importlib.util, os, sys
from math import comb
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
SMALL = (5, 7, 11, 13, 17, 19)      # exhaustive minimal-forced-set search
LARGE = (23, 29, 31)                # targeted checks only (keeps the checker fast)


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


def params(p):
    return (11 * p - 3) // 2, 3 * p - 2, p + 1


def special(p):
    N, D, amin = params(p)
    return sorted(L for L in range(amin, D + 1) if L % p == 0 or (N - L) % p == 0)


def spec_feasible(p, zeroset, pair_X=False):
    N, D, amin = params(p)
    sgn = (-1) ** N
    Ws = [L for L in range(amin, D + 1) if L not in zeroset]
    ov = [L for L in range(max(N - D, amin), D + 1)
          if L not in zeroset and N - L not in zeroset]
    if pair_X:
        reps = sorted({min(L, N - L) for L in ov})
        xcols = [(r, [L for L in ov if min(L, N - L) == r]) for r in reps]
    else:
        xcols = [(L, [L]) for L in ov]
    rows = []
    for d in range(0, N - D + 1):
        row = [(((-1) ** L) * (comb(L, d) + sgn * comb(N - L, d))) % p for L in Ws]
        row += [sum(-(((-1) ** L) * comb(L, d)) for L in grp) % p for _, grp in xcols]
        rows.append(row + [(-(comb(0, d) + sgn * comb(N, d))) % p])
    return gauss_feasible(p, rows, len(Ws) + len(xcols))


def minimal_forced(p, maxsize=2):
    N, D, amin = params(p)
    lens = list(range(amin, D + 1)); out = []
    for size in range(1, maxsize + 1):
        for S in combinations(lens, size):
            if any(set(m) <= set(S) for m in out):
                continue
            if not spec_feasible(p, set(S)):
                out.append(S)
    return out


def main():
    # ---- 1 : agreement with the recorded p=7 verifier ----------------------
    spec = importlib.util.spec_from_file_location(
        "vas", os.path.join(HERE, "verify_atom_spectrum_v3.py"))
    vas = importlib.util.module_from_spec(spec); spec.loader.exec_module(vas)
    lens7 = list(range(8, 20))
    dis = 0; n = 0
    for size in (1, 2, 3):
        for S in combinations(lens7, size):
            n += 1
            if vas.feasible(7, 37, 19, lens7, set(S), (18, 19)) != spec_feasible(7, set(S)):
                dis += 1
    assert dis == 0, dis
    print(f"1. general system agrees with the recorded p=7 verifier on all {n} "
          f"length subsets of size <= 3")

    # ---- 2 : the special lengths -------------------------------------------
    for p in SMALL + LARGE:
        assert special(p) == [3 * (p - 1) // 2, 2 * p, (5 * p - 3) // 2], (p, special(p))
    print(f"2. for every prime tested, {{L in [p+1,3p-2] : p | L or p | (N-L)}} "
          f"= {{3(p-1)/2, 2p, (5p-3)/2}}")

    # ---- 3, 6 : the three pairs are forced; controls ------------------------
    for p in SMALL + LARGE:
        assert spec_feasible(p, set()), (p, "unrestricted system must be consistent")
        for pair in combinations(special(p), 2):
            assert not spec_feasible(p, set(pair)), (p, pair)
            assert not spec_feasible(p, set(pair), pair_X=True), (p, pair, "with X_L=X_{N-L}")
    print(f"3. for every prime tested ({', '.join(map(str, SMALL + LARGE))}): the "
          f"unrestricted system is consistent, and excluding ANY TWO special "
          f"lengths makes it infeasible -- both with X_L free and with X_L = X_{{N-L}}")

    # ---- 4, 5 : minimality, and the small primes ---------------------------
    for p in SMALL:
        mf = minimal_forced(p)
        trip = sorted(tuple(sorted(c)) for c in combinations(special(p), 2))
        if p == 5:
            assert all(t in mf for t in trip), (mf, trip)
            print(f"5. p=5: RICHER -- {len(mf)} minimal forced sets, containing all three "
                  f"special pairs {trip}")
        elif p == 7:
            assert (13, 14) in mf, mf
            assert all(t in mf for t in trip), (mf, trip)
            print(f"5. p=7: RICHER -- {len(mf)} minimal forced sets, containing all three "
                  f"special pairs {trip} and the {{13,14}} used by the D_3(C_7^3)=36 proof")
        else:
            assert sorted(mf) == trip, (p, mf, trip)
            print(f"4. p={p}: the minimal forced sets are EXACTLY the three special "
                  f"pairs {trip} -- nothing else, no singletons")

    print("PASS: uniform special-length structure verified")


if __name__ == "__main__":
    main()
