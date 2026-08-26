# ORION-16–ORION-18 expert-review addendum V2

**Date:** 2026-08-17  
**Relationship:** additive to `EXPERT_REVIEW_LOG_V1.md`.  
**Status:** internal adversarial review functions, not external peer review.

## R13 — self-adjusting computation collapses generic ORION-16 change-propagation claims

### Pressure
Self-adjusting computation already records dynamic data/control dependencies and propagates input changes through only affected computation, with formal semantics/correctness and later parallel dependency-tracking systems.

### Review
- **FL:** ORION-16 graph-only minimal reopening/change propagation is structurally close to mature incremental-computation results and cannot carry novelty alone.
- **FME:** add a self-adjusting/incremental baseline. On pure dependency-recompute cases, ORION-16 should behave conservatively rather than inventing different outputs.
- **ENT:** ORION-17 may consume the same dependency substrate after a reframe, but navigation/closure semantics are separate.
- **AGL:** the useful distinction begins when recomputation is technically possible but the mutation/commit lacks authority or leaves a hard evidence obligation unresolved.
- **SENA:** change wording from “ORION-16 generalizes selective repair” to “ORION-16 tests whether epistemic obligation/authority/history semantics add anything beyond established change propagation.”

### Disposition
**ADOPT / DO NOT CLAIM:** dependency-driven change propagation and affected-only recomputation.

**Retain as candidate:** interaction with commit authorization, hard residual obligations, provenance/certification status and chronology-sensitive audit.

---

## R14 — lenses/schema evolution/conceptual change collapse generic ORION-17 preservation-map claims

### Pressure
Schema-transformation work already studies semantic/specification preservation; provenance-aware schema evolution studies reconstruction across schema versions; lenses/bidirectional transformations formalize update-preserving relationships; theory/ontology revision changes signatures and conceptual vocabularies.

### Review
- **FL:** a partial map `rho:T -> T'` plus preservation laws is not by itself a new navigation theorem.
- **FME:** add lens/schema-evolution fixtures as conservative donors. Require ORION to agree when the only question is state/data preservation.
- **ENT:** the sharper ORION-17 question is whether a transported observation still closes the **new scientific obligation**, not whether the raw datum survives.
- **AGL:** automatic conversion of preserved evidence into new task closure is an authority/discharge coercion and should be explicit.
- **SENA:** the publishable residual, if any, should be phrased as **evidence-versus-closure transport under representation/objective change**, not generic topology preservation.

### Disposition
**ADOPT / DO NOT CLAIM:** representation transformations, bidirectional update laws, specification preservation and provenance-assisted reconstruction.

**Retain as candidate:** separation of content/evidence preservation from scientific-obligation/closure preservation.

---

## R15 — proof-carrying/stateful/type-disciplined authorization collapses generic ORION-18 coercion claims

### Pressure
Authorization literature already supplies proof-carrying credentials, linear/effect-sensitive authorization, explicit system state/time, type systems proving implementation-policy compliance, logical attestation and policy-composition calculi.

### Review
- **FL:** a typed coercion rule plus proof object is mature authorization-logic structure.
- **FME:** strongest baselines must include proof/state/type-aware policy engines rather than only independent local gates.
- **ENT:** scientific-search/local-route facts may be correct inputs yet fail to discharge a target scientific closure obligation; that semantic mismatch is more specific than ordinary permission typing.
- **AGL:** define a valid cross-domain coercion as proving preservation of the **target hard-obligation meaning**, not simply allowing data/judgment flow.
- **SENA:** strike any implication that ORION-18 is the first typed or proof-carrying authorization calculus.

### Disposition
**ADOPT / DO NOT CLAIM:** typed/proof-carrying/stateful authorization and generic policy composition.

**Retain as candidate:** scientific-epistemic obligation-discharge coercion across heterogeneous action domains.

---

## R16 — current stateful agent governance directly pressures ORION-18 stale-epoch novelty

### Pressure
The August 2026 *Stateful Governance for Concurrent Agentic Systems* study makes stale authorization under changing shared policy state a first-class agent-governance problem and proposes policy-state serializability so committed effects are justified against policy state immediately before commit.

### Review
- **FL:** ORION-18 epoch validity/stale-certificate rejection is no longer even plausibly novel in isolation.
- **FME:** add a concurrent/stale-policy baseline and cases where request-time authorization becomes invalid before commit.
- **ENT:** ORION-17 chart/objective transformations can themselves cause the target obligation state to change between request and commit.
- **AGL:** ORION-18 needs commit-time or serializable authority semantics, then must test what *epistemic obligation meaning* adds beyond stateful governance.
- **SENA:** stale authorization is donor-owned; cross-domain scientific obligation transport remains the candidate residual.

### Disposition
**ADOPT:** commit-time state/epoch authorization discipline.

**New falsifier:** if policy-state serializability plus conventional typed obligations reproduces every ORION-18 hostile case, ORION-18 should merge into programme synthesis.

---

## Updated survival statements

### ORION-16
A separate paper must show something beyond dynamic dependency graphs/change propagation: authority- and obligation-sensitive epistemic repair/composition, with history that remains semantically relevant.

### ORION-17
A separate paper must show something beyond representation mapping/preservation: evidence may transport while scientific closure does not, with exact support/obligation semantics across atlas changes.

### ORION-18
A separate paper must show something beyond typed/stateful/proof-carrying authorization: valid source-domain epistemic judgments can fail to discharge target-domain scientific obligations, and explicit obligation-preserving coercions improve composition without total refusal.