# P1 ScienceAgentBench direct-route SLURM preflight V1 development packet

## Bounded development question

Can one additive lane bind but never invoke the unchanged LUNARC attempt
wrapper, reproduce its scheduler-capture semantics directly through pinned
directory descriptors, call the merged PR #1168 driver/adapter APIs, launch and
attest the exact local runtime, and capture exactly one task-arm-attempt tuple
without changing any upstream file or claiming that scheduler, production,
task, evaluator, or outcome gates are closed?

This packet begins at freshly fetched `origin/main`
`465ddcc04a644c41010defa558b93395d200b36f`, the merge of PR #1168. The merged
review head was `346469046ac27a012775bc3361ecce7764fc0ab2`.

## Atomic questions

1. Can the exact wrapper bytes remain a scheduler-semantics donor while wrapper
   execution is forbidden and the supervisor calls the direct driver/adapter
   APIs itself without modifying any upstream artifact?
2. Can runtime JSON become observation-backed rather than declarative by
   exact-byte hashing and live `/proc` process, mapping, command-line,
   environment, listener, health, and slot attestation?
3. Can RR and NR share one remaining 1,800-second raw-clock deadline instead
   of receiving independent 1,800-second HTTP timeouts?
4. Can every post-capture driver exception emit the unchanged adapter's
   `GenerationAttemptCapture.cannot_check_sidecar()` rather than only a generic
   shell failure?
5. Can the unextended Runner V2 plan be supplemented without pretending the
   native adapter ledger already binds driver and rendered-prompt hashes?
6. Can the owned server process group and every output fail closed while the
   wrapper is recorded as `NONINVOKED` rather than as a managed process?

## Considered approaches

### A. Modify PR #1168 driver and adapter wrapper

This could place the deadline and sidecar directly upstream, but violates the
requested additive ownership boundary and would invalidate the merged hashes.
Rejected.

### B. Rely on a declarative runtime JSON and an externally started server

This is smaller but cannot attest the bytes or live process and does not close
the scheduler/driver binding gap. Rejected.

### C. Add one supervisor/bridge module plus a minimal SLURM entrypoint

Selected, with the wrapper path removed after hostile review.
`run_direct_route_slurm_preflight_v1.sh` contains only SLURM resource headers
and execs the Python supervisor. `supervise` starts/stages/attests the runtime,
validates the exact SLURM environment grammar donated by the byte-bound
wrapper, runs exact argv `scontrol show job -dd <job-id>`, writes the snapshot
and identity through a pinned attempt-directory descriptor, and calls the
merged direct driver's public execution function with the unchanged adapter.
The default wrapper-driver mode fails closed.

## Frozen implementation hypothesis

A live tuple is admissible to this preflight only if all of the following hold:

- exact hashes for the merged driver, direct contract, prompt bundle, unchanged
  generation adapter, and unchanged attempt wrapper;
- exact new-file snapshots of the run plan, owner selection, runtime binding,
  masked packet, and recovered packet, each matching an owner-supplied SHA-256;
- exact GGUF byte count/hash, llama-server hash, CUDA backend hash, SLURM
  launcher hash, and Python bridge hash;
- exact server argv at `127.0.0.1:8080`, context 32,768, one slot,
  `--no-cont-batching`, and `--no-context-shift`; requests remain
  `cache_prompt=false` through the merged driver;
- after readiness, `/proc/<pid>/exe`, exact NUL-delimited argv, empty proxy
  environment, exact backend environment, exact model/backend mapped
  device+inode paths, one server-owned loopback listener, healthy endpoint, and
  exactly one `/slots` record;
- one `CLOCK_MONOTONIC_RAW` deadline initialized by the adapter's first boundary;
  every call receives only the remaining duration and a response that arrives
  after the deadline is rejected;
- static rendered prompts have prospective hashes; RR phase 1 is committed by
  the exact template, recovered-packet hash, and strict parsed canonical RR
  phase-0 state plus its SHA-256; every actual prompt and request is hash-bound
  in a separate bridge receipt;
- a driver exception after capture construction produces the adapter's typed
  `CANNOT_CHECK` sidecar; success remains allocation-finalization pending;
- the wrapper is byte-bound as
  `BYTE_BOUND_SCHEDULER_SEMANTICS_DONOR_NONINVOKED` and is never started; the
  server runs in one owned process group and the entire PGID is absent after
  cleanup even if its leader exited first;
