# P9 headline tables V1.1

Derived only from `OFFICIAL_EVIDENCE_SUMMARY_V1.json`.

## M1 — view accuracy versus exact empirical ceiling

| View | Accuracy | Ceiling | Gap | Violation |
|---|---:|---:|---:|---|
| SURFACE | 0.500000 | 0.500000 | 0.000000 | False |
| TOPOLOGY | 0.500000 | 0.500000 | 0.000000 | False |
| TYPED | 0.666667 | 0.666667 | 0.000000 | False |
| CURRENT | 0.670139 | 0.833333 | 0.163194 | False |
| SEMANTIC | 0.836806 | 1.000000 | 0.163194 | False |

## D1 — protected whole-domain transfer

| Arm | Selected model | Accuracy | Macro-F1 | Double corruption | UNRESOLVED |
|---|---|---:|---:|---:|---:|
| TRANSCRIPT_BAG | `logistic-C0.1` | 0.250000 | 0.133333 | 0.000000 | 0.000000 |
| UNTYPED_PAIR | `logistic-C0.1` | 0.906250 | 0.912886 | 1.000000 | 1.000000 |
| TYPED_RELATIONAL | `logistic-C0.1` | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| TYPED_SERIALIZED_BAG | `logistic-C1` | 0.500000 | 0.222222 | 1.000000 | 0.000000 |

Typed relational minus transcript: **0.750000**.
Typed relational minus same-information serialization: **0.500000**.

## D1 — paired protected-case effects

| Comparator | Delta | Paired 95% bootstrap CI | Discordant typed wins-losses | Exact McNemar p |
|---|---:|---|---:|---:|
| Transcript bag | 0.750000 | [0.671875, 0.820312] | 96-0 | 2.524e-29 |
| Untyped pair | 0.093750 | [0.046875, 0.148438] | 12-0 | 0.000488 |
| Same-information typed serialization | 0.500000 | [0.414062, 0.585938] | 64-0 | 1.084e-19 |

The paired analysis is post-hoc and derived from the frozen 128 protected predictions; it quantifies the existing D1 result and is not a new preregistered endpoint.

## Explicit-inference closure

| Atom | Weaker view | Weaker accuracy | Sufficient view | Sufficient accuracy | Interpretation |
|---|---|---:|---|---:|---|
| A2 relation semantics | TOPOLOGY | 0.000000 | TYPED | 1.000000 | typed relation semantics are load-bearing; explicit selection suffices |
| A4 failure history | CURRENT | 0.500000 | SEMANTIC | 1.000000 | admitted scoped failure history is load-bearing; explicit filtering suffices |
| A5 affine transport | TYPED | 0.000000 | CURRENT | 1.000000 | visible local maps plus exact composition close the D0 computation |
