# ORION-16–ORION-18 parent-field pressure supplement V2 — 2026-08-17

**Status:** additive breadth pass; does not replace `PARENT_FIELD_PRESSURE_MAP_2026-08-17.md`.  
**Purpose:** record parent fields discovered after the first wide map that materially tighten ORION-16/ORION-17/ORION-18.  
**Rule:** a newly discovered parent may contract a candidate. That is a successful assimilation outcome.

## 1. ORION-16 — self-adjusting and incremental computation is direct pressure on change propagation

### Self-adjusting computation
Classic self-adjusting computation already tracks data/control dependencies in dynamic dependence graphs and performs **change propagation** so a computation after input mutation is updated by re-executing only affected parts while preserving reusable work. The literature also provides operational/semantic correctness results and later parallel variants with explicit dependency structures and propagation-cost analyses.

Representative parent routes:

- Acar, Blelloch, Harper and collaborators — adaptive/self-adjusting computation and dynamic dependence graphs;
- *A Consistent Semantics of Self-adjusting Computation* — semantics/correctness of memoization + change propagation;
- later efficient parallel self-adjusting computation using explicit control/dependency structures.

### Consequence for ORION-16
ORION-16 must not claim generic **dependency graph + selective recomputation after change** as a new formal mechanism. This pressure is stronger than the agent-specific rollback donor because it comes from a mature programming-languages theory of incremental change.

The remaining ORION-16 question tightens to what ordinary self-adjusting computation does **not** by itself settle:

- whether a requested state change is epistemically authorized to commit;
- whether a hard scientific/evidence obligation remains unresolved after a locally successful recomputation;
- whether a prior certificate should become `OPEN`, `CANNOT_CHECK`, `REVOKED`, or remain valid under independent support;
- how content-bound provenance and protected authority roots constrain reuse;
- how audit chronology remains observable even when current computation state is equivalent.

### Required new discriminator
Add a self-adjusting/incremental-computation baseline family to #335/#353. On dependency-only instances ORION-16 should reduce conservatively to the incremental donor. Candidate value can only arise on pre-frozen cases where epistemic obligations/authority/history change the correct verdict beyond recomputation efficiency.

---

## 2. ORION-17 — representation preservation has deep parents in schema evolution, lenses and conceptual change

### Schema transformation and specification preservation
Database/schema-evolution work has long formalized transformations between schemas and preservation of semantic/specification properties. Work on schema evolution with provenance shows that exact inversion/reconstruction can require additional provenance, and that provenance can be necessary for reproducing prior scientific results under evolved schemas.

### Bidirectional transformations and lenses
Lens theory already formalizes relationships between sources, views and updates; update lenses distinguish views from updates and define composition. Relational/incremental lenses propagate changes bidirectionally and efficiently. These are direct parents for any ORION-17 claim framed merely as “partial map between representations that preserves state.”

### Concept/signature and ontology change
Belief/theory repair and ontology-revision work also changes signatures, concepts or interpretations rather than only truth values inside a fixed vocabulary. Therefore `rho:T -> T'` and semantic-preservation maps are not sufficient novelty.

### Consequence for ORION-17
The ORION-17 residual should contract from generic **support-preserving representation change** to the more specifically scientific-epistemic question:

> when a chart/schema/ontology/objective changes, which **evidence identities and derivations** remain transportable, and separately, which **scientific closure/obligation-authority judgments** remain licensed?

This distinction matters because a database/view transformation can preserve data or reconstruct a prior state while the *scientific question or obligation semantics* has changed. ORION-17's strongest candidate theorem therefore remains the asymmetry:

\[
\text{evidence transport} \not\Rightarrow \text{closure transport}.
\]

A content-bound observation may survive an objective/ontology change while an old task-completion certificate must reopen.

### Required new donor baselines
#337/#353 should add at least:

- a schema/specification-preserving transformation baseline;
- a lens/bidirectional-transformation style baseline;
- a provenance-assisted schema-evolution/reconstruction case;
- a concept/signature-change or ontology-reinterpretation case.

The benchmark discriminator is no longer whether a map exists. It is whether ORION correctly separates **data/evidence preservation** from **obligation/closure preservation** under the same transformation.

---

## 3. ORION-18 — proof-carrying, stateful and typed authorization sharply pressure the coercion story

### Proof-carrying / linear authorization
Proof-carrying authorization and linear authorization logics already model authorization as production/checking of formal proofs, including effect-sensitive/resource-sensitive policies. Generic proof-bearing authority is therefore prior art.

