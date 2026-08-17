# ORION-P3 journal-readiness plan — Global Knowledge Portrait

**Current terminal:** `CANNOT_CHECK` for `PEER_REVIEW_READY` / end-to-end eight-family construct validity.  
**Narrow V1 public-reference mapping route:** `CONFIRMED IN FROZEN NARROW SCOPE` on `origin/main` (PRs #255/#260/#262/#263/#264). This does not close raw-text extraction, recoverability of generated portraits, downstream utility, or the original expert-gold atlas. Adversarial V2 gold is owned by issue #280 and is not claimed here.

**Already present:** typed source projections, representation mappings, scientific meaning and ignorance projections, GLUE/obstruction semantics, local exact semantic worlds and source-recoverability tests.

Checkbox audit (2026-08-17 vs `origin/main`): `evidence/JOURNAL_READINESS_CHECKBOX_AUDIT_2026-08-17.md`. Remaining `CANNOT_CHECK` record: `evidence/CANNOT_CHECK_REMAINING_V1.md`. Manuscript claim map: `CLAIM_LEDGER_MANUSCRIPT_MAP_V1.md`.

## 1. Novelty closure

- [x] Absorb MUSE (arXiv:2608.10974): source-grounded cross-domain structured problem/solution/rationale knowledge is not novel.
- [x] Absorb SciSchema.org (arXiv:2607.27955): multidisciplinary expert scientific-process schemas with measurements/provenance are not novel.
- [x] Absorb SCOPE/SCION schema induction/fusion (arXiv:2607.21610): evidence-linked conservative schema fusion is a direct baseline.
- [x] Absorb Executable Schema Contracts (arXiv:2606.05415): shared schema contracts + provenance-aware multi-source KG/retrieval are not novel.
- [x] Retain SciER (EMNLP 2024) and related scientific IE/discourse as extraction baselines, not novelty.
- [x] Re-search ontology alignment, construct/measurement harmonization, data integration, multimodel/federated KGs, contradiction detection and scientific epistemic pluralism.
- [x] Keep the candidate residual narrow: typed identity/context/construct/measurement hypotheses + explicit obstruction/pluralism + source recoverability + feedback from new representations into W.

## 2. Primary hypotheses

**H1 — safe integration:** ORION reduces false merges/false contradictions relative to flat-schema or direct synthesis baselines while preserving useful integrations.

**H2 — recoverability:** a reader/evaluator can recover the source projection, mapping conditions and non-preserved information behind a global statement.

**H3 — obstruction value:** explicitly retaining incompatible charts improves downstream scientific answering/decision quality compared with forced canonicalization.

**H4 — semantic-coordinate necessity:** removing referent/context/measurement/modality/attribution coordinates causes measurable errors on targeted cases.

- [x] Freeze one primary hypothesis and a practical false-merge safety margin.

## 3. Real gold dataset required

> **Two gold objects must not be conflated.** (1) Public-reference V1/V1.1 jsonl + SHA256SUMS + PROVENANCE.env on `origin/main` is a completed *narrow* mapping freeze from pinned MUSE/SciFact/SciSchema authorities. (2) `gold/adjudicated/P3.*.gold.json` (32 files, annotator `seed-to-gold-v1`) is a schema-valid *seed template*, not expert gold. An LLM/heuristic/simulated label cannot become gold. The 2026-08-16 programme audit's implication that P3 external evaluation had never been run is superseded for route (1) only; see `research/paper-programme-v1/JOURNAL_READINESS_AUDIT_2026-08-16_SUPERSEDE_P3_V1.md`.

A new expert-annotated evaluation set remains the main *end-to-end* publication artifact and is still `CANNOT_CHECK`.

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

- [x] exact source span/document/version;
- [x] referent/entity identity judgment;
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
- [ ] domain-expert review for specialist cases — **CANNOT_CHECK** (no specialist-review artifacts; `GOLD_METHODOLOGY_V1.md` §3.1);
- [ ] at least two independent labels on a substantial shared subset — **CANNOT_CHECK** (annotator-a/b files: 0);
- [ ] report agreement per coordinate, not only one global score — **CANNOT_CHECK** (agreement not computable);
- [x] adjudication policy frozen before test-system outputs are examined;
- [x] data statement, licensing and privacy/IP review.

Existing resources such as MUSE, SciSchema and SciER should be reused where their licenses/tasks match rather than recreating their annotations.

**Remaining (original eight-family expert-gold execution — still `CANNOT_CHECK`):**
- [ ] actual *expert* gold labels for all 32 samples (24 core + 8 margin) — seed-to-gold-v1 templates exist; they are not expert gold
- [ ] independent annotation by two annotators on the 24 core samples — **CANNOT_CHECK**
- [ ] per-coordinate inter-annotator agreement report — **CANNOT_CHECK**
- [ ] adjudication of disagreements — **CANNOT_CHECK** (no independent annotators to disagree)
- [ ] domain-expert review of escalated cases — **CANNOT_CHECK**

**Public-reference V1 gold freeze (verified 2026-08-17 against `origin/main`; not a substitute for the boxes above):**
- [x] portable gold jsonl, 32 lines — SHA-256 `35f9e39b75ff53b7f0ec82cd03ebcaaa82509ee0aea3f5b96aac3fd62c854ed8`
- [x] confirmatory holdout jsonl, 32 lines, zero overlap — SHA-256 `13a76c68c149c2552f3543babeca6e1ad5afe23c45ea9c0dc365c1445cf2782b`
- [x] content-hash freeze in `evidence/public-reference-v1/SHA256SUMS` and `evidence/public-reference-v1.1-confirmatory/SHA256SUMS`
- [x] `PROVENANCE.env` bound for both archives
- [x] 32 schema-valid `gold/adjudicated/P3.*.gold.json` files exist on disk and remain `seed-to-gold-v1` templates (not promoted)

## 4. Baselines and ablations

Baselines:

- [ ] vanilla long-context multi-paper synthesis;
- [ ] standard scientific RAG with citations;
- [ ] cross-domain translation/RAG baseline;
- [x] flat universal-schema / KG canonicalization baseline — **narrow public-reference control only** (flat predicate canonicalization on frozen jsonl; not a full KG system and not the original eight-family study);
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

Covered *public-reference confirmatory* ablations (not a tick of the eight-family study): `force_compatibility_without_obstruction` and `remove_modality_polarity_attribution_discourse` each add +0.1875 false merges on the disjoint holdout; referent/construct/measurement/temporal removals are zero-effect and coverage-limited (`CLAIM_LEDGER_V1.md` P3.C6). Stronger schema/provenance baselines and a coordinate-targeted V2 atlas are issue #280.

## 5. Metrics

- [x] false merge rate — **public-reference mapping layer only** (initial + confirmatory);
- [x] false split rate where same referent/construct should align — **public-reference mapping layer only**;
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

Public-reference *substitutes* (do not close P3-1..P3-7): `evidence/public-reference-v1.1-confirmatory/publication/` PR3-F1..F3 and PR3-T1..T4, regenerated by `make paper03-public-reference-publication`.

## 7. Manuscript work missing

- [x] create canonical full manuscript under `manuscript/`;
- [x] define source projection, scientific meaning projection, representation mapping, GLUE and obstruction formally enough for reimplementation;
- [x] explain why a universal canonical schema is an unsafe default rather than attacking KGs broadly;
- [x] include MUSE/SciSchema/SCOPE-SCION/Executable-Schema-Contracts in related work;
- [x] write dataset/annotation Methods before final labeling;
- [x] add Results only from frozen artifacts;
- [ ] include extraction-vs-mapping-vs-integration stage error attribution — **CANNOT_CHECK** (no end-to-end extractor run);
- [x] add limitations on expert subjectivity, domain coverage, evolving terminology and ontology dependence;
- [x] include data/code availability and ethics/licensing statements.

Claim ledger: `CLAIM_LEDGER_V1.md`. Sentence-to-claim map: `CLAIM_LEDGER_MANUSCRIPT_MAP_V1.md`. Abstract/conclusion still quote the *initial* 32-case numbers; confirmatory authority is `P3.C5`.

## 8. Reproducibility package

- [x] annotation handbook + versioned schemas;
- [ ] document/source IDs and legally shareable source spans or retrieval instructions — **partial**: public-reference stores revision/locator/content hash without vendoring restricted text; eight-family spans remain SEED placeholders;
- [x] adjudicated gold with provenance — **public-reference V1/V1.1 only** (`PUBLIC_REFERENCE_GOLD_V1.jsonl` + `PROVENANCE.env` + `SHA256SUMS`);
- [ ] baseline prompts/configs — **CANNOT_CHECK** for raw-text/RAG/synthesis arms;
- [ ] raw model projections/mappings/portraits — **CANNOT_CHECK**;
- [x] scripts for every *public-reference* metric/plot/table (`make paper03-public-reference-publication`); original P3-1..P3-7 remain ungenerated;
- [x] one-command or short deterministic evaluation path (`make paper03-public-reference`);
- [x] independent replay of headline *public-reference mapping* results (byte-for-byte gold freeze + confirmatory eval workflow). Headline eight-family obstruction results remain **CANNOT_CHECK**.

## Done definition

`ORION-P3 = PEER_REVIEW_READY` only when the real cross-domain gold study validates the claimed integration/recoverability advantage, annotation quality is defensible, strongest structured-integration baselines are included, and all programme readiness gates pass.
