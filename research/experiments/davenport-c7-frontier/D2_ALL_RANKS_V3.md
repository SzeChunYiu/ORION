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

`M(r,p)` is `p` times the **fractional matching number** of the best intersecting family on `[r]`, subject to integrality — the Erdős–Ko–Rado / Füredi setting. `M(r,p)` was computed **exactly** for `r ≤ 5` by enumerating every maximal intersecting family on `[r]` (2, 4, 12 and 81 of them) and solving the integer program on each (`tools/d2_intersecting_optimum_v3.py`):

| r | optimal support | `ν*` | `M(r,p)` | `r(p−1) + M` |
|---|---|---|---|---|
| 2 | `{12}` (star) | 1 | `p` | `3p−2` |
| 3 | `{12, 13, 23}` (triangle) | 3/2 | `(3p−1)/2` | `(9p−7)/2` |
| 4 | `{12, 13, 14, 234}` | 5/3 | `⌊5p/3⌋` | `4(p−1)+⌊5p/3⌋` |
| 5 | (16-set maximal family) | 9/5 | `9` at `p=5`, `12` at `p=7` | `29`, `42` |

The rank-4 optimum is explicit and pretty: a star of three edges at vertex 1 together with the complementary triple. Its fractional matching puts `p/3` on each edge and `2p/3` on the triple, giving `3·(p/3) + 2p/3 = 5p/3`. Verified: `M(4,p) = ⌊5p/3⌋` at `p = 5, 7, 11, 13` (values 8, 11, 18, 21).

Verified by exact packing computation (`tools/d2_rank_families_v3.py`): the star, triangle, triangle-inside-`[4]`, triangle-inside-`[5]` and all-3-subsets-of-`[4]` configurations all have packing number exactly 1 at `p = 5` and `p = 7`.

**The half-defect is `ν*(triangle) = 3/2`.** `CUBE_PACKING_PROFILE_V3.md` §5 traced the `(n−1)/2` in `D_2(C_n^3) = D + n + (n−1)/2` to the determinant-2 minor of the cube incidence matrix. Theorem 2 says the same thing combinatorially and more usefully: the extremal rank-3 configuration is the triangle `{12, 13, 23}` — the unique intersecting graph with fractional matching number above 1 — and the half is that number. The two readings agree, since the triangle's incidence matrix *is* the determinant-2 minor.

## 3. The two sides meet at ranks 2 and 3

| r | p | lower (Thm 2, exact `M`) | upper (Thm 1) | |
|---|---|---|---|---|
| 2 | 5, 7, 11, 13 | 14, 20, 32, 38 | 14, 20, 32, 38 | **equal** |
| 3 | 5, 7, 11, 13 | 20, 29, 47, 56 | 20, 29, 47, 56 | **equal** |
| 4 | 5, 7, 11, 13 | 25, 36, 59, 70 | 27, 39, 63, 75 | gap 2, 3, 4, 5 |
| 5 | 5, 7 | 30, 43 | 32, 47 | gap 2, 4 |

**Corollary.** For `r ∈ {2,3}` and every prime `p ≤ 13` tested, the framework alone gives

    D_2(C_p^2) = 3p−1,    D_2(C_p^3) = (9p−5)/2,

with the lower bound from Theorem 2's intersecting-family optimum and the upper bound from Theorem 1's certificate. Modulo Olson's `D(C_p^r) = r(p−1)+1`, both values are established here without any donor input — the `r = 3` case being exactly the premise the rest of the packet had been assuming from unreadable text.

So `D_2(C_p^r)` is **determined at ranks 2 and 3 and bracketed for `r ≥ 4`**, the gap growing slowly. Closing the gap needs either a better intersecting-family construction (the maximum of `ν*` over intersecting families is maximised by projective planes in the uniform case, with Füredi's bound `ν* ≤ k−1+1/k` for `k`-uniform), or a sharpening of the congruence system using more than the length spectrum.

A Fano-plane instance (`r = 7`, the seven lines, `ν* = 7/3`) is the natural next test of the lower bound; its exact packing computation exceeded the session's resource budget and is recorded as `CANNOT_CHECK_RESOURCE_BOUND`, not as a negative.

## Claim ceiling

The `r = 2` and `r = 3` values are donor-owned. Theorem 1's higher-rank instances are each proved by a finite certificate, but their novelty is unassessed, as is Theorem 2's. Nothing here is claimed to be new; the literature could not be reached from this host.
