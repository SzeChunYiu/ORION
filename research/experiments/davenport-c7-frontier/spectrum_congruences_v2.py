#!/usr/bin/env python3
"""Zero-sum length-spectrum congruences over C_p^r (Chevalley--Warning counting).

Classical fact (see SPECTRUM_CONGRUENCE_THEOREM_V2.md for the proof).  Let p be prime,
G = C_p^r, D = D(G) = r(p-1)+1, and T = g_1 ... g_N a sequence over G.  For every
multilinear polynomial h of degree d <= N - D and every c in G,

        sum_{I subset [N], sigma(I) = c} (-1)^{|I|} h(1_I) == 0   (mod p).

With c = 0 and h = e_d (elementary symmetric), writing N_l for the number of index
subsets I of size l with sigma(I) = 0 (so N_0 = 1, and N_N = 1 with N_l = N_{N-l} when T
is zero-sum):

        sum_l (-1)^l C(l, d) N_l == 0 (mod p),   0 <= d <= N - D.            (*)

This script decides, for a zero-sum sequence length N and a forbidden length window
[lo, hi] (closed under complementation), whether (*) admits ANY solution modulo p.  If it
does not, every zero-sum sequence of length N over C_p^r contains a zero-sum subsequence
whose length lies in the window.  When inconsistent, a human-checkable certificate
(lambda_d) is printed: sum_d lambda_d * (equation d) has zero left-hand side and nonzero
right-hand side modulo p.

Run without arguments to execute the frozen assertion suite used by the C_7^3 packet.
"""
import sys
from math import comb


def solve_mod_p(rows, p):
    """rows: list of (coeff dict var->int, rhs).  Returns (consistent, reduced rows, vars, certificate)."""
    vars_ = sorted({v for r, _ in rows for v in r})
    idx = {v: i for i, v in enumerate(vars_)}
    n = len(vars_)
    m = len(rows)
    # augmented with an identity block to track the row combination (certificate)
    A = []
    for i, (r, rhs) in enumerate(rows):
        row = [0] * (n + 1 + m)
        for v, c in r.items():
            row[idx[v]] = c % p
        row[n] = rhs % p
        row[n + 1 + i] = 1
        A.append(row)
    prow = 0
    for col in range(n):
        piv = next((i for i in range(prow, m) if A[i][col]), None)
        if piv is None:
            continue
        A[prow], A[piv] = A[piv], A[prow]
        inv = pow(A[prow][col], p - 2, p)
        A[prow] = [(x * inv) % p for x in A[prow]]
        for i in range(m):
            if i != prow and A[i][col]:
                f = A[i][col]
                A[i] = [(A[i][j] - f * A[prow][j]) % p for j in range(n + 1 + m)]
        prow += 1
        if prow == m:
            break
    consistent = True
    cert = None
    for i in range(m):
        if not any(A[i][:n]) and A[i][n]:
            consistent = False
            cert = A[i][n + 1:]
            break
    return consistent, A, vars_, cert


def spectrum_system(p, r, N, forbidden):
    D = r * (p - 1) + 1
    dmax = N - D
    allowed = [l for l in range(N + 1) if l not in forbidden]
    assert 0 in allowed and N in allowed
    rows = []
    for d in range(dmax + 1):
        coeffs = {}
        rhs = 0
        for l in allowed:
            c = ((-1) ** l) * comb(l, d)
            if l in (0, N):
                rhs -= c
            else:
                v = min(l, N - l)  # complement symmetry N_l = N_{N-l}
                coeffs[v] = coeffs.get(v, 0) + c
        rows.append((coeffs, rhs))
    return rows, dmax


def analyse(p, r, N, lo, hi, verbose=True):
    forbidden = set(range(lo, hi + 1)) | set(range(N - hi, N - lo + 1))
    rows, dmax = spectrum_system(p, r, N, forbidden)
    cons, A, vars_, cert = solve_mod_p(rows, p)
    if verbose:
        print(f"p={p} r={r} N={N} D={r*(p-1)+1} d<= {dmax} forbid lengths {lo}..{hi} (and complements): "
              f"consistent={cons}")
        if not cons:
            # verify certificate independently
            lam = cert
            lhs = {}
            rhs = 0
            for d, (coeffs, b) in enumerate(rows):
                for v, c in coeffs.items():
                    lhs[v] = (lhs.get(v, 0) + lam[d] * c) % p
                rhs = (rhs + lam[d] * b) % p
            assert all(x == 0 for x in lhs.values()) and rhs != 0
            print(f"   certificate lambda_d (d=0..{dmax}) = {lam}; combination gives 0 = {rhs} (mod {p})")
    return cons


