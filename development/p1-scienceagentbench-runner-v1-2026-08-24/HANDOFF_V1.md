# P1 ScienceAgentBench verified runner V1 — handoff

## Terminal

`P1_SAB_VERIFIED_RUNNER_STATIC_AND_SYNTHETIC_CONTRACT_READY__OWNER_RUNTIME_BINDINGS_AND_OFFICIAL_RUNTIME_CANNOT_CHECK__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED`

This additive packet implements a network-free, standard-library contract runner
for the verified ScienceAgentBench population. It validates immutable input and
mask identities, exact task/arm/attempt products, matched prospective budgets,
complete per-attempt accounting, null-preserving failure records, and inert
official-evaluator command emission. It does not generate a candidate, execute a
candidate program, invoke the official evaluator, open an outcome, or authorize
a benchmark run.

Scientific authority delta: `NONE`.

## Frozen production bindings

| Binding | Required value |
|---|---|
| Split | Explicit `verified`; omission, `validation`, and every other value are hard errors. |
| Verified Parquet SHA-256 | `c6f937863a220bd1762a00c20a0f79cc8dfca900b819bdb552150310731ae147` |
| Mask manifest SHA-256 | `442d9793024a91c752d34b9ad3185af612d1db3759458e91a61911b385cbe758` |
| Task IDs | Exact ordered canonical IDs `1..102`; integer or canonical decimal-string inputs normalize to strings. |
| Arms | Exact ordered set `RR`, `OS`, `NR`. |
| Attempts | Exactly 3 per task/arm; 918 task/arm/attempt records. |
| Final candidates | Exactly 1 per attempt. |
| Official source commit | `c26e151ed601ba109dc4d35e057ff8e73fec469d` |
| Official evaluator split argv | Exactly one adjacent pair `--split`, `verified`; `--split=...`, omission, and duplication fail. |

Production callers can supply artifact paths and owner bindings, but cannot
override any expected hash, task set, arm set, attempt count, source commit, or
evaluator module. Internal expected-hash/ID parameters exist only on underscored
functions for temporary nonbenchmark fixtures.

## Three-stage boundary

1. **Validate bindings:** hash the supplied verified Parquet without parsing it,
   parse only the hash-only mask manifest and run-plan JSON, and reject unbound
   model/provider/tokenizer/prompt/seed/tool/runtime/credential-route fields or
   unequal RR/OS/NR envelopes.
2. **Seal generation metadata:** after an external owner-controlled generator
   has produced attempts, validate exactly 918 records and content-seal the run
   plan, candidate ledger, tuple product, raw-output hashes, candidate-program
   hashes, usage, costs, and failures. Every attempt is retained. This module
   provides no model or program-execution capability.
3. **Emit an evaluator command receipt:** only a complete seal can produce an
   argv receipt. The receipt pins the required official source commit and emits
   `python -m evaluation.harness.run_evaluation ... --split verified`. It sets
   `execution_allowed=false`, `official_evaluator_invoked=false`, and runtime
   status `CANNOT_CHECK`. The module has no subprocess or shell execution path.

One command receipt names one arm/attempt. A future authorized run must preserve
all nine RR/OS/NR x attempt receipts; emitting a receipt is not execution
authority. The caller must independently prove that the specified evaluator
checkout is exactly the pinned commit before any external invocation.

## Contract inputs

`RUNNER_CONTRACT_V1.json` gives the exact run-plan, ledger, seal, command,
forbidden-field, forbidden-path, missingness, and retention contracts.

A production run plan remains inadmissible until an owner supplies concrete,
immutable values for:

- exact model ID, provider, tokenizer revision, and model-parameter hash;
- complete ordered prompt-bundle SHA-256 for RR, OS, and NR;
- paired three-attempt seed schedule plus confirmed provider seed capability;
- tool-policy and generation-runtime manifest SHA-256;
- owner-controlled credential-route SHA-256/status, never secret values;
- identical per-attempt total input/output token, tool-call, wall-time,
  local-execution-time, and one-candidate caps across all arms.

`AUTHOR_INPUT_NEEDED`, `CANNOT_CHECK`, `TBD`, `TODO`, `UNKNOWN`, `UNBOUND`, empty,
and null binding values fail closed. No concrete value is invented in this
packet.

Each candidate record requires task ID, arm, attempt, paired seed, actual input
and output tokens, actual tool calls, wall time, local-execution wall time,
billed USD, failure, raw-output SHA-256, and candidate-program SHA-256. A
successful record requires all measurements and hashes. A failed record uses a
typed `CANNOT_CHECK` object and may retain genuine nulls; partial measurements
remain recorded. There is no `solved` field and no missing-to-zero conversion.

