# P9/P10 Structural Scaling Research Program V1

Status: **RESEARCH AGENDA — NO NEW OUTCOME CLAIMS**

Frozen: 2026-08-20

## 1. Program thesis

P9 and P10 jointly motivate a stronger hypothesis than either paper currently claims:

> For bounded reasoning systems, representation quality can substitute for model capacity and inference compute because some semantically equivalent encodings make the task computationally easier to access. In formal mathematics, verifier-native state may expose transferable action-relevant structure beyond proof-history recurrence.

This document freezes a novelty-expansion program. It does **not** promote any unrun experiment, null result, exploratory endpoint, or historical P9/P10 evidence into a stronger claim.

## 2. Existing evidence that remains locked

### P9

The existing P9 bounded result supports a representation/identifiability interpretation: typed relation/history/method coordinates can make signal accessible to simple learners, exact deterministic inference can close some residual computation, and the held-out-domain comparison favors typed relational structure over transcript, untyped, and same-information serialization controls. These results do not by themselves establish an LLM scaling law.

### P10

The existing P10 V2.1 result establishes coarse cross-module tactic-history transfer on the frozen Mathlib corpus. Under leave-top-module-out evaluation, Markov accuracy is 0.3842 versus 0.2796 for the pooled unigram baseline, delta 0.1046, with positive top-module bootstrap interval approximately [0.0863, 0.1223]. The separate native-state protocol asks whether proof-state/dependency structure adds incremental held-out-module information beyond this locked baseline.

## 3. Mathematical core: four quantities to distinguish

Let latent task state be `X`, target decision/action be `Y`, domain be `D`, representation be `R=r(X)`, model family be `F`, training sample size be `n`, and inference budget be `C`.

### 3.1 Information sufficiency

A representation is statistically sufficient for `Y` when

`P(Y | X) = P(Y | R)`

or equivalently `I(Y; X | R)=0` under the relevant distribution.

This asks whether information was discarded.

### 3.2 Computational accessibility

For loss `L`, define restricted-family risk

`Risk_F(R) = inf_{f in F} E[L(f(R),Y)]`.

For two semantically equivalent or bijectively related representations `R1,R2`, define the **Computational Accessibility Gap**

`CAG_F(R1,R2) = Risk_F(R2) - Risk_F(R1)`.

If `R1` and `R2` preserve the same task information but `CAG_F > 0`, the performance difference is not explained by Shannon information loss alone. It measures accessibility relative to `F`.

This is the natural mathematical extension of P9 same-information controls.

### 3.3 Representation-induced reasoning tax

Let `C*(R,q)` be the minimum declared inference budget required by a fixed model family to reach target quality `q`. Define

`RT_q(R1,R2) = log C*(R2,q) - log C*(R1,q)`.

A positive value means `R2` requires multiplicatively more inference compute than `R1` to reach the same quality. This is a prospective empirical quantity; it must be estimated under fixed model weights and protocol-matched inference regimes.

### 3.4 Structural scaling substitution

Let model scale be `S` (for example parameter count or a compute-normalized capacity coordinate). For a fixed target quality `q`, define the **Structural Scaling Substitution Ratio** between a flat representation `Rf` and structured representation `Rs` as

`SSR_q = log(S*_flat(q) / S*_structured(q))`,

where `S*_r(q)` is the smallest preregistered model scale that reaches `q` under representation `r` at matched inference budget.

A positive `SSR_q` is the direct test of whether structure shifts the model-scaling frontier. It is not established by current P9/P10 evidence.

## 4. Strongest experiment: structure x scale x inference

### Factors

1. Model scale: at least 3 preregistered sizes from one architecture family.
2. Representation:
   - FLAT: ordinary task serialization.
   - SAME-INFO-SERIALIZED: contains the same facts as structured state but in a deliberately flattened canonical serialization.
   - STRUCTURED: typed entities, relations, scoped history, constraints, provenance, and state coordinates.
3. Inference regime:
   - fixed single trajectory;
   - matched token budget;
   - optional verifier/search regime with separately accounted compute.
4. Exact-computation assistance:
   - none;
   - deterministic tool for preregistered closed-form/subsymbolic-free operations only.

### Primary endpoint

Held-out-domain exact success under a fixed compute budget.

### Primary novelty test

Estimate the interaction:

`Delta_structure(size) = Perf(STRUCTURED,size) - Perf(SAME-INFO-SERIALIZED,size)`.

Then test whether a smaller structured model non-inferiorly matches or exceeds a larger flat/same-info model under matched inference compute.

### Required controls

