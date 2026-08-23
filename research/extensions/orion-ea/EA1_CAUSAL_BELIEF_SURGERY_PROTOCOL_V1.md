# EA-1A Causal Belief Surgery — protocol V1

**Status:** FROZEN BEFORE MODEL OUTCOMES  
**Parent:** #957 / EA-0A  
**Primary question:** does learning a typed epistemic delta provide incremental protected value beyond strong same-information state/memory/revision baselines?

No result-bearing model run may alter this protocol without a new version. The exact kernel/generator may be corrected for implementation defects only with preserved history and a new digest.

## 1. Scientific discriminator

Given a pre-state `E_t`, an evaluator-controlled change `I_t`, and a model-visible observation of that change, predict the **minimal typed delta** `ΔE_t` needed to reach the exact valid post-state.

```text
(E_t, I_t) --model--> proposed ΔE_t
(E_t, I_t) --exact kernel--> gold ΔE_t*
```

The model is scored on `ΔE_t` before final-answer generation.

This deliberately differs from:

- answering a question about the latest fact;
- deleting stale text;
- merely detecting that a conflict exists;
- letting an exact graph engine choose the delta and crediting the LLM;
- free-form “reflection” about what should change.

The central object is **proposal fidelity for state transition**.

## 2. Two separate claims must not be conflated

### EA-1I — information/structure value

Some restricted views should be provably non-identifying. Exact hostile pairs establish which state coordinates are necessary.

### EA-1A — architecture/update-learning value

All serious architecture arms receive **the same typed information**. Native state may claim incremental value only over equivalent typed serialization/external state under matched resources.

A positive EA-1I does not imply EA-1A.

## 3. Exact families

Each family is generated with opaque reminted identities and evaluator-side family/gold metadata.

### F1 — sparse descendant retraction

State:

```text
E1 SUPPORTS C1
C1 REQUIRES C2
E2 SUPPORTS C3
```

Intervention: retract `E1`.

Gold:

- `E1 -> RETRACTED`;
- `C1 -> RETRACTED`;
- `C2 -> RETRACTED`;
- preserve `E2`, `C3`.

Purpose: basic dependency surgery with unrelated-state preservation.

### F2 — independent support preservation

State:

```text
E1 SUPPORTS C1
E2 SUPPORTS C1
C1 REQUIRES C2
```

Intervention: retract `E1` while `E2` remains active.

Gold:

- retract `E1` only;
- preserve `C1` and `C2`.

Purpose: defeat over-broad rollback and “invalidate all descendants” policies.

### F3 — active defeater

State:

```text
E1 SUPPORTS C1
D1 DEFEATS C1
D1 initially non-active
```

Intervention: activate `D1`.

Gold:

- activate `D1`;
- retract `C1` and its hard dependents;
- preserve unrelated state.

Purpose: separate support loss from explicit defeating evidence.

### F4 — scoped failure reopening after material representation change

State:

```text
representation semantic key = A
F1 = ACTIVE failure scoped to A
F1 DEFEATS M1
M1 = BLOCKED
```

Intervention: move to representation semantic key `B` with a registered material correspondence event.

Gold:

- set new representation;
- `F1 -> STALE`;
- `M1 -> ACTIVE` if no other blocker remains.

Purpose: test ORION-style scoped negative history. The result does not say the method is scientifically validated; it says the old failure is no longer an active blocker in the new exact-world semantics.

### F5 — remint is not semantic change

State is identical to F4, but the new representation has a new occurrence id with the **same semantic key A**.

Gold:

- set representation occurrence only;
- keep `F1 = ACTIVE`;
- keep `M1 = BLOCKED`.

Purpose: hostile anti-reopen control. Surface/identity change must not launder a failed method.

### F6 — obligation reopening under representation change

State:

```text
representation semantic key = A
O1 = ACTIVE obligation scoped to A, transportable = false
O1 REQUIRES C1
```

Intervention: material change `A -> B`.

Gold:

- new representation;
- `O1 -> UNKNOWN`;
- `C1 -> UNKNOWN`;
- no automatic refutation or acceptance.

