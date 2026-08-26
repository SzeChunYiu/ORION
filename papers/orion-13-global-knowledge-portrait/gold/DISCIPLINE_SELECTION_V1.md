# ORION-ORION-13: Real three-discipline gold atlas — discipline selection V1

**Status:** DESIGN_FROZEN (before gold annotation). Part of `ORION-13.cross-domain-atlas.v1`.

**Related:** CORPUS_DESIGN_V1.md, ANNOTATION_SCHEMA_V1.json, Issue #158.

---

## 1. Selection rationale

Three disciplines with materially different terminology, measurement practice, and
evidential conventions are required by the protocol. A fourth discipline (climate)
is retained as a margin extension for follow-up robustness checks.

### Primary criterion

Each selected discipline must:
1. Exhibit a **distinct terminological regime** — different degree of explicit
   ontological commitment, different ratio of formal-mathematical to natural-language
   construct definition.
2. Exhibit a **distinct measurement episteme** — different relationship between
   the construct and its operationalisation, different tolerance for
   measurement pluralism.
3. Be **well-represented in open-access literature** with sufficient paired
   claims for all eight case families.
4. Pose a **unique challenge for cross-domain knowledge integration** that tests
   a different coordinate of the ORION annotation schema.

---

## 2. Discipline 1: Biomedical / life sciences (biomed)

### Why selected

Biomedicine represents the most **ontologically committed** scientific discourse
among the three. The field has mature, centrally maintained ontologies (GO, HPO,
ICD, MeSH, ChEBI) that provide explicit identifier-to-entity mappings. This makes
it the ideal testbed for the `referent_relation` and `mapping_relation` coordinates:
systems that rely on ontology lookup rather than semantic inference can be
cleanly distinguished.

### Unique challenge for cross-domain integration

- **False confidence from ontology coverage.** Because many biomedical entities
  have canonical identifiers, there is a temptation to treat all co-referent spans
  as integrable. However, different publications may operationalise the same
  gene/protein in different assay systems, cell types, or disease contexts.
- **Measurement pluralism hidden behind standardised endpoints.** Standardised
  endpoints (e.g., RECIST, TNM staging) create the appearance of universal
  measurement equivalence, but inter-rater variability and instrument sensitivity
  differences persist.
- **Temporal/state context is critical.** A finding about a biomarker in a
  treatment-naive cohort may not generalise to a relapsed cohort, even though
  the entity name is identical.

### Applicable case families from Issue #100

| Case family | Biomed example | Gold template |
|---|---|---|
| referent ambiguity | "zebrafish" as model organism vs invasive species | referent=DIFFERENT, obstruction |
| synonymy | PD-L1 vs CD274 | referent=SAME, identity mapping |
| operationalisation mismatch | FPG vs HbA1c for glycemic control | construct=SAME, measurement=NON_EQUIVALENT |
| temporal/state context | Pre-treatment vs post-treatment viral load | context=DIFFERENT_STATE_OR_TIME |
| polarity | Drug X reduces mortality (asserted) vs may reduce (hedged) | polarity=SAME, modality=DIFFERENT_STRENGTH |
| modality | RCT vs review citation | modality=DIFFERENT_STRENGTH |
| attribution/stance | Primary result vs secondary citation | attribution=DIFFERENT_ATTRIBUTION |
| valid transforms | NYHA vs ACC/AHA heart failure classification | CONSTRUCT=RELATED_NOT_SAME, conditional transform |
| invalid transforms | Direct numeric comparison of FPG and HbA1c without calibration | measurement=NON_EQUIVALENT |
| literature bridges | Melatonin circadian-clock mechanism -> clinical jet-lag trial | bridge with transfer conditions |
| plural views | H. pylori single-cause vs multifactorial peptic ulcer model | PLURAL_VIEW obstruction |

---

## 3. Discipline 2: Physics / condensed matter (physics)

### Why selected

Physics represents the most **mathematically formalised** scientific discourse.
Constructs are often defined by equations (e.g., band structure, magnetisation,
critical temperature), and the same name can refer to mathematically distinct
objects in different subfields. This tests the `construct_relation` and
`mapping_relation` coordinates at their most demanding.

### Unique challenge for cross-domain integration

- **Same name, different mathematical object.** "Spin" in particle physics
  (intrinsic angular momentum, SU(2) representation) and "spin" in statistical
  mechanics (binary lattice variable, Z_2 state space) share a name but are
  different constructs. A system that relies on surface-form matching will
  make false merges.
- **Unit-system diversity.** Energy may be reported in J, eV, cm^-1, or
  natural units (c=1). The `valid_invalid_representation_mapping` case family
  requires distinguishing between genuine unit conversion (identity with
  known conversion factor) and non-bijective mapping (natural units lose
  dimensionful information).
