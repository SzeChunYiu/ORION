# Paper 1 GPU visibility diagnostic V7 freeze

## Status and authority boundary

This additive packet is scientifically bound to the merged V5 result commit
`9ea21a1719fafbe9ab5f0d10a55dfd5f05036c67`. Its status is exactly
`FROZEN_NOT_EXECUTED`, and `submission_authority=false`.

No V7 deployment or live job has occurred. This packet authorizes no SSH,
submission, protected-body access, protected retry, model or server start,
network access, task-bearing request, tokenization, completion, generation,
evaluator invocation, outcome access, production admission, causal claim, or
scientific claim. The owner separately authorized Paper 1 LUNARC computation;
that authorization becomes actionable only after this freeze is merged,
validated from a clean archive, deployed immutably to a fresh root, and all
frozen live roots are proved absent.

## Bound V6 deployment-validation failure and exact V7 repair

`V6_DEPLOYMENT_VALIDATION_FAILURE_BINDING_V1.json` separately binds merged
result commit `598fa94273349094848659b7e3357a494e294b5a`. V6 was deployed to
its fresh sealed ROOT, but its required clean-deployment validator failed
before LOG creation or `sbatch`; no V6 live job ran and accounting remained
260 combined GPU-seconds. The exact failure is:

```text
status=CANNOT_CHECK_V6_DEPLOYMENT_VALIDATION
failure_code=SANITIZED_SELF_INTERPRETER_NOT_EXECUTABLE
failure_subcode=LIBPYTHON_NOT_FOUND_UNDER_COMMAND_ENVIRONMENT
failed_tests=24,25
observed_child_return_code=127
jobs_submitted=0
```

All three synthetic child launches in tests 24-25 used the validator's
EasyBuild `sys.executable`, but `bounded_command` correctly replaced the child
environment with `PATH=/usr/bin:/bin`, `LANG=C`, and `LC_ALL=C`. The EasyBuild
child then could not load `libpython3.11.so.1.0`. Under the same sanitized
environment, `/usr/bin/python3` executed the fixture and returned its intended
code. V7 therefore changes only those three test-child argvs to the exact
`/usr/bin/python3`, and the validator asserts both that exact path and the
three-launch count. It does not add `LD_LIBRARY_PATH`, broaden the live command
environment, or change any live diagnostic command, decision, allocation, or
scientific boundary.

The V6 deployment failure is not the scientific predecessor. Job `3537915`
and merged result commit `9ea21a1719fafbe9ab5f0d10a55dfd5f05036c67`
remain the separate adverse scientific predecessor below. The preserved V6
ROOT must not be repaired, reused, or deleted.

## Exact adverse predecessor

`JOB_3537915_PREDECESSOR_BINDING_V1.json` preserves job `3537915` as the
adverse body-free predecessor. Its merged result is:

```text
job=3537915
state=FAILED
exit=1:0
elapsed=84s
node=cg14
allocation=one A40 GRES
terminal=P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_V2_CANNOT_CHECK failure_code=GPU_IDENTITY_INVALID detail_sha256=37a3b93da155ad4641b63864fd78781f9144c3813a2b02fae9ba0924a98025a2
```

The completed `nvidia-smi` capture is bound exactly as:

```text
failure_subcode=NVIDIA_SMI_NONZERO_RETURN
return_code=6
stdout.bytes=22
stdout.sha256=cda3a19e75eacfb91b9b2c2f85080bddea247dd500abec231f6212e3d8fff3bd
stderr.bytes=76
stderr.sha256=0a0daacddae467fe5f39a91401c306cb9b469459f8ba6d7e78d485c2d925c76a
stdout_parse_attempted=false
```

The relevant merged result surfaces are:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `JOB_3537915_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V2.json` | 1,883 | `2b421bb1ed442ac15689975658b4a4320611276cc4dfad6649d9b85f68d67cf3` |
| `JOB_3537915_BODY_FREE_CANNOT_CHECK_CERTIFICATE_V2.json` | 7,161 | `44054d293392d480ca8c4f154f963a3dbb60600a156e042432eab44aa2e63cc5` |
| `GPU_IDENTITY_FAILURE_CLASSIFICATION_V2.json` | 7,557 | `abfc0d0ddddff00412554bc00d59e24e1bb1c811062e87d03b0b18f943a3ce0c` |
| `NVIDIA_SMI_RETURN_VALUE_SOURCE_V1.txt` | 917 | `a95583b6d96309dc823b04a7b89f62d7ee2b81847bd2f75b119c97911c6a56a3` |
| `RESULT_EXPORT_MANIFEST_V2.json` | 5,322 | `9ffdb5135cf4848863cb49d604a86af7747cbbaf7a241bba627c8f460d33decd` |

