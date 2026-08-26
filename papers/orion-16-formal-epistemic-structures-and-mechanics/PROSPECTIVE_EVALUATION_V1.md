# ORION-16 prospective evaluation V1 — discriminating mechanic-contract tests

**Candidate:** Formal Epistemic Structures and Mechanics  
**Status:** protocol draft, **not frozen / not result-bearing**  
**Owners:** #335, #353; literature/donor constraints from #334/#352  
**Rule:** no positive score can authorize a novelty/superiority claim until the protocol is frozen before execution and routed through #283 where applicable.

## 1. Research question

Does a donor-faithful epistemic mechanic contract add a measurable property beyond simpler or donor-specific representations when state changes have dependencies, hard residual obligations, scoped authority and retained history?

The experiment is **not** designed to show that typed state machines are better than untyped code. It is designed to discriminate the surviving ORION-16 composition hypothesis.

## 2. Systems/representations under comparison

All baselines operate on the same frozen hidden instance and receive only the information their formalism is allowed to represent.

### B0 — plain transition graph
Represents states and executable transitions only. No explicit authority, hard residual obligations, provenance dependency or repair semantics.

### B1 — dependency repair
Represents support/dependency edges and performs selective downstream invalidation/replay. This baseline should instantiate the strongest feasible TMS/dependency-guided rollback donor semantics for the synthetic family rather than a deliberately weak reset rule.

### B2 — effect/obligation typing
Represents requested/committed effect classes and hard residual obligations, following an ETAS-style donor projection where possible, but without ORION-16 dependency repair/epistemic history composition.

### B3 — evidence-backed authorization
Represents scoped permission/evidence requirements using a FAVA-/authorization-logic-style donor projection, but without ORION-16 dependency repair and history-aware composition.

### B4 — ORION-11-native mechanic/reopening gate
Exact ORION-11 fixtures once the conservative embedding is implemented. This is mandatory for ORION-11-like reconstruction cases.

### ORION-16 — combined mechanic contract
Represents typed effects, hard residual obligations, provenance/dependency, scoped commit authority, selective reopening and retained audit history under the current formal core.

A baseline may be omitted only with an explicit `CANNOT_CHECK` reason (e.g. no faithful implementable donor mapping). It must not be silently replaced with a strawman.

## 3. Exact-ground-truth instance families

### F1 — dependency-only repair
A directed acyclic support graph contains one corrupted upstream coordinate. No authority or hard obligation complication exists.

**Purpose:** negative control. ORION-16 should reduce conservatively to dependency repair and should not reopen more state than B1.

### F2 — authority-bearing mutation
A transition is computationally valid and dependency-local but lacks authority for one write coordinate.

**Ground truth:** commit must be `UNAUTHORIZED`; no scientific-state mutation may be retained.

### F3 — residual-obligation loss trap
Mechanic A succeeds locally but emits a hard obligation; mechanic B later succeeds computationally without discharging it.

**Ground truth:** final state retains the obligation or terminates `CANNOT_CHECK`; success must not erase it.

### F4 — stale dependent certification
A material upstream coordinate changes and a downstream certificate depends on it.

**Ground truth:** every affected certificate reopens; independent support remains certified.

### F5 — alternative independent support
A certificate has two complete independent support derivations. One support branch is invalidated.

**Ground truth:** the certificate remains valid if the remaining derivation is complete under the frozen semantics.

### F6 — separated mechanics with history
Two mechanics have separated scientific read/write/evidence/authority footprints.

**Ground truth:** current scientific projection commutes; audit sequences differ by order but are equivalent under the frozen independence relation.

### F7 — chronology-sensitive policy
Two effects commute on current state, but a later policy reads chronology/epoch.

**Ground truth:** the histories must remain distinguishable; a representation that erases chronology is unsound for the later policy.

### F8 — recursive audit cycle
An auditor recursively invokes the same unresolved audit state without a decreasing rank/cycle guard.

**Ground truth:** nontermination/cycle risk is detected.

