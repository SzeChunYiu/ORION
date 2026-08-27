# ORION-13 nearest-work dispositions V1 — journal-readiness audit

**Status:** COMPREHENSIVE, covering all 13 mechanism families requested in issue #100.  
**Supersedes:** `NEAREST_WORK_ATLAS.md` Paper III rows, `NEAREST_WORK_SUPPLEMENT_2026-08-16.md` Paper III section.  
**Rule:** Absorption is not a threat. Every absorbed mechanism shrinks the novelty boundary. The surviving residual is the smallest set of distinctions that prior work does not collectively address.

---

## Core: the surviving residual

After absorbing all 13 mechanism families, the residual is:

| ID | Residual | Not claimed |
|---|---|---|
| D1 | Source-local projections remain addressable, not overwritten by a canonical summary | ⨯ structured knowledge artifacts (MUSE, Discovery Engine) |
| D2 | Referent, construct, measurement/operationalization, temporal/state context, and representation are **distinct typed hypotheses** | ⨯ schema matching, ontology alignment, entity resolution |
| D3 | GLUE is conditional on licensed mappings; failed compatibility produces typed obstruction/plural portraits, not forced integration | ⨯ schema fusion, KG canonicalization, federated KGs |
| D4 | A global portrait must expose how each source claim projects into it and what was not preserved (recoverability) | ⨯ provenance graphs, scientific IE |
| D5 | Absorbing a new representation expands the relevance/search-universe model, reopening research (W effect) | ⨯ literature-based discovery |

---

## Per-mechanism dispositions

### 1. MUSE — arXiv:2608.10974

| Field | Value |
|---|---|
| **Disposition** | `ADAPT` |
| **Mechanism** | Full-text source-grounded problem-solution-rationale knowledge base across domains |
| **Removed from novelty** | Source-grounded cross-domain structured knowledge extraction is not novel. Any claim to "structured knowledge from scientific text" is absorbed. |
| **Surviving residual** | MUSE does not distinguish referent vs construct vs measurement vs context as separate typed hypotheses; it produces a single problem/solution/rationale structure. ORION's D2 (typed coordinate distinctions) survives. MUSE does not represent obstruction, plural views, or recoverability. |
| **Reference pinned** | `cohentsofia/MUSE@f7a40317db46145d0c90b221311d8324db5da1b9` |

### 2. SciSchema.org — arXiv:2607.27955

| Field | Value |
|---|---|
| **Disposition** | `ADAPT` |
| **Mechanism** | Expert multidisciplinary scientific-process schemas with parameters, measurements, and provenance |
| **Removed from novelty** | Multidisciplinary expert scientific-process schemas, explicit measurement/provenance representation, and domain-specific schema design are not novel. |
| **Surviving residual** | SciSchema.org provides expert-designed *static* schemas per discipline. ORION's D1 (projection atlas) proposes that schemas are *source-local, composable, and obstruable* — they are not fixed per discipline but assembled per research question from source projections. D4 (recoverability) requires that the path from source to schema is traceable, which expert-designed schemas do not guarantee. |

### 3. SCOPE/SCION — arXiv:2607.21610

| Field | Value |
|---|---|
| **Disposition** | `COMPOSE` as a direct baseline; `ADAPT` for schema induction mechanism |
| **Mechanism** | Evidence-linked conservative schema induction and fusion across scientific papers |
| **Removed from novelty** | Schema induction from evidence, conservative schema fusion, and evidence-linked integration are not novel. |
| **Surviving residual** | SCOPE/SCION fuses schemas to produce a single integrated schema. ORION's D3 (GLUE-or-obstruction) permits fusion only when all coordinates are compatible; otherwise it preserves obstruction/plural portraits — a contingent GLUE, not a forced fusion. SCOPE/SCION does not represent measurement/operationalization equivalence as a separate coordinate or track what was not preserved. |

### 4. Executable Schema Contracts — arXiv:2606.05415

| Field | Value |
|---|---|
| **Disposition** | `COMPOSE` as a baseline; `ADAPT` for provenance-aware integration |
| **Mechanism** | Provenance-aware shared-schema integration across multiple sources, with retrieval and contract-based composition |
| **Removed from novelty** | Provenance-aware multi-source knowledge integration, shared schema contracts, and retrieval under schema constraints are not novel. |
| **Surviving residual** | Executable Schema Contracts assume a shared schema exists or can be derived. ORION's D3 allows the case where *no* shared schema is justified — obstruction/plural views are the correct output. D4 (recoverability) extends beyond provenance tracking to include *non-preserved coordinates*: what was lost in the mapping. |

### 5. SciER / scientific IE / discourse / coreference / modality — EMNLP 2024