- output-root and receipt creation pin verified parent directory descriptors and
  use relative `mkdirat`/`openat`-style operations, so concurrent parent renames
  cannot redirect writes; the supervisor creates `attempt/` in-process with
  `mkdirat`, and scheduler snapshot, scheduler identity, success capture,
  bridge binding, failure sidecars, and rollback all use the pinned attempt FD;
  production has no `/dev/fd` or `/proc/self/fd` descendant-path dependency.

## Binding boundary

Runner V2's exact run-plan schema cannot accept new fields, and the unchanged
adapter finalizer cannot natively seal the separate bridge receipt. This lane
does not hide that limitation. It emits a hash-bound per-tuple extension and
request-binding receipt, but a future owner must retain and jointly finalize
all 918 bridge receipts before using them as execution-identity evidence.
Until then, and regardless of scheduler finalization:

```text
task_fit_status = CANNOT_CHECK_BEFORE_TASK_OPENING
allocation_status = CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION
production_admissibility = CANNOT_CHECK
semantic_choice_sensitivity = NOT_ESTABLISHED
scientific_authority_delta = NONE
```

No upstream amendment is required for the bounded per-tuple preflight because
missing or drifting extension evidence rejects that tuple. An upstream schema
amendment would be required before claiming the native V2 ledger itself seals
these new fields.

## TDD and preserved red witnesses

The validator was written before implementation. Observed red witnesses
included:

- `AssertionError: direct-route SLURM preflight bridge is not implemented`;
- missing `execute_bridge_attempt` for real success/failure bridge tests;
- the original cross-phase clock fixture did not exceed its deadline and was
  corrected before implementation interpretation;
- missing mapped-backend identity and acceptance of a wrong mapped inode;
- backend attestation occurring before readiness;
- missing re-hash of staged files before capture;
- missing exact new-file runtime snapshots;
- missing owned process-group cleanup;
- output creation accepting a symlink parent.
- receipt creation following a concurrently swapped parent pathname;
- missing descriptor-relative output-root creation;
- cleanup treating an exited leader as proof that its surviving PGID child was
  absent; and
- wrapper cleanup failure preventing the server cleanup attempt;
- `KeyError: 'wrapper_execution_allowed'` after a fake `mkdir` proved that the
  exact unchanged wrapper returned success while redirecting every artifact to
  a replacement `attempt/` pathname;
- missing `output_dir_fd` support for direct adapter capture;
- missing direct scheduler capture and missing `NONINVOKED` wrapper record; and
- missing typed `/proc/self/fd/<fd>/child` portability probing.

The exact wrapper execution in that hostile regression is evidence of the
defect, not evidence that the wrapper is safe to run. A fake `mkdir` earlier in
`PATH` called `/bin/mkdir`, immediately displaced the created directory,
created a replacement at the original pathname, and allowed the unchanged
wrapper to exit successfully with the displaced directory empty. The contract
therefore forbids wrapper execution.

The final synthetic validator covers exact upstream/lane hashes, claim
boundaries, server geometry, staged runtime hashing, deadline behavior, a real
adapter-backed successful OS capture, a real RR deadline sidecar, live-process
identity rejection, runtime snapshotting, input re-hash, cleanup, and output
path safety, deterministic concurrent parent swaps, orphaned-group termination,
non-invoked wrapper recording, the exact wrapper swap witness, direct scheduler
capture, and audit-only descendant-capability portability. The final focused
suite contains 24 synthetic tests.

## Reopen triggers

Reopen rather than weaken the contract if the site binary does not support the
frozen flags, the exact model/backend are not mapped after readiness, `/slots`
does not expose exactly one slot, a source or process hash drifts, prompt
commitments cannot be reproduced, a typed sidecar cannot be emitted, cleanup
cannot prove owned process absence, the wrapper becomes reachable, production
depends on descendant FD path traversal, or any attempt requests task/
evaluator/outcome authority.

## Non-execution boundary

Development and validation use synthetic JSON, fake HTTP connections, fake
clock values, temporary files, and fake `/proc` trees only. They perform no
model launch, GPU allocation, official task access, evaluator call, outcome
opening, pytest, CI, manuscript, or PDF work.
