# Runtime-Gated Novelty Analysis Contract V1

Status: **FROZEN BEFORE RUNTIME-GATED OUTCOMES**

Frozen: 2026-08-20

This contract makes the statistical/terminal logic for currently unavailable LLM/Lean experiments explicit before their run artifacts exist. Missing input yields `CANNOT_CHECK_*`; malformed or identity-inconsistent input yields `INVALID_*`; neither may be treated as positive evidence.

## Lane L — P9 LLM structure × scale × compute

Expected input: `inputs/P9_LLM_STRUCTURE_SCALING_RUNS_V1.json`.

Required:

- one architecture family;
- at least three checkpoints with strictly increasing parameter counts;
- same frozen item IDs/domains for R1 same-information and R2 typed-state arms;
- at least one identical inference-budget grid across all checkpoints/arms;
- target qualities frozen in input and restricted to the protocol's preregistered set;
- per-item correctness and generated-token accounting;
- equivalence and hostile-control gates all green.

Primary pooled effect is paired R2-R1 accuracy. Domain is the uncertainty block. Use 10,000 deterministic domain-block bootstrap resamples with seed `914031`.

`LLM_STRUCTURE_SCALING_FRONTIER_SUPPORTED` requires:

1. pooled R2-R1 `>0` at the frozen primary budget of every model size;
2. at the largest model/primary budget, domain-block bootstrap lower 95% bound `>0`;
3. at least 60% of domains non-negative at that cell;
4. at least one target quality `q` and common budget for which a strictly smaller R2 model and a larger R1 model both achieve `>=q` and the smaller R2 accuracy is at least the larger R1 accuracy;
5. all equivalence/token/order/symbol/leakage controls green.

A test-time-compute substitution is separately reported only if, for identical weights and a frozen q, R2 reaches q at a strictly smaller observed generated-token budget than R1.

## Lane N — P10 native-state incremental value

Expected input: `inputs/P10_NATIVE_STATE_PREDICTIONS_V1.json`.

Every row must bind transition ID, held-out module, true action, B1/B3/B4 predicted action and probability assigned to the true action. Coverage relative to the V2.1 transition population must be supplied.

Use 10,000 deterministic module-block bootstrap resamples with seed `914033`.

`P10_NATIVE_STATE_INCREMENTAL_VALUE_SUPPORTED` requires exactly the already-frozen gate:

- B4-B1 accuracy `>0`;
- module-block bootstrap lower 95% bound `>0`;
- >=60% evaluable modules non-negative;
- B4 multiclass log loss lower than B1;
- receipt/leakage/shuffle/near-duplicate controls green;
- eligibility coverage >=80%.

## Lane A — P10 proof-action abstraction phase diagram

Expected input: `inputs/P10_ACTION_ABSTRACTION_SEARCH_V1.json`.

Each theorem must have paired results for A0 atomic, A1 raw, A2 coarse-family, A3 effect-grounded and, when executable, A4 macro. Search algorithm, theorem manifest, verifier-call cap, action availability and stopping rules must be identical except for action representation.

The primary comparison is verifier-backed solve rate under the common call cap. Report calls per solved theorem only as a secondary efficiency metric.

`INTERMEDIATE_ACTION_ABSTRACTION_FRONTIER_SUPPORTED` requires:

1. A2 or A3 has the highest solve rate among all fully executable arms, allowing exact ties;
2. the chosen intermediate arm beats both A0 and A1 by a positive paired solve-rate difference;
3. a 10,000-resample theorem-paired bootstrap with seed `914035` gives lower 95% bound `>0` versus the better of A0/A1;
4. it does not use a higher verifier-call cap;
5. if A4 is executable, the intermediate arm is not lower in solve rate than A4 by more than 0.01 absolute;
6. all proof receipts validate.

If A4 cannot be executed, the result can be `BOUNDED_INTERMEDIATE_FRONTIER_WITHOUT_MACRO_BASELINE` but not standalone novelty.

## Lane F — same-information Lean feedback representation

Expected input: `inputs/P10_LEAN_FEEDBACK_REPAIR_V1.json`.

Each eligible failed proof attempt must have an equivalence receipt and paired F0/F1/F2/F3 repair outcomes under identical one-attempt budget and action/tool availability.

Primary contrast: F2 typed delta versus F1 same-information canonical text.

Use item-paired bootstrap, 10,000 resamples, seed `914037`.

`TYPED_LEAN_FEEDBACK_ACCESSIBILITY_SUPPORTED` requires:

1. all included F1/F2 diagnostic fact-multiset equivalence receipts pass;
2. F2 verified repair success > F1;
3. paired bootstrap lower 95% bound for F2-F1 >0;
4. no greater Lean-call or generated-token cap for F2;
5. raw F0 and dependency F3 remain reported regardless of sign;
6. all final repaired proofs verify under the frozen Lean identity.

## Lane G — P10 cross-revision structural transfer

Expected input: `inputs/P10_CROSS_REVISION_TRANSFER_V1.json`.

The target revision must have been selected before its outcomes. Report coverage and predictive performance separately.

Define absolute degradation from source-revision held-out performance to target-revision performance for B1 history and B4 state+dependency.

`STRUCTURAL_COORDINATES_CROSS_REVISION_ROBUSTNESS_SUPPORTED` requires:

1. target-revision eligibility coverage >=80% of the prospectively matched population;
2. B4 target accuracy > B1 target accuracy;
3. B4 absolute accuracy degradation is smaller than B1 degradation;
4. module/family-block bootstrap lower 95% bound for target B4-B1 >0;
5. no target-revision refitting for the primary endpoint;
6. all revision/toolchain/receipt identities pass.

## Cross-domain composition

No runtime-gated lane may be inferred from controlled logistic results. Programme-level cross-domain promotion requires an independently positive formal-domain result from Lane N/F/G or another prospectively frozen formal test, not merely existing P10 tactic-history transfer.