- **Model-dependent vs measurement-dependent values.** The Hubble tension
  illustrates how the same measured quantity (H0) can yield different values
  depending on the measurement method and the underlying cosmological model.
  This directly tests the `modality_relation` and `attribution_relation`
  coordinates.

### Applicable case families from Issue #100

| Case family | Physics example | Gold template |
|---|---|---|
| referent ambiguity | "spin" as quantum number vs binary lattice variable | referent=DIFFERENT, obstruction |
| synonymy | "gravitational field" vs "metric tensor perturbation h_mu_nu" | referent=SAME, identity mapping |
| operationalisation mismatch | Cepheid distance vs SN Ia distance | construct=SAME, measurement=NON_EQUIVALENT |
| temporal/state context | Solar cycle 24 vs 25 sunspot peak | context=DIFFERENT_STATE_OR_TIME |
| polarity | H0 = 73 (direct) vs H0 = 67.4 (CMB-inferred) | modality=DIFFERENT_STRENGTH |
| modality | Direct measurement vs model-dependent inference | modality=DIFFERENT_STRENGTH |
| attribution/stance | Primary vs secondary analysis of same data | attribution=DIFFERENT_ATTRIBUTION |
| valid transforms | Joules to eV (bijective, known constant) | CONSTRUCT=RELATED_NOT_SAME, conditional transform |
| invalid transforms | Natural units (c=1) to SI without dimension reconstruction | non-bijective mapping |
| literature bridges | Topological band theory -> quantized Hall resistance standard | bridge with idealisation conditions |
| plural views | Copenhagen vs Many-Worlds interpretation | PLURAL_VIEW obstruction |

---

## 4. Discipline 3: Social / behavioural science (social)

### Why selected

Social science represents the most **construct-revisionist** discourse. Unlike
biomedicine (where constructs are constrained by biological mechanism) or physics
(where constructs are constrained by mathematical law), social science constructs
are explicitly debated and revised: "What is intelligence?" "What is well-being?"
"Is social capital a single construct or a family?" This tests the
`construct_relation` coordinate at its most challenging boundary.

### Unique challenge for cross-domain integration

