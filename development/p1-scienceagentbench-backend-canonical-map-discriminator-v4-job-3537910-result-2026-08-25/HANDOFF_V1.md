# Paper 1 body-free job 3537910 result handoff

## Frozen result

Job `3537910` is an immutable body-free CANNOT_CHECK from merged commit
`8e84ae99af5122ce6f8e641955e196c27aed07c8`:

```text
state=FAILED
exit=1:0
elapsed=00:01:26
node=cg14
allocated=one A40 GRES
terminal=P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK failure_code=GPU_IDENTITY_INVALID detail_sha256=a31dfb1a2c932320ecf692f380dfd8aca87a7afb107026347fed63e2c4a490c4
```

Do not relabel this job PASS, retry its roots, or infer an unretained exact GPU
diagnostic. Preserve the raw receipt, scheduler/operator evidence, empty Slurm
stdout, exact Slurm stderr, hashes, modes, and cleanup fields in this lane.

## What passed

The live receipt reached `CANONICAL_MAP_ATTESTATION_1`. Under the executed
code, that is one fresh first-attestation witness for exact process, argv,
environment, loopback listener, and frozen server/backend/model mapping
identities under their allowed logical/canonical path sets. This narrows the V3
pathname residual but does not repair or promote job `3537893`.

## What did not pass

`GPU_IDENTITY_BOUND`, the second mapping attestation, byte-identical
reattestation, final full-file hash/custody rebind, and final listener rebind
were not completed. Production admissibility and scientific authority remain
`CANNOT_CHECK` and `NONE`. No protected body, prompt, tokenize, completion,
generation, evaluator, or outcome operation occurred.

## Offline diagnosis

Run without pytest:

```bash
python3 -B classify_gpu_identity_failure_v1.py
python3 -B validate_gpu_identity_failure_classification_v1.py
python3 -O -B validate_gpu_identity_failure_classification_v1.py
python3 -I -S -B validate_gpu_identity_failure_classification_v1.py
python3 -B validate_job_3537910_body_free_cannot_check_certificate_v1.py
python3 -O -B validate_job_3537910_body_free_cannot_check_certificate_v1.py
python3 -I -S -B validate_job_3537910_body_free_cannot_check_certificate_v1.py
shasum -a 256 -c SHA256SUMS
```

Require the exact terminal prefix
`P1_SAB_GPU_IDENTITY_FAILURE_CLASSIFICATION_PASS` and require the generated
classification to equal
`OFFLINE_GPU_IDENTITY_FAILURE_CLASSIFICATION_V1.json` byte-for-byte.

The classification proves only that the executed failure used a dynamic
nonempty-`nvidia-smi`-stderr branch. It cannot distinguish zero from nonzero
return because V4 did not retain return code or direct stream bindings.

## Bound artifacts and external dependency

- `JOB_3537910_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V1.json` is the
  raw 1,464-byte live receipt.
- `JOB_3537910_BODY_FREE_CANNOT_CHECK_CERTIFICATE_V1.json` binds the job,
  first-attestation scope, cleanup, zero counters, scheduler cost, and retained
  sources without promoting the job.
- `OFFLINE_GPU_IDENTITY_FAILURE_CLASSIFICATION_V1.json` is the deterministic
  static-source classification.
- `RESULT_EXPORT_MANIFEST_V1.json` binds all 13 payload files. `SHA256SUMS`
  binds those payloads plus the manifest and excludes only itself.

The classifier's sibling-lane dependency is
`../p1-scienceagentbench-backend-canonical-map-discriminator-v4-2026-08-25/backend_canonical_map_discriminator_v1.py`,
exactly 59,609 bytes with SHA-256
`59780ecb75ffc47f8f6c15eae239a5570d7bebb66cfbaf573368affaab1f8219`.
Its deployed copy is bound to merged execution commit
`8e84ae99af5122ce6f8e641955e196c27aed07c8`.

## Next bounded action

Develop and independently review a V5 GPU capture that retains return code and
stdout/stderr byte/hash bindings. The smallest evidence-derived policy keeps
nonzero return and zero-return/nonempty-stderr as distinct typed CANNOT_CHECK
outcomes; only zero-return/empty-stderr reaches the exact one-A40 parser.
Tolerating nonempty stderr after a valid parse would be a separate policy change
requiring its own justification and retained stderr binding. A full V5 body-free
job requires a new immutable packet, fresh ROOT/RUN/OUTPUT/LOG, and separate
authorization. This packet itself authorizes no submission and no protected
retry.
