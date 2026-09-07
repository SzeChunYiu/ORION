# ORION-26 claim ledger — V1

Paper: *The pointed polynomial method for generalized Davenport constants of `C_p^3`* (`MANUSCRIPT_V1.md`).
Lane: `claude/orion-research-frontier-3ck9yt`. Evidence packet: `research/experiments/davenport-c7-frontier/`.

Status vocabulary: **proved** (mathematical proof, machine-checked) · **verified-range** (finite computation over a stated range, no proof beyond it) · **external** (relied on, not proved here) · **open**.

| # | Claim | Evidence | Status |
|---|---|---|---|
| 1 | `D(C_p^r) = r(p−1)+1` | Olson (1969) | **external** — the only external input to claims 2–7 |
| 2 | `D_2(C_p^3) = (9p−5)/2` for every prime `p ≥ 5` | `D2_UNIFORM_SELFCONTAINED_THEOREM_V3.md`; `tools/d2_digit_certificate_v3.py`; structural steps re-checked for all 44 primes `5 ≤ p ≤ 200` | **proved** |
| 3 | Counting identities **(C)**, **(S)**, **(P)**, with both degree bounds sharp | `verify_short_atom_bound_v4.py` step 1 — brute force over `C_3^3`, plus explicit failure one degree higher | **proved** |
| 3b | **Theorem G**: the pointed system on `[w+1, m−w−1]` is inconsistent iff some `d ∈ [m−2w−1, m−3p+1]` is base-`p` digit-dominated by `m−1−w` | `LUCAS_CRITERION_V5.md`; `verify_lucas_criterion_v5.py` — Lucas and Newton checked separately, criterion vs elimination on all 2,916 cases over six primes, 0 disagreements | **proved** (Fredholm + Newton + Lucas; every step an identity) |
| 4 | **Proposition B**: over `C_p^3`, zero-sum `C` with `3p−2 < \|C\| ≤ (11p−3)/2` and all atoms `≥ p+1` has an atom of length `≤ w(p,m)`, closed form; at `p = 7` that is `≤ 10` for `\|C\| ∈ {23,24,27,28,29}` | `SHORT_ATOM_BOUND_UNIFORM_V4.md`; `verify_short_atom_bound_v4.py` steps 2–3 and `verify_short_atom_law_v5.py` — every system decided by Gaussian elimination **and** (where the window allows) exhaustive search, required to agree; `w−1` feasible everywhere (non-vacuity); law checked for 7 primes over every applied length | **proved** — now a corollary of claim 3b, hence for all primes |
| 5 | First corridor is exactly `(8,10,19)`, `(9,9,19)`, `(9,10,18)`, `(10,10,17)` | `verify_short_atom_bound_v4.py` step 4a | **proved**, given claims 2 and 4 |
| 6 | Second corridor is exactly `(9,13,15)`, `(9,14,14)`, `(10,13,14)` | `verify_short_atom_bound_v4.py` step 4b | **proved**, given claims 4 and 8 |
| 7 | **Theorem C**: `D_3(C_7^3) = 36` | `HYPOTHESIS_Z_PROVED_V3.md`, `D3_C7_CONDITIONAL_CLOSURE_V3.md`; `verify_D3_C7_end_to_end_v3.py` (8 asserted steps, passes) | **proved** |
| 8 | Every `p = 7` obstruction has an atom of length 13 or 14 | `ATOM_SPECTRUM_CONGRUENCE_V3.md`; `verify_atom_spectrum_v3.py` | **proved** |
| 9 | Exactly three special lengths `3(p−1)/2`, `2p`, `(5p−3)/2` for every prime `p ≥ 5`, characterised by base-`p` low digit `0` or `(p−3)/2` | `verify_general_spectrum_v4.py` step 2 — closed form asserted at every prime tested | **proved** (elementary identity) |
| 10 | Excluding any two special lengths makes `(S_p)` inconsistent | superseded by claim 23 | **proved** (was verified-range) |
| 11 | Those three pairs are the only minimal forced sets of size `≤ 2` | `verify_general_spectrum_v4.py` step 4 | **verified-range** `11 ≤ p ≤ 19` |
| 12 | The general system is a faithful generalisation of the recorded `p = 7` one | `verify_general_spectrum_v4.py` step 1 — agreement on **all 298** subsets of size `≤ 3`, zero disagreements | **proved** (as an agreement statement) |
| 13 | Pointing strictly gains on two-sided windows; the earlier "pointing buys nothing" record is correct only for one-sided windows | `SHORT_ATOM_BOUND_UNIFORM_V4.md` §3; `verify_short_atom_bound_v4.py` step 3 — symmetric feasible at `w = 13`, pointed infeasible at `w = 10` | **proved** (as a separation) |
| 16 | **Lemma E**: the two-sided window needs no packing hypothesis | `D4_C5_FOUR_ATOM_CORRIDOR_V4.md` §2 | **proved** |
| 17 | Every zero-sum over `C_5^3` of length `m ∈ [14,31]` has an atom of length `≤ 8`, and `≤ 7` unless `m ≡ 4 (mod 5)` | `verify_d4_c5_corridor_v4.py` step 2 — 18 bounds by elimination, 12 cross-checked by exhaustive search, `w−1` feasible throughout | **proved** |
| 18 | **Theorem F**: a length-31 obstruction over `C_5^3` has four-atom profile in `{(6,6,6,13), (6,6,7,12), (6,7,7,11), (6,7,8,10), (7,7,7,10)}` | `verify_d4_c5_corridor_v4.py` step 3 | **proved**, given `D_3(C_5^3) = 25` (external, prior ORION-RG X1-F) |
| 19 | Observation D reduces to: `Q = P + (−1)^N P∘σ` is `(−1)^N`-symmetric, vanishes on the atom range except at the two excluded lengths (nonzero at both) and at `0`; `P` vanishes on the interval `[N−D,D]` of length `(p−3)/2` | `OBSERVATION_D_REDUCTION_V5.md`; `verify_observationD_reduction_v5.py` (`p = 11,13,17,19,23`) | **proved as a reduction**; does not extend Observation D's verified range |
| 20 | Step 5 of Theorem C double-implemented, exact agreement (548 → 8 → 0) | `D3_STEP5_SECOND_IMPLEMENTATION_V5.md`; `verify_d3_step5_independent_v5.c` | **double-implemented, not independently verified** (same author) |
| 21 | **Lemma H**: of the twelve points `S = {jp} ∪ {jp+h}`, `h=(p−3)/2`, exactly `3(p−1)/2`, `2p`, `(5p−3)/2` lie in `[p+1,3p−2]` | `DUAL_SUPPORT_TWELVE_POINTS_V5.md`; `verify_dual_support_v5.py` (four inequalities, all 76 primes 5..397) | **proved**, uniform in `p` |
| 22 | **Theorem I**: for `Z` a set of special lengths, every dual satisfies `supp Q ⊆ S` | `SUPP_Q_PROVED_V5.md`; `verify_supp_Q_proof_v5.py` — identities exact over `ℤ` both signs; span check `p = 11..37` | **proved**, uniform in `p` |
| 23 | **Theorem J**: each special pair is forced, so every obstruction has atoms of at least two of `3(p−1)/2`, `2p`, `(5p−3)/2` | `OBSERVATION_D_EXISTENCE_PROVED_V5.md`; `verify_existence_proved_v5.py` — explicit dual, finite identity set, parity fact checked per branch | **proved, all primes `p ≥ 5`** |
| 25 | **Lemma K**: no special length or complement lies in `[N−D,D]`, so no `X_L` column is dropped for special `Z` — the Newton parametrisation used by Theorems I and J is exact there | `MINIMALITY_ATTEMPT_V5.md`; checked all 76 primes 5..397 | **proved** — closes an implicit gap in the setup of claims 22 and 23 |
| 24 | Sharpness: the three pairs are the *only* minimal forced sets | `verify_general_spectrum_v4.py` | **verified `p ≤ 19`, not proved**; nothing downstream uses it. The natural dimension count is refuted (`MINIMALITY_ATTEMPT_V5.md` §3) — the ambient space moves with `Z` |
| 14 | `D_3(C_p^3)` for `p ≥ 11` | — | **open** |
| 26 | **Theorem T**: `D_4(C_5^3) = 30`; hence `D_k(C_5^3) = 5k+10` for every `k ≥ 2` | `D4_C5_DECIDED_V6.md`; orbit sweeps at `L = 10,11,12,13`, each by two independent builds with exactly matching node counts | **proved**, given `D_3(C_5^3) = 25` (external, prior ORION-RG X1-F); the line consequence additionally uses the Freeze–Schmid induction |
| 15 | Observation D for `p > 31` | — | **open**, with the obstacle now exact: find `P` vanishing on `[N−D,D]` with `P(L) = −(−1)^N P(N−L)` on `[p+1, N−D−1]` and `P(0) + (−1)^N P(N) ≠ 0` (`LUCAS_CRITERION_V5.md` §4) |

