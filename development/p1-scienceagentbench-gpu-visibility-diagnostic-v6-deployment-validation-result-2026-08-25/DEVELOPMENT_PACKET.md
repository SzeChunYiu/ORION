# Paper 1 V6 deployment-validation result

## Exact status

The V6 freeze merged in PR `#1284` at
`79865e469c79f656bcca92044975eeb6895bb283`. A selective clean `git archive`
of that commit was bound locally by SHA-256
`2f8773ff5637d6ec19c92bb1fccf0103be95f8640db5bf0b9c7b4351500537ff`
and deployed to the frozen V6 ROOT after ROOT, RUN, OUTPUT, and LOG were all
proved absent.

The archive was sealed successfully: every regular file was mode `0400`, the
V1 trampoline was mode `0500`, and every directory was mode `0500`. The live
job was **not submitted** because the required LUNARC clean-deployment
validator failed before LOG creation or `sbatch`.

Exact disposition:

```text
status=CANNOT_CHECK_V6_DEPLOYMENT_VALIDATION
failure_code=SANITIZED_SELF_INTERPRETER_NOT_EXECUTABLE
failure_subcode=LIBPYTHON_NOT_FOUND_UNDER_COMMAND_ENVIRONMENT
jobs_submitted=0
v6_scheduler_gpu_seconds=0
RUN=ABSENT
OUTPUT=ABSENT
LOG=ABSENT
production_admissibility=CANNOT_CHECK
scientific_authority_delta=NONE
```

The sealed V6 ROOT and the failed remote deployment script are preserved in
place. They must not be edited, repaired, reused, or deleted.

## Reproduced failure

The normal remote validator ran 50 tests. Exactly tests 24 and 25 failed:

```text
test_24_bounded_command_retains_exact_bodies_hashes_and_rc: expected return 6, observed 127
test_25_bounded_command_fails_closed_at_stream_cap: expected 64 retained bytes, observed 0
Ran 50 tests
FAILED (failures=2)
```

Both tests construct their child argv with `sys.executable`. On LUNARC the
validator itself is the EasyBuild Python:

```text
/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3
```

The core `bounded_command` deliberately replaces the child environment with
the frozen command environment:

```text
PATH=/usr/bin:/bin
LANG=C
LC_ALL=C
```

That environment excludes `LD_LIBRARY_PATH`, so launching the EasyBuild
interpreter as the synthetic child returns 127 with the exact diagnostic:

```text
/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3: error while loading shared libraries: libpython3.11.so.1.0: cannot open shared object file: No such file or directory
```

This is a validator-fixture portability defect, not a live `nvidia-smi`
observation and not evidence about GPU visibility. The production diagnostic
commands remain the three exact `/usr/bin/nvidia-smi` argvs; the V6 job never
ran.

## Smallest supported repair

A direct discriminator under the same sanitized environment established:

```text
EasyBuild Python child: return 127, libpython3.11.so.1.0 not found
/usr/bin/python3 child: emitted the synthetic stdout/stderr and returned 6
```

Therefore the smallest justified V7 change is validator-only: tests 24 and 25
must launch the already-required `/usr/bin/python3` rather than
`sys.executable`. The core command environment must **not** be broadened with
`LD_LIBRARY_PATH`; doing so would change the live diagnostic instead of fixing
the synthetic fixture. The V7 core decision surface, body-free boundary,
allocation, and `cg14` exclusion remain unchanged.

Because V6 ROOT now exists, V7 requires a new lane, deployment root, run root,
output root, log root, runner self-binding, source hashes, freeze/merge, clean
archive, and fresh absence proof. No in-place V6 repair or V6 submission is
admissible.

## Accounting and authority

No scheduler job was submitted and no GPU was allocated. Accounting therefore
remains exactly:

```text
protected GPU-seconds=90
body-free GPU-seconds=170
combined GPU-seconds=260
body-free submissions=2
protected generation attempts=0
```

No model or server started. SSH/archive deployment transport did access the
network; it is recorded explicitly and is not relabeled as zero. The diagnostic
made zero model, task-bearing, or protected network requests, and no protected
body, task route, tokenize, completion, generation, evaluator, or outcome
surface was accessed. This result supplies deployment-validation failure
evidence only. It does not change Paper 1 scientific authority and does not
promote any prior job.

## Evidence surfaces

- `DEPLOYMENT_EVIDENCE.txt`: exact fresh-root and mode-seal terminal surface.
- `VALIDATOR_FAILURE_OUTPUT.txt`: exact 50-test remote failure output and root
  state.
- `SANITIZED_INTERPRETER_PROBE.txt`: ordered EasyBuild/system-Python
  discriminator.
- `REMOTE_DEPLOYMENT_SCRIPT_V1.sh`: exact script whose validation gate stopped
  before LOG creation and submission.
- `DEPLOYMENT_VALIDATION_FAILURE_V1.json`: canonical machine-readable result.
- `RESULT_EXPORT_MANIFEST_V1.json` and `SHA256SUMS`: noncircular integrity
  topology.
