# P9 unified I/A/C/M resource-ledger protocol V2

**Programme:** #977
**State:** `FROZEN_BEFORE_EXECUTION`
**Role:** close the P9 gap item *unified resource accounting with an authoritative CI receipt*. V2 supersedes `P9_UNIFIED_RESOURCE_LEDGER_PROTOCOL_V1.md` for execution while keeping its vector schema, field names and information-preservation semantics unchanged.

## Audit of the V1 accounting (why V2 exists)

The V1 builder was inspected before this protocol was frozen. Four defects:

1. **Hidden fitted state.** `M_state` counted only the fitted access-model parameters. The fitted `StandardScaler` coordinates were omitted: every digits arm hides the 64-feature scaler's 128 fitted coordinates, and the `D-I` `INFORMATION` arm hides an intervention-specific 64-feature scaler (128 coordinates) on top of its logistic parameters.
2. **Zero inference touches in the exact domain.** every `B-*` arm emitted `C_infer=0`, hiding the frozen base readout's single coordinate touch per example.
3. **Zero transform for `B-C` `ACCESSIBILITY`.** the frozen intervention serializes/reorders the local-map coordinates; V1 recorded `A_transform=0`, hiding that work.
4. **No re-derivation and no bound receipt.** decisions were hardcoded literals; the causal diagnostic was never re-executed under the ledger, no per-cell matched-resource comparison existed, and no result receipt (run id, artifact id, artifact SHA-256) was committed.

V2 repairs 1–3 by rule and 4 by construction. None of these repairs may change a quality value, a quality target, a registered cost, a prediction, a protected gold, the `D-A` protected `CANNOT_CHECK` cell, or the protected Qwen scaling negative.

## Frozen source authority

- causal protocol: `P9_CAUSAL_DIAGNOSTIC_PROTOCOL_V1.md`;
- causal result receipt: `P9_CAUSAL_DIAGNOSTIC_RESULT_RECEIPT_V1.md` (primary receipt SHA-256 `2408d028de6ecb4f174433fba8291de84c4af5b6e5ff71870536c38e7f0c9313`);
- frozen decisions that the V2 re-derivation must reproduce exactly:

| Task | Probe prediction | Protected gold |
|---|---|---|
| `D-A` | `ACCESSIBILITY` | `CANNOT_CHECK` |
| `D-I` | `INFORMATION` | `INFORMATION` |
| `B-I` | `INFORMATION` | `INFORMATION` |
| `B-A` | `ACCESSIBILITY` | `ACCESSIBILITY` |
| `B-C` | `COMPUTATION` | `COMPUTATION` |

The V2 builder must import and re-execute the frozen executor `run_causal_diagnostic_v1.py` (splits, seeds, models, targets, registered costs) rather than re-authoring it. Hardcoding outcome numbers in V2 is prohibited; qualities must come from execution.

## Vector schema (unchanged from V1)

`R9 = (I_sem, A_dim, A_transform, M_state, C_fit, C_infer, C_explicit, R_registered)` with the V1 field semantics, plus the corrected computation rules:

- `M_state` = **all** fitted coordinates of the arm: access-model parameters plus fitted preprocessing coordinates where the arm fits a scaler (`2 * n_features`). A `base_state_fitted_coordinates` field per digits task discloses the base scaler shared identically by every arm of that task.
- `C_infer` = per-example access-mechanism coordinate touches: `A_dim` for linear access, support-vector coordinate count for RBF SVC, and `1` for every exact-domain arm (the frozen base readout touches exactly one coordinate per example; constant within a cell so it cannot bias within-cell comparisons but is no longer hidden).
- `A_transform` for `B-C` `ACCESSIBILITY` = 7 (serialize/reorder 3 affine maps x 2 coordinates + input).
- `C_fit` = `n_train * A_dim` where a learned access mechanism is fit, else 0.
- `C_explicit` keeps the frozen registered operation counts: `B-I` 4/3/8, `B-A` 0/0/1, `B-C` 0/0/7 for INFORMATION/ACCESSIBILITY/COMPUTATION.

Pre-registered exact-domain vectors `R9` (I_sem, A_dim, A_transform, M_state, C_fit, C_infer, C_explicit, R_registered):

