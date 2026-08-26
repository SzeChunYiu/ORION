# File Index — gold/

| File | Status | Description |
|------|--------|-------------|
| `SAMPLE_MANIFEST_SEED_V1.json` | ✓ SEED | 32 seed entries across 8 case families, 4 disciplines |
| `SAMPLE_MANIFEST_V1.json` | ✓ SEED | JSON Schema for manifest format |
| `annotate.py` | ✓ | Annotation CLI tool (list, annotate, validate, adjudicate, stats) |
| `GOLD_ATLAS_FREEZE_V1.json` | ✓ | Freeze manifest (content hashes, coverage, validation status) |
| `GOLD_METHODOLOGY_V1.md` | ✓ | Gold construction methodology, limitations, and recovery path |
| `README.md` | ✓ | Dataset documentation |
| `MANIFEST.md` | ✓ | This file (index) |
| `CORPUS_DESIGN_V1.md` | ✓ | Corpus design rationale |
| `DISCIPLINE_SELECTION_V1.md` | ✓ FROZEN | Three-discipline selection + case-family coverage (Issue #158) |
| `ANNOTATION_SCHEMA_V1.md` | ✓ FROZEN | Annotation schema, double-annotation procedure, agreement targets, expert escalation |
| `OAEI_TRACK_LICENSE_MANIFEST_V1.json` (+ `.md`) | ✓ FROZEN | OAEI/SemTab licence + selection record, pre-download (Issue #1086 ORION-13 box 1) |
| `check_oaei_track_license_manifest_v1.py` | ✓ | Checker for the licence manifest and its bound analysis freeze (exit 0/1/2) |

## Coverage Matrix

32 samples: 4 disciplines × 8 samples each, covering all 8 case families.

All samples are SEED placeholders with retrieval_hints. Final gold requires
replacing these with verified open-access source spans.

**Design docs frozen:** `DISCIPLINE_SELECTION_V1.md` and `ANNOTATION_SCHEMA_V1.md`
define the three-discipline selection (biomed, physics, social + climate margin),
the annotation schema for all 8 case families, the double-annotation procedure
(2 independent labels on 24 core samples), per-coordinate agreement targets, and
the domain-expert escalation policy (Issue #158). Actual gold labels are produced
only after these docs are frozen and before any system-output inspection.

## Protocol Files (referenced)

| File | Status |
|------|--------|
| `protocol/ANNOTATION_SCHEMA_V1.json` | ✓ Frozen |
| `protocol/ANNOTATION_HANDBOOK_V1.md` | ✓ Frozen |
| `protocol/ADJUDICATION_POLICY_V1.md` | ✓ Frozen |
| `protocol/CORPUS_DESIGN_V1.md` | ✓ Frozen |
| `protocol/OAEI_MULTI_CASE_ANALYSIS_FREEZE_V1.json` (+ `.md`) | ✓ Frozen — pre-execution analysis contract (Issue #1086 ORION-13 boxes 2-5) |
| `protocol/PROTOCOL_V1.json` | ✓ Frozen |
| `protocol/SAMPLE_MANIFEST_V1.json` | ✓ Frozen |

## Frozen Artifacts (checked in)

| File | Description |
|------|-------------|
| `GOLD_ATLAS_FREEZE_V1.json` | Freeze manifest — coverage, validation status, source-span status, two-annotator status |
| `GOLD_METHODOLOGY_V1.md` | Gold construction methodology, limitations, and recovery path |
| `adjudicated/` | 32 schema-validated adjudicated gold records |

## Target Files (still pending)

| File | Description |
|------|-------------|
| `annotations/annotator-a/` | Independent annotator-a label set (PENDING — external blocker #100) |
| `annotations/annotator-b/` | Independent annotator-b label set (PENDING — external blocker #100) |
| `REPRODUCIBILITY.md` | Data reproduction checklist (PENDING — blocked on corpus commitment) |