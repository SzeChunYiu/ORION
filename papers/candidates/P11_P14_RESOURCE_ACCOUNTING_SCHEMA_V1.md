# ORION-21–ORION-24 Resource Accounting Schema V1

**Owner track:** #664  
**Consumers:** ORION-21 #471, ORION-22 #665, ORION-23 #666, ORION-24 #669 where system overhead is compared  
**Status:** DRAFT FROZEN WRITING CONTRACT — no outcome-derived weights

## Principle

State construction is computation. A comparison is invalid if compilation, preprocessing, caching, recovery, verifier calls, model/search effort or state memory is charged in one arm but hidden in another.

The canonical object is a **resource vector**, not a scalar score:

`R = (C_compile, T_compile, S_state, M_model, C_reason, N_search, N_verify, N_tool, S_cache, C_recover, T_wall, E_energy?)`

A paper may report a Pareto frontier or apply a prospectively supplied decision cost vector. It may not choose scalar weights after seeing which arm wins.

## Required receipt fields

Every evaluated item/episode should emit one machine-readable receipt with at least:

| Field | Meaning | Rule |
|---|---|---|
| `episode_id` | protected item identity | immutable, non-semantic identifier |
| `paper_id` | ORION-21/ORION-22/ORION-23/ORION-24 | required |
| `split_id` | train/dev/protected family | no protected-outcome tuning |
| `system_arm` | exact arm name | preregistered vocabulary |
| `raw_source_id` | identity/hash of raw evidence/state | required for all transforms |
| `state_type` | RAW/UNIVERSAL/TASK_COMPILED/CACHE_SET/RCS | do not merge categories |
| `compiler_id` | exact compiler/transform identity | `NONE` if no compiler |
| `compiler_train_cost` | reusable training resource vector | never silently free |
| `compile_ops` | exact/estimated primitive operations | state estimation method |
| `compile_time_s` | measured wall/process time for transform | distribution + environment required |
| `state_bytes` | serialized byte size where meaningful | same serialization rule across arms |
| `state_tokens` | tokenizer-specific state length where meaningful | record tokenizer identity |
| `model_identity` | model/checkpoint/version | exact identity |
| `model_capacity` | params/active params/interaction degree or task-relevant capacity proxy | define before comparison |
| `generated_tokens` | downstream generated tokens | include hidden reasoning only if observable/accountable |
| `recurrent_steps` | recurrent/inference steps when non-token model | arm-comparable definition |
| `search_nodes` | explicit search expansion count | include failed branches |
| `verifier_calls` | exact verifier invocations | successful + failed |
| `tool_calls` | external calls | type breakdown retained |
| `cache_bytes` | retained reusable compiled state | charge all arms consistently |
| `cache_hits` | reuse events | do not infer benefit without hit definition |
| `recovery_mode` | none/raw-reopen/reconstruct/recompile | required when richer state is reacquired |
| `recovery_cost` | resource vector for recovery | not assumed zero |
| `wall_time_s` | end-to-end latency | non-authoritative if nondeterministic unless protocol says otherwise |
| `energy_j` | optional reproducible energy estimate | only if measurement method is frozen |
| `quality_metric` | task/verifier outcome | exact definition |
| `quality_value` | observed task outcome | no resource/quality mixing |
| `notes` | bounded anomaly field | no post-hoc endpoint changes |

## Training/amortization accounting

Learned compilers and allocators have two cost layers:

1. **development/training cost** — reported independently and never hidden;
2. **per-query inference/compile cost** — charged to each test episode.

If training is amortized, the reuse horizon `H` and deployment distribution must be declared before protected evaluation. Report at least:

- no-amortization view;
- per-episode inference-only view;
- one or more prospectively justified amortization horizons.

Do not claim a Pareto improvement that exists only at an undisclosed reuse horizon.

## Quality matching

Resource comparisons are valid only at the same quality target or as full quality–resource curves. If an arm does not reach a frozen target, record `NOT_REACHED`; do not extrapolate a fictional crossing.

For verified domains, final correctness is the verifier outcome. For non-verifier domains, define the primary metric and judge procedure before results.

## Cache and optionality accounting

