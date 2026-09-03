# A6 External Authority/Discharge Study — Census Lane README (v1)

Lane authority: SzeChunYiu/ORION-paper#49, section A6 Phase 2.
Scope of this lane: outcome-blind source census + external adjudicator handoff
contract. Nothing here adjudicates eligibility, seals predictions, or touches
gold labels.

## Artifacts in this directory

| Artifact | Role |
|---|---|
| `A6_EXTERNAL_ADJUDICATOR_HANDOFF_V1.json` | Contract binding the external adjudicator's gold packets to the (future) `ORION.A6.ExternalAuthorityPacketIntakeManifest.v1`; two gold labels, three-valued alphabet (ADMIT/DENY/CANNOT_CHECK), disagreement rule, candidate-blind + independence attestations. |
| `validate_external_adjudicator_packet_v1.py` | Validator for `ORION.A6.ExternalAdjudicatorGoldPacket.v1` (`--self-test` runs hostile mutants). |
| `census_a6_workflowhub_transitions_v1.py` + `workflowhub-census-v1/` | Stratum 2 census + snapshot (reuses the A3 frozen frame; see below). |
| `census_a6_zenodo_software_releases_v1.py` + `zenodo-census-v1/` | Stratum 1 census + snapshot. |
| `census_a6_scientific_record_transitions_v1.py` + `scientific-record-census-v1/` | Stratum 3 census + snapshot. |
| `lunarc_a6_strata_1_3_job_v1.sh`, `lunarc_a6_stratum3_job_v1.sh` | sbatch wrappers used for the census runs (record of execution environment). |
| `LANE_A6_CENSUS_README_V1.md` | This file. |

CI: `.github/workflows/orion-a6-external-adjudicator-handoff-v1.yml` (mirrors
`orion-a3-external-curator-handoff-v1.yml`; runs contract boundary assertions,
both validators' self-tests, py_compile, forbidden-import AST ban, and
whitespace checks).

## Execution record (LUNARC, account lu2026-2-51, partition lu48)

| sbatch job | What ran | Result |
|---|---|---|
| 3569323 | egress probe (workflowhub, crossref, zenodo, datacite) | all 200 |
| 3569334 | stratum-2 WorkflowHub census | 313 packet candidates; stratum-1 attempt died on Zenodo HTTP 400 (see blockers) |
| 3569831 / 3569850 | strata 1+3 retry | 504 retry-hardening iteration (see blockers) |
| 3570006 | strata 1+3 retry | node-level CANCELLED at 53 s (no script output); resubmitted |
| 3570015 | strata 1+3 | stratum-1 GREEN (228 candidates); stratum-3 first route enumerated Crossref-side and yielded 0 bindable packets → re-derived (below) |
| 3571277 | stratum-3 (re-derived supplement-side enumeration) | 188 packet candidates, exit 0 |

All scripts ran `--self-test` on-target (GREEN) before each network census.

## Census results vs the 20/20/20 quota

| Stratum | Universe | Packet candidates | Distinct org lineages | Distinct source families | Capacity decision |
|---|---|---|---|---|---|
| 1 — Zenodo software release transitions (`zenodo-census-v1/`) | 400 most recent open licensed software record families | **228** | **211** | 228 | `A6_STRATUM1_..._AT_LEAST_20_DISJOINT_ORG_LINEAGES` |
| 2 — WorkflowHub RO-Crate versioned workflow transitions (`workflowhub-census-v1/`) | 430 multiversion WorkflowHub families (TRS list 1,534 tools) | **313** (128 reused from the A3 frozen frame `a47d9255…`, 185 freshly RO-Crate-bound) | **64** | 313 | `A6_STRATUM2_..._AT_LEAST_20_DISJOINT_ORG_LINEAGES` |
| 3 — scientific-record transitions (`scientific-record-census-v1/`) | 300 DataCite Dataset records declaring DOI-typed `IsSupplementTo` | **188** | **25** | 87 | `A6_STRATUM3_..._AT_LEAST_20_DISJOINT_ORG_LINEAGES` |

