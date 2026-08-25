# Paper 1 V5 job-3537915 result handoff

## Frozen result

Preserve job `3537915` exactly:

```text
state=FAILED
exit=1:0
elapsed=00:01:24
node=cg14
terminal=P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_V2_CANNOT_CHECK failure_code=GPU_IDENTITY_INVALID detail_sha256=37a3b93da155ad4641b63864fd78781f9144c3813a2b02fae9ba0924a98025a2
```

The result is `CANNOT_CHECK_BACKEND_CANONICAL_MAP_DISCRIMINATOR` with
production admissibility `CANNOT_CHECK` and scientific-authority delta `NONE`.
Do not rerun in place, overwrite the create-only receipt, reinterpret the job
as PASS, or promote its first mapping attestation.

## Exact new discriminator

V5 resolves the V4 dynamic branch only:

```text
failure_subcode=NVIDIA_SMI_NONZERO_RETURN
return_code=6
stdout.bytes=22
stdout.sha256=cda3a19e75eacfb91b9b2c2f85080bddea247dd500abec231f6212e3d8fff3bd
stderr.bytes=76
stderr.sha256=0a0daacddae467fe5f39a91401c306cb9b469459f8ba6d7e78d485c2d925c76a
stdout_parse_attempted=false
```

NVIDIA documents return code 6 as a query that could not find an object. It
does not identify which object or why. The string `No devices were found\n`
matches the retained stdout byte/hash pair, but raw stdout was not retained;
record it only as a declared-candidate hash match. Do not guess or reconstruct
stderr.

## Evidence surfaces

Require these raw bindings:

```text
2b421bb1ed442ac15689975658b4a4320611276cc4dfad6649d9b85f68d67cf3  JOB_3537915_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V2.json  bytes=1883
c80d3ab5044472895eace3c7faa096eaa1f7441108696d98b51c50a10f53870e  slurm-3537915.err  bytes=172
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  slurm-3537915.out  bytes=0
```

`DEPLOYMENT_PRE_SUBMIT_EVIDENCE.txt` binds the merged-main archive, deployed
files, custody, three LUNARC validator modes, and fresh-root gates.
`POST_MERGE_CLEAN_ARCHIVE_EVIDENCE.txt` separately binds all four frozen host
modes to a clean archive of the same merge; do not call those four runs remote
LUNARC validation. `SUBMISSION_EVIDENCE.txt` binds scheduler fields and the job
ID. `SUBMIT_LINE_AND_RESIDUAL_EVIDENCE.txt` binds Slurm's retained exact
`SubmitLine`, including `--export=NIL`, and an explicit zero residual-process
count.
`JOB_3537915_OPERATOR_EVIDENCE.txt` binds final accounting, scheduler record,
logs, receipt custody/content, and cleanup absence.

The result certificate and failure classification are derived surfaces. Their
validators must rebind the raw evidence, the merged V5 core/contract/runner,
the job-3537910 predecessor boundary, and every zero-activity claim. A derived
PASS is validation of provenance and classification only, never a live
discriminator PASS.

## Completed and incomplete stages

Completed exactly:

```text
CONTRACT_BOUND
RUNTIME_FILES_BOUND
SERVER_STARTED
SERVER_READY_BODY_FREE
CANONICAL_MAP_ATTESTATION_1
SERVER_CLEANUP_PASS
```

Not completed: GPU identity, second mapping attestation, byte-identical
reattestation, final runtime-file rebind, final listener rebind, and a full V5
PASS. Cleanup succeeded and no residual server/discriminator process was
observed.

## Cost and activity boundary

After job `3537915`:

```text
protected_gpu_seconds=90
body_free_gpu_seconds=170
combined_gpu_seconds=260
protected_infrastructure_submissions=3
body_free_discriminator_submissions=2
protected_generation_attempts=0
protected_bodies_opened=0
tokenize_requests=0
completion_requests=0
generation_invocations=0
official_outcomes_opened=0
```

## V6 successor rule

Do not reuse any V1-V5 ROOT, RUN, OUTPUT, LOG, receipt, or upload path. A V6
successor requires a new freeze, new immutable roots, a merged-main clean
archive, fresh absence proof, and separate authorization.

The next body-free job should compare GPU visibility before server launch,
after readiness/first mapping attestation, and after cleanup. It may retain
exact call bindings, allowlisted scheduler visibility variables, safe metadata
for `/dev/nvidia*`, and bounded cgroup classification. It may not read device
bodies, protected packets, prompts, task inputs, completions, generations,
evaluator data, or outcomes.

Stop and preserve the first result. A pre-server failure localizes the issue to
allocation/cgroup/device visibility; pre-server success followed by post-ready
failure isolates a server-lifecycle transition; cross-phase instability
remains typed `CANNOT_CHECK`. None of those outcomes alone supports a task or
model claim.