## Corrections

- **V5 → V6 prior-art correction (this pass).** `MANUSCRIPT_V1.md` §9 previously reported that
  "the nearest prior work is located and lies on a disjoint family of groups". That was correct
  about reference 4 (Girard–Schmid, `C_2 ⊕ C_{n_2} ⊕ C_{n_3}`) and **wrong as a summary of the
  prior-art position**. A later search pass identified **reference 6**, Marchan–Ordaz–Santos–Schmid,
  *Multi-wise and constrained fully weighted Davenport constants and interactions with coding
  theory* (JCTA 2015; arXiv:1407.1966): its `m`-wise Davenport constant at trivial weights `W={1}`
  **is** `D_m`, it treats **elementary `p`-groups** specifically, and it links these constants to
  linear-code parameters and cap sets, reporting explicit values. Elementary `p`-groups of rank
  three are inside its scope, so reference 4's disjointness does not transfer. The reference is
  added, the Positioning paragraph is rewritten, and the pre-submission gate now names it first.
  No claim in this ledger changes status as a result — but the *novelty* of claims 2, 7 and 26 is
  now explicitly `CANNOT_CHECK` against a named nearest neighbour rather than against a field
  described as disjoint.

- **Contribution-list correction (this pass).** The list in §1 was numbered `1, 2, 2b, 3, 3c, 3b,
  4, 5` (sub-items out of order) and described the three special lengths as "verified for
  `5 ≤ p ≤ 31`", understating claim 9, which is **proved** for every prime by an elementary
  identity. Renumbered `1–8`; the special-length item now states the proof, and the
  verified-only-for-`11 ≤ p ≤ 19` sharpness (claims 11/24) is stated separately as such.