| Field | Value |
|---|---|
| **Disposition** | `ADAPT` |
| **Mechanism** | Full-text scientific entity/relation extraction, discourse parsing, coreference resolution, modality detection |
| **Removed from novelty** | Scientific information extraction, entity/relation recognition, discourse parsing, coreference, and modality detection are not novel. |
| **Surviving residual** | SciER extracts entities and relations into a flat or hierarchy-structured form. ORION's ScientificMeaningProjection.v1 preserves each coordinate as a *typed hypothesis* that participates in mapping/GLUE/obstruction decisions — not just extracted relations but explicit mapping conditions. The extraction itself is a baseline; the *participation of typed coordinates in a GLUE-or-obstruction decision* is the residual. |

### 6. Ontology/schema alignment

| Field | Value |
|---|---|
| **Disposition** | `COMPOSE` as a baseline; `ADAPT` for alignment mechanism |
| **Mechanism** | Ontology matching, schema alignment, instance- and element-level correspondence discovery |
| **Removed from novelty** | Finding correspondences between schemas or ontologies is not novel. Any claim to "alignment" or "mapping" is absorbed. |
| **Surviving residual** | Ontology alignment typically produces a single equivalence or subsumption relation. ORION's D2 distinguishes *referent*, *construct*, *measurement*, *context* as separate alignment axes — two schemas may align at the construct level but differ at the measurement level. Alignment methods do not produce preservation/non-preservation conditions (D4) or obstruction verdicts (D3). |

### 7. Measurement harmonization / construct validity / psychometrics / metrology

| Field | Value |
|---|---|
| **Disposition** | `ADAPT` |
| **Mechanism** | Measurement equivalence testing, construct validity frameworks, psychometric invariance, metrological traceability |
| **Removed from novelty** | The concept of measurement equivalence, construct validity, or operationalization differences is not novel. Psychometrics and metrology have studied these for decades. |
| **Surviving residual** | Measurement science has established that constructs and operationalizations are distinct. ORION's contribution is not discovering this fact but *representing it as a first-class typed coordinate in an automated integration pipeline* — and making the GLUE-or-obstruction decision depend on it. The measurement-equivalence literature does not provide a generic computational representation that plugs into a scientific-knowledge integration system. |

### 8. Data integration / entity resolution / record linkage

| Field | Value |
|---|---|
| **Disposition** | `COMPOSE` |
| **Mechanism** | Schema matching, entity resolution, record linkage, data fusion, blocking and matching |
| **Removed from novelty** | Matching records, resolving entities, integrating data sources, and fusing data are not novel. |
| **Surviving residual** | Data integration assumes a shared referent/entity and produces a fused record. ORION's D3 admits cases where the correct output is *not* a fused record — obstruction/plural views. D2 distinguishes cases where the referent is the same but the construct, measurement, or context differs, which data integration treats as a single alignment score. D5 (W effect) applies when an absorbed representation changes search relevance, which data integration does not address. |

### 9. Contradiction and stance/context detection

| Field | Value |
|---|---|
| **Disposition** | `ADAPT` |
| **Mechanism** | Contradiction detection, stance detection, context-aware claim comparison, fact-checking |
| **Removed from novelty** | Detecting contradiction, stance, or context differences between statements is not novel. |
| **Surviving residual** | Contradiction detection typically labels a binary "contradiction/not contradiction." ORION distinguishes contradiction from *context difference*, *modality difference*, *measurement difference*, and *attribution difference* — each of which would produce a "contradiction" label in a standard system. The distinction matters because only true contradiction (after aligning all coordinates) should trigger a revision; context/modality differences are informative obstructions, not contradictions. |

### 10. Multimodel/federated knowledge graphs

| Field | Value |
|---|---|
| **Disposition** | `COMPOSE` |
| **Mechanism** | Multiple knowledge graphs combined under a federation layer, mapping alignments at the KG level |
| **Removed from novelty** | Federating multiple KGs, aligning entities across graphs, and querying a multi-KG federation are not novel. |
| **Surviving residual** | Federated KGs assume each KG is a canonical representation of its domain. ORION's D1 treats each source as a *local projection*, not a canonical KG. D3 allows obstruction when source projections cannot be aligned — federated KGs either find a mapping or return no result. D4 (recoverability) tracks what is lost in the mapping, which federated KGs do not report. |

### 11. Literature-based discovery (Swanson lineage)

| Field | Value |
|---|---|
| **Disposition** | `ADAPT` |
| **Mechanism** | A-B-C bridging: finding implicit connections between literatures that do not cite each other |
| **Removed from novelty** | A-B-C literature-based discovery is not novel. |
| **Surviving residual** | LBD discovers the bridge but does not check whether the *meaning* of B changes across the A-B and B-C compositions. ORION's D2 and D3 require that the referent, construct, measurement, and context of B are compatible across both halves of the bridge before accepting the composition. If B changes meaning, the bridge is an obstruction, not a discovery. |

### 12. Scientific pluralism / model plurality / incompatible representations

