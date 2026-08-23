# N-Lane Replay Verification Ledger

Independent replay verification of every ORION-Q N-lane receipt.

- **Date of verification:** 2026-08-21
- **Environment:** Python 3.11.15 (GCC 13.3.0, linux), NumPy 2.4.6
- **Method:** Each runner script was executed in place from
  `research/extensions/orion-q/nlanes/` with a clean git tree. The single
  `ORIONQ_*` receipt line was extracted from stdout, its JSON payload parsed,
  and compared for canonical equality (`json.dumps(..., sort_keys=True)`)
  against the committed `*_RESULTS.json` file. Afterwards
  `git -C /home/user/ORION status -s` was checked for any modification to a
  RESULTS file (several scripts rewrite their RESULTS file on run; a
  byte-identical rewrite is the expected deterministic outcome).

## Results

| # | Runner script | Receipt file | Exit | Replay == saved | Wall (s) | Terminal |
|---|---|---|---|---|---|---|
| 1 | `n1a_parameterized_schema_invention.py` | `N1_A_PARAM_SCHEMA_RESULTS.json` | 0 | true | 0.17 | `N1A_SYMBOLIC_SYNTHESIS_PARENT_SUFFICIENT` |
| 2 | `n1b_failure_conditioned_grammar_growth.py` | `N1_B_GRAMMAR_GROWTH_RESULTS.json` | 0 | true | 4.37 | `N1B_LIBRARY_LEARNING_SUFFICIENT` |
| 3 | `n1c_costly_verification_voi.py` | `N1_C_COSTLY_VERIFICATION_RESULTS.json` | 0 | true | 5.53 | `N1C_TYPED_FAILURE_STATE_VALUE__VOI_POLICY_PARENT_SUFFICIENT` |
| 4 | `n1d_representation_frame_edit.py` | `N1_D_REPRESENTATION_EDIT_RESULTS.json` | 0 | true | 0.47 | `N1D_CANONICAL_TRANSFORM_PARENT_SUFFICIENT` |
| 5 | `n1_lower_bound.py` | `N1_LOWER_BOUND_RESULTS.json` | 0 | true | 0.21 | `LOWER_BOUND_CLOSED_FOR_FINITE_COMPLETE_CLASS` |
| 6 | `n2_f3_partial_evidence.py` | `N2_F3_PARTIAL_EVIDENCE_RESULTS.json` | 0 | true | 0.22 | `N2_F3_PARTIAL_EVIDENCE_NO_RESIDUAL__EXACT_SYNTHETIC_ONLY` |
| 7 | `n2_f4_access_edits.py` | `N2_F4_ACCESS_EDITS_RESULTS.json` | 0 | true (minus `per_instance`; see note) | 16.17 | `N2_F4_ACCESS_EDITS_NO_RESIDUAL__EXACT_SYNTHETIC_ONLY` |
| 8 | `n2_f5_crossover_prediction.py` | `N2_F5_CROSSOVER_PREDICTION_RESULTS.json` | 0 | true | 0.17 | `N2_F5_CROSSOVER_PREDICTION_RESIDUAL_SUPPORTED__EXACT_SYNTHETIC_ONLY` |
| 9 | `n3_a_symbolic_induction.py` | `N3_A_SYMBOLIC_INDUCTION_RESULTS.json` | 0 | true | 1.03 | `N3A_RESIDUAL_CONFIRMED_EXACT_SYNTHETIC` |
| 10 | `n3_b_obligation_expansion.py` | `N3_B_OBLIGATION_EXPANSION_RESULTS.json` | 0 | true | 31.36 | `N3B_RESIDUAL_CONFIRMED_EXACT_SYNTHETIC` |
| 11 | `n3_c_operator_induction.py` | `N3_C_OPERATOR_INDUCTION_RESULTS.json` | 0 | true | 0.75 | `N3C_RESIDUAL_CONFIRMED_EXACT_SYNTHETIC` |
| 12 | `n3_d_representation_variables.py` | `N3_D_REPRESENTATION_VARIABLES_RESULTS.json` | 0 | true | 0.46 | `N3D_RESIDUAL_CONFIRMED_EXACT_SYNTHETIC` |
| 13 | `n4_a_unknown_voi.py` | `N4_A_UNKNOWN_VOI_RESULTS.json` | 0 | true | 4.08 | `N4_A_TYPED_VOI_SUPPORTED__EXACT_SYNTHETIC` |
| 14 | `n4_b_stale_receipt_reopening.py` | `N4_B_STALE_RECEIPT_REOPENING_RESULTS.json` | 0 | true | 0.51 | `N4_B_SCOPED_REOPENING_SUPPORTED__EXACT_SYNTHETIC` |
| 15 | `n4_c_interval_pareto.py` | `N4_C_INTERVAL_PARETO_RESULTS.json` | 0 | true | 0.77 | `N4_C_TARGETED_INTERVAL_PARETO_SUPPORTED__EXACT_SYNTHETIC` |
| 16 | `n4_d_laundering_detection.py` | `N4_D_LAUNDERING_DETECTION_RESULTS.json` | 0 | true | 0.03 | `N4_D_CHAIN_TRANSPORT_LAUNDERING_DETECTION_SUPPORTED__EXACT_SYNTHETIC` |
| 17 | `n4_e_active_experiments.py` | `N4_E_ACTIVE_EXPERIMENTS_RESULTS.json` | 0 | true | 0.48 | `N4_E_DECISION_COUPLED_SELECTION_SUPPORTED__EXACT_SYNTHETIC` |