Job `3537915` completed exactly the stages `CONTRACT_BOUND`,
`RUNTIME_FILES_BOUND`, `SERVER_STARTED`, `SERVER_READY_BODY_FREE`,
`CANONICAL_MAP_ATTESTATION_1`, and `SERVER_CLEANUP_PASS`. The first mapping
attestation remains a post-outcome body-free code-semantic witness only. GPU
identity, the second attestation, final runtime-file rebind, final listener
rebind, protected execution, and official evaluation did not complete.
Production admissibility remains `CANNOT_CHECK`; scientific-authority delta
remains `NONE`.

NVIDIA documents return code 6 only as an unsuccessful query for an object.
It does not identify the object and does not establish device absence, driver
failure, scheduler failure, cgroup denial, node failure, or any other cause.
The 22-byte stdout binding is not reinterpreted as causal evidence. Neither
job `3537893`, `3537910`, nor `3537915` is repaired or promoted.

## Smallest unresolved scientific question

Jobs `3537910` and `3537915` both failed on `cg14`, but repeated placement is
not causal evidence. V7 asks a narrower falsifiable diagnostic question on one
different allocated A40 node:

> Does the allocated process expose a coherent A40 identity across device-node
> metadata, the scheduler visibility token, `nvidia-smi -L`, the exact
> unscoped identity query, and the same identity query explicitly scoped by the
> validated `CUDA_VISIBLE_DEVICES` token?

The node change is a diagnostic intervention only. It cannot by itself prove
that `cg14` caused either predecessor failure.

## Minimal body-free diagnostic

V7 requests one node, one task, one CPU, 4 GiB, one A40 GRES, and ten minutes,
with `cg14` excluded. It never starts the model or server and never imports a
network stack. It captures only:

1. raw/base64 bindings for the allowlisted variables `SLURM_JOB_ID`,
   `SLURMD_NODENAME`, `SLURM_JOB_GPUS`, `SLURM_STEP_GPUS`, and
   `CUDA_VISIBLE_DEVICES`;
2. bounded, non-following `/dev/nvidia*` metadata and read-only openability,
   without reading a device body or issuing an ioctl;
3. bounded `/proc/self/cgroup` and selected `/proc/self/mountinfo` evidence;
4. exact raw/base64 stdout and stderr bindings for `nvidia-smi -L`, the
   unscoped identity query, and the scoped identity query; and
5. exact return code, completeness, parse-attempt, and parsed-identity state
   for each command.

Every command uses `PATH=/usr/bin:/bin`, `LANG=C`, `LC_ALL=C`, a 30-second
timeout, and a 65,536-byte cap per stream. Parsing is eligible only after a
completed call with exact integer return code zero, complete valid raw
bindings, and decoded empty stderr. Nonzero return or nonempty stderr is never
parsed or promoted.

The scoped token grammar accepts exactly one nonnegative decimal device index
or one GPU UUID. Commas, aliases, whitespace, and malformed values stop scoped
execution and produce a typed incomplete receipt.

## Frozen decision surface

The decision order is exact:

1. `VISIBLE_A40_IDENTITY_BOUND` requires character-device evidence, three
   mutually identical parsed `NVIDIA A40` identities, a matching scope token,
   and no denied read-only open.
2. `UNSCOPED_FAILURE_SCOPED_SUCCESS_A40_BOUND` requires character-device
   evidence, a parsed scoped A40 matching the token, and a completed nonzero
   unscoped query.
3. `NVIDIA_DEVICE_NODES_ABSENT` requires an empty bounded inventory and no
   parsed identity.
4. `DEVICE_ACCESS_RESTRICTED_CGROUP_CAUSE_CANNOT_CHECK` requires denied
   read-only device opens and no parsed identity; it deliberately does not
   claim that the retained cgroup evidence is causal.
5. `NVIDIA_SMI_RC6_UNSUCCESSFUL_QUERIES` requires all three exact commands to
   complete with integer return code 6, all six streams complete and valid,
   no parse attempt, and three null identities.
6. otherwise use `CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCONCLUSIVE`.
7. any incomplete environment, inventory, cgroup, command, source, or custody
   evidence uses `CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCOMPLETE`.

All seven outputs are diagnostic labels, including the two positive identity
bindings. None proves a cause, repairs a predecessor, authorizes a protected
retry, establishes task execution, supports production admission, or changes
scientific authority.

## Fresh immutable roots

The frozen paths are:

```text
ROOT=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-gpu-visibility-v7-20260825
RUN=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-gpu-visibility-v7-20260825
OUTPUT=$RUN/evidence
LOG=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-gpu-visibility-v7-20260825-submit-logs
```

