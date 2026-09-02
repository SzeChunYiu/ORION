#!/usr/bin/env python3
"""ORION-02 successor: exact integer-DP optimizer for profile-Kmin and its
asymptotic law (asymptotics-kmin-v1).

Parent (frozen, certified 10/10 vs exhaustive search): `../verify_c2c10_profile.py`.
Every cost quantity there is a dyadic rational whose denominator divides
2^(m-2) (L = 1), so in pure Python integers this module computes Kmin EXACTLY
at sizes where the float harness loses precision (>= ~m=51, G > 2^53) and
infeasible partition enumeration (>= ~m=66, p(66) ~ 2.3M with per-profile
inner loops). The maximizing profile is found by DP over
(covered size, #variable blocks, running max-b) instead of enumeration.

Decomposition (exactness argument, mirrors profile_cost):
  C(profile) = 2m+k-3 + anchor_term(a) + df(a) + [sum over variable blocks of
  (var_term(s) + df(s))] + max(b(all blocks)),
with k = 1 + #variable blocks. The anchor is the first block of its size
class; costs are permutation-symmetric, so designating one block of size a
as anchor + a multiset of variable blocks covering m - a covers every
(anchor class, profile) pair exactly. Variable blocks have s <= m-2
(f = N/2^s integer); the single profile with a size-q = m-1 variable block is
(1, q), handled by an explicit boundary family (f = eps*L in {0,1}).

Usage:
  python3 kmin_asymptotics_v1.py validate 5 48    # vs frozen float harness
  python3 kmin_asymptotics_v1.py law 49 140       # exact table + gamma* + profile
"""
from __future__ import annotations

import sys
from functools import lru_cache

sys.setrecursionlimit(10000)


@lru_cache(maxsize=None)
def bf(s: int) -> int:
    """ceil(log2 s) with bf(1) = 0 — frozen harness definition."""
    if s == 1:
        return 0
    v = 0
    while (1 << v) < s:
        v += 1
    return v


