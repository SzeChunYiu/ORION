# P1-X successor protocol V1 — Scientific Revision Responsibility

Date: 2026-08-19  
Parent issue: #529  
Programme: #528  
Base: `main@f2d6b8b3f58da3e3577975ac5215c7439a9ffc5f`  
Status: `PROTOCOL_FROZEN__NO_PROTECTED_OUTCOMES_ACCESSED`

## Research question

Does an explicit scientific-layer escalation contract add value above donor-complete diagnosis, repair, revision and authorization systems when the system must distinguish:

1. what caused a failure;
2. what intervention would restore the task; and
3. what scientific epistemic layer the evidence actually justifies changing?

The frozen P1 v2.2.4 result remains historical/bounded evidence and is not pooled with this successor.

## Novelty boundary before execution

Donor-owned and not claimed as P1-X atomic novelty:

- generic belief revision / minimal change;
- evidence-gated revision contracts;
- causal/fault diagnosis and repair assignment;
- diagnosis-conditioned recovery;
- M-open model-class expansion and active experiment design;
- representational-regime revision;
- goal/objective evolution;
- dependency rollback / truth maintenance;
- generic mutation/action authorization;
- certificate-bound execution;
- generic reflective research-agent orchestration.

P1-X tests only the incremental coupling:

> identify the currently justified scientific revision layer, require registered strictly narrower admissible revisions to be exhausted/refuted before broader mutation, preserve protected state and exact reopen scope, and return `UNRESOLVED` when multiple incomparable minimal revision classes remain.

An ideal information-equivalent donor product is expected to tie extensionally if supplied identical semantics. P1-X therefore makes no inherent-expressivity claim.

## Scientific case object

Normative schema: `SCIENTIFIC_REVISION_RESPONSIBILITY_CASE_V1.schema.json`.

Each case binds:

- visible anomaly/trajectory;
- candidate-visible evidence and explicit unknown/unavailable evidence;
- causal responsibility set;
- best intervention set;
- scientifically justified revision set;
- claim-relative invasiveness relation;
- registered narrower alternatives and counterfactual outcomes;
- protected invariants;
- dependency graph and exact reopen set;
- ambiguity state;
- correct terminal;
- candidate information/tool budget;
- protected gold provenance.

`causal responsibility`, `best intervention`, and `scientifically justified revision` are distinct labels by design.

## Domain families

Protected evaluation spans five materially different families:

1. software/debugging;
2. scientific retrieval/discovery;
3. semantic integration;
4. evidence/verification;
5. model/experiment design.

The fifth family must distinguish at least measurement/data error, parameter/model-selection error, model-form/model-class inadequacy, and representation/measurement-regime inadequacy.

Question/objective/formulation responsibility is included where task-isomorphic, but objective revision itself remains donor/#288 territory.

## Required archetypes

Each domain must instantiate all eight archetypes:

A. narrow repair sufficient;  
B. high-level revision necessary;  
C. incomparable minimal responsibilities -> discriminator / `UNRESOLVED`;  
D. diagnosis != prescription;  
E. external/evaluator/measurement responsibility where scientific-content mutation is wrong;  
F. locally successful high-level revision that violates a protected invariant;  
G. correct revision class with over- and under-reopen variants;  
H. clean no-change and insufficient-evidence/`CANNOT_CHECK` controls.

## Scale and split

Development corpus:

`5 domains x 8 archetypes x 5 variants = 200` non-authorizing cases.

Protected corpus:

`5 domains x 8 archetypes x 10 variants = 400` disjoint cases.

Rules:

- dev and protected identities/seeds are disjoint;
- at least one whole-template holdout per domain;
- protected gold is inaccessible during controller/baseline tuning;
- all protected cases are reported; no post-hoc deletion;
- if a larger exact finite universe is cheaply enumerable, prefer the full universe and report exact bounded counts.

## Frozen arms

Normative registry: `P1_X_BASELINE_REGISTRY_V1.json`.

### B1 — DONOR_COMPLETE_GREEDY

Receives the same diagnosis, admissible candidates, evidence gates, dependency/protection data, mutation authorization and execution enforcement as P1-X. Chooses the highest validated/predicted task-restoration utility among currently admissible candidates. It has no explicit `strictly narrower repair must be exhausted before broader scientific revision` rule and no dedicated incomparable-minima discriminator rule.

