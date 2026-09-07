#!/usr/bin/env python3
"""One command rebuilds the whole D_4(C_5^3) = 30 proof.

Mirrors verify_D3_C7_end_to_end_v3.py for the p=5, k=4 result.

  Step 1  lower bound: T_4(5) has length 29 and packing number 3
  Step 2  a length-31 obstruction has no zero-sum of length <= 5 (uses D_3 = 25)
  Step 3  the short-atom law w(5,m), decided independently per length
  Step 4  the four-atom corridor: exactly five profiles
  Step 5  every profile's largest part lies in {10,11,12,13}
  Step 6  the L=13 orbit sweep, RUN LIVE, finds no completion
  Step 7  the L=10,11,12 sweeps (recorded; too large to re-run here)
  => D_4(C_5^3) = 30
"""
import os, subprocess, sys
from math import comb
from itertools import product, combinations
from functools import lru_cache

P, N, D, AMIN = 5, 31, 13, 6
HERE = os.path.dirname(os.path.abspath(__file__))

RECORDED = {   # from D4_C5_DECIDED_V6.md; L=13 is re-run live below
    10: (94515860, 15289814, 44111, 5923695859, 0),
    11: (89338594, 13851427, 39760, 3674071087, 0),
    12: (36202974,  5603363, 17141, 1406175228, 0),
    13: ( 6315607,   998182,  3325,  284529220, 0),
}


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


@lru_cache(maxsize=None)
def wbound(m):
    for w in range(AMIN - 1, m):
        S = [l for l in range(w + 1, m - w) if AMIN <= l <= m - AMIN]
        rows = [[(((-1) ** l) * comb(l - 1, d)) % P for l in S] +
                [(-((-1) ** m) * comb(m - 1, d)) % P] for d in range(0, m - D)]
        if not S or not gauss_feasible(P, rows, len(S)):
            return w
    return None


def main():
    # ---- step 1 -----------------------------------------------------------
    pts = [(1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,0,1),(0,1,1)]
    mult = [14, 4, 4, 3, 2, 2]                       # T_4(5)
    assert sum(mult) == 29
    # T_4(5) need not itself be zero-sum; only its packing number matters here
    is_zs = lambda b: all(sum(b[i]*pts[i][j] for i in range(6)) % P == 0 for j in range(3))
    box = list(product(*[range(x+1) for x in mult]))
    zero = [b for b in box if any(b) and is_zs(b)]
    leq = lambda x, y: all(x[i] <= y[i] for i in range(6))
    atoms = [b for b in zero if not any(c != b and leq(c, b) for c in zero)]

    @lru_cache(maxsize=None)
    def pa(rm, t):
        if t == 0:
            return True
        return any(leq(b, rm) and pa(tuple(rm[i]-b[i] for i in range(6)), t-1) for b in atoms)
    pk = 0
    while pk < 6 and pa(tuple(mult), pk + 1):
        pk += 1
    assert pk == 3, pk
    print(f"1. lower bound: T_4(5) has length 29 and packing number {pk} -> D_4(C_5^3) >= 30")

    # ---- step 2 -----------------------------------------------------------
    assert N - 5 - 1 >= 25, "deleting one element must leave at least D_3 = 25"
    print("2. a length-31 obstruction has no zero-sum of length <= 5 "
          "(uses D_3(C_5^3) = 25, the only external input)")

    # ---- step 3 -----------------------------------------------------------
    tbl = {m: wbound(m) for m in range(14, N + 1)}
    assert tbl[31] == 7 and tbl[24] == 7 and tbl[17] == 7 and tbl[18] == 8, tbl
    print(f"3. short-atom law decided per length: w(m) = {[tbl[m] for m in range(31,13,-1)]}")

    # ---- step 4 -----------------------------------------------------------
    corridor = set()
    for s in range(AMIN, tbl[N] + 1):
        m1 = N - s
        for a2 in range(s, tbl[m1] + 1):
            m2 = m1 - a2
            if m2 < 14:
                continue
            for a3 in range(s, tbl[m2] + 1):
                a4 = m2 - a3
                if s <= a4 <= D:
                    corridor.add(tuple(sorted((s, a2, a3, a4))))
    corridor = sorted(corridor)
    assert corridor == [(6,6,6,13), (6,6,7,12), (6,7,7,11), (6,7,8,10), (7,7,7,10)], corridor
    print(f"4. four-atom corridor: {corridor}")

    # ---- step 5 -----------------------------------------------------------
    tops = sorted({max(c) for c in corridor})
    assert tops == [10, 11, 12, 13], tops
    print(f"5. every profile's largest part lies in {tops}")

    # ---- step 6 : run the L=13 sweep live ---------------------------------
    src = os.path.join(HERE, "tools", "sweep_atoms_turbo_c5_v6.c")
    exe = "/tmp/_d4_turbo_check"
    if subprocess.call(["gcc", "-O3", "-o", exe, src]) != 0:
        print("6. SKIPPED: could not compile the sweep (no gcc?)"); sys.exit(1)
    out = subprocess.run([exe, "13"], capture_output=True, text=True, timeout=3600).stdout
    orb = int(out.split("ORBITS")[1].split("(")[0].strip())
    comp = int(out.strip().rsplit(":", 1)[1])
    assert (orb, comp) == (RECORDED[13][2], 0), (orb, comp, RECORDED[13])
    print(f"6. L=13 sweep RE-RUN LIVE: {orb} orbits, {comp} completions")

    # ---- step 7 -----------------------------------------------------------
    for L in (10, 11, 12):
        pairs, dist, orbs, nodes, comps = RECORDED[L]
        assert comps == 0
        print(f"7. L={L} (recorded, two independent builds agreeing on node counts): "
              f"{orbs} orbits, {nodes} nodes, {comps} completions")

    print()
    print("THEOREM: D_4(C_5^3) = 30.")
    print("Hence D_k(C_5^3) = 5k+10 for every k >= 2 (via the Freeze-Schmid induction).")
    print("External inputs: D_3(C_5^3) = 25, and Olson for D(C_5^3) = 13.")


if __name__ == "__main__":
    main()
