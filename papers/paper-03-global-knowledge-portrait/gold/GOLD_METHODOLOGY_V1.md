# P3 Gold Atlas — Construction Methodology (V1)

## Status: SEED-PLACEHOLDER

This document describes how the P3 cross-domain annotation gold atlas was constructed.
It is a companion to the **[GOLD_ATLAS_FREEZE_V1.json](GOLD_ATLAS_FREEZE_V1.json)** freeze manifest.

---

## 1. Overview

The gold atlas comprises **32 adjudicated annotation records** (4 disciplines × 8 case families),
frozen against the schema `orion.p3.annotation.v1` defined in
[protocol/ANNOTATION_SCHEMA_V1.json](../protocol/ANNOTATION_SCHEMA_V1.json).

Each record carries 11 coordinates (referent, construct, measurement, context, polarity,
modality, attribution, discourse, mapping, contradiction, integration) plus preservation
conditions, recoverability targets, and source span metadata.

## 2. Construction Pipeline

### 2.1 Seed manifest design

The source of truth is `SAMPLE_MANIFEST_SEED_V1.json`, which defines 32 sample entries
with:

- **Document IDs** using SEED placeholders (e.g. `pmc:SEED-BIOMED001A`) — these are NOT
  verified open-access source spans but synthetic identifiers.
- **Text hashes** using `seed:sha256:...` — placeholder values, not real content hashes.
- **Retrieval hints** describing the intended source.
- **Gold hints** in the `notes` field, containing the annotator's intended labels.

### 2.2 Gold template generation

The `generate_gold.py` script defines a `GOLD_BY_CASE` dictionary mapping each of the 8
`case_family` strings to a complete set of 11 coordinate labels plus preservation
conditions, contradiction verdict, and integration verdict. These templates were derived
from the SEED manifest notes and the frozen annotation handbook.

For each sample in the manifest, `generate_gold.py`:
1. Reads the manifest entry.
2. Looks up the `GOLD_BY_CASE` template for the sample's `case_family`.
3. Builds a full annotation record with source spans, coordinates, and metadata.
4. Validates the output against the schema (required fields, enum values).
5. Writes to `adjudicated/{sid}.gold.json`.

### 2.3 Annotator identity

All 32 gold records carry the annotator ID `seed-to-gold-v1` and annotation round
`ADJUDICATION`. There are **no independent annotator-a / annotator-b pairs** — the
"adjudication" round was applied directly from the template rather than resolving
differences between independent labels.

## 3. Known Limitations

### 3.1 No independent inter-annotator agreement

The protocol requires two independent initial labels on a substantial shared subset
with coordinate-level agreement (`annotation_agreement_by_coordinate` in
`src/orion/study/metrics.py`). As of this freeze:

- **Annotator-a files on disk: 0**
- **Annotator-b files on disk: 0**
- **Coordinate-level agreement computable: False**

Per the owner's governance decision on issue #158[^1], coordinates requiring
independent labelling remain **CANNOT_CHECK** and are recorded in issue #100 as an
external blocker. This fork does not manufacture a second annotator or adjudicate
fabricated disagreement.

### 3.2 SEED-placeholder source spans

All 64 source spans (32 samples × 2 sources) use SEED placeholder document IDs
(e.g. `pmc:SEED-BIOMED001A`) and placeholder text hashes (`seed:sha256:...`). The
annotation corpus is not committed to git and cannot be regenerated from a fresh
checkout. Verified open-access source spans are required before the gold atlas can
support real-world construct-validity claims.

### 3.3 Annotation corpus is untracked

The raw annotation corpus (from which the gold records were derived) does not exist
in this repository. A fresh checkout of the repository produces the adjudicated gold
records via `generate_gold.py` but cannot reproduce the source corpus or the
independent label sets. The owner's recommended disposition on issue #158 is to
record this as an external blocker in issue #100.

## 4. What Is Frozen

| Artifact | Frozen | Status |
|----------|--------|--------|
| Annotation schema (`ANNOTATION_SCHEMA_V1.json`) | ✓ | Frozen |
| Annotation handbook (`ANNOTATION_HANDBOOK_V1.md`) | ✓ | Frozen |
| Adjudication policy (`ADJUDICATION_POLICY_V1.md`) | ✓ | Frozen |
| Protocol (`PROTOCOL_V1.json`) | ✓ | DESIGN_FROZEN |
| Seed manifest (`SAMPLE_MANIFEST_SEED_V1.json`) | ✓ | SEED |
| 32 adjudicated gold records (`adjudicated/*.gold.json`) | ✓ | All schema-validated |
| Freeze manifest (`GOLD_ATLAS_FREEZE_V1.json`) | ✓ | This file |
| Independent annotator-a/b label sets | ✗ | External blocker (#100) |
| Verified open-access corpus | ✗ | External blocker (#100) |
| Coordinate-level agreement metric | ✗ | Not computable without (a) |

## 5. Recovery

If the external blockers are resolved (independent annotations obtained for a shared
subset), the recovery path is:

1. Place annotator-a files in `gold/annotations/annotator-a/` and annotator-b files in
   `gold/annotations/annotator-b/`.
2. Run `annotation_agreement_by_coordinate(gold, gold)` via `src/orion/study/metrics.py`.
3. If agreement ≥ threshold, run `generate_gold.py` with the `--independent-labels` flag
   (or the equivalent adjudication workflow) to produce a fresh adjudicated set.
4. Update the freeze manifest and re-register content hashes.

---

[^1]: Issue #158, owner comment 2026-08-16T22:51:40Z (IC_kwDOT5fCLM8AAAABPIFd8A):
      "Two independent initial labels on a substantial shared subset and
      coordinate-level agreement. annotator-a files: 32, annotator-b files: 0,
      adjudicated gold: 32, agreement computable on real data: False."
      Recommended disposition: coordinates needing independent labelling stay
      CANNOT_CHECK, recorded in #100 as external blocker.