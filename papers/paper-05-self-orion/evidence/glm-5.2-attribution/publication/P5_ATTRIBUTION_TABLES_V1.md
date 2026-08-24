# ORION-P5 glm-5.2 attribution publication tables V1

These tables are deterministic presentation artifacts of the archived glm-5.2 hidden-cause *attribution* campaign (n=24, single model, single run). They do not establish protected fresh-transfer improvement, matched baseline/ablation results, specialist-regression trajectories, or intervention-backed repair. Missing campaign axes are recorded as CANNOT_CHECK rather than filled with proxies.

## Table P5-2 — fresh-transfer vs motivating replay

Status: `CANNOT_CHECK`. Archived rows have no replay/fresh deltas.

## Table P5-3 — hidden-cause attribution confusion

Accuracy 21/24 = 0.8750; macro-F1 0.8726.
Preserved errors: P5-HC-002, P5-HC-012, P5-HC-018.

| Gold family | n | correct | precision | recall | F1 |
|---|---:|---:|---:|---:|---:|
| `RETRIEVAL_MISS` | 3 | 2 | 1.0000 | 0.6667 | 0.8000 |
| `ROUTING_PLANNING_MISS` | 3 | 3 | 1.0000 | 1.0000 | 1.0000 |
| `IMPLEMENTATION_BUG` | 3 | 3 | 0.7500 | 1.0000 | 0.8571 |
| `ENVIRONMENT_DEPENDENCY_TOOL_FAILURE` | 3 | 2 | 1.0000 | 0.6667 | 0.8000 |
| `EVALUATOR_METRIC_BUG` | 3 | 3 | 1.0000 | 1.0000 | 1.0000 |
| `REPRESENTATION_GAP` | 3 | 2 | 0.6667 | 0.6667 | 0.6667 |
| `MEASUREMENT_SPECIFICATION_GAP` | 3 | 3 | 1.0000 | 1.0000 | 1.0000 |
| `METHOD_BASIS_GAP` | 3 | 3 | 0.7500 | 1.0000 | 0.8571 |

| Case | Gold | Attributed |
|---|---|---|
| `P5-HC-002` | `RETRIEVAL_MISS` | `REPRESENTATION_GAP` |
| `P5-HC-012` | `ENVIRONMENT_DEPENDENCY_TOOL_FAILURE` | `IMPLEMENTATION_BUG` |
| `P5-HC-018` | `REPRESENTATION_GAP` | `METHOD_BASIS_GAP` |

## Table P5-4 — longitudinal specialist regression

Status: `CANNOT_CHECK`. No improvement-round trajectory is archived.

## Table P5-5 — improvement vs integrity frontier

Status: `CANNOT_CHECK`. No matched baseline/ablation results are archived.

## Table P5-6 — recognized-failure recurrence

Status: `CANNOT_CHECK`. No negative-history on/off rounds are archived.

## Table P5-7 — attribution-campaign cost

Prompt tokens 11081; completion tokens 3109; total 14190; mean latency 13.0366s.
This is not cost-to-protected-validated-improvement.

**Authority boundary.** These tables are deterministic presentation artifacts of the archived glm-5.2 hidden-cause *attribution* campaign (n=24, single model, single run). They do not establish protected fresh-transfer improvement, matched baseline/ablation results, specialist-regression trajectories, or intervention-backed repair. Missing campaign axes are recorded as CANNOT_CHECK rather than filled with proxies.
