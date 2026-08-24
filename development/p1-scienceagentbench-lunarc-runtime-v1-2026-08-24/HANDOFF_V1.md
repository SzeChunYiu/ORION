# P1 ScienceAgentBench LUNARC runtime V1 — handoff

## Terminal

`P1_SAB_LUNARC_SYNTHETIC_CONTAINER_ROUTE_READY__OFFICIAL_BASE_ARCHIVE_EVALUATOR_AND_CREDENTIALS_CANNOT_CHECK__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED`

## Closed in this increment

- The local 3 GiB/dormant-Docker blocker no longer determines feasibility.
- LUNARC provides protected project storage and large node-local scratch.
- A Slurm compute node successfully exposed a Podman-backed Docker API to
  Docker SDK 7.1.0.
- Synthetic Docker SDK build/create/start/exec/remove passed in job `3533810`.
- Required userland runtime binaries and executed scripts are content-hashed.

## Not closed

- no archive payload has been retained or extracted on LUNARC;
- no official base or instance image has been built;
- no official evaluator has been imported or invoked;
- no OpenAI/Azure evaluator credential route is present;
- no official task, candidate or outcome has been opened;
- exact prompts, seeds, tokenizer guarantees and matched budgets remain under
  the separate generation-route lane;
- scientific authority delta remains `NONE`.

## Reproduction

1. Stage the binaries named in `PODMAN_TOOLCHAIN_SHA256SUMS` under an
   owner-only external path. Do not commit binaries or container layers.
2. Stage the three executable Python/shell files in this packet under
   `${ORION_SAB_REMOTE_ROOT}/scripts-v1` and verify `REMOTE_SHA256SUMS`.
3. Submit `run_lunarc_synthetic_smoke_v1.sh` with Slurm account
   `lu2026-2-51`, partition `lu48`.
4. Require a PASS receipt, zero credential presence, zero tasks/outcomes and
   verified container/image cleanup.

The packet intentionally does not include the benchmark, predictions,
credentials, raw container layers or task/evaluator bodies.