- randomize representation assignment per item where possible;
- preserve semantic information exactly between structured and same-info controls;
- token-count and context-length accounting;
- order/permutation controls;
- symbol-renaming controls;
- module/domain identity attacker;
- verifier-blinded scoring;
- frozen seeds and model versions;
- no prompt retuning after outcome inspection.

## 5. P9 novelty ladder

### P9-R0 — existing bounded representation result

Already supported by current P9 evidence.

### P9-R1 — same-information computational accessibility

Earned only if structured state beats a semantically equivalent canonical serialization across held-out domains for a frozen restricted learner/model family.

Claim form:

> Equivalent task information can have materially different computational accessibility under a bounded learner.

### P9-R2 — representation changes LLM scaling frontier

Earned only if `SSR_q > 0` with uncertainty excluding zero for preregistered target qualities and the result survives matched token/inference controls.

Claim form:

> Structured state reduces the model scale required to attain a fixed held-out-domain reasoning quality.

### P9-R3 — representation reduces test-time reasoning tax

Earned only if structured state reaches matched quality using materially less protocol-matched inference compute.

Claim form:

> Some test-time reasoning compute compensates for representational inaccessibility rather than missing task information.

### P9-R4 — exact-computation decomposition

Partition tasks into information-limited, representation-limited, and computation-limited strata using prospective interventions:

- add missing information without changing representation;
- preserve information while changing representation;
- preserve representation while adding an exact deterministic subroutine.

This is the strongest mechanistic P9 extension because the interventions distinguish three failure modes experimentally.

## 6. P10 novelty ladder

### P10-R0 — existing coarse tactic-history transfer

Already supported by V2.1.

### P10-R1 — native proof-state incremental signal

Use the already frozen native-state protocol. Primary statistic remains B4-B1 on identical receipt-eligible transitions.

### P10-R2 — conditional information decomposition

Estimate leakage-safe predictive lower bounds corresponding to:

- `I(Y;H)` tactic history;
- `I(Y;S | H)` native proof state beyond history;
- `I(Y;G | H,S)` dependency graph beyond history+state.

Do not report plug-in mutual information as exact truth in high dimension. Use preregistered predictive log-loss reductions as variational lower-bound style evidence and report estimator sensitivity.

### P10-R3 — module-invariant proof coordinates

Test whether a representation `Z=g(S,G)` admits approximately invariant action conditionals across held-out top-level modules:

`P(Y | Z, D=d) approximately P(Y | Z)`.

Operationalize with per-module calibration, held-out log loss, domain-adversary accuracy, and worst-module risk. Direct module identity must be excluded from `Z`.

### P10-R4 — proof-search consequence

A predictor result alone is not a prover result. Embed the frozen state/dependency scorer into a verifier-backed search procedure with strictly matched node/Lean-call budgets. Primary endpoint: theorem solve rate; secondary: nodes expanded, Lean calls, wall time, proof length, failure mode.

### P10-R5 — tactic-library structure novelty

Requires a faithful TacMiner-class comparator on the identical corpus/split. Measure whether P10's state/dependency coordinates provide incremental held-out-module predictive or search utility beyond tactic-dependence-graph structure.

## 7. Cross-paper novelty: the potentially field-level result

The highest-value claim is not that structured prompts are better. It is a cross-domain law-like statement:

> Under matched information and compute, the accessibility of task-relevant structure changes the capacity and inference budget required for successful reasoning.

To earn this, replicate the same mathematical quantities in at least two qualitatively different domains:

1. P9 procedural/epistemic transfer tasks.
2. P10 formal Lean proof states.
3. Optional third domain chosen prospectively, not because it is favorable.

The key cross-domain quantity is a normalized structural advantage curve:

`A_r(S,C,D) = Perf(structured;S,C,D) - Perf(same-info;S,C,D)`.

A program-level result requires consistent sign and nontrivial magnitude on preregistered held-out domains, with transparent heterogeneity rather than pooled-only success.

## 8. New mathematical directions worth deepening

### 8.1 Blackwell/order-of-experiments view

When one representation is a stochastic garbling of another, Blackwell informativeness distinguishes genuine information loss from pure re-encoding. P9 should explicitly separate:

- strict refinements (more information),
- garblings (less information),
- bijective/equivalent encodings (same information, different accessibility).

The revolutionary case is the third: performance differences between equivalent encodings expose computational rather than informational limitations.

### 8.2 Restricted sufficient statistics

Define `R` as epsilon-sufficient for model family `F` when

`Risk_F(R) - Risk*(X) <= epsilon`,

where `Risk*` is unrestricted Bayes risk. Compare epsilon across model scales. This yields a representation-capacity phase diagram instead of a single benchmark score.

### 8.3 Minimum description/access complexity

