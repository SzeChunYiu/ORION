# Donor-product evaluation protocol V2

**Date:** 2026-08-18  
**Purpose:** freeze what would count as ORION outperforming the structures it engulfs.

## 1. Principle

ORION may absorb donor mechanisms without claiming them. To claim **outperformance**, the comparison must not give ORION extra capabilities that the baseline is forbidden to use.

The strongest baseline is an **ideal donor product** containing the same donor-native mechanisms with correct cross-module adapters wherever those adapters are already established by the literature/protocol.

A paper may report:

- superiority over an isolated donor on a cross-structure task only as evidence that integration is necessary, not that the donor is inferior in its own scope;
- superiority over a naive donor product only as evidence that the tested integration rule matters;
- superiority over the ideal donor product only when ORION has an additional prospectively frozen law/interface or measurable engineering property.

## 2. Capability matching

Every comparison records a capability vector:

\[
C=(repair,effects,authorization,provenance,navigation,abstraction,goal\_change,revocation,history).
\]

Primary comparisons require equal capability vectors or an explicit statement that the comparison is a coverage/expressivity experiment rather than a performance contest.

Budgets for model calls, retrieval actions, verification work and external effects must be matched or normalized.

## 3. ORION-16 comparison ladder

### Isolated donors

- TMS/ATMS-like dependency maintenance;
- self-adjusting/incremental computation;
- ETAS-style effect/residual-obligation layer;
- FAVA-style authorization layer;
- dependency-guided rollback/repair.

### Strong product

`ORION-16-PRODUCT` contains dependency maintenance + incremental recomputation + typed effects/residuals + pre-effect authorization + provenance + independent-support preservation.

### ORION-only candidate laws to test

- root-inclusive scientific certification invalidation;
- explicit distinction between computational reuse and certification reuse;
- protected preservation certificates tied to the exact change;
- cross-layer hard-obligation persistence;
- full scientific-footprint composition/audit history.

### Primary measures

- stale scientific certificate rate;
- unnecessary recomputation/reopening rate;
- false preservation rate;
- hard-obligation loss rate;
- authority violation rate;
- recomputation cost;
- proof/audit trace size.

## 4. ORION-17 comparison ladder

### Isolated donors

- fixed-graph/Search-on-Graph style navigation;
- POMDP/belief-space information gathering;
- sound/complete planning abstraction;
- schema/lens/ontology transform;
- SAGA-style objective evolution;
- self-evolving world-model revision.

### Strong product

`ORION-17-PRODUCT` contains all of the above plus ORION-12 route/task stopping and provenance-preserving evidence identity.

### ORION-only candidate laws to test

- evidence-preservation/closure-preservation separation;
- complete scientific support/obligation transport witness;
- ambiguity-conditioned reopening after incomplete transform;
- strict terminal separation under censored/resource-limited navigation;
- representation-change governance distinct from ordinary model update.

### Primary measures

- useful region/obligation discovery;
- premature task closure;
- false closure transport;
- unnecessary reopening;
- harmful reframe rate;
- evidence reuse retained after valid transforms;
- resource cost;
- exploration breadth/concentration as diagnostic, not override.

## 5. ORION-18 comparison ladder

### Isolated donors

- SecPAL/Delegation Logic style proof authorization;
- UCON ongoing authorization;
- ETAS/FAVA effect authorization;
- AgentBound/multi-authority composition;
- authorization propagation;
- AgentAbstain-style non-action competence;
- provenance/execution-provenance systems;
- origin-bound/non-amplifying authority systems.

### Strong product

`ORION-18-PRODUCT` has per-domain typed gates plus a shared full-type coercion registry, commit-time freshness and support-family revocation store.

By theorem, this ideal product is behaviorally equivalent to the shared ORION-18 calculus when semantics are identical. Therefore **behavioral decision accuracy alone cannot establish ORION-18 superiority over this baseline**.

### Additional properties allowed to distinguish architectures

- duplicated-policy inconsistency frequency under controlled updates;
- proof/derivation size;
- audit-query complexity;
- revocation propagation latency/cost;
- policy-drift defect rate;
- ease of adding a new effect domain while preserving old tests;
- number of independently maintained interface rules;
- verification/review burden.

These must be prospectively operationalized before comparison.

## 6. Cross-paper envelope cases

A protected cross-donor benchmark must include:

1. repair + authority;
2. effect + reopening;
3. representation + scientific obligation;
4. goal evolution + provenance;
5. generic permission + scientific discharge;
6. alternative-support revocation;
7. current-state equality + chronology-sensitive policy;
8. censored region + resource exhaustion;
9. clean authorized no-alarm controls;
10. harmful-transform/no-reframe controls.

## 7. Statistical/decision rule

Safety/scientific-authority measures are non-compensatory. A method cannot claim overall superiority if it improves a soft efficiency measure while worsening a protected authority/closure measure beyond the predeclared tolerance.

If multiple methods tie on protected correctness, cost/auditability may break the tie only under a frozen measurement definition.

## 8. Current deterministic preflight

`check_donor_complete_envelope_v1.py` is a finite semantic preflight, not the final real-system experiment. It should:

- reproduce every frozen cross-structure gold terminal;
- expose the errors of a plausible naive product;
- tie an ideal product by construction when the semantics are identical.

This preflight prevents us from designing a later experiment around an already false superiority premise.

## 9. Claim terminals

Until an actual donor-product evaluation is run:

- `ENGULFING = COMPLETE_AT_THEORY/INTERFACE_LEVEL`
- `SUPERIOR_TO_ISOLATED_DONORS = NOT_A_GENERAL_CLAIM`
- `SUPERIOR_TO_NAIVE_INTEGRATION = FINITE_PREFLIGHT_ONLY`
- `SUPERIOR_TO_IDEAL_DONOR_PRODUCT = CANNOT_CHECK`

This protocol allows ORION to maximize width without converting width into an automatic performance claim.
