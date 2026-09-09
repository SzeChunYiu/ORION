# ORION-27 claim ledger — V1

Paper: *An exact packing criterion for generalized Davenport constants of `C_p^r` above rank three* (`MANUSCRIPT_V1.md`).
Lane: `claude/orion-research-frontier-3ck9yt`. Evidence packet: `research/experiments/davenport-c7-frontier/`.

Status vocabulary: **proved** (mathematical proof, machine-checked) · **verified-range** (finite computation over a stated range, no proof beyond it) · **external** (relied on, not proved here) · **conjecture** · **open**.

Every row's *independent check* column records what was re-derived **in this drafting session**, from a
separate implementation or a separate decision procedure, rather than read off the evidence packet.
Four rows failed that check; see **Corrections** below.

## Uniform results (§3–§5) — proved for all `(p, r)`

| # | Claim | Evidence | Independent check | Status |
|---|---|---|---|---|
| 1 | `D(C_p^r) = r(p−1)+1` | Olson (1969) | — | **external** — the only external input to every proof here |
| 2 | **Theorem C**: blocks of `S` are the nonzero binary codewords of `ker M`; disjointness is disjointness of supports; `D_k` is the corresponding extremal problem | `CODE_DICTIONARY_V7.md` §1; `verify_code_dictionary_v7.py` steps 1–2 | block set computed twice (brute-force subset sums vs Gaussian elimination + code enumeration) on 60 sequences, `z(S)` on 96; 0 disagreements | **proved** (elementary; claimed as translation, not discovery) |
| 3 | **Lemma A**: `z(S) ≤ 1` ⟹ the blocks form an antichain | ibid. §2; checker step 3 | 84 sequences with `z ≤ 1`, 0 violations; 246 with `z ≥ 2` as negative control | **proved** |
| 4 | **Corollary C1**: `z(S) ≤ 1` iff the atoms pairwise intersect | ibid. §2; checker step 4 | biconditional agrees on all 305 sequences possessing a block | **proved** |
| 5 | **Theorem Y**: a sequence with a block, some position of which lies in every block, has `n ≤ D(C_p^r)`; and it is sharp | ibid. §3; checker steps 5–6 | 3,074 random sequences with a block; 734 had a covering position, none exceeding `D`; sharpness exhibited at `C_3^3`, `C_3^5`, `C_5^3`, `C_7^2` | **proved** |
| 6 | **Corollary Y1**: a `z ≤ 1` witness of length `≥ D+1` has atoms with empty common intersection | ibid. §3 | empty core confirmed on all six extremal witnesses of ledger row 22 | **proved** |
| 7 | **Lemmas 1–2**: blocks of `(†)` are indexed by `b`, the `e`-part forced to `⟨−(Mb)_i⟩`; disjointness is coordinatewise no-carry | `WITNESS_CRITERION_V6.md` §2 | implicit in row 8's check | **proved** |
| 8 | **Theorem W**: `z(S) ≤ 1` iff every admissible pair `(b,b′)` has a witness coordinate | ibid. §3; `verify_witness_criterion_v6.py` | criterion re-implemented **from the statement alone** in this session and run against all seven published optimal families; agrees with the packing DP on every family it validated, and **found two published families to be inadmissible** (Corrections C2, C4) | **proved** |
| 9 | **Corollaries 1–3**: intersecting; `m_A ≤ p`; the load-capped sufficient condition | ibid. §4 | Corollary 2 re-derived; Corollary 3 is a three-line specialisation | **proved** |
| 10 | **Theorem W_t**: the `t`-fold criterion, for every `t` | ibid. §9 | multiwise optima recomputed at `(r,p,k) = (3,5,3), (3,7,3), (3,5,4), (4,3,3)`, giving `M*_k = 12, 17, 17, 8` and the bounds `25, 36, 30, 17` | **proved** |
| 11 | **Theorem X**: the extra part has no proper zero-sum, so `M* ≤ D` | ibid. §7 | — | **proved** |
| 12 | **Theorem X′**: projections are zero-sum free, so `M* ≤ a(p−1)+1` | ibid. §7 | tightness table recomputed from the families returned in this session: tight at `C_3^2`, `C_3^4`, `C_3^6`, `C_5^4` | **proved** (indicator families) |
| 13 | **Corollaries 4, 4′**: no `(p+1)`-petal sunflower; `p` petals is the threshold | ibid. §7a | — | **proved** |
| 14 | **Corollaries 5, 5a**: at `p = 3` at most one set is repeated, so `Σ m_A ≤ |F| + 2` | ibid. §7b | ceiling re-derived (Correction C3) | **proved** |
| 15 | The two necessary conditions do not characterise admissibility: `B(4,3) = 9` against `M*(4,3) = 5` | ibid. §7c | — | **verified-range** `r ≤ 4`, `p = 3` |

