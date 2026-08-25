# Paper 1 V7 job 3537988 submission-fixture failure

## Exact status

The frozen V7 lane merged at
`87a1f6f76dcefbc79d00c397a5aa9c7047a760b7`. Its clean selective archive
was deployed to the fresh V7 ROOT, sealed, validated in four modes, rechecked
for fresh RUN/OUTPUT/LOG absence, and given a new mode-`0700` LOG. Submission
then created body-free job `3537988`.

The job failed immediately in the trampoline before RUN creation:

```text
job=3537988
state=FAILED
exit=2:0
elapsed=0
node=cg15
allocation=one A40 GRES
terminal=P1_SAB_GPU_VISIBILITY_DIAGNOSTIC_TRAMPOLINE_V1_CANNOT_CHECK failure_code=SUBMIT_ROOT_INVALID detail_sha256=1e0b0ccad8cab36771b3dc63311de1f26ba7a08dc692d14a02fa47ce1780b759
RUN=ABSENT
OUTPUT=ABSENT
success_receipt=ABSENT
cannot_check_receipt=ABSENT
ROOT=SEALED_PRESERVED
LOG=0700
```

The exact failure detail is:

```text
SLURM_SUBMIT_DIR differs from the exact successor root
```

Its UTF-8 bytes are length 54 and SHA-256
`1e0b0ccad8cab36771b3dc63311de1f26ba7a08dc692d14a02fa47ce1780b759`.
The retained stdout is zero bytes with SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
The retained stderr is 172 bytes with SHA-256
`aedf4ea5358a0d37bc6f1ddbc3b78b0e392adab3a1093b241665961c2bee495c`.

## Root cause and claim boundary

The submission script invoked `/usr/bin/sbatch` outside the frozen ROOT while
passing `--chdir="$ROOT"`. Slurm uses `--chdir` for the job working directory;
it does not rewrite the submission-time `SLURM_SUBMIT_DIR`. The trampoline
requires `SLURM_SUBMIT_DIR` to equal the exact frozen successor ROOT and
therefore failed closed with `SUBMIT_ROOT_INVALID`.

This is an operator handoff/submission-fixture defect. It is not GPU evidence.
The diagnostic core did not start, RUN and OUTPUT were never created, no
`nvidia-smi` command ran, and no device, driver, scheduler, cgroup, node, or GPU
visibility cause may be inferred. Allocation to `cg15` with one A40 GRES is
scheduler custody only. It does not establish process-visible GPU identity.
Production admissibility remains `CANNOT_CHECK`; scientific-authority delta
remains `NONE`. Job `3537915` at merged result commit
`9ea21a1719fafbe9ab5f0d10a55dfd5f05036c67` remains the adverse scientific
predecessor and is not promoted or replaced.

## Preserved deployment and evidence

The selective archive was 368,640 bytes with SHA-256
`88017af9faa0ed4d020c155af026a2edc597146c872b8b77550cc977bff2d6d8`.
The V7 ROOT remains sealed mode `0500`; it must not be repaired, reused, or
deleted. LOG remains mode `0700`; the two raw Slurm streams remain mode `0600`
at first custody. RUN, OUTPUT, and both possible receipt paths remain absent.

The packet preserves exact local copies of:

- `REMOTE_DEPLOYMENT_EVIDENCE.txt`: archive, root absence, seal, merged-lane
  integrity, four clean-deployment validator modes, and post-validation root
  absence.
- `SUBMISSION_EVIDENCE.txt`: exact submitted job identifier and initial queue
  observation.
- `JOB_3537988_FIRST_CUSTODY.txt`: roots, file custody, exact raw bodies, and
  `sacct` records.
- `REMOTE_SUBMIT_SCRIPT_V1.sh`: the exact submission script exhibiting the
  outside-ROOT invocation.
- `slurm-3537988.out` and `slurm-3537988.err`: exact raw scheduler streams.
- `JOB_3537988_SUBMIT_ROOT_CANNOT_CHECK_V1.json`: canonical result and source
  bindings.

The result also binds the merged V7 freeze lane, the merged V6
deployment-validation-failure lane at
`598fa94273349094848659b7e3357a494e294b5a`, and the merged V5 job-3537915
scientific-predecessor lane at
`9ea21a1719fafbe9ab5f0d10a55dfd5f05036c67` by exact manifest/SHA256SUMS
bytes and hashes.

## Accounting

Job `3537988` adds exactly one body-free diagnostic submission and zero
scheduler GPU-seconds because `ElapsedRaw=0` with one allocated GPU. Accounting
after the job is therefore:

```text
protected infrastructure GPU-seconds=90
body-free discriminator GPU-seconds=170
combined scheduler GPU-seconds=260
protected infrastructure submissions=3
body-free discriminator submissions=3
protected generation attempts=0
```

The job is not a protected generation attempt, task execution, hidden sample,
production observation, or scientific result.

## Reopen boundary

Any successor must use a new submission fixture and preserve this first result.
The minimum discriminator is to invoke `sbatch` from the exact frozen ROOT, not
merely pass `--chdir`. Do not repair, delete, or reuse the existing ROOT, RUN,
OUTPUT, LOG, or job identifiers. A future submission remains separately gated
by fresh owner authorization, exact source/receipt bindings, fresh mutable
roots, and a new freeze. This packet itself authorizes no retry, SSH, mutation,
deployment, submission, protected access, or scientific claim.
