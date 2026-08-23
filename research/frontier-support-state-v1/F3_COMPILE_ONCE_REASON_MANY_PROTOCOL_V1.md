# Frontier F3 — Compile Once, Reason Many Protocol V1

Status: **FROZEN BEFORE OUTCOMES**

Frozen: 2026-08-20

## 1. Question

Can a world/session be compiled once into an answer-blind reusable state so that a smaller solver answers many future queries at lower amortized cost than repeated direct reasoning by a larger solver?

The scientific target is **amortization into representation**, not weight distillation or replaying a memorized skill.

## 2. Non-negotiable query-blind rule

For every evaluation world `W`:

1. reveal `W` to the compiler;
2. run the compiler once and freeze state `Z(W)`;
3. hash and seal `Z(W)`;
4. only then reveal the downstream query set `Q_1...Q_m`.

The compiler receives no query text, answer label, target index, or evaluator feedback. Any refresh/update after query reveal is counted as a new compilation and invalidates the primary amortization arm.

## 3. Controlled world family

Use generated relational worlds with:

- 32 typed entities;
- 48 binary relations;
- 12 typed constraints/invariants;
- 8 nuisance surface aliases;
- one exact canonical relational graph/state.

Every world has a verbose flat/event serialization and a canonical typed state that are deterministically generated from the same latent world.

Downstream questions are generated *after compilation* from five frozen families:

1. relation reachability;
2. constraint satisfaction after a local mutation;
3. invariant preservation;
4. scoped history/order query;
5. exact terminal-condition query.

Each world supports `m in {1,2,4,8,16,32}` downstream queries. At least four query families must appear in every `m>=8` bundle.

## 4. Arms

### LD — LARGE_DIRECT
Large solver receives the raw flat world plus each query independently.

### SD — SMALL_DIRECT
Small solver receives the raw flat world plus each query independently.

### LS — LARGE_SUMMARY_TO_SMALL
Large compiler produces free-form summary once; small solver receives frozen summary plus each query.

### LT — LARGE_TYPED_TO_SMALL
Large compiler produces a typed state once; small solver receives frozen typed state plus each query.

### ET — EXACT_TYPED_TO_SMALL
An exact deterministic compiler produces the canonical typed state once; small solver receives it plus each query. This is an upper-bound/reference arm and may be available only in controlled domains.

The model family/sizes for real LLM execution are frozen separately before any model outcome. Controlled classical execution may use fixed learners as a prior mechanistic tranche but cannot authorize the LLM claim.

## 5. State contract

Typed compiler schema must contain only world/session information independent of future query identity:

- entities and types;
- relations;
- constraints/invariants;
- relevant scoped history/state transitions;
- provenance/unknown markers.

Forbidden fields include evaluator labels, query IDs, precomputed answers, `likely_question`, answer candidates, or any future-query-specific retrieval.

A leakage checker scans schema keys and values and reconstructs the fact set against the exact latent world in the controlled phase.

## 6. Cost accounting

Report separately:

- compiler input tokens;
- compiler output tokens;
- compiler wall time;
- compiled-state bytes/tokens;
- downstream solver input/output tokens per query;
- number and size of model calls;
- tool/retrieval calls if any;
- total wall time.

For model `a` serving `m` queries,

`TotalCost(a,m) = CompileCost(a) + sum_j SolveCost(a,j)`.

Primary amortized cost is

`A_m = TotalCost / m`.

Do not collapse different native units into money/FLOPs unless the conversion is frozen before outcomes. Pareto comparisons are primary.

## 7. Quality

Primary quality = exact downstream query success averaged per world, with world-block bootstrap uncertainty.

A compiled arm must be non-inferior to `LARGE_DIRECT` within absolute margin 0.02 to qualify for a cost crossover claim.

Report worst query-family accuracy and worst-world failure count. A pooled mean cannot hide a query-family collapse.

## 8. Primary crossover

Let `m*` be the smallest preregistered `m` where:

1. `LT` quality is non-inferior to `LD` within 0.02 with bootstrap lower bound above `-0.02`;
2. `LT` amortized native model-token cost per query is strictly lower than `LD`;
3. total large-model calls for `LT` are exactly one per world while `LD` uses one per query;
4. state leakage checks are zero;
5. the same frozen state supports all query families in the bundle.

If no `m*` is observed by 32 queries, the amortization terminal fails.

## 9. Secondary structural test

Compare `LS` versus `LT` at identical compiler/solver model identities. This asks whether a typed reusable state is more robust than free-form summarization, not whether compilation itself works.

Required hostile controls:

- key/order permutation of typed state;
- opaque entity renaming;
- summary length matching where practical;
- state fact-set audit;
- no state refresh.

## 10. Frozen terminals

Positive primary:

`ANSWER_BLIND_STATE_COMPILATION_AMORTIZES_REASONING`

Positive compilation but no crossover:

`REUSABLE_STATE_SUPPORTED__NO_AMORTIZED_COST_CROSSOVER`

Leakage/mutable-state failure:

`INVALID_COMPILE_ONCE_PROTOCOL`

No quality support:

`COMPILED_STATE_QUALITY_GATE_NOT_MET`

## 11. Strongest allowed claim

If the positive primary terminal is earned:

> A query-blind state compiled once from a world/session can amortize part of repeated reasoning: the same frozen state supports unseen downstream queries with large-direct-noninferior quality while reducing per-query large-model dependence beyond a measured reuse threshold.

Forbidden:

- `distilled intelligence into the small model` (weights were not changed);
- `general memory solution`;
- `all reasoning can be compiled`;
- any claim that ignores compiler cost.
