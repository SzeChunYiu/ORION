# Paper 1 GPU visibility diagnostic V6 operator handoff

## Frozen, owner-authorized compute, not deployed, not executed

This lane is scientifically bound to merged V5 result commit
`9ea21a1719fafbe9ab5f0d10a55dfd5f05036c67`. Require exact status
`FROZEN_NOT_EXECUTED` and `submission_authority=false`.

The owner has separately authorized Paper 1 LUNARC computation. Do not treat
the freeze itself as authority. The authorization may be used only after the
lane is merged, a clean archive passes every direct validator and integrity
check, a fresh deployment is sealed, and the four V6 roots are freshly proved
absent. No protected execution, prompt access, generation, evaluator, outcome,
production, causal, or scientific authority is granted.

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

## Frozen V6 paths

```text
ROOT=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-gpu-visibility-v6-20260825
RUN=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-gpu-visibility-v6-20260825
OUTPUT=$RUN/evidence
LOG=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-gpu-visibility-v6-20260825-submit-logs
```

Before every `ssh lunarc` command, run locally:

```bash
ssh -O check lunarc 2>/dev/null && echo "Connected" || /Users/billy/lunarc-init.sh
```

Then prove ROOT, RUN, OUTPUT, and LOG are all absent. Any existing path,
including an empty directory or symlink, stops the operation. Do not change,
reuse, or delete any V1-V5 deployment, run, output, or log root.

Deploy only a new clean `git archive` extraction at ROOT. Before calling it
immutable, seal every regular archive file mode `0400`, then set only the V1
trampoline mode `0500`, and seal every archive directory mode `0500`. The
manifest separately binds `BODY_FREE_DIAGNOSTIC_EXPORT_MANIFEST_V1.json` and
`SHA256SUMS` to deployment mode `0400`; they are not writable exceptions.

On LUNARC, after extraction and before validation, apply and verify the exact
mode policy without following symlinks:

```bash
ENTRY="$ROOT/development/p1-scienceagentbench-gpu-visibility-diagnostic-v6-2026-08-25/run_gpu_visibility_diagnostic_v1.sh"
find "$ROOT" -type f -exec chmod 0400 -- {} +
chmod 0500 -- "$ENTRY"
find "$ROOT" -depth -type d -exec chmod 0500 -- {} +
test "$(stat -Lc '%a' -- "$ENTRY")" = 500
test -z "$(find "$ROOT" -type f ! -path "$ENTRY" -printf '%m\n' | awk '$1 != "400" {print; exit}')"
test -z "$(find "$ROOT" -type d -printf '%m\n' | awk '$1 != "500" {print; exit}')"
test "$(stat -Lc '%a' -- "$ROOT/development/p1-scienceagentbench-gpu-visibility-diagnostic-v6-2026-08-25/BODY_FREE_DIAGNOSTIC_EXPORT_MANIFEST_V1.json")" = 400
test "$(stat -Lc '%a' -- "$ROOT/development/p1-scienceagentbench-gpu-visibility-diagnostic-v6-2026-08-25/SHA256SUMS")" = 400
```

Any mode mismatch stops. With `umask 077`, create only the separate LOG root
mode `0700`. Leave RUN and OUTPUT absent: the exact V1 trampoline creates RUN,
and the core creates OUTPUT.

## Clean-archive validation gate

From the lane directory, without pytest, require:

```bash
/bin/bash -n run_gpu_visibility_diagnostic_v1.sh
python3 -B validate_gpu_visibility_diagnostic_v1.py
python3 -O -B validate_gpu_visibility_diagnostic_v1.py
python3 -I -S -B validate_gpu_visibility_diagnostic_v1.py
/usr/bin/python3 -I -S -B validate_gpu_visibility_diagnostic_v1.py
shasum -a 256 -c SHA256SUMS
```

Require the exact V1 synthetic PASS terminal with `tests=50` and zero
protected-body, task-route, tokenize, completion, generation, job, and outcome
counts in all four modes. Validate the noncircular manifest topology and
`SHA256SUMS` after all payload hashes are frozen. Any mismatch stops; never
edit a deployed copy.

Also require:

1. contract and schema base exactly
   `9ea21a1719fafbe9ab5f0d10a55dfd5f05036c67`;
2. status exactly `FROZEN_NOT_EXECUTED`;
3. `submission_authority=false`;
4. exact predecessor result commit, artifact hashes, job facts, rc6 capture,
   and accounting;
5. exact one-A40, one-CPU, 4-GiB, ten-minute allocation with `cg14` excluded;
6. exact fresh ROOT/RUN/OUTPUT geometry;
7. runner byte/hash bindings to the final module and contract;
8. normalized runner self-hash
   `87691b1bdfc198a074104675b0bd57fc92349a3a05caca74bb16f98156f44aea`;
9. zero model, server, network, protected-body, task-route, evaluation, and
   outcome surfaces; and
10. no device reads or ioctls.

## Diagnostic decision interpretation

The V6 receipt binds one of exactly seven decisions:

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
sbatch --export=NIL \
  --chdir="$ROOT" \
  --output="$LOG/slurm-%j.out" \
  --error="$LOG/slurm-%j.err" \
  "$ROOT/development/p1-scienceagentbench-gpu-visibility-diagnostic-v6-2026-08-25/run_gpu_visibility_diagnostic_v1.sh"
```

The trampoline receives zero argv and the core receives exactly:

```text
--output-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-gpu-visibility-v6-20260825/evidence
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

Before V6, cumulative scheduler cost is 260 GPU-seconds: `90 protected + 170
body-free`. Protected infrastructure submissions remain three, completed
body-free discriminator submissions remain two, and protected generation
attempts remain zero.

After completion, add the V6 scheduler-accounted elapsed GPU-seconds and one
body-free diagnostic submission. Do not count V6 as protected execution or a
protected generation attempt. No result, positive or adverse, may erase prior
cost or failed jobs.
