# P6–P8 executable embedding into live ORION — V1

**Date:** 2026-08-17  
**Source-of-truth runtime:** `main`, framework `0.3.9-shadow` at inspection time  
**Candidate branch:** `shadow/p6-p8-wide-sync-2026-08-17`  
**Status:** structural correspondence audit; not a claim that the candidate calculi are already implemented.

## 1. Purpose

This document answers a stricter question than “can we describe ORION with the new notation?”

For every important P6/P7/P8 formal field, determine whether the live ORION runtime already contains:

- an **EXACT** first-class object with the same relevant semantics;
- a **PARTIAL** object that covers part of the semantics but needs an adapter or stronger invariant;
- a **PROPOSED** research-only object absent from the current runtime;
- an **OWNER_P1–P5** native mechanism that must remain attributed to an existing flagship.

A candidate does not gain novelty from an `EXACT` or `OWNER_P1–P5` mapping. A `PROPOSED` gap is not automatically novel either; it is simply a real implementation/theory gap rather than a renamed field.

## 2. Live ORION source objects used in this audit

### Canonical registry
`src/orion/registry.py` declares:

- framework version `0.3.9-shadow`;
- state coordinates `K`, `W`, `M`;
- core operators `FRAME.v1`, `SEARCH.v1`, `ABSORB.v1`, `RECONSTRUCT.v1`, `DETECT.v1`, `DIAGNOSE.v1`, `REFRAME.v1`, `REOPEN.v1`, `SATURATE_BOUNDED.v3`;
- mechanics substrate identities including `MechanicCell.v1`, `MechanicReceipt.v1`, `TaskEpisode.v1`, `MechanicTraceReceipt.v2`, `MechanicGuard.v1`, `RouteFamilyHealth.rakl-v1`, `ScientificMeaningProjection.v1`, `IgnoranceProjection.v1`, `SelfOrionReadinessGate.v2`, `DevelopmentIssue.v1`, `EvolutionArchive.v1` and related objects.

### Mechanic cell
`src/orion/mechanics/model.py` defines `MechanicCell` with explicit fields for inputs/outputs/handoffs/state/observables/actions/transitions/mathematics/invariants/constraints/objectives/metrics/optimization/uncertainty/resources/failure/falsifiers/diagnosis/storage/provenance/verification/authority/dependencies/children/reopen/search coverage/parent domains/saturation/open empirical coordinates.

### Actions
`src/orion/mechanics/actions.py` defines typed action classes and `MechanicAction` with preconditions, authority effect, side-effect semantics and failure semantics. Current action plans explicitly state that local actions do not directly mint scientific authority; promotion is a separate certificate path. `SEARCH.stop-route` explicitly does not imply task saturation. `REFRAME` stages proposals. `REOPEN` computes dependents/stales closure/reopens affected fibres. `CROSS.AUTHORITY` evaluates promotion and promotes-or-blocks. `CROSS.EXECUTION` binds identities, executes effects and writes receipts.

### Dependencies
`src/orion/mechanics/dependencies.py` defines typed dependency kinds and `DependencyRequirement` with exact identity binding, precondition, failure propagation, fallback semantics and integrity/provenance requirements. Required dependency failure/block/`CANNOT_CHECK` propagates unless an explicit fallback applies.

### Invariants
`src/orion/mechanics/invariants.py` already includes default invariants for:

- generation non-authority;
- typed non-escalation;
- negative-history monotonicity;
- missing-evidence honesty / `BLOCKED` or `CANNOT_CHECK`;
- lineage independence;
- dependent residual reopening;
- evaluator separation;
- uncertainty visibility;
- bounded-closure honesty;
- declared state-transition-only execution;
- local-to-root progress transport;
- resource-is-not-closure;
- failure-no-self-promotion.

### Recursive audit
`src/orion/mechanics/audit.py` already recursively audits child and dependency closures; reports unknown children/dependencies; detects containment, dependency and mixed cycles; and returns `READY_FOR_BENCHMARK`, `OPEN`, or `CANNOT_CHECK`-compatible structures.

### P2 route/progress structures
`src/orion/knowledge/route_family_health.py` already separates local progress from root progress through a preservation interface, treats route-health telemetry as non-authoritative, tracks route-family continuity on declared coordinates, retains prospective/post-hoc chronology and makes programme-health vectors deliberately non-aggregable with non-compensatory coordinates.

