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

## Coverage Matrix

32 samples: 4 disciplines × 8 samples each, covering all 8 case families.

All samples are SEED placeholders with retrieval_hints. Final gold requires
replacing these with verified open-access source spans.

## Protocol Files (referenced)

| File | Status |
|------|--------|
| `protocol/ANNOTATION_SCHEMA_V1.json` | ✓ Frozen |
| `protocol/ANNOTATION_HANDBOOK_V1.md` | ✓ Frozen |
| `protocol/ADJUDICATION_POLICY_V1.md` | ✓ Frozen |
| `protocol/CORPUS_DESIGN_V1.md` | ✓ Frozen |
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