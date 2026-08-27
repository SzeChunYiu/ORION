# ORION-13 Public-Reference Gold Authority Policy V1

**Status:** DESIGN_FROZEN, outcome-blind.  
**Protocol:** `ORION-13.public-reference-mapping.v1`  
**Purpose:** make Paper III executable without commissioning a new expert-annotation team while preserving a hard scientific authority boundary.

## Decision

The original `ORION-13.cross-domain-atlas.v1` remains unchanged. Its end-to-end expert-gold claim is still the stronger follow-up.

The resource-constrained route evaluates the **projection → mapping / GLUE-or-obstruction layer** using labels that already exist in public research artifacts. It is not allowed to turn an LLM guess, lexical heuristic, simulated annotator, or citation-count proxy into final gold.

A case is publishable only when the relation being scored has one of these authorities:

1. `UPSTREAM_EXPERT` — a label produced by an external expert annotation process.
2. `UPSTREAM_HUMAN` — a label produced by an external manual annotation process whose provenance is retained.
3. `DETERMINISTIC_STANDARD` — a relation that follows mechanically from a versioned standard/schema/identifier or exact conversion rule.
4. `DERIVED_FROM_ALLOWED` — a deterministic transformation of allowed labels, with the rule and inputs recorded.

The following are **never gold**:

- `LLM_PROPOSAL`
- `HEURISTIC_PROXY`
- `SIMULATED`
- `SELF_LABEL`

They may be used to discover candidate cases, but the candidate must be confirmed by allowed upstream authority before entering the frozen atlas.

## Why this removes the staffing blocker

The benchmark reuses already-funded annotation work instead of reproducing it. The frozen source registry currently points to:

- MUSE expert annotations;
- SciSchema expert-built multidisciplinary schemas;
- SciFact expert scientific claim/evidence labels;
- SciER manually annotated scientific entity/relation data.

ORION stores upstream revision + locator + content hash. It does not need to copy source text into this repository.

## Coordinate masking

Coverage is not purchased by inventing labels.

If a public source does not authoritatively determine a coordinate, that coordinate is `UNRESOLVED` / `NOT_EVALUATED` for the case. A headline metric may only read coordinates whose authority is allowed by this policy.

This is deliberately stricter than the previous pilot document, which proposed citation-count and other heuristic proxies for missing coordinates.

## Outcome blindness

Case construction and all derivation rules are frozen before evaluated-system outputs are inspected.

A selector may use:

- upstream labels;
- upstream dataset metadata;
- deterministic sampling keys;
- discipline/case-family quotas fixed in the protocol.

A selector may not use:

- ORION predictions;
- baseline predictions;
- error rates;
- downstream results;
- manual removal of cases after seeing system behavior.

## Source custody and licensing

Each case stores a `source_records` entry with:

- dataset/repository name;
- immutable revision;
- upstream locator;
- content hash;
- licence status when known.

Raw upstream text is not vendored by default. If redistribution rights are unclear, the case remains a pointer/hash record.

## Quality gates

A final atlas is invalid if any of the following is true:

- a scored expected relation has forbidden authority;
- a source record lacks an immutable locator or content hash;
- a derived label has no machine-readable derivation rule;
- a derivation rule begins with an LLM/heuristic authority source;
- final case selection depends on evaluated-system output;
- local synthetic fixtures are mixed into publication results;
- missing authority is silently converted into a negative label.

## What this route can and cannot claim

**Can claim, if results support it:** performance of ORION's typed mapping/integration semantics on externally grounded structured cases, including false-merge/false-split behavior and selected bridge/contradiction coordinates.

**Cannot claim from this route alone:** raw-text extraction superiority, retrieval superiority, provider/model superiority, universal construct-validity adequacy, or end-to-end downstream scientific benefit.

Those stronger claims remain `CANNOT_CHECK` until separately evidenced.