### Protected P4/P5 execution
Current development packets bind P4 protected evaluator/candidate separation, immutable hidden labels, production hard-gate execution, independent reproduction and fail-closed custody. P5 protected-suite freeze binds hidden root truth, fresh-transfer identity separation, protected evaluator identity, negative/harmful variant retention and disjoint candidate/protected write surfaces.

---

# Part I — P6 mapping

## 3. P6 state object

Candidate formal state:

\[
E=(\nu,s,D,P,O,A,H).
\]

| P6 component | Live ORION object(s) | Fidelity | Ownership / gap |
|---|---|---|---|
| typed coordinate valuation `nu` | canonical `K/W/M`; `MechanicCell.state_ids`, input/output ids; domain-specific projection objects | `PARTIAL` | P1 owns K/W/M. P6's generalized typed coordinate domain is wider than the three canonical top-level coordinates but mostly expressible through mechanic state/projection identities. |
| claim/certificate status `s` | receipts, `AnswerRecord.v1`, verification/saturation/readiness objects; typed `OPEN/CANNOT_CHECK` patterns | `PARTIAL` | no single universal `Q -> {open, certified, invalid, cannot_check}` registry identified. Adapter required. |
| dependency relation `D` | `dependency_ids`, `external_dependency_contract_ids`, `DependencyRequirement`; reopen triggers | `EXACT/PARTIAL` | structural dependency identity/failure propagation exists. Candidate theorem requires semantic support completeness, which runtime does not guarantee automatically. |
| provenance `P` | `provenance_contracts`, dependency integrity/provenance requirements, trace/episode/receipt identities | `EXACT/PARTIAL` | provenance is first-class, but P6's one unified provenance graph would be an adapter over several receipt/provenance objects. |
| obligations `O` | verification contracts, search-coverage obligations, empirical-open coordinates, dependency preconditions, non-compensatory metric gates, audit questions | `PARTIAL` | obligations exist in multiple typed surfaces; no universal hard/soft residual-obligation registry identified. |
| authority `A` | `authority_boundaries`, action `authority_effect`, CROSS.AUTHORITY, protected evaluator/certificate mechanisms | `PARTIAL` | strong runtime authority rules exist; P8 rather than P6 owns any general authorization formalization. |
| history `H` | `TaskEpisode.v1`, `MechanicTraceReceipt.v2`, negative-history invariant, chronology records, evolution/archive objects | `PARTIAL/STRONG` | retained history is live. P6's explicit trace-equivalence semantics is proposed formal machinery over it. |

### P6 conclusion
P6 cannot claim the existence of an explicit mechanic state as a new ORION idea. The runtime already encodes most dimensions. The possible contribution is in **formal composition semantics across these dimensions**, especially where current schemas are distributed rather than unified.

## 4. P6 mechanic contract

Candidate:

\[
m=(R_m,W_m,Pre_m,Req_m,Eff_m,\tau_m,Emit_m,Fail_m,Inv_m).
\]

| Candidate field | Live ORION mapping | Fidelity | Required adapter / nonclaim |
|---|---|---|---|
| `R_m` read footprint | `input_ids`, `observable_ids`, dependency preconditions, context-selection contracts | `PARTIAL` | live schema lists declared inputs/observables but not one explicit coordinate-level read set over all state. |
| `W_m` write footprint | `output_ids`, `state_ids`, action side-effect semantics, declared transitions | `PARTIAL` | no universal coordinate-level write-set field identified. P6 may need an adapter or a new proposed `write_scope` contract. |
| `Pre_m` | `MechanicAction.preconditions`; dependency preconditions; handoff/verification constraints | `EXACT/PARTIAL` | multiple live precondition surfaces must be composed. |
| `Req_m` hard/soft requirements | verification contracts, authority boundaries, non-compensatory metric gates, search coverage obligations, dependencies, audit questions | `PARTIAL` | current live system has hard requirements but not one universal residual-obligation type algebra. |
| `Eff_m` requested effects | `MechanicAction.action_class`, `side_effect_semantics`; `EXTERNAL_EFFECT`; CROSS.EXECUTION | `PARTIAL` | action/effect types exist; explicit request-vs-allow-vs-commit event algebra is not a single first-class runtime type identified here. ETAS/FAVA remain external donors. |
| `tau_m` transition relation | `transition_semantics`, action plans, declared state-transition-only invariant | `PARTIAL` | transition descriptions are explicit, but a mathematically executable relation over one uniform state space is research-level formalization. |
| `Emit_m` | `output_ids`, handoff fields, receipts/residuals/open questions | `PARTIAL` | residual outputs exist across schemas; one formal emitted-obligation operator is proposed. |
| `Fail_m` | `failure_signatures`, `falsifiers`, `MechanicAction.failure_semantics`, typed dependency failure propagation | `EXACT/STRONG` | runtime already treats failure as typed residual rather than silent success. |
| `Inv_m` | `invariant_ids`, constraint ids, default `MechanicInvariantPlan` | `EXACT/STRONG` | P6 must not claim explicit invariants as novel. |

