# R0 Frozen-Manifest Path Corruption — Defect Report & Repair (DES-CENSUS-01)

**Date:** 2026-08-27
**Status:** REPAIRED (byte-restore, git-verified)
**Machine receipt:** `R0_PATH_REPAIR_RECEIPT_V1.json` (same directory)
**Repair scripts:** `repair_r0_path_corruption_V1.py` (inference layer), `verify_and_restore_r0_v2.py` (restore layer)

## 1. Defect

The R0 namespace-unification wave (commit `3a1a8317`, PR #1474, 2026-08-27 00:40 +0200)
mechanically rewrote old→new paper-directory name strings in **every scanned text file**,
including five **frozen** DES-CENSUS-01 artifacts whose evidentiary pins
(`subject_commit`, `subject_tree`, blob oids) remained at the pre-R0 world:

| Artifact | Corrupted path strings | Replacement sites |
|---|---|---|
| `RAW_MANIFEST_V1.json` | 2,759 unique | 5,456 |
| `LABEL_CENSUS_V1.json` | 2,161 unique | 23,901 |
| `RESULT_BINDING_PACKET_V1.json` | 2,721 unique | 2,721 |
| `UNCLASSIFIED_BLOCKER_ATLAS_V1.json` | 1,341 unique | 6,259 |
| `RESOURCE_LEDGER_V1.json` | 1 unique | 1 |

Consequence: the frozen records named `papers/orion-XX-…` paths that do not exist in
the tree they claim to have censused (`subject_commit=3c97b87f`, 2026-08-25 19:29,
`subject_tree=ec9455cc`, 11,434 entries, old `paper-XX`/`theory-X` names). Any consumer
resolving frozen references against the pinned tree would fail or — worse — silently
resolve against the post-R0 working tree, breaking the freeze contract.

Corruption classes found (standalone strings **and** paths embedded in larger strings —
`ARTIFACT:papers/…` ids, `json_key=… value=…` annotation records, prose snippets):
directory renames (`paper-09-…`→`orion-19-…`, `theory-C-…`→`orion-02-…`), merges into
`orion-01-certificate-realization`, file-level archive moves
(`papers/FIVE_PAPER_…md`→`papers/archive/2026-08-pre-unification/…`), and the
`QG-paper-03-intrinsic-support-numbers`→`candidates/qg-paper-03-stub` stub move.

## 2. Evidence chain

1. **Git history:** each artifact was created 2026-08-25 (`1c645f74` census execution,
   or `9f957d9d` for the binding packet) and touched afterwards **only** by R0
   (`git log -- <file>` = creation + R0, nothing else).
2. **Layer-1 inference:** inverse-R0 transform + blob-oid verification + bijection
   closure resolved **2,721/2,721** missing `file_rows` paths (2,712 transform, 9
   bijection) into the subject tree with exact oid equality; the mapping covers every
   unclaimed subject-tree path exactly (the census enumerates the subject tree
   bijectively — 11,434 rows = 11,434 tree entries).
3. **Layer-2 ground truth:** applying the forward R0 rename map — taken from R0's own
   recorded file renames (`git diff --name-status -M 3a1a8317^ 3a1a8317`), not from
   prose — to the original pre-R0 bytes reproduces the post-R0 bytes **exactly**. This
   proves R0's edit on these files was precisely the mechanical rename rewrite and
   nothing else (R0's `rebind.hand_edits` lists no census file).

## 3. Repair

Byte-restore: each artifact was restored to the exact bytes of its last pre-R0 commit
(per-file commit + sha256 in the receipt). This restores standalone paths, embedded
paths, ids, and annotation strings alike. Freeze pins were never touched:
`subject_commit`, `subject_tree`, and all blob oids are pre-R0 and remain so;
`freeze_sha256` hashes `FREEZE_V1.json`, which contains no `papers/` paths and was not
modified by R0 — the freeze pin therefore stays valid and now matches the restored
bytes again.

## 4. Post-repair invariants (all pass)

- `RAW_MANIFEST_V1.json`: 11,434/11,434 `file_rows` paths exist in `subject_tree`
  `ec9455cc` with exact oid match; every `occurrence_rows.file_refs` `[path, oid]` pair
  matches a `file_rows` row.
- All five files byte-identical to their last pre-R0 commits (sha256 in receipt).

## 5. Blast radius beyond DES-CENSUS-01

A full `research/**` sweep (same corrupt-reversible criteria: file created pre-R0,
touched afterwards only by R0, path strings rewritten while evidentiary pins stayed
pre-R0) found the damage extends well past this family:

- **21 further corrupt-reversible JSON artifacts** across other DES result families
  (FREEZE_V1.json, receipts, ledgers) — every one reversible as a pure R0 name rewrite.
- **5 `.py` scripts** carrying the same rewritten path strings.
- **`DES-SATURATION-01/FREEZE_V1.json` is corrupt** (3 rewritten `papers/` strings) —
  an earlier "clean" read of this file was a display-escaping artifact and is retracted.
- **`DES-NOVELTY-01/CLAIM_ATOMS_V1.json` is corrupt, not legitimate** (corrects this
  report's first edition): git history shows it was created 2026-08-25 20:37
  (`6f45f713`, "freeze: external novelty review contract") with `paper-XX` paths and
  pin `subject_revision=3c97b87f`, then touched **only** by R0. Its 75 `papers/`
  strings now name `orion-XX` paths absent from its own pinned revision — the same
  freeze-contract break as the census five. An earlier "legitimate post-R0 artifact"
  classification (based on `subject_revision` pin semantics alone) is withdrawn.
- **Census-scrape files are do-not-repair**: they are live post-R0 re-derivations, not
  frozen pre-R0 records.

Batch repair of the 21 + 5 + DES-SATURATION + DES-NOVELTY set follows as a separate
PR using the generalized verifier; each file is admitted only through the same
forward-vocabulary byte-equality gate used here.

## 6. Prevention

R0's rewrite honored no freeze boundary. Any future namespace wave must exclude
artifacts carrying a freeze pin (or must re-derive and re-pin them explicitly); the
freeze contract should grow a guard that fails when an artifact's referenced paths
diverge from its pinned subject tree.
