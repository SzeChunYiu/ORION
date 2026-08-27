# ORION-13: Annotation schema and handbook V1

**Status:** DESIGN_FROZEN (before gold annotation). Part of `ORION-13.cross-domain-atlas.v1`.

**Related:** ANNOTATION_SCHEMA_V1.json (machine-readable schema), ANNOTATION_HANDBOOK_V1.md (annotator reference), ADJUDICATION_POLICY_V1.md, DISCIPLINE_SELECTION_V1.md, Issue #158.

---

## 1. Overview

The gold object is a structured annotation over 11 coordinates for each source-pair
case. The annotation schema, handbook, and adjudication policy are frozen before
any gold labels are produced and before any evaluated system outputs are inspected.
This document specifies the annotation procedure, the shared double-annotation
design, the agreement targets, and the domain-expert escalation triggers.

### Schema version

`orion.p3.annotation.v1` (defined in `ANNOTATION_SCHEMA_V1.json`)

### Handbook version

`ANNOTATION_HANDBOOK_V1.md` (frozen before final labelling)

### Adjudication policy version

`ADJUDICATION_POLICY_V1.md` (frozen before final labelling)

---

## 2. Annotation coordinates

All 11 coordinates are annotated in the fixed order specified in the handbook.
The schema defines the permitted values for each coordinate.

| # | Coordinate | Values | When NOT_APPLICABLE |
|---|---|---|---|
| 1 | referent_relation | SAME, DIFFERENT, PARTIAL_OVERLAP, UNRESOLVED | Always applicable |
| 2 | construct_relation | SAME, RELATED_NOT_SAME, DIFFERENT, UNRESOLVED | Always applicable |
| 3 | measurement_relation | EQUIVALENT, TRANSFORMABLE_WITH_CONDITIONS, NON_EQUIVALENT, NOT_APPLICABLE, UNRESOLVED | When constructs are DIFFERENT or referents are DIFFERENT |
| 4 | context_relation | ALIGNED, CONDITIONED_COMPATIBLE, DIFFERENT_STATE_OR_TIME, INCOMPATIBLE, UNRESOLVED | Always applicable |
| 5 | polarity_relation | SAME, OPPOSITE, NOT_COMPARABLE, UNRESOLVED | When referents or constructs are DIFFERENT |
| 6 | modality_relation | SAME, DIFFERENT_STRENGTH, NOT_COMPARABLE, UNRESOLVED | When referents or constructs are DIFFERENT |
| 7 | attribution_relation | SAME_SPEAKER_OR_SOURCE, DIFFERENT_ATTRIBUTION, NOT_APPLICABLE, UNRESOLVED | When referents or constructs are DIFFERENT |
| 8 | discourse_relation | ALIGNED, CONTEXTUAL_DIFFERENCE, NOT_COMPARABLE, UNRESOLVED | When referents or constructs are DIFFERENT |
| 9 | mapping_relation | IDENTITY, EQUIVALENCE, CONDITIONAL_TRANSFORM, SUBSUMPTION, ASSOCIATION_ONLY, NO_LICENSED_MAPPING, UNRESOLVED | Always applicable |
| 10 | contradiction_verdict | CONTRADICTION, NO_CONTRADICTION, CONTEXT_DEPENDENT, UNRESOLVED | Always applicable |
| 11 | integration_verdict | GLUE_ALLOWED, OBSTRUCTION, PLURAL_VIEW, UNRESOLVED | Always applicable |

### Additional fields per annotation

- `preservation_conditions`: list of strings describing what must hold for the
  mapping to be valid (empty when mapping is IDENTITY or NO_LICENSED_MAPPING)
- `non_preserved_coordinates`: list of coordinate names that are not preserved
  across the mapping (empty when mapping is IDENTITY)
- `recoverability_target`: list of source and mapping coordinates that must be
  exposed in a global statement for the case to count as recoverable
- `confidence`: 0.0–1.0, how confident the annotator is in the composite annotation
- `rationale`: free-text justification for the annotation choices

---

## 3. Annotation procedure

### 3.1 Fixed annotation order

The annotation order is **mandatory** and follows the handbook:

1. Source identity verification (document, version, span, hash)
2. Referent relation
3. Construct relation
4. Measurement/operationalisation relation
5. Context relation
6. Polarity and modality relation
7. Attribution and discourse relation
8. Mapping relation
9. Contradiction verdict
10. Integration verdict (GLUE_ALLOWED / OBSTRUCTION / PLURAL_VIEW / UNRESOLVED)
11. Recoverability target

The order is fixed because each coordinate constrains the next. For example,
mapping cannot be labelled before referent and construct are established, and
contradiction cannot be labelled before polarity, modality, and attribution
are separated.

### 3.2 UNRESOLVED is always available

