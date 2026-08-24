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
hostile suite were exercised only with invented metadata. Privacy-safe parser
shapes were repaired after fresh read-only LUNARC review probes on 2026-08-24;
those probes submitted no job and opened no protected body, credential,
evaluator material, or official outcome. No model or evaluator was invoked
while producing this lane.

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
- 8 CPUs, 64 GiB, one node, one task (`scontrol NumTasks=1`; terminal
  `sacct NTasks` may be empty or `1` and `ReqMem` is raw `64G`)
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

Bounded read-only terminal watcher and scheduler capture. Start this immediately
after the job ID is issued; the partition is frozen internally and the unique
node is derived from the terminal allocation row:

```text
python3 protected_rr1_one_tuple_finalizer_v1.py watch-capture \
  --job-id <SLURM_JOB_ID> \
  --output-root <ABSOLUTE_NEW_CAPTURE_ROOT>
```

Private evidence finalization:

```text
python3 protected_rr1_one_tuple_finalizer_v1.py finalize \
  --evidence-root <ABSOLUTE_PRIVATE_RUNTIME_EVIDENCE_ROOT> \
  --capture-root <ABSOLUTE_PRIVATE_CAPTURE_ROOT> \
  --output-root <ABSOLUTE_NEW_FINALIZATION_ROOT>
```

`watch-capture` polls only the exact allocation-level 24-field `sacct` query at
five-second intervals, with a hard limit of 1,440 polls. Nonterminal blank and
`Unknown` scheduling fields are accepted only by the narrow poll identity/state
parser; a terminal row receives the full strict parser. The operator does not
supply partition or node. On one unique terminal row the module binds internal
partition `gpua40i`, derives one canonical `NodeList`, captures `scontrol show
job -dd` first and immediately, then runs the remaining four exact read-only
queries. Every poll argv/count/monotonic time is retained in body-free
provenance. There is no submission, shell, network, or external API route.

The unique terminal observation is bound to exact UTC microseconds and an
integer monotonic-nanosecond timestamp. The first post-job `scontrol` subprocess
must start no more than two monotonic seconds later. Its subprocess launch
occurs **before** any `O_EXCL` write or `fsync` of the terminal `sacct` bytes;
after that launch, any failure still causes those already-held terminal bytes
to be retained and sealed. Every post-terminal command has both a subprocess
timeout and a validated monotonic-duration ceiling of 20 seconds. Per-command
start/completion UTC, start/completion monotonic time, duration, seconds after
terminal observation, and remaining deadline are recorded and arithmetically
validated. The whole five-command sequence must complete within 240 seconds,
leaving a fixed 60-second margin under the live `MinJobAge=300` setting.

A later capture failure does not discard already unique terminal/controller
bytes. The new mode-`0700` root is retained with only safely created raw files
and `SCHEDULER_CAPTURE_CANNOT_CHECK_V1.json`; every retained file is sealed
mode `0400`, and stderr/private details are represented only by SHA-256.

The finalize route never executes scheduler commands. It parses the separate
capture and runtime roots, deterministically constructs the canonical
`SCHEDULER_EXPORT_V1.jsonl` in memory, and writes that export plus the receipt
with verified `O_EXCL` output custody. A pre-existing export in the runtime
root is optional and is treated only as an assertion: it must byte-equal the
deterministic record. Operators never hand-author the export or its source map.

## Private evidence layout

The evidence root and both child directories must be exact mode `0700`.
Every opened evidence file must be owned by the current user, link count one,
and mode `0400` or `0600`. Symlinks, hardlinks, case aliases, duplicate fields,
CRLF, noncanonical JSON, file swaps, and group/world-readable evidence fail
closed.

The finalize CLI and direct API require three distinct path values. The held
runtime-evidence and capture directory descriptors must also resolve to
different `(st_dev, st_ino)` identities; lexical aliases cannot satisfy this
separation requirement.

Capture-root success inputs (all sealed mode `0400` by `watch-capture`):

```text
POST_JOB_SACCT_V1.txt
POST_JOB_SACCT_NONOVERLAP_V1.txt
POST_JOB_SCONTROL_V1.txt
SCHEDULER_CONFIG_V1.txt
SCHEDULER_PARTITION_V1.txt
SCHEDULER_NODE_V1.txt
SCHEDULER_CAPTURE_PROVENANCE_V1.json
```

Runtime evidence-root inputs:

```text
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
opens them. An optional `SCHEDULER_EXPORT_V1.jsonl` assertion may coexist at
the runtime root; it is not required and cannot override generated bytes.

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
5. exact repeated poll/capture argv, capture provenance raw-file hashes,
   UTC/monotonic timing order and arithmetic, two-second first-query latency,
   20-second per-command duration, 240-second sequence deadline,
   deterministic scheduler export, and the complete opened-evidence source-hash
   map.

The scheduler parsers match the fresh Slurm 23.11.3 read-only shapes: config
starts with exactly `Configuration data as of <seconds timestamp>`;
`TaskPlugin` contains both `task/cgroup` and `task/affinity`; partition
`AllowAccounts` is `ALL` or a canonical list containing `lu2026-2-51`; node
`-o` values may contain spaces (including `OS`); and `parsable2` rows contain
exactly 24 fields with no trailing `|`.

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
`0700`. Finalizer receipt/export files use `O_EXCL`, exact mode `0600`,
`fsync`, descriptor reread, SHA-256 verification, and named-inode recheck.
Capture files use the same verified creation path before their exact mode
`0400` seal. Held input reads recheck regular-file type, owner, mode, link
count, identity, size, and modification time after the descriptor read.

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
