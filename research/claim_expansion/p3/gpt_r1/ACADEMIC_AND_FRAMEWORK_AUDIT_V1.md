# P3-U GPT-R1 academic-paper-skills and framework audit

Date: 2026-08-20
Parent: #651
Base: `main@a143d9ece8a86469216d469c457bd03b8fcd9c22`

## Academic-paper-skills scope

This pass uses the same high-rigor contracts as P1/P2: current multi-source literature search, reference verification, three separately frozen reviewer lenses, statistics/independent-unit audit, and whole-manuscript claim/evidence/boundary polishing. No journal-specific prestige criterion is assumed.

## Verified donor frontier

The first P3-U manuscript already cited real 2026 donors. The reference-verifier pass confirms:

- **SciGraph-LLM** is a WSDM Companion 2026 paper, doi:10.1145/3779211.3793169, using constrained provenance-aware extraction from scientific papers.
- **Oarga et al.** `Scientific knowledge graph and ontology generation using open large language models`, Digital Discovery 5 (2026) 1269-1279, doi:10.1039/d5dd00275c.
- **OntoDup** is real and stronger than a generic matching baseline because it makes scholarly entity matching a governed, evidence/provenance/version-aware decision process: Information 17(4):325, doi:10.3390/info17040325.

The current frontier adds important pressure:

1. **Heterogeneity in entity matching: A survey and experimental analysis**, Data & Knowledge Engineering 164 (2026) 102575, doi:10.1016/j.datak.2026.102575, explicitly separates representation and semantic heterogeneity and shows test-time heterogeneity can be particularly damaging.
2. **GenOM**, World Wide Web 29, 29 (2026), doi:10.1007/s11280-026-01413-y, uses LLM-generated definitions plus embedding/lexical retrieval for ontology matching.
3. **HGNet**, ICLR 2026, provides scalable scientific KG generation and cross-domain pressure.
4. **BRINK**, EACL 2026, tests KG-RAG reasoning under incomplete knowledge, warning that downstream QA can look strong when answers are directly retrievable rather than genuinely integrated.
5. Multi-source LLM-assisted KG fusion and GraphRAG systems make entity-level fusion plus downstream reasoning direct donor structure.

Generic KG construction, ontology matching, entity matching, governance/provenance, multi-source fusion, and KG-RAG are therefore donor-owned.

## Reviewer 1 — validity/methods, frozen

**P3-R1-01 — Extraction and identity rule must be causally separable. Blocking: Yes.**
A false merge may originate from extraction, normalization, identity reasoning, or state/interface loss. The study needs coordinate-equalized arms using protected/gold extracted coordinates before attributing error to the identity rule.

**P3-R1-02 — False merge is non-compensatory. Blocking: Yes.**
A high average F1 can hide catastrophic scientific glue. False merge, false split, plurality loss, obstruction miss, and unresolved calibration must be reported separately.

**P3-R1-03 — Ambiguous gold cannot be forced into binary identity. Blocking: Yes.**
Double annotation/adjudication must preserve genuine expert disagreement and allow `Plural/Obstruction/Unresolved` rather than converting every item into same/different.

## Reviewer 2 — prior work/contribution, frozen

**P3-R2-01 — Governance-aware matching is already donor structure. Blocking: Yes for novelty language.**
OntoDup already combines candidate generation, matching, provenance, conflict management, governance state, and materialization. P3-U cannot claim that pairwise identity becomes governed simply because ORION records evidence.

**P3-R2-02 — Semantic heterogeneity is a mature problem family. Blocking: Yes.**
The P3 residual must be scientific identity across construct, measurement, context, stance, temporal, causal-role and responsibility coordinates, not the generic observation that schemas differ.

**P3-R2-03 — Downstream value needs incomplete-knowledge controls. Blocking: Yes for H3.**
BRINK-style controls are needed so downstream QA improvement cannot be explained by direct triple retrieval or answer leakage.

## Reviewer 3 — reproducibility/generalization, frozen

**P3-R3-01 — Independent unit is the scientific item/pair or predeclared cluster. Blocking: Yes.**
Repeated prompts/judges are technical repeats.

**P3-R3-02 — Held-out identity coordinates are mandatory for the broad claim. Blocking: Yes.**
At least one protected domain must require a load-bearing coordinate/mechanic absent from development families. Otherwise H5 is circular.

**P3-R3-03 — Source round-trip must survive promoted integration. Blocking: Yes.**
Every promoted identity relation must remain recoverable to source spans/records; generated ontology or graph labels cannot self-authorize.

## Editor synthesis

The largest P3-U claim survives donor subtraction. The clean residual is not KG extraction or entity matching. It is a **scientific identity responsibility relation** that knows which semantic/measurement/context/provenance coordinates are load-bearing, preserves legitimate plurality/obstruction, detects insufficient state, and improves downstream science under heterogeneous raw evidence.

## Framework consistency

Current code already supplies relevant proposal-level substrate:

- `ScientificMeaningProjection.v1` records source span, predicate, referents, constructs, measurements, temporal context, attribution, discourse relation, polarity, modality and unresolved ambiguity.
- `compare_meaning` conservatively prefers contextual difference or `UNRESOLVED` over false equivalence and distinguishes referent, construct and measurement mismatch.
- `MeasurementRelation.rakl-v1`, `SimilarityWitness.rakl-v1`, `GeneratorTransport.rakl-v1`, and `EpistemicContextCompiler.rakl-v1` provide mapping/transport/representation research substrate.
- P3 has an independent evaluator and public-reference infrastructure in `src/orion/study/`.

Critically, `ScientificMeaningProjection` is documented as proposal-level. Text extraction does not create scientific authority. This matches P3-U.

### Prospective only

- automatic naturalistic acquisition of the right identity coordinates across arbitrary domains;
- learned routing among `Glue/Distinct/Plural/Obstruction/Unresolved` beyond registered coordinates;
- invention of a new identity coordinate/mechanic from failures;
- general scientific identity/integration superiority.

Verdict: `CONSISTENT_AS_PROSPECTIVE_EXTENSION`.

## Negative-to-positive successor — Causal Identity Coordinate Discovery (CICD)

Historical information-equivalent typed-product ties are preserved. They show representation architecture alone cannot win. The successor target is therefore acquisition of the missing identity coordinate under raw heterogeneous evidence.

CICD treats every false merge/split as a set of competing responsibility hypotheses: extraction error, missing construct coordinate, missing measurement coordinate, temporal/context mismatch, stance/provenance mismatch, state insufficiency, or annotation non-identifiability. It selects a discriminator that changes one coordinate while holding the others fixed, and may propose a new coordinate only after registered coordinates and strong donor mappings fail on the frozen case family.

Generic feature discovery/metric learning is donor-owned. The residual is the scientific responsibility and authority relation that determines when a new coordinate is necessary and how prior integration claims must reopen.

## Broad positive terminal

`GENERAL_SCIENTIFIC_IDENTITY_INTEGRATION_SUPERIORITY` requires prospectively:

1. lower false scientific merge against the strongest donor-complete comparator;
2. non-inferior false-split/plurality preservation;
3. downstream synthesis/QA gain under leakage-resistant/incomplete-knowledge controls;
4. held-out domain/schema/source/representation transfer and independent annotation/implementation;
5. at least one failure-derived identity coordinate/mechanic with fresh transfer;
6. source recoverability and external authority preserved.
