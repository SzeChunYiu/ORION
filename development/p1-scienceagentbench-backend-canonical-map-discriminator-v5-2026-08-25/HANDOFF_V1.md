# Paper 1 backend canonical-map discriminator V5 operator handoff

## Frozen, not authorized, not executed

This lane is bound to merged-main base
`cf002879df0aac27d269d6fa1477818ab507d15a`. Require exact status
`FROZEN_NOT_EXECUTED` and `submission_authority=false`.

Nothing in this lane authorizes SSH, deployment, a scheduler submission,
protected-body access, a protected retry, generation, evaluation, outcome
access, or production admission. A future body-free V5 job requires a separate
owner authorization after all gates below pass in a clean checkout.

## Preserved job-3537910 boundary

Job `3537910` remains an immutable adverse predecessor:

```text
state=FAILED
exit=1:0
elapsed=00:01:26
node=cg14
allocated=one A40 GRES
terminal=P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK failure_code=GPU_IDENTITY_INVALID detail_sha256=a31dfb1a2c932320ecf692f380dfd8aca87a7afb107026347fed63e2c4a490c4
```

Verify these exact merged-main bindings before reuse:

```text
cf62273ddb03288e23a7933332367794f0712e14103c4fe7fdb99579d112448a  JOB_3537910_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V1.json  bytes=1464
c275878988c6bb2ce0ea9ca4dccca068bcd7678807cd79865e30dbe2e4176402  JOB_3537910_BODY_FREE_CANNOT_CHECK_CERTIFICATE_V1.json  bytes=4644
c3138f01a7c83c4740890c0dcddfc0f693f0153e8f7249c51da11f106bca2aa7  OFFLINE_GPU_IDENTITY_FAILURE_CLASSIFICATION_V1.json  bytes=4512
c236c934e9f4e261fc631417393f3d2086d7b6ad2ab07d616e1e618b5575d414  RESULT_EXPORT_MANIFEST_V1.json  bytes=3230
```

The first mapping attestation is the only positive witness. Do not infer
retained observed paths or segments, GPU identity, a second attestation, final
rebind, full discriminator PASS, causal repair, production admissibility, or
scientific authority.

## Frozen V5 paths

```text
ROOT=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v5-20260825
RUN=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v5-20260825
OUTPUT=$RUN/evidence
LOG=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v5-20260825-submit-logs
```

The freeze did not live-probe these roots. Before any separately authorized
deployment, confirm ROOT, RUN, OUTPUT, and LOG are all absent. Any existing
path, including an empty directory or symlink, stops the operation. Do not use
any V1-V4 root.

Deploy only a new immutable clean-checkout snapshot at ROOT. With `umask 077`,
create only LOG mode `0700`. Leave RUN and OUTPUT absent: the exact V2
trampoline creates RUN, and the V2 core creates OUTPUT.

## Clean-checkout validation gate

From this lane, without pytest, require all of the following:

```bash
bash -n run_backend_canonical_map_discriminator_v2.sh
python3 -B validate_backend_canonical_map_discriminator_v2.py
python3 -O -B validate_backend_canonical_map_discriminator_v2.py
python3 -I -S -B validate_backend_canonical_map_discriminator_v2.py
/usr/bin/python3 -I -S -B validate_backend_canonical_map_discriminator_v2.py
shasum -a 256 -c SHA256SUMS
```

Require the exact V2 synthetic validation PASS terminal and zero protected-body,
tokenize, completion, generation, job, and outcome counts in every mode. The
terminal must report exactly `tests=32`.
Verify the final packet manifest and `SHA256SUMS` after all payload hashes are
frozen. Any mismatch stops; do not edit a deployed copy.

Also require:

1. contract base exactly `cf002879df0aac27d269d6fa1477818ab507d15a`;
2. contract status exactly `FROZEN_NOT_EXECUTED`;
3. `submission_authority=false`;
4. exact predecessor binding and all four result hashes;
5. exact server, backend, model, argv, environment, map, listener, allocation,
   and cleanup fields;
6. runner byte/hash binding to the final module and contract; and
7. no protected packet path or task-bearing HTTP route anywhere in the live
   code path.

## V5 GPU decision matrix

Every completed `nvidia-smi` call must retain:

```text
gpu_capture.status=COMPLETED
gpu_capture.argv=<exact frozen argv>
gpu_capture.return_code=<integer>
gpu_capture.stdout={bytes,sha256}
gpu_capture.stderr={bytes,sha256}
gpu_capture.stdout_parse_attempted=<boolean>
```

- Nonzero return: `NVIDIA_SMI_NONZERO_RETURN`, typed CANNOT_CHECK, no parse.
- Zero return plus nonempty stderr: `NVIDIA_SMI_STDERR_NONEMPTY`, typed
  CANNOT_CHECK, no parse.
- Only zero return plus empty stderr reaches UTF-8/framing/one-row/UUID/A40
  parsing.
- Parse failures retain the completed capture and their distinct subcodes.
- Success retains the capture at `gpu.nvidia_smi`.

Precompletion subcodes are `SLURM_JOB_ID_INVALID`,
`CUDA_VISIBLE_DEVICES_INVALID`, `NVIDIA_SMI_EXECUTION_ERROR`, and
`NVIDIA_SMI_TIMEOUT`; because no call completed, they omit `gpu_capture`.

Nonempty stderr is not tolerated by V5. Do not relabel zero-return plus
nonempty stderr as PASS even if stdout appears valid. That would be a separate
policy change, not a repair supported by job `3537910`.

## Separately authorized submission shape

This section freezes a possible future operator shape; it grants no authority
to execute it. After a separate authorization, fresh-root proof, and immutable
deployment receipt, submit the zero-argv V2 trampoline from ROOT with
`--export=NIL`, exact chdir, and LOG-only scheduler streams. The trampoline's
embedded `#SBATCH` geometry is one A40, one node/task, eight CPUs, 64 GiB, and
one hour. Do not use `--wrap` or pass argv to the trampoline.

The trampoline failure prefix is:

```text
P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_TRAMPOLINE_V2_CANNOT_CHECK
```

The core receives exactly:

```text
--output-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v5-20260825/evidence
```

The core may issue only `GET /health` and `GET /slots` to exact loopback
`127.0.0.1:8080`. It may not open protected packet or prompt bodies and may not
send tokenize or completion requests.

## Receipt gate

Require exactly one create-only mode-`0400` file under new OUTPUT:

```text
BACKEND_CANONICAL_MAP_DISCRIMINATOR_RESULT_V2.json
BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V2.json
```

OUTPUT must become mode `0500`. The exact terminal prefixes are:

```text
P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_V2_PASS
P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_V2_CANNOT_CHECK
```

A PASS is admissible only after return-zero/empty-stderr parsing, singular A40
identity, two byte-identical mapping attestations, final runtime-file and
listener rebind, frozen contract rebind, and confirmed process/process-group
cleanup. Any other result is CANNOT_CHECK and must be preserved without an
in-place retry.

## Accounting and interpretation

Before any V5 execution, cumulative scheduler cost is 176 GPU-seconds:
`90 protected + 86 body-free`. Protected infrastructure submissions remain
three, protected generation attempts remain zero, and completed body-free
discriminator submissions remain one. V5 currently adds zero submissions and
zero GPU-seconds.

Even a future V5 PASS would be one body-free runtime/map/GPU witness. It would
not repair or promote jobs `3537893` or `3537910`, authorize a protected retry,
establish task execution or official evaluation, support production admission,
or establish model or ORION superiority.