- **Construct validity is itself a research topic.** The same surface term may
  denote different constructs across papers (e.g., "institution" as formal
  constitutional structure vs as informal norms), and different surface terms
  may denote the same construct (e.g., "remittances" vs "transnational money
  flows"). This is the core ORION target.
- **Measurement equivalence is contested.** Survey instruments calibrated on
  one population may not transfer to another. The `measurement_relation`
  coordinate must capture this non-equivalence without defaulting to
  "unresolved."
- **Pluralism is the norm, not the exception.** Competing explanatory models
  (rational choice vs identity-based models of protest participation) coexist
  without being resolved. The `integration_verdict` = PLURAL_VIEW is not a
  failure signal but a scientifically appropriate outcome.

### Applicable case families from Issue #100

| Case family | Social science example | Gold template |
|---|---|---|
| referent ambiguity | "institution" as formal (polysci) vs informal (sociology) | referent=DIFFERENT, obstruction |
| synonymy | "remittances" vs "transnational money flows" | referent=SAME, identity mapping |
| operationalisation mismatch | SWB index vs objective income/consumption for welfare | construct=SAME, measurement=NON_EQUIVALENT |
| temporal/state context | Census 2000 vs 2020 median income | context=DIFFERENT_STATE_OR_TIME |
| polarity | Framing affects donation (causal) vs associated (correlational) | modality=DIFFERENT_STRENGTH |
| modality | Causal claim vs associational claim | modality=DIFFERENT_STRENGTH |
| attribution/stance | Experimental vs correlational evidence | attribution=DIFFERENT_ATTRIBUTION |
| valid transforms | HDI vs MPI composite indices (partial dimension overlap) | CONSTRUCT=RELATED_NOT_SAME, conditional transform |
| invalid transforms | Direct ranking comparison across different composite indices | non-bijective mapping |
| literature bridges | Construal-level theory -> temporal discounting intervention | bridge with context transfer conditions |
| plural views | Rational choice vs identity model of protest | PLURAL_VIEW obstruction |

---

## 5. Margin discipline: Climate / earth science (climate)

Climate science is retained in the existing corpus (8 samples, 8 case families)
but is designated as a **margin discipline** for the primary analysis. The ORION-13
primary analysis uses the three core disciplines (biomed, physics, social);
climate is available for robustness checks, cross-discipline generalisation
tests, and follow-up.

### Why climate is the margin

1. **Multi-scale integration is its own dimension.** Climate science typically
   integrates across spatial scales (global, regional, local) and temporal
   scales (paleoclimate, historical, projection). This cuts across the
   case-family structure in a way that the three core disciplines handle
   more cleanly within families.
2. **Measurement conditional on retrieval/assimilation system.** Climate
   measurements (temperature anomaly, precipitation) are not instrument
   readings but products of reanalysis or retrieval systems. The
   `measurement_relation` coordinate interacts with `context_relation` in a
   way that requires additional annotation complexity.
3. **Plural views are institutionalised.** The IPCC's multi-model ensemble
   approach means that pluralism is not a problem to be resolved but a
   feature of the knowledge production system. This makes the
   `genuine_plural_obstruction` case family especially rich but also means
   that the margin between PLURAL_VIEW and GLUE_ALLOWED is harder to draw.

### Planned use in analysis

The 8 climate samples will be annotated and adjudicated to the same standard,
but the primary hypothesis test (H1: safe integration) is stratified by
discipline. Climate results are reported separately and contribute to the
generality discussion rather than the headline claim.

---

## 6. Case-family coverage across all three disciplines

The following table confirms that every case family from Issue #100 has at least
one representative sample in each of the three core disciplines, plus one in
climate (margin).

| # | Case family | Biomed | Physics | Social | Climate (margin) |
|---|---|---|---|---|---|
| 1 | same_name_different_referent | ORION-13.BIOMED.001 | ORION-13.PHYS.001 | ORION-13.SOCIAL.001 | ORION-13.CLIMATE.001 |
| 2 | different_name_same_referent | ORION-13.BIOMED.002 | ORION-13.PHYS.002 | ORION-13.SOCIAL.002 | ORION-13.CLIMATE.002 |
| 3 | same_construct_different_measurement | ORION-13.BIOMED.003 | ORION-13.PHYS.003 | ORION-13.SOCIAL.003 | ORION-13.CLIMATE.003 |
| 4 | same_entity_different_temporal_state | ORION-13.BIOMED.004 | ORION-13.PHYS.004 | ORION-13.SOCIAL.004 | ORION-13.CLIMATE.004 |
| 5 | polarity_modality_attribution_context | ORION-13.BIOMED.005 | ORION-13.PHYS.005 | ORION-13.SOCIAL.005 | ORION-13.CLIMATE.005 |
| 6 | valid_invalid_representation_mapping | ORION-13.BIOMED.006 | ORION-13.PHYS.006 | ORION-13.SOCIAL.006 | ORION-13.CLIMATE.006 |
| 7 | valid_invalid_literature_bridge | ORION-13.BIOMED.007 | ORION-13.PHYS.007 | ORION-13.SOCIAL.007 | ORION-13.CLIMATE.007 |
| 8 | genuine_plural_obstruction | ORION-13.BIOMED.008 | ORION-13.PHYS.008 | ORION-13.SOCIAL.008 | ORION-13.CLIMATE.008 |

**Total: 24 core samples (3 disciplines x 8 families), plus 8 margin samples (climate) = 32.**

---

## 7. Discipline-wise challenges for each annotation coordinate

| Coordinate | Biomed | Physics | Social |
|---|---|---|---|
| referent_relation | Ontology-backed; false positives from name overlap | Formal definition mismatch common | Construct-level ambiguity; same name, different theorisation |
| construct_relation | Often tractable via GO/HPO/ICD | Equation-level identity checks needed | Requires reading the method section, not just the surface term |
| measurement_relation | Standardised assays mask real non-equivalence | Unit conversion ≠ measurement equivalence | Instrument non-equivalence is recognised and debated |
| context_relation | Population/disease state is primary | Temperature/pressure dependence routine | Population/cultural context is primary |
| modality_relation | RCT vs meta-analysis vs mechanistic study | Direct measurement vs model-dependent inference | Experimental vs correlational vs qualitative |
| attribution_relation | Primary vs secondary citation | Measurement vs model inference | Primary vs secondary data analysis |
| mapping_relation | Ontology-driven identity mapping common | Formal mathematical mapping possible | Partial overlap; dimension weighting required |
| contradiction_verdict | Usually resolvable with temporal/population context | Usually resolvable with measurement context | Often unresolved; competing models coexist |
| integration_verdict | GLUE_ALLOWED common when context is separated | GLUE_ALLOWED with conditional transforms | PLURAL_VIEW is the most frequent appropriate verdict |

---

## 8. Discipline boundaries in the corpus

The 32 samples in the SEED manifest are labelled by discipline, but some
samples could be argued to straddle boundaries (e.g., ORION-13.CLIMATE.005
involves physical reasoning about global warming that touches physics).
The discipline label is assigned based on the **primary source venue** of
the two documents in the pair. This is a pragmatic choice that keeps the
stratification variable clean, even though cross-pollination across
disciplines is a real and interesting phenomenon.

Cross-discipline samples (e.g., biomed + physics) are not included in the
current corpus but are a natural extension for future work, particularly
for the `valid_invalid_literature_bridge` case family where the bridge
crosses a genuine disciplinary boundary.