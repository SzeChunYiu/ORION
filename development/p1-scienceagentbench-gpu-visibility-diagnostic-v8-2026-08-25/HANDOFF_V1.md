# Paper 1 GPU visibility diagnostic V8 operator handoff

## Frozen, owner-gated compute; not deployed or executed

This V8 lane is a body-free diagnostic freeze. Its scientific base remains the
merged job-3537915 result commit
`9ea21a1719fafbe9ab5f0d10a55dfd5f05036c67`. Require exact status
`FROZEN_NOT_EXECUTED` and `submission_authority=false`. The freeze itself does
not grant deployment or submission authority.

V8 changes only the operator submission sequence that failed before the V7
core began. It does not weaken the runner, change the three diagnostic command
argv values, broaden the live command environment, change the classifier, or
open any model, server, network, protected body, task route, evaluator, or
official outcome.

## Three separately preserved events

### Scientific predecessor: job 3537915

`JOB_3537915_PREDECESSOR_BINDING_V1.json` preserves job `3537915` at merged
result commit `9ea21a1719fafbe9ab5f0d10a55dfd5f05036c67`: FAILED, exit
`1:0`, elapsed 84 seconds, node `cg14`, one A40 GRES, and a completed
`/usr/bin/nvidia-smi` query returning exact integer 6. Its stdout was 22 bytes
with SHA-256 `cda3a19e75eacfb91b9b2c2f85080bddea247dd500abec231f6212e3d8fff3bd`;
stderr was 76 bytes with SHA-256
`0a0daacddae467fe5f39a91401c306cb9b469459f8ba6d7e78d485c2d925c76a`.
Return code 6 is generic unsuccessful-query evidence only. Do not infer a
missing device, failed driver, cgroup cause, broken node, or repair.

### V6 deployment-validation failure

`V6_DEPLOYMENT_VALIDATION_FAILURE_BINDING_V1.json` separately preserves merged
result commit `598fa94273349094848659b7e3357a494e294b5a`. Validation failed before
submission with code `SANITIZED_SELF_INTERPRETER_NOT_EXECUTABLE`, subcode
`LIBPYTHON_NOT_FOUND_UNDER_COMMAND_ENVIRONMENT`, in tests 24-25. V6 submitted
zero jobs and consumed zero GPU-seconds. It is deployment evidence, not the
scientific predecessor and not GPU-visibility evidence.

### V7 job-3537988 pre-run failure

`V7_JOB_3537988_PRE_RUN_FAILURE_BINDING_V1.json` separately binds the exact
11-file result topology at merged result commit
`c9741a30f4d1634cbacdf79b454ae56c6eb89da5`. Job `3537988` was FAILED, exit
`2:0`, elapsed 0, node `cg15`, with one A40 GRES allocated. The trampoline
failed with `SUBMIT_ROOT_INVALID` before RUN creation because `sbatch` was
invoked outside the exact V7 ROOT. `--chdir` controls the job working directory
but does not rewrite submission-time `SLURM_SUBMIT_DIR`.

The exact detail is `SLURM_SUBMIT_DIR differs from the exact successor root`
(54 UTF-8 bytes; SHA-256
`1e0b0ccad8cab36771b3dc63311de1f26ba7a08dc692d14a02fa47ce1780b759`).
Stdout is 0 bytes with SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`;
stderr is 172 bytes with SHA-256
`aedf4ea5358a0d37bc6f1ddbc3b78b0e392adab3a1093b241665961c2bee495c`.
RUN, OUTPUT, and both receipt paths are absent; the V7 ROOT is sealed and the
V7 LOG is mode `0700`. This is an operator handoff/submission-fixture defect,
not GPU evidence. The core and all three `nvidia-smi` commands did not start.

Do not repair, reuse, delete, or reinterpret any preserved V6/V7 root or job.

## Fresh V8 geometry

```text
ROOT=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-gpu-visibility-v8-20260825
RUN=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-gpu-visibility-v8-20260825
OUTPUT=$RUN/evidence
LOG=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-gpu-visibility-v8-20260825-submit-logs
```

Before every `ssh lunarc` command, run locally:

```bash
ssh -O check lunarc 2>/dev/null && echo "Connected" || /Users/billy/lunarc-init.sh
```

Prove all four V8 paths absent before deployment. Any existing file,
directory, or symlink stops the operation. Build the selective archive from
exactly these four ordered pathspecs and no fifth lane or member:

```bash
ARCHIVE_PATHS=(
  'development/p1-scienceagentbench-gpu-visibility-diagnostic-v8-2026-08-25'
  'development/p1-scienceagentbench-backend-canonical-map-discriminator-v5-job-3537915-result-2026-08-25'
  'development/p1-scienceagentbench-gpu-visibility-diagnostic-v6-deployment-validation-result-2026-08-25'
  'development/p1-scienceagentbench-gpu-visibility-diagnostic-v7-job-3537988-result-2026-08-25'
)
EXPECTED_ARCHIVE_MEMBERS=55
EXPECTED_ARCHIVE_REGULAR_FILES=50
EXPECTED_ARCHIVE_DIRECTORY_ENTRIES=5
test "${#ARCHIVE_PATHS[@]}" -eq 4
git archive --format=tar --output="$ARCHIVE" "$MERGED_COMMIT" -- \
  "${ARCHIVE_PATHS[@]}"