@lru_cache(maxsize=None)
def df(s: int) -> int:
    return 0 if s == 1 else df((s + 1) // 2) + df(s // 2) + s - 2


def var_term(s: int, m: int) -> int:
    """Variable-block cost term, exact integer (requires s <= m-2)."""
    N = 1 << (m - 2)
    w = s * (N >> 1)
    f = N >> s
    return 2 * f + (bf(s) + 2) * (w - s * f)


def anchor_term(s: int, m: int) -> int:
    """Anchor-block cost term, exact integer (anchor of size s <= m-1)."""
    N = 1 << (m - 2)
    w = N + (s - 1) * (N >> 1)
    f = N >> (s - 1)
    return 2 * f + (bf(s) + 2) * (w - s * f)


def c_one(m: int, eps: int) -> int:
    """Cost of the one-block profile, exact integer (L = 1)."""
    N = 1 << (m - 2)
    W = (m + 1) * (N >> 1)
    b, d = bf(m), df(m)
    return (b + 1) * W + (m - 1) + d + b - (m * (b + 1) - 1) * eps


def dp_variable(m: int, maxn: int):
    """dp[j] = {(kv, mb): (cost, last_s)}: minimum of
    sum(var_term + df) over multisets of variable blocks with sizes in
    1..m-2 covering exactly j, with kv blocks and running max bf = mb.
    last_s records a realizing final block for profile recovery."""
    dp = [dict() for _ in range(maxn + 1)]
    dp[0] = {(0, 0): (0, 0)}
    for j in range(1, maxn + 1):
        best: dict[tuple[int, int], tuple[int, int]] = {}
        for s in range(1, min(j, m - 2) + 1):
            ts = var_term(s, m) + df(s)
            bs = bf(s)
            for (kv, mb), (c, _) in dp[j - s].items():
                key = (kv + 1, mb if mb >= bs else bs)
                nc = c + ts
                cur = best.get(key)
                if cur is None or nc < cur[0]:
                    best[key] = (nc, s)
        dp[j] = best
    return dp


def recover(dp, j: int, kv: int, mb: int) -> list[int]:
    """Recover one realizing multiset of variable blocks by walking last_s."""
    out = []
    while kv > 0:
        _, s = dp[j][(kv, mb)]
        out.append(s)
        bs = bf(s)
        mb_prev = mb if mb > bs else bs  # mb = max(mb_prev, bs)
        # candidate previous mb: any value with max(value, bs) == mb
        found = None
        for (kv2, mb2), (c2, _) in dp[j - s].items():
            if kv2 == kv - 1 and (mb2 if mb2 >= bs else bs) == mb:
                if found is None or c2 < found[1]:
                    found = (mb2, c2)
        assert found is not None, "profile recovery failed"
        j, kv, mb = j - s, kv - 1, found[0]
    out.reverse()
    return out


def kmin_dp(m: int) -> tuple[int, tuple | None]:
    """Exact profile-Kmin (L = 1), mirrors kmin_profile(m, 1) of the frozen
    harness: max over eps, anchor classes, k >= 2 profiles of
    floor(G/(2k-1)) + 1 for G = C_one - C(profile) > 0."""
    dp = dp_variable(m, m - 1)
    q = m - 1
    best, best_prof = 0, None
    for eps in (0, 1):
        C1 = c_one(m, eps)
        for a in range(1, m):
            rem = m - a
            a_term, a_d, a_b = anchor_term(a, m), df(a), bf(a)
            for (kv, mb), (cost, _) in dp[rem].items():
                if kv < 1:
                    continue
                k = kv + 1
                Cpi = (2 * m + k - 3) + a_term + a_d + cost + max(mb, a_b)
                G = C1 - Cpi
                if G > 0:
                    t = G // (2 * k - 1) + 1
                    if t > best:
                        best = t
                        blocks = sorted(recover(dp, rem, kv, mb), reverse=True)
                        best_prof = (tuple(blocks), a, eps)
            if a == 1 and m >= 4:
                # boundary family: profile (1, q), anchor on the 1-block,
                # q-block is a pure-variable block (f = eps*L, L = 1)
                k = 2
                N = 1 << (m - 2)
                w = q * (N >> 1)
                bterm = 2 * eps + (bf(q) + 2) * (w - q * eps)
                Cpi = ((2 * m + k - 3) + anchor_term(1, m) + 0
                       + bterm + df(q) + max(bf(q), 0))
                G = C1 - Cpi
                if G > 0:
                    t = G // (2 * k - 1) + 1
                    if t > best:
                        best = t
                        best_prof = ((q,), 1, eps)
    return best, best_prof


def gamma(m: int, kmin: int) -> float:
    """gamma*(m) = Kmin / N = Kmin / 2^(m-2), 12-digit exact ratio."""
    return kmin * 10**12 // (1 << (m - 2)) / 10**12


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "validate"
    if mode == "validate":
        lo, hi = int(sys.argv[2]), int(sys.argv[3])
        sys.path.insert(0, str(__file__).rsplit("/", 1)[0] + "/..")
        import verify_c2c10_profile as harness
        ok = True
        for m in range(lo, hi + 1):
            want, _ = harness.kmin_profile(m, 1)
            got, _ = kmin_dp(m)
            match = got == want
            ok = ok and match
            print(f"m={m:3d}: dp={got} harness={want:.0f} "
                  f"{'OK' if match else 'MISMATCH'}", flush=True)
        print("ALL MATCH" if ok else "FAILURE")
        return 0 if ok else 1
    if mode == "law":
        lo, hi = int(sys.argv[2]), int(sys.argv[3])
        print("m     b(m)  Kmin(exact)                      gamma*=Kmin/N   "
              "gamma*/2^b  profile(anchor,eps)")
        for m in range(lo, hi + 1):
            got, prof = kmin_dp(m)
            g = gamma(m, got)
            b = bf(m)
            print(f"{m:4d}  {b:3d}  {got:<32d} {g:14.6f} "
                  f"{g / (1 << b):9.5f}  {prof}", flush=True)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