## CLI surface

All paths must be absolute and must remain outside forbidden gold/evaluator/
rubric/result-body locations.

```text
python sab_verified_runner_v1.py validate-bindings \
  --split verified \
  --parquet /approved/external/data/verified-00000-of-00001.parquet \
  --mask-manifest /checkout/development/p1-scienceagentbench-preflight-2026-08-24/MASK_MANIFEST_V1.json \
  --run-plan /approved/external/run/RUN_PLAN.json \
  --output /approved/external/run/BINDING_RECEIPT.json

python sab_verified_runner_v1.py seal-candidates \
  --split verified \
  --parquet /approved/external/data/verified-00000-of-00001.parquet \
  --mask-manifest /checkout/development/p1-scienceagentbench-preflight-2026-08-24/MASK_MANIFEST_V1.json \
  --run-plan /approved/external/run/RUN_PLAN.json \
  --candidate-ledger /approved/external/run/CANDIDATE_LEDGER.json \
  --output /approved/external/run/CANDIDATE_SEAL.json

python sab_verified_runner_v1.py emit-evaluator-command \
  --split verified \
  --seal-receipt /approved/external/run/CANDIDATE_SEAL.json \
  --official-repo-root /approved/external/ScienceAgentBench-pinned \
  --benchmark-path /approved/external/benchmark_verified \
  --pred-program-path /approved/external/run/pred_programs/RR/attempt-1 \
  --log-fname /approved/external/run/logs/RR-attempt-1.jsonl \
  --arm RR --attempt 1 --run-id rr-a1 \
  --output /approved/external/run/commands/RR-attempt-1.json
```

These commands are documentation only and were not run against official data.
The third command writes JSON argv; it does not execute that argv.

## Synthetic validation

`validate_runner_v1.py` creates temporary two-task nonbenchmark byte/JSON
fixtures. It exercises the valid boundary and hostile cases for:

- omitted/`validation` split and wrong or missing artifact hashes;
- wrong, duplicate, extra, or noncanonical task IDs;
- missing arms, mismatched caps, unbound runtime/seed/credential routes;
- missing, duplicate, extra, wrong-attempt, or wrong-seed candidate tuples;
- missing hashes, invalid or over-cap usage, best-attempt-only cost, and run-plan drift;
- forbidden outcome/feedback fields and forbidden body-path components;
- null-preserving typed `CANNOT_CHECK` failures;
- partial/unsealed command emission and missing/duplicate/conflicting split argv;
- production CLI constant non-overrideability; and
- absence of network, provider, subprocess, Docker, Parquet, or evaluator imports.

The committed receipt records 28 passing synthetic tests. Validation opened no
official Parquet or task text, no benchmark archive, no gold/evaluation/rubric/
result body, no official outcome, and invoked no evaluator.

## What this closes and does not close

This packet closes the static verified-split/matching/ledger/command contract
portion of preflight blockers PF-02 and PF-05. It does **not** close:

- full `benchmark_verified.zip` byte count/SHA-256, decryption, and extracted
  manifest identity on approved external storage;
- exact prompts, model, provider, tokenizer, seeds, tools, budgets, credentials,
  or runtime owner approval;
- pinned evaluator checkout verification, Docker/base/dependency/image identity,
  sufficient disk/RAM, secret cleanup, or official GPT-4o route callability;
- a fresh isolated runtime smoke test, protocol/runner/analysis signature, or
  preregistration freeze;
- official candidate generation, evaluator execution, all-three judge-sample
  retention, outcome parsing, paired task analysis, or any P1 gate;
- protected custody, independent adjudication, hidden-formulation responsibility,
  transition authority, superiority, or publication promotion.

All of those remain `AUTHOR_INPUT_NEEDED` or `CANNOT_CHECK`. Missing, partial,
wrong-split, runtime-failed, and evaluator-failed future records remain
`CANNOT_CHECK`, never solved=0.

## Retention and execution boundary

Do not commit the verified Parquet, benchmark ZIP or extracted data, task text,
raw model outputs, predicted programs, gold/evaluation programs, rubrics, gold
results, evaluator logs, judge responses, credentials, container layers, or
official outcomes. Keep those on owner-approved external storage subject to the
upstream terms recorded in the preflight. This repository packet contains only
contract prose/JSON, runner/validator source, synthetic validation receipt, and
hashes.

The official evaluator must not be invoked until every remaining blocker is
closed and the final protocol/runner/analysis bundle is byte-bound. This PR must
remain unmerged pending review.