## Exact values (§6)

| # | Claim | Evidence | Independent check | Status |
|---|---|---|---|---|
| 16 | `D_2(C_3^4) = 14` | `D2_C3_4_DECIDED_V7.md`; `verify_d2_c3_4_v7.py` (6 steps); sweep 987,944 nodes / 10,852 leaves / 0 with `z ≤ 1` | lower-bound family re-derived by exhaustive enumeration and re-tested against a from-scratch criterion implementation; enumerator calibration reproduces `D_2(C_3^3) = 11` from both sides | **proved**, given row 1 |
| 17 | `D_2(C_3^5) = 17` | `D2_C3_5_DECIDED_V6.md`; sweep 2,730,591,635 nodes / 0 leaves across 49 shards | lower-bound family re-derived and re-tested as above | **proved**, given rows 1 and 16 |
| 18 | Row 16 repairs row 17: the `s = 4` branch of the spanning reduction cited `D_2(C_3^4) = 14` before it was proved, and the trivial bound `2D − 1 = 17` did not suffice | `D2_C3_4_DECIDED_V7.md` §3; V7 correction appended to `D2_C3_5_DECIDED_V6.md`; checker step 6 | the trivial bound's insufficiency re-checked arithmetically | **proved** (as a repair) |
| 19 | These are the first exact `D_2(C_p^r)` values for `r ≥ 4`, odd `p` | — | — | **open — novelty unverified**; see gate 1. Stated in §6.3 on that footing only |

## Bounds and brackets (§7)

| # | Claim | Evidence | Independent check | Status |
|---|---|---|---|---|
| 20 | `M*(r,p)` at the twelve computed points: `3,5,7 / 4,7,10 / 5,9,12 / 6,10 / 7` | `WITNESS_CRITERION_V6.md` §5–6 | **all twelve recomputed from scratch in this session** by exhaustive enumeration; every value reproduced | **verified-range** (exhaustive over indicator families at each stated `(r,p)`) |
| 21 | Five improved lower bounds: `D_2 ≥ 17, 20, 26, 37, 31` for `C_3^5, C_3^6, C_5^4, C_7^4, C_5^5`, each propagating to every `k` | ibid. §5, §9a | every optimal family re-tested against the criterion; four passed, one was mis-transcribed (Correction C2) — the **bounds are unaffected**, the enumerator returns an admissible family of the same size | **verified-range** for the constructions; propagation is **proved** given row 10 |
| 22 | Upper bounds `D_2(C_5^4) ≤ 27`, `D_2(C_7^4) ≤ 39`, `D_2(C_5^5) ≤ 32`, `D_2(C_11^4) ≤ 63`, by congruence certificate | `D2_ALL_RANKS_V3.md` §1; `tools/d2_rank_bounds_v3.py` | certificate rerun in this session over `2 ≤ r ≤ 6`, `p ∈ {5,7,11,13}`; reproduces `3p−1` and `(9p−5)/2` at ranks 2 and 3 as calibration | **proved** per pair (finite certificate) |
| 23 | Hence `D_2(C_5^4) ∈ {26,27}`, `D_2(C_5^5) ∈ {31,32}`, `D_2(C_7^4) ∈ {37,38,39}` | rows 21 + 22 | arithmetic re-checked | **proved**, given rows 21 and 22 |