If the annotator cannot determine the correct value, UNRESOLVED is the correct
answer. Uncertainty must not be coerced into a forced value. The adjudication
policy handles inter-annotator UNRESOLVED cases.

### 3.3 Source packet

Each sample provides:
- A frozen source packet containing the two source spans (document_id, version,
  span_start, span_end, text_hash, retrieval_hint)
- The case family label (informational, not used for annotation)
- The discipline label (informational)

The annotator should use the retrieval_hint to locate the full document if
span-level context is needed, but the annotation must be based on the actual
span content, not on the annotator's prior knowledge of the document.

---

## 4. Double-annotation design

### 4.1 Shared subset

**All 24 core samples (3 disciplines x 8 families = 24) are independently
annotated by two annotators.** This is the "substantial shared subset" required
by Issue #158.

The 8 climate margin samples are single-annotated by a primary annotator and
subsequently reviewed by a domain expert (climate science). They contribute to
robustness analysis but not to the primary hypothesis test.

| Set | Samples | Annotation | Source |
|---|---|---|---|
| Core — double-annotated | 24 (3 disc. x 8 fam.) | Two independent annotators | DISCIPLINE_SELECTION_V1.md |
| Margin — single + review | 8 (climate) | One annotator + domain expert | DISCIPLINE_SELECTION_V1.md |
| **Total** | **32** | | |

### 4.2 Annotator qualification

Annotators must:
- Hold or be pursuing a postgraduate degree in a relevant scientific discipline
- Have familiarity with the annotation schema and handbook (assessed by a
  practice round on 4 held-out samples before the main annotation)
- Not be authors of the ORION system or any ORION-13 baseline
- Not have inspected any evaluated-system outputs at the time of annotation

### 4.3 Practice round

Before the main annotation, each annotator completes a practice round on 4
held-out samples (one per discipline, same case families as the main set).
Practice annotations are compared with the gold template from `generate_gold.py`.
Annotators who achieve < 0.70 agreement on the practice round repeat the
practice with additional instruction.

### 4.4 Blinding

Annotators are blind to each other's labels during the independent annotation
phase. They see only the source packet and the annotation schema. The case
family label is visible (it is needed for the annotation protocol), but
annotators are instructed to annotate each coordinate independently regardless
of the expected case-family pattern.

---

## 5. Agreement targets

### 5.1 Per-coordinate agreement targets

