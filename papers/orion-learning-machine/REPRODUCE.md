# Reproduce the bounded P9/P10 closure

**Papers:** `../paper-xx-executable-research-core/` and
`../paper-xx-content-bound-math-evaluation/`

**Authority:** `LOCAL_REPRODUCIBLE_CORE_ONLY`. Identity, deterministic outputs
and local hostile gates are in scope. External novelty, theorem-statement
faithfulness, scientific authority and journal acceptance are not.

## Quick current closure

```bash
./VERIFY_LOCAL_CLOSURE.sh
```

This checks the current publication manifest, all shared framework tests, the
P9 merged-evidence gate and the P10 merged technical-note gate. It supersedes
the unavailable delivered `LOCAL_CORE_COMPLETE` assertion, which referenced
missing `CLOSURE_MANIFEST.json` and
`closure_logs/FROZEN_SHA256SUMS.txt`. The exact replacement authority and its
exclusions are in `LOCAL_CLOSURE_AUTHORITY.json`.

`SCRIPT_MANIFEST_SHA256.txt` remains a historical receipt for the 36 files as
delivered at commit `bbe178d`; it is not the current publication manifest.

## Environment

The recorded Python result environment is CPython 3.13, NumPy 2.4.4, SymPy
1.14.0 and scikit-learn 1.8.0. The framework package imports its competence
module eagerly, so the framework tests and Phase 2A replay require NumPy and
scikit-learn even though Phase 2A's own tactic parser does not use them. The
ASlib replay also requires NumPy/scikit-learn.

## Full local experiment replay

```bash
./REPRODUCE_LOCAL_CLOSURE.sh
```

The script runs the current closure plus deterministic phase 0, corrected phase
1 V2 and archival phase 2A. It intentionally does not call the legacy Phase-2B
runner: `HF_MATHLIB_TACTICS_SAMPLE.json` was not delivered, so that question is
removed from the P10 technical note and retained only as a triggered follow-up.

## Public P9 discriminator

```bash
python ../paper-xx-executable-research-core/benchmark/test_aslib_v1.py
python ../paper-xx-executable-research-core/benchmark/run_aslib_v1.py
python ../paper-xx-executable-research-core/check_merged_ready.py
```

The source-pinned `SAT11-HAND-ALGO` output is deterministic. P9 closes as a
merged P8/programme evidence object, not a standalone routing novelty claim.

## Programme-scale P10 study

```bash
python ../paper-xx-content-bound-math-evaluation/benchmark/check_mathlib_corpus_v2.py
python ../paper-xx-content-bound-math-evaluation/benchmark/test_mathlib_transfer_v2_1.py
python ../paper-xx-content-bound-math-evaluation/check_technical_note_ready.py
```

The native replay requires the exact Mathlib commit and Lean 4.34.0-rc1; its
command and runtime-adapter boundary are documented in P10's
`JOURNAL_READINESS.md`. The stored receipts claim native acceptance only for the
eight prospectively selected audit subjects.

## Supported terminals

- P9: `MERGE_P9_INTO_P8_PROGRAMME`.
- P10: `TECHNICAL_NOTE_MERGED_INTO_P4_P8_PROGRAMME`.

Neither terminal promotes capability, a digest or a Lean exit status into
execution authority, theorem faithfulness or scientific truth.
