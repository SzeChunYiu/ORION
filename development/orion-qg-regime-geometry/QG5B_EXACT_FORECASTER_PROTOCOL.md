# QG-5b exact forecaster protocol (wave-2 lead lane, residual R1)

Status: FROZEN before any outcome under this protocol was computed. Date frozen:
2026-08-21. Programme: ORION-QG (charter `PROGRAMME_CHARTER_V1.md`, issue #740).
Branch: `claude/orion-harness-verification-b17qdj`. Lane: QG-5b — the exact
support-<=2-family forecaster and the enlarged borrow family, repairing the two
residuals the QG-5 refutation localized (`QG_WAVE1_CLOSURE_PACKET.md`, ledger
entry R1): (i) the three-family closed-form forecast min(C_R6L, C_Dplus, f_B)
under-predicts C_DP on one fresh n=3 instance (C_DP = 10 < 11), and (ii) that
instance is the first false positive of the R6Q predicate P1. The repair path is
theorem-backed: MAX-R6S proves C_DP == C_Dxx (the full support-<=2 family D++)
for every n, so a forecaster that minimizes over D++ is provably exact.

Authority ceiling: NOT_R6 on every branch. No novelty credit, no donor credit,
no scientific-authority claim. The protected stretched-N2 subject
`N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt` is
never read (the frozen R6R eligibility already excludes the whole N2 molecule,
and the eq-N2 chemistry subject is read only through the blob-pinned frozen
batch machinery).

## Frozen machinery (imported UNMODIFIED, exactly as QG-5 did)

From `research/extensions/orion-q/`:
- `max_r6m_exact_three_tare2_shared_factor_dp` (r6m): `_synthetic_terms`,
  `donor_r6l_matching`, `exact_r6m_matching` (witnessed exact matcher),
  `perfect_matchings`, `_local_table`, `_F3`, receipt
  `MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json`.
- `max_r6o_enlarged_tag_donor_closure` (r6o): `dplus_pairs`,
  `dp_cost_n2_reader`, `dp_cost_frozen_configs`, `_letter_key`, `_local_code`,
  `_block_cache`, receipt `MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json`.
- `max_r6p_weight2_frame_donor_closure` (r6p): `dxx_search` (the independent
  exact D++ enumerator), `verify_dxx_witness` (independent witnessed referee
  through the frozen donor factor machinery), `_tables`, `F3`, pair-count
  guards.
- `max_r6q_regime_predicate` (r6q): `borrow_family_min` (frozen B(t)),
  `bind_training_to_receipt`, `simple_features`, `F3`, `INF`, `MATCHING`.
- `max_r6s_all_n_composition` (r6s): `bind_tables`, `config_cost`,
  `config_labels` (the exact configuration referee used to verify enlarged-
  borrow witnesses), theorem receipt `MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`.
- `max_r6f_donor_clifford_preconditioned_tare3` (r6f): `_frozen_batch`
  (blob-pinned chemistry admission).
- `max_r6_p10_candidate_blind_frame_optimizer` (p10): `base.SUBJECTS`, `wt`,
  `mul`, `symp`.
- `max_r6r_prospective_fresh_subject` (r6r): `pinned_tree_listing`,
  `eligible_candidates`, `try_admit`, `sha256_text`,
  `PROTECTED_STRETCHED_N2_PATH`, `EXCLUDED_MOLECULES`, receipt
  `MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json`.

From `research/extensions/orion-qg/`: `qg5_certified_forecast` (qg5):
`forecast` (the refuted three-family forecaster, reused verbatim so C_R6L,
C_Dplus, f_B, regime and P1 are computed by byte-identical code), `SEED_FRESH`
(20260826), receipt `QG5_CERTIFIED_FORECAST_RESULTS.json`.

No repository file is modified. All new code lives in
`research/extensions/orion-qg/qg5b_exact_forecaster.py`.

## The two objects under test

### F2(t): the theorem-backed exact D++ forecaster

F2(t) := C_Dxx(t) = the exact minimum over the FULL support-<=2 family D++,
computed by the frozen independent enumerator `r6p.dxx_search(target_pairs, n)`
(2 label orientations x all nonzero Tags via the Tag-relaxation identity x all
ordered anticommuting support-<=2 frame-Pauli pairs per block x 2 permutations,
joint minimum via the exact don't-care pattern min-transform). NO unrestricted
DP call anywhere in the F2 path. By the machine-checked R6S theorem
(C_DP == C_Dxx for every n, every six-tuple, every matching), F2 is expected
exact everywhere; any observed F2(t) != C_DP is a first-class refutation of the
lane premise and is serialized verbatim.

Regime rule (frozen): donor_exact iff F2 == C_R6L; else split iff
F2 == C_Dplus; else borrow iff F2 == f_Bprime; else "beyond_enlarged_family".

### B'(t): the enlarged closed-form borrow family

The frozen R6Q family B(t) restricts each phantom block's borrow home qubit
q_h to the block's OWN target support — exactly the restriction the QG-5
refuting instance defeats. B'(t) enlarges only that clause. Frozen definition
(everything else copied structurally from `r6q._borrow_block_options` /
`r6q.borrow_family_min`, re-implemented inside qg5b without modifying r6q):

- U := union of the supports of all six targets; E := the lowest-index qubit
  outside U if one exists (single empty representative), else absent.
- Tag sweep: q_t in U plus E (if present); Tag letter v in {1,2,3}; Tag
  S = v@q_t (weight-one Tag, +2 cost), identical to B(t).
- Per block j, options:
  - anchored (surcharge 0): frames (v@q_t, c@q_t), c in {1,2,3}\{v}, target
    permutation sigma in {0,1}; identical to B(t).
  - phantom (surcharge +2): comm frame m0@q_h, anti frame l@q_t * m1@q_h with
    l in {1,2,3}\{v}, m0 != m1 in {1,2,3}, sigma in {0,1}, and — the single
    enlargement — home q_h ranging over (U ∪ {E}) \ {q_t} for EVERY block
    (out-of-support homes admitted), instead of supp_j \ {q_t}.
- Restore letters evaluated on rel := sorted(U ∪ {q_t} ∪ {E}); per-class
  signature dedup as in B(t); the all-anchored corner is excluded (that is
  R6L, not borrow); at least one block phantom; value = min total
  (surcharges + branch F3 sums) + 2. If no feasible member exists,
  f_Bprime := INF (r6q.INF).

Containment B(t) subset-of B'(t) holds by construction (supp_j subset-of U);
hard-asserted per instance: f_Bprime <= f_B whenever f_B is not None.
Soundness hard-asserted per DP-compared instance: C_DP <= f_Bprime.

B' witness referee (hostile gate): the argmin member is reconstructed
explicitly (q_t, v, per-block kind/sigma/frames) and re-verified through the
committed R6S exact configuration referee: frames6 = (comm_j, anti_j) per
block, t6 with sigma applied, S = v@q_t, centrals = (1,1,1) (anti frame
central); `r6s.config_labels` must accept with labels (0,1) and
`r6s.config_cost` must equal f_Bprime exactly.

## Frozen panels (all DP-compared; runtime target < 25 min/run)

- Panel A — the QG-5 refuting instance, verbatim from the QG-5 receipt's
  `fresh_seeded_panel.nonzero_errors_verbatim[0]`: n=3, index 7, target_pairs
  (((3,6),(7,3)), ((7,3),(3,4)), ((0,3),(2,2))). Bound by equality against the
  receipt row (targets and all four values C_DP=10, C_R6L=C_Dplus=f_B=11).
  C_DP recomputed here twice: `r6o.dp_cost_frozen_configs` AND the witnessed
  `r6m.exact_r6m_matching` (checks must all pass); both must give 10 to bind.
- Panel B — the exhaustive structured n=2 slice: 21^3 = 9,261 instances,
  generator copied digit-for-digit from QG-5 (`r6o._letter_key` weight-one
  letters, unordered pair index triples). C_DP truth: `r6o.dp_cost_n2_reader`.
  Receipt binding: `r6q.bind_training_to_receipt` (equal_count 8775 and
  verbatim violating rows must bind).
- Panel C — the QG-5 fresh seeded panel: seed 20260826, 120 instances per n,
  n in {2,3} (240 total), generator copied digit-for-digit from QG-5
  (including per-instance cache clearing). C_DP truth:
  `r6o.dp_cost_frozen_configs`. Receipt binding: zero/nonzero counts must be
  239/1 against the QG-5 three-family values recomputed by `qg5.forecast`; the
  single nonzero row must match the receipt row verbatim (n=3, index 7); the
  QG-5 regime census recomputed from `qg5.forecast` must equal the receipt
  census {donor_exact 153, split 26, borrow 61}. Panel A's instance is
  index 7 of the n=3 half of this panel; it is additionally evaluated
  standalone as Panel A.
- Panel D — receipted chemistry rows (45): H4 (n=8, 15 matchings) and eq-N2
  (n=12, 15) via `r6f._frozen_batch` over `p10.base.SUBJECTS` (blob
  verified, source indices bound to the R6M receipt; C_DP := receipt C_R6M;
  C_R6L and C_Dplus recomputed and bound to the R6M/R6O receipts); Benzene
  DUCC2 cc-pVDZ 6Elec_6Orbs (n=12, 15) via the frozen R6R enumeration
  (pinned-tree listing digest bound to the R6R receipt, candidate selected as
  the unique eligible candidate whose blob equals the R6R subject blob,
  admission via `r6r.try_admit`, source indices bound; C_DP := receipt C_DP;
  C_R6L/C_Dplus/f_B bound against the receipt rows). The heavy DP is never
  re-run.

Frozen infeasibility disclosures (Panel D):
- A direct D++ sweep is infeasible at n >= 8 (the pattern min-transform space
  is 4^(2n)). F2 on Panel D is therefore obtained by the exact containment
  pinch, R6P precedent: C_DP <= C_Dxx <= C_Dplus with C_Dplus recomputed and
  C_DP receipt-bound; a row with C_Dplus == C_DP forces F2 = C_Dxx = C_DP
  (status PINCHED_EXACT); a row with C_Dplus > C_DP leaves F2 honestly
  UNRESOLVED there (its own outcome branch below). No approximation is ever
  reported as exact.
- f_Bprime is NOT computed on Panel D (runtime cap; the enlarged triple
  product over union-support homes at n=12 exceeds the budget). The Q2
  identity on Panel D is instead decided exactly by the R6L pinch: every
  Panel D row's receipt-bound C_R6L equals its C_DP (donor-exact receipts),
  so min(C_R6L, C_Dplus, f_Bprime) == C_DP iff f_Bprime >= C_DP, which is
  exactly the B' soundness gate (B' members are feasible grammar
  configurations; referee-verified on the sampled witnesses). A Panel D row
  with C_R6L != C_DP would break the pinch and is its own branch
  (Q2_UNRESOLVED_CHEMISTRY row, serialized verbatim).

Per-instance computed quantities (Panels A-C): C_DP (truth), F2 (with witness
on the frozen sample), C_R6L / C_Dplus / f_B / regime / P1 via `qg5.forecast`
verbatim, f_Bprime (with witness on the frozen sample). Panel D: C_DP
(receipt), C_R6L, C_Dplus, f_B via `qg5.forecast`, F2 by pinch.

## Frozen questions and outcome branches

### Q1 — theorem-backed exactness of F2

Zero-error criterion: F2 == C_DP on Panel A, all 9,261 Panel B instances, all
240 Panel C instances, and all 45 Panel D rows (via the pinch). Branches:
- Q1_ZERO_ERROR: criterion met everywhere.
- Q1_REFUTED_R6S_CONTRADICTION: any Panel A-C instance with F2 != C_DP, or
  any Panel D row where the pinch RESOLVES to F2 != C_DP. First-class
  refutation of the lane premise (and of the machine-checked R6S theorem's
  implementation); every such instance serialized verbatim (cap 100 per
  panel).
- Q1_PARTIAL_CHEMISTRY_PINCH_UNRESOLVED: zero error on Panels A-C but some
  Panel D row has C_Dplus > C_DP so F2 is not pinch-resolvable there; rows
  serialized verbatim.

### Q2 — the enlarged borrow family B'

Identity criterion: min(C_R6L, C_Dplus, f_Bprime) == C_DP on Panels A, B, C;
on Panel D the identity is decided by the R6L pinch as disclosed above.
Additional Panel A requirement: f_Bprime == 10 == C_DP (B' captures the third
configuration) and the enlarged predicate
P1'(t) := [C_Dplus == C_R6L] AND [f_Bprime >= C_R6L] must be False at Panel A
(repairing P1's false positive). Branches:
- Q2_ENLARGED_BORROW_CLOSES: identity holds on all panels AND Panel A
  requirements hold.
- Q2_RESIDUAL_GAP_FOURTH_CONFIGURATION: some Panel A/B/C instance has
  min(C_R6L, C_Dplus, f_Bprime) > C_DP. This is a discovery, not a failure:
  the SMALLEST counterexample — the first in the frozen enumeration order
  Panel A, then Panel B by instance_index, then Panel C by (n, index) — is
  serialized verbatim together with its D++ witness (from `r6p.dxx_search`
  want_witness, referee-verified), which localizes the fourth elementary
  trade configuration. All counterexamples serialized up to cap 100.
- Q2_UNRESOLVED_CHEMISTRY: identity holds on Panels A-C but some Panel D row
  has C_R6L != C_DP (pinch broken); rows serialized verbatim.

Note Q2_ENLARGED_BORROW_CLOSES additionally requires the Panel A P1'
repair; if the identity holds everywhere but f_Bprime > C_DP at Panel A
(i.e. exactness recovered only through C_R6L/C_Dplus, which is impossible at
Panel A since both equal 11 > 10 — listed for completeness), the outcome is
Q2_RESIDUAL_GAP_FOURTH_CONFIGURATION.

### Q3 — cost

On Panel C only: per-instance wall-clock of the unrestricted DP truth
(`r6o.dp_cost_frozen_configs`) versus the F2 forecaster (`r6p.dxx_search`,
target-independent per-(n, max_weight) tables warm — they carry no target
data; disclosed convention identical to R6P's table reuse) versus the QG-5
three-family forecast (`qg5.forecast`, caches cleared per instance as in
QG-5). Reported as median/percentile speedup statistics. Per the R6P
convention all timing lives ONLY in the RESULTS `timing` section and on
stderr; the canonical stdout line excludes it.

## Hostile gates (all boolean, frozen; failure of an integrity gate aborts)

1. `tables_bound`: r6s.bind_tables() all true; r6p.F3 == r6m._F3;
   r6q.F3 == r6m._F3; r6p pair counts {1:6, 2:120, 3:666} re-asserted.
2. `structured_receipt_bound`: r6q.bind_training_to_receipt equal_count and
   verbatim rows bound (Panel B).
3. `panel_bound_to_qg5_receipt`: Panel C counts 239/1, verbatim error row
   match, regime census match (as specified above).
4. `refuting_instance_bound`: Panel A receipt row match; both C_DP
   recomputations give 10; `exact_r6m_matching` witness checks all pass.
5. `chemistry_receipts_bound`: blobs verified; source indices, C_R6L, C_Dplus
   (and for Benzene also f_B and predicted_C_DP) equal to the committed
   R6M/R6O/R6R receipt values; R6R listing digest binds; protected
   stretched-N2 path absent from candidacy (hard assert).
6. `dxx_witness_referee_pass`: `r6p.verify_dxx_witness` passes on the frozen
   sample — Panel A always; Panel B instances with idx % 97 == 0 or
   F2 < C_Dplus; Panel C instances with index % 10 == 0 or F2 < C_Dplus.
7. `bprime_witness_referee_pass`: the R6S configuration referee accepts the
   B' argmin witness with exact cost equality on the frozen sample — Panel A
   always (witness serialized verbatim, including whether the home lies
   outside the block's own target support); Panel B idx % 191 == 0 or
   f_Bprime < min(C_R6L, C_Dplus); Panel C index % 10 == 0 or
   f_Bprime < min(C_R6L, C_Dplus). Witnesses only exist when f_Bprime < INF;
   infeasible-f_Bprime instances are exempt (counted).
8. `sandwich_and_soundness`: on every Panel A-C instance,
   C_DP <= F2 <= C_Dplus <= C_R6L and C_DP <= f_Bprime <= f_B (f_B finite) —
   hard-asserted inline.
9. `weight1_binding`: `r6p.dxx_search(..., max_weight=1) == C_Dplus` on the
   frozen sample Panel B idx % 210 == 0, Panel C index % 15 == 0.
10. `dp_exact_matcher_binding`: `r6m.exact_r6m_matching` (witnessed) equals
    the DP reader truth on the frozen sample Panel B idx % 1153 == 0, Panel C
    index % 24 == 0 (checks must all pass).
11. `p1_false_positive_reclassified`: at Panel A, P1 (recomputed via
    qg5.forecast) is True while C_DP=10 < 11=C_R6L, and F2 == 10, i.e. the
    D++ forecaster classifies the instance non-donor-exact; and the F2-based
    donor predicate [F2 == C_R6L] disagrees with P1 exactly there.
12. `f2_donor_predicate_exact`: [F2 == C_R6L] <-> [C_DP == C_R6L] on every
    Panel A-C instance and every pinch-resolved Panel D row (the repaired
    exact regime predicate).
13. `no_dp_call_in_forecast_path`: structural — the F2 path invokes only
    `r6p.dxx_search`; the B' path only the closed-form enumeration.
14. `protected_stretched_n2_unreachable`: hard-asserted (r6r exclusions).
15. Authority string contains NOT_R6 (hard assert).

Verbatim serialization cap: 100 rows per panel per error class. All caps,
samples, seeds and thresholds above are frozen now and may not be changed
after outcomes are seen; a refutation is reported under its pre-frozen branch,
never gate-weakened.

## Authority strings (frozen per branch; ceiling NOT_R6)

- Q1_ZERO_ERROR and Q2_ENLARGED_BORROW_CLOSES:
  `ORIONQG_QG5B_EXACT_FORECASTER_THEOREM_BACKED_ZERO_ERROR__DPP_FAMILY_MIN__ENLARGED_BORROW_CLOSES__NOT_R6`
- Q1_ZERO_ERROR and Q2_RESIDUAL_GAP_FOURTH_CONFIGURATION:
  `ORIONQG_QG5B_EXACT_FORECASTER_ZERO_ERROR__ENLARGED_BORROW_RESIDUAL_GAP_FOURTH_CONFIGURATION__NOT_R6`
- Q1_ZERO_ERROR and Q2_UNRESOLVED_CHEMISTRY:
  `ORIONQG_QG5B_EXACT_FORECASTER_ZERO_ERROR__ENLARGED_BORROW_CHEMISTRY_PINCH_UNRESOLVED__NOT_R6`
- Q1_REFUTED_R6S_CONTRADICTION (any Q2):
  `ORIONQG_QG5B_DPP_EXACTNESS_REFUTED__R6S_THEOREM_CONTRADICTION_REPORTED_VERBATIM__NOT_R6`
- Q1_PARTIAL_CHEMISTRY_PINCH_UNRESOLVED (any Q2):
  `ORIONQG_QG5B_EXACT_FORECASTER_PARTIAL__CHEMISTRY_PINCH_UNRESOLVED__NOT_R6`

## Receipts and replay discipline

`qg5b_exact_forecaster.py` emits one canonical stdout line
`ORIONQG_QG5B_EXACT_FORECASTER=<canonical json>` (sorted keys, compact
separators, NO timing fields, per R6P) and writes
`QG5B_EXACT_FORECASTER_RESULTS.json` (indented, sorted keys) whose content is
the canonical result plus a `timing` section (the only non-canonical part).
The run is executed twice in full; the two canonical stdout lines must be
byte-identical and the two RESULTS files identical after deleting the `timing`
section. The protocol file's sha256 is embedded in the result. Runtime target
< 25 minutes per run; the sizing that meets it (the Panel D caps) is disclosed
above and frozen.
