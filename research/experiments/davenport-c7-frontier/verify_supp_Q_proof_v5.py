#!/usr/bin/env python3
"""Checker for SUPP_Q_PROVED_V5.md.

PROVES  supp Q subset S  for Z a pair of special lengths, closing the claim left
open by DUAL_SUPPORT_TWELVE_POINTS_V5.md.

Set G_j(t) := P(jp + t).  Because deg P <= A = N-D = 2p+h+2 < 3p, Lucas gives
G_j = F_0 + j F_1 + C(j,2) F_2, so the third difference in j vanishes:

    G_{j+3} - 3G_{j+2} + 3G_{j+1} - G_j = 0,

hence G_3 = 3G_2-3G_1+G_0,  G_4 = 6G_2-8G_1+3G_0,  G_5 = 10G_2-15G_1+6G_0.

With s = (-1)^N and N = 5p+h, the point jp+t pairs with (5-j)p+(h-t) when t <= h
and with (4-j)p+(p+h-t) when t > h, so

    Q(jp+t) = G_j(t) + s G_{5-j}(h-t)      (t <= h)
    Q(jp+t) = G_j(t) + s G_{4-j}(p+h-t)    (t >  h).

The two identities below are pure algebra in the G's (checked exactly, both signs):

 (VI)  G_5(x) + s G_0(h-x) = 3[G_4(x)+s G_1(h-x)] - 3[G_3(x)+s G_2(h-x)] + [G_2(x)+s G_3(h-x)]
 (VII) G_4(u) + s G_0(w)   = 3[G_3(u)+s G_1(w)]   - 3[G_2(u)+s G_2(w)]   + [G_1(u)+s G_3(w)]

Each bracket is Q at a point of the atom range, i.e. an imposed condition.  So Q
vanishes on the two bottom intervals, which by FACT 1 of
DUAL_SUPPORT_REDUCTION_V5.md is exactly supp Q subset S.

The checker below does not take the hand derivation on trust: it builds the
linear span of the imposed conditions over F_p in the 3p unknowns
(G_0(t), G_1(t), G_2(t)) and verifies that every target form lies in it.
"""
PRIMES = (11, 13, 17, 19, 23, 29, 31, 37)

COEF = {0: (1, 0, 0), 1: (0, 1, 0), 2: (0, 0, 1),
        3: (1, -3, 3), 4: (3, -8, 6), 5: (6, -15, 10)}


def algebra_identities():
    """The two identities, exactly, over the integers, for both signs."""
    def G(j, off):
        v = [0] * 6; v[off], v[off+1], v[off+2] = COEF[j]; return v
    X = lambda j: G(j, 0); Y = lambda j: G(j, 3)
    add = lambda *vs: [sum(t) for t in zip(*vs)]
    mul = lambda k, v: [k * x for x in v]
    for j in range(3):
        assert add(X(j+3), mul(-3, X(j+2)), mul(3, X(j+1)), mul(-1, X(j))) == [0]*6
    for s in (1, -1):
        assert add(X(5), mul(s, Y(0))) == add(
            mul(3, add(X(4), mul(s, Y(1)))), mul(-3, add(X(3), mul(s, Y(2)))),
            add(X(2), mul(s, Y(3)))), s
        assert add(X(4), mul(s, Y(0))) == add(
            mul(3, add(X(3), mul(s, Y(1)))), mul(-3, add(X(2), mul(s, Y(2)))),
            add(X(1), mul(s, Y(3)))), s


def form(p, j, t, s):
    """Q(jp+t) as a vector in the 3p unknowns G_0(.),G_1(.),G_2(.)."""
    h = (p - 3) // 2
    v = [0] * (3 * p)
    for i, c in enumerate(COEF[j]):
        v[i * p + t] = (v[i * p + t] + c) % p
    if t <= h:
        jj, tt = 5 - j, h - t
    else:
        jj, tt = 4 - j, p + h - t
    for i, c in enumerate(COEF[jj]):
        v[i * p + tt] = (v[i * p + tt] + s * c) % p
    return v


def in_span(p, rows, target):
    M = [r[:] for r in rows] + [target[:]]
    n = len(M[0]); piv = 0
    for c in range(n):
        r = next((i for i in range(piv, len(rows)) if M[i][c] % p), None)
        if r is None:
            continue
        M[piv], M[r] = M[r], M[piv]
        iv = pow(M[piv][c], p - 2, p); M[piv] = [x * iv % p for x in M[piv]]
        for i in range(len(M)):
            if i != piv and M[i][c] % p:
                f = M[i][c]; M[i] = [(M[i][j] - f * M[piv][j]) % p for j in range(n)]
        piv += 1
    return not any(M[-1][c] % p for c in range(n))


def main():
    algebra_identities()
    print("1. the third-difference law and identities (VI), (VII) hold exactly over "
          "the integers, for both s = +1 and s = -1")

    for p in PRIMES:
        h = (p - 3) // 2; N = 5 * p + h; D = 3 * p - 2; A = N - D
        s = 1 if N % 2 == 0 else -1
        a, b, c = 3 * (p - 1) // 2, 2 * p, (5 * p - 3) // 2
        assert {a, b, c} == {p + h, 2 * p, 2 * p + h}
        for Z in ({b, c}, {a, c}, {a, b}):
            rows = []
            # (i) P = 0 on [A, D]: digits (2, t), t in [h+2, p-2]  =>  G_2(t) = 0
            for t in range(h + 2, p - 1):
                v = [0] * (3 * p); v[2 * p + t] = 1; rows.append(v)
            # Q(L) = 0 for L in the atom range, L not in Z
            for L in range(p + 1, D + 1):
                if L in Z:
                    continue
                rows.append(form(p, L // p, L % p, s))
            # targets: Q on the two bottom intervals
            targets = [form(p, 0, y, s) for y in range(1, p) if y != h]
            for tg in targets:
                assert in_span(p, rows, tg), (p, sorted(Z))
        print(f"2. p={p:>3}: for each of the three special pairs, EVERY target form "
              f"Q(y), y in [1,h-1] u [h+1,p-1], lies in the span of the imposed "
              f"conditions -- so Q vanishes there and supp Q is inside S")

    print("PASS: supp Q subset S is proved for special pairs; the identities are "
          "exact and the span check confirms every range condition is available")


if __name__ == "__main__":
    main()
