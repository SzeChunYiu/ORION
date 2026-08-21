# ORION-Q programme closure packet — 2026-08-21

Status: **CLOSED 2026-08-21** — every bound slot below carries its committed receipt, and
every scientific receipt referenced here has been independently replay-verified
bit-identical in this session (R6I/K/L/M/N/O; all N1–N4 lane receipts per
`../orion-q-nlane-closure/REPLAY_VERIFICATION_LEDGER.md`; the campaign drive workspace;
the full-suite JUnit report by digest). Reopen triggers in §3 remain in force.
Branch: `claude/orion-harness-verification-b17qdj`
Programme issues: #633 (reopened recovery programme), #679 (MAX), #698 (MAX-R4 endpoint),
lane issues #674–#677, infrastructure #725, absorbed children #694/#695.
Authority: development record only. No receipt referenced here grants scientific, novelty,
merge, or R6 authority; every terminal below is bounded by its own protocol's scope.

## 1. What this closure claims — and what it does not

Claimed: the registered ORION-Q programme questions have each reached a receipted terminal
under prospectively frozen protocols: positive where gates passed, negative where they
failed, absorbed where a donor owned the object, and saturated where the registered
successor space was exhausted. Negative results are preserved as first-class outcomes.

Not claimed: real-quantum novelty, R6 promotion, or superiority beyond each receipt's
declared scope (most terminals are exact-synthetic or frozen-open-subject scope).

## 2. The receipted ladder (all paths repo-relative)

### 2.1 Infrastructure (issue #725) — COMPLETE
- `packages/orion-research-harness/` — shared host-capability harness; 98/98 tests green.
- Live host-driven E2E: `development/orion-research-harness/E2E_HOST_DRIVE_VERIFICATION_2026-08-21.md`
  (+ full receipt workspace `e2e-2026-08-21-receipts/`).
- Campaign layer + ORION-Q adapter driving the full R6 chain inside the harness:
  `development/orion-q-max-r0/HARNESS_R6_DRIVE_VERIFICATION_2026-08-21.md` and
  `harness-r6-drive-2026-08-21/` (terminal `R6_VERDICT`, all authority booleans false).
- Recovery mechanics added after a live defect: `orion-harness retry-failed`
  (failed receipts archivable, successful receipts immutable).

### 2.2 MAX ladder R0–R5 (issues #679, #694, #695, #698)
- R0 heterogeneous arena: `research/extensions/orion-q/MAX_R0_HETEROGENEOUS_ARENA_RESULTS.json`.
- R1 operator arbitration: `MAX_R1_OPERATOR_ARBITRATION_RESULTS.json`
  (`..._SUPPORTED__EXACT_SYNTHETIC`).
- R2 known-operator transfer: honest negative (generic baseline sufficient).
- R3B obligation transport: `MAX_R3B_JOINT_OBLIGATION_BINDING_RESULTS.json` — the issue's own
  B5 absorption contingency fired (P7/P4 joint binding owns the object; exact 1/2 donor
  ceiling vs 1.0 joint on 4,800 hostile cases).
- R3E protected self-evolving skills: both terminals earned in exact-synthetic scope
  (`MAX_R3E_PROTECTED_SKILL_ADMISSION_RESULTS.json`,
  `MAX_R3E_PERSISTENT_SKILL_STREAM_RESULTS.json`, summary `MAX_R3E_MILESTONE.md`).
- R4A/R4B complete; R4C regime-limited H2 negative + H2O positive
  (`MAX_R4D_H2O_DUCC_CONFIRMATION_RESULTS.json`, locked public source, CI receipt).
- R5: proof replay green, outer accounting projection-mixed
  (`MAX_R5B_N2_PROOF_OUTER_REPLAY_RESULTS.json`, `FULL_R5_NOT_SUPPORTED`).

### 2.3 R6 chain — executed to a frozen negative, then saturated
- Native campaign chain N0→N1→N2→P10 candidate→prospective gate, driven end-to-end by the
  harness: `harness-r6-drive-2026-08-21/` — `R6_EARNED = NO`,
  `MAX_R6_NOT_EARNED__PROTECTED_SUBJECT_NOT_OPENED`; the protected stretched-N2 subject was
  never opened by any lane, ever.
