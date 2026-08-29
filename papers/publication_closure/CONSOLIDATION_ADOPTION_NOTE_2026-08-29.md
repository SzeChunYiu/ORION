# What was adopted from `chatgpt/all-paper-consolidation-authoritative-20260828`, and what was refused

Issue #1701 lists this branch under **ADOPT FIRST** for ORION-15. Checked before adopting.

## Scope of the branch

154 files differ from the merge-base (`2b912e727`). Against `main` `344c1225c`, per-file
three-way blob test:

| | files |
|---|---:|
| already identical to `main` | **145** |
| genuinely diverged | **9** |

So ~94% of this branch is already absorbed. Note also that seven sibling branches
(`-final`, `-openpr`, `-pr`, `-ready`, `-review`, `-submit`, `-validation`) share this
branch's exact tree `e785b867e6c4`; they are one lineage, not seven.

## Adopted (3 files — present here, absent from `main`)

- `ALL_PAPER_CONSOLIDATION_STATUS_2026-08-28.json`
- `ALL_PAPER_CONSOLIDATION_STATUS_2026-08-28.md`
- `CODEX_CLAUDE_CONSOLIDATION_RECEIPT_2026-08-28.json`

Adopted verbatim. They are coordination/custody records that declare
`scientific_authority_delta: NONE` and state their own base (`main@2b912e727`), so they
create no claim and are self-dating. Later work supersedes individual rows in the status
table; the file is kept as the historical record it says it is.

## Refused (2 files — adopting them would delete evidence `main` holds)

**`papers/orion-02-.../r23-density-backoff-revival/ORION02_REVIVAL_ATTEMPT_LEDGER_V1.jsonl`**
`main` has 13 records; the branch has 5. Keyed comparison:

- branch records: `ORION02-HISTORICAL-R22`, and 4× `ORION02-REVIVAL-001-R23-HAMMING-K2`
- on `main` and absent from the branch: **8× `ORION02-REVIVAL-002-R24-ARM-CONDITIONAL-BOUNDARY-FIBRES`**
- on the branch and absent from `main`: **none**

The branch predates the R24 revival round. It has nothing to contribute to this file and
would delete the entire R24 attempt record. A revival ledger is precisely where negative
and superseded attempts are supposed to survive.

**`papers/orion-18-.../CONTENT_MANIFEST_V2.json`**
`main` binds 86 files, the branch 85. The single difference is
`rewrite_academic_pipeline/MANUSCRIPT_REWRITE_V1.md`, which `main` binds and the branch
does not — this branch predates the additive wave1 binding (#1712). Adopting it would
re-open the `sync` failure that fix closed. Both carry the same `subject_commit`
(`d6a1e08f4`), so the branch is simply older, not an alternative.

## No-ops (4 files)

`SHA256SUMS`, `CLOSURE_MANIFEST.json`, `PUBLICATION_MANIFEST_SHA256.txt` and
`HF_MATHLIB_TACTICS_SAMPLE.json` differ from the merge-base on both sides but carry no
content `main` lacks.

## Rule this illustrates

"Differs from the merge-base" is not "is newer". Every file here was classified by
comparing branch, `main` and merge-base blobs, which is what separated three real
contributions from two silent regressions in the same branch.