- **V4 → V5 range correction.** `SHORT_ATOM_BOUND_UNIFORM_V4.md` stated Proposition B for `23 ≤ |C| ≤ 29`. Only `{23,24,27,28,29}` was verified, and `|C| = 25, 26` genuinely give 11 and 12, not 10. Corrected here and in the record. No downstream conclusion changes: the corridors consume exactly the five verified lengths (`29,28,27` and `24,23`).

## Withdrawn / not claimed

- No priority claim is made against the external literature: the authoring host has no network access, so the prior-art pass is outstanding (`MANUSCRIPT_V1.md` §9). Earlier records in this programme already withdrew four claims that duplicated in-repository work (`PRIOR_WORK_RECONCILIATION_V3.md`); none of those is re-asserted here.
- The value `D_2(C_5^3) = 20` and `D_3(C_5^3) = 25` are **not** claimed as new; they are prior ORION-RG results (X1-F, X1-F0). Claim 2 is a self-contained *proof route* for all primes, which matters because later reductions consume `D_2`.
- Theorem F does **not** decide `D_4(C_5^3)` and excludes none of its five profiles. `D_3(C_5^3) = 25`, which it consumes, is prior ORION-RG work.
- The prime-uniform maximal-atom corridor `(p+j, p+(p+1)/2−j, 3p−2)` is a parallel lane's result, cited in §6 and not claimed here.

## Pre-submission gates

1. **Read reference 6 first** — Marchan–Ordaz–Santos–Schmid, arXiv:1407.1966. It is the nearest
   prior work by subject (`m`-wise Davenport constants, elementary `p`-groups, linear codes and
   cap sets) and the single reference whose reading could most change the novelty position. Then
   the rest of the prior-art pass against primary sources. Network access required; every
   scholarly host is refused by the authoring host's egress policy.
2. Independent mathematical review of Theorem C, in particular the step-5 enumeration. The
   existing double implementation shares an author and is **not** independent replication.
3. Independent re-implementation of `verify_D3_C7_end_to_end_v3.py` step 8.