- Frozen successor grammar lanes, all implemented and executed 2026-08-21 with
  replay-verified bit-identical receipts:
  - R6L donor: `MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_RESULTS.json` — positive
    (absorption; Erratum-1 floors H4=12/N2=12; post-absorption 8/9; rotation 9).
  - R6I: `MAX_R6I_EXACT_RANK2_SHARED_TAG_DP_RESULTS.json` — negative (ties R6H donor on
    all 10 partitions, both subjects).
  - R6K: `MAX_R6K_EXACT_RANK2_SHARED_TAG_RESTORE_FACTOR_DP_RESULTS.json` — negative
    (collapses onto R6J donor everywhere; 4 panels × 54 configs DP-vs-brute exact).
  - R6M: `MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json` — negative
    (C_R6M = C_R6L on all 30 matchings; strict 0/15 both subjects).
- Saturation statement: within the frozen open subjects, every registered residual coupled
  representation optimization beyond the absorbed donors has zero exact value — the DPs
  saturate onto the donor envelopes.

### 2.4 Explanatory closure — R6N executed: half theorem, half discovery

`MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json` (replay-verified bit-identical; protocol frozen
before outcome with the Tag-repair coupling explicitly declared as the analytic gap):

- **Theorem-grade half.** Frame-support dominance is machine-verified with **zero
  violations over 688,041,472 local configurations** across the R6I and R6M grammars
  (max savings/cost ratio 1.0, ties only), and the weight-one equality holds on **all 50
  recorded chemistry optima**. The R6I/R6K/R6M collapses are thereby *explained*: no exact
  DP could ever profit from spread frame support.
- **Discovery half.** The full donor-family closure is **refuted exactly at the declared
  gap**: synthetic R6M instance `n2_b` has unrestricted DP = 8 < weight-one-Tag donor
  family = 9, witnessed by weight-one frames anchored at *different* qubits with a
  **weight-2 shared Tag (Y⊗Y)** — a regime the R6L donor grammar cannot express, which both
  frozen chemistry subjects happen to avoid. The post-gate diagnostic shows the enlarged
  family (weight-one frames + unrestricted minimal Tag) recovers the DP optimum there.
- Authority: `MAX_R6N_SUPPORT_DOMINANCE_REFUTED__NEW_REGIME_FOUND__NOT_R6`.

**R6O executed — closure doubly refuted; converse regime characterized.**
`MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json`
(`MAX_R6O_ENLARGED_TAG_DONOR_CLOSURE_REFUTED__SECOND_NEW_REGIME_FOUND__NOT_R6`):

- D+ (weight-one frames, arbitrary anchors, minimal unrestricted Tag) **repairs the R6N
  gap** — the refuting instance `n2_b` now ties the DP at 8 — and D+ strictly beats the old
  R6L donor on 34/240 random instances; the containment sandwich DP ≤ D+ ≤ R6L held on
  every computed instance, and DP == D+ closes exhaustively on all 4,096 n=1 instances.
- But a **second, converse regime** exists: on 486/9,261 exhaustive structured-n2 and
  73/240 random instances the DP strictly beats D+ by spending a weight-2 frame Pauli at
  the central multiplier to compress the shared Tag to weight one and improve
  Restore-factor alignment (smallest counterexample serialized: DP 5 < D+ 6). R6N traded
  Tag weight for frame anchors; R6O's regime trades frame weight for Tag compression —
  inexpressible in any weight-one-frame family.
- Chemistry is unchanged: DP == D+ == R6L on all 30 recorded matchings, so weight-one
  donors remain exactly optimal on the frozen subjects.
- Honest position after R6O: exact family closure doubly refuted; the two named questions
  were then executed the same day.

**R6P executed — closure restored at support two on all verified domains.**
`MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json`
(`MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_VERIFIED__FAMILY_CLOSURE_RESTORED_AT_SUPPORT_TWO_ON_
VERIFIED_DOMAINS__NOT_R6`, all 12 gates true, byte-identical double run):

- D++ (frame Paulis of global support ≤ 2, minimal shared Tag) equals the unrestricted DP
  on every verified domain: 5/5 R6N panels, exhaustive n=1 (4,096), the FULL exhaustive
  structured n=2 slice (9,261), the 240-instance random panel, and all 30 chemistry
  matchings (quadruple tie DP == D++ == D+ == R6L; H4 8/11, N2 9/10).
- All 559 previously violating instances re-derived, cross-checked against the R6O
  receipt row-by-row, and closed instance-by-instance with fully re-verified witnesses —
  each gap explained by the single weight-2-at-central Tag/factor trade. **No third
  regime exists on any verified domain.**
