# Paper 1 GPU visibility diagnostic V8 freeze

## Status and authority

This directory is the V8 body-free diagnostic freeze. Status is
`FROZEN_NOT_EXECUTED`; `submission_authority=false`; production admissibility
is `CANNOT_CHECK`; scientific-authority delta is `NONE`. No V8 deployment,
SSH session, scheduler submission, model start, protected-body access, task
route, tokenizer, completion, generation, evaluator, official outcome, or CI
run occurred while producing this packet.

The scientific base remains merged result commit
`9ea21a1719fafbe9ab5f0d10a55dfd5f05036c67`. V8 does not change the three
live diagnostic argv values, their sanitized environment, the evidence caps,
the classifier, output custody, the trampoline's zero-argv rule, or the
one-A40 allocation.

## Separately bound provenance

### Scientific predecessor

`JOB_3537915_PREDECESSOR_BINDING_V1.json` is unchanged from V7 and preserves
job `3537915` at merged result commit
`9ea21a1719fafbe9ab5f0d10a55dfd5f05036c67`. That adverse job ran on `cg14`,
returned exact integer 6 from its GPU-identity query, and remains
`CANNOT_CHECK`. Return code 6 is generic unsuccessful-query evidence only; it
is not a device, driver, cgroup, scheduler, or node diagnosis.

### V6 deployment validation

`V6_DEPLOYMENT_VALIDATION_FAILURE_BINDING_V1.json` is unchanged from V7 and
preserves merged result commit
`598fa94273349094848659b7e3357a494e294b5a`. V6 stopped before any job because
the frozen EasyBuild test-child interpreter could not load `libpython3.11` in
the sanitized environment. The V7 validator portability repair remains
preserved and the live command environment remains unbroadened.

### V7 job-3537988 pre-run failure

`V7_JOB_3537988_PRE_RUN_FAILURE_BINDING_V1.json` is new. It binds at merged
result commit `c9741a30f4d1634cbacdf79b454ae56c6eb89da5` the exact 11-file topology
of `development/p1-scienceagentbench-gpu-visibility-diagnostic-v7-job-3537988-result-2026-08-25`.

Exact job outcome:

```text
job=3537988
state=FAILED
exit=2:0
elapsed=0
node=cg15
allocation=one A40 GRES
failure_code=SUBMIT_ROOT_INVALID
detail=SLURM_SUBMIT_DIR differs from the exact successor root
detail_utf8_bytes=54
detail_sha256=1e0b0ccad8cab36771b3dc63311de1f26ba7a08dc692d14a02fa47ce1780b759
stdout_bytes=0
stdout_sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
stderr_bytes=172
stderr_sha256=aedf4ea5358a0d37bc6f1ddbc3b78b0e392adab3a1093b241665961c2bee495c
RUN=ABSENT
OUTPUT=ABSENT
success_receipt=ABSENT
cannot_check_receipt=ABSENT
ROOT=SEALED_PRESERVED mode=0500
LOG=PRESENT mode=0700
```

The exact root cause is an operator handoff/submission-fixture defect:
`sbatch` was invoked outside the frozen V7 ROOT. `--chdir` does not set
submission-time `SLURM_SUBMIT_DIR`. The trampoline failed before RUN creation,
the core did not start, and zero `nvidia-smi` commands ran. Allocation to
`cg15` is scheduler custody only and provides no GPU-visibility evidence.

## Exact V8 repair

The repair scope is `OPERATOR_SUBMISSION_SEQUENCE_ONLY`:

1. canonicalize ROOT and require exact canonical equality;
2. require ROOT to be a non-symlink directory at mode `0500`;
3. reject any inherited `SBATCH_*` environment member;
4. execute `cd -- "$ROOT"`;
5. require both logical `PWD` and physical `pwd -P` to equal ROOT;
6. invoke the zero-argv trampoline with `--export=NIL`, `--chdir="$ROOT"`, and
   stdout/stderr paths under LOG only.

