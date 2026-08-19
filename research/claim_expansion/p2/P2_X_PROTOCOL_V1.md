# P2-X successor protocol V1 — Unresolved-Route Scientific Closure

Date: 2026-08-19  
Parent: #530  
Programme: #528  
Base: `main@f59133b48cc4309c75bc059e90428242ead8531c`  
Status: `PROTOCOL_FROZEN__NO_PROTECTED_OUTCOMES_ACCESSED`

## Research question

After granting strong retrieval and stopping mechanisms to the host system, does an explicit scientific-route authority layer reduce false task-global closure when a material acquisition route is unavailable, censored, provider-invalid, or not question-conditionally processed?

The current P2 narrowed paper remains historical evidence and is not pooled with this successor.

## Novelty boundary before execution

Donor-owned / not P2-X atomic novelty:

- lexical/dense/hybrid/reasoning-aware retrieval;
- query planning and iterative search;
- learned STOP/CONTINUE;
- confidence/uncertainty stopping;
- utility/EVPI stopping;
- decision-sufficiency stopping;
- per-claim evidence-coverage stopping (HALT-like);
- coverage-driven deep-research objectives and evidence-based completion;
- finite obligation ledgers / finite closure certificates (KnowPlan-like);
- generic workflow obligation graphs;
- generic open-world closure-gap terminology.

P2-X tests only the incremental scientific-acquisition contract:

> route-local stopping signals do not self-authorize task-global scientific closure when a predeclared material route remains unresolved. Unavailable/censored/provider-invalid routes supply missing authority, not negative evidence. Content identity is also distinct from question-conditioned processing completion.

An ideal information-equivalent product given the same unresolved-route semantics is expected to tie. P2-X makes no inherent-expressivity claim.

## Exact case object

Each case contains:

- task/question identity;
- route inventory and route materiality;
- route state: `AVAILABLE / UNAVAILABLE / CENSORED / PROVIDER_INVALID`;
- route-local signals: evidence coverage, decision sufficiency, utility stop, finite obligation certificate;
- content identities acquired per route;
- question-conditioned processing state per acquired content;
- route-local correct stop decision;
- task-global correct terminal;
- protected decisive-evidence locations;
- budget and provider-state provenance.

Candidate-visible route failure state is explicit. Protected gold contains whether the unresolved route is actually decision-changing; the candidate never receives that fact directly.

## Domains

Five exact acquisition families:

1. `SCIENTIFIC_LITERATURE`;
2. `WEB_API_EVIDENCE`;
3. `DATASET_REGISTRY`;
4. `CODE_ARTIFACT_REPOSITORY`;
5. `EXPERIMENT_MEASUREMENT_ROUTE`.

## Eight archetypes per domain

A. `ALL_OBLIGATIONS_DISCHARGED` — every material route available and complete; task stop is correct.  
B. `AVAILABLE_ROUTE_STOPS_OTHER_OPEN` — one route locally stops while another available material route is still open.  
C. `MATERIAL_ROUTE_UNAVAILABLE` — all available routes locally stop; a material route is unavailable.  
D. `MATERIAL_ROUTE_CENSORED` — same, but censored access makes absence non-evidence.  
E. `PROVIDER_INVALID` — route returns transport/provider failure and cannot discharge closure.  
F. `DUPLICATE_ROUTE_COVERAGE` — redundant/correlated routes appear to increase coverage while an independent material obligation remains open.  
G. `ACQUIRED_NOT_QUESTION_PROCESSED` — content is already acquired/deduplicated, but question-conditioned processing for a material item is incomplete.  
H. `LOW_UTILITY_HARD_ROUTE_OPEN` — expected marginal utility is low, but a hard scientific verification/source obligation remains open.

## Scale

Development: `5 x 8 x 5 = 200` non-authorizing cases.  
Protected: `5 x 8 x 10 = 400` disjoint cases.

The factorization `(5,8,10,400)` is frozen.

## Terminals

