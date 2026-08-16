# File Index — gold/

| File | Status | Description |
|------|--------|-------------|
| `SAMPLE_MANIFEST_SEED_V1.json` | ✓ SEED | 32 seed entries across 8 case families, 4 disciplines |
| `SAMPLE_MANIFEST_V1.json` | ✓ SEED | JSON Schema for manifest format |
| `annotate.py` | ✓ | Annotation CLI tool (list, annotate, validate, adjudicate, stats) |
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

## Target Files (to be created)

| File | Description |
|------|-------------|
| `annotations/` | Per-sample annotation records (PENDING) |
| `adjudicated/` | Adjudicated gold truth (PENDING) |
| `REPRODUCIBILITY.md` | Data reproduction checklist (PENDING) |