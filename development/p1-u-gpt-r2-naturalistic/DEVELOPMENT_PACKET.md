# P1-U GPT-R2 — protected naturalistic reformulation-superiority campaign

Parent: #649  
Campaign issue: #711  
Predecessor mechanism tranche: #696 / merged #709  
Frozen policy base: `main@ea7543fc5b6ad14f151215d87dc7ed81253a8269`

## Objective

Earn `P1_U_GENERALIZED_REFORMULATION_SUPERIORITY_SUPPORTED` on fresh, source-grounded heterogeneous scientific decision episodes rather than extending the authored exact ARD panel.

The exact R1 result remains bounded mechanism evidence. It is not counted as an R2 outcome.

## Pre-outcome separation

This packet and the candidate/baseline policy code are frozen **before** the held-out source dossiers and evaluator labels are collected.

Sources already inspected before this freeze are development/donor-only and excluded from held-out evaluation: Model Discovery Agent / NeuronBench, Self-Revising Discovery Systems for Science, SCION, Robin, RootCauseBench, and the 2026 ML-pipeline RCA paper.

Held-out cases are acquired only after the policy freeze from predeclared public-primary-source search routes. Candidate policies receive only case-visible dossier fields; gold responsibility labels, source resolution, and evaluator-only probe outcomes are evaluator-side data.

## Independent unit

One distinct source-grounded scientific/workflow episode. Rephrasings, repeated model samples, policy reruns, or metamorphic remints never increase `n`.

## Responsibility classes

- `SEARCH_OR_EVIDENCE` — objective/model may be adequate; missing evidence/search is the current responsibility.
- `REPRESENTATION_OR_INTERFACE` — scientific target is adequate but representation/access/interface blocks progress.
- `IMPLEMENTATION_OR_ENVIRONMENT` — code, harness, dependency, tool, or environment defect.
- `MEASUREMENT_OR_EVALUATOR` — measurement, scoring, calibration, benchmark, or evaluator defect.
- `OBJECTIVE_OR_MODEL_CLASS` — objective/hypothesis class is materially wrong/incomplete after lower-level causes are excluded.
- `PROBLEM_BOUNDARY` — registered problem boundary is materially wrong and must be widened/reframed.
- `NO_HIGH_LEVEL_REFORMULATION` — control: current objective/boundary is decision-complete; high-level reformulation is unnecessary/harmful.
- `UNRESOLVED` — available evidence does not identify a safe responsibility under the frozen budget.

## Generic probe menu

Every episode exposes the same probe names; availability cannot reveal the gold label.

1. `P_SEARCH_COVERAGE`
2. `P_REPRESENTATION_ROUNDTRIP`
3. `P_ENVIRONMENT_REPLAY`
4. `P_MEASUREMENT_CROSSCHECK`
5. `P_OBJECTIVE_PREDICTIVE_CHECK`
6. `P_BOUNDARY_COUNTERFACTUAL`
7. `P_ABSTAIN`

Each non-abstention probe has cost 1. Probe observations are evaluator-owned facts extracted from the source record and encoded without the gold class name.

## Candidate arms frozen before holdout acquisition

### B0 — no reformulation
Never chooses objective/model-class or problem-boundary reformulation.

### B1 — always escalate on unresolved failure
Hostile control matching the historical false-escalation failure mode.

### B2 — donor-complete immediate VoI
Flat cause-state controller. At each step, choose the probe with greatest expected immediate entropy reduction per cost under the development prior, then choose the intervention with greatest posterior expected utility. This arm owns generic active diagnosis, VoI, M-open expansion, representation revision, failure localization, and objective evolution; those are not ORION novelty.

### B3 — donor-complete horizon-2 Bayes planner
Same flat cause state and complete donor action set as B2, but optimizes expected two-probe terminal utility under the frozen development transition table. This is the primary runnable comparator.

### ORION-R2 — responsibility-ordered ARD
Uses the same visible dossier and probe observations, but maintains typed responsibility obligations. High-level objective/model or boundary reformulation is inadmissible until lower-level `SEARCH/REPRESENTATION/IMPLEMENTATION/MEASUREMENT` explanations that remain plausible are either falsified by acquired evidence or become explicitly non-identifiable under budget. Among admissible probes, choose expected reduction in unresolved responsibility mass per cost. If evidence remains non-identifying, return `UNRESOLVED` rather than escalate.

### Ceiling
Full-information ideal product is analysis-only and receives the evaluator responsibility label. It is not a realistic baseline and cannot be counted as a comparator win/loss.

## Search-route freeze for held-out cases

Acquire cases only after this policy freeze. For each route, take the first qualifying primary/official source result in the frozen search snapshot that has enough public evidence to establish both the failure responsibility and a corrective/diagnostic outcome. No case may be selected or dropped based on policy performance.

Publication window: 2024-01-01 through 2026-08-20.

Predeclared domains / source routes:

1. computational biology / mechanistic-model or experimental-design failure;
2. physics or chemistry / model, representation, measurement, or access-model revision;
3. ML/data-analysis pipeline / data, metric, configuration, or evaluation failure;
4. scientific software / implementation, dependency, numerical, or harness failure;
5. experimental/observational measurement / calibration, proxy, instrumentation, or measurement-construct defect;
6. cross-domain scientific workflow / objective, representation, workflow, or problem-boundary revision.

For each domain, acquire at least four qualifying episodes and retain all qualifying first-hit episodes until the route quota is filled. At least two episodes overall must be `NO_HIGH_LEVEL_REFORMULATION`, and at least two must be non-identifiable under the frozen two-probe budget and therefore gold `UNRESOLVED`.

## Primary endpoint

`GeneralizedReformulationSuccess = 1` iff:
- final responsibility decision is evaluator-correct;
- selected intervention is compatible with the source-grounded successful/appropriate next action;
- no high-level reformulation occurs on a no-reformulation control;
- no lower-level repair is skipped when source evidence establishes it as load-bearing;
- `UNRESOLVED` is returned when the frozen evidence is non-identifying;
- probe cost is charged and total budget <= 2.

Primary contrast: paired case-level `ORION-R2 - B3` GRS.

## Frozen decision rule

- superiority margin: +0.10 absolute paired GRS;
- ORION must exceed B3 by at least the margin on the primary corpus;
- exact paired bootstrap 95% stability interval lower bound must be > 0;
- no domain may have ORION GRS below B3 by more than 0.10;
- false/unnecessary high-level reformulation: ORION <= B3 and absolute <= 0.05;
- harmful regression / lower-level skip: zero tolerated;
- false resolution of evaluator-gold `UNRESOLVED`: zero tolerated;
- no evaluator/label/source leakage tolerated.

Because the corpus is finite and prospectively acquired rather than sampled from a known population, inferential language is bounded to the registered acquisition process; bootstrap intervals are stability summaries, not population-general authority.

## Replication gate

If the primary acquisition passes, freeze a second acquisition snapshot with:
- disjoint source identities;
- at least one domain not used in policy development;
- independently implemented evaluator/scorer;
- independent direct reconstruction of ORION-R2 decisions from the written protocol;
- at least one changed axis (domain, representation regime, evaluator host, or implementation).

The same frozen margin/guards apply. No primary policy update is allowed before replication.

## Stop / recurse rule

A negative is retained. Diagnose whether it is donor dominance, inadequate representation, insufficient probe basis, bad cost model, non-identifiability, or wrong research object. The next successor must alter a materially different causal ingredient and receive a new pre-outcome freeze.

No margin changes, query changes, route deletion, case deletion, label changes, baseline weakening, or endpoint switching after outcome access.
