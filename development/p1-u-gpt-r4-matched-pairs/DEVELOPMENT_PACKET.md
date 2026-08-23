# P1-U GPT-R4 — matched within-source adverse/control campaign

Parent: #649  
Campaign: #719  
Base: `main@2d6065755084588737274102aa7c140f2f1d8b7c`

## Why R4 exists

R2 and R3 both stopped before policy scoring because acquisition could not produce a valid independent control set. R4 makes the control a property of every admitted adverse source rather than a separate search target.

## Primary scientific question

Under matched information and a two-probe budget, can ORION's responsibility-ordered ARD distinguish **when a scientific problem/objective/boundary really needs reformulation** from a matched same-source condition where it does not, better than a donor-complete horizon-2 Bayesian/VoI controller?

## Freshness

Primary sources: calendar year 2020 only. Replication if primary passes: 2019 only. All R1–R3 sources are excluded.

## Matched source unit

A substantive source is admissible only if the same primary study/artifact family supplies both:

- `adverse`: a pre-resolution condition in which one registered substantive responsibility is load-bearing;
- `control`: a scientifically matched condition in which high-level reformulation is unnecessary and the current objective/problem boundary remains adequate.

The pair must match as closely as the source permits on scientific objective/task, domain, measurement system, implementation family, population/material/system, and study method. It may differ only on a source-grounded factor that activates the adverse responsibility.

A source that provides only an adverse case is rejected. A control may still require a lower-level action; what it must not require is objective/model-class or problem-boundary reformulation.

## Frozen source targets

Acquire exactly four pair sources for each substantive adverse class:

- SEARCH_OR_EVIDENCE;
- REPRESENTATION_OR_INTERFACE;
- IMPLEMENTATION_OR_ENVIRONMENT;
- MEASUREMENT_OR_EVALUATOR;
- OBJECTIVE_OR_MODEL_CLASS;
- PROBLEM_BOUNDARY.

That yields 24 pair sources / 48 episodes, of which exactly 24 are matched `NO_HIGH_LEVEL_REFORMULATION` controls.

Acquire four additional source-disjoint `UNRESOLVED` episodes with genuine non-identifiability. Total primary evaluation episodes: 52.

At least five actual scientific/workflow domains must be represented across the 28 primary sources.

## Candidate/comparator freeze

Reuse merged R2 policy/protocol bytes unchanged:
- primary comparator `B3_HORIZON2_DONOR_COMPLETE`;
- candidate `ORION_R2`;
- same six generic probes;
- same likelihood model;
- same two-probe budget;
- same candidate-visible dossier boundary;
- full-information ideal product is analysis ceiling only.

No source-specific policy tuning is permitted.

## Primary endpoints

### Episode-level GRS
Existing R2 exact correctness endpoint, preserving all non-compensatory harm guards.

### Pair-selective success
For each of the 24 matched sources:

`pair_selective_success = 1` iff the policy is correct on both adverse and control members.

This directly tests whether the system escalates only in the responsibility-changing member while preserving the matched no-high-level control.

## Promotion rule

All R2 primary gates remain mandatory:
- episode-level ORION-B3 GRS >= +0.10;
- paired bootstrap 95% stability lower bound > 0;
- domain non-inferiority >= -0.10;
- ORION unnecessary high-level rate <= B3 and <= 0.05;
- zero harmful lower-level skips;
- zero false resolution of gold UNRESOLVED;
- zero leakage.

Additional R4 gates:
- pair-selective-success ORION-B3 >= +0.10;
- pair-level bootstrap 95% stability lower bound > 0;
- zero ORION harmful high-level escalation on any control member;
- at least three substantive classes have non-negative pair-selective ORION-B3 difference;
- no substantive class pair-selective difference < -0.10.

Primary passing only opens the 2019 replication. #649 closes only after the disjoint-source independent replication passes and the parent Done-when conditions are satisfied.

## Acquisition integrity

Before any 2020 search, freeze 28 exact queries and the pair evaluator. Then:
- execute queries individually and verbatim;
- inspect at most 50 returned results;
- admit first qualifying nonexcluded source in returned order;
- log every skipped source and objective reason;
- if any of the 28 required queries has no qualifying source, terminate `CANNOT_CHECK_MATCHED_SOURCE_UNIVERSE` before policy scoring;
- do not add replacement queries after acquisition begins;
- do not score policies until all source/pair/unresolved records are sealed.

## Stop / recurse

A negative result is retained. If acquisition fails, diagnose the source-object problem rather than relaxing it. If B3 ties/wins, diagnose the policy residual and open a materially different successor. No post-outcome margin, label, pair, probe, query or baseline changes.
