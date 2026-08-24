# P5 native task-environment fan-out — V7

## Result

V7 uses the V6 common LANG-1 case and the six V4 arm contracts. It closes the
C1 `runtime.task_environment` field by materializing exact offline setup bytes
and an effective fixed-agent configuration. It does not run an arm or model.

| Quantity | V6 | V7 | Delta |
|---|---:|---:|---:|
| Bound field instances | 54 | 55 | +1 |
| Blocking field instances | 72 | 71 | -1 |
| R2 task-environment blockers | 6 | 5 | -1 |
| Execution-ready arms | 0 | 0 | 0 |

## Why only C1 closes

C1's missing environment consisted of setup/configuration bytes that can be
authored without native data, outcomes, or execution. The setup verifies the
rights-cleared V6 source archive, stages it offline, and makes only
`NumberUtils.java` writable. The config disables retries, sampling, review,
chooser/reviewer loops, local patch application, and open-PR behavior.

C2 lacks a substantive session/certificate/evaluator/write-root packet; C3
lacks a filtered DGM seed and case-specific certificate/policies; C4 has no
retained native domain implementing the shared Java repair task; C5 lacks
frozen solver outputs and development memberships; C6 lacks an actual filtered
seed/topic/corpus/skill/profile environment. Creating filenames or pointing to
schemas would not satisfy the preregistered byte-level rule.

## Boundary

This is task-environment evidence only. It does not bind the other 120 field
instances, authorize execution, measure performance, or establish superiority.

**Terminal:** `P5_V7_C1_NATIVE_TASK_ENVIRONMENT_BOUND__ONE_OF_SIX_ENVIRONMENTS_CLOSED__FIFTY_FIVE_OF_ONE_HUNDRED_TWENTY_SIX_FIELDS_BOUND__SEVENTY_ONE_BLOCKING__FIVE_R2_NATIVE_ENVIRONMENT_INSTANCES_REMAIN__ZERO_OF_SIX_READY__PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK`
