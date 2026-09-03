# A5 Phase-2 Execution Plan (post-precondition-merge)

Scope: everything required to move from the current state (design freeze +
source census + backbone bytes binding) to the frozen terminal
`A5_PANEL_24_8_16_ALLOCATION_FROZEN_BEFORE_OUTCOMES` and then to executed
arms under `NATURALISTIC_SCORING_AND_NULL_ANALYSIS_FREEZE_V1.json`.  Nothing
here touches outcomes before allocation; all work streams are fail-closed.

## State as of 2026-09-03 (this PR)

- Source feasibility: CLOSED as a census artifact — 6/32 cells hold >=48
  rights-and-bytes-bound candidate units; 26 cells
  `CANNOT_CHECK_A5_CELL_SOURCE_UNIVERSE_SHORTFALL`; frame terminal
  `A5_SOURCE_UNIVERSE_32_CELL_FRAME_CANNOT_CHECK`
  (`A5_SOURCE_FEASIBILITY_RESULT_V1.json`).
- M1 arXiv pool: 1531/1536 bound; 5 rows confirmed permanently absent upstream
  (both official hosts, 30 attempts — `source_binding/arxiv-cc-by-fulltext-pool-binding-resume-v3/`).
- Comparator backbone: bytes + runtime precondition verified on-host
  (`source_binding/comparator-backbone-bytes-binding-v1/`), CI verifies API pins.
- Allocation manifest: NOT producible in-house (external screen gate).

## Work streams

### S1. Source-universe repair for the 26 short cells (in-house, billy-old/LUNARC)

Ordered by expected cell gain per effort:

| # | Job | Cells touched | Expected gain | Effort |
|---|-----|---------------|---------------|--------|
| S1a | Domain-assigned re-harvest of PMC reservoirs (M4: 203, M8: 14, M3: 3 rights-clear pairs) with per-object bytes+rights receipts | 12 (M3/M4/M8 x4) | up to 12 cells if reservoirs cover quota after domain assignment + eligibility attrition | 2-3 days |
| S1b | M2 earlier-version licence+bytes binding: for each metadata-signal candidate, bind BOTH versions' licence and PDF sha256 (v-introspection via export.arxiv.org) | 4 | up to 4 cells (signals: 102/138/75/81) | 2-3 days |
| S1c | M7 linked-pair rights route: crossref/DOI conference-proceedings linkage + rights binding | 4 | partial (signals 16/31/100/83 but no route executed yet) | 3-5 days |
| S1d | M5 shortfall top-up (EE gap 5, PE gap 15, SS gap 15): Zenodo record-level rights+bytes receipts beyond census counts | 3 | likely partial | 1-2 days |
| S1e | M6 shortfall top-up (EE gap 40, LB gap 41, PE gap 40): Software Heritage archive bindings + Zenodo-M6 cross-route dedup audit to admit the 6/10/10/7 reservoir | 3 | partial | 2-3 days |

Fail-closed rule: any cell still short after S1 stays
`CANNOT_CHECK_A5_CELL_SOURCE_UNIVERSE_SHORTFALL`; no cross-cell borrowing
(frozen attrition rule).

### S2. External eligibility/mechanism screen handoff (external dependency, in-house prep)

- Author the screen packet format: one row per bound candidate with the frozen
  eligibility fields (`same_exact_target_claim_predeclared`,
  `one_information_coordinate_candidate`,
  `restricted_state_existed_independently`, lineage ids, rights receipts).
- Effort (prep): 1 day.  Runtime: external party.

### S3. Comparator execution identities C2/C3/C4 (author-side + external)

- C2/C3: declare-or-reimplement decision + frozen identity receipts
  (MISSING_ORIGINAL_OR_DECLARED_REIMPLEMENTATION_IDENTITY today).
- C4: separate implementation of the frozen specification + external
  execution binding.
- Effort: 2-4 days author-side.

### S4. Allocation (deterministic, in-house) — after S1+S2

- Feed the external-screen-complete pool to the frozen allocator
  (`allocate_naturalistic_panel_v1.py`); commit the 768+256 manifest;
  validate with `validate_naturalistic_panel_manifest_v1.py`.
- Effort: 0.5 day (the code is frozen and self-tested).

### S5. Arm execution + analysis (phase 3, after S4)

- Candidate + C1-C4 over primary then replication clusters under the scoring
  freeze; nuisance probes; 10000-resample cluster bootstrap; report per the
  freeze's required_analyses.  Effort: 3-5 days compute+reporting once panels
  and gold exist.

## External-party blockers (stated once)

1. Eligibility/mechanism screen + terminal adjudication + gold custody: needs
   an independent external custodian (per ORION-paper#49 adjudication).
2. C4 external execution (and optionally C2/C3 original-identity holders).

## Sequencing

S1 (parallel tracks on billy-old) -> S2 handoff -> S4 allocation as soon as
the screen returns complete -> S5.  S3 can proceed in parallel with S1/S2.