Route decision per route: `ROUTE_STOP / ROUTE_CONTINUE / ROUTE_CANNOT_CHECK`.

Task terminal: `TASK_STOP / CONTINUE / CANNOT_CHECK`.

Rules:

1. A material available route may `ROUTE_STOP` when its local donor-complete stopping obligations are satisfied.
2. `UNAVAILABLE`, `CENSORED`, or `PROVIDER_INVALID` material routes are `ROUTE_CANNOT_CHECK`, never `ROUTE_STOP` by absence.
3. Task `TASK_STOP` requires every material route obligation to be discharged and every required acquired content item to be question-conditionally processed.
4. If a material route is unavailable/censored/provider-invalid and protected materiality cannot be discharged by an allowed substitute, task terminal is `CANNOT_CHECK`.
5. If a material route is available but still open, duplicated coverage is misleading, question-conditioned processing is incomplete, or a hard route remains open despite low utility, task terminal is `CONTINUE`.
6. Route-local `ROUTE_STOP` never implies `TASK_STOP` by itself.

## Arms

Registry: `P2_X_BASELINE_REGISTRY_V1.json`.

### B1 — DONOR_COMPLETE_AVAILABLE_ROUTE_PRODUCT

Receives HALT-like evidence coverage, decision sufficiency, utility/EVPI, finite obligation certificates, route identities/status, deduplication, and generic workflow obligations. It treats every available route strongly, but its global aggregation closes the task once all **available** material routes locally stop; unavailable/censored/provider-invalid routes are excluded from the global denominator.

### B2 — GLOBAL_SUFFICIENCY_AGGREGATOR

Same information/budget, but a global evidence/decision-sufficiency signal can authorize task stop even if an unresolved hard route remains.

### B3 — IDEAL_TYPED_ROUTE_PRODUCT

Receives exactly P2-X route materiality, unresolved-route semantics, question-conditioned processing obligations and task-closure rule. Expected to tie P2-X extensionally; no significance test.

### P2-X — FAIL_CLOSED_ROUTE_AUTHORITY

Applies the deterministic terminal rules above.

## Primary metric

`Exact Scientific Closure Decision (ESCD)=1` iff:

- every route decision is correct;
- task-global terminal is correct;
- no unresolved material route is laundered into closure;
- no provider/censor failure is counted as negative evidence;
- required question-conditioned processing is complete before closure.

Primary hypothesis:

> `H-P2X`: on the protected 400-case battery, P2-X reduces false task-global closure and improves paired ESCD over B1 by at least `+0.10` absolute, with the predeclared domain-stratified bootstrap 95% lower bound above zero, while preserving correct closure efficiency on archetype A.

## Non-regression gates

- archetype-A correct task stop: P2-X non-inferior to B1 within `-0.02`;
- false task closure rate: P2-X no worse than B1 and target zero for any headline fail-closed claim;
- unnecessary `CANNOT_CHECK` on all-available clean cases: target zero;
- each domain P2-X minus B1 ESCD > `-0.05` for any cross-domain wording;
- matched query/tool/provider-information budgets.

## Analysis

- paired ESCD difference;
- domain-stratified bootstrap 95% CI, 20,000 reps, seed 20260819;
- exact McNemar secondary test;
- Holm correction for P2-X vs B1/B2 secondary family;
- B3 equivalence by exact decision equality;
- all cases/denominators retained.

## Protected-outcome firewall

Before outcome access, content-bind schema, dev/protected identities, route/archetype generator, arms, ESCD, margins, analysis and candidate/protected field separation. Any material post-access change creates V2.

## Literature convergence used for freeze

#530 records the material architecture narrowing from HALT, Don't Stop Early, KnowPlan, Confidence-Based/decision-theoretic stopping and Science of Intent, followed by two independent no-material-change routes including iCORE/work-obligation and provider-failure pressure.

## Result authority

Current result: `CANNOT_CHECK`.

No successor result or manuscript broadening is authorized before protected execution, independent verification and #287 novelty disposition.
