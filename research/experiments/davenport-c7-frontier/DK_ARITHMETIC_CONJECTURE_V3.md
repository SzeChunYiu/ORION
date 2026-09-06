# `D_k(C_n^3)` is arithmetic from `k = 2` with a half-defect — V3

Status: **the lower bound is now a theorem for all `k` and all odd `n`** (`GENERAL_LOWER_BOUND_AND_ETA_INDUCTION_V3.md`, Theorem 1, family `T_k(n)`); the matching upper bound is a conjecture, proved for `C_3^3` (all `k`), for `k = 2` at `n = 3, 5, 7` and prime powers `p^a, p ≥ 5`, and for `k = 3` at `n = 3, 5`. Priority: CANNOT_CHECK — the donor literature could not be read from this host (ledger row C7-DONOR-1), and the `k = 2` case and the general inequality `D_{k+1} ≥ D_k + exp` are certainly donor-owned. No novelty is claimed.
Branch: `claude/orion-research-frontier-3ck9yt`.

## The statement

**Conjecture.** For every odd `n ≥ 3` and every `k ≥ 2`,

    D_k(C_n^3) = ((2k+5)n − 5)/2.

Equivalently, writing `D = D(C_n^3) = 3n−2` (Olson, for `n` a prime power) and `exp = n`,

    D_k(C_n^3) = D(C_n^3) + (k−1)·exp(C_n^3) + (n−1)/2       for all k ≥ 2,

i.e. the sequence `(D_k)_{k≥2}` is an arithmetic progression of difference `exp(G)` — the eventual behaviour proved in general by Freeze–Schmid — which begins already at `k = 2`, and which sits **exactly `(n−1)/2` above** the naive value `D(G) + (k−1)exp(G)`. The defect `(n−1)/2` is independent of `k`.

## Status of the two halves

**Lower bound — proved.** For every odd `n` and every `k ≥ 2`,

    T_k(n) = e_1^{(k−1)n−1} e_2^{n−1} e_3^{n−1} e_12^{(n+1)/2} e_13^{(n−1)/2} e_23^{(n−1)/2}

has length `((2k+5)n−7)/2` and packing number exactly `k−1`, so `D_k(C_n^3) ≥ ((2k+5)n−5)/2`. Hand proof and machine check: `GENERAL_LOWER_BOUND_AND_ETA_INDUCTION_V3.md`. This supersedes the case-by-case families `S_2, S_3, S_4` as the source of the lower bound (they remain the *cube-supported* record holders, which is what `CUBE_PACKING_PROFILE_V3.md` measures).

**Upper bound — open in general, with a switch-on mechanism.** `D_{k+1} ≤ D_k + n` holds as soon as `D_k + n ≥ η(C_n^3)` (Theorem 2, ibid.). Assuming `η(C_n^3) = 8n−7`, that is available for all `k ≥ 5` (and `k ≥ 4` for `n ≤ 9`). So the conjecture reduces to finitely many values of `k` per `n`: at `n = 7`, everything from `k = 4` up follows from `D_4(C_7^3) = 43` plus `η`, and `k = 3` — the frozen question — stands alone. For `n = 3` the reduction completes: `D_k(C_3^3) = 3k+5` for **all** `k ≥ 2` (Theorem 4, ibid.).

## Evidence

| n | k = 2 | k = 3 | k = 4 | k = 5 |
|---|---|---|---|---|
| 3 | **11** exh. + donor | **14** exh. | **17** exh. | 20 (untested) |
| 5 | **20** exh. (this packet) | **25** exh. (this packet, two independent runs) | ≥ 30 (family `S_4`) | untested |
| 7 | **29** spectrum proof + donor | ≥ 36 (family `S_3`); = 36 is the frozen question | ≥ 43 (family `S_4`) | untested |
| 9 | ≥ 38 (family `S_2`) | ≥ 47 (family `S_3`) | ≥ 56 (family `S_4`) | untested |
| 11, 13 | ≥ (9n−5)/2 (family `S_2`) | ≥ (11n−5)/2 (family `S_3`) | — | — |
| `p^a`, `p ≥ 5` | `(9n−5)/2` donor route | — | — | — |

"exh." = exhaustive symmetry-reduced enumeration in `EXHAUSTIVE_ANALOG_RESULTS_V2.md`. Every entry marked `≥` is an explicit sequence whose packing number is certified by two differently structured programs.

**No computed value contradicts the formula**, including the two independent exact determinations produced in this packet (`D_2(C_5^3) = 20`, `D_3(C_5^3) = 25`).

## The families

