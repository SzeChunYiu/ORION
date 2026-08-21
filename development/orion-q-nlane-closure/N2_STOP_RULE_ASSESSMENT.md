# ORION-Q N2 — stop-rule assessment for issue #675 (post-execution)

Date: 2026-08-21 (written after the F3/F4/F5 runs; the per-family protocols were frozen before outcomes)
Lane issue: #675; parent programme: #633; immutable prior negative: #671
Branch: `claude/orion-harness-verification-b17qdj`

## Receipts

| Family (#675) | Protocol (frozen pre-outcome) | Runner / receipt | Terminal |
|---|---|---|---|
| 1 multi-route regimes | — (absorbed) | MAX lane: `MAX_R4B_TARE_SPLIT_MAJORISATION_RESULTS.json`, `MAX_R5_N2_JOINT_INTERNAL_CONFIRMATION_RESULTS.json`, `MAX_R5B_N2_PROOF_OUTER_REPLAY_RESULTS.json` ("N2" there = nitrogen molecule, unrelated) | absorbed in spirit; no distinct N2-lane residual |
| 2 vector resources | — (absorbed) | same MAX receipts | absorbed in spirit; no distinct N2-lane residual |
| 3 partial evidence (QUERY / CANNOT_COMPARE / Pareto) | `N2_F3_PROTOCOL.md` | `nlanes/n2_f3_partial_evidence.py` -> `N2_F3_PARTIAL_EVIDENCE_RESULTS.json` | `N2_F3_PARTIAL_EVIDENCE_NO_RESIDUAL__EXACT_SYNTHETIC_ONLY` (honest negative; all hostile gates pass) |
| 4 access edits under NO_STRONGER_ORACLE | `N2_F4_PROTOCOL.md` (Amendment A1: LA2 made never-no-op) | `nlanes/n2_f4_access_edits.py` -> `N2_F4_ACCESS_EDITS_RESULTS.json` | `N2_F4_ACCESS_EDITS_NO_RESIDUAL__EXACT_SYNTHETIC_ONLY` (honest negative; laundering caught 60/60 + 60/60) |
| 5 held-out crossover prediction | `N2_F5_PROTOCOL.md` (Amendment A1: `c5` 0.8 -> 15.0, defective hostile control repaired) | `nlanes/n2_f5_crossover_prediction.py` -> `N2_F5_CROSSOVER_PREDICTION_RESULTS.json` | `N2_F5_CROSSOVER_PREDICTION_RESIDUAL_SUPPORTED__EXACT_SYNTHETIC_ONLY` (all gates pass) |

Key numbers: F3 — ORION mean loss 0.0663 vs best baseline (scalarized midpoint) 0.0166 on the primary world (ratio 3.99 against ORION); ORION perfect (loss 0, no abstention/query) on the hostile all-decidable world where the lazy abstainer loses 0.864. F4 — ORION win fraction 0.00 (its best chain is always the single `merge` edit, tying the best-single-edit baseline; mean scalar cost 258.88 vs B0 307.28, B2 259.89); both laundering attempts rejected on every instance; no admissible chain beat the forbidden spectral bound (mean 132.47 queries). F5 — held-out score ORION 0.9948 vs 1-NN 0.9167, majority 0.9167, linear 0.9271, oracle 1.0; crossover-location relative error 9.0e-16; broken-form world drops ORION to 0.4427 (hostile control bites).

## Stop rule of #675, applied

> closes only with `LOWER_BOUND_CLOSED` for a registered class or `DONOR_COMPLETE_AND_SUCCESSOR_SATURATED` after >=3 materially distinct successor route/resource formulations fail to leave an ORION residual.

- `LOWER_BOUND_CLOSED`: **not satisfied.** No new lower bound was proved; `TWO_ROUTE_ANALYTICALLY_CLOSED` (#671) remains the only analytic closure and remains a boundary condition, not a terminal.
- Count of materially distinct formulations failing to leave an N2-lane ORION residual: families 1 and 2 (absorbed by MAX without a distinct N2-lane residual) plus F3 and F4 (executed honest negatives) = **4 >= 3**. The literal count of the saturation clause is therefore **receipt-satisfied**.
- **However**, family 5 left a *supported* residual (prospective analytic crossover prediction beats all frozen baselines on held-out extrapolative regimes, with the hostile broken-form world bounding its authority). Declaring `DONOR_COMPLETE_AND_SUCCESSOR_SATURATED` while a registered successor holds a gate-passing residual would be dishonest saturation.

## Recommendation (no authority claim)

The lane should close not as a clean saturation but as: **4 of 5 registered formulations leave no residual; the single surviving residual (F5) is exact-synthetic, partly an artifact of a well-specified world (the mechanism's frozen feature library contains the true functional forms), and is explicitly bounded by the H2 functional-form-shift gate.** Either fold that named residual into #679/#698 for donor comparison against Predict-and-Conquer-style selection (the strong parent #675 already names), or record the stop rule as met with the F5 residual explicitly carried forward. Deciding which is the issue owner's call, not this harness's.

## Claim boundary

Everything above is exact-synthetic scope only: frozen proxy worlds, frozen accounting, frozen grids. No compiled-resource, hardware, novelty, or lower-bound authority. Honest negatives (F3, F4) are valid results under ORION discipline; both passed all their hostile/validity controls, so the negatives are about the mechanism's value, not about broken harnesses.