## 5. P6 theorem-to-runtime correspondence

### P6.T1/T2 dependency reopening
**Live anchor:** `REOPEN` action family + reopen triggers + `residual-reopening` invariant + dependency plans.  
**Ownership:** P1.  
**Candidate addition:** theorem-level sufficiency/minimality relative to a sound dependency abstraction; external TMS/rollback donor pressure remains.

### P6.T3 history-aware commutation
**Live anchor:** action identities, trace receipts, negative-history invariant, chronology records.  
**Fidelity:** `PROPOSED FORMAL SEMANTICS`. Runtime retains chronology, but no general Mazurkiewicz-style independence quotient was identified.  
**Candidate value:** potentially real formal layer if it creates a useful chronology-sensitive composition theorem; concurrency/process literature is parent work.

### P6.T4 non-escalation
**Live anchor:** `generation-non-authority`, typed non-escalation, action authority-effect rule, protected promotion.  
**Fidelity:** `OWNER_P4/P5 + EXACT INVARIANT`.  
**Candidate status:** supporting theorem only.

### P6 residual-obligation preservation
**Live anchor:** missing-evidence honesty, dependency failure propagation, audit questions/open empirical coordinates.  
**Fidelity:** `PARTIAL`.  
**Gap:** no one universal runtime theorem/object saying a hard residual obligation cannot disappear under composition. This is a legitimate formalization target, heavily pressured by effect-system donors.

### P6 recursive audit
**Live anchor:** `RecursiveMechanicAudit`, cycle paths, mixed dependency/containment cycles.  
**Fidelity:** `OWNER_P1 / EXACT IMPLEMENTATION SUBSTRATE`.  
**Candidate status:** no novelty for recursive audit itself.

---

# Part II — P7 mapping

## 6. P7 atlas state

Candidate:

\[
N=(\mathfrak A,i,x,F,R,O,C,V_h,B,H).
\]

| P7 field | Live ORION mapping | Fidelity | Ownership / gap |
|---|---|---|---|
| active representation/chart `i` | `W`, RECONSTRUCT update-atlas/expand-search-universe, REFRAME staged proposal | `PARTIAL` | P1 owns representation/search-universe mutation. No universal chart identity/morphism object was identified. |
| current location/belief `x` | current mechanic/task state, K/W/M, search state | `PARTIAL` | distributed. |
| frontier `F` | SEARCH `inspect-frontier`, backward obligations, open residuals | `PARTIAL/STRONG` | P2/search substrate. |
| routes `R` | retrieval routes, route-family descriptors/lineage, continuity policies, SEARCH expand/stop route | `EXACT/PARTIAL` | P2 owns route semantics. |
| obligations `O` | search coverage obligations, residuals, root critical obligations, audit questions | `PARTIAL` | distributed obligation surfaces. |
| censored/unknown regions `C` | route status, external blockers, open coverage, `CANNOT_CHECK` | `PARTIAL` | P2 owns fail-closed coverage behavior. |
| visited/history `V_h/H` | episodes, chronology records, route-family lineage, trace receipts | `STRONG` | already live. |
| budget `B` | resource coordinates; `resource-is-not-closure` invariant | `STRONG` | budget explicitly cannot silently authorize closure. |
| atlas maps `mathcal M` | generator transports, measurement relations, representation mappings, REFRAME/RECONSTRUCT actions | `PARTIAL` | several domain-specific mapping objects exist, but no universal chart/objective preservation morphism identified. |

## 7. P7 live mechanisms that are already owned

### Route stopping versus task closure
`SEARCH.stop-route` explicitly states that route stop does not imply task saturation. `SATURATE` emits `OPEN/CANNOT_CHECK/bounded-stop`, and route-health telemetry states that it cannot grant scientific authority.  
**Status:** `OWNER_P2`.

