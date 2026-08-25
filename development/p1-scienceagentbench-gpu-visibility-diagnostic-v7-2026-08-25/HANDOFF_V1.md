# Paper 1 GPU visibility diagnostic V7 operator handoff

## Frozen, owner-authorized compute, not deployed, not executed

This lane is scientifically bound to merged V5 result commit
`9ea21a1719fafbe9ab5f0d10a55dfd5f05036c67`. Require exact status
`FROZEN_NOT_EXECUTED` and `submission_authority=false`.

The owner has separately authorized Paper 1 LUNARC computation. Do not treat
the freeze itself as authority. The authorization may be used only after the
lane is merged, a clean archive passes every direct validator and integrity
check, a fresh deployment is sealed, and the four V7 roots are freshly proved
absent. No protected execution, prompt access, generation, evaluator, outcome,
production, causal, or scientific authority is granted.

## Preserved V6 deployment-validation failure

Separately verify merged result commit
`598fa94273349094848659b7e3357a494e294b5a` and
`development/p1-scienceagentbench-gpu-visibility-diagnostic-v6-deployment-validation-result-2026-08-25`
against `V6_DEPLOYMENT_VALIDATION_FAILURE_BINDING_V1.json`. V6 deployment
validation stopped with exact code
`SANITIZED_SELF_INTERPRETER_NOT_EXECUTABLE`, subcode
`LIBPYTHON_NOT_FOUND_UNDER_COMMAND_ENVIRONMENT`, failures in tests 24-25, and
zero submitted jobs. Its sealed ROOT is preserved and must not be repaired,
reused, or deleted.

The sole V7 portability repair freezes `/usr/bin/python3` for all three
synthetic child launches in tests 24-25 and asserts the exact interpreter and
launch count. Do not add `LD_LIBRARY_PATH` to `bounded_command`, broaden its
frozen `PATH=/usr/bin:/bin`, `LANG=C`, `LC_ALL=C` environment, or change the
three live `/usr/bin/nvidia-smi` argvs. The V6 failure is deployment evidence,
not a scientific predecessor and not GPU-visibility evidence.

## Preserved job-3537915 boundary

Job `3537915` remains an immutable adverse predecessor:

```text
state=FAILED
exit=1:0
elapsed=84s
node=cg14
allocated=one A40 GRES
terminal=P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_V2_CANNOT_CHECK failure_code=GPU_IDENTITY_INVALID detail_sha256=37a3b93da155ad4641b63864fd78781f9144c3813a2b02fae9ba0924a98025a2
failure_subcode=NVIDIA_SMI_NONZERO_RETURN
return_code=6
stdout=22 bytes / cda3a19e75eacfb91b9b2c2f85080bddea247dd500abec231f6212e3d8fff3bd
stderr=76 bytes / 0a0daacddae467fe5f39a91401c306cb9b469459f8ba6d7e78d485c2d925c76a
stdout_parse_attempted=false
```

Verify the exact merged-main surfaces in
`development/p1-scienceagentbench-backend-canonical-map-discriminator-v5-job-3537915-result-2026-08-25`
against `JOB_3537915_PREDECESSOR_BINDING_V1.json`. NVIDIA return code 6 is
generic unsuccessful-query evidence only. Do not infer a missing device,
failed driver, broken node, cgroup cause, or other root cause. Do not promote
jobs `3537893`, `3537910`, or `3537915`.

## Frozen V7 paths

```text
ROOT=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-gpu-visibility-v7-20260825
RUN=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-gpu-visibility-v7-20260825
OUTPUT=$RUN/evidence
LOG=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-gpu-visibility-v7-20260825-submit-logs
```

Before every `ssh lunarc` command, run locally:

```bash
ssh -O check lunarc 2>/dev/null && echo "Connected" || /Users/billy/lunarc-init.sh
```

Then prove ROOT, RUN, OUTPUT, and LOG are all absent. Any existing path,
including an empty directory or symlink, stops the operation. Do not change,
reuse, or delete any V1-V6 deployment, run, output, or log root.

