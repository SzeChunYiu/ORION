# ORION-P3 public-reference Step-3 rescue status V1

**Date:** 2026-08-17  
**Issue:** #100  
**Route:** `P3.public-reference-mapping.v1`

## What is now implemented

The resource constraint is no longer treated as a requirement to commission a new paid annotation team. The repository contains an outcome-blind public-reference route that reuses independently produced public human/expert artifacts and refuses unsupported coordinates.

Implemented artifacts:

- `protocol/PUBLIC_REFERENCE_PROTOCOL_V1.json` — prospective, non-mutating protocol for the mapping/integration layer;
- `protocol/PUBLIC_REFERENCE_GOLD_V1.md` — gold-authority gates and interpretation boundary;
- `gold/PUBLIC_REFERENCE_AUTHORITY_POLICY_V1.md` — admissible vs forbidden authority;
- `gold/PUBLIC_REFERENCE_SOURCE_REGISTRY_V1.json` — pinned MUSE, SciSchema and SciFact authorities; SciER remains pointer-bound pending an immutable dataset pin;
- `gold/PUBLIC_REFERENCE_CASE_SCHEMA_V1.json` — machine-readable case/authority schema;
- `src/orion/study/p3_public_reference_build.py` — deterministic import/build layer for MUSE expert coreference, SciFact expert support/contradict labels and SciSchema versioned expert schemas;
- `src/orion/study/p3_public_reference.py` — deterministic ORION-vs-control mapping evaluation;
- `src/orion/study/p3_public_reference_analysis.py` — intervals, paired analysis and ablation analysis;
- `Makefile` targets for build, evaluation, analysis and isolated tests;
- three P3 public-reference unit-test modules;
- `CLAIM_LEDGER_V1.md` separating what this route can establish from end-to-end claims that remain `CANNOT_CHECK`.

## Authority boundary

No LLM-only proposal, simulated agreement, heuristic proxy or evaluated-system output is permitted to become gold. Unsupported scientific coordinates remain `UNRESOLVED`/`NOT_EVALUATED`.

This means the route can be executed with public data and ordinary compute while remaining scientifically auditable. It does **not** manufacture the original stronger end-to-end expert-gold claim.

## Issue #100 eligibility

This implementation makes the Step-3 item **"reuse MUSE/SciSchema/SciER annotations where task/license actually match rather than duplicating existing work"** substantively complete: reuse is now an executable data path with pinned authorities, not merely a recommendation.

The following remain intentionally unchecked until artifacts exist:

- a complete 32-case frozen atlas meeting final coverage gates;
- new ORION-specific two-annotator agreement;
- domain-expert adjudication of any newly interpreted specialist coordinate;
- the original V1 end-to-end raw-text experiment;
- real baseline/ablation outcome tables and figures.

## Next executable gate

Populate the builder from pinned upstream artifacts, run `make paper03-public-reference-build`, and inspect its fail-closed coverage report. If `READY_FOR_FREEZE`, bind the case-manifest/source-registry/evaluator hashes prospectively before evaluating any system output. If `CANNOT_CHECK`, expand only through additional externally authoritative public records; do not fill gaps with model guesses.
