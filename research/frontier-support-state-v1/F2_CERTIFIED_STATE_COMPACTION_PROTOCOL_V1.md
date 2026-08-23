# Frontier F2 — Certified State Compaction Protocol V1

Status: **FROZEN BEFORE OUTCOMES**

Frozen: 2026-08-20

## 1. Question

Can a long interaction history be replaced by a much smaller state object that is *machine-certified* to preserve every declared future task outcome, and does this reduce the sample/context burden of a fixed downstream learner?

This is not a generic `summaries help` experiment. The load-bearing object is an exhaustive future-behavior certificate.

## 2. Finite environment

State has 10 Boolean coordinates:

- relevant: `q0..q4`;
- nuisance: `n0..n4`.

Initial state is all zeros.

Available actions:

1. `R0`: `q0 ^= 1`
2. `R1`: `q1 ^= q0`
3. `R2`: `q2 ^= q1`
4. `R3`: `q3 ^= q2`
5. `R4`: `q4 ^= q3`
6. `N0`: `n0 ^= 1; n1 ^= n0`
7. `N1`: rotate `(n0..n4)` right by one position

Nuisance coordinates never influence relevant-coordinate transitions and never enter the reward.

Task reward after a queried future action sequence is

`Y = 1[ q0 + q1 + q2 + q3 + q4 >= 3 ]`.

The future query horizon is exactly `H=3`. Every query is one of the `7^3=343` action sequences of length 3.

## 3. State representations

For a generated history of length `L`:

### T — TRANSCRIPT
The full ordered one-hot action sequence of length `L`. No current-state coordinates are supplied.

### H4 — HEURISTIC_LAST4
Only the final 4 actions. This is deliberately lossy and is not expected to be sufficient.

### F — FULL_STATE
All 10 current Boolean state coordinates.

### C — CERTIFIED_STATE
Only `(q0..q4)`.

### I — INVALID_QUOTIENT
Only `(q0..q3)`; drops `q4`. It is a hostile negative control and must fail the exact certificate.

The future query is appended identically to every learner arm.

## 4. Exact sufficiency certificate

Before any learner outcome is generated:

1. enumerate all `2^10=1024` finite states;
2. enumerate all 343 future queries;
3. compute each state's 343-bit future reward signature;
4. group states by `C=(q0..q4)` and require every member of a group to have exactly the same future reward signature;
5. group states by `I=(q0..q3)` and require at least one group to contain two distinct future reward signatures.

Positive certificate terminal:

`CERTIFIED_STATE_EXACT_FUTURE_EQUIVALENCE`

Negative-control terminal:

`INVALID_QUOTIENT_COUNTEREXAMPLE_FOUND`

If either condition fails, the learning experiment is invalid and must not run.

This certificate is only for the frozen environment/action set/horizon/reward. It is not a universal losslessness claim.

## 5. Dataset

History lengths: `L in {8, 16, 32}`.

For each `L`, generate independent train/test histories using NumPy PCG64 seeds derived from the fixed strings:

- train: `frontier-f2-train-v1|L`
- test: `frontier-f2-test-v1|L`

History actions are iid uniform over the seven actions.

Each history is paired with one uniformly sampled future query during training. The protected test contains 8192 independently generated `(history, query)` pairs per `L`.

Training sizes:

`n in {256, 512, 1024, 2048, 4096, 8192, 16384}`.

No test example may be used for early stopping or hyperparameter choice.

## 6. Fixed learner

Primary learner for all arms: `sklearn.neural_network.MLPClassifier` with

- hidden layers `(64,64)`;
- activation `relu`;
- solver `adam`;
- `alpha=1e-4`;
- learning rate `1e-3`;
- batch size `128`;
- max iterations `300`;
- early_stopping `False`;
- random_state `914211`.

Inputs are binary one-hot/Boolean vectors scaled to `{0,1}`. The architecture/hyperparameters are identical across arms; only input dimensionality/representation differs.

Secondary deterministic comparator: random forest with 256 trees, fixed seed `914213`, reported descriptively only. It may not rescue a failed primary terminal.

## 7. Primary endpoints

For each `L` and arm:

- protected test accuracy at every training size;
- smallest training size reaching accuracy >=0.90;
- smallest training size reaching accuracy >=0.95;
- input dimensionality;
- serialized token/byte surrogate length from a frozen canonical textual renderer.

Define `n90(R,L)` as the first observed training size reaching 0.90.

## 8. Frozen success gate

The experiment earns

`CERTIFIED_STATE_COMPACTION_ACCESSIBILITY_SUPPORTED`

only if all are true:

1. exact `C` certificate passes with zero violations;
2. invalid `I` certificate produces at least one counterexample;
3. at `L=32`, `C` protected accuracy at `n=16384` is >=0.95;
4. at `L=32`, `C` is non-inferior to `F` within 0.01 accuracy at `n=16384`;
5. `n90(C,32)` is observed and <= 0.5 * `n90(T,32)` if `T` reaches 0.90; if `T` never reaches 0.90, `C` must reach 0.90 by `n<=4096`;
6. `C` input dimension is strictly smaller than `F` and transcript input grows with `L` while `C` remains constant;
7. `H4` is not allowed to be called certified even if its sampled accuracy is high.

If the exact certificate passes but the learner/sample-efficiency gate does not, terminal is

`CERTIFIED_STATE_EXISTS_BUT_ACCESSIBILITY_GATE_NOT_MET`.

## 9. Strongest allowed claim

If positive:

> In the frozen finite environment, a five-bit quotient state is exhaustively certified to preserve every declared three-step future reward outcome of the ten-bit world state. Relative to replaying raw histories, that certified state materially reduces the learning/context burden for a fixed downstream learner while preserving protected predictive quality.

Forbidden wording:

- `lossless for all future tasks`;
- `minimal state` unless a separate minimality proof is supplied;
- `LLM result`;
- `new bisimulation theorem`.

## 10. Follow-up bridge

Only after this controlled terminal is frozen may the certificate methodology be instantiated in P9-like procedural worlds, Lean proof states, or coding-agent environments. Real-system state may be called `certified` only if an equivalence proof/checker covers the declared future behavior class.
