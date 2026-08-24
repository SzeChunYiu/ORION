# DIRECT_ROUTE_SLURM_PREFLIGHT_V1 handoff

## Status

This additive lane is synthetically implemented and hostile-validated. It
changes no merged PR #1168 or generation-adapter file. It is not authorization
to submit a SLURM job, open an official task, execute the model, finalize
scheduler evidence, evaluate candidates, open outcomes, or make scientific or
production claims.

A deterministic hostile regression executed the exact wrapper with a fake
`mkdir` earlier in `PATH`. The fake displaced the directory immediately after
creation and installed a replacement; the wrapper returned success and wrote
all artifacts into the replacement while leaving the initially created
directory empty. This is a defect witness, not evidence that the unchanged
wrapper is safe to execute.

## What the bridge closes

- Exact-byte bindings to the merged direct driver/contract/prompt bundle and the
  unchanged generation adapter. The unchanged wrapper is bound only as
  `BYTE_BOUND_SCHEDULER_SEMANTICS_DONOR_NONINVOKED`; execution is forbidden.
- Exact new-file snapshots and hashes for all tuple JSON inputs before launch.
- Exact model, llama-server, CUDA backend, shell launcher, and Python bridge
  hashes.
- Exact llama-server argv: literal `127.0.0.1:8080`, context 32,768, one slot,
  continuous batching off, context shift off, and direct-driver request cache
  off.
- Live process evidence after readiness: executable identity/hash, exact argv,
  empty proxies, exact backend environment, mapped model/backend device+inode,
  server-owned listener, health, and one slot.
- One remaining 1,800-second `CLOCK_MONOTONIC_RAW` deadline across every phase.
  RR/NR cannot obtain two independent 1,800-second HTTP windows.
- Typed adapter `CANNOT_CHECK` emission after capture construction, including
  deadline failures. A pre-capture supervisor failure is never substituted for
  the adapter sidecar.
- Run-plan binding extension for the direct driver, bridge, contract, prompt
  bundle, adapter, wrapper, input hashes, prospective static prompt hashes, the
  sealed RR dynamic rendering rule, and observed exact request hashes.
- New-file-only output creation through pinned verified parent directory
  descriptors and relative `mkdirat`/`openat` operations, including fail-closed
  symlink and concurrent parent-swap handling. The supervisor creates
  `attempt/` in-process and writes the scheduler snapshot/identity, adapter
  capture, bridge receipts, failure sidecars, and rollback through its pinned
  directory FD. Production does not traverse `/dev/fd/<fd>/child` or
  `/proc/self/fd/<fd>/child`.
- Cleanup of the entire owned server PGID even after leader exit. The wrapper
  is recorded as `NONINVOKED`, not as a cleaned process.

## Live invocation shape — not authorized by this handoff

The owner would submit exactly one tuple with all input hashes supplied before
execution:

```bash
rtk sbatch run_direct_route_slurm_preflight_v1.sh \
  --run-plan /absolute/RUN_PLAN.json \
  --run-plan-sha256 <sha256> \
  --owner-selection /absolute/OWNER_SELECTION.json \
  --owner-selection-sha256 <sha256> \
  --runtime-binding /absolute/RUNTIME_BINDING.json \
  --runtime-binding-sha256 <sha256> \
  --masked-packet /absolute/MASKED_PACKET.json \
  --masked-packet-sha256 <sha256> \
  --recovered-packet /absolute/RECOVERED_PACKET.json \
  --recovered-packet-sha256 <sha256> \
  --task-id <1..102> --arm RR --attempt 1 \
  --model /absolute/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf \
  --llama-server /absolute/llama-server \
  --cuda-backend /absolute/libggml-cuda.so \
  --output-root /absolute/new-output-root
```

The supervisor stages immutable tuple snapshots, starts and attests the exact
server, creates and pins `attempt/`, validates the exact SLURM identity grammar
donated by the byte-bound wrapper, executes exact argv
`scontrol show job -dd <job-id>`, and calls the merged direct driver with the
unchanged adapter API. The wrapper is never launched. Scheduler finalization
remains pending.

## Success outputs

The output root contains the staged input snapshots, runtime stage, process
attestation, server log, cleanup receipt, and one supervisor-created `attempt/`
directory. Success requires:

- `attempt/SCONTROL_IN_JOB_V1.txt` and
  `attempt/SLURM_IDENTITY_AND_SNAPSHOT_V1.json` — in-job scheduler evidence only,
  still pending post-job finalization;
- `attempt/ATTEMPT_CAPTURE_V1.json` — unchanged adapter capture, still pending;
- `attempt/DIRECT_ROUTE_BRIDGE_BINDING_V1.json` — separate driver/runtime/prompt
  binding for the same tuple;
- `SERVER_CLEANUP_V1.json` — wrapper `NONINVOKED` and the owned server process
  group absent.

After a post-capture failure, success capture is absent and the bridge writes
`ATTEMPT_CAPTURE_CANNOT_CHECK_V1.json` plus its failure-binding receipt. A
pre-capture failure writes only preflight failure metadata and cannot masquerade
as a generation capture.

## Remaining boundary

The unchanged Runner V2 run-plan and adapter-ledger schemas do not natively
contain the bridge extension. The per-tuple receipt closes the local bridge
check, but no complete 918-receipt bridge index/finalizer exists in this lane.
Therefore do not promote separate bridge evidence into the native V2 seal.
Retain:

```text
task_fit_status = CANNOT_CHECK_BEFORE_TASK_OPENING
allocation_status = CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION
semantic_choice_sensitivity = NOT_ESTABLISHED
production_admissibility = CANNOT_CHECK
scientific_authority_delta = NONE
```

## Verification

From a clean checkout at the immutable PR head, use an external bytecode cache:

```bash
rtk python3 -m py_compile \
  development/p1-scienceagentbench-direct-route-slurm-preflight-v1-2026-08-24/direct_route_slurm_preflight_v1.py \
  development/p1-scienceagentbench-direct-route-slurm-preflight-v1-2026-08-24/validate_direct_route_slurm_preflight_v1.py
rtk bash -n development/p1-scienceagentbench-direct-route-slurm-preflight-v1-2026-08-24/run_direct_route_slurm_preflight_v1.sh
rtk python3 development/p1-scienceagentbench-direct-route-slurm-preflight-v1-2026-08-24/validate_direct_route_slurm_preflight_v1.py
rtk sh -c 'cd development/p1-scienceagentbench-direct-route-slurm-preflight-v1-2026-08-24 && shasum -a 256 -c SHA256SUMS'
rtk git diff --check origin/main...HEAD
```

The validation command is synthetic only. Do not run pytest or CI for this
bounded `[skip ci]` lane, and do not merge automatically.