### F9 — protected-root self-authorization
A candidate controls its own admission predicate/evidence but not an external protected property label.

**Ground truth:** internal acceptance cannot authorize promotion.

### F10 — full-reset-sufficient negative control
All downstream state is dependent on the changed coordinate.

**Purpose:** ORION-16 should not claim a preservation advantage where full reset is already minimal.

## 4. Cross-domain transfer families from #353

At least three families must be instantiated before any broad ORION-16 claim:

1. **memory/state repair** — typed memory-to-action dependency and selective replay;
2. **effectful workflow** — tool/action requests with scoped authorization and residual obligations;
3. **non-LLM symbolic workflow** — exact state-transition/dependency ground truth.

A fourth ORION-11-like reconstruction family tests conservative internal embedding but does not count as external transfer.

## 5. Generator schema

Each instance should serialize at least:

```text
instance_id
family
seed_or_exhaustive_index
coordinates + typed domains
initial valuation
claims/certificates + status
mechanics
read/write footprints
requested effects
hard/soft obligations
authority grants/scopes/epochs
provenance identities
dependency graph/hypergraph
history prefix
hidden defect/intervention
expected admissible terminal
expected changed coordinates
expected reopened/revoked certificates
expected retained independent certificates
expected residual obligations
expected trace-equivalence class or chronology distinction
```

For exhaustive finite families, `seed_or_exhaustive_index` is the canonical enumeration index and randomness is forbidden.

## 6. Primary metrics

### Safety/correctness
- unauthorized commit false-negative rate;
- stale certification retained rate;
- hard residual-obligation loss rate;
- invalid composition acceptance rate;
- self-authorization acceptance rate.

### Conservation
- collateral reopening rate: independent certified objects unnecessarily reopened;
- retained-valid-state ratio;
- alternate-support preservation correctness.

### Composition/history
- projected commutation correctness;
- chronology erasure error on history-sensitive cases;
- recursive-cycle detection.

### Resource
- representation/checking time;
- number of retained/replayed nodes;
- serialized contract size.

## 7. Primary hypotheses

### H1 — conservative dependency repair
On F1, ORION-16 matches the strongest dependency-repair baseline's correct reopen/preserve decisions.

### H2 — hard-obligation/authority discrimination
On F2/F3, ORION-16 rejects/retains cases that a dependency-only baseline cannot represent without extra policy state.

### H3 — history distinction
On F6/F7, ORION-16 preserves both current-state commutation and audit chronology needed by later policy.

### H4 — no universal dominance
On F1/F10, ORION-16 provides no scientific advantage from extra dimensions that are inactive; overhead is reported rather than hidden.

A publishable empirical result requires a discriminator on H2/H3 or a comparable cross-domain result, not merely H1.

## 8. Evaluation discipline

- freeze generator code and hidden expected labels before running system variants;
- no hand edits to failing instances after seeing comparative outcomes;
- retain every negative/null instance and result;
- report every family, not only families where ORION-16 wins;
- report exact `CANNOT_CHECK` adapter failures;
- separate implementation bug fixes from result-bearing protocol revisions;
- any protocol revision after result visibility creates V2 with a new prospective run.

## 9. Statistical treatment

For exhaustive finite families, report exact counts/rates with no null-hypothesis significance theater.

For sampled larger families, predeclare the sampling distribution, seed set, primary metric and interval method before execution. Do not pool structurally different families into one headline number without per-family results.

## 10. Promotion/failure criteria

### Supports separate ORION-16 candidate
At least one non-ORION-11 transfer family shows a predeclared composition/repair discriminator that cannot be reproduced by the strongest faithful donor-specific baseline without adding the ORION-16 coupling being tested, while negative controls remain conservative.

### Merge/strike pressure
- ORION-16 matches B1/B2/B3/B4 on every scientifically relevant verdict;
- differences are only notation/overhead;
- strongest parent formalism already derives the same composition result;
- the only positive cases are ORION-11-native reopening/audit mechanisms.

## 11. Current result authority

`NO_RESULT`. This file defines a prospective experiment only.