The freeze has not live-probed these roots. Before deployment, require ROOT,
RUN, OUTPUT, and LOG all absent. An empty directory or symlink is reuse and
stops. No V1-V6 deployment, run, output, or log root may be changed, reused, or
deleted. Deploy a new read-only clean-archive snapshot and never repair it in
place. With `umask 077`, the operator may create only the separate LOG root
mode `0700`; the zero-argv trampoline creates RUN mode `0700`, and the core
alone creates OUTPUT.

## Runtime and receipt custody

The trampoline binds its canonical and spooled bytes, normalized self-hash,
module, contract, Python target, libpython, required system tools, submit root,
working directory, and fresh-run geometry before executing the core with the
single frozen `--output-root` pair. It receives zero operator argv.

Exactly one mode-`0400` receipt may be created under a new OUTPUT:

```text
GPU_VISIBILITY_DIAGNOSTIC_RESULT_V1.json
GPU_VISIBILITY_DIAGNOSTIC_CANNOT_CHECK_V1.json
```

OUTPUT becomes mode `0500` afterward. The terminal prefixes are:

```text
P1_SAB_GPU_VISIBILITY_DIAGNOSTIC_V1_PASS
P1_SAB_GPU_VISIBILITY_DIAGNOSTIC_V1_CANNOT_CHECK
```

A V1 `PASS` means only that the bounded diagnostic receipt is complete and one
frozen decision label was bound. A positive identity label is not equivalent
to production or scientific PASS.

## Accounting

- Protected scheduler cost before V7: 90 GPU-seconds.
- Body-free discriminator cost before V7: 170 GPU-seconds.
- Combined scheduler cost before V7: 260 GPU-seconds.
- Protected infrastructure submissions completed: three.
- Body-free discriminator submissions completed: two.
- Protected generation attempts consumed: zero.
- V7 submissions and V7 scheduler GPU-seconds: zero while status is
  `FROZEN_NOT_EXECUTED`.

A future V7 job must add only its scheduler-accounted cost after completion.
It is not a protected generation attempt and is not a hidden evaluation
sample.

## Frozen artifact and validation topology

The final export contains ten payload files: contract, output schema, job
predecessor binding, V6 deployment-validation failure binding, development
packet, operator handoff, V1 core, V1
zero-argv trampoline, direct hostile validator, and synthetic-validation
receipt. `BODY_FREE_DIAGNOSTIC_EXPORT_MANIFEST_V1.json` binds those ten
payloads while excluding itself and `SHA256SUMS`; `SHA256SUMS` binds the ten
payloads plus the manifest and excludes only itself. The manifest separately
binds deployment mode `0400` for both excluded integrity files. A deployment
archive is sealed with every regular file mode `0400`, except the V1
trampoline mode `0500`, and every directory mode `0500`; exact mode verification
is required before validation or submission.

The direct validator must pass 50 synthetic tests under normal, optimized,
isolated, and exact-system isolated Python. Its exact terminal is:

```text
P1_SAB_GPU_VISIBILITY_DIAGNOSTIC_V1_SYNTHETIC_VALIDATION_PASS tests=50 protected_bodies=0 task_routes=0 tokenize=0 completion=0 generation=0 jobs=0 outcomes=0 production_admissibility=CANNOT_CHECK scientific_authority=NONE
```

These are offline, body-free conformance results. They submit no job and add no
live diagnostic, production, outcome, causal, or scientific authority.

On LUNARC the clean-archive gate freezes `/usr/bin/bash -n`, the exact
EasyBuild Python
`/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3`
for the normal, optimized, and isolated validator modes, `/usr/bin/python3`
for exact-system isolated mode, and `/usr/bin/sha256sum -c SHA256SUMS` for
integrity. Validation occurs while RUN, OUTPUT, and LOG are absent. Only after
all modes pass may the operator recheck fresh RUN/OUTPUT/LOG absence and create
LOG mode `0700`. Immediately before `sbatch`, the handoff rejects any inherited
`SBATCH_*` member with `/usr/bin/env | /usr/bin/grep -q '^SBATCH_'`. LOG must
never be created before validation.

## Reopen conditions

Reopen and stop if either predecessor binding or any bound source artifact
byte/hash differs; if the contract, schema,
module, runner, validator, fresh paths, allocation, or decision order drifts;
if `cg14` can be selected; if any command can exceed its time or body cap; if
any stream can be omitted; if parsing can occur before return-zero and empty
stderr; if device bodies or ioctls become reachable; if a node change is
treated as causal proof; or if any model, server, network, protected, task,
evaluation, or outcome surface becomes reachable.