Write `a = n−1`, `hi = (n+1)/2`, `lo = (n−1)/2`, and use the cube points `e_1,e_2,e_3,e_12,e_13,e_23,e_123` plus `g = e_1+e_2+2e_3`.

    S_2(n) = e_1^a e_2^a e_3^a e_12^{hi} e_13^{lo} e_23^{lo}                          |S_2| = (9n−7)/2,  pk = 1   ( = T_2(n) )
    S_3(n) = e_1^a e_2^a e_3^a e_12^a    e_13^{hi} e_23^{lo} e_123^{hi}               |S_3| = (11n−7)/2, pk = 2
    S_4(n) = e_1^a e_2^a e_3^a e_12^a    e_13^{hi} e_23^{lo} e_123^a   g^{(n+3)/2}    |S_4| = (13n−7)/2, pk = 3

`S_2` and `S_3` are proved for every odd `n` in `CUBE_FAMILY_LOWER_BOUNDS_V2.md`. `S_4` is verified exactly for `n = 3, 5, 7, 9` by `cube_packing_profile_v3.py` and `tools/famcheck_v3.py`; a hand proof is **open**.

Each step adds exactly `exp(G) = n` elements, and does so in a fixed way: raise one existing multiplicity from `hi` to `a` (that is `+(n−3)/2`) and introduce one new point at `(n+3)/2`. The support grows by one point per step, which is forced: the binary cube has `c_3(n) = 6n−4 < (13n−7)/2` for `n ≥ 5` (`CUBE_PACKING_PROFILE_V3.md`), so seven points cannot realise the `k = 4` bound, and eight can.

## Where the `(n−1)/2` comes from

The naive prediction `D + (k−1)exp` is what one gets from a "one long atom plus `k−1` full cyclic blocks" picture. The true constant is larger by `(n−1)/2`, and the extremal families show where the extra half-length lives: in the multiplicities `hi = (n+1)/2` and `lo = (n−1)/2` on the weight-two points `e_12, e_13, e_23`.

Those halves are not a coincidence of small cases. The `3×3` minor of the cube incidence matrix on the columns `e_12, e_13, e_23` is

    [[1,1,0],[1,0,1],[0,1,1]],   determinant −2,

so the sublattice `⟨e_12, e_13, e_23⟩` has index 2 in `⟨e_1,e_2,e_3⟩`, the associated rational polytope has half-integral vertices, and the packing profile of the cube is affine in `n` with half-integer slopes (`CUBE_PACKING_PROFILE_V3.md` §5). **The `(n−1)/2` defect in the generalized Davenport constants of `C_n^3` is the arithmetic shadow of that index-2 sublattice.** This is a mechanism statement, not a proof: it explains the shape of the answer and predicts that the same half-defect appears for any rank-3 geometry built on a determinant-2 configuration, which is a falsifiable prediction the packet has not yet tested.

## What would settle it

1. **Upper bound `D_3(C_n^3) ≤ (11n−5)/2`.** The obstruction-side reduction is complete (`OBSTRUCTION_REDUCTION_LEMMAS_V2.md`): one must show every zero-sum sequence of length `(11n−3)/2` over `C_n^3` has four disjoint blocks. The cube case is settled with room to spare (shortfall `(n+3)/2`, `CUBE_PACKING_PROFILE_V3.md` §4); the general case is open. At `n = 7` this is exactly the frozen question `D_3(C_7^3) = 36`.
2. **The step inequality `D_{k+1} ≤ D_k + n` for `k ≥ 2`.** The matching lower step `D_{k+1} ≥ D_k + n` is donor-owned. A short-zero-sum route (`|U| ≤ n` then apply `D_k` to the complement) would need `η(C_n^3) ≤ D_k + n`, which fails: `η(C_n^3) ≥ 8n−7 > (11n−5)/2` for `n ≥ 3`. So the induction must use the zero-sum form of the problem, where `SPECTRUM_CONGRUENCE_THEOREM_V2.md` gives shortest-block bounds (length `≤ 10` at `n = 7`) that are still one step too weak (`n+1 = 8` is what is needed).
3. ~~A hand proof for `S_4` and the general `S_k`~~ — **done**, by a different and simpler family (`T_k(n)`, Theorem 1 of `GENERAL_LOWER_BOUND_AND_ETA_INDUCTION_V3.md`). The lower bound no longer depends on the donor step inequality.
4. **`η(C_n^3) = 8n−7`** for `n = 5, 7`: verified here only for `n = 3` (`≤ 17`, from a frame with no leaves). With it, `D_4` at a given `n` settles every larger `k`.

## Claim ceiling

This is a conjecture. The `k = 2` value for prime powers, the eventual-arithmetic theorem, and the step inequality are donor results that this host could not read and that are not claimed here. The exact values at `n = 3, 5` and the families are the packet's own contribution, and even those grant no priority.