| Task | Intervention | I_sem | A_dim | A_transform | M_state | C_fit | C_infer | C_explicit | R_registered |
|---|---|---|---|---|---|---|---|---|---|
| B-I | INFORMATION | 4 | 4 | 0 | 0 | 0 | 1 | 4 | 8 |
| B-I | ACCESSIBILITY | 3 | 3 | 3 | 0 | 0 | 1 | 3 | 2 |
| B-I | COMPUTATION | 3 | 3 | 0 | 0 | 0 | 1 | 8 | 12 |
| B-A | INFORMATION | 2 | 2 | 0 | 0 | 0 | 1 | 0 | 8 |
| B-A | ACCESSIBILITY | 2 | 2 | 1 | 0 | 0 | 1 | 0 | 2 |
| B-A | COMPUTATION | 2 | 2 | 0 | 0 | 0 | 1 | 1 | 12 |
| B-C | INFORMATION | 7 | 7 | 0 | 0 | 0 | 1 | 0 | 8 |
| B-C | ACCESSIBILITY | 7 | 7 | 7 | 0 | 0 | 1 | 0 | 2 |
| B-C | COMPUTATION | 7 | 7 | 0 | 0 | 0 | 1 | 7 | 12 |

Digits-domain vectors are fit-dependent (`n_train = 1078`): logistic `M_state = 650` for 64-feature arms and `20` for 1-feature arms before scaler correction; SVC `M_state = C_infer = support-vector coordinate count`. `D-A` all arms add the shared base scaler (128). `D-I` `INFORMATION` `M_state = 650 + 128`; `D-I` `ACCESSIBILITY` `M_state = 20 + 2`; `D-I` `COMPUTATION` adds the shared 1-feature base scaler (2).

**Erratum (pre-execution, 2026-08-23).** Two `R_registered` cells in the table above were transcribed as `4` where the frozen rule `R_registered = COST[intervention]` with `INFORMATION = 8` requires `8`: `B-A` `INFORMATION` and `B-C` `INFORMATION`. The correction is fully determined by the frozen `COST` dictionary of `run_causal_diagnostic_v1.py`, was made before any workflow run of this protocol completed (the sole queued run was cancelled and superseded), and touches no quality value, no target, no prediction and no protected gold. The builder and the independent checker implement `R_registered = COST[intervention]` throughout and never read this table.

## Re-derivation under matched full accounting

For each of the five task families and each split (probe, protected):

1. re-execute the frozen diagnostic and take the per-intervention qualities;
2. re-derive the split decision with the frozen rule: among interventions with quality >= frozen target choose minimum `R_registered`; if none reaches target the decision is `CANNOT_CHECK`;
3. attach the full corrected `R9` vector to every arm.

**Survival endpoints** (the causal-diagnostic conclusion under matched full accounting):

- re-derived probe predictions equal the frozen predictions in all five cells;
- re-derived protected golds equal the frozen golds in all five cells;
- diagnostic accuracy remains `4/5` and generic `UNCERTAINTY_ESCALATE_COMPUTE` accuracy remains `1/5`;
- the `D-A` protected cell remains `CANNOT_CHECK` (a quality-transport failure; no cost rule can alter it);
- diagnostic false compute-escalation count remains 0 and generic remains 4.

**Vector-dominance disclosure** (separate from survival): for each split and cell, the selected arm must not be strictly dominated on the seven physical coordinates by another target-reaching arm of the same cell (dominance = `<=` on all of I_sem, A_dim, A_transform, M_state, C_fit, C_infer, C_explicit and `<` on at least one). Any dominance finding is reported per cell and named; it does not silently pass, does not change the frozen scientific outcome, and is recorded in the receipt.

**Matched per-cell comparison:** for every cell emit the full vectors of the diagnostic's deployed arm and the generic heuristic's arm (`COMPUTATION`, or the base arm when base quality already meets target), their per-coordinate deltas, and the coordinates the abstract `R_registered` conceals (`A_transform + M_state + C_fit + C_infer + C_explicit` totals per arm). No arm gets hidden compute; no scalar exchange rate is derived.

## Terminals

- `P9_UNIFIED_RESOURCE_LEDGER_V2_GREEN`: all V1 GREEN conditions under corrected accounting + re-derivation reproduces the frozen five-cell decisions + all survival endpoints hold + deterministic byte replay + independent checker green + receipt bound to the actual workflow run (run id, artifact id, artifact ZIP SHA-256).
- `P9_UNIFIED_RESOURCE_LEDGER_V2_SURVIVAL_FAIL`: any survival endpoint fails; the moved cells are named. The frozen causal-diagnostic receipt remains authoritative and unchanged; the failure is the accounting result.
- `P9_UNIFIED_RESOURCE_LEDGER_V2_CONTRADICTION`: a dominance finding exists; cells named, disclosed in the receipt, frozen outcome unchanged.

A GREEN terminal closes accounting completeness for the bounded P9 causal-diagnostic headline only. It does not establish a universal resource exchange rate, does not repair the `D-A` `CANNOT_CHECK` cell, and does not touch the protected Qwen scaling negative.

## Authority boundary

Post-outcome accounting only. This protocol may not change any scientific outcome, quality target, intervention semantics, registered selection cost, protected causal gold, predicted intervention, the `D-A` protected `CANNOT_CHECK` cell, the wine null cell, or the Qwen scaling negative. The negative Qwen scaling result must not be repaired or re-run.
