# Protected RR1 one-tuple post-job finalizer freeze V1

## Status and authority

This additive lane freezes a fail-closed metadata finalizer for exactly one
ScienceAgentBench Runner V2 tuple:

- task `1`
- arm `RR`
- attempt `1`
- seed `101`

It was rebased on `origin/main` commit
`eba4a67e8607cdef96a2bb038d685a9a5d548599`. The implementation and its
hostile suite were exercised only with invented metadata. No LUNARC job was
submitted, no model or evaluator was invoked, no protected packet body was
opened, and no official outcome was opened while producing this lane.

The strongest possible success receipt is only
`PASS_ONE_TUPLE_POST_JOB_METADATA_FINALIZATION`. It is not a Runner V2
918-tuple ledger result, a production-admissibility result, or scientific
evidence. Every receipt fixes:

- `runner_v2_population_ledger_status=NOT_FINALIZED_918_TUPLES`
- `production_admissibility=CANNOT_CHECK`
- `scientific_authority_delta=NONE`
- `runner_v2_population_finalizer_invoked=false`

## Frozen allocation and scheduler scope

The finalizer accepts only controller and in-job metadata for one allocation
with all of the following properties:

- account `lu2026-2-51`
- partition `gpua40i`
- `gpu:a40:1`
- 8 CPUs, 64 GiB, one node, one task
- 60-minute time limit
- no constraint
- terminal `COMPLETED`, `ExitCode=0:0`, and `DerivedExitCode=0:0`
- exactly one in-job visible `NVIDIA A40` UUID
- `SLURM_JOB_GPUS` and `SLURM_STEP_GPUS` equal the `GresDetail IDX:N`
- a strictly positive half-open controller-local allocation interval

The non-overlap claim is deliberately limited to the named node and captured
time interval. A node-bounded `sacct` allocation query must contain the target
row exactly once. Any overlapping allocation with typed, generic, or unknown
GPU TRES, or with an unknown end, fails closed. CPU-only and half-open adjacent
rows do not create a conflict. The finalizer never claims whole-node,
UUID-global, cluster-global, or 918-tuple non-overlap.

## Entrypoints

Run from this directory or invoke the module by an absolute path. Both output
parents must already be owned by the current user and mode `0700`; each output
root must not exist.

Read-only scheduler capture:

```text
python3 protected_rr1_one_tuple_finalizer_v1.py capture \
  --job-id <SLURM_JOB_ID> \
  --partition gpua40i \
  --node <NODE> \
  --output-root <ABSOLUTE_NEW_CAPTURE_ROOT>
```

Private evidence finalization:

```text
python3 protected_rr1_one_tuple_finalizer_v1.py finalize \
  --evidence-root <ABSOLUTE_PRIVATE_EVIDENCE_ROOT> \
  --output-root <ABSOLUTE_NEW_FINALIZATION_ROOT>
```

The capture route executes only the six exact read-only `sacct`/`scontrol`
argument vectors frozen in `FINALIZER_CONTRACT_V1.json`, using a fixed
credential-free environment. There is no submission command, shell route,
network route, or external API route. A failed capture retains only a SHA-256
of stderr in its terminal diagnostic and rolls back the newly created capture
root when its identity is still safe.

The finalize route never executes scheduler commands. It only parses already
retained private metadata and emits one new canonical JSON receipt.

## Private evidence layout

The evidence root and both child directories must be exact mode `0700`.
Every opened evidence file must be owned by the current user, link count one,
and mode `0400` or `0600`. Symlinks, hardlinks, case aliases, duplicate fields,
CRLF, noncanonical JSON, file swaps, and group/world-readable evidence fail
closed.

Root inputs:

```text
POST_JOB_SACCT_V1.txt
POST_JOB_SACCT_NONOVERLAP_V1.txt
POST_JOB_SCONTROL_V1.txt
SCHEDULER_CONFIG_V1.txt
SCHEDULER_PARTITION_V1.txt
SCHEDULER_NODE_V1.txt
SCHEDULER_EXPORT_V1.jsonl
SCHEDULER_CAPTURE_PROVENANCE_V1.json
GPU_ALLOCATION_IDENTITY_V1.json
SERVER_CLEANUP_V1.json
STAGED_RUNTIME_INPUT_V1.json
PROCESS_ATTESTATION_V1.json
```

`attempt/` always contains:

```text
SCONTROL_IN_JOB_V1.txt
SLURM_IDENTITY_AND_SNAPSHOT_V1.json
```

It then contains exactly one complete terminal pair:

```text
# success pair
DYNAMIC_RR1_PRETOKENIZE_BINDING_V1.json
DIRECT_ROUTE_BRIDGE_BINDING_V1.json
ATTEMPT_CAPTURE_V1.json

# or typed failure pair
DIRECT_ROUTE_BRIDGE_FAILURE_BINDING_V1.json
ATTEMPT_CAPTURE_CANNOT_CHECK_V1.json
```

`runtime-inputs/RUN_PLAN.json` is opened and must be the complete frozen
102-task, three-arm, three-attempt Runner V2 plan (918 tuples). The selection
of task `1` / `RR` / attempt `1` occurs only after the full plan validates.
Other private runtime packet files may coexist there, but the finalizer never
opens them. The scheduler export is a private upstream input; the capture
entrypoint does not synthesize it. Its exact canonical record and complete
source-hash map must be assembled by the evidence custodian before finalizing.

## Cross-bindings required for success

Success requires all of these chains to agree:

1. frozen full plan bytes, staged runtime source hashes, exact server argv,
   and process attestation;
2. fixed tuple and seed, in-job job identity, in-job `scontrol` hash, attempt
   capture, RR0/RR1 request order, and dynamic RR1 tokenize-fit receipt;
3. stage file hash, process file hash, attempt canonical hash, dynamic raw file
   hash, bridge binding, and cleanup evidence;
4. terminal `sacct`, post-job `scontrol -dd`, scheduler config, partition,
   node, in-job GPU UUID/index identity, and conservative non-overlap query;
5. exact capture argv, capture provenance raw-file hashes, scheduler export
   raw record, and the complete opened-evidence source-hash map.

The truthful success fields distinguish actions by this finalizer from the
metadata it observes: generation was not invoked by the finalizer, while a
successful exact evidence chain records one observed two-completion RR tuple.
Task execution and official evaluation remain false.

## Self-binding and output custody

The module hard-checks raw SHA-256 values for its contract and output schema.
The contract also fixes the output-schema hash and a normalized module hash.
Normalization zeros only the three exact embedded assignments
`CONTRACT_SHA256`, `SCHEMA_SHA256`, and `NORMALIZED_MODULE_SHA256`; this breaks
the otherwise circular module/contract binding without weakening any other
byte.

Output directories are created with exclusive semantics and exact mode
`0700`. Receipt files use `O_EXCL`, exact mode `0600`, `fsync`, descriptor
reread, SHA-256 verification, and named-inode recheck. Rollback unlinks only a
new file or directory whose identity remains the one created by the module.

## Synthetic verification

```text
python3 -m py_compile \
  protected_rr1_one_tuple_finalizer_v1.py \
  validate_protected_rr1_one_tuple_finalizer_v1.py
python3 validate_protected_rr1_one_tuple_finalizer_v1.py
shasum -a 256 -c SHA256SUMS
```

The recorded local result is `44/44` tests passed. The suite uses only invented
metadata and injected fake scheduler runners. That result validates software
conformance and hostile fail-closed behavior only; it is not evidence that a
live allocation, generation attempt, or scientific evaluation succeeded.
