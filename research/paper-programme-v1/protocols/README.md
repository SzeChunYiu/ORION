# ORION publication protocol assets

This directory contains **prospective, outcome-blind** protocol infrastructure for Papers P1–P5. It exists to make Gate 3 (prospective freeze), Gate 6 (pre-specified figures/tables) and Gate 7 (reproducible artifact) executable without pretending that missing external evidence already exists.

## Status model

A paper protocol may be:

- `DESIGN_FROZEN`: hypotheses, task families, metrics, baselines, ablations, exclusion rules, statistics and figure/table definitions are fixed, but one or more external identities (dataset hash, provider/model revision, evaluator hash, final subject commit) are not yet bound.
- `EXECUTION_FROZEN`: every identity required for the final run is content-addressed/frozen before test-outcome access.
- `OUTCOME_ACCESSED`: the final run has begun or its outcomes have been inspected. Any design change after this point creates a new protocol version and leaves the old version immutable.
- `INVALIDATED`: a protocol/run cannot support a publication claim because a prospective or integrity requirement was violated.

`DESIGN_FROZEN` is useful progress but is **not** external evidence and does not close Gate 3 by itself.

## Non-negotiable rules

1. The protocol is frozen before final test outcomes are inspected.
2. Exact subject revision, evaluator, datasets/splits, provider/model/tool versions and baseline configurations must be bound before `EXECUTION_FROZEN`.
3. Failed, null and harmful runs remain in the artifact.
4. Public-benchmark web/search access is declared prospectively and contamination is measured when applicable.
5. Hidden labels/answers stay outside candidate custody.
6. A post-outcome protocol change creates `v2` (or later); never rewrite `v1` to fit the result.
7. Result-bearing plots/tables are generated from raw archived result records, never from manually transcribed numbers.
8. The execution freeze itself is content-addressed and committed before the first final outcome is inspected.

## Files

- `PUBLICATION_PROTOCOL_SCHEMA_V1.json` — machine-checkable common protocol fields.
- `RUN_MANIFEST_SCHEMA_V1.json` — exact subject/data/model/baseline/evaluator/split/resource/environment identity for one prospective final run.
- `RESULT_RECORD_SCHEMA_V1.json` — normalized raw result record shape.
- `ANALYSIS_STANDARD_V1.md` — common statistical and reporting rules.
- `EXECUTION_FREEZE_CHECKLIST_V1.md` — exact transition from design freeze to publication-authorizing execution freeze.
- `publication_manifest.py` — canonical JSON hashing plus protocol/run-manifest state validation; rejects execution freezes with unresolved `UNBOUND` identities.
- `publication_stats.py` — dependency-free precision/CI/bootstrap utilities for preregistration and headline tables.
- `publication_svg.py` — dependency-free SVG bar/scatter/heatmap rendering from frozen summaries.

Each paper owns a `protocol/` directory containing its exact design-freeze protocol and paper-specific schemas/policies.
