# Cross-session empirical-provenance audit — P1 and P3

## Terminal

`CROSS_SESSION_EMPIRICAL_PROVENANCE_AUDIT_P1_P3_COMPLETE__NO_RECORD_PROMOTED__TOP_TIER_EMPIRICAL_CLAIMS_CANNOT_CHECK`

No empirical record was imported or promoted. No manuscript, readiness file, source evidence, Git ref, or shared result was edited.

## Source checkout

| Item | Exact value |
|---|---|
| Parent-observed head | `b55f553b7b16b488cf4c515ba286578783a5fd83` |
| Audited stable head | `8d6d5992a9f0e2b93254ed441b88ea0b5e61644b` |
| Branch | `claude/orion-rg-d2-decomposition-criterion-20260823` |
| Distance | 1 descendant commit |
| Selected tracked sources identical across heads | 9/9 |
| Source status excluding this audit path | 72 untracked entries; SHA-256 `b0054941fff801fd283bb59201ff4efd87e415281824c5bcbe799d665fc545c2` |
| Selected inventory | 121 files; digest `098e405d9f8177320f6a07961947de55137bca79760a2ec94b6bd12e4d600cae` |

The head moved after the parent observed it, but the nine selected tracked interpretation sources are blob-identical at both heads. Candidate empirical files remain untracked and are not bound by either commit.

## Exact admission matrix

| Group | Files | Audit facts | Narrow empirical scope | Naturalistic/real-source | Rejected or CANNOT_CHECK for top-tier promotion |
|---|---:|---:|---:|---:|---:|
| P1 pilot raw/scored | 2 | 2 | 0 | 0 | 2 |
| P1 tracked test raw/scored | 2 | 2 | 2 | 0 | 2 |
| P3 untracked annotation files | 32 | 32 | 0 | 0 | 32 |
| P3 run-full core artifacts | 5 | 5 | 0 | 0 | 5 |
| P3 run-smoke core artifacts | 3 | 3 | 0 | 0 | 3 |
| P3 partial analysis artifacts | 2 | 2 | 0 | 0 | 2 |
| **Total** | **46** | **46** | **2** | **0** | **46** |

The two narrow-scope files are the tracked P1 test raw/scored files, and their admissible claim is **historical `P1.hidden-formulation.v1` harness performance only**. They do not license P1 V2/V3 naturalistic action semantics.

Additionally, 66 run-full logs were hashed but not semantically opened, and nine tracked context/code files were used only to interpret provenance.

## P1

- Pilot: **990** unique rows = 18 cases × 11 systems × 5 seeds; both files are untracked; subject revision `55f0bc766f2242ca6fffd729f3f44c01168f663d+dirty`; **0/990** raw rows report nonzero model tokens.
- Test: **2,880** unique rows = 48 cases × 12 systems × 5 seeds; both files are tracked. Exactly **240** `orion_live_provider` rows report **289,261** model tokens.
- All four artifacts bind `P1.hidden-formulation.v1` suite fingerprints. Therefore they are hidden-formulation harness evidence, not naturalistic P1 V2/V3 action, postpublication, construct-validity, or owner-authority evidence.

P1 terminal: `P1_CROSS_SESSION_RAW_EVIDENCE_IS_HIDDEN_FORMULATION_HARNESS_ONLY__NATURALISTIC_V2_V3_ACTION_EVIDENCE_CANNOT_CHECK`

## P3

### Source and annotation provenance

- **32** annotation files, **64** source references.
- **64/64** document IDs contain `SEED-`; **64/64** text hashes use `seed:sha256:`; **0/64** are valid 64-hex content hashes.
- Only **63** unique placeholder hashes exist (one duplicate excess).
- Tracked combined-gold source texts are only 31–87 characters and **0/64** declared hashes equal SHA-256(text).
- **32** annotator-a files, **0** annotator-b files; all declare `adjudicated-v1`. The tracked freeze explicitly records `independent_labels_exist=false` and `coordinate_agreement_computable=false`.

### Run-full result layer

- **75** PASS rows = 15 systems × 5 seeds; ORION_FULL contributes **5** PASS rows.
- **75/75** rows report zero tokens, tools, wallclock, and currency; **75/75** have `cost_metrics_error=-1`.
- AST evidence shows the cost function takes one argument while the metric dispatcher supplies two; the error sentinel is deterministic.
- **75/75** `raw_artifact_hash` values equal `SHA256(system_id|seed)`, not retained raw model output.
- The evaluator contains `ORION_FULL_NOT_YET_BOUND`, hard-coded zero cost metadata, and no source-revision field.
- Manifest gold hash `667be9620944abba078dca442c1283baec59a14989fbdf5761137a7cd11e5c8a` does **not** match tracked combined-gold byte SHA-256 `778168a5c05da95464f76b877762c1f9da19f41a8ee5dcc28ac65aca58471e7e`.
- Resource policy leaves context budget and retrieval allowance as `TBD`.

### Checkpoint layer

- Final checkpoint: **3,340 rows**, **2,400** unique `(system, case, seed)` keys, **940 duplicate excess**.
- **683** keys repeat and **all 683 conflict**; no repeat is byte-identical; maximum multiplicity is **7**.
- Pre-retry: **2,720 rows**, **2,328** unique keys, **392 duplicate excess**. Final adds the 72 missing keys.
- Analyzer source silently performs last-write-wins by `case_id`; no prospective attempt-selection rule is bound.
- Analysis output is incomplete: **0** aggregate systems and only `ORION_FULL`/`VanillaLongContext` at one seed each.

P3 terminal: `P3_CROSS_SESSION_STRUCTURAL_OUTPUTS_PRESENT__REAL_SOURCE_PROVENANCE_ANNOTATOR_INDEPENDENCE_COST_AND_DEDUPLICATED_EMPIRICAL_BINDING_CANNOT_CHECK`

## Bounded positive result

The files prove structural harness execution and complete index grids: P1's hidden-suite grids are complete, P3's 75 system-seed result records exist, and P3's final checkpoint covers all 2,400 expected keys. They do **not** prove real-source construct validity, independent annotation reliability, actual ORION backend execution, measured cost, deterministic retry selection, or a content-addressed metric derivation.

## Next discriminator

1. **P1:** clean source-bound prospective naturalistic action study with rights-valid cases and owner-separated independent gold.
2. **P3 sources:** replace all 64 placeholders with verified licensed document/version/span bytes and exact hashes.
3. **P3 annotation:** two independent blind labels on a preregistered shared subset, coordinate-wise agreement, then adjudication.
4. **P3 execution:** exact clean revision, real backend/raw outputs, measured costs, numeric matched resource policy.
5. **P3 retry/analysis:** prospective attempt rule, duplicate-free checkpoint, exact gold hash, and one derivation manifest binding every selected row through final metrics.
