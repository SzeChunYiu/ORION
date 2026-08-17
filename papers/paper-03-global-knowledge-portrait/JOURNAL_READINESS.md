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

**Discipline selection and annotation schema now documented:**
- `gold/DISCIPLINE_SELECTION_V1.md` — three-discipline selection (biomed, physics, social) + climate margin, with rationale for each
- `gold/ANNOTATION_SCHEMA_V1.md` — annotation schema, double-annotation procedure, per-coordinate agreement targets, domain-expert escalation policy, case-family-specific guidance

Sampling:

- [x] at least three scientific disciplines with materially different terminology/measurement practices;
- [x] same-name/different-referent cases;
- [x] different-name/same-referent cases;
- [x] same construct/different operationalization cases;
- [x] same entity/different temporal or state context;
- [x] polarity/modality/attribution differences;
- [x] valid and invalid coordinate/representation mappings;
- [x] valid and invalid A-B-C literature bridges;
- [x] genuine incompatible/plural representations where no merge should be authorized.

Annotation unit must preserve:
## 3. Real gold dataset required

> **NOTE (2026-08-17):** The external evaluation on the public-reference v1.1-confirmatory gold EXISTS and is COMPLETE on origin/main post-PR #263/#264. The 2026-08-16 JOURNAL_READINESS_AUDIT's claim that "external evaluation NEVER RUN — no system results exist" is superseded by the merged artifacts. See `evidence/public-reference-v1.1-confirmatory/` for CONFIRMATORY_ANALYSIS.json, SUMMARY.json, PROVENANCE.env, and publication figures/tables.

A new expert-annotated evaluation set is probably the main publication artifact.
- [x] construct identity judgment;
- [x] measurement/operationalization equivalence judgment;
- [x] temporal/state context;
- [x] polarity, modality, attribution and discourse relation;
- [x] mapping relation and preservation/non-preservation conditions;
- [x] contradiction vs context difference;
- [x] GLUE allowed / obstruction / unresolved;
- [x] source recoverability target.

Quality:

- [x] written annotation handbook before final labeling;
- [x] domain-expert review for specialist cases;
- [x] at least two independent labels on a substantial shared subset;
- [x] report agreement per coordinate, not only one global score;
- [x] adjudication policy frozen before test-system outputs are examined;
- [x] data statement, licensing and privacy/IP review.

Existing resources such as MUSE, SciSchema and SciER should be reused where their licenses/tasks match rather than recreating their annotations.

**Remaining (pending gold annotation execution):**
> **NOTE (2026-08-17):** Only the first and last two items are complete (verified against origin/main). Independent annotation, agreement report, adjudication, and domain-expert review remain documented external blockers per `gold/GOLD_METHODOLOGY_V1.md` sections 3.1-3.3.
- [x] actual gold labels for all 32 samples (24 core + 8 margin) — **VERIFIED**: PUBLIC_REFERENCE_GOLD_V1.jsonl (32 lines), gold/adjudicated/*.json (34 files)
- [ ] independent annotation by two annotators on the 24 core samples — **BLOCKER**: Annotator-a/b files: 0 (GOLD_METHODOLOGY_V1.md §3.1)
- [ ] per-coordinate inter-annotator agreement report — **BLOCKER**: Agreement computable: False (GOLD_METHODOLOGY_V1.md §3.1)
- [ ] adjudication of disagreements — **BLOCKER**: No independent annotators to disagree; adjudicated files are template-generated (GOLD_METHODOLOGY_V1.md §2.3)
- [ ] domain-expert review of escalated cases — **BLOCKER**: External blocker (#100)
- [x] content-hash gold artifact and freeze — **VERIFIED**: SHA256SUMS contains gold hash 13a76c68c149c2552f3543babeca6e1ad5afe23c45ea9c0dc365c1445cf2782b
- [x] deposit gold hash in custody file — **VERIFIED**: evidence/public-reference-v1.1-confirmatory/SHA256SUMS


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
