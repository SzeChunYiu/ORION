# Paper 1 protected RR1 direct-route freeze V1 handoff

## Terminal

```text
P1_SAB_PROTECTED_RR1_DIRECT_ROUTE_V1_FROZEN_PREPARED_NOT_SUBMITTED
```

This additive lane prepares exactly one discriminator and does not submit it:

```text
task_id=1
arm=RR
attempt=1
seed=101
allocation=one LUNARC NVIDIA A40
```

Submission, merge, evaluator access, outcome access, production use, and a
scientific claim are not authorized by this packet.

## Bound public inputs

- base/integration commit: `674152066986d5e2a480ed95ca65431ff0f25b6a`
- PR 1198 source head: `9f8bc8294a480b6e8daeac1bde78770dc4e4a531`
- job 3537617 protected prompt-fit receipt:
  - bytes: `539479`
  - SHA-256: `4ff1163b7e405b5881a7d2d4aea10bb634aaf49ada7bfc0c02159a1b5e18fa83`
- job 3537617 successor result V2:
  - bytes: `5728`
  - SHA-256: `63f818cbf0558fb53201f7e7b4b2b97cfae03b0687fbaca91d3d64586df70ce9`
- source `SHA256SUMS`:
  - bytes: `1498`
  - SHA-256: `bc894b82b7635db206f72ef1fb82a28132a272e36e25330c249b5d1c0695ea7f`
- full Runner V2 plan: `RUN_PLAN_V1.json` (102 tasks, three arms,
  three attempts; not a one-row substitute)
- owner selection: exact byte-for-byte JSON object from
  `DIRECT_ROUTE_FREEZE_CONTRACT_V1.json["budget_owner_selection_interface"]`
- runtime binding: exact direct-route runtime object

Job 3537617 established task 1 RR0 static fit at 235 prompt tokens plus a 1024
output cap in a 32768-token context. It did **not** establish RR1 fit; RR1 stayed
`CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_REQUIRED`.

## Private inputs kept outside Git

The operator must stage two exact canonical JSON files in a private `0700`
directory. Their bodies must not be copied into the repository, PR, issue,
terminal transcript, or model context.

| input | exact bytes | exact SHA-256 |
|---|---:|---|
| masked packet | 622 | `405f5836a21192d0a6d21e4b85143865fec8a2fb7cd9a4eb62100862b9d1a3df` |
| recovered packet | 1681 | `3fce9e45e3012845d7dec2e343c224b43a4d79dea0c1192e5bf1972652733722` |

The supervisor rejects a newline, alternate JSON serialization, symlink, byte
count mismatch, or hash mismatch. The current preparation does not fetch or
open those bodies.

## What the additive successor changes

The merged direct-route bridge already seals RR0 state and reproduces RR1, but
it sends RR1 `/completion` before it can learn `timings.prompt_n`. This successor
keeps the merged donors unchanged and inserts the missing temporal gate:

1. freeze and hash every public/private input plus runtime before any completion;
2. execute RR0 through the merged direct driver;
3. strict-parse and canonicalize RR0 state;
4. reproduce the exact RR1 prompt;
5. send that prompt three times only to loopback `POST /tokenize` using
   `add_special=true, parse_special=true` under the same remaining raw deadline;
6. require byte-identical raw responses and identical integer token arrays;
7. require `prompt_tokens + 7168 <= 32768`;
8. only then send RR1 `/completion`;
9. require completion `timings.prompt_n` to equal the pre-tokenized count; and
10. retain only hashes/counts, never prompt, response, packet, or token-ID bodies.

Malformed tokens, repeat disagreement, raw-byte disagreement, overflow,
deadline expiry, and tokenize/completion count disagreement fail closed. If the
adapter capture exists, the attempt writes a typed `CANNOT_CHECK` sidecar. RR1
completion is never sent when the pre-tokenize gate fails.

## Frozen nonexecuted allocation command shape