**Totals: 17/17 verified, 0 failures.**

## Authority strings

| Lane | Authority (from receipt) |
|---|---|
| N1A | `N1A_DIAGNOSTIC__NO_P10_AUTHORITY__NO_NOVELTY_AUTHORITY__EXACT_SYNTHETIC_ONLY` |
| N1B | `N1B_DIAGNOSTIC__NO_P10_AUTHORITY__NO_NOVELTY_AUTHORITY__EXACT_SYNTHETIC_ONLY` |
| N1C | `N1C_DIAGNOSTIC__NO_P10_AUTHORITY__NO_NOVELTY_AUTHORITY__EXACT_SYNTHETIC_ONLY` |
| N1D | `N1D_DIAGNOSTIC__NO_P10_AUTHORITY__NO_NOVELTY_AUTHORITY__EXACT_SYNTHETIC_ONLY` |
| N1 lower bound | `N1_LOWER_BOUND__BENCHMARK_CLASS_CLOSURE_ONLY__EXACT_SYNTHETIC_ONLY` |
| N2 F3 | `exact_synthetic_frozen_world_only; not compiled-resource, hardware, or novelty authority` |
| N2 F4 | `exact_synthetic_frozen_accounting_only; not compiled-circuit, hardware, or novelty authority` |
| N2 F5 | `exact_synthetic_frozen_world_only; not measured-implementation, hardware, or novelty authority` |
| N3 A–D | `exact_synthetic_bounded__no_real_quantum_no_novelty_no_p10_authority` |
| N4 A–E | (no `authority` field in schema; terminal string above carries the `__EXACT_SYNTHETIC` scope) |

## Notes

1. **N2 F4 receipt-line scope.** `n2_f4_access_edits.py` deliberately prints its
   `ORIONQ_N2_F4_ACCESS_EDITS=` receipt with the bulky `per_instance` array
   stripped (`receipt = {k: v for k, v in r1.items() if k != "per_instance"}`,
   line 400), while the saved `N2_F4_ACCESS_EDITS_RESULTS.json` retains it. A
   naive whole-object comparison of receipt line vs. saved file therefore
   differs on exactly the key `per_instance`. Verified explicitly: the replay
   receipt line is canonically equal to the saved file minus `per_instance`,
   AND the script rewrote its full RESULTS file (including `per_instance`)
   byte-identically (git shows no diff), so the full receipt — `per_instance`
   included — replays deterministically. Recorded as PASS, not a mismatch.
2. **RESULTS files rewritten in place.** All 17 scripts write their RESULTS
   file on run. After all replays, `git status -s` showed **no modification to
   any file under `research/extensions/orion-q/nlanes/`** — every rewrite was
   byte-identical to the committed receipt. No determinism failures.
3. **Unrelated concurrent activity observed.** During verification an untracked
   file `research/extensions/orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json`
   appeared (mtime 2026-08-21 08:41 UTC), produced by
   `max_r6o_enlarged_tag_donor_closure.py` (itself modified at 08:33 UTC by a
   concurrent session, not by this verification). None of the 17 N-lane runners
   reference or write that file; it is outside the N-lane receipt set and was
   left untouched. It does not affect any verdict above.
4. Each script emitted exactly one `ORIONQ_*` line on stdout and exited 0.
   Several scripts (e.g. N2 F4, N3 lanes) internally run their pipeline twice
   and gate on self-determinism; those internal gates also passed, consistent
   with the committed receipts.
