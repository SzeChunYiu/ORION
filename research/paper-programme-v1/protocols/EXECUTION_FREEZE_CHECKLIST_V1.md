# Publication execution-freeze checklist V1

Use this checklist for exactly one paper/protocol before the first final outcome is inspected. A `DESIGN_FROZEN` protocol is not yet permission to run a publication-authorizing final study.

## 1. Freeze the subject

- record the exact 40-character ORION subject commit;
- verify the working/evaluation environment actually checks out that subject;
- do not mix observations from different subject revisions in one headline run.

## 2. Freeze data, gold and splits

For every dataset/corpus/case set:

- record immutable release revision or content hash;
- record license/access restrictions;
- freeze train/pilot/development/replay/fresh/test/protected split identities as applicable;
- retain the gold/evaluator object outside candidate custody when the protocol requires hidden labels;
- freeze adjudication/gold before final model outputs when P3/P4 human/protected evaluation requires it.

## 3. Freeze systems and baselines

- record provider/model/tool versions;
- content-hash every baseline configuration/prompt/controller;
- record deterministic and stochastic seeds;
- bind the same resource policy/budget class across matched systems;
- document any unavoidable capability/resource mismatch prospectively.

## 4. Freeze evaluator and access policy

- content-hash the evaluator/metric/guard artifact;
- bind the evaluation epoch;
- freeze candidate-visible evidence/tools/search policy;
- enable required file/network/search/evaluator access telemetry;
- verify candidate code cannot write protected evaluator/holdout state.

## 5. Create the run manifest

Create one JSON object conforming to `RUN_MANIFEST_SCHEMA_V1.json` with:

- protocol ID and canonical protocol SHA-256 digest;
- exact subject revision;
- data/gold/split identities;
- provider/model and baseline config identities;
- evaluator hash and epoch;
- seeds and resource limits;
- environment/dependency identity;
- access-policy hash;
- artifact root;
- `created_before_outcome_access=true`.

Validate it with:

```bash
python research/paper-programme-v1/protocols/publication_manifest.py run path/to/RUN_MANIFEST.json
```

## 6. Promote the protocol state prospectively

Copy the exact run bindings into the paper's `protocol/PROTOCOL_V1.json`, change only:

- `protocol_status`: `DESIGN_FROZEN` -> `EXECUTION_FROZEN`;
- the previously `UNBOUND` execution-binding values.

Keep `outcome_accessed=false`.

Validate:

```bash
python research/paper-programme-v1/protocols/publication_manifest.py protocol papers/<paper>/protocol/PROTOCOL_V1.json
```

Commit/PR/CI this freeze **before** launching or inspecting final outcomes. The PR/commit itself is part of the provenance record.

## 7. Outcome-access transition

When the final run starts or its outcomes become visible, preserve the execution-frozen protocol and run manifest. If the repository needs a state marker, a follow-up record may set `OUTCOME_ACCESSED`/`outcome_accessed=true` without changing the frozen scientific design or execution identities.

If any hypothesis, task family, baseline, ablation, metric, exclusion rule, statistical rule, safety margin, evaluator identity, gold/split, or access policy must change after outcome access, **do not rewrite V1**. Create a new immutable V2 protocol and state why V1 was insufficient or invalidated.

## 8. Invalidating conditions

The final run cannot support the headline publication claim if, among other protocol-specific failures:

- final outcomes were inspected before required identities were frozen;
- subject revisions are mixed;
- final gold/holdout leaked to the candidate;
- evaluator/metric changed post-outcome without a new protocol version;
- hidden/protected data cannot be tied to an auditable external custodian;
- failed/null/harmful candidate observations are silently removed;
- public benchmark search contamination is ignored where the protocol requires auditing.

Such runs remain evidence, but their authority is `INVALIDATED` or bounded to a weaker claim rather than silently promoted.
