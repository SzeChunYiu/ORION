# ORION Paper 3 — Gold Dataset

## Overview

This directory contains the gold-standard annotation dataset for the
ORION Paper 3 evaluation protocol (`ORION-13.cross-domain-atlas.v1`). The
dataset is used to score all 7 baselines, 8 ablations, and the full
ORION system against human expert annotations.

## Disciplines

Four disciplines are represented in balanced coverage:

| Discipline | # Samples | Rationale |
|------------|-----------|-----------|
| Biomedicine | 8 | High-stakes integration, mature ontology landscape |
| Physics | 8 | Mathematical precision, multiple interpretation frameworks |
| Social Science | 8 | Construct measurement diversity, pluralism challenges |
| Climate Science | 8 | Multi-scale integration, attribution complexity |

## Case Families

Eight case families, each with 4 samples (one per discipline):

1. **same_name_different_referent** — Two sources use the same surface
   term to refer to distinct entities.
2. **different_name_same_referent** — Two sources use different surface
   terms to refer to the same entity.
3. **same_construct_different_measurement** — Same underlying construct
   measured by different instruments.
4. **same_entity_different_temporal_state** — Same entity at different
   time points; not a contradiction.
5. **polarity_modality_attribution_context** — Claims sharing polarity
   but differing in modality, attribution, or context.
6. **valid_invalid_representation_mapping** — Non-isomorphic but valid
   mapping between classification systems.
7. **valid_invalid_literature_bridge** — Cross-domain literature bridges
   with transfer conditions.
8. **genuine_plural_obstruction** — Genuine scientific pluralism;
   verdict is PLURAL_VIEW.

## Annotation Schema

Every sample is annotated on 11 coordinates defined in
`../protocol/ANNOTATION_SCHEMA_V1.json`:

- referent_relation, construct_relation, measurement_relation,
  context_relation, polarity_relation, modality_relation,
  attribution_relation, discourse_relation, mapping_relation,
  contradiction_verdict, integration_verdict

Integration verdict uses one of four values:

- `GLUE_ALLOWED` — sources are compatible and can be merged
- `OBSTRUCTION` — sources are genuinely incompatible
- `PLURAL_VIEW` — multiple valid perspectives coexist
- `UNRESOLVED` — cannot determine

## Status

| Status | Meaning |
|--------|---------|
| SEED | Placeholder entries with synthetic document identifiers |
| GOLD_COMPLETE | All 32 samples annotated and adjudicated (target) |
| QUALITY_GATE | Inter-annotator agreement ≥ threshold across all coordinates |

Current status: **SEED** — placeholder entries; not yet annotated.

## Tools

Use `annotate.py` to manage the annotation workflow:

```bash
python3 annotate.py list              # list samples with status
python3 annotate.py annotate ID out   # create blank annotation skeleton
python3 annotate.py validate ann      # validate a completed annotation
python3 annotate.py adjudicate a b out # merge two independent annotations
python3 annotate.py stats             # coverage statistics
```

## Files

| File | Description |
|------|-------------|
| `SAMPLE_MANIFEST_SEED_V1.json` | 32 seed entries (4 disciplines × 8 samples each) |
| `SAMPLE_MANIFEST_V1.json` | JSON Schema for the manifest format |
| `annotate.py` | Annotation CLI tool (list, annotate, validate, adjudicate, stats) |
| `README.md` | This file |
| `MANIFEST.md` | File index and coverage matrix |
| `CORPUS_DESIGN_V1.md` | Corpus design rationale |
| `DISCIPLINE_SELECTION_V1.md` | Three-discipline selection + case-family coverage (Issue #158) |
| `ANNOTATION_SCHEMA_V1.md` | Annotation schema, procedure, agreement targets, expert escalation |

## Licensing

All sources are selected from open-access publications per the
licensing rules in `CORPUS_DESIGN_V1.md`. Final gold
replacements use verified open-access document spans.