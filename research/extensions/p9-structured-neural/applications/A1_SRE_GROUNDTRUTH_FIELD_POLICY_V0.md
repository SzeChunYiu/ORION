# P9 A1 SRE ground-truth field policy V0

Status: **PRE-EXECUTION / outcome_accessed=false**.

External source identity:

- ITBench `a1fffbe9221d5792c566e944c01763403413d97c`.
- ITBench-Evaluations `14f026fc9cc348c4ecec5ab32714de954c95c1b1`.

Purpose: prevent an SRE ``structured representation'' from winning by ingesting ITBench evaluator truth.

## Observation from source audit

ITBench SRE `groundtruth_v1.yaml` files can contain, in the same file:

- alert/symptom records;
- `fault` records describing injected conditions;
- `groups` records including `root_cause: true`;
- explicit propagation edges/conditions/effects;
- recommended actions.

For example, scenario 7 contains downstream `HighRequestErrorRate` / `NoRequestsReceived` alerts while also marking `flagd-config` as the root cause and explicitly recording the propagation chain through payment, checkout, frontend and proxy services.

Therefore **the file is not a model input**. It is a mixed evaluator/source object that must be projected through a frozen custody policy.

## Evaluator-only fields — prohibited from every model-visible arm

Unless a future protocol explicitly proves a field is independently observable from runtime evidence, exclude:

- `fault` entire subtree;
- `groups[*].root_cause`;
- root-cause group membership inferred from that boolean;
- `propagations` entire subtree;
- `recommended_actions` entire subtree;
- solution guides / remediation steps;
- disruption/injection identifiers and arguments;
- changed-from/to configuration values from scenario construction;
- fault mechanism names;
- scenario id/index if it can act as a reusable answer key;
- any natural-language string containing the injected fault name or explicit causal explanation.

These fields may be used only by the evaluator/verifier to derive protected labels and propagation metrics.

## Candidate-visible fields — only after separate observability audit

### Surface arm

May include only information that would plausibly be available to an operator/agent at incident time, for example:

- alert ids/types;
- alert source/group after identity reminting;
- scalar telemetry/statistics from the bound snapshot;
- log/trace excerpts after leakage filtering;
- coarse resource type if independently observable.

Even alert descriptions must be audited: a description such as ``failing due to feature flag'' leaks a causal hypothesis and therefore must be removed or normalized for protected evaluation.

### Topology arm

May add only topology reconstructed independently of the evaluator truth, e.g. from:

- Kubernetes ownership/reference structure;
- runtime service-call traces;
- deployment/service/config references;
- separately frozen application architecture.

The evaluator `propagations` list is **not** a permitted topology source.

### Typed-evidence arm

May add externally grounded relation/node types over the same independently observable evidence, e.g.:

- `SERVICE`, `DEPLOYMENT`, `POD`, `CONFIGMAP`;
- `CALLS`, `OWNS`, `SELECTS`, `MOUNTS`, `EMITS_ALERT`, `REFERENCES_CONFIG`;
- temporal/runtime relation types if derived from candidate-visible traces.

Do not introduce a type such as `CAUSES_ROOT_FAILURE` or any equivalent evaluator label.

### Explicit traversal/check arm

Receives exactly the typed-evidence payload. It may perform deterministic search/filter/check operations but receives no additional incident evidence.

## Ground-truth projection

The evaluator may derive:

- root-cause entity set from the frozen ground truth;
- protected propagation chain;
- fault-localization/component labels;
- accepted diagnostic terminal.

Projection code must be isolated from model-payload code and hostile-tested by falsifying evaluator truth while holding candidate payload byte-identical.

## Required hostile tests before execution

1. changing `root_cause: true` changes evaluator target but not model payload;
2. changing `fault` subtree changes evaluator target/metadata but not model payload;
3. deleting `propagations` changes propagation evaluation availability but not candidate topology;
4. recommended actions never appear in model payload;
5. causal phrases in alert descriptions are stripped or normalized;
6. scenario ids are reminted and unavailable as reusable features;
7. candidate topology can be rebuilt without reading evaluator propagation edges;
8. all model arms consume a common evidence manifest with view-specific projection only.

## Fail-closed rule

If a candidate-visible topology/type cannot be reconstructed without evaluator-only fields, that coordinate is marked `UNAVAILABLE/CANNOT_CHECK`; it is not backfilled from ground truth merely to make the benchmark runnable.
