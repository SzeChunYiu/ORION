# P1-U GPT-R1 Active Responsibility Discrimination protocol V1

Issue: #696  
Parent: #649  
Frozen framework base: `83abfc5c3a98606d9339b88024f83d1d4ab313e7`  
Status: `PROTOCOL_FROZEN__NO_ARD_OUTCOMES_ACCESSED`

## Purpose

This is the first exact/public mechanism discriminator for the P1-U negative-to-positive programme.

It does **not** test general open-ended reformulation superiority. It tests whether a scientifically decision-focused, finite-horizon responsibility-acquisition policy has incremental value over strong static/myopic/label-focused donor controls when the responsibility coordinate is not supplied.

Generic active diagnosis, value of information, model discrimination, intervention-supported attribution, theory revision and reformulation are donor-owned. The experiment tests their composition with ORION's scientific responsibility hierarchy and non-compensatory revision consequences.

## Historical evidence remains immutable

- historical broad `failure => reformulate` remains failed;
- decision-complete objective-basis tie remains a real no-reformulation regime;
- P1-X V2 remains `400/400` versus `275/400` on exact revision responsibility;
- full-information ideal product remains an analysis ceiling that ties when supplied complete responsibility semantics.

No old outcome enters the new denominator.

## Exact episode model

Each episode is a finite decision problem:

- hidden causal hypothesis set `H`;
- mapping from each hypothesis to a scientific revision decision `D(h)`;
- candidate-visible prior over `H`;
- candidate-visible diagnostic actions `a in A`;
- deterministic observation partition for each action;
- action cost;
- optional action-enablement relation;
- total diagnostic budget of two cost units;
- protected correct scientific decision;
- protected harmful-high-level-revision flag.

Runnable systems receive the same prior, action set, observation model, costs and budget. They do **not** receive the hidden hypothesis or protected correct decision.

## Scientific decisions

`D(h)` is one of:

- `KEEP_SEARCH`
- `KEEP_COMPILE`
- `KEEP_REPAIR`
- `REVISE_MEASUREMENT`
- `REFORMULATE_OBJECTIVE`
- `REFORMULATE_BOUNDARY`
- `UNRESOLVED`

## Action vocabulary

- `SEARCH_MORE`
- `COMPILE_OR_REPRESENT`
- `REPAIR_ENV_OR_HARNESS`
- `REMEASURE`
- `TEST_OBJECTIVE_BASIS`
- `TEST_PROBLEM_BOUNDARY`
- `ABSTAIN`

An episode may mark a diagnostic action as enabled only after another observation. Enablement is candidate-visible in the action model but the future observation is not.

## Distinct causal template families

The public exact arena contains eight template families in each of five domains:

1. **DIRECT_LOWER_LEVEL** — one low-cost test separates two lower-level causes.
2. **DIRECT_HIGH_LEVEL** — one test separates objective from boundary revision.
3. **REPRESENTATION_MASQUERADE** — surface failure suggests objective change but a representation probe can establish `KEEP_COMPILE`.
4. **HARNESS_MASQUERADE** — surface failure suggests scientific change but an environment/harness probe can establish `KEEP_REPAIR`.
5. **OBJECTIVE_BASIS_SUFFICIENT** — attractive reformulation exists but decision-complete basis requires no high-level revision.
6. **SEQUENTIAL_COMPLEMENT** — a first probe has little/no immediate terminal value but enables a second probe that disambiguates the scientifically important revision class.
7. **DECISION_VS_LABEL_INFORMATION** — one action maximizes hidden-cause label discrimination while another better separates the scientific decisions that matter under the budget.
8. **NON_IDENTIFIABLE** — no admissible two-cost sequence can resolve the responsibility; correct output is `UNRESOLVED`.

Domains:

- software/debugging;
- scientific retrieval/discovery;
- semantic integration;
- evidence/verification;
- model/experiment design.

Thus there are 40 distinct causal templates. Each template has deterministic remints/permutations used only as metamorphic robustness checks.

## Remint policy and independent unit

For each distinct template, 12 surface/id/order remints are generated, yielding 480 concrete episode records.

**The remints are not treated as 480 independent scientific samples.** They are metamorphic checks of identity/order/surface invariance. Mechanistic inference is at the 40-template level and, where appropriate, summarized by domain and family.

## Frozen systems

### B0 — STATIC_NO_PROBE

Chooses the Bayes-optimal scientific decision from the initial prior and takes no diagnostic action.

### B1 — GREEDY_RESTORATION