Agreement is computed as **raw proportional agreement** (number of matches /
total paired annotations) on the 24 double-annotated core samples. A
chance-corrected statistic (Cohen's kappa) is reported secondarily for
coordinates with > 2 categories. The following targets define the minimum
acceptable agreement before adjudication begins.

| Coordinate | Target (raw) | Rationale |
|---|---|---|
| referent_relation | >= 0.90 | Least ambiguous coordinate; small category set |
| polarity_relation | >= 0.90 | Binary-aligned (SAME/OPPOSITE/NOT_COMPARABLE) |
| contradiction_verdict | >= 0.85 | Small category set (4 values) |
| context_relation | >= 0.85 | Moderate ambiguity, but anchored in source text |
| modality_relation | >= 0.85 | Moderate ambiguity |
| attribution_relation | >= 0.85 | Moderate ambiguity |
| mapping_relation | >= 0.80 | Largest category set (7 values); highest ambiguity |
| construct_relation | >= 0.80 | Core interpretive judgment |
| measurement_relation | >= 0.80 | Core interpretive judgment |
| discourse_relation | >= 0.80 | Fine-grained distinction |
| integration_verdict | >= 0.75 | Most interpretive; 4 values including PLURAL_VIEW |

### 5.2 If a coordinate falls below target

If any coordinate's raw agreement falls below the target, the following
escalation applies:

1. **Adjudication review** (per ADJUDICATION_POLICY_V1.md): The adjudicator
   examines the disagreeing cases, identifies the source of ambiguity, and
   produces a consolidated label.
2. **Handbook revision assessment**: If the disagreement is systematic (e.g.,
   both annotators interpreted the same handbook rule differently), the
   handbook may be revised for the remaining annotation rounds. The change
   is logged and the original labels are preserved.
3. **Domain-expert escalation**: If the disagreement depends on specialist
   knowledge not available to the general annotator, the case is escalated
   to a domain expert (see Section 6).

### 5.3 Aggregate agreement reporting

A single aggregate agreement score (macro-average across all 11 coordinates)
is reported secondarily but cannot substitute for any coordinate that falls
below its target. The publication reports:
- Per-coordinate raw agreement (proportion)
- Per-coordinate Cohen's kappa (where applicable)
- Number of adjudicated cases per coordinate
- Number of domain-expert escalations per coordinate
- Unresolved rate per coordinate
- Examples of consequential disagreements

---

## 6. Domain-expert escalation

### 6.1 Escalation triggers

A case is escalated to a domain expert when the disputed coordinate depends on
specialist knowledge not recoverable from the source packet by a trained
general annotator. Specific triggers:

| Trigger | Example |
|---|---|
| Instrument-specific operationalisation | Whether two different ELISA kits for the same biomarker are equivalent |
| Domain-specific ontology resolution | Whether a gene alias maps to the same protein isoform |
| Nontrivial coordinate transformation | Whether a unit conversion between natural-unit systems preserves the relevant information |
| Scientific boundary condition | Whether a result obtained at T=0K is expected to hold at room temperature |
| Construct validity debate | Whether a psychological construct measured by self-report is the same construct measured by behavioural observation |

### 6.2 Escalation procedure

1. The adjudicator identifies the case as requiring domain-expert review and
   records the disputed coordinate, both original labels, and the reason for
   escalation.
2. The domain expert receives the original source packet, both independent
   annotations, and the adjudicator's notes. The expert does not receive
   the evaluated-system outputs.
3. The domain expert produces a label under the same schema. The expert label
   is recorded as `annotation_round: DOMAIN_EXPERT_ESCALATION`.
4. The expert label becomes the gold for that coordinate. The original
   independent labels remain immutable and are reported.
5. If the expert also returns UNRESOLVED, the gold for that coordinate is
   UNRESOLVED. This is a valid outcome, not a failure.

### 6.3 Expert qualification

Domain experts are:
- Active researchers in the relevant discipline (publication record in the
  last 5 years)
- Not authors of the ORION system or any ORION-13 baseline
- Not involved in the annotation of the same case
- Compensated for their time (rate per case, not per result)

### 6.4 Expected escalation rate

Based on the discipline analysis in DISCIPLINE_SELECTION_V1.md, the expected
escalation rate is:
- Biomed: 1–2 cases (operationalisation equivalence, ontology resolution)
- Physics: 1–2 cases (mathematical equivalence, instrument equivalence)
- Social: 2–3 cases (construct validity, measurement equivalence)
- Climate: 1–2 cases (margin — reviewed anyway)

Total expected: 5–9 escalations out of 24 double-annotated core cases (21–38%).

---

## 7. Annotation workflow timeline

```
Phase 1: Practice round (4 held-out samples)
  → Annotator qualification assessment
  → If < 0.70 agreement: repeat with instruction

Phase 2: Independent annotation (24 core samples)
  → Annotator A: all 24 samples
  → Annotator B: all 24 samples (same 24)
  → Annotator C: 8 climate margin samples (single)

Phase 3: Agreement computation (per coordinate)
  → Report per-coordinate agreement
  → Identify cases requiring adjudication

Phase 4: Adjudication (24 core samples)
  → Adjudicator reviews disagreements
  → Escalate to domain expert where required

Phase 5: Domain-expert review (escalated cases + 8 climate margin)
  → Expert produces gold labels
  → Expert verification of core adjudicated cases

Phase 6: Gold freeze
  → Content-hash the gold artifact
  → Lock schema, handbook, and gold
  → Begin system evaluation
```

---

## 8. Case-family-specific annotation guidance

The following guidance supplements the handbook for each case family. Annotators
should read this section alongside the handbook before annotating.

### 8.1 same_name_different_referent

- **Expected pattern**: referent=DIFFERENT, construct=DIFFERENT, mapping=NO_LICENSED_MAPPING, integration=OBSTRUCTION
- **Key pitfall**: Do not let surface-form identity override referent judgment.
  The two sources use the same term but refer to different entities. Verify
  entity identity from the document context, not from the term.
- **If uncertain**: Prefer referent=DIFFERENT over referent=PARTIAL_OVERLAP.
  Shared terminology is not evidence of shared referent.

### 8.2 different_name_same_referent

- **Expected pattern**: referent=SAME, construct=SAME, mapping=IDENTITY, integration=GLUE_ALLOWED
- **Key pitfall**: Do not treat terminological variation as evidence of
  referent difference. Check entity identity from the document context
  (e.g., gene ontology, system of equations, survey instrument).
- **Preservation conditions**: Minimal (synonym dictionary or canonical
  identifier mapping).

### 8.3 same_construct_different_measurement

- **Expected pattern**: construct=SAME, measurement=NON_EQUIVALENT, mapping=CONDITIONAL_TRANSFORM, integration=GLUE_ALLOWED
- **Key pitfall**: Do not conflate construct SAME with measurement EQUIVALENT.
  Two studies may measure the same construct with differently calibrated
  instruments. The construct is the same; the measurement is not equivalent.
- **Preservation conditions**: Calibration or bridging study required.
  Direct numeric comparison without calibration is invalid.

### 8.4 same_entity_different_temporal_state

- **Expected pattern**: referent=SAME, context=DIFFERENT_STATE_OR_TIME, mapping=CONDITIONAL_TRANSFORM, integration=GLUE_ALLOWED
- **Key pitfall**: Do not treat a changed value as a contradiction. The entity
  is the same; the temporal state changed. The difference is information, not
  an error.
- **Preservation conditions**: Trend normalisation required; temporal context
  must be carried forward.

### 8.5 polarity_modality_attribution_context

- **Expected pattern**: polarity=SAME, modality=DIFFERENT_STRENGTH, attribution=DIFFERENT_ATTRIBUTION, mapping=SUBSUMPTION, integration=GLUE_ALLOWED
- **Key pitfall**: Do not treat modality/attribution differences as
  contradictions. An asserted claim subsumes a hedged claim about the same
  entity/construct; the modality and attribution differences are metadata.
- **If polarity is genuinely OPPOSITE**: This is a real contradiction (rare).
  The contradiction_verdict is CONTRADICTION and integration_verdict is
  UNRESOLVED (or OBSTRUCTION if the contradiction is structural).

### 8.6 valid_invalid_representation_mapping

- **Expected pattern**: construct=RELATED_NOT_SAME, measurement=TRANSFORMABLE_WITH_CONDITIONS, mapping=CONDITIONAL_TRANSFORM, integration=GLUE_ALLOWED
- **Key pitfall**: Do not label IDENTITY when the mapping is non-bijective.
  Two classification systems may have overlapping but not identical categories.
  The mapping is valid under specified conditions.
- **Preservation conditions**: Enumerate what is lost in each direction.

### 8.7 valid_invalid_literature_bridge

- **Expected pattern**: construct=RELATED_NOT_SAME, mapping=CONDITIONAL_TRANSFORM, integration=GLUE_ALLOWED
- **Key pitfall**: Do not label a literature bridge as valid merely because
  both papers mention the same entity. The bridge must be underwritten by a
  transfer mechanism or boundary condition.
- **Preservation conditions**: Specify dose, exposure, outcome, timescale,
  and any idealisation assumptions.

### 8.8 genuine_plural_obstruction

- **Expected pattern**: construct=DIFFERENT, mapping=NO_LICENSED_MAPPING, integration=PLURAL_VIEW
- **Key pitfall**: Do not treat PLURAL_VIEW as a failure signal. It is a
  scientifically appropriate integration verdict for cases where multiple
  legitimate, non-collapsible views coexist.
- **Distinction from OBSTRUCTION**: OBSTRUCTION implies that the two claims
  are incompatible (one must be wrong). PLURAL_VIEW implies that both are
  legitimate and the choice between them is underdetermined by evidence.
- **If uncertain**: Prefer PLURAL_VIEW over UNRESOLVED when the literature
  itself recognises the pluralism. Prefer UNRESOLVED when the evidence is
  simply insufficient to determine.

---

## 9. Quality assurance

### 9.1 Annotation consistency checks

After annotation, the following automated checks are run:

1. **Schema compliance**: Every annotation field must pass the JSON Schema
   validation in ANNOTATION_SCHEMA_V1.json.
2. **Coordinate consistency**: Check that the annotation follows the expected
   case-family pattern (informational, not a correctness gate).
3. **Preservation-conditions completeness**: If mapping is CONDITIONAL_TRANSFORM
   or SUBSUMPTION, preservation_conditions must be non-empty.
4. **Non-preserved-coordinates completeness**: If mapping is CONDITIONAL_TRANSFORM,
   non_preserved_coordinates must list at least one coordinate.
5. **Recoverability-target completeness**: recoverability_target must include
   source_a.document_id, source_b.document_id, the mapping_relation value,
   and any non-default preservation_conditions.

### 9.2 Gold freeze

The gold artifact is frozen when:
- All 32 samples have a gold annotation
- All 24 double-annotated core samples have been adjudicated
- All domain-expert escalations are resolved
- The consistency checks pass
- The gold artifact is content-hashed (SHA-256) and the hash is recorded
- The hash is deposited in a custody file accessible to the evaluation
  pipeline but not modifiable by it

After gold freeze, evaluated-system outputs may be inspected. No gold label
may be changed after system access without a versioned schema update and a
written justification.

---

## 10. Licensing and data statement

The gold annotations are released under CC-BY 4.0. The source spans are
quoted under fair use / scientific quotation (each < 400 characters).
Full-text retrieval instructions are provided for each source document.
The annotation schema, handbook, and adjudication policy are released under
the same license as the ORION codebase.

A formal data statement (following the guidelines of Gebru et al., 2021)
will accompany the publication. It will document:
- Dataset purpose and composition
- Collection process and annotator qualifications
- Intended uses and limitations
- Licensing and access restrictions
- Maintenance and update policy