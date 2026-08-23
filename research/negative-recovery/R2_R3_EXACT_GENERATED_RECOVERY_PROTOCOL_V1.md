# R2/R3 Exact Generated Negative-Recovery Protocol V1

**Status:** `FROZEN_BEFORE_REPOSITORY_RESULT_BEARING_EXECUTION`  
**Parent:** #964  
**Branch:** `research/negative-recovery-atlas-v1`

## Purpose

Test a bounded version of the research goal before claiming real scientific recovery:

> Can a recovery policy learned only from **atomic negative episodes** recursively resolve **unseen composite failures** by selecting the right research action at each stage, while an independently coded native responsibility controller reaches the same functional terminal and both correctly refuse unnecessary escalation on exact-sufficiency controls?

This is a controlled causal research-world experiment. It is not yet evidence of autonomous real-world science.

## Failure causes

The exact generator uses eight responsibility classes:

1. `REPRESENTATION_LIMIT`
2. `MODEL_CAPACITY_LIMIT`
3. `DATA_SCARCITY`
4. `PARTIAL_INFORMATION`
5. `LEAKAGE_OR_SHORTCUT`
6. `MISSING_PARENT_METHOD`
7. `EXACT_MECHANIC_SUFFICIENT`
8. `BENCHMARK_NON_IDENTIFYING`

Each cause produces a noisy diagnostic signature over evaluator-defined probes such as same-information relation gain, interaction-order gain, sample gain, missing-information gain, invariance repair, donor gain, exact-ceiling evidence, collision/non-identifiability evidence, semantic-orbit instability, and train/test gap.

The signatures are not passed as labels. Candidate lanes see only the generated diagnostic vector and their own prior action history.

## Recovery actions

- `EXPOSE_RELATION_COORDINATE`
- `INCREASE_INTERACTION_ORDER`
- `ACQUIRE_MORE_DATA`
- `ACQUIRE_MISSING_OBSERVATION`
- `ENFORCE_INVARIANT_STATE`
- `ADOPT_DONOR_METHOD`
- `STOP_NEURAL_ESCALATION`
- `RUN_DISCRIMINATING_EXPERIMENT`

`BENCHMARK_NON_IDENTIFYING` is a two-stage case: the first action must be a discriminator; only then is the hidden representation-vs-capacity subtype revealed to the recovery state.

`EXACT_MECHANIC_SUFFICIENT` is a hard anti-escalation control. Correct behavior is to stop neural escalation.

## Lane A — learned recovery policy

Train only on atomic episodes.

The V1 model is deliberately simple: nearest-centroid classification over the diagnostic vector. The point is not model novelty; the point is whether a learned atomic failure-to-action map composes recursively on failure combinations never seen during training.

No composite episode is used for fitting.

## Lane B — native responsibility controller

A separately coded typed controller receives the same diagnostic vector but no learned centroids. It uses explicit responsibility thresholds:

- exact-ceiling evidence has first right of refusal;
- non-identifiability/collision evidence triggers a discriminator;
- otherwise the strongest registered responsibility probe selects the next action.

Lane B is an independent decision path, not a paraphrase of Lane A.

## Protected panels

### Atomic holdout

Fresh seeds, all eight causes.

### Composite holdout

All 2-cause and 3-cause combinations drawn from the seven non-exact classes. These combinations are absent from Lane-A training.

Recovery is recursive: after one valid repair, the repaired cause is removed and a new diagnostic vector is generated for the remaining failure state.

## Pilot-only metric correction before freeze

A non-result-bearing local design pilot found a methodological issue: on a composite failure with two simultaneously valid repairs, Lane A and Lane B can choose different first actions and still both be correct and converge to full recovery.

Therefore **strict first-action equality on composite cases is not a scientific gate**. Requiring it would make an arbitrary repair ordering authoritative.

The frozen comparison distinguishes:

- atomic first-action agreement — meaningful because one responsibility is active;
- composite first-action *validity* for each lane — each first action must address an actually active cause;
- final recovery success;
- strict composite first-action equality — reported descriptively only;
- terminal agreement — both lanes reach the same recovered/non-recovered state.

This correction is frozen before repository result-bearing execution.

## Baselines

1. same learned policy, **single shot only** — tests whether recursion itself matters;
2. random recursive action policy — tests trivial search;
3. exact-sufficiency anti-escalation control.

## Primary gates

All must pass:

- learned atomic recovery `>= 0.95`;
- native atomic recovery `>= 0.95`;
- atomic first-action agreement `>= 0.95`;
- learned unseen-composite recovery `>= 0.90`;
- native unseen-composite recovery `>= 0.95`;
- both lanes' first actions are valid on `>= 0.95` of composite episodes;
- dual terminal agreement `>= 0.95`;
- exact-sufficiency no-overescalation `= 1.00`;
- learned recursive composite recovery strictly exceeds the same learned policy in single-shot mode;
- learned recursive composite recovery strictly exceeds random recursive action.

No average may compensate a failed exact-sufficiency control.

## Leakage / construction controls

- candidate payload excludes hidden cause ids;
- candidate payload excludes gold action;
- candidate payload excludes the latent subtype behind a non-identifying collision;
- composite causes are not present in Lane-A training rows;
- evaluator may inspect hidden cause only after the candidate action is sealed for that step;
- exact-sufficiency is retained in denominator;
- wrong actions do not silently repair a cause;
- history records actions only, not evaluator gold.

## Allowed terminal

Positive bounded terminal:

`ORION_NEGATIVE_RECOVERY_EXACT_GENERATED_WORLDS_SUPPORTED`

Negative:

`ORION_NEGATIVE_RECOVERY_EXACT_GENERATED_WORLDS_NOT_SUPPORTED`

A positive terminal means only that atomic failure knowledge can be composed recursively in this frozen exact generated world. It does **not** establish historical blind recovery, real LLM research recovery, quantum method invention, or autonomous science.

## Next gate after a positive

The programme must still execute a prospective owner-domain negative whose recovery was unknown at freeze time. Historical cases remain calibration/evidence only unless a truly independent candidate lane is available.