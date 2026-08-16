# Paper III research object — Global Knowledge Portrait

## Candidate claim after nearest-work challenge

ORION is not novel merely because it retrieves across domains, builds a knowledge graph, or summarizes multiple papers.  The scoped candidate is:

> A provenance-preserving **atlas of source projections** in which referents, context, measurement/operationalization and representation mappings are explicit; compatible views may GLUE, incompatible views remain typed obstructions/plural charts, and the reconstructed global portrait must retain enough lineage to recover the contributing source views rather than flattening them into one universal summary.

## Atoms

1. scientific-language interpretation;
2. entity/event/referent identity;
3. context and observation coordinates;
4. measurement/operationalization identity;
5. source projection construction;
6. representation mapping/equivalence;
7. contradiction versus context difference;
8. literature bridge / implicit connection discovery;
9. GLUE / obstruction / pluralism;
10. global portrait reconstruction and source recoverability.

## Nearest work and mechanisms absorbed

### OpenScholar — arXiv:2411.14199
Mechanisms: scientific retrieval over a very large corpus, passage selection, citation-backed long-form synthesis, self-feedback.

**Absorb:** strong retrieval/synthesis baseline; evidence-backed passages; expert-query evaluation.

**Not a surviving novelty:** literature synthesis with citations.

### BioSage — arXiv:2511.18298
Mechanisms: cross-disciplinary retrieval, translation agents aligning specialized terminology/methods, reasoning agents, citation-backed synthesis.

**Absorb:** explicit cross-domain translation stage; user-facing traceability; agent specialization for terminology/method translation.

**Residual:** translation should produce typed mapping hypotheses with preservation/non-preservation conditions, not silently normalize terms.

### Discovery Engine — arXiv:2505.17500
Mechanisms: papers distilled into structured knowledge artifacts under a universal schema, encoded in a conceptual tensor and unrolled into graph/vector views for navigation/gap discovery.

**Absorb:** structured knowledge artifacts; multiple computational views; graph-native gap/navigation operations.

**Challenge:** a universal schema/tensor may encourage premature flattening. ORION should preserve local charts and typed obstructions when mappings are not justified.

### LLMatch / schema matching — arXiv:2507.10897 and related data-integration work
Mechanisms: schema preparation, candidate selection, fine-grained alignment, rollup/drilldown, explicit benchmarked mapping.

**Absorb:** staged mapping rather than one-shot similarity; higher-order conceptual rollup followed by fine-grained drilldown; mapping should be independently evaluated.

### Scientific information extraction / discourse
SciER (EMNLP 2024) and scientific discourse work demonstrate that full-text scientific meaning cannot be reduced to abstract-level entity/relation extraction.  Context, discourse relation, scope and attribution matter for evidential interpretation.

**Absorb:** scientific entity/relation extraction as a projection layer; retain source spans, discourse/context and unresolved interpretation; do not let extraction create authority.

### Literature-based discovery — Swanson 1986/1987 lineage
Mechanism: complementary but bibliographically disconnected literatures can expose an implicit A–B–C hypothesis not stated in either literature alone.

**Absorb:** literature-bridge route as a first-class search operation; require relation/context compatibility before composing A–B and B–C.

**Not a surviving novelty:** discovering implicit cross-literature links.

### Provenance graphs / procedure representations
MatPROV and related provenance-KG work show the value of representing processes/conditions as graph structure rather than flat fields.

**Absorb:** source/transformation/procedure lineage as a graph-capable projection; preserve conditions and causal/process order.

## ORION mechanics already present

Current main includes `AssimilationOutcome`, typed referent bindings, source projections, representation mappings, compatibility verdicts, residual generation for unresolved referents/mappings, K/W update effects, and portrait reconstruction with source/mapping lineage.

## Surviving candidate deltas

- `P3.D1.PROJECTION_ATLAS`: source-local representations remain addressable projections rather than being overwritten by a canonical summary.
- `P3.D2.TYPED_IDENTITY_CONTEXT_MEASUREMENT`: entity sameness, construct sameness, operationalization sameness, temporal/state sameness and measurement equivalence are distinct hypotheses.
- `P3.D3.GLUE_OR_OBSTRUCTION`: global synthesis is conditional on licensed mappings; failed compatibility becomes an informative obstruction/plural portrait rather than forced integration.
- `P3.D4.RECOVERABLE_GLOBAL_PORTRAIT`: a global portrait should expose how each source claim/view projects into it and what was not preserved.
- `P3.D5.ABSORPTION_CHANGES_W`: a newly absorbed concept/representation can expand the model of what domains/search routes are relevant, causing another research round.

## Falsifiers / benchmarks

### Synthetic atlas worlds
Create exact source charts with controlled:
- same name / different entity;
- different name / same entity;
- same construct / different measurement;
- same entity / different temporal state;
- negation/modality/attribution changes;
- compatible and incompatible coordinate transforms;
- A–B + B–C bridges that are valid or invalid because B changes meaning.

Metrics:
- false merge rate;
- false contradiction rate;
- missed contradiction rate;
- mapping precision/recall;
- source-projection recoverability;
- obstruction detection;
- downstream answer correctness after global reconstruction.

### Real cross-domain cases
Freeze cases requiring at least three disciplines and multiple operationalizations of the same apparent construct. Compare:
- vanilla long-context synthesis;
- OpenScholar/BioSage-like RAG/translation;
- flat knowledge graph/universal-schema representation;
- ORION atlas/gluing.

### NLP ablation
Remove discourse/coreference/modality/measurement coordinates. If performance does not degrade on targeted cases, the richer projection layer is unjustified.

## Paper claim boundary

Paper III must not claim:
- first cross-disciplinary RAG;
- first scientific knowledge graph;
- first schema matching system;
- first literature-based discovery system;
- first provenance graph.

It may test whether a **typed, projection-preserving atlas with explicit obstruction and recoverability** avoids false integration while still enabling useful global synthesis and new-search-space discovery.
