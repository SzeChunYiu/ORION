# P12 tuning-eval instrument finding — 2026-09-03 (pre-amendment codex pass)

Finding class: INSTRUMENT_VALIDATION (measurement infrastructure), recorded
before any tuning binding and before any protected model call. This file is
the evidence base for `P12_HARNESS_AMENDMENT_DATASET_MOUNTPOINT_V1.json`.

## What was measured

LUNARC sbatch job 3570675 (`p12-eval-tune`, 41m20s, exit 0) evaluated all 68
codex-lane tuning run records (6 families x 17 instances x 4 actions) through
the pinned upstream evaluator, unmodified:

    {"phase": "tuning", "expected_cells": 136, "done": 67,
     "skipped_existing": 1, "failed": 0}

The evaluator itself ran correctly end to end (validated earlier the same day
by eval-path smoke 3570240 and judge-path smoke 3570445).

## Result

0/68 successes. Failure taxonomy over the 68 eval records:

- 43 `FileNotFoundError` on input dataset paths
- 24 geo/raster IO errors on input dataset paths
  (pyogrio/rasterio "No such file or directory")
- 1 program `SyntaxError`
- 0 judge calls (no program produced judgeable output)

Every IO failure is the same class: the program references a dataset path
exactly as the frozen prompt's `DATASET TREE` presents it (for example
`sea_surface_temperature/sst_anom.nc`, or an invented absolute path ending in
`.../ScienceAgentBench/EOF_standard/hgt_djf.nc`), while the evaluator mounts
datasets at `./benchmark/datasets/<dataset>/...` relative to the repo root.
The pinned upstream gold programs use the prefixed form; the upstream
annotation sheet (`dataset_folder_tree` in the frozen parquet) and therefore
the frozen terminal template do not state the mount point.

## Why this is an instrument defect, not a model-capability result

1. The frozen terminal template asked for "one complete, self-contained
   Python program" but never disclosed the working-directory data-mount
   convention. The campaign's lanes are single-turn non-interactive CLIs with
   no repository access, so the mount point is undiscoverable in principle.
2. The harness's own design intent was that the S1 state artifact carry
   "shared data schemas, file conventions, and reusable facts" — but S1's
   input is the same unprefixed trees, so no action arm could ever acquire
   the convention. All four arms are equally path-blind, which collapses the
   tuning matrix toward zero and makes threshold fitting vacuous.
3. Upstream ScienceAgentBench agents are interactive (shell access inside the
   repo); one directory listing yields the mount convention. Withholding it
   from single-turn lanes measures path guessing, not the state/reasoning
   treatment the campaign is testing.

## Disposition (per freeze successor rules — 0 protected calls at all times)

- The 68 pre-amendment run records and 68 eval records are archived under
  `runs/tuning-archive-pre-mountpoint-amendment-20260903/` and
  `eval/tuning-archive-pre-mountpoint-amendment-20260903/` on the execution
  host; they are retained as this finding's evidence.
- `P12_HARNESS_AMENDMENT_DATASET_MOUNTPOINT_V1.json` amends the terminal
  template with a one-sentence mount-point disclosure, uniform across arms
  and lanes, before any binding and before any protected call.
- Both lanes' tuning phases rerun from scratch under the amended template;
  no thresholds, families, splits, identities, scoring, or evaluator bytes
  change.
