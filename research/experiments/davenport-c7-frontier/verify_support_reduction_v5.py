#!/usr/bin/env python3
"""Checker for DUAL_SUPPORT_REDUCTION_V5.md.

Shrinks the one remaining gap in Observation D -- the claim supp Q subset S --
to a statement about two short intervals in the bottom base-p block.

FACT 1 (proved, interval arithmetic).  Q vanishes on the atom range [p+1, 3p-2]
off Z, hence by the symmetry Q(N-y) = (-1)^N Q(y) also on
sigma([p+1,3p-2]) = [2p+h+2, 4p+h-1] off sigma(Z).  Those intervals overlap,
because 2p+h+2 <= 3p-1 for p >= 3.  So Q vanishes on the single interval
[p+1, 4p+h-1] off Z u sigma(Z), whence

    supp Q  subset  [0,p]  u  (Z u sigma Z)  u  [4p+h, N].

S n [0,p] = {0,h,p}, and the top block is the sigma-image of the bottom, so

    supp Q subset S     <=>     Q vanishes on [1,h-1] u [h+1,p-1].

FACT 2 (proved, Lucas).  deg P <= A = N-D = 2p+h+2 < 3p, so writing
y = y1*p + y0 and d = d1*p + d0,

    P(y) = F_0(y0) + y1*F_1(y0) + C(y1,2)*F_2(y0),

with F_0, F_1 arbitrary functions on F_p and F_2 of degree <= h+2 -- the degree
cap bites only in the d1 = 2 block.  On the bottom block P = F_0, so the
remaining claim is a relation among F_0, F_1, F_2 at paired residues.
"""
from math import comb, factorial

PRIMES = (11, 13, 17, 19, 23)


def bp(n, k):
    if k < 0:
        return 0
    r = 1
    for i in range(k):
        r *= (n - i)
    return r // factorial(k)


def duals(p, Z):
    N = (11 * p - 3) // 2; D = 3 * p - 2; amin = p + 1; sgn = (-1) ** N
    A = N - D; hh = D - A + 1
    ds = list(range(hh, A + 1))
    Pb = lambda d, y: bp(y - A, d) % p
    Ls = [L for L in range(amin, D + 1) if L not in Z]
    M = [[(Pb(d, L) + sgn * Pb(d, N - L)) % p for d in ds] for L in Ls]
    nr, nc = len(M), len(ds); piv = []; r = 0
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
        out.append(([(Pv(y) + sgn * Pv(N - y)) % p for y in range(N + 1)], Pv))
    return N, A, sgn, out


def main():
    # ---- FACT 1: the interval arithmetic, for a wide range of primes ------
    prs = [n for n in range(5, 400) if all(n % q for q in range(2, int(n ** .5) + 1))]
    for p in prs:
        h = (p - 3) // 2; N = 5 * p + h
        assert N == (11 * p - 3) // 2
        assert 2 * p + h + 2 <= 3 * p - 1, p          # the two intervals overlap
        assert N - (3 * p - 2) == 2 * p + h + 2, p    # sigma of the atom range, left end
        assert N - (p + 1) == 4 * p + h - 1, p        # ... right end
        S = {j * p for j in range(6)} | {j * p + h for j in range(6)}
        assert {x for x in S if x <= p} == {0, h, p}, p
    print(f"1. FACT 1 verified for all {len(prs)} primes 5..397: the atom range and "
          f"its sigma-image overlap and cover [p+1, 4p+h-1], and S n [0,p] = {{0,h,p}} "
          f"-- so 'supp Q subset S' reduces to 'Q = 0 on [1,h-1] u [h+1,p-1]'")

    # ---- FACT 2: the Lucas parametrisation --------------------------------
    import random
    random.seed(5)
    for p in (11, 13, 17):
        N = (11 * p - 3) // 2; A = N - (3 * p - 2); h = (p - 3) // 2
        assert A == 2 * p + h + 2, (p, A)
        caps = {d1: max((d % p for d in range(A + 1) if d // p == d1), default=None)
                for d1 in (0, 1, 2)}
        assert caps[0] == p - 1 and caps[1] == p - 1 and caps[2] == h + 2, (p, caps)
        lam = {d: random.randrange(p) for d in range(A + 1)}
        direct = lambda y: sum(lam[d] * bp(y, d) for d in range(A + 1)) % p
        split = lambda y: sum(lam[d] * comb(y // p, d // p) * comb(y % p, d % p)
                              for d in range(A + 1)
                              if d // p <= y // p and d % p <= y % p) % p
        assert all(direct(y) == split(y) for y in range(N + 1)), p
    print("2. FACT 2 verified: A = 2p+h+2, the per-block degree caps are "
          "(p-1, p-1, h+2), and the Lucas split P = F_0 + y_1 F_1 + C(y_1,2) F_2 "
          "reproduces P exactly on every point")

    # ---- the reduction is faithful ----------------------------------------
    for p in PRIMES:
        h = (p - 3) // 2
        a, b, c = 3 * (p - 1) // 2, 2 * p, (5 * p - 3) // 2
        S = {j * p for j in range(6)} | {j * p + h for j in range(6)}
        for Z in ({b, c}, {a, c}, {a, b}):
            N, A, sgn, out = duals(p, Z)
            for Q, _ in out:
                if not Q[0]:
                    continue
                sup = {y for y in range(N + 1) if Q[y]}
                inside = sup <= S
                bottom_clean = all(Q[y] == 0 for y in range(1, p) if y != h)
                assert inside == bottom_clean, (p, sorted(Z), inside, bottom_clean)
                assert inside, (p, sorted(Z))
        print(f"3. p={p:>3}: for every dual, 'supp Q subset S' and 'Q = 0 on the two "
              f"bottom intervals' are the SAME condition, and both hold")

    print("PASS: the remaining gap is exactly Q = 0 on [1,h-1] u [h+1,p-1]")


if __name__ == "__main__":
    main()