Purpose: state revision must carry obligation semantics; a representational change cannot silently reuse an old certificate.

### F7 — transportable obligation control

Same as F6 except `O1.transportable = true` under the exact-world contract.

Gold:

- new representation only;
- preserve `O1` and `C1`.

Purpose: prevent broken-shut behavior where every representation change destroys all prior knowledge.

### F8 — unknown prerequisite propagation

State:

```text
E1 REQUIRES C1
C1 REQUIRES C2
```

Intervention: `E1 -> UNKNOWN` rather than retracted.

Gold:

- `E1`, `C1`, `C2 -> UNKNOWN`;
- no `RETRACTED` claim unless a refuting condition exists.

Purpose: distinguish lack of current entitlement from scientific refutation.

### F9 — no-op / irrelevant intervention

Intervention changes an unrelated node or remints a non-load-bearing surface token.

Gold:

- only the directly changed coordinate when applicable;
- preserve all task-relevant state.

Purpose: anti-overreaction control.

## 4. Information lattice

Freeze multiple model views for diagnostic ceilings.

### V0 — surface transcript

Opaque natural-language/event descriptions with graph semantics removed.

### V1 — topology

Nodes and unlabeled connectivity only.

### V2 — typed state

Node/edge types and statuses, but failure/obligation scope omitted.

### V3 — full EA-1 state

All `EpistemicState.v0` fields except evaluator family/gold metadata.

Required hostile collisions:

- F4 vs F5 collide under a representation-id-only/surface view but separate by semantic key/correspondence state;
- F6 vs F7 collide when obligation transportability is hidden;
- F1 vs F2 can be constructed to collide when independent support edges are hidden;
- UNKNOWN vs RETRACTED cases collide when status semantics are removed.

For balanced exact hostile pairs, the empirical deterministic ceiling of any colliding fingerprint class must be computed before learned-model comparison. Any learned arm exceeding its selected-view ceiling invalidates the run as leakage/evaluator mismatch.

## 5. Model-visible identity rules

- world id, family id and gold delta are evaluator-only;
- node/edge identifiers are opaque content-derived tokens;
- train/dev/test identity namespaces are disjoint;
- candidate delta operation ordering is permuted independently of gold;
- surface labels are reminted across splits;
- representation ids do not encode semantic keys;
- semantic keys are themselves opaque categories in model payloads and are permuted between generated corpora where possible;
- no filename/path/domain label may reveal family.

## 6. Baseline ladder

Execute in this order.

### B0 — nulls

- majority delta;
- no-change policy;
- invalidate-all policy;
- candidate-position policy.

### B1 — direct sequence model

Direct Transformer/LLM over the full typed serialization.

### B2 — explicit CoT/scratchpad

Same information, allowed textual deliberation, final output constrained to the delta schema.

### B3 — recurrent/latent state

Strong current latent/recurrent baseline where runnable, informed by Thinking States / SST / T²MLR / Coconut-class mechanisms. Match serial compute/state capacity as faithfully as practical.

### B4 — state-commitment baseline

A State-Commitment-style training arm or faithful protocol adaptation that distinguishes temporary reasoning from committed answer state, but does not receive a special EA delta kernel beyond the same evaluator API.

### B5 — typed serialization + exact kernel

The model predicts only the primitive intervention/update interpretation; a donor-complete exact revision engine computes consequences. This is a very strong baseline and may close EA-1A.

### B6 — external graph/versioned-memory baseline

Grounded-Continuation/Kumiho/StateMem-style external structured state with exact dependency semantics.

### B7 — rollback-repair baseline

DGRR-style dependency-guided rollback/preservation, adapted only where task mapping is faithful.

### B8 — EA typed-delta predictor + exact kernel

The proposed learnable object: model emits a typed minimal delta, kernel validates/applies it.

### B9 — native epistemic-state architecture

Only implement/run if B8 leaves a predeclared residual that cannot be explained by sequence/latent/external-state baselines. A native pathway is not needed merely to complete EA-1.

## 7. Resource matching

For B1–B9 report or control:

