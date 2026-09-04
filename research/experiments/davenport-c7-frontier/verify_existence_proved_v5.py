#!/usr/bin/env python3
"""Checker for OBSERVATION_D_EXISTENCE_PROVED_V5.md.

PROVES the EXISTENCE half of Observation D, uniformly in p: for each of the three
special pairs Z, an explicit dual exists, so Z is forced.

Ansatz: F_2 = 0, so G_j = F_0 + j F_1 is LINEAR in j, and F_0, F_1 are supported
on the two residues {0, h}, h = (p-3)/2.  Then P(jp+t) = F_0(t) + j F_1(t), and
the coefficients below are integers in s = (-1)^N (with s^2 = 1) that do NOT
depend on p:

    all three pairs:  F_0 = (-4-4s) d_0 + (-4-4s) d_h
    Z = {b,c}:        F_1 = (1+2s) d_0 + (4s) d_h
    Z = {a,c}:        F_1 = (-2+s) d_0 + (2+4s) d_h
    Z = {a,b}:        F_1 = (2s) d_0 + (1+4s) d_h

WHY THIS IS UNIFORM IN p.  Q(jp+t) involves G_j(t) and either G_{5-j}(h-t)
(t <= h) or G_{4-j}(p+h-t) (t > h).  Since F_0, F_1 vanish off {0,h}, a condition
is nontrivial only if t in {0,h} or the partner argument is in {0,h}.  For t <= h
the partner h-t lies in {0,h} exactly when t in {h,0}; for t > h the partner
p+h-t lies in {0,h} only for t = p or p+h, neither a residue.  So the only
nontrivial conditions are at jp+t with t in {0,h}, i.e. at
    p (not in the atom range), p+h = a, 2p = b, 2p+h = c.
Likewise P = 0 on [A,D] is automatic because that interval is j = 2 with
t in [h+2, p-2], which misses 0 and h.

So the whole verification is a FIXED, FINITE set of identities in s, independent
of p -- checked below for s = +1 and s = -1 -- plus the requirement that the
resulting values be nonzero mod p, which holds for every prime p >= 5.
"""
PAIRS = {
    "{b,c}": ((-4, -4), (-4, -4), (1, 2), (0, 4)),
    "{a,c}": ((-4, -4), (-4, -4), (-2, 1), (2, 4)),
    "{a,b}": ((-4, -4), (-4, -4), (0, 2), (1, 4)),
}
PRIMES = [n for n in range(5, 200)
          if all(n % q for q in range(2, int(n ** .5) + 1))]


def dual(p, coeffs):
    h = (p - 3) // 2; N = 5 * p + h; s = 1 if N % 2 == 0 else -1
    x0, xh, y0, yh = coeffs
    ev = lambda c: (c[0] + c[1] * s) % p
    F0 = lambda t: ev(x0) if t == 0 else (ev(xh) if t == h else 0)
    F1 = lambda t: ev(y0) if t == 0 else (ev(yh) if t == h else 0)
    G = lambda j, t: (F0(t) + j * F1(t)) % p
    P = lambda y: G(*divmod(y, p))

    def Q(y):
        j, t = divmod(y, p)
        return (G(j, t) + s * G(5 - j, h - t)) % p if t <= h else \
               (G(j, t) + s * G(4 - j, p + h - t)) % p
    return N, s, h, P, Q


def main():
    # ---- 1: the support argument that makes the check finite ---------------
    for p in PRIMES:
        h = (p - 3) // 2
        # for t <= h the partner is h-t; it hits {0,h} only at t in {h,0}
        assert {t for t in range(0, h + 1) if (h - t) in (0, h)} == ({0, h} if h else {0})
        # for t > h the partner p+h-t never hits {0,h}
        assert not {t for t in range(h + 1, p) if (p + h - t) in (0, h)}
        # the overlap interval [A,D] is j=2, t in [h+2,p-2], missing 0 and h
        assert 0 not in range(h + 2, p - 1) and h not in range(h + 2, p - 1)
    print(f"1. support argument verified for all {len(PRIMES)} primes 5..199: with "
          f"F_0, F_1 supported on {{0,h}}, the ONLY nontrivial conditions sit at "
          f"p+h, 2p, 2p+h, and P = 0 on [A,D] is automatic -- so the check is a "
          f"finite set of identities, independent of p")

    # ---- 2: the identities, for both signs, then over many primes ---------
    for nm, coeffs in PAIRS.items():
        for p in PRIMES:
            h = (p - 3) // 2
            a, b, c = p + h, 2 * p, 2 * p + h
            Z = {"{b,c}": {b, c}, "{a,c}": {a, c}, "{a,b}": {a, b}}[nm]
            N, s, h, P, Q = dual(p, coeffs)
            D = 3 * p - 2; A = N - D
            assert all(P(y) == 0 for y in range(A, D + 1)), (p, nm, "P on [A,D]")
            bad = [L for L in range(p + 1, D + 1) if L not in Z and Q(L)]
            assert not bad, (p, nm, bad[:5])
            assert Q(0), (p, nm, "Q(0) must be nonzero")
            assert all(Q(L) for L in Z), (p, nm, "Q must be nonzero on Z")
            assert all(Q(y) == (P(y) + s * P(N - y)) % p for y in range(N + 1)), (p, nm)
        print(f"2. Z = {nm:>7}: explicit dual valid for all {len(PRIMES)} primes 5..199 "
              f"-- P vanishes on [A,D], Q vanishes on the atom range off Z, and Q is "
              f"nonzero at 0 and at both lengths of Z")

    # ---- 3: Q(0) as an exact integer in s, and its divisibility ----------
    # N = (11p-3)/2 is even iff p = 1 mod 4, so s = +1 iff p = 1 mod 4.
    for p in PRIMES:
        N = (11 * p - 3) // 2
        assert (1 if N % 2 == 0 else -1) == (1 if p % 4 == 1 else -1), p
    print("3. parity fact: s = +1 exactly when p = 1 (mod 4), for every prime tested")

    for nm, coeffs in PAIRS.items():
        x0, xh, y0, yh = coeffs
        line = []
        for s in (1, -1):
            F00 = x0[0] + x0[1] * s          # F_0(0)
            F0h = xh[0] + xh[1] * s          # F_0(h)
            F1h = yh[0] + yh[1] * s          # F_1(h)
            q0 = F00 + s * (F0h + 5 * F1h)   # Q(0) = F_0(0) + s[F_0(h) + 5F_1(h)]
            # this branch occurs only for p = 1 mod 4 (s=+1) or p = 3 mod 4 (s=-1)
            bad = [q for q in PRIMES if q % 4 == (1 if s == 1 else 3) and q0 % q == 0]
            line.append(f"s={s:+d} -> Q(0) = {q0}, vanishing primes in that class: "
                        f"{bad if bad else 'none'}")
            assert not bad, (nm, s, q0, bad)
        print(f"   Z = {nm:>7}: " + " ; ".join(line))

    print("PASS: the existence half of Observation D is proved for all three "
          "special pairs, uniformly in p")


if __name__ == "__main__":
    main()