### Local progress versus root progress
`RouteFamilyHealth` already requires a root-coordinate preservation interface; absent/refuted preservation keeps surrogate improvement local or `CANNOT_CHECK`. The programme health vector is deliberately non-aggregable and has non-compensatory coordinates.  
**Status:** strong existing internal mechanism. P7 must not reinvent “local progress != root progress.”

### Resource versus closure
The live invariant explicitly states that budget exhaustion with material obligations open yields `CANNOT_CHECK`, never bounded closure.  
**Status:** existing invariant.

## 8. P7 research-only gap: chart/objective support transport

The strongest runtime evidence for P7 is actually a **negative** finding:

- ORION has representation/world/search-universe mutation;
- ORION has domain-specific transport/mapping objects;
- ORION has root-coordinate preservation interfaces;
- ORION has dependency reopening and fail-closed closure;

but this audit did **not** identify one general first-class object that binds all of:

1. old chart/objective identity;
2. new chart/objective identity;
3. partial maps of state/relations;
4. the complete support of an old closure certificate;
5. semantic preservation of obligation meaning;
6. evidence-identity preservation;
7. resulting `TRANSPORT`, `REOPEN`, or `CANNOT_CHECK` decision.

### Fidelity
`PROPOSED RESEARCH OBJECT`, potentially assembled from existing mapping/reopen/provenance mechanisms.

### Candidate P7 discriminator
A chart/objective transformation should be able to preserve content-bound evidence while reopening an old closure when obligation meaning/support scope fails to transport.

This is not enough for novelty—planning abstraction, homomorphism, model revision and ontology evolution are direct parent fields—but it is a real ORION implementation/theory gap rather than merely P1/P2 vocabulary.

---

# Part III — P8 mapping

## 9. P8 effect domains and local authority

Candidate domains:

`REFRAME`, `SEARCH_ROUTE_STOP`, `SEARCH_TASK_STOP`, `MAP_MERGE`, `ASSERT`, `SELF_MODIFY`, plus external effect domains.

### Live effect/action substrate
`ActionClass` already distinguishes inspect, information acquisition, transform, control, verify, external effect and fail-closed actions. Core operator/action prefixes distinguish search, reframe, reopen, authority and execution contexts.

### Live local authority principles
- generated/model text cannot directly increase scientific authority;
- missing mandatory evidence fails closed;
- weaker/different relations cannot silently mint stronger claims;
- candidates cannot rewrite protected evaluator after outcome access;
- local metric improvement needs an explicit root-progress transport witness;
- repeated failure/guard success cannot self-promote;
- external effects require declared adapters/receipts;
- P4/P5 protected packets separate candidate and evaluator/protected write surfaces.

**Conclusion:** P8 cannot claim that ORION lacked capability/authority separation. It is already pervasive.

## 10. P8 formal-field mapping

| P8 field | Live ORION mapping | Fidelity | Gap |
|---|---|---|---|
| effect request identity/domain/scope | action id/class/prefix, execution identity binding, authority boundaries | `PARTIAL` | domain labels exist but not a unified P8 effect-domain type system. |
| hard obligations | non-compensatory metrics, verification/coverage/dependency preconditions, invariants | `PARTIAL/STRONG` | distributed rather than one typed obligation set per effect. |
| grants/roots | protected evaluator/certificate paths, authority boundaries, runtime/protected-host identity bindings | `PARTIAL/STRONG` | no general delegation/grant calculus identified; external authorization logic donors own that parent problem. |
| provenance | provenance contracts, evidence lineage, receipts, protected manifests | `STRONG` | not P8 novelty. |
| epoch/content identity | runtime/build/provider/content hashes, frozen revisions, protected freeze chronology | `PARTIAL/STRONG` | version/identity discipline exists; no universal auth-certificate epoch type identified. |
| `CANNOT_CHECK` | audit verdicts, route health, missing-evidence/resource invariants, many protocol terminals | `EXACT/STRONG` | terminal is already canonical behavior. |
| revocation dependency lineage | dependency/reopen/provenance mechanisms | `PARTIAL` | general authorization-certificate revocation/re-derivation object not identified. |
| protected roots | P4/P5 protected evaluator/custody and write separation | `EXACT DOMAIN-SPECIFIC` | local ownership P4/P5. |
| cross-domain coercion registry | no general registry identified | `PROPOSED` | central possible P8 object. |

