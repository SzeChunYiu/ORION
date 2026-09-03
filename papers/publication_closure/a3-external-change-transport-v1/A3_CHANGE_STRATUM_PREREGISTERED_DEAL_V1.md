# A3_CHANGE_STRATUM_PREREGISTERED_DEAL_V1 — decision document

Date: 2026-09-03. Governance record: `A3_CHANGE_STRATUM_PREREGISTERED_DEAL_V1.json`.
Validator: `validate_change_stratum_preregistered_deal_v1.py` (`--self-test`).

## Decision

The blocking stratum label for each of the 128 frozen change-transport families
is assigned by a preregistered, outcome-blind, zero-free-parameter mechanical
deal over descriptor-side frame values only:

- `score = SHA256("A3-CHANGE-STRATUM-DEAL-V1|" + workflow_id + "|" + version_before
  + "|" + version_after + "|" + license_before + "|" + license_after + "|"
  + before_normalized_sha256 + "|" + after_normalized_sha256)`
- families ordered ascending by `(score, int(workflow_id), workflow_id)`
- rank `r` in `0..127` maps to `STRATA_ORDER[r mod 4]` = (representation_schema,
  responsibility_output_contract, objective_acceptance_criterion,
  evidence_dependency) → exactly 32 per stratum.

No frozen stratum-assignment rule existed in the repository when this record
was drafted (repo-wide search, cross-checked), so the mission-authorized
preregistration path was taken. No outcome, gold, or prediction value existed
anywhere in the pipeline at deal time — the only inputs are the frozen
successor frame (sha256 `a47d92…c2993`) and the frozen A6 census organization
lineages.

## What this is NOT

This deal assigns the stratification dimension only. It is not the external
curator's semantic adjudication: REUSE/REOPEN/CANNOT_CHECK gold remains
escrowed out of house (reviewer scope, SzeChunYiu/ORION-paper#49), and no
scientific judgment is made or implied about any family. The
`curator_assignment_receipt_id` on each pool row is the deal's mechanical
receipt, labeled as standing in for the external curator for the blocking
stratum label only.

## Organization lineage granularity (forced, not chosen)

The frozen allocator requires global uniqueness of
`normalized_organization_lineage` across all 128 selections. The frame holds
only 33 distinct census organizations, so a bare-organization lineage is
arithmetically impossible (33 < 128) and fails the allocator closed — verified
mechanically by the validator's quota-consequence control. The committed rule
uses the family-terminated token `{census_org}:family:{workflow_id}`, the
coarsest lineage satisfying the frozen uniqueness contract while preserving
the census organization verbatim as prefix.

## Execution

Run on billy-laptop-old (ssh billy-old, Python 3.14.4, 2026-09-03), rc 0 for
each command: assignments → governed pool build → frozen allocator
(`allocate_change_clusters_v1.py` unmodified). Terminal
`A3_PREOUTCOME_PRIMARY_REPLICATION_ALLOCATION_FROZEN`, 128 selected, 24
primary + 8 replication per stratum, selection manifest sha256
`e5237c80139a2ecbc05fd6a95fad760cb3b4308592e7c6b2b9dada2d92a00bf7`.
Artifacts: `blocking-stratum-deal-v1/ASSIGNMENTS_V1.json`,
`eligible-pool-v1/A3_ELIGIBLE_POOL_BLOCKING_DEAL_V1.json`,
`allocation-v1/A3_PREOUTCOME_ALLOCATION_RESULT_V1.json`.

## What would supersede this record

External curator packets validated by the frozen curator validator, or a new
governed successor record (v2) with its own preregistered rule; either lands
as new artifacts — this record and its outputs are never edited in place.
