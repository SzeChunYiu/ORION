# ORION-ORION-13 public-reference gold authority route V1

**Status:** DESIGN_FROZEN, outcome-blind addendum to `ORION-13.public-reference-mapping.v1`.

## Purpose

ORION-ORION-13 does not require a newly commissioned paid annotation team if equivalent scientific authority already exists in public human/expert resources. The requirement is stronger and simpler: every scored gold coordinate must be independently authoritative, reproducible, source-addressable, and frozen before evaluated-system outputs.

This addendum therefore permits reuse of pinned public human/expert annotations and deterministic transformations of those annotations. It does not permit model consensus, simulated agreement, heuristic proxies, or evaluated-system output to create gold authority.

## Allowed authority

A scored coordinate must be one of:

- `UPSTREAM_EXPERT` — directly normalized from a pinned public expert annotation/schema;
- `UPSTREAM_HUMAN` — directly normalized from a pinned public human annotation;
- `DETERMINISTIC_STANDARD` — fixed by a versioned scientific/technical standard with exact locator;
- `DERIVED_FROM_ALLOWED` — a deterministic, documented derivation whose inputs are all allowed-authority facts.

Anything else is `UNRESOLVED` / `NOT_EVALUATED`.

## Pinned authorities

The canonical source registry is `gold/PUBLIC_REFERENCE_SOURCE_REGISTRY_V1.json`. At minimum the current route binds:

- MUSE expert annotations at `cohentsofia/MUSE@f7a40317db46145d0c90b221311d8324db5da1b9`;
- SciSchema expert schemas at `scischema/scischema@55b6197cdb0b66c3123df16d0b0c70b02c4bde8b`;
- SciFact expert SUPPORT/CONTRADICT annotations at `allenai/scifact@68b98a56d93e0f9da0d2aab4e6c3294699a0f72e` plus the release data downloaded by the pinned upstream script;
- SciER only when its exact dataset artifact/license is content-bound in the registry.

## Freeze gates

`PUBLIC_REFERENCE_GOLD_FROZEN` requires all of:

1. target case count reached by an outcome-blind deterministic sampler;
2. at least three scientific/domain strata represented;
3. both merge-compatible and non-merge authoritative cases present;
4. every case validates against `PUBLIC_REFERENCE_CASE_SCHEMA_V1.json`;
5. every source record carries immutable revision, locator and content hash;
6. every expected relation carries allowed authority and evidence locators;
7. no `LLM_PROPOSAL`, `HEURISTIC_PROXY`, `SIMULATED`, `SELF_LABEL`, or evaluated-system output appears in gold authority;
8. exact case-set hash, source-registry hash, evaluator revision and split identity recorded before system evaluation;
9. deterministic rebuild reproduces the semantic case-set hash;
10. independent replay can re-resolve the source locators and derivations.

Failure of a gate is `CANNOT_CHECK`, never success.

## Scope boundary

This route evaluates the projection-to-mapping/integration semantics that can be grounded in public authority. It does not silently claim end-to-end raw-text extraction quality, provider quality, retrieval quality, or universal cross-domain adequacy. Those stronger claims remain separately `CANNOT_CHECK` until corresponding evidence exists.
