# ORION-QG wave-1 closure packet

Status: UNDER ASSEMBLY — becomes the wave-1 closure record when every slot carries its
receipt and the harness-driven closure decision is recorded.
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

## Closure decision (bound slot)

- [SLOT] Harness-driven wave-1 closure adjudication: after all five lanes land, the
  question "is QG wave 1 scientifically closed, and what does wave 2 inherit?" is posed
  through the harness (dual-instrument where warranted), and the decision receipt is
  recorded here with the residual ledger for wave 2.

## Stop rules

Per the charter: each lane closes only by theorem, donor absorption, receipted
saturation, or cannot-check; refutations are first-class; no post-outcome gate changes;
the protected stretched-N2 subject remains sealed.
