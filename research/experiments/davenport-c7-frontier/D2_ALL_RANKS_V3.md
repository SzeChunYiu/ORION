# `D_2(C_p^r)` for every rank: a two-sided framework — V3

Status: **upper bound proved per `(p,r)` by an explicit `F_p` certificate (60 pairs verified, `2 ≤ r ≤ 11`, `5 ≤ p ≤ 23`); lower bound proved in general and verified by exact packing computations for `r ≤ 5`. The two sides meet exactly at `r = 2` and `r = 3` and leave a gap for `r ≥ 4`.** Priority CANNOT_CHECK from this host; the `r = 2, 3` values are donor-owned and the higher-rank statements have not been checked against the literature.
Tools: `tools/d2_rank_bounds_v3.py`, `tools/d2_rank_families_v3.py`.
Branch: `claude/orion-research-frontier-3ck9yt`.

Throughout `p` is prime, `G = C_p^r`, and `D = D(G) = r(p−1)+1` (Olson).

## 1. Upper bound

The argument of `D2_UNIFORM_SELFCONTAINED_THEOREM_V3.md` uses `r = 3` only in its arithmetic. In general: if `S` has `|S| = N−1` and no two disjoint nonempty zero-sums, then `T = S·(−σ(S))` is zero-sum of length `N` with packing number `≤ 2`, so by the atom-window lemma every proper nonempty zero-sum of `T` has length in `[N−D, D]`. Feeding that window into

    Σ_l (−1)^l N_l C(l,d) ≡ 0 (mod p)      (0 ≤ d ≤ N−D)

and solving over `F_p` either is consistent, or produces a certificate of infeasibility — and infeasibility means no such `S` exists, i.e. `D_2(G) ≤ N−1`.

**Theorem 1.** Let `N*(p,r)` be the least `N` for which the system is infeasible. Then `D_2(C_p^r) ≤ N*(p,r) − 1`. For every pair with `2 ≤ r ≤ p` that was tested (`r ≤ 11`, `p ≤ 23`, 60 pairs),

    N*(p,r) − 1  =  (3D+1)/2      if r is odd,
                    (3D+r−1)/2    if r is even.

For `r > p` the method degrades and returns a weaker bound (`r = 6,7` at `p = 5`; `r = 8,9` at `p = 7`), so the statement is confined to `r ≤ p`.

At `r = 2` and `r = 3` the bound is **exactly the known value**: `(3(2p−1)+1)/2 = 3p−1` and `(3(3p−2)+1)/2 = (9p−5)/2`. That agreement across six primes each is the method's validation; the `r ≥ 4` values are not known to this packet from any other source.

## 2. Lower bound: intersecting families

**Theorem 2.** Let `F` be a family of nonempty subsets of `[r]` that is **intersecting** (`A ∩ B ≠ ∅` for all `A,B ∈ F`), and let `m : F → Z_{≥0}` satisfy `Σ_{A ∋ i} m_A ≤ p` for every coordinate `i`. Write `v_A ∈ {0,1}^r` for the indicator of `A`. Then

    e_1^{p−1} ⋯ e_r^{p−1} · Π_{A ∈ F} v_A^{m_A}

has packing number 1. Consequently

    D_2(C_p^r) ≥ r(p−1) + M(r,p) + 1,    M(r,p) = max{ Σ_A m_A : F intersecting, Σ_{A ∋ i} m_A ≤ p }.

*Proof.* Every coordinate sum is `(p−1) + Σ_{A ∋ i} m_A ≤ 2p−1 < 2p`, so each coordinate contributes at most one multiple of `p` and can be used by at most one zero-sum block. A block using no `v_A` is `Π e_i^{a_i}` with every `a_i ≡ 0 (mod p)` and `a_i ≤ p−1`, hence empty; so every nonempty block's coordinate set contains some `A ∈ F` with `m_A > 0`. Two disjoint blocks would have disjoint coordinate sets, hence contain disjoint members of `F`, contradicting intersectingness. ∎

`M(r,p)` is `p` times the **fractional matching number** of the best intersecting family on `[r]`, subject to integrality — the Erdős–Ko–Rado / Füredi setting. It is what produces the halves:

| r | best family found | `ν*` | `M(r,p)` | resulting length | known `D_2 − 1` |
|---|---|---|---|---|---|
| 2 | single edge (star) | 1 | `p` | `3p−2` | `3p−2` ✔ tight |
| 3 | triangle | 3/2 | `(3p−1)/2` | `(9p−7)/2` | `(9p−7)/2` ✔ tight |
| 4 | triangle inside `[4]` | 3/2 | `(3p−1)/2` | `(11p−9)/2` | ? (upper bound `6p−4`) |
| 5 | triangle inside `[5]` | 3/2 | `(3p−1)/2` | `(13p−11)/2` | ? (upper bound `(15p−13)/2`) |

Verified by exact packing computation (`tools/d2_rank_families_v3.py`): every row has packing number exactly 1 at `p = 5` and `p = 7`, as does the 3-uniform family of all four 3-subsets of `[4]` (a weaker family, `ν* = 4/3`).

**The half-defect is `ν*(triangle) = 3/2`.** `CUBE_PACKING_PROFILE_V3.md` §5 traced the `(n−1)/2` in `D_2(C_n^3) = D + n + (n−1)/2` to the determinant-2 minor of the cube incidence matrix. Theorem 2 says the same thing combinatorially and more usefully: the extremal rank-3 configuration is the triangle `{12, 13, 23}` — the unique intersecting graph with fractional matching number above 1 — and the half is that number. The two readings agree, since the triangle's incidence matrix *is* the determinant-2 minor.

## 3. Where the two sides stand

| r | lower (Thm 2, best family found) | upper (Thm 1) | gap |
|---|---|---|---|
| 2 | `3p−1` | `3p−1` | **0** |
| 3 | `(9p−5)/2` | `(9p−5)/2` | **0** |
| 4 | `(11p−7)/2` | `6p−3` | `(p+1)/2` |
| 5 | `(13p−9)/2` | `(15p−11)/2` | `p−1` |

So `D_2(C_p^r)` is **determined at ranks 2 and 3 and bracketed for `r ≥ 4`**. Closing the gap needs either a better intersecting-family construction (the maximum of `ν*` over intersecting families is maximised by projective planes in the uniform case, with Füredi's bound `ν* ≤ k−1+1/k` for `k`-uniform), or a sharpening of the congruence system using more than the length spectrum.

A Fano-plane instance (`r = 7`, the seven lines, `ν* = 7/3`) is the natural next test of the lower bound; its exact packing computation exceeded the session's resource budget and is recorded as `CANNOT_CHECK_RESOURCE_BOUND`, not as a negative.

## Claim ceiling

The `r = 2` and `r = 3` values are donor-owned. Theorem 1's higher-rank instances are each proved by a finite certificate, but their novelty is unassessed, as is Theorem 2's. Nothing here is claimed to be new; the literature could not be reached from this host.
