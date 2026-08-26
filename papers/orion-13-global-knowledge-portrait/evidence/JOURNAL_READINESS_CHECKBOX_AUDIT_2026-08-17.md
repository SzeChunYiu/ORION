# P3 journal-readiness checkbox audit vs `origin/main`

**Date:** 2026-08-17  
**Issue:** #100  
**HEAD audited:** `origin/main` at audit time (worktree `cursor/paper-100` was equal to `origin/main` before this docs change)  
**Not in scope:** issue #280 V2 gold; PR #269 Phase-3 prefreeze

Method: `git show origin/main:<path>`, SHA-256 of jsonl bytes, `git ls-tree`, GitHub Actions run list. No gold labels were invented.

## Gold freeze (the #270 job)

| Item | Expected | Observed on `origin/main` | Verdict |
|---|---|---|---|
| Initial `PUBLIC_REFERENCE_GOLD_V1.jsonl` | 32 lines, SHA-256 `35f9e39b75ff53b7f0ec82cd03ebcaaa82509ee0aea3f5b96aac3fd62c854ed8` | 32 lines, hash match | **TICK** V1 portable gold |
| Confirmatory jsonl | 32 lines, SHA-256 `13a76c68c149c2552f3543babeca6e1ad5afe23c45ea9c0dc365c1445cf2782b` | 32 lines, hash match, 0 case-id overlap with initial | **TICK** V1.1 holdout |
| `evidence/public-reference-v1/SHA256SUMS` | gold hash line | contains `35f9e39b…54ed8  artifacts/frozen/PUBLIC_REFERENCE_GOLD_V1.jsonl` | **TICK** custody |
| `evidence/public-reference-v1.1-confirmatory/SHA256SUMS` | gold hash line | contains `13a76c68…2782b  artifacts/frozen/PUBLIC_REFERENCE_GOLD_V1.jsonl` | **TICK** custody |
| `PROVENANCE.env` (both archives) | present, pinned MUSE/SciSchema/SciFact SHAs | both present | **TICK** |
| `gold/adjudicated/*.json` | 32 eight-family records | 32 `P3.*.gold.json`, annotator `seed-to-gold-v1` | **DO NOT TICK as expert gold** |
| `gold/annotations/annotator-a/` and `annotator-b/` | independent labels | 0 files | **CANNOT_CHECK** |

PR #270 mixed the seed JSON files with the public-reference jsonl when ticking “actual gold labels for all 32 samples (24 core + 8 margin)”. That mix is rejected here.

## `JOURNAL_READINESS.md` after this pass

| Section | Ticked this pass | Left open / corrected |
|---|---|---|
| 1 Novelty | all 7 | — |
| 2 Hypotheses | freeze H1 + margin | H2–H4 remain secondary |
| 3 Sampling/schema design | already ticked (design) | quality execution boxes for dual annotators/IAA/expert review **unticked** (were overclaimed) |
| 3 Expert-gold execution | — | all five remaining expert boxes `CANNOT_CHECK` |
| 3 Public-reference freeze | jsonl hashes, SHA256SUMS, PROVENANCE.env | seed JSON not promoted |
| 4 Baselines | flat predicate canonicalization (narrow) | vanilla synthesis, RAG, translation, SCOPE/SCION, schema-contract |
| 5 Metrics | false merge + false split (public-reference only) | contradiction, recoverability, downstream, IAA, cost |
| 6 Plots P3-1..P3-7 | — | all original figures/tables; PR3-F1..F3 are substitutes only |
| 7 Manuscript | all except stage-error attribution | stage extraction vs mapping vs integration |
| 8 Reproducibility | handbook, public-reference gold+provenance, publication scripts, eval path, mapping replay | shareable eight-family spans, baseline prompts, raw portraits |

## Issue #100 alignment

Steps 1, 2, 3R, 3C and most of Step 8 were already ticked on the issue. This pass does **not** tick original Step 3 case-family / dual-annotator boxes, Step 4 raw-text baselines, Step 6 P3-1..P3-7, Step 10, or any V2 box from later comments.
