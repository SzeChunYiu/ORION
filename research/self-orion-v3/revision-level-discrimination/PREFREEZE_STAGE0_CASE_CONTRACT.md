# Self-ORION V3 revision-level discrimination — pre-freeze Stage 0 case contract

Issue: #455  
Status: **pre-freeze design pressure only**. This document does not freeze H1, a final taxonomy, statistics, or any result-bearing campaign.

## Purpose

Before provider/LLM trials, define a white-box synthetic case format that can expose fake revision-level discrimination. The same visible residual must support multiple incompatible responsible layers, with the gold cause and licensing evidence kept outside candidate-visible state.

## Expert review lenses used for this contract

- **Causal diagnosis / Bayesian criticism:** asks whether the allowed diagnostic action actually separates competing responsibility hypotheses.
- **Safety / authority:** checks that a diagnosis does not itself grant mutation authority and that objective/evaluator changes remain protected.
- **Experimental design / leakage:** separates candidate-visible fields from protected gold and requires outcome-permutation controls.
- **Continual/self-revision systems:** checks that simple direct update, M-open expansion, world-model rewrite, representation change and no-change/containment remain genuine competing responses.

## Required case fields

Every Stage 0 case should carry the following fields before any result-bearing run:

```text
case_id
family_id
public_state
visible_residual
candidate_revision_options
admissible_diagnostics[]
  - diagnostic_id
  - cost
  - public_action
  - observation_by_responsibility_hypothesis
protected_gold
  - responsible_layer
  - minimal_licensed_response
  - sufficient_observation_ids
  - forbidden_revision_classes
  - unaffected_state_invariants
  - required_followups
  - harmful_broader_revisions
budget
scoring_contract
  - revision_class_correct
  - false_broad_revision
  - harmful_invalidation
  - preservation
  - unresolved_correct
  - diagnostic_cost
```

`protected_gold` must never be serialized into the candidate prompt/request. A diagnostic result updates evidence only; it does not directly authorize a change.

## Provisional response classes under test pressure

These are **case labels, not a frozen universal ontology**:

- `NO_SELF_REVISION / EXOGENOUS_STOCHASTICITY`
- `CONTAIN / RESTRICT_ACTION_SCOPE`
- `EVIDENCE_ACQUIRE_OR_RECHECK`
- `MEASUREMENT_OR_EXPERIMENT_REDESIGN`
- `PARAMETER_UPDATE`
- `MODEL_SELECTION_WITHIN_CLASS`
- `M_OPEN_MODEL_CLASS_EXPANSION`
- `REPRESENTATION_OR_REGIME_CHANGE`
- `OBJECTIVE_OR_QUESTION_REVISION` (protected under #288)
- `METHOD_BASIS_REVISION_OR_INVENTION`
- `EXECUTION_OR_ENVIRONMENT_REPAIR`
- `EVALUATOR_OR_AUTHORITY_REPAIR`
- `UNRESOLVED / ADDITIONAL_DISCRIMINATOR_REQUIRED`

If Stage 0 reveals that two classes cannot be distinguished under admissible observations, the correct response is to merge/narrow the benchmark, not to force a label.

## Minimum cause-confusable families

### 1. Evidence vs parameter vs model-class inadequacy

Same prediction failure; one case is missing an observation, one is resolvable by parameter update, one requires M-open expansion. At least one diagnostic must separate all three within budget.

### 2. Measurement vs mechanism

Same apparent mismatch; one sensor/operationalization is defective, one experiment is non-identifying, one mechanism is genuinely absent.

### 3. Alignment adapter vs representation regime change

Same downstream task failure; one nuisance transformation is repairable by an interface/alignment adapter, one requires state augmentation, one makes the current ontology/decomposition inadequate.

### 4. Objective vs optimizer/execution vs poor candidate

Same low score; one proxy is misspecified, one implementation is broken, one candidate is simply bad. Low reward alone must not license objective mutation.

### 5. Evaluator vs candidate vs insufficient evidence

Same `FAIL`; one evaluator is stale/defective, one artifact is defective, one has correct terminal `CANNOT_CHECK`.

### 6. Stochasticity vs self-defect

Same bad outcome; one is candidate/policy fault, one is exogenous stochasticity, one is epistemically unresolved. Measure false self-revision under noisy outcomes.

### 7. Contain vs investigate vs revise

Same model uncertainty; one case is safely useful under restricted action scope, one needs one data-acquisition step, one has systematic model-class failure, one has a defective uncertainty estimator.

### 8. Strategically linked revision bundle

Patch A is locally neutral/worse but is valid only when bound to required follow-up B; A alone is harmful, while tempting patch C is locally attractive but blocks the valid sequence. Score missing-required-followup separately from local improvement.

## Fake-adaptivity controls

Every result-bearing implementation derived from this contract must include:

1. permuted diagnostic outcomes with prompts otherwise held fixed;
2. no-feedback condition;
3. contradictory-feedback condition;
4. fixed proposal prior with changed quantitative evidence;
5. same proposal list with different intervention outcomes;
6. random discriminator under matched cost;
7. perfect diagnosis with wrong permission matrix;
8. correct permission matrix without diagnosis;
9. always-broad-revise policy;
10. always-UNRESOLVED policy.

A mechanism that does not change behavior when diagnostic outcomes are permuted has not demonstrated evidence-responsive revision discrimination.

## Preservation and history split

Stage 0 must score immutable audit/negative history separately from mutable working state:

- audit history may not be erased to launder a failure;
- obsolete working beliefs may be superseded when evidence warrants it;
- pathological refusal to forget stale working state is a failure distinct from history erasure.

## Baseline floor

At minimum compare against:

- fixed/no revision;
- simple direct/parameter-efficient update;
- current P5 V2 active-discriminator/repair path;
- M-open-only expansion;
- world-model/context revision;
- representation-regime comparator where faithfully runnable;
- generic multi-hypothesis causal diagnosis;
- modification-consequence/include-vs-exclude comparator;
- oracle responsibility ceiling for analysis only.

A donor implementation that cannot map faithfully must be labelled a mechanism comparator, not an official reproduction.

## Freeze blockers

Do **not** freeze the result-bearing V3 protocol until:

- #452 supplies a taxonomy or V3 records a justified narrower subset;
- #454/#318 structural receipts exist for load-bearing donor mechanisms;
- Stage 0 cases demonstrate at least one discriminating diagnostic for each retained class boundary;
- public/protected leakage checks are executable;
- compute/action budgets and primary statistics are written before final holdout outcomes.

## Reopen triggers

Reopen the design if any of the following occurs:

- two nominal revision classes are observationally indistinguishable;
- a simpler direct-update or M-open policy matches the full framework under matched budget;
- containment dominates self-revision on a material region of the benchmark;
- performance is invariant to feedback permutation;
- apparent V3 gain disappears under matched compute;
- protected gold leaks into candidate-visible state;
- revision correctness improves while useful fresh-transfer collapses.

This artifact is intentionally additive and non-authorizing. Green schema/instrumentation tests would not close #455.
