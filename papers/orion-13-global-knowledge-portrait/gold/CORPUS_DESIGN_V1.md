# ORION-ORION-13 gold corpus design V1

**Status:** DESIGN_FROZEN (outcome-blind). Part of `ORION-13.cross-domain-atlas.v1`.

## Discipline selection rationale

Three disciplines with materially different terminology, measurement practice and
evidential conventions are required by the protocol. A fourth discipline is
included for margin.

### 1. Biomedical / life sciences (biomed)
- **Typical constructs:** disease status, biomarker concentration, drug efficacy,
  survival rate, expression level.
- **Measurement practice:** standardised assays, clinical endpoints, statistical
  thresholds (e.g. p < 0.05), meta-analytic pooling.
- **Why it differs:** strong ontological commitment via ontologies (GO, HPO, ICD);
  measurement is often instrument-mediated and reported with precision bounds.
- **Source examples:** PubMed Central open-access articles, arXiv q-bio.

### 2. Physics / condensed matter (physics)
- **Typical constructs:** critical temperature, band gap, magnetisation,
  conductivity, lattice parameter.
- **Measurement practice:** instrument-specific (XRD, STM, SQUID), unit conversion
  common, temperature/pressure dependence is routine.
- **Why it differs:** constructs are often mathematically defined and
  instrument-independent in principle, but operationalisations can differ by
  technique. Same name / different measurement is common (e.g. "band gap" from
  optical vs transport measurement).
- **Source examples:** arXiv cond-mat, Phys. Rev. open-access.

### 3. Social / behavioural science (social)
- **Typical constructs:** well-being, trust, economic preference, intelligence,
  social capital.
- **Measurement practice:** survey instruments, Likert scales, latent-variable
  models, construct validity debates are explicit and persistent.
- **Why it differs:** construct validity is itself a research topic; measurement
  equivalence across populations is a known challenge; "same construct, different
  operationalisation" is the norm, not the edge case.
- **Source examples:** Open-access psychology/economics journals, SocArXiv.

### 4. Climate / earth science (climate) — margin discipline
- **Typical constructs:** global mean temperature, radiative forcing, climate
  sensitivity, precipitation anomaly.
- **Measurement practice:** reanalysis products, satellite retrievals, proxy
  reconstruction, model ensembles; measurement is conditional on the
  retrieval/assimilation system.
- **Why it differs:** multiple legitimate operationalisations of the same construct
  (e.g. "temperature anomaly" from different reanalyses) coexist as plural views
  rather than one being correct.
- **Source examples:** IPCC reports, ESSD open-access, arXiv physics.ao-ph.

## Source-paper selection criteria

1. **Open-access or CC-BY licensed** — preferred for legal shareability of spans.
2. **Published in a peer-reviewed venue** or on arXiv with substantive scientific
   content.
3. **Contains at least one claim** that can be compared with another paper's claim
   along one of the 12 case families.
4. **Sufficient bibliographic metadata** — DOI, arXiv ID, or PubMed ID.
5. **No embargoed or access-controlled data** as the primary source.

## Case-family coverage strategy

The PROTOCOL_V1.json task_families are:

| # | Task family | Primary discipline pair | How to source |
|---|---|---|---|
| 1 | same_name_different_referent | biomed, physics | Find papers using "titanium dioxide" (pigment vs photocatalyst), "zebrafish" (model organism vs ornamental), "critical temperature" (superconductivity vs magnetic transition) |
| 2 | different_name_same_referent | biomed, social | "Major Depressive Disorder" vs "clinical depression" / "MDE"; "hypertension" vs "high blood pressure" |
| 3 | same_construct_different_measurement | biomed, social, climate | "Intelligence" via WAIS vs Raven's; "well-being" via SWLS vs PANAS; "temperature anomaly" via different reanalyses |
| 4 | same_entity_different_temporal_state | climate, physics | "El Niño strength" in 1997 vs 2015; "CO₂ concentration" pre-industrial vs current; "Hubble constant" 2020 vs 2024 measurement |
| 5 | polarity_modality_attribution_context | biomed, social | "Drug X is effective" vs "Drug X may be effective"; "result supports hypothesis" vs "authors cite prior work supporting hypothesis" |
| 6 | valid_invalid_representation_mapping | physics, climate | Convertible units (eV ↔ J); non-equivalent operationalisations (band gap optical vs transport); incompatible spatial resolutions |
| 7 | valid_invalid_literature_bridge | cross-discipline | A–B–C bridges where middle term preserves or shifts meaning across disciplines |
| 8 | genuine_plural_obstruction | social, climate | Unresolved construct debates (e.g. "g" factor vs multiple intelligences; different equilibrium climate sensitivities from different models) |

Additional case families are derived from the annotation schema's coordinate
structure and the handbook's special cases; they are not separate task_families
in the protocol but are guaranteed by the family coverage above.

## Privacy / IP / copyright review

- All source documents are **open-access** or CC-BY licensed where possible.
- Short quoted spans (<400 characters) are considered fair-use / quotation for
  scientific annotation in most jurisdictions; we nevertheless prefer documents
  with explicit CC-BY / CC-0 licences.
- Each source entry in the manifest records `document_id`, `document_version`,
  `span_start`, `span_end` and `text_hash` so the gold remains verifiable even
  if the full text cannot be redistributed.
- For non-open documents, the manifest provides retrieval instructions
  (DOI / arXiv ID / PubMed ID) rather than the full text.
- **No copyrighted full-text redistribution.** The gold artifact is the
  structured annotation, not the source text.

## License strategy for the gold artifact

The adjudicated gold annotations are released under **CC-BY 4.0**.
The annotation schema, handbook and manifest are released under the same
licence as the ORION codebase.