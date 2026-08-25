# Paper 1 protected RR1 execution successor V4 — interrupted design packet

## Status and authority

Status is exactly:

```text
DRAFT_DESIGN_ONLY__NOT_IMPLEMENTED_NOT_VALIDATED_NOT_DEPLOYED_NOT_EXECUTED
```

This packet preserves the latest design after the work session was explicitly
closed. It contains no executable successor, no manifest, no frozen archive,
no submission authority, and no scientific-authority increment. It must not be
used to deploy or submit a job. Production admissibility remains
`CANNOT_CHECK`.

The latest merged evidence base is ORION main merge
`634241328eaa0865615659d0d078a6034c0bbd45` (PR #1297), which preserves
body-free GPU-visibility diagnostic job `3538042`.

## Evidence chain that must remain separate

1. Protected V3 job `3537893` ran on `cg14`: `FAILED`, exit `1:0`, elapsed
   88 seconds. It opened, validated, and staged two protected packets but made
   zero tokenize, completion, generation, evaluator, or official-outcome
   calls. Exact typed failure:

   ```text
   PreflightError:staged CUDA backend is not mapped into the live server process
   ```

2. Body-free job `3537910` ran on `cg14` for 86 seconds. Its first canonical
   mapping attestation passed, then GPU identity failed through a retained
   nonempty-stderr ambiguity. Return code 6 was not established for this job.

3. Body-free job `3537915` ran on `cg14` for 84 seconds. Its first canonical
   mapping attestation passed and its exact `nvidia-smi` return code was 6.
   That means only that an object query was unsuccessful.

4. Body-free job `3537988` was submitted for zero scheduler GPU-seconds but
   stopped before core execution because `SLURM_SUBMIT_DIR` differed from the
   exact frozen root.

5. Body-free job `3538042` ran on `cg15`: `COMPLETED`, exit `0:0`, elapsed
   3 seconds. It bound exactly one process-visible `NVIDIA A40`, index `0`,
   UUID `GPU-06bb5356-4a6f-8c40-d27d-a0de37505a16`, under list, scoped, and
   unscoped queries. This is positive GPU-visibility evidence for that job
   only—not causal proof, model execution, protected success, task success,
   production admission, or ORION superiority.

## Actual runtime defect to repair

A node exclusion alone is insufficient. The V3 failure is rooted in the V1
helper:

```text
development/p1-scienceagentbench-direct-route-slurm-preflight-v1-2026-08-24/
  direct_route_slurm_preflight_v1.py::attest_process_identity::require_mapped
```

The V1 check requires the pathname rendered in `/proc/<pid>/maps` to equal the
frozen logical `/sw/...` path. On LUNARC, the same file may be rendered under
canonical `/lunarc/sw/...`, with matching device and inode identity.

A future implementation must successorize, at minimum:

- `direct_route_slurm_preflight_v2.py`;
- `DIRECT_ROUTE_SLURM_PREFLIGHT_CONTRACT_V2.json`;
- retained non-invoked `run_direct_route_slurm_preflight_v2.sh`;
- `protected_rr1_direct_route_v2.py` with an exact-bound V2 helper;
- `PROTECTED_RR1_DIRECT_ROUTE_CONTRACT_V2.json`;
- `run_protected_rr1_direct_route_v2.sh`;
- an outer V4 trampoline/finalizer/validator and their contracts.

The outer trampoline must hash and execute the V2 protected launcher, module,
and contract rather than the immutable V1 donor. The V3 loader, job-ID parser,
watcher, capture, and finalizer semantics must otherwise remain unchanged.

## Required mapping rule

For each frozen backend/model identity:

1. bind the logical path and `resolve(strict=True)` canonical path;
2. require logical and canonical paths to identify the same device and inode;
3. allow `/proc/<pid>/maps` rows only under the exact one- or two-element set
   `{logical, canonical}`;
4. require at least one row with the frozen maps-device and inode;
5. reject an allowed path carrying a different device or inode;
6. reject the frozen identity under any third alias, including ` (deleted)`;
7. require the second attestation to be byte/identity equivalent to the first.

Required hostile tests include logical-only, canonical-only, and both-path
success; wrong device; wrong inode; correct identity under a third alias;
logical/canonical identity disagreement; deleted/non-normalized aliases; and
post-read alias or identity drift. A normalized semantic diff must prove no
change to protected-packet, tokenize, completion, or generation behavior.

## Scheduler and root policy

A future successor may add exactly:

```text
#SBATCH --exclude=cg14
```

It must capture `ExcNodeList=cg14` and require the allocated node not to equal
`cg14`. It must reject `--nodelist`, `-w`, any `cg15` pin, GPU UUID pin, or
other positive node allowlist. Job `3538042` makes `cg15` a positive local
witness, not the uniquely functional node.

Never reuse the old body-free V4 discriminator roots. Proposed fresh protected
roots, still requiring a new live absence check, are:

```text
ROOT=.../repo-protected-rr1-exec-successor-v4-20260825
RUN=.../live-protected-rr1-exec-successor-v4-20260825
```

Retain `cd "$ROOT"` before `sbatch`, exact `--chdir="$ROOT"`, `--export=NIL`,
and immutable fresh output custody.

## Accounting before any future attempt

```text
protected infrastructure GPU-seconds=90
protected infrastructure submissions=3
next protected infrastructure ordinal=4
protected generation attempts=0
repaired generation ordinal=1
body-free diagnostic GPU-seconds=173
body-free diagnostic submissions=4
labelled programme total GPU-seconds=263
```

No prior cost or adverse result may be erased.

## Provisional archive design, not a frozen count

At merge `634241328eaa0865615659d0d078a6034c0bbd45`, the exact predecessor
selection is 81 files, not 80:

```text
frozen V3 snapshot=60
job-3537893/3537910/3537915 certificates=3
V8 freeze core surfaces=5
merged V8 result lane=13
```

If a future complete successor lane contains 18 files, the resulting selective
snapshot would provisionally contain 99 files, 21 subordinate directories,
22 directories including the archive root, 94 mode-`0400` files, and five
mode-`0500` files. These numbers are a design target only and must be recomputed
from the actual merged path set; this interrupted packet does not freeze them.

## Required future gates

Before any deployment or submission, a future lane must provide:

- complete contracts, schemas, development packet, handoff, manifest,
  `SHA256SUMS`, synthetic receipt, implementation, and hostile validator;
- direct normal, optimized, isolated, and exact-system-isolated validation
  without pytest or CI;
- clean fixed-commit archive validation and exact topology/mode checks;
- independent provenance, claim, and custody review;
- a PR merged to current main;
- a new read-only LUNARC absence/custody audit for every exact path;
- separate owner authorization for the one-tuple protected execution.

Even a successful future one-tuple run would not authorize the 918-tuple
campaign or establish a broad superiority claim. Scaling requires its own
predeclared evidence gates and receipts.