Chooses the lowest-cost action with the highest probability of immediately identifying a single restoring action/decision. No lookahead.

### B2 — ONE_STEP_LABEL_VOI

Chooses the action maximizing one-step expected hidden-hypothesis classification accuracy improvement minus `0.05 * action_cost`; then makes the Bayes-optimal scientific decision from the posterior.

### B3 — ONE_STEP_DECISION_VOI

Chooses the action maximizing one-step expected scientific-decision accuracy improvement minus `0.05 * action_cost`; then makes the Bayes-optimal scientific decision from the posterior.

This is the primary runnable donor baseline for the exact pilot.

### B4 — TWO_STEP_LABEL_PLANNER

Uses exact two-cost lookahead but optimizes hidden-cause label accuracy rather than scientific-decision utility. This tests whether generic diagnosis can spend budget on distinctions that do not change the warranted scientific action.

### P1-ARD — HORIZON2_SCIENTIFIC_RESPONSIBILITY

Uses exact two-cost lookahead over the declared action/observation model. Utility is decision-focused and non-compensatory:

- `+1.0` correct scientific decision;
- `0.0` incorrect decision;
- `-1.0` additional penalty for an incorrect high-level reformulation on a protected no-high-level-revision case;
- `-0.05 * diagnostic_cost` action cost.

When expected utility is tied within exact rational arithmetic, choose the lexicographically stable action id. After observations, select the decision with maximal posterior expected protected utility. `UNRESOLVED` is correct only on templates whose admissible observation graph cannot distinguish decision classes within budget.

This planning algorithm is not claimed as novel. The scientific object is the responsibility-state/action/utility composition.

### CEILING — HORIZON2_FULL_SCIENTIFIC_ORACLE

Receives the same finite model and uses the optimal two-cost scientific-decision policy. For this exact pilot it should match P1-ARD if the implementation is correct. It is an analysis ceiling, not a realistic baseline.

## Primary mechanistic endpoints

1. **Template GRS**: Generalized Reformulation Success on each of the 40 distinct causal templates.
2. **False high-level reformulation** on templates where high-level revision is not warranted.
3. **Missed necessary high-level reformulation**.
4. **Correct unresolved** on NON_IDENTIFIABLE templates.
5. **Mean diagnostic cost conditional on correct GRS**.
6. **Metamorphic invariance** across all 12 remints of each template.

`GRS=1` iff the final scientific decision is correct and no protected high-level harm rule is violated.

## Prospective decision rules

The exact pilot reaches `ARD_EXACT_MECHANISM_POSITIVE` only if all are true:

1. P1-ARD template GRS exceeds B3 by at least `+0.10` absolute across the 40 distinct templates;
2. P1-ARD has no more false high-level reformulations than B3 and has zero protected high-level harm on the exact registered templates;
3. P1-ARD is correct on every NON_IDENTIFIABLE template;
4. P1-ARD matches CEILING on every distinct template;
5. all remints preserve each system's template-level decision and metric result;
6. effect direction P1-ARD minus B3 is non-negative in every domain and strictly positive in at least three of five domains;
7. no RED-first hostile integrity check fails.

No confidence interval is used to pretend the authored finite templates are a random population. Report exact template counts and paired differences. A later prospectively sampled naturalistic study will carry inferential uncertainty.

## Secondary comparisons

B0/B1/B2/B4 are diagnostic ablations. No multiplicity-adjusted confirmatory superiority claim is based on them. Their purpose is mechanism localization.

## RED-first integrity tests

Implementation tests must establish before interpreting outcomes:

- no hidden cause/decision in candidate-visible ids or action names;
- every runnable system receives byte-equivalent action/observation/cost model;
- reminting/permutation does not change semantics;
- action costs are charged identically;
- disabled actions cannot be queried;
- observations cannot be accessed before taking the action;
- protected harm flags are evaluator-only;
- B3 and P1-ARD differ only in finite-horizon policy/utility semantics, not information;
- CEILING receives no extra hidden cause;
- all 480 episode records are retained;
- failed/UNRESOLVED records remain in reports.

## Claim authority

A positive pilot supports only:

> explicit finite-horizon scientific-responsibility acquisition has non-vacuous mechanistic value on the registered exact cause-confusable worlds relative to the frozen myopic donor control.

It does **not** establish general reformulation superiority, naturalistic science performance, novelty of active diagnosis, or canonical runtime adoption.

The next step after a positive exact pilot is a separately frozen protected/naturalistic transfer study under #696. A negative pilot remains immutable and reopens the causal mechanism.