## 11. P8 research-only gap: cross-domain coercion

The runtime already has many **domain-local** prohibitions against authority escalation. What is not identified as a first-class shared object is an explicit relation

\[
c:d\Rightarrow d'
\]

with:

- source/target authority domains;
- premises/hard obligations;
- scope transformation;
- content/provenance preservation requirements;
- issuer/root authorized to register the coercion;
- epoch validity;
- dependency lineage for later revocation.

### Why this matters internally
A correct source-domain judgment can still be misused by glue code if the interface exposes a generic `PASS/SUCCESS` rather than a typed authority judgment. The P8 formalism predicts this as a cross-domain type/composition error, not as failure of the source gate.

### Why this does **not** yet establish novelty
Delegation Logic, SecPAL, authorization/trust-management logics, effect systems and information-flow/non-interference systems may already encode the same structure. P8 survives only if donor-faithful comparison plus autonomous-science transfer leaves a real discriminator.

## 12. Revocation correspondence

P6/P7 reopening and P8 revocation share a live dependency skeleton:

- dependencies have identity/failure propagation;
- new residuals stale dependent closures;
- provenance/lineage is retained;
- protected authority/evaluator state is version-bound.

However, P8's alternate-derivation rule—revoke one proof path while retaining/rederiving an authorization with another complete independent trusted path—is not identified as a universal live runtime object. It remains a candidate formalization/evaluation target.

---

# Part IV — exact internal ownership result

## 13. What P6–P8 must **not** claim after this audit

### P6 cannot claim
- first explicit mechanic-cell state/control model;
- first dependencies/provenance/invariants/failure semantics in ORION;
- first recursive mechanic audit/cycle detection;
- first fail-closed missing-evidence rule;
- first dependency reopening;
- first non-escalating authority discipline.

### P7 cannot claim
- first route identity/continuity structure;
- first route stop versus task stop distinction;
- first root-progress preservation requirement;
- first budget-is-not-closure rule;
- first representation/search-universe mutation.

### P8 cannot claim
- first capability-versus-authority distinction in ORION;
- first non-compensatory gate;
- first protected evaluator/root;
- first `CANNOT_CHECK` terminal;
- first no-self-promotion invariant;
- first provenance-bound authority/evidence practice.

## 14. What remains legitimately proposed

### P6
A formal **composition semantics** over the already-rich live mechanic substrate: explicit scientific-state projection, audit-trace equivalence, hard residual-obligation preservation and donor-faithful effect/repair algebra.

### P7
A general **chart/objective support-and-closure transport contract** spanning representation mutation, objective semantics, evidence identity and reopen/`CANNOT_CHECK` decisions.

### P8
A general **cross-domain epistemic authority coercion/revocation layer** over existing local gates, with typed interfaces preventing valid local judgments from becoming foreign-domain authority by accident.

These are implementation/theory gaps only. Each still requires external parent-field saturation and prospective discrimination before novelty.

---

# Part V — executable conservative-embedding plan

## 15. Phase A — schema conformance

Create a deterministic checker that imports the live `src/orion` package and verifies the exact schema anchors used above:

- registered core state/operators/substrate identities;
- required `MechanicCell` fields;
- required `MechanicAction` fields/classes;
- dependency requirement fields;
- invariant kinds/semantic statements;
- recursive-audit cycle surfaces.

Failure means this mapping is stale and every candidate embedding reopens.

## 16. Phase B — native-decision fixtures

For each flagship, freeze at least one positive and one fail-closed native decision:

- P1: reframe/reopen scope;
- P2: route stop versus task stop/open coverage;
- P3: merge versus obstruction/ambiguity;
- P4: assertion promotion versus protected hard-gate block;
- P5: self-change readiness versus missing fresh/protected evidence.

The candidate representation must reproduce the native decision exactly when candidate-only dimensions are inert.

## 17. Phase C — proposed-layer fixtures

Only after Phase B passes:

- P6: add trace-order/residual-obligation composition cases;
- P7: add cross-chart support/closure transport cases;
- P8: add cross-domain coercion/revocation cases.

This sequencing prevents the generalization from hiding a broken embedding.

## 18. Current authority

The executable correspondence is **structurally mapped but not yet decision-equivalence certified**. Exact P1–P5 executable fixtures and clean runtime import checks remain open. All P6/P7/P8 promotion/novelty terminals remain `CANNOT_CHECK`.