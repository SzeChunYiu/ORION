# C7^3 frontier progress ledger — V2

Status: **active exploratory programme; no novelty authority; no D3 closure**. Supersedes nothing in `PROGRESS_LEDGER_V1.md`; extends it. Lane: `claude/orion-research-frontier-3ck9yt` (Claude session), built on the merged ChatGPT-lane packet `shadow/davenport-c7-frontier-20260903` (PR #2198).

## Frozen target (unchanged)

`D_3(C_7^3) = 36 ?` — equivalently (Lemma 1.2 of `OBSTRUCTION_REDUCTION_LEMMAS_V2.md`): is there a zero-sum sequence of length 37 over `C_7^3` that is a product of three minimal zero-sum sequences in every factorisation?

## New results retained in V2

| ID | Claim / finding | Status | Boundary / checker |
|---|---|---|---|
| C7-SPEC-1 | Length-spectrum congruence `Σ_ℓ (−1)^ℓ C(ℓ,d) N_ℓ ≡ 0 (mod p)`, `d ≤ N − D(G)`, for every sequence over `C_p^r` (Theorem 1). | PROVED; classical technique | `spectrum_congruences_v2.py` cross-checks it on an explicit example with index-subset weighting. |
| C7-SPEC-2 | `D_2(C_7^3) ≤ 29` with a self-contained proof (Olson + Theorem 1, certificate `λ = (5,0,0,0,6,0,6,0,1,0,1,0)`), no reliance on reading Zhao Lemma 4.4. | PROVED (independent route) | Same script; also `p = 5, 11, 13`; silent at `p = 3`. |
| C7-SPEC-3 | Every zero-sum sequence of length 37 over `C_7^3` has a zero-sum subsequence of length `≤ 10`; threshold table `k(N)` for `N = 20..40`; `k(26) = 7` for `C_5^3`. | PROVED (certificates) | Cannot be pushed to `≤ 9` by this method; binary-cube sequences show `≤ 7` is false in general. |
| C7-SPEC-4 | A length-29 zero-sum sequence with no zero-sum of length `≤ 9` has `N_10 ≡ 3 (mod 7)`, hence factors as (atom of length 19)·(zero-sum of length 10). | PROVED | Proposition D. |
| C7-CUBE-4 | Explicit families `S_2(n)`, `S_3(n)` on the binary cube with `pk = 1`, `pk = 2` and lengths `(9n−7)/2`, `(11n−7)/2` for every odd `n`, with hand proofs; `D_3(C_7^3) ≥ 36` witnessed by `e_1^6 e_2^6 e_3^6 e_12^6 e_13^4 e_23^3 e_123^4`. | PROVED; **priority not claimed** (presumably the Freeze–Schmid construction) | `verify_cube_family_v2.py` (p = 3,5,7[,11]); `tools/boxmax.c` shows the cube is sharp for `pk ≤ 2` at every tested `p` and caps at `6(p−1)+2` for `pk ≤ 3`. |
| C7-RED-1 | Reduction lemmas: a length-36 obstruction has multiplicities `≤ 6`, `T = S·(−σ)` has no zero-sum of length `≤ 7`, a shortest block of length `u ∈ {8,9,10}`, and `B = T U^{−1}` is a zero-sum sequence with `L(B) = {2}` of length `37 − u`; for `u = 8` every one-element deletion of `B` is `D_2`-extremal and `B = A_19 · A'_10`; plane occupancy `≤ 26`. | PROVED (routine) | `OBSTRUCTION_REDUCTION_LEMMAS_V2.md`. |
| C7-EXH-1 | `D_2(C_3^3) = 11`, `D_3(C_3^3) = 14`, `D_4(C_3^3) = 17` re-proved by exhaustive symmetry-reduced enumeration; extremal sequences classified: 43 / 161 / 69 `GL(3,3)`-orbits. | EXACT FINITE (replayable, < 3 min) | `run_exhaustive_analogs_v2.sh --ci`; values are donor-owned. |
| C7-EXH-2 | `D_2(C_5^3) = 20` re-proved by exhaustive enumeration (no dependence on Zhao or on the spectrum route); 1 405 `GL(3,5)`-orbits of extremal sequences. | EXACT FINITE (replayable, ~70 s) | Same script. |
| C7-EXH-3 | (CORRECTED by `CORRECTION_MULTIPLICITY_CAP_V3.md`: true as a complete statement only for `k = 2`; the `k = 3, 4` frames are capped.) Every `D_2`-extremal sequence for `p ∈ {3,5}` contains an element of multiplicity `p − 1`; maximal atoms of `C_5^3` do **not** all have this property (753 raw examples with maximal multiplicity 2). | EXACT FINITE OBSERVATION → Conjecture 5.1 | `EXHAUSTIVE_ANALOG_RESULTS_V2.md`. |
| C7-EXH-4 | **`D_3(C_5^3) = 25`**: the bound frame (`L = 25`, `s = 5`, `pk ≤ 2`, plane cap 18) enumerates 7 716 438 short-zero-sum-free leaves (848 752 855 nodes) and finds none with `pk ≤ 2`; lower bound by `S_3(5)`. | EXACT FINITE (single run; reverse-order rerun in progress) | Priority CANNOT_CHECK; first `p ≥ 5` instance of `D_3(C_p^3) = (11p−5)/2`. |
| C7-EXH-5 | `D_2(C_7^3)` inverse frame (`L = 28`, `s = 9`, `pk ≤ 1`), class `m(e_1) = 6`: 19 174 witnesses, supports 5–10; class `m(e_1) = 5`: 791 short-zero-sum-free leaves, **no** `pk = 1` witness. Both frames were **terminated incomplete** by a container restart (1.7e10 and 2.3e10 nodes), so the `m(e_1) = 5` zero is not an exhaustive negative. | TERMINATED INCOMPLETE | Supports Conjecture 5.1 at `p = 7`. |
| C7-DONOR-1 | arXiv, export.arxiv, alphaxiv, Semantic Scholar, ScienceDirect and ResearchGate are all blocked by this host's egress policy; Freeze–Schmid Theorem 4.1 and Zhao Lemma 4.4 could **not** be re-read. The V1 D2 gate therefore now rests on C7-SPEC-2 instead. | NEGATIVE / RESOURCE | Priority questions stay CANNOT_CHECK. |

## What changed in the picture

1. The **upper-bound machinery** for `D_2` is now understood inside the packet (Theorem 1). The same machinery fails at the `D_3` target exactly where the binary-cube objects live: the residual after C7-SPEC-3 is a complement `B` of length 27–29 with `L(B) = {2}`, and the symmetric congruences are consistent for all three lengths.
2. The **lower-bound objects** are now explicit and uniform in `p` (C7-CUBE-4). Within the cube, `(11p−5)/2` is sharp for every tested `p`.
3. The **inverse problems** are the actual frontier: `D_2`-extremal sequences appear to be far more rigid (always a `p−1` multiplicity) than maximal atoms. Conjecture 5.1 is the cleanest structural statement produced by this session and is exactly what the `u = 8` residual needs.
4. `p = 5` is closed: `D_3(C_5^3) = 25`, the first `p ≥ 5` instance of `D_3(C_p^3) = (11p−5)/2`; the extremal objects are being classified (length-24 frame).

## Open residuals (V2)

1. **`D_3(C_7^3)` itself.** Complete search frame is specified (`7 36 6 7 2 --planecap 26`) but the all-small-multiplicity region is far beyond the plain DFS; needs Conjecture 5.1 or an analytic multiplicity bound to cut it.
2. **Conjecture 5.1** (`p−1` multiplicity in `D_2`-extremal sequences) — no proof idea beyond the data.
3. **Non-symmetric spectrum constraints** (`h = x_J e_d` in Theorem 1) and multiplicity-aware counting are unexploited.
4. **Priority / donor saturation** unchanged from V1 and now also blocked by egress policy.
5. `D_4(C_p^3)`: the cube caps at `6(p−1)+2 < (13p−7)/2`; an eight-point construction realising `D_4 ≥ (13p−5)/2` was not searched.

## Claim ceiling

Nothing in V2 proves `D_3(C_7^3) = 36` or `≥ 37`. Nothing establishes novelty or priority. Records marked RUNNING/PARTIAL/PENDING are execution status, not results.
