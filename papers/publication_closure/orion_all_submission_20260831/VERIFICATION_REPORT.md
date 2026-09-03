# ORION-01--25 dual-route verification

> **SUPERSEDED 2026-09-03 — do not read this file as a pass.**
> The `PASS` below is the record of a full clean-build run written on 2026-09-01
> (`bf2a3575`). The gate has not been PASS since. Live result at supersession:
> **`FAIL`, 21/25** — `ORION-01` and `ORION-13` active-authority hash mismatch,
> `ORION-08` and `ORION-10` academic-paper-skills release authority mismatch.
> (CI run `33721708560`, head `3fe35fb2`, reported 20/25; the `ORION-02`
> active-authority rebind landed with this notice restores 21/25.)
> Three further checks show the record is stale on its own terms: the recorded
> `builder_sha256` no longer matches `build_all_submission_materials.py`, four of
> the twenty-five per-paper `manifest_sha256` values are stale (`ORION-02`,
> `ORION-03`, `ORION-08`, `ORION-10`), and in the `SzeChunYiu/ORION-paper` mirror
> the per-paper package paths do not resolve at all.
> The rows below are retained unchanged as the historical record of that run.
> See the `superseded` block in `VERIFICATION_REPORT.json` for the regeneration
> requirement.

**Aggregate:** `SUPERSEDED` (record: `PASS`, 2026-09-01)  
**Packages checked:** 25/25  
**Global checks:** 4  
**Verifier:** `fa406fd3823563a6cd1a97d4798ac167829d1060456016c1582f38900b300d23`

| Paper | Result | arXiv pages | Journal pages | Overfull boxes |
|---|---:|---:|---:|---:|
| ORION-01 | PASS | 12 | 12 | 0 |
| ORION-02 | PASS | 7 | 7 | 0 |
| ORION-03 | PASS | 14 | 14 | 0 |
| ORION-04 | PASS | 5 | 5 | 0 |
| ORION-05 | PASS | 7 | 7 | 0 |
| ORION-06 | PASS | 6 | 6 | 0 |
| ORION-07 | PASS | 9 | 10 | 0 |
| ORION-08 | PASS | 9 | 7 | 0 |
| ORION-09 | PASS | 7 | 7 | 0 |
| ORION-10 | PASS | 7 | 7 | 0 |
| ORION-11 | PASS | 48 | 41 | 0 |
| ORION-12 | PASS | 29 | 29 | 0 |
| ORION-13 | PASS | 9 | 9 | 0 |
| ORION-14 | PASS | 12 | 12 | 0 |
| ORION-15 | PASS | 38 | 33 | 0 |
| ORION-16 | PASS | 7 | 8 | 0 |
| ORION-17 | PASS | 7 | 7 | 0 |
| ORION-18 | PASS | 9 | 9 | 0 |
| ORION-19 | PASS | 8 | 8 | 0 |
| ORION-20 | PASS | 9 | 9 | 0 |
| ORION-21 | PASS | 8 | 8 | 0 |
| ORION-22 | PASS | 7 | 6 | 0 |
| ORION-23 | PASS | 7 | 7 | 0 |
| ORION-24 | PASS | 6 | 6 | 0 |
| ORION-25 | PASS | 12 | 12 | 0 |

The verifier checks exact registry coverage, active-authority and terminal bindings,
manifest/checksum closure, safe archives, top-level arXiv source, clean builds,
PDF text parity, resolved references, route-specific files, personal-metadata
consistency, double-blind identity partitions, and retention of every registered
null, adverse, refuted, open, or CANNOT_CHECK result.

Overfull-box counts are reported for visual follow-up; undefined references or
citations fail verification.