Deploy only a new clean `git archive` extraction at ROOT containing the V7
lane, the job-3537915 result lane, and the V6 deployment-validation result
lane. Before calling it
immutable, seal every regular archive file mode `0400`, then set only the V1
trampoline mode `0500`, and seal every archive directory mode `0500`. The
manifest separately binds `BODY_FREE_DIAGNOSTIC_EXPORT_MANIFEST_V1.json` and
`SHA256SUMS` to deployment mode `0400`; they are not writable exceptions.

On LUNARC, after extraction and before validation, apply and verify the exact
mode policy without following symlinks:

```bash
ENTRY="$ROOT/development/p1-scienceagentbench-gpu-visibility-diagnostic-v7-2026-08-25/run_gpu_visibility_diagnostic_v1.sh"
find "$ROOT" -type f -exec chmod 0400 -- {} +
chmod 0500 -- "$ENTRY"
find "$ROOT" -depth -type d -exec chmod 0500 -- {} +
test "$(stat -Lc '%a' -- "$ENTRY")" = 500
test -z "$(find "$ROOT" -type f ! -path "$ENTRY" -printf '%m\n' | awk '$1 != "400" {print; exit}')"
test -z "$(find "$ROOT" -type d -printf '%m\n' | awk '$1 != "500" {print; exit}')"
test "$(stat -Lc '%a' -- "$ROOT/development/p1-scienceagentbench-gpu-visibility-diagnostic-v7-2026-08-25/BODY_FREE_DIAGNOSTIC_EXPORT_MANIFEST_V1.json")" = 400
test "$(stat -Lc '%a' -- "$ROOT/development/p1-scienceagentbench-gpu-visibility-diagnostic-v7-2026-08-25/SHA256SUMS")" = 400
```

Any mode mismatch stops. Do **not** create LOG yet. RUN, OUTPUT, and LOG must
all remain absent throughout clean-deployment validation. The exact V1
trampoline creates RUN, and the core creates OUTPUT only after submission.

## Clean-archive validation gate

From the lane directory, without pytest, require:

```bash
/usr/bin/bash -n run_gpu_visibility_diagnostic_v1.sh
/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3 -B validate_gpu_visibility_diagnostic_v1.py
/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3 -O -B validate_gpu_visibility_diagnostic_v1.py
/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3 -I -S -B validate_gpu_visibility_diagnostic_v1.py
/usr/bin/python3 -I -S -B validate_gpu_visibility_diagnostic_v1.py
/usr/bin/sha256sum -c SHA256SUMS
```

Require the exact V1 synthetic PASS terminal with `tests=50` and zero
protected-body, task-route, tokenize, completion, generation, job, and outcome
counts in all four modes. Validate the noncircular manifest topology and
`SHA256SUMS` after all payload hashes are frozen. Any mismatch stops; never
edit a deployed copy.

Only after every validation command passes, recheck the fresh mutable roots
and create LOG in this exact order:

```bash
for path in "$RUN" "$OUTPUT" "$LOG"; do
  test ! -e "$path" && test ! -L "$path" || exit 1
done
umask 077
mkdir -- "$LOG"
chmod 0700 -- "$LOG"
test "$(stat -Lc '%a' -- "$LOG")" = 700
```

This is the only admissible LOG creation point. Never create LOG before the
four validator modes and `/usr/bin/sha256sum` succeed and the fresh
RUN/OUTPUT/LOG absence recheck passes.

Also require:

1. contract and schema base exactly
   `9ea21a1719fafbe9ab5f0d10a55dfd5f05036c67`;
2. status exactly `FROZEN_NOT_EXECUTED`;
3. `submission_authority=false`;
4. exact predecessor result commit, artifact hashes, job facts, rc6 capture,
   and accounting;
5. separate V6 deployment-validation failure binding at merged result commit
   `598fa94273349094848659b7e3357a494e294b5a`, with zero submitted jobs;
6. exact `/usr/bin/python3` for all three test-child launches, with no live
   command-environment broadening;