Each snapshot directory carries `A6_STRATUM{n}_CENSUS_MANIFEST_V1.json` with
per-chunk SHA-256s and a `packet_candidate_rows_sha256` binding; all rows carry
the full lineage trio (`source_family_id`, `normalized_organization_lineage`,
`artifact_lineage_id`) required by the allocation stage.

These are **capacity statements only**. The 20/20/20 primary quota and the
replication quota stay **unallocated**: allocation is deliberately unrun until
the `EligibleExternalAuthorityPacketPool.v1` and externally frozen replication
quotas exist (deterministic pre-outcome allocation contract:
`orion-a6-deterministic-preoutcome-allocation-v1.yml`). Stratum 3's 25 distinct
organization lineages pass the ≥20 capacity gate but cap replication headroom;
that constraint transfers to the pool stage, not the census.

## Blockers and re-derivations (recorded, never padded)

1. **Corrections sub-route (stratum 3) — CANNOT_CHECK.** The Crossref relation
   vocabulary (server-enumerated 2026-09-03) has no correction relation type;
   OpenAlex `type:erratum` reaches the original work only via algorithmic
   `related_works`. Correction pairs are not mechanically bindable without
   fuzzy title matching. Recorded in the stratum-3 manifest
   (`correction_subroute_blocker`).
2. **Software-side supplements (stratum 3) — CANNOT_CHECK.** Software records
   declare `IsSupplementTo` via URL identifiers (GitHub links; 15/15 sampled),
   never DOIs, so no Crossref article record is mechanically reachable. The
   bound sub-route is Dataset-side. Recorded in the manifest
   (`software_subroute_blocker`).
3. **Zenodo unauthenticated page-size cap.** `size>25` returns HTTP 400
   ("Page size cannot be greater than 25…"); fixed by `size=25` pagination.
   Zenodo also intermittently 504s on the sorted scan query (same URL 504s
   then 200s minutes later); handled with 6-retry exponential backoff
   (1→2→4→8→16 s). Both behaviours are commented in the script.
4. **Stratum-3 first enumeration route (Crossref article-side) — re-derived,
   not shipped.** Enumerating `is-supplemented-by` from the article side
   reaches publisher `posted-content`/`component` supplements and dead
   protocols.io DOIs, yielding 0 mechanically bindable Dataset/Software
   transitions. The lane re-derived the enumeration from the supplement side
   (DataCite `IsSupplementTo`, DOI-typed), which makes the resource-type filter
   native and binds the article from Crossref for organization lineage. The
   failed route's artifacts were discarded, not committed.
5. **15 WorkflowHub binding failures (stratum 2)** recorded as
   `cannot_check_binding_failure_n` (RO-Crate or landing fetch failed after
   retries); 23 Zenodo family failures and 112 DataCite record skips
   (`no_doi_typed_supplement_relation`) recorded in their manifests.

## Outcome-blindness

Every manifest carries `stratum_eligibility_adjudicated: false`,
`gold_adjudicated: false`, `protected_orion_predictions_accessed: false`,
`scientific_authority_delta: NONE__OUTCOME_BLIND_SOURCE_CENSUS_ONLY`. Rows
contain only public source metadata, digests, and lineage ids — no candidate
predictions (sealed later against the pool), no gold labels (external gold only,
per the handoff contract).

## What remains (downstream lanes)

1. `EligibleExternalAuthorityPacketPool.v1` from these census frames.
2. `ExternalAuthorityPacketIntakeManifest.v1` (the adjudicator validator
   already binds to its schema and exact fields).
3. Externally frozen replication quotas per stratum.
4. Deterministic pre-outcome allocation (20/20/20 + replication) — unrun by
   design until 1–3 exist.
5. External adjudication via the handoff contract; validation; analysis.
