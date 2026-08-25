# Paper 1 V8 job 3538042 positive GPU-visibility result (lane C)

## Exact result

The frozen V8 diagnostic lane was deployed from merge commit
`123a75b5663a77290741ae7f5c24490954118f4d`. Its clean selective archive
was 450,560 bytes with SHA-256
`ef795324bda3293e74c19b4999c08bd5d250770be2f08983fa56d79a653691a2`,
55 members, 50 regular files, and 5 directory entries. Body-free Slurm job
`3538042` then completed on `cg15` with one A40 GRES:

```text
job=3538042
state=COMPLETED
exit=0:0
elapsed=3
start=2026-08-25T08:10:43
end=2026-08-25T08:10:46
node=cg15
allocation=one A40 GRES
scheduler GPU-seconds=3
decision=VISIBLE_A40_IDENTITY_BOUND
terminal=P1_SAB_GPU_VISIBILITY_DIAGNOSTIC_V1_PASS decision=VISIBLE_A40_IDENTITY_BOUND
```

The receipt binds exactly one process-visible GPU. The list, unscoped query,
and `--id=0` scoped query all returned code 0 with empty stderr and the same
identity:

```text
index=0
uuid=GPU-06bb5356-4a6f-8c40-d27d-a0de37505a16
name=NVIDIA A40
```

The exact `nvidia-smi -L` stdout is 67 bytes with SHA-256
`68362ead8006fec11a6aadd27bce4ca3f7b8055951a60929af377afccb8f5b0f`.
The exact unscoped and scoped identity stdout is 56 bytes with SHA-256
`cc5322d6b5896f8ac36c0cd313c9670861c2a2a66ad5ad6a4a30bc6537dc18e9`.

## Custody observations

Submission evidence was retained with recorded local mtime
`2026-08-25T08:10:43+0200`. Its first line binds job `3538042`, zero entrypoint
arguments, submission from the exact frozen ROOT, and pre-submission RUN and
OUTPUT absence.

At first custody, recorded local mtime `2026-08-25T08:11:19+0200`, Slurm had
already reported `COMPLETED`, exit `0:0`, elapsed 3 seconds, and both scheduler
streams were present. RUN, OUTPUT, and both possible receipt files were
observed absent. At receipt custody, recorded local mtime
`2026-08-25T08:12:34+0200`, RUN was present mode `0700`, OUTPUT was sealed mode
`0500`, and the success receipt was present mode `0400`.

The two custody-record mtimes are exactly 75 seconds apart. That interval is
classified only as:

```text
OBSERVED_FILESYSTEM_VISIBILITY_LATENCY_ONLY__NOT_JOB_RUNTIME_CORE_RUNTIME_CAUSAL_OR_FAILURE_EVIDENCE
```

It is not the job runtime, diagnostic-core runtime, failure evidence, or a
causal observation. The authoritative scheduler elapsed time is 3 seconds.

The success receipt is 9,896 bytes with SHA-256
`dfb40dd1565cd73533d320aa325bf28386b6478a129d01f2fa7fb1826a09daee`.
`JOB_3538042_RECEIPT_CUSTODY.txt` embeds an exact byte-for-byte copy of that
receipt between its receipt markers. The raw stdout is 77 bytes with SHA-256
`8230b7d0b95aa98e354f3e2c527fc2eb773dff4f18a99bfb05ae232f37524796`;
raw stderr is zero bytes with SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

The V8 ROOT remains sealed mode `0500`, RUN remains mode `0700`, OUTPUT remains
sealed mode `0500`, LOG remains mode `0700`, the success receipt remains mode
`0400`, and the two remote streams remain mode `0600`. Result export was
read-only with respect to the remote ROOT, RUN, OUTPUT, LOG, receipt, and
streams.

## Source and freeze bindings

This lane retains exact local copies of:

- `GPU_VISIBILITY_DIAGNOSTIC_RESULT_V1.json`: the canonical remote success
  receipt.
- `SUBMISSION_EVIDENCE.txt`: the submission receipt and initial queue state.
- `JOB_3538042_FIRST_CUSTODY.txt`: the first absence observation, exact stream
  bodies, and Slurm accounting.
- `JOB_3538042_RECEIPT_CUSTODY.txt`: final root/file custody, embedded success
  receipt, stream bindings, and Slurm accounting.
- `REMOTE_DEPLOYMENT_SCRIPT_V1.sh` and `REMOTE_SUBMIT_SCRIPT_V1.sh`: exact
  deployment and submission fixtures.
- `slurm-3538042.out` and `slurm-3538042.err`: exact raw scheduler streams.
- `JOB_3538042_GPU_VISIBILITY_RESULT_V1.json`: the canonical lane-C result and
  source bindings.

The result also binds the frozen V8 lane
`../p1-scienceagentbench-gpu-visibility-diagnostic-v8-2026-08-25` at commit
`123a75b5663a77290741ae7f5c24490954118f4d`, including the exact bytes and
SHA-256 values of its contract, synthetic-validation receipt, export manifest,
runner, and `SHA256SUMS`. The receipt binds contract SHA-256
`4065d3271a002624bddd539e25293d41c0dab74aa7444a145a5aa058533e4e31`,
scientific predecessor job `3537915` at result commit
`9ea21a1719fafbe9ab5f0d10a55dfd5f05036c67`, and V7 pre-run failure job
`3537988` at result commit `c9741a30f4d1634cbacdf79b454ae56c6eb89da5`.

## Accounting

Job `3538042` adds exactly one body-free diagnostic submission and 3 scheduler
GPU-seconds. The arithmetic is exact:

```text
protected infrastructure GPU-seconds=90
prior body-free discriminator GPU-seconds=170
prior combined scheduler GPU-seconds=260
job 3538042 scheduler GPU-seconds=3
body-free discriminator GPU-seconds after job=173
combined scheduler GPU-seconds after job=263
protected infrastructure submissions=3
body-free discriminator submissions after job=4
protected generation attempts=0
```

Thus `260 + 3 = 263` and `170 + 3 = 173`.

## Claim boundary

This is positive GPU-visibility evidence for body-free diagnostic job
`3538042` only. It shows that this job's allocated process could enumerate one
NVIDIA A40 and obtain the same identity from list, unscoped, and scoped
`nvidia-smi` commands. It does not establish:

- model execution or model start;
- any task-bearing request or task success;
- protected prompt or packet execution;
- production evidence or production admission;
- a causal explanation of any prior failure;
- ORION superiority; or
- any scientific-authority increase.

Job `3537915` is not repaired or reinterpreted. Job `3537988` is not promoted.
No protected retry is authorized. Production admissibility remains
`CANNOT_CHECK`, and scientific-authority delta remains `NONE`.

## Reopen boundary

This packet authorizes no SSH, mutation, deployment, submission, protected
access, production admission, or scientific claim. Any successor must use a
new separately authorized lane and preserve this job and its sealed remote
custody roots. Do not repair, reuse, delete, or mutate the V8 ROOT, RUN,
OUTPUT, LOG, receipt, or streams.