The launcher is `run_protected_rr1_direct_route_v1.sh`. It fixes account
`lu2026-2-51`, partition `gpua40i`, `gpu:a40:1`, one node, one task, eight CPUs,
64 GiB, one hour, and `#SBATCH --signal=B:TERM@120` so Python receives a
two-minute cleanup/failure-receipt window before scheduler termination. It
contains no submission command.

An authorized operator would pass only absolute paths for:

```text
--masked-packet <private exact canonical MASKED_PACKET.json>
--recovered-packet <private exact canonical RECOVERED_PACKET.json>
--model <Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf>
--llama-server <exact llama-server b10434 executable>
--cuda-backend <exact libggml-cuda.so>
--output-root <new private 0700 output directory>
```

Expected runtime hashes:

```text
model bytes=18556689568
model sha256=fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad
llama-server sha256=234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b
CUDA backend sha256=fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb
llama.cpp version=b10434
llama.cpp commit=7e4c0a96880dae4fc4268ad441f8a6446bd5460a
```

No command in this handoff was executed against LUNARC and no job ID exists for
this discriminator.

After attempt capture and verified server cleanup, a live success would print
only this body-free terminal:

```text
P1_SAB_PROTECTED_RR1_ONE_TUPLE_CAPTURED__SCHEDULER_FINALIZATION_PENDING
```

## Live output boundary

All live outputs are private and excluded from Git. The server's stdout/stderr
is discarded rather than retained, preventing accidental server-side body logs.
The bridge receipts retain hash-only completion-response bindings and hash-only
dynamic tokenization bindings. Known credential variables are unset by the
launcher, and the llama-server and `nvidia-smi` child processes receive only a
narrow noncredential environment allowlist.

Required success-path files include:

```text
STAGED_RUNTIME_INPUT_V1.json
PROCESS_ATTESTATION_V1.json
GPU_ALLOCATION_IDENTITY_V1.json
attempt/SCONTROL_IN_JOB_V1.txt
attempt/SLURM_IDENTITY_AND_SNAPSHOT_V1.json
attempt/DYNAMIC_RR1_PRETOKENIZE_BINDING_V1.json
attempt/DIRECT_ROUTE_BRIDGE_BINDING_V1.json
attempt/ATTEMPT_CAPTURE_V1.json
SERVER_CLEANUP_V1.json
```

A failure after adapter capture substitutes
`ATTEMPT_CAPTURE_CANNOT_CHECK_V1.json` and
`DIRECT_ROUTE_BRIDGE_FAILURE_BINDING_V1.json` for success capture/binding.

## Separate one-tuple post-job finalization gate

Do not call the merged 918-tuple finalizer for this discriminator. The required
boundary is frozen in `ONE_TUPLE_FINALIZATION_CONTRACT_V1.json`.

After a terminal scheduler state, an authorized finalizer must capture exact raw
post-job `sacct`, `scontrol show job -dd`, scheduler configuration, and canonical
scheduler export bytes; bind their hashes to the in-job SLURM identity/snapshot;
confirm terminal state and exit code; bind the one visible A40 and GPU UUID;
and record exclusivity/non-overlap as confirmed scheduler evidence or typed
`CANNOT_CHECK`. It must also verify the attempt capture or typed failure, the
dynamic RR1 pre-tokenize receipt, and whole server process-group absence.

Even a passing one-tuple gate has only scheduler/capture metadata authority:

```text
runner_v2_population_ledger_status=NOT_FINALIZED_918_TUPLES
production_admissibility=CANNOT_CHECK
scientific_authority_delta=NONE
```

## Validation

The validator is synthetic and uses invented packets/responses only. It covers
the TDD red/green path, exact source provenance, full-plan binding, dynamic
request order, malformed/repeated/overflow/deadline failures, typed sidecars,
raw response hashes, exact held-descriptor donor loading, same-UID staged-input
swap/restore defense, one-A40 capture, privacy exclusions, and artifact hashes.

No live generation, job submission, protected body opening, evaluator, outcome,
credential, or external API occurs during validation.