## The closed form (§8)

| # | Claim | Evidence | Independent check | Status |
|---|---|---|---|---|
| 24 | `D_k(C_p^r) = (3/2)r(p−1) + (k−2)p + 2` | `CLOSED_FORM_CONJECTURE_V7.md`; `verify_closed_form_conjecture_v7.py` (10 steps) | checker rerun; constants shown forced by a rank-two solve over `Q` | **conjecture** — not proved in any rank |
| 25 | It agrees with all **25** known exact values, and the naive rank-two shape fails at all **9** points of rank `≥ 3` | checker step 2–3 | recount from the checker's own table: `16 + 4 + 5 = 25` | **verified** as an arithmetic fact (Correction C1 corrects the source record's stale `24` and `8`) |
| 26 | The construction shortfall runs `0, 0, 1, 2` at `(4,p)`, `p = 3,5,7,11`, and 1 at `(7,3)` and `(5,5)` | checker step 9 | `M*(4,3) = 5`, `M*(4,5) = 9`, `M*(4,7) = 12`, `M*(5,5) = 10`, `M*(7,3) = 7` recomputed here; `M*(4,11) = 19` is the packet's exhaustive run, **not** re-derived here | **verified-range** |
| 27 | **The dichotomy**: at `(4,7)`, `(4,11)`, `(5,5)` and `(7,3)`, either the closed form is false or the family `(†)` is not extremal | rows 24 + 26 | logical restatement of rows 24 and 26; rests on `M*(4,7) = 12` and `M*(7,3) = 7`, both recomputed here | **proved** as a dichotomy; neither branch decided |
| 28 | Six extremal witnesses saturate the atom-size window with empty core | checker step 7; `D2_C3_4_DECIDED_V7.md` §1; `CODE_DICTIONARY_V7.md` §5 | — | **verified-range** (six groups) |
| 29 | The half-budget mechanism is refuted: no recorded optimum satisfies `|e(b)| > q/2` | checker step 8 | — | **proved as a refutation** (8 of 8 counterexamples) |

## Negative results (§9)

| # | Claim | Evidence | Independent check | Status |
|---|---|---|---|---|
| 30 | `M*(7,3) = 7`, so `M*(r,3) = r+1` is **false** at `r = 7` | `WITNESS_CRITERION_V6.md` §6 (corrected) | both halves re-derived here: Lemma R lifts the rank-six optimum to `[7]` (lower), and the minimum-set-size-4 search was **rerun to completion** (upper), returning 7 with a family that passes a from-scratch criterion implementation | **verified-range** (exhaustive over indicator families at `(7,3)`) |
| 31 | `ν_r = 3(r−1)/(r+1)` fits 12 of 14 computed optima and fails at `(6,3)` and `(7,3)` | `CLOSED_FORM_CONJECTURE_V7.md` §3; checker step 10 | checker rerun; `M*(6,3) = 7` and `M*(7,3) = 7` recomputed here, against a predicted 6 in both cases | **verified-range**; recorded as an observation with its failures attached |
| 32 | Neither natural uniform family shape achieves the optimum | `WITNESS_CRITERION_V6.md` §8 | — | **verified-range** (`r ≤ 12`; 120 graphs at `r = 6`, 6,435 at `r = 7`) |
| 33 | Widening to general `F_p^r` vectors gains nothing at `(3,3)`, `(4,3)`, `(5,3)`; beyond rank 5 the exhaustive route does not run and randomised searches are **uncalibrated** | `CLOSED_FORM_CONJECTURE_V7.md` §3 | — | **verified-range** `r ≤ 5, p = 3`; `(7,3)` reported **undecided**, not negatively decided |

## Pre-submission gates

1. **Prior art.** Reference 5 (Marchan–Ordaz–Santos–Schmid, arXiv:1407.1966) is **done** — read in
   full, overlap established as empty because its elementary-`p`-group results are fully weighted.
   The remaining four references are unread; every scholarly host is refused by this environment's
   egress policy. The novelty of Theorems C, W, W_t, X, X′ and Y is **CANNOT_CHECK**, as is
   whether `D_2(C_3^4)` or `D_2(C_3^5)` already appears in the literature (row 19).