ARCHIVE_MEMBER_COUNT=$(/usr/bin/tar -tf "$ARCHIVE" | /usr/bin/wc -l)
ARCHIVE_REGULAR_FILE_COUNT=$(/usr/bin/tar -tvf "$ARCHIVE" | /usr/bin/awk '$1 ~ /^-/ {count++} END {print count+0}')
ARCHIVE_DIRECTORY_ENTRY_COUNT=$(/usr/bin/tar -tvf "$ARCHIVE" | /usr/bin/awk '$1 ~ /^d/ {count++} END {print count+0}')
test "$ARCHIVE_MEMBER_COUNT" -eq "$EXPECTED_ARCHIVE_MEMBERS"
test "$ARCHIVE_REGULAR_FILE_COUNT" -eq "$EXPECTED_ARCHIVE_REGULAR_FILES"
test "$ARCHIVE_DIRECTORY_ENTRY_COUNT" -eq "$EXPECTED_ARCHIVE_DIRECTORY_ENTRIES"
test "$((ARCHIVE_REGULAR_FILE_COUNT + ARCHIVE_DIRECTORY_ENTRY_COUNT))" -eq "$ARCHIVE_MEMBER_COUNT"
```

The exact census is 55 tar members: 50 regular files (`13` V8, `18` V5
job-3537915 result, `8` V6 deployment-validation failure, and `11` V7
job-3537988 result) plus five directory entries (`development/` and the four
lane directories). Any different pathspec, order, member count, file count, or
member type stops deployment. Extract only this verified clean archive at ROOT.

Seal every regular archive file mode `0400`, set only the V8 trampoline mode
`0500`, and seal every directory mode `0500`. On LUNARC, after extraction:

```bash
ENTRY="$ROOT/development/p1-scienceagentbench-gpu-visibility-diagnostic-v8-2026-08-25/run_gpu_visibility_diagnostic_v1.sh"
find "$ROOT" -type f -exec chmod 0400 -- {} +
chmod 0500 -- "$ENTRY"
find "$ROOT" -depth -type d -exec chmod 0500 -- {} +
test "$(stat -Lc '%a' -- "$ENTRY")" = 500
test -z "$(find "$ROOT" -type f ! -path "$ENTRY" -printf '%m\n' | awk '$1 != "400" {print; exit}')"
test -z "$(find "$ROOT" -type d -printf '%m\n' | awk '$1 != "500" {print; exit}')"
test "$(stat -Lc '%a' -- "$ROOT/development/p1-scienceagentbench-gpu-visibility-diagnostic-v8-2026-08-25/BODY_FREE_DIAGNOSTIC_EXPORT_MANIFEST_V1.json")" = 400
test "$(stat -Lc '%a' -- "$ROOT/development/p1-scienceagentbench-gpu-visibility-diagnostic-v8-2026-08-25/SHA256SUMS")" = 400
```

Do not create LOG before clean-deployment validation. RUN, OUTPUT, and LOG must
remain absent throughout validation.

## Clean-archive validation gate

From the V8 lane directory, without pytest or CI, require these commands in
this order:

```bash
/usr/bin/bash -n run_gpu_visibility_diagnostic_v1.sh
/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3 -B validate_gpu_visibility_diagnostic_v1.py
/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3 -O -B validate_gpu_visibility_diagnostic_v1.py
/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3 -I -S -B validate_gpu_visibility_diagnostic_v1.py
/usr/bin/python3 -I -S -B validate_gpu_visibility_diagnostic_v1.py
/usr/bin/sha256sum -c SHA256SUMS
```

Require the exact synthetic PASS terminal with `tests=51` and zero protected
bodies, task routes, tokenize, completion, generation, jobs, and outcomes in
all four modes. The dedicated test must accept the exact operator sequence and
must reject a mutation that removes its ROOT change-directory step.

Only after every validation command succeeds, recheck fresh mutable-root
absence and create the private LOG in this exact order:

```bash
for path in "$RUN" "$OUTPUT" "$LOG"; do
  test ! -e "$path" && test ! -L "$path" || exit 1
