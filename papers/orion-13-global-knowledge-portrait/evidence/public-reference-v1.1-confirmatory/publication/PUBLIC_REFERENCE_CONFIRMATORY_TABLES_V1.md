# ORION-P3 public-reference confirmatory publication tables V1

Generated deterministically from `CONFIRMATORY_ANALYSIS.json`. Scope: already-structured public-reference mapping only.

## Table PR3-T1 — confirmatory composition

| Case family | n | ORION false merge | Flat false merge | Exact abstention |
|---|---:|---:|---:|---:|
| `different_name_same_referent` | 13 | 0.0000 | 0.0000 | 0.0000 |
| `polarity_modality_attribution_context` | 13 | 0.0000 | 0.4615 | 0.4615 |
| `valid_invalid_representation_mapping` | 6 | 0.0000 | 0.0000 | 0.0000 |

## Table PR3-T2 — pooled systems

| System | Accuracy | False merge | False split | Abstention |
|---|---:|---:|---:|---:|
| ORION typed mapping | 1.0000 | 0.0000 | 0.0000 | 0.0000 |
| Flat predicate canonicalization | 0.8125 | 0.1875 | 0.0000 | 0.0000 |
| Exact-coordinate conservative | 0.8125 | 0.0000 | 0.0000 | 0.1875 |

## Table PR3-T3 — predeclared primary comparisons

| Comparison | Difference | 95% paired bootstrap CI |
|---|---:|---:|
| ORION − flat false merge | -0.1875 | [-0.3438, -0.0625] |
| ORION − exact false split | +0.0000 | [+0.0000, +0.0000] |

## Table PR3-T4 — covered ablations

| Ablation | False-merge delta vs full ORION | 95% CI |
|---|---:|---:|
| `force_compatibility_without_obstruction` | +0.1875 | [+0.0625, +0.3438] |
| `remove_construct` | +0.0000 | [+0.0000, +0.0000] |
| `remove_measurement` | +0.0000 | [+0.0000, +0.0000] |
| `remove_modality_polarity_attribution_discourse` | +0.1875 | [+0.0625, +0.3438] |
| `remove_referent` | +0.0000 | [+0.0000, +0.0000] |
| `remove_temporal_context` | +0.0000 | [+0.0000, +0.0000] |

**Authority boundary.** These tables do not establish raw-text extraction, retrieval/provider quality, generated-portrait recoverability, downstream utility, or the original eight-family end-to-end claim.
