# QG-28 — realize QG-6's support-capped corollary, and measure what it actually buys

Date: 2026-08-22
Lane: ORION-QG / wave 3 · residual **W9**
Branch: `claude/orion-harness-verification-b17qdj`
Base revision: `53913fd6`
Status: **FROZEN BEFORE THE OUTCOME-DETERMINING RUN, WITH A SCOUTING DISCLOSURE
IN §0 THAT NARROWS WHAT "PROSPECTIVE" MEANS HERE. READ §0 FIRST.**

Authority ceiling: **NOT_R6**. `novelty_authority: false`, `novelty_credit: false`,
`physical_quantum_advantage_claim: false`. No chemistry read. The protected
stretched-N₂ subject is never read. Committed analyzers imported **unmodified**.
Runtime cap **< 45 minutes for the full run**; every cap disclosed.

---

## 0. Scouting disclosure — what was already known when this protocol was written

**A prototype was run before this file existed.** Writing "frozen before outcome"
over a protocol whose author has already seen the answer is precisely the failure
`orion_research_harness.criterion_binding` was committed to stop, so the honest
move is to say what was seen rather than to claim a freeze that did not happen.

Before freezing, a scratch prototype of the capped search had already returned:

* exact agreement with the committed `r6p.dxx_search(max_weight=2)` on **all 4096
  n=1 instances**, on a 20-instance random n=2 sample, and on a 2-instance random
  n=3 sample;
* agreement between an O(n) Tag syndrome DP and an exhaustive 4^n−1 Tag minimum on
  200 random frame-pair triples at n=1;
* wall-clock per instance of roughly 0.0015 s (n=1), 0.16 s (n=2), 40 s (n=3) for
  the capped search against 0.0004 s / 0.0025 s / 0.022 s for the committed one.

So **Q1 and Q2 below are NOT prospective.** Their terminals are written knowing
the direction of the answer, and the results file must label them
`prospective: false`. What the prototype did *not* fix, and what this lane
therefore does hold prospectively, is:

* the **full declared domains** (n=1 exhaustive, the complete 9,261-instance
  structured n=2 domain, all R6N hostile panels) rather than samples — a
  disagreement anywhere in them refutes Q2 as stated;
* **Q3 in its entirety**: the cell-count model, the crossover n it predicts, and
  whether measured wall-clock corroborates that model. No crossover figure had
  been computed when this section was written.

The counting rules in §5 are frozen here **before** either count is evaluated.

## 1. The residual, as registered

W9, registered by QG-22 and carried in `QG_WAVE23_CLOSURE_PACKET.md`:

> committed family search does not realize QG-6's support-capped corollary —
> partial; QG-10's `U_W1` supplies an uncapped weight-one enumerator … support-2
> remains

and, from `VERIFICATION_COVERAGE_2026-08-21.md`:

> QG-6's committed corollary bounds a certified support-≤2 search at `O(n²·16)`
> frame-pair candidates per block. The committed `r6p.dxx_search` does not realize
> it … `O(n·4^{3n})` cells. … **Registered as W9 … The bound is already proved;
> this is engineering.**

The registration also carries a *projection* — "projected exponential→polynomial
implementation win" (`reopen-adjudication/CONVERSION_LEDGER.md`). **That
projection has never been evaluated.** Evaluating it is Q3.

## 2. Frozen objects

* Family **D++** exactly as committed in R6P: three TARE-M2 frames whose six frame
  Paulis each have global support ≤ 2, one shared Tag of unrestricted support, a
  per-block central choice, donor-owned all-three Restore factoring.
* Reference implementation: `max_r6p_weight2_frame_donor_closure.dxx_search`,
  imported **unmodified** and never edited.
* Frozen definitional rules taken from the committed modules, not re-derived:
  `r6m._uanti_m2` for the anti-commutation charge, `h.BITS_CODE` for letter codes,
  `p10.wt` / `p10.symp` / `p10.mul` for the Pauli algebra.
* Cost identity this lane enumerates directly from the family definition:

      C = Σ_j uanti_j + 2·wt(S) + Σ_j (wt(t0_j·R0_j) + wt(t1_j·R1_j)) − 2·match

  where `match` counts the positions at which all three Restore factors carry the
  same **non-identity** letter.

## 3. Q1 — build the certified capped search

Enumerate frame-pair triples directly over the support-capped candidate set, with
**no don't-care pattern space**:

1. Candidate set per block: ordered anticommuting pairs of nonzero Paulis of
   weight ≤ 2. This is the object QG-6's corollary bounds.
2. `uanti` **minimised over the per-block central choice the family grants**,
   through the frozen `r6m._uanti_m2` — not through `dxx_search`'s tie-break.
3. The shared Tag is obtained **without the 4^n−1 sweep**, by an exact per-qubit
   syndrome DP over the six label constraints: 64 states, O(n) time. If this DP
   does not reproduce the exhaustive Tag minimum, Q1 fails and the lane says so.
4. The enumeration is **unpruned**. A certified search is worth more as a plainly
   exhaustive loop than as a fast one; the verifier has to be able to re-derive it.

The implementation is written from the family definition and from the frozen
primitive functions. It does not call `dxx_search`, `_zeta_min`, `_block_arrays`,
`_DxxTables` or `_dxx_backtrack`.