done
umask 077
mkdir -- "$LOG"
chmod 0700 -- "$LOG"
test "$(stat -Lc '%a' -- "$LOG")" = 700
```

Any mismatch stops. Never edit a deployed copy. The final runner binds the
diagnostic module SHA-256
`ed95905c1124cda3799ee03e38b6faff5a7c7511240f9fd26bfda1166033dea9`, the
contract SHA-256
`4065d3271a002624bddd539e25293d41c0dab74aa7444a145a5aa058533e4e31`, and
normalized runner self-hash
`9f9647a4d9705ef34437477e7e5955f2875052d128d822d6d2d5afb554bc0e5c`.

## Authorized submission shape after every gate passes

The minimum V8 repair is the sequence below and nothing in the diagnostic
runner or core. It first canonicalizes and mode-checks ROOT, rejects inherited
scheduler submission variables, changes the operator shell into ROOT, checks
both logical and physical current directories, and only then invokes the
zero-argv trampoline. Retain `--chdir="$ROOT"`, `--export=NIL`, and LOG-only
scheduler streams.

```bash
ROOT_CANONICAL=$(/usr/bin/readlink -f -- "$ROOT")
test "$ROOT_CANONICAL" = "$ROOT"
test -d "$ROOT" && test ! -L "$ROOT"
test "$(/usr/bin/stat -Lc '%a' -- "$ROOT")" = 500
if /usr/bin/env | /usr/bin/grep -q '^SBATCH_'; then
  printf '%s\n' 'inherited SBATCH_* environment is forbidden' >&2
  exit 1
fi
cd -- "$ROOT"
test "$PWD" = "$ROOT"
test "$(pwd -P)" = "$ROOT"
submit_line=$(/usr/bin/sbatch --export=NIL \
  --chdir="$ROOT" \
  --output="$LOG/slurm-%j.out" \
  --error="$LOG/slurm-%j.err" \
  "$ROOT/development/p1-scienceagentbench-gpu-visibility-diagnostic-v8-2026-08-25/run_gpu_visibility_diagnostic_v1.sh"
)
```

Do not use `--wrap`, do not pass trampoline argv, and do not remove or reorder
any line in the exact sequence. The trampoline continues to require zero argv
and the core receives exactly:

```text
--output-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-gpu-visibility-v8-20260825/evidence
```

## Diagnostic and claim boundary

The seven classifier outputs and their order are unchanged from V7:
`VISIBLE_A40_IDENTITY_BOUND`,
`UNSCOPED_FAILURE_SCOPED_SUCCESS_A40_BOUND`,
`NVIDIA_DEVICE_NODES_ABSENT`,
`DEVICE_ACCESS_RESTRICTED_CGROUP_CAUSE_CANNOT_CHECK`,
`NVIDIA_SMI_RC6_UNSUCCESSFUL_QUERIES`,
`CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCONCLUSIVE`, and
`CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCOMPLETE`.

Every output is diagnostic only. A different node is not causal proof. A PASS
means a complete bounded receipt, not model or ORION superiority, protected
execution, official evaluation, production admission, or scientific
authority. Require exactly one create-only mode-`0400` receipt under new OUTPUT
and a mode-`0500` OUTPUT directory. Preserve the first receipt and both raw
scheduler streams. Do not repair or retry in place.

## Accounting before and after V8

Before V8, cumulative scheduler cost is exactly 260 GPU-seconds: 90 protected
and 170 body-free. Protected infrastructure submissions are three; body-free
diagnostic submissions are three; protected generation attempts are zero.
Job `3537988` added one body-free submission and zero GPU-seconds.

After a V8 job completes, add exactly one body-free submission and its
scheduler-accounted elapsed GPU-seconds. Do not count V8 as protected
execution or a protected generation attempt. No result may erase prior cost,
failed jobs, or the preserved pre-run failure.

## Stop boundary

This handoff authorizes no automatic retry, SSH session, mutation, deployment,
submission, protected access, or scientific claim. Any future execution still
requires fresh owner authorization, clean source/receipt bindings, fresh
mutable roots, and exact preservation of the first V8 result.
