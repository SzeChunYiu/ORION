# P5-3_cause_confusion

**Status:** OK / DESCRIPTIVE_ONLY

Accuracy **21/24** = 0.875 (macro precision 0.895833; macro recall 0.875000; standard macro-F1 0.872619; nominal Wilson score interval 0.690–0.957). This interval treats the 24 fixed cases as Bernoulli units and is not a population confidence interval. Three residual errors are retained.

| gold \ attributed | RETRIEVAL_MISS | ROUTING_PLANNING_MISS | IMPLEMENTATION_BUG | ENVIRONMENT_DEPENDENCY_TOOL_FAILURE | EVALUATOR_METRIC_BUG | REPRESENTATION_GAP | MEASUREMENT_SPECIFICATION_GAP | METHOD_BASIS_GAP |
|---|---|---|---|---|---|---|---|---|
| RETRIEVAL_MISS | 2 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| ROUTING_PLANNING_MISS | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| IMPLEMENTATION_BUG | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 |
| ENVIRONMENT_DEPENDENCY_TOOL_FAILURE | 0 | 0 | 1 | 2 | 0 | 0 | 0 | 0 |
| EVALUATOR_METRIC_BUG | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| REPRESENTATION_GAP | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 1 |
| MEASUREMENT_SPECIFICATION_GAP | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| METHOD_BASIS_GAP | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |

## Residual errors (not successes)

- `ORION-15-HC-002`: gold `RETRIEVAL_MISS` attributed `REPRESENTATION_GAP` (MEDIUM)
- `ORION-15-HC-012`: gold `ENVIRONMENT_DEPENDENCY_TOOL_FAILURE` attributed `IMPLEMENTATION_BUG` (HIGH)
- `ORION-15-HC-018`: gold `REPRESENTATION_GAP` attributed `METHOD_BASIS_GAP` (HIGH)

Single-model, single-run diagnostic attribution on the archived 24-case hidden-cause suite. Not a protected fresh-transfer campaign, not H1, and not a 24/24 result.
