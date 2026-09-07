#!/usr/bin/env python3
"""Independent recomputation of the binary-cube packing profile of CUBE_PACKING_PROFILE_V3.md.

For odd n it computes, over the full box [0,n-1]^7 of multiplicity vectors on the seven nonzero
points of {0,1}^3 in C_n^3:

    c_j(n) = max{ |m| : pk(m) <= j },        z_j(n) = max{ |m| : m zero-sum, pk(m) <= j }

by (i) enumerating minimal zero-sum sub-multisets (atoms) of the full box, then (ii) a forward
dynamic programme pk(m) = 1 + max{ pk(m - a) : a atom, a <= m } over the box in mixed-radix order.
This is written independently of tools/cube_profile_v3.c (different language, different data
layout, atoms found by minimality filtering rather than by the H-flag recursion).

Default run: n = 3 and n = 5 plus the family checks (a few seconds).  `--slow` adds n = 7.
Exit code 0 iff every asserted value matches the closed forms of the record.
"""
import sys
from itertools import product

Q = ((1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,0,1),(0,1,1),(1,1,1))

FORMULAS = {                      # j -> (c_j(n), z_j(n)) as functions of odd n
    0: (lambda n: 3*n-3,      None),
    1: (lambda n: (9*n-7)//2, lambda n: 3*n-2),
    2: (lambda n: (11*n-7)//2, lambda n: (9*n-5)//2),
    3: (lambda n: 6*n-4,      lambda n: 5*n-3),
    4: (lambda n: 7*n-7,      lambda n: 6*n-3),
}


def profile(n):
    """Return (c, z, pk_full) where c[j], z[j] are the maxima defined above."""
    cap = n - 1
    radix = [cap + 1] * 7
    R = [1] * 8
    for i in range(7):
        R[i+1] = R[i] * radix[i]
    NS = R[7]

    def digits(idx):
        out = []
        for i in range(7):
            out.append(idx % radix[i]); idx //= radix[i]
        return out

    zs = bytearray(NS); length = bytearray(NS)
    for idx in range(NS):
        d = digits(idx)
        length[idx] = sum(d)
        zs[idx] = 1 if all(sum(d[i]*Q[i][j] for i in range(7)) % n == 0 for j in range(3)) else 0
    zs[0] = 0

    # atoms: zero-sum vectors with no proper nonempty zero-sum sub-vector.
    # A vector has one iff some one-step-smaller vector is zero-sum or itself has one.
    has = bytearray(NS)
    atoms = []
    for idx in range(NS):
        d = digits(idx)
        h = 0
        for i in range(7):
            if d[i]:
                j = idx - R[i]
                if zs[j] or has[j]:
                    h = 1; break
        has[idx] = h
        if idx and zs[idx] and not h:
            atoms.append((idx, tuple(d)))

    pk = bytearray(NS)
    for idx in range(NS):
        d = digits(idx)
        best = 0
        for a_idx, a in atoms:
            if a_idx > idx:
                break
            ok = True
            for i in range(7):
                if a[i] > d[i]:
                    ok = False; break
            if not ok:
                continue
            v = 1 + pk[idx - a_idx]
            if v > best:
                best = v
        pk[idx] = best

    c = {}; z = {}
    for idx in range(NS):
        j = pk[idx]; L = length[idx]
        if L > c.get(j, -1): c[j] = L
        if zs[idx] and L > z.get(j, -1): z[j] = L
    # make them cumulative maxima (pk <= j, not = j)
    cc = {}; zz = {}; rc = -1; rz = -1
    for j in range(5):
        rc = max(rc, c.get(j, -1)); rz = max(rz, z.get(j, -1))
        cc[j] = rc; zz[j] = rz
    return cc, zz, pk[NS-1], len(atoms)


def packing_number(n, pts, m):
    """Exact packing number of one multiplicity vector (used for the family checks)."""
    from functools import lru_cache
    k = len(pts)
    def is_zs(b): return all(sum(b[i]*pts[i][j] for i in range(k)) % n == 0 for j in range(3))
    zero = [b for b in product(*[range(x+1) for x in m]) if any(b) and is_zs(b)]
    leq = lambda a, b: all(a[i] <= b[i] for i in range(k))
    atoms = [b for b in zero if not any(o != b and leq(o, b) for o in zero)]
    @lru_cache(maxsize=None)
    def pack(r, t):
        if t == 0: return True
        return any(leq(b, r) and pack(tuple(r[i]-b[i] for i in range(k)), t-1) for b in atoms)
    j = 0
    while pack(tuple(m), j+1): j += 1
    return j


def families(n):
    """The conjectured extremal families S_2, S_3, S_4 (see DK_ARITHMETIC_CONJECTURE_V3.md)."""
    a, hi, lo = n-1, (n+1)//2, (n-1)//2
    return [
        ("S_2", list(Q[:6]),            [a,a,a,hi,lo,lo],          1, (9*n-7)//2),
        ("S_3", list(Q),                [a,a,a,a,hi,lo,hi],        2, (11*n-7)//2),
        ("S_4", list(Q)+[(1,1,2)],      [a,a,a,a,hi,lo,a,(n+3)//2],3, (13*n-7)//2),
    ]


def main():
    slow = "--slow" in sys.argv
    ns = [3, 5] + ([7] if slow else [])
    for n in ns:
        c, z, full, na = profile(n)
        print(f"n={n}: atoms={na} pk(full cube)={full}")
        for j in range(5):
            cf, zf = FORMULAS[j]
            got_c = c.get(j); got_z = z.get(j)
            print(f"   c_{j}={got_c:4d} (formula {cf(n):4d})   z_{j}={got_z:4d}"
                  + (f" (formula {zf(n):4d})" if zf else "   [no zero-sum with pk=0]"))
            assert got_c == cf(n) or (n == 3 and j >= 3), (n, j, got_c, cf(n))
            if zf and not (n == 3 and j == 4):
                assert got_z == zf(n), (n, j, got_z, zf(n))
        assert full == (3 if n == 3 else 4)
    for n in ns + ([9] if slow else []):
        for name, pts, m, want, L in families(n):
            assert sum(m) == L, (n, name)
            got = packing_number(n, pts, m)
            print(f"n={n} {name}: len={sum(m)} pk={got} (target {want})")
            assert got == want, (n, name, got, want)
    print("PASS: binary-cube packing profile and extremal families match the record")


if __name__ == "__main__":
    main()