- The two-mechanism account (R6N Tag-anchor coupling + R6O weight-2 frame-for-Tag trade)
  is thereby sufficient on all checked domains. Open: the all-n theorem (whether the
  dominance inequality composes across qubits to exclude support-≥3 frames analytically);
  chemistry closure rests on the exact containment pinch DP ≤ D++ ≤ D+ ≤ R6L rather than
  a direct sweep.
**R6Q executed — exact regime predicate; two-trade completeness identity.**
`MAX_R6Q_REGIME_PREDICATE_RESULTS.json`
(`MAX_R6Q_REGIME_PREDICATE_EXACT__TWO_TRADE_CHARACTERIZATION_ON_VERIFIED_DOMAINS__NOT_R6`,
all gates true, byte-identical double run):

- The predicate P(targets) — donor-exact iff neither trade is profitable, decided by
  closed-form family minima with **no DP call**: (1) no split gain, C_R6L == C_D+;
  (2) no borrow gain, f_B ≥ C_R6L over the algebraically forced borrow family (weight-2
  frame on the central branch purchasing a weight-one Tag). **Zero classification errors
  on 9,741 instances**: exhaustive structured n=2 (9,261), the R6O held-out panel (240,
  bound row-by-row), a fresh-seed panel generated after P was fixed (240), and all 30
  chemistry matchings. An independent 3-literal exhaustive induction converged to the
  same two clauses.
- **Completeness identity (theorem candidate):** C_DP == min(C_R6L, C_D+, f_B) on all
  9,741 instances — the two discovered trades are jointly complete for the DP's advantage
  over the donor family on every verified domain, and the remaining proof obligation is
  sharply localized (rewrite any weight-≥2 witness into one of the three families without
  cost increase; the protocol's forced-form derivation already covers the single-borrow
  shape).
- Chemistry explained structurally: the recorded DUCC batches are pure-Z with heavily
  overlapping supports, so the shared anchor realizes all alignment and neither trade can
  pay its +2 surcharge (Gsplit = 0 on all 30 matchings; f_B strictly above C_R6L).