| Field | Value |
|---|---|
| **Disposition** | `ADAPT` |
| **Mechanism** | Philosophy of science literature on scientific pluralism, model plurality, and incompatible-but-valid scientific representations (e.g., Kellert, Longino, Cartwright, Suppes, Chang) |
| **Removed from novelty** | The observation that multiple incompatible scientific representations can each be valid, and that forced unification is harmful, is not novel. The scientific pluralism literature has argued this for decades. |
| **Surviving residual** | The pluralism literature diagnoses the problem but does not provide a *computational representation* for obstruction, plural portraits, or GLUE-with-preservation-conditions. ORION's D3 is not claiming discovery of pluralism — it is claiming that an automated integration system can *represent* pluralism as a first-class output (OBSTRUCTION/PLURAL_VIEW) rather than being forced to produce a single unified answer. The computational implementation of the pluralism principle is the residual. |

### 13. Current 2026+ scientific foundation-model knowledge-representation work

| Field | Value |
|---|---|
| **Disposition** | `COMPOSE` |
| **Mechanism** | Foundation-model-based scientific knowledge representation: LLM-based structured extraction, in-context integration, retrieval-augmented synthesis, prompt-based schema alignment |
| **Removed from novelty** | Using LLMs for structured extraction, scientific synthesis, knowledge integration, or schema alignment is not novel. |
| **Surviving residual** | Current FM-based approaches typically use a single prompt or schema to extract/integrate, implicitly flattening source projections into a canonical representation. ORION's D1-D5 propose explicit typed coordinates, GLUE-or-obstruction decisions, and recoverability as *architectural invariants* rather than prompt engineering decisions. The question is whether these invariants measurably reduce false integration compared to FM-based flat integration. This is the empirical question the gold study must answer. |

---

## Updated novelty boundary

### What is explicitly NOT claimed

- Cross-domain RAG (OpenScholar, BioSage)
- Scientific knowledge graphs (Discovery Engine, federated KGs)
- Schema matching/alignment (LLMatch, ontology alignment)
- Schema induction/fusion (SCOPE/SCION)
- Source-grounded structured extraction (MUSE)
- Scientific IE/discourse parsing (SciER)
- Provenance graphs (MatPROV, Executable Schema Contracts)
- Literature-based discovery (Swanson lineage)
- Measurement-equivalence awareness (psychometrics/metrology)
- Contradiction/stance detection
- Entity resolution/record linkage (data integration)
- Scientific pluralism diagnosis
- LLM-based structured knowledge representation

### What IS the surviving claim

| # | Claim | Prior work does not |
|---|---|---|
| 1 | **Typed coordinate distinctions** — referent, construct, measurement, context, modality, attribution are separate typed hypotheses in an integration pipeline | Treat all six as distinct hypotheses that each independently gate GLUE |
| 2 | **GLUE-or-obstruction** — integration is conditional on all coordinates aligning; failed alignment produces a typed obstruction, not forced integration | Allow obstruction as a first-class integration output rather than "no mapping" |
| 3 | **Recoverability** — a global portrait exposes source projections, mapping conditions, and non-preserved coordinates | Track what was lost during mapping, not just what was preserved |
| 4 | **W effect** — absorbing a new representation expands the relevance/search universe, reopening research | Represent the feedback loop from representation change to search-space change |

---

## Implications for the manuscript and evaluation

1. The manuscript's **Related Work** section must treat all 13 mechanisms as absorbed, not as competitors. The comparison is not "ORION vs Schema Matching" but "ORION with typed coordinates + obstruction + recoverability vs ORION without them" (ablations) and "ORION vs best flat integration" (baselines).

2. The **evaluation** must measure the marginal contribution of D1-D5 against the strongest flat baseline, not against a straw-man. The gold study comparison is:
   - Full ORION (D1-D5) vs strongest flat baseline
   - Full ORION vs each ablation (remove D2, remove D3, remove D4, remove D5)
   - The marginal benefit of typed coordinates over flat alignment

3. The **significance test** is whether typed coordinates + obstruction + recoverability + W effect produce a measurable reduction in false integration at acceptable valid-integration cost. This is the predeclared H1 in the protocol.

---

## References

- MUSE: arXiv:2608.10974
- SciSchema.org: arXiv:2607.27955
- SCOPE/SCION: arXiv:2607.21610
- Executable Schema Contracts: arXiv:2606.05415
- SciER: EMNLP 2024; scientific discourse and IE
- LLMatch: arXiv:2507.10897 (schema matching baseline)
- Discovery Engine: arXiv:2505.17500 (structured knowledge artifacts)
- BioSage: arXiv:2511.18298 (cross-domain translation)
- OpenScholar: arXiv:2411.14199 (scientific RAG)
- ADIAS: arXiv:2608.06410 (issue-centric self-improvement)
- NEAREST_WORK_ATLAS.md: `research/paper-programme-v1/NEAREST_WORK_ATLAS.md`
- NEAREST_WORK_SUPPLEMENT: `research/paper-programme-v1/NEAREST_WORK_SUPPLEMENT_2026-08-16.md`