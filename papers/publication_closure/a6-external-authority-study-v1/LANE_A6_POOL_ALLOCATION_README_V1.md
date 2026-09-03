# A6 downstream lane: eligible pool, frozen quotas, pre-outcome allocation, intake, adjudication prep (v1)

Date: 2026-09-03. Builds on the frozen census snapshots (`zenodo-census-v1/`,
`workflowhub-census-v1/`, `scientific-record-census-v1/`; see
`LANE_A6_CENSUS_README_V1.md`). Everything below is outcome-blind: no ORION
candidate predictions, no baselines, and no protected outcomes exist at this
stage, and every artifact asserts `protected_outcomes_accessed=false`,
`candidate_predictions_accessed=false`, `gold_adjudicated=false`.

## What was built

| Stage | Artifact | sha256 |
|---|---|---|
| Eligible pool v1 | `eligible-pool-v1/A6_ELIGIBLE_POOL_V1.json` | `649e4be71d6945f5da4480855f2b210267e520f504202bb3ef6fcac80e301cb7` |
| Replication quota freeze | `A6_REPLICATION_QUOTA_FREEZE_V1.json` | `f7525f4d5b484e94629a701df676b1bf02a31d294ccc75cb44a9b1bfa804dc53` |
| Pre-outcome allocation | `allocation-v1/A6_PREOUTCOME_ALLOCATION_RESULT_V1.json` | `41eecb7c3f1f6cc39fba3c94063aa0053e10365d0ad2185ece15269e499dc13d4` |
| Intake manifest v1 | `intake-v1/A6_EXTERNAL_AUTHORITY_PACKET_INTAKE_MANIFEST_V1.json` | `3c86b456ad502dd7925026ef6235394fc0c5a8a0624648c39a3d700cefe9d896` |
| Adjudication prep | `adjudication-prep-v1/` (75 `PACKET_*.json` + coverage manifest) | coverage manifest `1d42da6b64b09f69d36e0c615762389d8f587b0e3c5318e48de42e3dcb09d187` |

Builder tooling (each with a hostile self-test; all GREEN):
`build_eligible_external_authority_pool_v1.py`,
`build_external_authority_intake_manifest_v1.py`,
`prepare_external_adjudicator_packets_v1.py`,
`A6_EXTERNAL_ADJUDICATOR_PACKET_TEMPLATE_V1.json`,
CI: `.github/workflows/orion-a6-pool-intake-allocation-v1.yml` (keyless,
PR-path; rebuilds the committed artifacts and proves byte identity,
re-derives the allocation through the frozen allocator, re-validates intake
and prep, bans RNG/network imports).

## Eligible pool v1 (729 packets, zero ineligibles)

| Stratum | census candidates | eligible_preterminal | ineligibles |
|---|---|---|---|
| scientific_software_release_provenance_attestation | 228 | 228 | 0 |
| workflowhub_rocrate_versioned_workflow | 313 | 313 | 0 |
| scientific_record_transition | 188 | 188 | 0 |

Eligibility is adjudicated from registry/metadata properties only, per the
frozen rule table (`E_COMMON_*`, `E_S1_*`, `E_S2_*`, `E_S3_*`; see the pool
builder). The census construction had already excluded the recorded blocker
classes, so the sweep marks every remaining candidate eligible and every
ineligible rule count is empty — nothing was padded, loosened, or silently
dropped. Each pool packet carries `eligible_preterminal` plus its full rule
failure list (empty), the tamper-evident census bindings (manifest sha256 +
`packet_candidate_rows_sha256`, re-verified at build time), the three custody
receipts, and the `candidate_visible_packet_sha256` over the canonical
science-coordinates-only payload.

## Replication quotas (externally frozen, zero free parameters)

`A6_REPLICATION_QUOTA_FREEZE_V1.json` derives, and the pool builder
re-proves from the live census manifests:

```
R = max(1, min_s(cap_s - 20)),  cap_s = distinct_normalized_organization_lineage_n
caps = { s1: 211, s2: 64, s3: 25 }   (census-frozen external facts)
R = min(191, 44, 5) = 5   ->   replication_quota_by_stratum = 5/5/5
replication_target_n = 15
```

- The uniform 5/5/5 quota honors the 20/20/20 primary quota and per-stratum
  source disjointness; the derivation rule
  (`A6_REPLICATION_QUOTA_UNIFORM_MIN_EXTERNAL_CAPACITY_V1`) has no free
  parameter — change a capacity and the builder rejects the freeze as
  non-derived (self-test mutant).