### Stateful authorization logic
Stateful authorization logic explicitly includes system state and time inside authorization reasoning. ORION-18 cannot claim novelty simply for epochs, policy state or state-conditioned authorization.

### Type disciplines for policy compliance
Authorization-policy type systems already verify that implementations conform to logical authorization policies, including dependency on principals and adversarial/compromised contexts. A ORION-18 “typed interface prevents invalid authorization use” thesis must be compared directly to this literature.

### Logical attestation
Logical attestation already uses attributable, unforgeable logical statements about program/runtime properties as machine-checkable credentials for authorization. Content-/identity-bound proof objects are not new by themselves.

### Policy composition / multi-valued logic
Formal access-control work already studies composition of grant/deny/conflict/unspecified policies. Multi-valued policy composition is relevant pressure on ORION-18's distinction among `ALLOW`, `DENY`, `CANNOT_CHECK`, conflict and unresolved states.

### Non-interference / information-flow typing
Compositional non-interference systems already enforce that information/security classifications do not flow across forbidden interfaces. ORION-18's “authority non-fungibility” could collapse to a standard information-flow/type discipline unless its epistemic semantics adds something real.

### 2026 stateful agent governance
A very recent agent-governance result, *Stateful Governance for Concurrent Agentic Systems* (arXiv:2608.02764), identifies **stale authorization** as a core concurrent-agent failure and proposes policy-state serializability: committed effects must be explainable as authorized against the policy state immediately before they occur. This directly pressures ORION-18's epoch/stale-certificate story.

### Consequence for ORION-18
Generic cross-domain coercion, epoch validity and proof-carrying authorization are not enough. The remaining candidate should sharpen to **scientific-epistemic authority transport** where the source judgment and target action differ not only in security domain but in the *meaning of the epistemic obligation being discharged*.

Examples:

- route-local exhaustion is a valid source-domain fact but does not discharge global scientific coverage;
- evidence/source support is valid but does not discharge independent verification;
- semantic correspondence is valid but does not discharge measurement/referent merge obligations;
- replay improvement is valid but does not discharge fresh-transfer/protected-promotion obligations.

The scientific residual, if any, is not simply “typed values do not flow.” It is that **correct epistemic judgments have typed discharge semantics**, and an explicit coercion must prove that the source judgment satisfies the target domain's hard obligations without changing their meaning.

### Required new baselines
#340/#341/#353 should include or formally compare against:

- proof-carrying / linear authorization;
- stateful authorization logic with time/state;
- authorization-policy type disciplines;
- logical-attestation-style proof credentials;
- explicit policy-composition semantics with conflict/unspecified states;
- non-interference/information-flow formulations;
- a policy-state-serializable/stale-authorization baseline inspired by current concurrent-agent governance.

A separate ORION-18 survives only if these donors still miss a reproducible **epistemic-obligation transport** failure that the ORION-18 calculus catches without excessive refusal.

---

## 4. Cross-paper synthesis after V2 pressure

The new parent fields sharpen a common separation between three kinds of preservation:

1. **computational preservation** — can an updated computation reuse unaffected dependency structure?;
2. **representational/evidence preservation** — can state, data, evidence or meaning be transported across a transformation?;
3. **epistemic authority preservation** — does the transported object still discharge the scientific obligation required for a closure/merge/assert/promotion action?

ORION-16 is primarily pressured by (1), ORION-17 by (2), and ORION-18 by (3), but the papers interact at their boundaries.

A possible programme-level theorem schema is:

\[
\text{preserved object} + \text{preserved derivation} + \text{preserved obligation semantics}
\Rightarrow
\text{eligible authority transport};
\]

if any required preservation premise fails, the domain-specific terminal is `REOPEN`, `REVOKED`, `DENY`, or `CANNOT_CHECK` rather than silent carry-over.

This is a **synthesis target only**. It must be compared against lens laws, incremental-computation correctness, authorization proof systems and policy/non-interference composition before any novelty claim.

## 5. Immediate disposition changes

### ORION-16
- `dependency-scoped recomputation/repair`: **ADOPT / DO NOT CLAIM**;
- possible residual: epistemic commit/obligation/history semantics layered over change propagation.

### ORION-17
- `representation-preserving map`: **ADOPT / DO NOT CLAIM**;
- possible residual: evidence-versus-closure/obligation transport under chart/objective change.

### ORION-18
- `typed/proof-carrying/stateful authorization`: **ADOPT / DO NOT CLAIM**;
- possible residual: target-obligation-preserving coercion across heterogeneous scientific epistemic domains.

All three remain `CANNOT_CHECK` for paper-level novelty.