2. **Independent mathematical review.** None of the proofs has been read by a mathematician. The
   reductions in §6 are what a reviewer should attack first.

## Corrections

Four defects were found in the evidence packet by this drafting session's atomic-verification
pass, all by re-deriving numbers rather than by re-reading records. They are recorded here and
fixed at source.

- **C1 — the closed-form record's evidence count was stale.** `CLOSED_FORM_CONJECTURE_V7.md` §2
  is headed "24 of 24 known exact values" and says the naive formula "fails at all 8" points of
  rank `≥ 3`. Its own checker asserts **25** and **9**: the record's §2 table was not updated when
  `D_2(C_3^4) = 14` was added to the known-value set, though §3 of the same record was. The
  manuscript uses 25 and 9, which is what the checker computes.

- **C2 — the `C_5^4` optimal family printed in `WITNESS_CRITERION_V6.md` §5 is inadmissible.**
  The record prints `12, 13, 124², 14, 134², 234²`. Tested against Theorem W by an implementation
  written in this session from the statement alone, that family **fails**, on the pair
  `b = e_{14}`, `b′ = e_{13} + 2e_{124} + 2e_{134} + e_{234}`. The enumeration returns
  `12, 13, 14, 123², 124², 134²` instead, which passes, has the same size 9, and yields the same
  bound. **The bound `D_2(C_5^4) ≥ 26` is unaffected**; the printed family was a transcription
  error. The manuscript prints the family the enumeration actually returns.

- **C3 — `WITNESS_CRITERION_V6.md` §7b's ceiling is right and an early manuscript draft's was
  wrong.** Corollary 5a caps the number of repeated sets at one; since Corollary 2 caps that one
  at `m_A ≤ p = 3`, the resulting bound is `Σ m_A ≤ |F| + 2`, not `|F| + 1`. Caught in draft.

- **C4 — the `C_3^7` optimal family printed in `WITNESS_CRITERION_V6.md` §6 was wrong in two of
  its seven sets.** The record printed `{1234}, {1235}, {1236}, {1456}, {12456}, {12467},
  {12357}` and stated that the corresponding length-21 sequence has `z = 1`. Tested against
  Theorem W in this session, that family has **28 obstructed pairs** — for instance
  `b = e_{12456} + e_{12467} + e_{12357}`, load `(0,0,1,2,2,2,2)`, against
  `b′ = e_{1234} + e_{1235} + e_{1236} + e_{1456}`, load `(1,0,0,2,2,2,0)`, which share no
  coordinate where both entries are nonzero and sum to at most 3.

  **Resolved.** The exhaustive minimum-set-size-4 search was rerun to completion here and returns
  `max Σ m_A = 7` with `{1234}, {1235}, {1236}, {1456}, {12456}, {1247}, {1257}` — the same value,
  with two four-element sets where the record printed two five-element ones. That family passes a
  from-scratch criterion implementation. So **`M*(7,3) = 7` stands**, as do `D_2(C_3^7) ≥ 22`, the
  refutation of `M*(r,3) = r+1` (row 30), the `(7,3)` shortfall row (row 26) and the `ν_r`
  failure at `(7,3)` (row 31). The defect was in the transcription, not in the result.

  Independently, **Lemma R** (manuscript §5.3, new here) re-derives the lower half without any
  rank-seven search: `M*(·,p)` is non-decreasing in the rank, so lifting the rank-six optimum
  gives `M*(7,3) ≥ M*(6,3) = 7`. Verified by lifting that family to `[7]` and `[8]`.

  *Lesson recorded: of the seven optimal families the packet prints, two were mis-transcribed.
  Both were caught by re-testing them against the theorem statement rather than by re-reading the
  record, and in both cases the underlying value survived. A printed witness is a claim like any
  other and needs its own check.*