### B2 — SUCCESS_AUTHORIZES_REFRAME

Same information/modules/budget. A high-level revision is admitted when it restores the target and passes generic protected safety, without lower-level necessity/exhaustion.

### B3 — IDEAL_TYPED_PRODUCT

Receives exactly the P1-X responsibility classes, invasiveness relation, counterfactual outcomes, preservation predicates, reopen map and authority predicates. It implements the same decision semantics if logically possible. It is an equivalence/boundary arm, not an arm P1-X is expected to outperform.

### P1-X — MINIMAL_SCIENTIFIC_ESCALATION

1. compute evidence-admissible revision candidates;
2. remove broader candidates when a registered strictly narrower admissible candidate is demonstrated sufficient;
3. if no candidate remains, block/continue diagnosis;
4. if multiple incomparable minimal candidates remain, request discriminator / `UNRESOLVED`;
5. for a unique high-level candidate require target restoration, protected-invariant preservation, exact reopen-scope fidelity and external authority;
6. only then issue the execution certificate.

## Primary outcome

`Exact Scientific Revision Decision (ESRD) = 1` iff all applicable conditions are correct:

1. terminal class;
2. selected revision class;
3. no broader-than-justified escalation;
4. protected invariants preserved;
5. reopen scope exact.

Primary hypothesis:

> `H-P1X`: on the protected 400-case battery, P1-X improves paired ESRD over `B1 DONOR_COMPLETE_GREEDY` by at least `+0.10` absolute, with the lower bound of the predeclared 95% paired bootstrap interval above zero, while satisfying all non-regression gates.

The `+0.10` practical margin is prospective and is not derived from old P1 outcomes.

## Non-regression gates

- lower-level repair success: non-inferior to B1 within `-0.02` absolute on archetype A/lower-level controls;
- false high-level reframe rate: no worse than B1 by more than `+0.02` absolute;
- protected-invariant violations: target `0` on the exact protected battery for any headline safety statement;
- `UNRESOLVED/CANNOT_CHECK` only scores as correct when it is the gold terminal;
- cross-domain headline requires each domain ESRD difference versus B1 to be greater than `-0.05` and full per-domain reporting.

## Analysis

- paired ESRD difference with domain-stratified bootstrap 95% CI;
- exact McNemar test as secondary paired binary check;
- per-domain effects always reported;
- Holm correction for confirmatory secondary P1-X vs B1/B2 comparisons;
- B3 equivalence assessed formally plus exhaustive/metamorphic agreement, not significance testing;
- null/harmful cases and all denominators retained.

## Information and compute fairness

Primary coupling comparison must hold constant:

- candidate-visible information;
- diagnosis engine outputs;
- recovery candidates;
- tool/query/intervention budgets;
- dependency/protection information;
- generic authorization/execution machinery.

Only the escalation coupling rule differs between P1-X and the primary B1/B2 controls.

## Architecture-independence phase

After the primary coupling study is frozen, repeat with at least two diagnosis policies and at least two recovery policies where task mapping is valid. Architecture-level wording requires the P1-X effect direction to survive donor substitution and must report interactions/costs.

## Protected-outcome firewall

Before protected execution, all must be content-bound:

- schema;
- domain/archetype generators;
- dev/protected seeds/identities;
- B1/B2/B3/P1-X semantics;
- ESRD metric;
- practical/non-inferiority margins;
- analysis script tested only on dummy/dev labels;
- candidate-visible/protected field separation;
- contamination/exclusion manifest.

Any material change after protected outcome access creates V2; V1 results remain immutable.

## Literature convergence used for this freeze

Issue #529 records two consecutive independent no-material-change rounds after material earlier narrowing:

- model criticism / uncertainty / minimal-diagnosis route;
- theory-change / objective-reformulation / reflective-runtime route.

A new material donor legitimately reopens this protocol before outcome access.

## Result authority

Current result state: `CANNOT_CHECK`.

No result, novelty promotion, or manuscript broadening is authorized by this protocol freeze. Positive outcomes must route through #283 independent verification and #287 novelty authority before any widened P1 claim is promoted.
