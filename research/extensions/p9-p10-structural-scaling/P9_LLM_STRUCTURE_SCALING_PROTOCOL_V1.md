# P9 LLM Structure × Scale × Compute Protocol V1

Status: **FROZEN BEFORE LLM OUTCOMES**
Frozen: 2026-08-20

## Question

Does an information-equivalent structured task state reduce the model scale or inference compute required for held-out-domain reasoning?

## Subject

Use the frozen P9 procedural/epistemic task generators and held-out-domain boundaries. Historical P9 results are prior evidence only and may not tune this protocol.

## Representation arms

- `R0_FLAT_ORIGINAL`: canonical original task transcript.
- `R1_SAME_INFO`: canonical deterministic serialization containing exactly the facts exposed in structured state, but without typed slots/edges or privileged grouping.
- `R2_TYPED_STATE`: typed entities, relations, scoped history, constraints, provenance and method coordinates.
- `R3_TYPED_STATE_EXACT_TOOL`: R2 plus only preregistered deterministic exact subroutines.

The primary causal contrast is R2-R1, not R2-R0. R0 may contain a different effective information set.

## Model scale

Use at least three frozen checkpoints from one open-weight architecture family, chosen before outcomes. Preferred design: approximately log-spaced parameter counts. If a family cannot supply three compatible sizes under one tokenizer/interface, report `CANNOT_CHECK` rather than mix unrelated families for the primary scaling claim.

A second architecture family is replication only and cannot rescue a failed primary family.

## Inference regimes

For every model/representation pair:

1. deterministic or minimally stochastic single-pass budget;
2. matched generated-token budget grid;
3. optional multi-sample/verifier search, accounted separately.

Do not collapse token budget, candidate count, verifier calls and wall-clock into one unnamed `compute` variable.

## Primary endpoints

For held-out domains:

1. exact task success at each frozen budget;
2. paired `R2-R1` success difference;
3. smallest preregistered model size reaching each target quality `q`;
4. smallest inference budget reaching each target quality `q`.

Target qualities `q` must be frozen from pilot-independent considerations. If absolute thresholds are infeasible before execution, freeze quantile-free targets such as `{0.50,0.70,0.85}` provided task ceilings make them meaningful.

## Derived quantities

### Computational Accessibility Gap

`CAG_F(R2,R1) = Risk_F(R1)-Risk_F(R2)`.

### Structural Scaling Substitution

`SSR_q = log(S*_R1(q)/S*_R2(q))`.

### Representation-induced reasoning tax

`RT_q = log(C*_R1(q)/C*_R2(q))` for identical model weights.

Interpolation between tested scales/budgets may be descriptive; primary pass/fail uses observed grid points unless interpolation method is frozen independently.

## Strong success gate

The structure-shifts-scaling claim requires all of:

1. positive pooled R2-R1 effect on held-out domains;
2. block-bootstrap 95% lower bound above zero using held-out domain as block;
3. non-negative R2-R1 effect on at least 60% of evaluable domains;
4. at least one preregistered target quality where a strictly smaller structured model meets or exceeds the larger same-information model at matched inference regime;
5. no token/context-length explanation sufficient to account for the result;
6. semantic-equivalence validator passes;
7. symbol/order hostile controls pass;
8. no model/version/prompt selection after outcome inspection.

The test-time-compute substitution claim additionally requires positive `RT_q` on at least one preregistered target with uncertainty and protocol-matched compute reporting.

## Exact tool arm

R3 tools may compute only deterministic operations declared before execution. They may not call another LLM, retrieve hidden labels, or inspect held-out answer keys. Every tool call is logged with input/output digest and cost.

Use R3 to distinguish representation accessibility from exact-computation deficits, not to inflate R2.

## Semantic equivalence validator

For each R1/R2 item pair, construct a canonical fact multiset `F(x)` from the generator before surface realization. Both renderers must round-trip to identical `F(x)` under an independent parser. Failure on any item excludes the pair by a pre-outcome deterministic rule and is reported.

The validator additionally checks:

- no answer label encoded in field names/order;
- no domain identity field available only to R2;
- equal numerical precision;
- same historical events/failures;
- same constraints/provenance facts;
- no renderer-specific extra hints.

## Hostile controls

1. random symbol renaming;
2. stable random permutation of fields/facts where semantics allow;
3. distractor-preserving serialization changes;
4. explicit domain-identity attacker;
5. answer-token leakage scanner;
6. renderer round-trip mutation;
7. representation-label blinding in scorer;
8. prompt hash and model response receipt.

## Statistical analysis

Report paired item effects, domain-block uncertainty, worst-domain risk, and model-scale curves. Do not rely only on pooled significance. Apply multiplicity correction to secondary target-quality comparisons or label them exploratory.

## Claim ladder

- `L0`: current P9 bounded structural evidence only.
- `L1`: same-information structured accessibility supported.
- `L2`: model-scale substitution supported.
- `L3`: test-time-compute substitution supported.
- `L4`: exact-tool decomposition supported.
- `L5`: replicated across a second model family without changing protocol logic.

No rung may be claimed unless all lower load-bearing gates pass.

## Required artifacts

- frozen model identifiers and tokenizer revisions;
- prompts/system-message digests;
- exact task manifest;
- R1/R2 canonical-fact equivalence receipts;
- generation configuration and raw responses;
- token/candidate/verifier/wall-time accounting;
- item-level scores;
- domain-block bootstrap samples/digest;
- hostile-control results;
- deterministic regeneration code;
- final claim-disposition receipt.
