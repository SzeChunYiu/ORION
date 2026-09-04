# Paper outline: generalized Davenport constants of `C_n^3` — V1 (draft skeleton, not a manuscript)

Status: **planning document**. Not a submission, not a claim of novelty, and not written under the `nature-*` skills package — those apply when manuscript content is authored in `papers/` (see `AGENTS.md`, paper writing rule). This file records what the packet currently supports, at what strength, so that a manuscript can be scoped honestly if and when the operator opens one (the operator has indicated `orion-paper` as the destination; that repository is not in this session's scope).

## Working title

*Generalized Davenport constants of rank-three groups: exact values, a uniform lower bound, and the packing profile of the binary cube.*

## What the packet can currently support

| # | Statement | Strength | Where |
|---|---|---|---|
| 1 | `T_k(n)` has packing number `k−1` and length `((2k+5)n−7)/2`, hence `D_k(C_n^3) ≥ ((2k+5)n−5)/2` for **every** odd `n` and **every** `k ≥ 2`. | Proved (hand proof, machine-checked) | `GENERAL_LOWER_BOUND_AND_ETA_INDUCTION_V3.md` Thm 1 |
| 2 | `D_2(C_p^3) = (9p−5)/2` for every prime `5 ≤ p ≤ 43`, self-contained: lower bound from (1), upper bound from a Chevalley–Warning length-spectrum congruence with an explicit `F_p` certificate. `p = 3` is genuinely different (the route is silent, matching `a_2 ≡ 0 mod 3`). | Proved per prime; uniform-in-`p` proof open | `SPECTRUM_CONGRUENCE_THEOREM_V2.md` Thm A |
| 3 | `D_3(C_5^3) = 25`. | Proved (exhaustive, two independent runs; cap justified) | `EXHAUSTIVE_ANALOG_RESULTS_V2.md` Thm 4.1, `CORRECTION_MULTIPLICITY_CAP_V3.md` §2 |
| 4 | `D_k(C_3^3) = 3k+5` for every `k ≥ 2`, self-contained. | Proved | `GENERAL_LOWER_BOUND_AND_ETA_INDUCTION_V3.md` Thm 4 |
| 5 | `η`-induction: `D_k(G) + exp(G) ≥ η(G)` implies `D_{k+1}(G) ≤ D_k(G) + exp(G)`; the switch-on point for `C_n^3` is `k = 5` (`k = 4` for `n ≤ 9`) assuming `η = 8n−7`. Consequence: at `n = 7` all `k ≥ 4` reduce to `D_4 = 43`, leaving `k = 3` isolated. | Proved (Thm 2); `η` value hypothetical for `n ≥ 5` | ibid. Thm 2, Cor 3 |
| 6 | Complete packing profile of the binary cube, `c_j(n)` and `z_j(n)` for `j ≤ 4`, exact for every odd `n ≤ 13`, all affine in `n`; the cube would need `z_3 ≥ (11n−3)/2` to host a `D_3` obstruction and has `z_3 = 5n−3`, shortfall `(n+3)/2`. | Exact for `n ≤ 13`; closed forms conjectural | `CUBE_PACKING_PROFILE_V3.md` |
| 7 | `D_2`-extremal sequences: complete `GL(3,n)`-orbit classifications at `n = 3` (43 orbits) and `n = 5` (1 405 orbits); all contain an element of multiplicity `n−1` (Conjecture R′); only 3 % contain a cube image. | Exact finite | `EXTREMAL_STRUCTURE_V3.md` |
| 8 | Structure of a hypothetical `D_3(C_7^3)` counterexample: multiplicities `≤ 6`, no zero-sum of length `≤ 7`, shortest block in `{8,9,10}`, complement a product of exactly two atoms, every one-element deletion `D_3`-extremal. | Proved | `OBSTRUCTION_REDUCTION_LEMMAS_V2.md` |
| 9 | Conjecture: `D_k(C_n^3) = D(C_n^3) + (k−1)n + (n−1)/2` for all `k ≥ 2`, odd `n`; the `k`-independent half-defect is the shadow of the index-2 sublattice `⟨e_12,e_13,e_23⟩`. | Conjecture with mechanism | `DK_ARITHMETIC_CONJECTURE_V3.md` |

## Retained negatives that belong in the paper

- The pointed (non-symmetric) polynomial-method congruences give **exactly** the symmetric threshold at the `D_3` target length; the counting route stops at "shortest block `≤ 10`" where `≤ 8` is needed.
- `D_k`-extremal sequences are **not** cube-like (3 % at `n = 3`, `k = 2`), so classification-by-geometry is not a route.
- The rigidity conjecture is **false** for `k ≥ 3` (`T_3(3)` has multiplicity 5) and survives only at `k = 2`.
- The `η`-route to `D_{k+1} ≤ D_k + n` is unavailable at small `k` because `η(C_n^3) ≥ 8n−7 > D_3 + n`.
- A multiplicity cap that is forced at one `(L,k)` is not forced one step along; the packet's own audit is in `CORRECTION_MULTIPLICITY_CAP_V3.md`.

## Priority work that must happen before any submission

1. **Donor subtraction.** Every statement above is `CANNOT_CHECK` for priority: this host cannot reach arXiv, ScienceDirect, ResearchGate or Semantic Scholar. Freeze–Schmid (Discrete Math. 310 (2010) 3373–3389) and Zhao (arXiv:2506.21383) must be read and the overlap stated explicitly. Expect items 1, 2, 4 and 5 to be at least partly classical; items 3, 6, 7 are the likeliest to survive as new, and item 9's mechanism reading is the likeliest original framing.
2. **External mathematical review** of Theorem 1's case analysis and of the `η`-induction.
3. **Independent replay** of the exhaustive frames on a second implementation (the packet has two engines but one author).
4. Decide whether the paper is about `C_n^3` in general (items 1, 5, 6, 9) or about the exact values (items 2, 3, 4, 7). The general-`n` framing is stronger and does not depend on resolving `D_3(C_7^3)`.

## Explicitly not claimed

`D_3(C_7^3)` is open in this packet. Nothing here proves it equals 36, nothing exhibits a counterexample, and no result is claimed to be new.