def forced_residues(p, r, N, lo, hi):
    forbidden = set(range(lo, hi + 1)) | set(range(N - hi, N - lo + 1))
    rows, dmax = spectrum_system(p, r, N, forbidden)
    cons, A, vars_, cert = solve_mod_p(rows, p)
    out = {}
    if cons:
        n = len(vars_)
        for row in A:
            nz = [j for j in range(n) if row[j]]
            if len(nz) == 1 and row[nz[0]] == 1:
                out[vars_[nz[0]]] = row[n]
    return cons, out


def threshold(p, r, N):
    """Smallest k such that forbidding lengths 1..k (and complements) is inconsistent, i.e.
    every zero-sum sequence of length N over C_p^r has a zero-sum subsequence of length <= k."""
    for k in range(1, N // 2 + 1):
        if not analyse(p, r, N, 1, k, verbose=False):
            return k
    return None


def brute_force_check():
    """Cross-check (*) on an explicit small zero-sum sequence with index-subset counting."""
    from itertools import product
    p = 3
    pts = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 1, 1), (1, 1, 2), (2, 0, 1)]
    m = [2, 2, 2, 2, 2, 1]
    N = sum(m)
    Nl = [0] * (N + 1)
    for b in product(*[range(x + 1) for x in m]):
        if all(sum(b[i] * pts[i][j] for i in range(6)) % p == 0 for j in range(3)):
            w = 1
            for i in range(6):
                w *= comb(m[i], b[i])
            Nl[sum(b)] += w
    assert Nl[N] == 1, "example must be zero-sum"
    for d in range(N - 7 + 1):
        assert sum((-1) ** l * comb(l, d) * Nl[l] for l in range(N + 1)) % p == 0
    return Nl


if __name__ == "__main__":
    if len(sys.argv) == 6:
        p, r, N, lo, hi = map(int, sys.argv[1:])
        analyse(p, r, N, lo, hi)
        sys.exit(0)
    print("brute-force cross-check of (*) on a p=3 example:", brute_force_check())
    # --- D2 gate for C_7^3 (Theorem A): length-30 zero-sum sequences have a zero-sum of length <= 10
    assert not analyse(7, 3, 30, 1, 10)
    assert analyse(7, 3, 30, 1, 9)
    # --- D3 target (Theorem B): length-37 zero-sum sequences have a zero-sum of length <= 10, not provable <= 9 this way
    assert not analyse(7, 3, 37, 1, 10)
    assert analyse(7, 3, 37, 1, 9)
    # --- same route for p=5, 11, 13 at N = (9p-3)/2 with window [1,(3p-1)/2]
    for p in (5, 11, 13):
        assert not analyse(p, 3, (9 * p - 3) // 2, 1, (3 * p - 1) // 2)
    # --- p=3: the route is silent (consistent), matching the Lucas degeneration a_2 = 0 mod 3
    assert analyse(3, 3, 12, 1, 4)
    # --- p=5 D3 analogue: length-26 zero-sum sequences over C_5^3 have a zero-sum of length <= 7
    assert not analyse(5, 3, 26, 1, 7)
    assert analyse(5, 3, 26, 1, 6)
    # --- residual near-extremal windows stay consistent (so the symmetric congruences alone do not close D3)
    for N, hi in ((29, 9), (28, 8), (27, 7)):
        assert analyse(7, 3, N, 1, hi)
    print("forced residues for p=7 N=29 forbid 1..9:", forced_residues(7, 3, 29, 1, 9))
    print("threshold table k(N) for C_7^3 (every zero-sum sequence of length N has a zero-sum of length <= k):")
    print({N: threshold(7, 3, N) for N in range(20, 41)})
    print("threshold table for C_5^3:")
    print({N: threshold(5, 3, N) for N in range(14, 31)})
    print("PASS: spectrum congruence assertion suite")