7. exact one-A40, one-CPU, 4-GiB, ten-minute allocation with `cg14` excluded;
8. exact fresh ROOT/RUN/OUTPUT geometry;
9. runner byte/hash bindings to the final module and contract;
10. normalized runner self-hash
   `49d06e6128e7ad26414a94241745799b5a18142f1acdcb3061cfa828faf41d67`;
11. zero model, server, network, protected-body, task-route, evaluation, and
   outcome surfaces; and
12. no device reads or ioctls.

## Diagnostic decision interpretation

The V7 receipt binds one of exactly seven decisions:

- `VISIBLE_A40_IDENTITY_BOUND`: all three commands parse the same A40 and the
  validated scope token matches, with character-device evidence and no denied
  read-only open.
- `UNSCOPED_FAILURE_SCOPED_SUCCESS_A40_BOUND`: scoped identity succeeds and
  matches while the completed unscoped identity query is nonzero.
- `NVIDIA_DEVICE_NODES_ABSENT`: bounded device inventory is empty and no
  command yields an identity.
- `DEVICE_ACCESS_RESTRICTED_CGROUP_CAUSE_CANNOT_CHECK`: device opens are denied
  without an identity; the cgroup cause remains explicitly `CANNOT_CHECK`.
- `NVIDIA_SMI_RC6_UNSUCCESSFUL_QUERIES`: all three completed commands return
  exact integer 6 with six complete raw bindings and no parse.
- `CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCONCLUSIVE`: complete evidence does not
  meet an earlier exact classifier.
- `CANNOT_CHECK_DIAGNOSTIC_EVIDENCE_INCOMPLETE`: one or more required evidence
  gates did not complete.

Every label is diagnostic only. A different node is not causal proof. A V1
`PASS` means a complete bounded diagnostic receipt, not model or ORION
superiority, protected execution, official evaluation, production admission,
or scientific authority.

## Authorized submission shape after every gate passes

Submit only the zero-argv V1 trampoline from immutable ROOT with `--export=NIL`,
exact chdir, and LOG-only scheduler streams. Do not use `--wrap` and do not pass
argv to the trampoline. Its embedded geometry includes `#SBATCH --exclude=cg14`.

The intended shape is:

```bash
if /usr/bin/env | /usr/bin/grep -q '^SBATCH_'; then
  printf '%s\n' 'inherited SBATCH_* environment is forbidden' >&2
  exit 1
fi
sbatch --export=NIL \
  --chdir="$ROOT" \
  --output="$LOG/slurm-%j.out" \
  --error="$LOG/slurm-%j.err" \
  "$ROOT/development/p1-scienceagentbench-gpu-visibility-diagnostic-v7-2026-08-25/run_gpu_visibility_diagnostic_v1.sh"
```

The trampoline receives zero argv and the core receives exactly:

```text
--output-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-gpu-visibility-v7-20260825/evidence
```

## Receipt and no-retry gate

Require exactly one create-only mode-`0400` receipt under new OUTPUT:

```text
GPU_VISIBILITY_DIAGNOSTIC_RESULT_V1.json
GPU_VISIBILITY_DIAGNOSTIC_CANNOT_CHECK_V1.json
```

OUTPUT must become mode `0500`. Require one exact terminal prefix:

```text
P1_SAB_GPU_VISIBILITY_DIAGNOSTIC_V1_PASS
P1_SAB_GPU_VISIBILITY_DIAGNOSTIC_V1_CANNOT_CHECK
```

Preserve the first receipt, scheduler streams, submission line, scheduler
accounting, immutable deployment binding, and root absence/deployment evidence.
Do not repair or retry in place. Any successor must use new filenames, fresh
roots, a new contract, a new freeze/merge, and fresh owner authorization.

## Accounting after execution

Before V7, cumulative scheduler cost is 260 GPU-seconds: `90 protected + 170
body-free`. Protected infrastructure submissions remain three, completed
body-free discriminator submissions remain two, and protected generation
attempts remain zero.

After completion, add the V7 scheduler-accounted elapsed GPU-seconds and one
body-free diagnostic submission. Do not count V7 as protected execution or a
protected generation attempt. No result, positive or adverse, may erase prior
cost or failed jobs.