Caching is not free preprocessing. Report:

- bytes/tokens retained;
- compilation cost that produced each cached state;
- cache invalidation/recompilation events;
- hit/miss definition;
- raw-state retention cost separately;
- recovery/reopen latency and compute;
- future-query coverage/optionality independently of current-task accuracy.

If raw state disappears, compiled-only recoverability must reflect that loss; do not label inaccessible coordinates `recoverable`.

## ORION-22 matched-total-budget audit

ORION-22 arms receive the same total envelope. The protocol must specify which resource dimensions are hard caps and how heterogeneous resources are compared.

Preferred reporting:

- exact controlled units where a common primitive exists;
- vector Pareto comparison for real systems;
- prospectively supplied operational cost vectors only when a downstream decision contract provides legitimate weights.

Unused budget is recorded. It is not silently transferred across axes after the protected outcome is known.

Mandatory arms:

- fixed state + fixed reasoning;
- fixed state + adaptive reasoning;
- adaptive state + fixed reasoning;
- joint adaptive state + adaptive reasoning;
- oracle diagnostic ceiling;
- random/simple threshold sanity controls.

The joint arm cannot receive additional compiler training, cache, verifier calls, retries or search depth unavailable to comparators.

## ORION-23 safety–cost accounting

Unsafe reuse can be reduced trivially by always reopening. Therefore report a multi-objective frontier over:

- unsafe reuse;
- verified task success;
- unnecessary reopen count;
- raw bytes/tokens reread;
- recovery latency;
- verifier/tool calls;
- state/certificate bytes.

A positive RCS claim requires improvement over confidence-only/unqualified compact state **without** collapsing to the always-raw/always-reopen corner.

## ORION-24 governance-overhead accounting

ORION-RSE must not win by receiving more research compute. Match or report:

- underlying model/version;
- context/input evidence;
- web/literature access;
- tool access;
- token budget;
- search/experiment budget;
- reviewer/evaluator access;
- wall time;
- number of research/reviewer passes.

Governance operations themselves count. More documentation, decomposition or debate is not free.

## Statistical reporting

For runtime/energy metrics, report repeated measurements and interval estimates only when repeated measurement is scientifically meaningful and the environment is controlled. Do not invent p values or confidence intervals when raw repetitions are unavailable.

For item-level paired comparisons, preserve family/domain blocks. Headline uncertainty should use family/domain-aware resampling where task families are the generalization unit. Report regime-specific effects so a positive global mean cannot hide a harmful subgroup.

## Invalid comparison checklist

A comparison fails the accounting audit if any of the following occurs:

- compiler computes the answer and its cost is omitted;
- state memory is charged in one arm only;
- compiler training cost is hidden;
- cached work is available asymmetrically;
- quality thresholds differ;
- verifier/stopping rules differ;
- one arm receives more total budget;
- raw recovery cost is treated as zero;
- nondeterministic timing is mixed into deterministic scientific hashes;
- asymptotic and concrete resource units are silently combined;
- post-hoc scalar weights create the reported winner.

## Minimal JSON shape

```json
{
  "schema": "ORION.P11P14.ResourceReceipt.v1",
  "episode_id": "...",
  "paper_id": "ORION-22",
  "split_id": "protected-family-A",
  "system_arm": "JOINT_STATE_REASONING",
  "raw_source_id": "sha256:...",
  "state": {
    "type": "TASK_COMPILED",
    "compiler_id": "...",
    "compile_ops": 0,
    "compile_time_s": null,
    "bytes": 0,
    "tokens": 0
  },
  "model": {
    "identity": "...",
    "capacity": {}
  },
  "reasoning": {
    "generated_tokens": 0,
    "recurrent_steps": 0,
    "search_nodes": 0,
    "verifier_calls": 0,
    "tool_calls": 0
  },
  "cache": {
    "bytes": 0,
    "hits": 0
  },
  "recovery": {
    "mode": "none",
    "cost": {}
  },
  "quality": {
    "metric": "verified_success",
    "value": 0
  }
}
```

## Freeze rule

Any change that can alter relative resource accounting after protected outcomes requires a new schema/protocol version and cannot retroactively change a prior terminal.
