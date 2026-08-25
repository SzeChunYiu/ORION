# Paper 1 backend canonical-map discriminator V5 freeze

## Status and authority boundary

This additive packet is frozen at merged-main base
`cf002879df0aac27d269d6fa1477818ab507d15a`. Its status is exactly
`FROZEN_NOT_EXECUTED`, and `submission_authority=false`.

No V5 deployment or live job has occurred. This packet authorizes no SSH,
submission, protected-body access, protected retry, tokenization, completion,
generation, evaluator invocation, outcome access, production admission, or
scientific claim. Any future body-free V5 job requires separate owner
authorization after a clean-checkout validation, immutable deployment binding,
and fresh live absence checks for every frozen root.

## Exact adverse predecessor

`JOB_3537910_PREDECESSOR_BINDING_V1.json` preserves job `3537910` as the
adverse body-free predecessor. The four merged-main result surfaces are:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `JOB_3537910_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V1.json` | 1,464 | `cf62273ddb03288e23a7933332367794f0712e14103c4fe7fdb99579d112448a` |
| `JOB_3537910_BODY_FREE_CANNOT_CHECK_CERTIFICATE_V1.json` | 4,644 | `c275878988c6bb2ce0ea9ca4dccca068bcd7678807cd79865e30dbe2e4176402` |
| `OFFLINE_GPU_IDENTITY_FAILURE_CLASSIFICATION_V1.json` | 4,512 | `c3138f01a7c83c4740890c0dcddfc0f693f0153e8f7249c51da11f106bca2aa7` |
| `RESULT_EXPORT_MANIFEST_V1.json` | 3,230 | `c236c934e9f4e261fc631417393f3d2086d7b6ad2ab07d616e1e618b5575d414` |

Job `3537910` remains `FAILED`, exit `1:0`, elapsed 86 seconds on `cg14`,
with one scheduler-allocated A40 GRES. Its exact terminal was:

```text
P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK failure_code=GPU_IDENTITY_INVALID detail_sha256=a31dfb1a2c932320ecf692f380dfd8aca87a7afb107026347fed63e2c4a490c4
```

The completed stages were exactly:

```text
CONTRACT_BOUND
RUNTIME_FILES_BOUND
SERVER_STARTED
SERVER_READY_BODY_FREE
CANONICAL_MAP_ATTESTATION_1
SERVER_CLEANUP_PASS
```

The sole positive result is a fresh, body-free, first-attestation
code-semantic witness. Under the executed V4 module, the exact server process,
argv, allowlisted environment, loopback listener, and frozen
server/backend/model identities passed under only their allowed logical or
canonical paths with matching device/inode identity. The exact observed paths,
segments, and attestation object were not retained. This is not a field-level
reconstruction, a full discriminator PASS, a causal repair, or a promotion of
job `3537893` or `3537910`.

GPU identity, the second map attestation, byte-identical reattestation, final
runtime-file rebind, and final listener rebind were not completed. Production
admissibility remains `CANNOT_CHECK`; scientific-authority delta remains
`NONE`. No protected packet or prompt body, tokenize request, completion
request, generation, evaluator, or official outcome operation occurred.

## V4 residual that V5 discriminates

The exact V4 static-source classification proves that the failure used one of
two dynamic nonempty-`nvidia-smi`-stderr branches:

1. nonzero return with nonempty stderr; or
2. zero return with nonempty stderr.

V4 retained neither the return code nor the direct stdout/stderr bindings, so
the branch and stream contents remain `CANNOT_CHECK`. Historical success on a
different job does not rank those alternatives and is not substituted for
fresh evidence.

## Smallest fail-closed V5 policy

V5 keeps the exact absolute `nvidia-smi` argv, filtered environment, 30-second
timeout, singular visible-device gate, UUID grammar, and exact `NVIDIA A40`
model gate. Every completed `nvidia-smi` call retains a `gpu_capture` object:

```text
status=COMPLETED
argv=<exact frozen argv>
return_code=<integer>
stdout={bytes,sha256}
stderr={bytes,sha256}
stdout_parse_attempted=<boolean>
```

The decision order is immutable:

| Condition | `failure_subcode` / action | Parse stdout? |
| --- | --- | --- |
| invalid `SLURM_JOB_ID` | `SLURM_JOB_ID_INVALID` CANNOT_CHECK | no call |
| invalid `CUDA_VISIBLE_DEVICES` | `CUDA_VISIBLE_DEVICES_INVALID` CANNOT_CHECK | no call |
| execution error | `NVIDIA_SMI_EXECUTION_ERROR` CANNOT_CHECK | no completed call |
| timeout | `NVIDIA_SMI_TIMEOUT` CANNOT_CHECK | no completed call |
| completed, return code nonzero | `NVIDIA_SMI_NONZERO_RETURN` CANNOT_CHECK with `gpu_capture` | no |
| completed, return code zero, stderr nonempty | `NVIDIA_SMI_STDERR_NONEMPTY` CANNOT_CHECK with `gpu_capture` | no |
| completed, return code zero, stderr empty | parse the exact stdout grammar | yes |

Only return code zero plus empty stderr is parse-eligible. UTF-8, framing,
row-count, row-grammar, and model failures retain the completed capture and use
their distinct typed subcodes. A successful receipt retains the same capture
under `gpu.nvidia_smi`.

V5 does **not** tolerate nonempty stderr. Treating a zero-return valid A40 row
with nonempty stderr as PASS would be a separate policy change requiring its
own justification and retained diagnostic binding; it is outside this freeze.

## Fresh immutable roots

The frozen paths are:

```text
ROOT=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v5-20260825
RUN=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v5-20260825
OUTPUT=$RUN/evidence
LOG=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v5-20260825-submit-logs
```

Their live absence was not probed while developing this freeze and is recorded
as `CANNOT_CHECK_NOT_LIVE_PROBED`. Before any separately authorized
deployment, require ROOT, RUN, OUTPUT, and LOG all absent. A stale empty path is
reuse and stops. Deploy a new read-only snapshot; never repair it in place.
With `umask 077`, the operator may create only the separate LOG root mode
`0700`; the trampoline creates RUN mode `0700`, and the core alone creates
OUTPUT.

## Runtime and result freeze

The V5 contract retains the V4 server, backend, model, argv, loader
environment, one-A40 scheduler geometry, loopback-only network gate, body-free
request allowlist (`GET /health`, `GET /slots`), map identity gates, cleanup
gate, and create-only receipt custody. The only scientific-method delta is the
typed GPU capture above.

The output names are:

```text
BACKEND_CANONICAL_MAP_DISCRIMINATOR_RESULT_V2.json
BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V2.json
```

The success and failure terminals are:

```text
P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_V2_PASS
P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_V2_CANNOT_CHECK failure_code=<CODE> detail_sha256=<LOWERCASE_SHA256>
```

Exactly one mode-`0400` receipt may be created under a new OUTPUT, and OUTPUT
must be mode `0500` afterward. A completed-call failure receipt must carry both
stream byte/hash bindings and the exact return code; an absent or partial
capture is CANNOT_CHECK, never PASS.

## Accounting

- Prior protected scheduler cost: 90 GPU-seconds.
- Job `3537910` body-free scheduler cost: 86 GPU-seconds.
- Cumulative cost before V5: 176 GPU-seconds, reported as `90 protected + 86
  body-free`.
- Protected infrastructure submissions completed: three.
- Protected generation attempts consumed: zero.
- Body-free discriminator submissions completed: one.
- V5 submissions and V5 scheduler GPU-seconds: zero while status is
  `FROZEN_NOT_EXECUTED`.

Job `3537910` is not protected infrastructure ordinal four, not protected
generation ordinal one, and not a hidden sample. A future body-free V5 job, if
separately authorized, must be accounted for separately without erasing any
prior cost.

## Frozen artifact and validation topology

The final export contains nine payload files: the contract, output schema,
predecessor binding, development packet, handoff, V2 core, V2 zero-argv
trampoline, direct hostile validator, and synthetic-validation receipt.
`BODY_FREE_EXPORT_MANIFEST_V2.json` binds those nine payloads while excluding
itself and `SHA256SUMS`; `SHA256SUMS` binds the nine payloads plus the manifest
and excludes only itself.

The direct validator must pass 32 synthetic tests under normal, optimized,
isolated, and exact-system isolated Python. Its exact terminal is:

```text
P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_V2_SYNTHETIC_VALIDATION_PASS tests=32 protected_bodies=0 tokenize=0 completion=0 generation=0 jobs=0 outcomes=0 production_admissibility=CANNOT_CHECK scientific_authority=NONE
```

These are offline, body-free conformance results. They submit no job and add no
live discriminator, production, outcome, or scientific authority.

## Reopen conditions

Reopen and stop if any predecessor byte/hash differs; if the V5 base, contract,
module, runner, output schema, or fresh paths drift; if a completed call can
omit return code or either stream binding; if stderr is tolerated; if parsing
can begin before return-zero/empty-stderr eligibility; or if any protected or
task-bearing route becomes reachable.