## 4. Q2 — machine-check equality on declared domains

`C_capped == C_Dxx` on:

* **A** — n=1, **all 4096** target-letter instances (complete).
* **B** — n=2, **all 9,261** structured instances of the committed R6P domain (complete).
* **C** — all R6N hostile panels (n=1 and n=2), which include the instance `n2_b`
  that refuted the weight-one family.
* **D** — n=3, a seeded random set whose size is declared and whose obstacle
  (the capped search costs ~40 s per instance at n=3) is named.

Any mismatch is reported **verbatim** and is the lane's result: it would mean the
corollary, the family definition, or one of the two searches is wrong.

## 5. Q3 — count the cells, then ask whether the projected win exists

**Frozen counting rule, written before either count was evaluated.** Both models
count *array cells touched*, derived from the committed source text, not timed:

* Committed `dxx_search`: for each of 2 label orientations and each of the 4^n−1
  Tags, three blocks each pay one fill plus a `_zeta_min` of 2n passes over
  4^{2n} cells, and one combine pass over 4^{2n} runs afterwards:

      N_dxx(n) = 2·(4^n − 1)·[ 3·(2n + 1)·4^{2n} + 4^{2n} ]

* This lane's capped search: for each of 2 label orientations and each of P(n)
  block-0 candidates, one Tag-mask reduction of 3 passes over P(n)² cells, then 8
  target-permutation combinations each paying 3 passes over P(n)²:

      N_cap(n) = 2·P(n)·[ 3·P(n)² + 8·3·P(n)² ] = 54·P(n)³

  with P(n) the number of ordered anticommuting pairs of nonzero Paulis of weight
  ≤ 2 — the quantity QG-6's `O(n²·16)`-per-block corollary controls.

Report both, the ratio, and **the smallest n at which `N_cap < N_dxx`**. Then
state, in one sentence, whether W9's registered "exponential→polynomial
implementation win" exists, and at what n it starts to pay.

**Wall-clock is reported and may not carry any part of the argument** (gate G3).
It appears for exactly one purpose: to say whether the frozen cell model is
corroborated or contradicted by measurement. A discrepancy is reported as a
discrepancy, not smoothed.

## 6. Terminals, frozen

* `QG28_COROLLARY_REALIZED__PROJECTED_WIN_CONFIRMED_WITH_ITS_CROSSOVER` — the
  capped search agrees on every declared domain, the Tag DP reproduces the
  exhaustive Tag minimum, and `N_cap < N_dxx` from some finite n onward, which is
  reported.
* `QG28_COROLLARY_REALIZED__NO_WIN_AT_ANY_N` — agreement holds, but the counting
  model shows the capped search never overtakes. W9's projection would then be
  **false as registered** and must be struck.
* `QG28_REALIZATION_DISAGREES__SOMETHING_IS_WRONG` — a mismatch on a declared
  domain. Reported verbatim; nothing else in the lane may be cited.
* `QG28_BLOCKED__CAPPED_SEARCH_NOT_RUNNABLE` — the capped search cannot be run at
  n=1 at all, with the measured reason.

## 7. Gates

* **G1** — donor search validated by the committed module. This lane asserts **no
  novelty**: the corollary is QG-6's, the family is R6P's, and the Tag step is a
  textbook minimum-weight-coset syndrome DP. Records carry `asserts_novelty:
  false`, and the results file says so in words rather than leaving it implied.
* **G2** — `dxx_search` and every frozen primitive imported unmodified; no
  committed file is edited by this lane.
* **G3** — **no complexity inference from wall-clock.** Timing corroborates or
  contradicts the frozen §5 cell model and does nothing else.
* **G4** — the equality claim is empirical over declared domains. This lane
  proves no theorem and may not say it has.
* **G5** — complete enumeration on domains A, B and C, or the shortfall named with
  its measured obstacle. Domain D is explicitly a declared sample.
* **G6** — QG-6's, QG-22's and R6P's receipts are not edited; qualifications live
  here and in the ledger rows this lane updates.
* **G7** — independent from-primitives verifier, demonstrated capable of failing
  on tampered copies whose digests are recomputed to be self-consistent, with
  every tamper rejected by a **named** check and the checks it never exercises
  listed.
* **G8** — determinism: a double run is byte-identical outside timing fields.
* **G9** — NOT_R6; protected subject unread; caps disclosed.

## 8. Files this lane may create

1. `research/extensions/orion-qg/qg28_support_capped_realization.py`
2. `research/extensions/orion-qg/QG28_SUPPORT_CAPPED_REALIZATION_RESULTS.json`
3. `development/orion-qg-regime-geometry/qg28_generic_verify.py`
4. `development/orion-qg-regime-geometry/qg28_assemble_verification.py`
5. `development/orion-qg-regime-geometry/QG28_GENERIC_VERIFICATION.json`

## 9. What this lane cannot do

It cannot claim novelty. It cannot prove the two searches equal — it checks them
on declared domains and the domains bound the claim. It cannot revise QG-6's,
QG-22's or R6P's receipts. It cannot read the protected subject. It cannot use
wall-clock as evidence for anything except the fidelity of its own cell model.
