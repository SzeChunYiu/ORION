# ORION-QG wave-1 closure packet

Status: CLOSED — every lane slot carries its receipt and the harness-driven closure
decision is recorded below (2026-08-21).
Charter: `PROGRAMME_CHARTER_V1.md` (issue #740). Branch:
`claude/orion-harness-verification-b17qdj` (from merged main `4cde8d48`).
Authority: development record only; no lane receipt grants scientific/novelty authority.

## Lane slots (bound verbatim from receipts on arrival)

- **QG-1 rank-2 all-n — THEOREM_MACHINE_CHECKED, B = 5** (`QG1_RANK2_ALL_N_RESULTS.json`,
  replay-verified;
  `ORIONQ_QG1_RANK2_ALL_N_THEOREM_MACHINE_CHECKED__GENERATOR_SUPPORT5_SUFFICES_ALL_N__
  CAP5_EQUALS_UNRESTRICTED__NOT_R6`): for every n and every R6I-grammar instance the
  exact optimum is attained with generator support ≤ 5. New machinery: coincidence /
  non-coincidence column split tames the dependent-triple coupling (solo moves ≤ 0 over
  55,296 cases; coincidence solo pays up to +4 — this grammar's weight-2-boundary
  analogue — so pairs handle them, ≤ −4 over 9,216 cases); the 2-bit Tag inflates the
  pigeonhole to F₂³ with an exact exceptional census (32 + 6 zero-sum-free patterns),
  honestly raising the provable bound to 5 rather than transplanting R6S. Stress: 44/44
  n=3 DP == brute == cap-2 == cap-1 (no trade realized — the objective lacks a factor
  rule, evidence that factoring powers the compression trade); 120/120 descents with
  exact predicted-vs-observed deltas. Open: tightness of 5.
- **QG-2 objective robustness — MIXED: THE GEOMETRY IS A PROPERTY OF THE
  (FAMILY, OBJECTIVE) PAIR** (`QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json`;
  `ORIONQ_QG2_OBJECTIVE_ROBUSTNESS_MIXED__FROZEN_REWEIGHTED_OBJECTIVES__NOT_R6`; the O0
  baseline control reproduces the R6Q counts and all hostile gates pass). Under the
  frozen coefficient-weighted objective O1 (t_c=1, t_nc=7, t_r=3, t_Tag=4): chemistry
  loses donor-exactness entirely (0/30), the two-trade completeness identity fails on
  4,484 structured instances, 7,752 membership transitions are witnessed verbatim
  (6,014 DONOR_EXACT→BORROW, 1,738 SPLIT→BORROW), and two new trade classes appear —
  including NEW_SUPPORT3, where a support-3 factorization strictly beats every
  support-≤2 one (C_DP=11 < C_D++=13 < C_D+=23; 53 support-2 closure failures), so the
  R6S sufficiency bound is *objective-scoped*, not universal. No predicate in the frozen
  literal family is exact under O1 (baseline P1: 327 errors, all false-positive; best
  re-induced form still 273 false negatives) — predicate verdict OBJECTIVE_SPECIFIC.
  Under the rotation-count-coupled O2 (ρ=5): exactly invariant within the family by a
  machine-checked constant-shift lemma (every member carries exactly 9 rotations, so O2
  = O0 + 45), and the cross-family comparator re-pricing changes zero H4/N2 deltas —
  GEOMETRY_ROBUST. Field reading: regime maps must be indexed by objective; the
  support-2 world is the unit-cost objective's.
- **QG-3 boundary prospective — POSITIVE_REGIME_PREDICTIONS_CONFIRMED**
  (`QG3_BOUNDARY_PROSPECTIVE_RESULTS.json`;
  `ORIONQG_QG3_BOUNDARY_PROSPECTIVE_POSITIVE_REGIME_PREDICTIONS_CONFIRMED__SPLIT_AND_
  BORROW_PREDICTED_BEFORE_DP__NOT_R6`, all boolean gates true): the R6R escalation is
  done — Track B staged 12 engineered instances under the frozen generator (quota met:
  4 predicted-split, 4 predicted-borrow, 4 donor-exact), predictions digest-stamped
  before any DP, and the DP confirmed the regimes and costs; Track A admitted 6 fresh
  real library batches. The predicate now carries confirmed prospective forecasts on
  all three branches of the regime map, not just the donor-exact exclusion branch.
- **QG-4 second family — TEMPLATE_TRANSFERRED** (`QG4_SECOND_FAMILY_RESULTS.json`,
  replay-verified bit-identical;
  `ORION_QG4_SECOND_FAMILY_TEMPLATE_TRANSFERRED__SIXLCU_PREP_SELECT_REGIME_GEOMETRY_ON_
  VERIFIED_DOMAINS__NOT_R6`): all four template stages instantiated on the frozen SixLCU
  PREP/SELECT family. Differently shaped geometry than TARE — local dominance refuted
  exactly at the 30 all-equal-column configurations (the family's trade currency);
  38,759/38,760 exhaustive-n2 instances are trades with a unique incumbent-exact instance
  ({XI,YI,ZI,IX,IY,IZ}); no strict sub-extension closes (both saturation axes must max
  out); yet an **exact pairs-only membership predicate P0 has zero error** on fit,
  held-out (two seeds incl. post-freeze 20260825) and exhaustive-n1 domains despite
  optimal witnesses needing size-six blocks. Cross-family findings: the exchange-refuted-
  at-characterizable-column → trade-currency → closed-form-predicate motif now has two
  independent instances; "boundary-is-low-order" is a candidate transferable principle;
  the field's visible frontier is families without exact finite referees.
- **QG-5 certified forecast — IDENTITY REFUTED ON A NEW INSTANCE** (a discovery;
  `QG5_CERTIFIED_FORECAST_RESULTS.json`, replay-verified: double-run canonical stdout
  byte-identical, receipt identical minus the non-canonical timing section;
  `QG5_FORECAST_IDENTITY_REFUTED__BOUNDARY_INSTANCES_REPORTED_VERBATIM__NOT_R6`):
  the three-family forecast min(C_R6L, C_D+, f_B) matched the unrestricted DP on
  9,261/9,261 exhaustive structured-n2 instances, all receipted chemistry rows, and
  239/240 of a fresh seeded panel — but one n=3 instance (serialized verbatim) has
  C_DP = 10 < 11 = all three family values. Localization (independently confirmed by the
  witnessed exact referee): the optimum uses a support-2 frame whose borrow home qubit
  lies *outside* the block's own target support — precisely the restriction the frozen
  B(t) family imposed — so this is a third elementary trade configuration, and
  simultaneously the first false positive for the R6Q predicate P1. The frozen
  borrow-family closed form f_B under-parametrizes the weight-2 trade at n=3; the two-trade
  *characterization* stands on the exhaustive n≤2 domains, while its closed-form
  completeness fails at higher n. Repair path known by theorem: R6S guarantees
  DP == D++ for all n, so a forecaster minimizing over the full support-≤2 family is
  provably exact — registered as the wave-2 lead lane (QG-5b).

## Closure decision (bound)

- **Harness-driven adjudication — SOLVED_VERIFIED: WAVE 1 SCIENTIFICALLY CLOSED**
  (`closure-adjudication/ADJUDICATION_TERMINAL_V3.json` + full workspace receipts in
  `closure-adjudication/adjudication-workspace-v3.tar.gz`; protocol frozen pre-run in
  `QG_WAVE1_CLOSURE_ADJUDICATION_PROTOCOL.md`). The question was posed to the generic
  ORION harness (host-driven recursive solve, this session servicing capabilities from
  committed receipts only); the terminal answer, on 20 verified claims, holds all three
  closure conjuncts: 5/5 lanes in charter closure modes with double-run replay-verified
  receipts; only the adjudication slot itself unbound; no post-outcome gate weakening
  (QG-5's `forecast_error_zero_everywhere=false` is the recorded refutation finding under
  its pre-frozen branch, not a weakened gate). Instrument honesty preserved verbatim: two
  earlier attempts terminated CANNOT_CHECK (V1 at insufficient resource bounds —
  `ADJUDICATION_TERMINAL_V1_CANNOT_CHECK.json`; V2 with the CURRENT_VOCABULARY route
  family uncovered) and are retained as negative records; the harness's fail-closed
  verifier also rejected two host evidence items (a non-verbatim charter paraphrase and a
  mis-sourced freshness item), which were excluded from claims. The verdict grants no
  scientific or novelty authority; it authorizes this packet's CLOSED status and binds
  the ledger below.

## Wave-2 residual ledger (inherited, receipt-localized)

- **R1 (lead) — QG-5b exact forecaster: DISCHARGED, FULL POSITIVE BRANCH**
  (`QG5B_EXACT_FORECASTER_RESULTS.json`, replay-verified: double-run canonical stdout
  byte-identical, receipt identical minus non-canonical timing;
  `ORIONQG_QG5B_EXACT_FORECASTER_THEOREM_BACKED_ZERO_ERROR__DPP_FAMILY_MIN__ENLARGED_
  BORROW_CLOSES__NOT_R6`; protocol frozen pre-outcome at `ad792082`). Q1: the
  theorem-backed forecaster F2(t) = full support-≤2-family minimum (no unrestricted DP
  call) is exact on all 9,547 DP-compared instances — the QG-5 refuting instance
  (F2 = 10 = C_DP), structured n=2 9,261/9,261, fresh panel 240/240, and all 45
  receipted chemistry rows by exact containment pinch. Q2: the single enlargement of
  the borrow family (phantom homes over the union target support) closes the
  closed-form identity — min(C_R6L, C_D+, f_B′) == C_DP everywhere, the refuting
  instance's B′ witness carries its phantom home outside the block's own support
  exactly as QG-5 localized, the F2-based donor predicate is exact (repairing P1's
  false positive), and **no fourth configuration exists on the verified domains**
  (residual gap 0). Q3: exact forecasting at median 16.4× DP speed (n=2: 45.4×). All
  14 hostile gates true (658 D++ + 611 B′ witnesses referee-verified, 0 failures).
  The two-trade taxonomy survives with the borrow family properly parametrized; the
  closed-form regime map is restored to exactness, now theorem-backed end to end on
  the unit-cost objective (QG-2's objective-indexing caveat stands).
- **R2 — objective-indexed sufficiency bounds.** Under O1 support-3 pays (C_DP 11 <
  C_D++ 13; 53 criticals): re-prove R6S-style bounds per objective.
  (`QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json`)
- **R3 — predicate-language enlargement.** No exact predicate exists in the frozen
  literal family under O1 (best re-induction: 273 errors). (QG-2 receipt)
- **R4 — feasible D++ chemistry referee under O1** at n = 8..12 (currently honestly
  UNRESOLVED on all 30 rows). (QG-2 receipt)
- **R5 — tightness witness for the QG-1 support-5 bound** (is 5 attained?).
  (`QG1_RANK2_ALL_N_RESULTS.json`)
- **R6 — third family without an exact finite referee**, plus formalization of the
  boundary-is-low-order candidate principle. (`QG4_SECOND_FAMILY_RESULTS.json`)
- **R7 — frozen hunt for a real trade-regime chemistry batch** (QG-3: all 90 real
  library matchings donor-exact; positive trade confirmations are synthetic-only).
  (`QG3_BOUNDARY_PROSPECTIVE_RESULTS.json`)
  **R7 is now instrumented by an independently authored lane** (issue #745, merged via
  PR #746, `164462bf`): a positive-forecast experiment with dual-harness custody —
  DP-forbidden stage-1 selector (scan cap 12 unread DUCC subjects), generic-harness +
  native typed-campaign admission on one sealed stage-1 digest, exact double-run
  referee gated on dual OPEN. Reconciliation notes: (a) that lane carries the label
  "QG-3" from its own charter; in this packet's registry it is the R7 lane — wave-1's
  QG-3 (boundary prospective, closed above) is a different, completed experiment.
  (b) Six of its twelve scan candidates (Benzene DUCC3 pVDZ/pVTZ 12q; 6E7O and 8E7O
  DUCC2/DUCC3 14q) already carry committed DP ground truth in
  `QG3_BOUNDARY_PROSPECTIVE_RESULTS.json` — all donor-exact, so its positive selector
  necessarily passes over them and can select only from the genuinely unread
  candidates 7–12; its internal custody is unaffected, but any positive terminal's
  "unseen subject" gate must be read against this packet's receipts, not only the
  R6R-era blob list frozen in its selector.

## Stop rules

Per the charter: each lane closes only by theorem, donor absorption, receipted
saturation, or cannot-check; refutations are first-class; no post-outcome gate changes;
the protected stretched-N2 subject remains sealed.
