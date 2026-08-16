# ORION-P3 journal-readiness plan — Global Knowledge Portrait

**Current terminal:** `CANNOT_CHECK` for real cross-domain semantic/integration adequacy / not peer-review ready.  
**Already present:** typed source projections, representation mappings, scientific meaning and ignorance projections, GLUE/obstruction semantics, local exact semantic worlds and source-recoverability tests.

## 1. Novelty closure

- [ ] Absorb MUSE (arXiv:2608.10974): source-grounded cross-domain structured problem/solution/rationale knowledge is not novel.
- [ ] Absorb SciSchema.org (arXiv:2607.27955): multidisciplinary expert scientific-process schemas with measurements/provenance are not novel.
- [ ] Absorb SCOPE/SCION schema induction/fusion (arXiv:2607.21610): evidence-linked conservative schema fusion is a direct baseline.
- [ ] Absorb Executable Schema Contracts (arXiv:2606.05415): shared schema contracts + provenance-aware multi-source KG/retrieval are not novel.
- [ ] Retain SciER (EMNLP 2024) and related scientific IE/discourse as extraction baselines, not novelty.
- [ ] Re-search ontology alignment, construct/measurement harmonization, data integration, multimodel/federated KGs, contradiction detection and scientific epistemic pluralism.
- [ ] Keep the candidate residual narrow: typed identity/context/construct/measurement hypotheses + explicit obstruction/pluralism + source recoverability + feedback from new representations into W.

## 2. Primary hypotheses

**H1 — safe integration:** ORION reduces false merges/false contradictions relative to flat-schema or direct synthesis baselines while preserving useful integrations.

**H2 — recoverability:** a reader/evaluator can recover the source projection, mapping conditions and non-preserved information behind a global statement.

**H3 — obstruction value:** explicitly retaining incompatible charts improves downstream scientific answering/decision quality compared with forced canonicalization.

**H4 — semantic-coordinate necessity:** removing referent/context/measurement/modality/attribution coordinates causes measurable errors on targeted cases.

- [ ] Freeze one primary hypothesis and a practical false-merge safety margin.

## 3. Real gold dataset required

A new expert-annotated evaluation set is probably the main publication artifact.

Sampling:

- [ ] at least three scientific disciplines with materially different terminology/measurement practices;
- [ ] same-name/different-referent cases;
- [ ] different-name/same-referent cases;
- [ ] same construct/different operationalization cases;
- [ ] same entity/different temporal or state context;
- [ ] polarity/modality/attribution differences;
- [ ] valid and invalid coordinate/representation mappings;
- [ ] valid and invalid A-B-C literature bridges;
- [ ] genuine incompatible/plural representations where no merge should be authorized.

Annotation unit must preserve:

- [ ] exact source span/document/version;
- [ ] referent/entity identity judgment;
- [ ] construct identity judgment;
- [ ] measurement/operationalization equivalence judgment;
- [ ] temporal/state context;
- [ ] polarity, modality, attribution and discourse relation;
- [ ] mapping relation and preservation/non-preservation conditions;
- [ ] contradiction vs context difference;
- [ ] GLUE allowed / obstruction / unresolved;
- [ ] source recoverability target.

Quality:

- [ ] written annotation handbook before final labeling;
- [ ] domain-expert review for specialist cases;
- [ ] at least two independent labels on a substantial shared subset;
- [ ] report agreement per coordinate, not only one global score;
- [ ] adjudication policy frozen before test-system outputs are examined;
- [ ] data statement, licensing and privacy/IP review.

Existing resources such as MUSE, SciSchema and SciER should be reused where their licenses/tasks match rather than recreating their annotations.

## 4. Baselines and ablations

Baselines:

- [ ] vanilla long-context multi-paper synthesis;
- [ ] standard scientific RAG with citations;
- [ ] cross-domain translation/RAG baseline;
- [ ] flat universal-schema / KG canonicalization baseline;
- [ ] SCOPE/SCION-like schema-fusion baseline where compatible;
- [ ] provenance-aware schema-contract/KG baseline where compatible.

Ablations:

- [ ] remove referent identity coordinate;
- [ ] remove measurement/operationalization coordinate;
- [ ] remove temporal/context coordinate;
- [ ] remove modality/polarity/attribution/discourse coordinates;
- [ ] remove explicit obstruction state and force best mapping;
- [ ] remove source-projection recoverability requirement;
- [ ] remove W-expansion/reopen effect;
- [ ] resource-match all systems.

## 5. Metrics

- [ ] false merge rate;
- [ ] false split rate where same referent/construct should align;
- [ ] false contradiction and missed contradiction rates;
- [ ] mapping precision/recall/F1 by mapping type;
- [ ] measurement-equivalence accuracy;
- [ ] obstruction precision/recall;
- [ ] source-projection recoverability rate;
- [ ] preservation-condition accuracy;
- [ ] literature-bridge validity precision/recall;
- [ ] downstream answer correctness using the reconstructed portrait;
- [ ] calibration/abstention quality for unresolved mappings;
- [ ] annotation agreement per coordinate;
- [ ] cost/latency/storage overhead.

## 6. Required plots

- [ ] **Figure P3-1:** projection → mapping → GLUE/obstruction → portrait pipeline with provenance paths.
- [ ] **Figure P3-2:** false-merge vs useful-integration frontier across systems.
- [ ] **Figure P3-3:** mapping/identity confusion matrix by case family.
- [ ] **Figure P3-4:** source recoverability distribution or rate by discipline/system.
- [ ] **Figure P3-5:** obstruction detection precision/recall by incompatibility type.
- [ ] **Figure P3-6:** ablation effect sizes for referent, measurement, context, modality/discourse and obstruction coordinates.
- [ ] **Figure P3-7:** downstream answer accuracy before/after portrait reconstruction by baseline.
- [ ] **Table P3-1:** dataset composition and annotation agreement.
- [ ] **Table P3-2:** main baseline/ablation results with intervals.
- [ ] **Table P3-3:** representative false-merge/false-contradiction/obstruction cases with source lineage.

## 7. Manuscript work missing

- [ ] create canonical full manuscript under `manuscript/`;
- [ ] define source projection, scientific meaning projection, representation mapping, GLUE and obstruction formally enough for reimplementation;
- [ ] explain why a universal canonical schema is an unsafe default rather than attacking KGs broadly;
- [ ] include MUSE/SciSchema/SCOPE-SCION/Executable-Schema-Contracts in related work;
- [ ] write dataset/annotation Methods before final labeling;
- [ ] add Results only from frozen artifacts;
- [ ] include extraction-vs-mapping-vs-integration stage error attribution;
- [ ] add limitations on expert subjectivity, domain coverage, evolving terminology and ontology dependence;
- [ ] include data/code availability and ethics/licensing statements.

## 8. Reproducibility package

- [ ] annotation handbook + versioned schemas;
- [ ] document/source IDs and legally shareable source spans or retrieval instructions;
- [ ] adjudicated gold with provenance;
- [ ] baseline prompts/configs;
- [ ] raw model projections/mappings/portraits;
- [ ] scripts for every metric/plot/table;
- [ ] one-command or short deterministic evaluation path;
- [ ] independent replay of headline mapping/obstruction results.

## Done definition

`ORION-P3 = PEER_REVIEW_READY` only when the real cross-domain gold study validates the claimed integration/recoverability advantage, annotation quality is defensible, strongest structured-integration baselines are included, and all programme readiness gates pass.