A dedicated validator test accepts the exact order and applies a negative
mutation that removes the `cd` line; that mutation must fail. No runner gate is
weakened and no diagnostic command or classifier branch is modified.

## Fresh immutable geometry

```text
ROOT=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-gpu-visibility-v8-20260825
RUN=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-gpu-visibility-v8-20260825
OUTPUT=$RUN/evidence
LOG=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-gpu-visibility-v8-20260825-submit-logs
```

ROOT, RUN, OUTPUT, and LOG must all be absent before clean deployment. Regular
archive files are deployed mode `0400`, the trampoline mode `0500`, and all
archive directories mode `0500`. RUN and OUTPUT remain create-only. LOG is
created mode `0700` only after all clean-deployment validators and integrity
checks pass and mutable-root absence is rechecked.

## Core binding and receipt changes

At startup the core binds, in separate stages, the contract, scientific
predecessor, and V7 pre-run failure. Before receipt persistence it re-reads and
rebinds all three sources and fails closed on identity, byte, digest, or parsed
value drift. Both success and cannot-check schemas require
`pre_run_failure_binding`. `prior_accounting` now records three completed
body-free submissions and the unchanged 260 scheduler GPU-seconds.

All seven decisions and their order are unchanged:

1. `VISIBLE_A40_IDENTITY_BOUND`
2. `UNSCOPED_FAILURE_SCOPED_SUCCESS_A40_BOUND`
3. `NVIDIA_DEVICE_NODES_ABSENT`
4. `DEVICE_ACCESS_RESTRICTED_CGROUP_CAUSE_CANNOT_CHECK`
5. `NVIDIA_SMI_RC6_UNSUCCESSFUL_QUERIES`
6. `CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCONCLUSIVE`
7. `CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCOMPLETE`

Every decision is diagnostic only. A PASS receipt proves bounded capture and
classifier conformance, not model superiority, protected execution, production
admissibility, causal repair, or scientific authority.

## Accounting before V8

```text
protected infrastructure scheduler GPU-seconds=90
body-free discriminator scheduler GPU-seconds=170
combined scheduler GPU-seconds=260
protected infrastructure submissions completed=3
body-free discriminator submissions completed=3
protected generation attempts consumed=0
job 3537988 submission delta=1
job 3537988 scheduler GPU-second delta=0
```

A future V8 completion must add one body-free submission and only its
scheduler-accounted elapsed GPU-seconds. It must never be counted as a
protected generation attempt.

## Synthetic validation boundary

The standard-library validator contains 51 synthetic tests. It uses temporary
regular files and injected device metadata only, never a real device read or
ioctl. It is required under normal, optimized, isolated, and exact system
isolated modes. The exact successful terminal is:

```text
P1_SAB_GPU_VISIBILITY_DIAGNOSTIC_V1_SYNTHETIC_VALIDATION_PASS tests=51 protected_bodies=0 task_routes=0 tokenize=0 completion=0 generation=0 jobs=0 outcomes=0 production_admissibility=CANNOT_CHECK scientific_authority=NONE
```

Bash syntax and final `SHA256SUMS` verification are separate required checks.
No pytest, CI, SSH, commit, push, deployment, submission, or live diagnostic
was invoked to create the freeze.

## Export topology

The manifest excludes itself and `SHA256SUMS` from its payload map, includes
the new V7 pre-run-failure binding as a manifested payload, and binds all other
V8 payload files by exact bytes, SHA-256, Git mode, and deployment mode.
`SHA256SUMS` covers the manifest plus every manifested payload and excludes
only itself.

## Stop boundary

Any mismatch in source bindings, root geometry, mode, sequence, validator
terminal, receipt custody, or checksum stops the operation. Do not repair or
retry in place. Preserve the first V8 deployment and result, and require a new
freeze plus fresh owner authorization for any successor.