**R6R executed — PREDICTION CONFIRMED on an unseen subject.**
`MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json`
(`MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_PREDICTION_CONFIRMED__TWO_TRADE_PREDICATE_HELD_ON_
UNSEEN_SUBJECT__NOT_R6`, all gates true): the fresh subject was selected by a rule frozen
before any coefficient was read (blob-pinned at the library's frozen commit), the
two-trade predicate's regime prediction was staged and printed BEFORE any ground-truth
computation, and the exact R6M DP then confirmed the prediction on every matching. This is
the programme's first prospective, pre-registered structural forecast — the strongest
evidence form the framework produces.

**R6S executed — ALL-N THEOREM MACHINE-CHECKED.**
`MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`
(`MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED__SUPPORT3_NEVER_PAYS__DXX_EQUALS_DP_
ALL_N__NOT_R6`, all gates true, byte-identical double run, 52.7s):

- For every n, target configuration, matching, permutation and central choice of the
  frozen R6M grammar, frame Paulis of support ≥ 3 never strictly pay, so **D++ equals the
  unrestricted DP unconditionally**. The proof replaces Tag-repair bookkeeping with an
  F₂²-pigeonhole zero-sum-subset exchange (repair never needed), reducing everything to
  one 18,432-case exhaustive inequality (0 violations) plus a three-line combinatorial
  lemma (43,688 class tuples checked; the only failing patterns are exactly the four
  w=2 configurations that realize the R6O trade — the weight-2 boundary is now
  *delineated*, not just observed).
- Corroboration: 70/70 DP == D++ on fresh n=3/n=4 panels; 210 seeded exchange descents
  with predicted-vs-observed ΔC equality on all 899 steps.
- Scope limits preserved: the frozen R6M grammar and support-count objective only; the
  R6I rank-2 grammar and the three-family completeness identity remain domain-bounded;
  no novelty or R6 authority.

The R6 lane's mathematical arc is complete: weight-1 collapse explained, the weight-2
trade characterized and delineated, nothing beyond weight 2 for any n — a closed,
receipted theory of the family.

### 2.5 N-lane recoveries (issues #674–#677) — ALL EXECUTED 2026-08-21

All protocols under `development/orion-q-nlane-closure/`; scripts and receipts under
`research/extensions/orion-q/nlanes/`; every receipt determinism-verified by re-run.

- **N1 (#674)**: families A/C/D fresh re-executions — parent-sufficient negatives
  (`N1A_SYMBOLIC_SYNTHESIS_PARENT_SUFFICIENT`, `N1C_TYPED_FAILURE_STATE_VALUE__VOI_POLICY_
  PARENT_SUFFICIENT` with the bounded typed-failure-state positive intact: typed−unscoped
  +0.0271 [+0.0248,+0.0296], exact tie with the ideal VOI donor at 0.9866,
  `N1D_CANONICAL_TRANSFORM_PARENT_SUFFICIENT`); family B FIRST execution
  (`N1B_LIBRARY_LEARNING_SUFFICIENT` — ORION's trace-free growth matches the parent's reach
  but a length-prior compressor variant reproduces the macro, so the donor closes it); and
  the machine-checked lower bound `LOWER_BOUND_CLOSED_FOR_FINITE_COMPLETE_CLASS`
  (53,248 comparisons, 0 violations). **#674's stop rule is receipt-satisfied on both
  branches** (saturated successor set AND formal class lower bound).
- **N2 (#675)**: F3 partial-evidence honest negative (hedged set answers lose 0.0663 vs
  0.0166); F4 access-edit cost negative with perfect laundering safety (120/120 rejections);
  F5 prospective crossover prediction **residual supported** (0.9948 vs 0.9271 best
  baseline; crossover-location error ~9e-16; functional-form-shift control bites at 0.4427).
  4-of-5 disposition with the F5 residual named for carry-forward
  (`N2_STOP_RULE_ASSESSMENT.md`). The carried residual was then given its donor
  comparison (F5B): **mixed** — the Predict-and-Conquer-style model-selection donor
  absorbs the residual on the well-specified world, while the candidate stays ahead only
  on the misspecified world
  (`N2_F5B_MIXED__CANDIDATE_AHEAD_ON_MISSPECIFIED_ONLY__EXACT_SYNTHETIC_ONLY`), so F5's
  surviving value is precisely robustness to functional-form misspecification.
- **N3 (#676)**: all four registered families residual-confirmed
  (`N3{A,B,C,D}_RESIDUAL_CONFIRMED_EXACT_SYNTHETIC`) with donors correctly deferring in the
  donor-sufficient worlds and every hostile trap caught (spec mutation, unresolved
  obligations, correction-gate transfer, keyed permutation). The lane's registered
  `DONOR_OWNS_PARAMETRIC_SYNTHESIS` terminal is unreachable per its own receipts.
- **N4 (#677)**: all six registered families now independently executed and positive
  (family 3, remint/receipt-transport, closed standalone:
  `N4_F3_TYPED_REMINT_TRANSPORT_SUPPORTED__EXACT_SYNTHETIC` — typed transport beats
  re-derive-from-scratch in the mixed regime at zero committed failures, stale
  carry-forward punished at 99.5% failure rate in the hostile regime, and the re-derive
  baseline ties exactly where remints are unnecessary). The original five:
  (typed-prior VOI 71% of oracle utility; scoped reopening beats never/always/unscoped in a
  two-regime hostile matrix; interval-dominance-targeted verification 2.3× over random;
  full-chain laundering detection recall 1.000 / FPR 0.000 incl. deep splices;
  decision-coupled probing with the info-gain baseline correctly decoy-trapped).
  **The classical full-knowledge negative does not recursively extend to partial knowledge
  on these constructions.**

Cross-lane synthesis: donors own the representation/optimization questions (N1, R6 family);
ORION's typed partial-knowledge state owns the epistemic-regime questions (N2-F5, N3, N4).
This division emerged from receipts, not design.

## 3. Reopen triggers

This closure reopens if: a violating configuration refutes the support-dominance lemma in a
regime the R6 protocols cover; a new donor is found that changes any absorption verdict; a
materially new method-language move (outside the R6B..R6M grammar family) is frozen and
earns a strict point; the protected stretched-N2 subject is legitimately released by a new
pre-outcome freeze; or any N-lane receipt fails independent replay.

## 4. Bound suite state

- Harness package: 98/98.
- Full main suite on this branch (confirmation run, 2026-08-21): **3,835 passed,
  0 failures, 11 skipped** (3,846 collected; 35m21s; Python 3.11, git 2.43).
  This run postdates and confirms the four failure-cluster repairs recorded in the
  residual campaign: the p1 derived-floor boundary, the p2 3.12-only f-string, the
  evidence-kernel `--no-lazy-fetch` version gap (20 tests), and the two derived-record
  drifts (CANNOT_CHECK inventory, P9/P10 publication manifest).