- base model/backbone;
- train examples;
- finetuning/RL tokens;
- parameters introduced;
- recurrent/serial compute steps;
- context tokens;
- persistent-state bytes;
- exact-kernel calls;
- retrieval calls;
- LLM calls;
- wall-clock/latency where reliable.

Do not describe a system as representation-superior if its effect can be explained by more information, more recurrence, a larger model or extra exact computation.

## 8. Primary endpoint

Primary endpoint is **micro-averaged exact delta operation F1** over the protected full-state test split, with operation equality defined on `(kind, target, value)` after evaluator canonicalization.

Primary success for EA typed-delta learning requires all of:

1. B8 delta F1 > strongest applicable learned same-information baseline by a prospectively meaningful margin fixed before final runs;
2. preservation error lower than the same baseline;
3. no information-ceiling violation;
4. false reopen rate on F5 below the frozen bound;
5. obligation laundering rate on F6 below the frozen bound;
6. UNKNOWN/refutation confusion below the frozen bound;
7. final-state reconstruction from proposed delta passes the exact kernel on the required fraction;
8. result survives identity/surface remint holdout.

The effect-size margin/statistical interval is frozen only after pilot variance is known; protected test remains unopened until then.

## 9. Mandatory secondary endpoints

- delta exact-match rate;
- node-status macro F1;
- descendant retraction precision/recall;
- unrelated-state preservation rate;
- false reopen rate;
- missed reopen rate;
- false stale-failure transfer rate;
- obligation laundering rate;
- broken-shut obligation reopen rate;
- UNKNOWN vs RETRACTED confusion matrix;
- final-state exact reconstruction;
- downstream verified action/task correctness;
- cost/latency/resource vector;
- per-family results F1–F9.

## 10. Hostile tests

A study is invalid if any of the following can explain the effect:

- gold encoded in node ids/order;
- native arm gets a richer state than serialized arm;
- exact engine chooses the whole delta for EA but not baseline;
- F4/F5 semantic-change distinction is exposed by a human-readable “new semantics” label unavailable to controls;
- train/test share world templates with stable positional identifiers;
- model invalidates all descendants and looks good because preservation is not scored;
- model never reopens failures and looks safe because F4 is absent;
- model always reopens after representation id changes and F5 is absent;
- all nontransportable obligations happen to belong to one token/type;
- final answer is correct despite an invalid state delta and state metrics are hidden;
- learned arm gets more inference compute;
- protected test is used for model or margin selection.

## 11. Stop/narrow rules

- If B5/B6/B7 reaches the exact ceiling with no learned residual, terminal `EA1_DONOR_EXACT_REVISION_SUFFICIENT`; do not add a native model.
- If B8 matches but does not beat typed serialization, terminal `EA1_TYPED_SERIALIZATION_SUFFICIENT` for architecture while retaining any useful training/protocol result.
- If only F4–F7 show a residual, narrow the scientific object to scoped failure/obligation transport rather than “epistemic autoregression”.
- If gains disappear under remint/domain holdout, terminal `EA1_SHORTCUT_DEPENDENT`.
- If the exact kernel is responsible for all downstream gains, credit the kernel/donor rather than the learned proposal model.
- If no learned arm improves delta fidelity or efficiency, close EA native learning at this scope; EA-5 is not licensed as a rescue.

## 12. Quantum pre-transfer

The first cross-domain transfer is frozen separately in `EA_QUANTUM_CROSSOVER_V1.md`. Quantum items reuse the same delta vocabulary and metrics so a positive cannot come from inventing a different evaluator after seeing EA-1 results.

## 13. Allowed terminals

- `EA1_DONOR_EXACT_REVISION_SUFFICIENT`;
- `EA1_TYPED_SERIALIZATION_SUFFICIENT`;
- `EA1_TYPED_DELTA_LEARNING_INCREMENTAL_VALUE`;
- `EA1_FAILURE_OBLIGATION_INTERACTION_ONLY`;
- `EA1_NATIVE_STATE_ESCALATION_LICENSED`;
- `EA1_SHORTCUT_DEPENDENT`;
- `REFUTED`;
- `CANNOT_CHECK`.

No terminal here establishes self-expanding language, general LLM reasoning superiority, or scientific discovery.