- Stratum 3's 25-lineage cap BINDS (headroom 5). This is recorded honestly
  in the freeze (`headroom_caps_recorded_honestly.scientific_record_transition`,
  `"THIS CAP BINDS"`); no
  padding, no eligibility loosening was performed to raise it.
- No shortfall: greedy max-disjoint feasibility per stratum (211 / 64 / 25)
  confirms 20 primary + 5 replication disjoint packets exist everywhere.
  The frozen allocator reached terminal
  `A6_EXTERNAL_PRIMARY_REPLICATION_ALLOCATION_FROZEN` (not CANNOT_CHECK).

## Deterministic pre-outcome allocation (frozen allocator, verbatim)

`allocate_external_authority_packets_v1.py` was imported and re-run
byte-identically by both downstream builders and by CI:

- terminal: `A6_EXTERNAL_PRIMARY_REPLICATION_ALLOCATION_FROZEN`
- primary_n 60 (20/20/20), replication_n 15 (5/5/5)
- `selection_manifest_sha256`: `e710198fe045d42305c587f53e4a0f60f3b8ae1adacb5e5e851c6daddc6cac8a`
- allocation key: SHA256 over
  `A6-ALLOCATION-V1|stratum|packet_id|source_family_id|normalized_organization_lineage|artifact_lineage_id`,
  greedy sort by (allocation_key_sha256, packet_id); seeded by content only
  (no RNG, no keys, no environment inputs). Row-order invariance is a
  self-test assertion.

## Intake manifest v1 (frozen validator GREEN on the real manifest)

`validate_external_authority_packet_manifest_v1.py` (frozen, imported
verbatim) output on `intake-v1/A6_EXTERNAL_AUTHORITY_PACKET_INTAKE_MANIFEST_V1.json`:

```json
{
  "decision": "GREEN",
  "gold_or_outputs_present": false,
  "intake_manifest_sha256": "3c86b456ad502dd7925026ef6235394fc0c5a8a0624648c39a3d700cefe9d896",
  "primary_counts": {
    "scientific_record_transition": 20,
    "scientific_software_release_provenance_attestation": 20,
    "workflowhub_rocrate_versioned_workflow": 20
  },
  "primary_n": 60,
  "replication_counts": {
    "scientific_record_transition": 5,
    "scientific_software_release_provenance_attestation": 5,
    "workflowhub_rocrate_versioned_workflow": 5
  },
  "replication_n": 15,
  "schema": "ORION.A6.ExternalAuthorityPacketIntakeValidation.v1",
  "source_disjoint": true
}
```

The intake rows carry exactly the 15 fields bound by
`ORION.A6.ExternalAuthorityPacketIntakeManifest.v1`; the builder re-derives
the allocation from the committed pool and refuses to emit any manifest on a
shortfall terminal.

## External adjudication prep (sign-off slots EMPTY)

`adjudication-prep-v1/` holds one `PACKET_*.json` per frozen intake packet
(75 total) with the intake-bound fields verbatim, the candidate-visible
packet rebuilt from the frozen census bytes and hash-asserted against the
intake's `candidate_visible_packet_sha256`, and an explicit
`UNADJUDICATED` block: both gold labels null, adjudicator receipt null,
`sign_off_slots_empty: true`. The template the external adjudicator fills is
`A6_EXTERNAL_ADJUDICATOR_PACKET_TEMPLATE_V1.json` (per
`A6_EXTERNAL_ADJUDICATOR_HANDOFF_V1.json`; gold packet validator
`validate_external_adjudicator_packet_v1.py`). Verify-mode result: `GREEN`,
`prep_packet_n 75`, `sign_off_slots_empty true`, `adjudications_performed 0`.

No external adjudicator has been engaged, no gold label exists, and no
sign-off slot is filled: governance sign-off is external continuation, never
promotion. These receipts record custody and assignment only.

## Compute provenance

- LUNARC sbatch job **3572262** (cn160, Python 3.11.5, account lu2026-2-51,
  partition lu48), staged under fs9; all six self-tests GREEN, then pool →
  allocation → intake → prep → verify in one deterministic run. (Job 3572234
  was an earlier failed run: a self-test fixture defect, fixed before this
  run; no artifact from it was used.)
- Mac-side rebuild of the pool and intake manifests is byte-identical
  (`cmp`) to the committed artifacts; the CI workflow re-proves this on
  every PR touching these paths.

## Honest gaps (one line each)

- 75 prep packets exist but no external adjudicator is engaged yet; every
  sign-off slot is empty and confers nothing.
- replication_target_n=15 is small in absolute terms — bounded by stratum 3's
  25 external org lineages; recorded as a binding constraint, not padded.
- The A3 mirror lane's standing CI debt (papers 01/08/10/13) is untouched by
  this lane.