For frozen task families, estimate whether structured representations reduce:

- description length of the decision rule;
- effective feature interaction order;
- depth needed by restricted circuits/trees;
- sample complexity needed for target risk.

These should be empirical complexity surrogates unless a theorem can be proved for a controlled synthetic subclass.

### 8.4 Compositional depth theorem on controlled generators

Construct an exact synthetic family where flat serialization forces a bounded architecture to recover a permutation/binding/composition map, while typed coordinates expose that map directly. Prove a separation for a restricted hypothesis class (for example bounded-depth decision trees, linear models, finite-state predictors, or another tractable class), then test whether LLM behavior tracks the theoretical separation.

A theorem on a controlled class plus corresponding LLM scaling evidence would be substantially stronger than benchmark-only novelty.

### 8.5 Error decomposition

Prospectively classify errors into:

`total error = information deficit + representation accessibility deficit + computation deficit + search/verification deficit`

not as an algebraic identity unless assumptions justify it, but as an intervention-defined taxonomy. Each component needs a paired intervention that changes only the corresponding factor as closely as experimentally possible.

### 8.6 State as an approximate Markov blanket

For sequential reasoning, test whether structured state makes distant transcript history conditionally irrelevant:

`I(Y_t ; H_{<t-k} | R_t) approximately 0`.

If true, structured state is functioning as an approximate predictive state / Markov blanket. This would connect P9 history compression and P10 proof state to a common mathematical object.

### 8.7 Representation robustness geometry

Define transformations that preserve semantics but alter surface form. Measure the local robustness set

`G(x) = {g : semantics(g(x)) = semantics(x)}`

and performance variance across `g in G`. A structurally grounded model should have lower semantic-orbit variance than a surface-sensitive model.

## 9. Surprise-generating falsifiers

The program should actively seek outcomes that would surprise us and reviewers:

1. **Inverse scaling under flat state:** larger models become more surface-sensitive while structured state removes the regression.
2. **Compute substitution:** structured small model at low inference budget matches a much larger flat model with long reasoning.
3. **State compression:** a compact typed state outperforms a much longer transcript despite containing no additional task facts.
4. **Verifier feedback phase transition:** native state is weak for one-step prediction but strongly improves bounded proof search.
5. **Structure ceiling:** after native state is exposed, extra model scale yields sharply diminishing returns on selected controlled tasks.
6. **Domain invariance:** a common structural representation reduces between-domain variance more than it improves pooled mean.

None may be promoted without the corresponding preregistered test.

## 10. Nearest-work and novelty boundary

A literature refresh is required before manuscript freeze. Current anchors include:

- LeanDojo / ReProver for proof-state/premise-aware Lean theorem proving and challenging splits.
- TacMiner for tactic-dependence graphs and reusable tactic-library discovery.
- recent work on state representation in dynamic LLM reasoning showing that state design itself can materially affect reasoning outcomes.
- recent test-time scaling work emphasizing that inference regimes and compute accounting must be separated rather than collapsed into a single vague budget.
- modern agentic Lean systems showing substantial gains from iterative verifier interaction, which raises the bar for any P10 prover-utility claim.

Novelty must therefore come from controlled **information-equivalent representation interventions**, scaling-frontier measurement, cross-domain mathematical unification, and verifier-backed formal evidence—not merely from using structure or Lean feedback.

## 11. Execution order

1. Finish P9 and existing P10 bounded peer-review packages without contaminating their frozen claims.
2. Execute the already-frozen P10 native-state incremental-value protocol.
3. Freeze a P9 LLM structure-vs-same-information scaling protocol before running any LLM outcomes.
4. Add exact compute-accounting and representation-equivalence validators.
5. Run the smallest preregistered matrix sufficient to estimate `CAG`, `SSR`, and `RT`.
6. Only after the primary analysis is frozen, expand to additional models/domains as replication.
7. Build a controlled mathematical generator and prove at least one restricted-class representation separation theorem.
8. Attempt verifier-backed P10 search utility under matched budgets.
9. Refresh nearest work and run strongest faithful comparators.
10. Select the highest claim rung that survives all hostile controls; retain every null and regression.

## 12. Publication strategy

P9 and P10 should remain independently reviewable bounded papers. The structural-scaling program should be a separate cross-paper research line unless its new experiments are completed before either manuscript freeze without jeopardizing current reproducibility.

Potential eventual paper thesis, if earned:

> **Representation Is a Scaling Variable: Structured State Reduces the Capacity and Inference Cost of Reasoning Across Procedural Tasks and Formal Mathematics.**

This title/thesis is prospective and must not appear as an achieved result until the scaling and cross-domain gates pass.
