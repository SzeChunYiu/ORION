# Failure and repair log

## Boundary

Only the frozen synthetic nonbenchmark prefix/suffix prompt and pinned open
model/runtime were used. No protected archive, benchmark task, outcome, gold
program, evaluator, rubric, or credential was opened. Prompt bodies were staged
for execution but are absent from the retained packet.

## Job 3534250: result-bearing adverse gate

Exact accounting: `FAILED`, exit `2:0`, `00:01:59`, node `cg04`, partition
`gpua40`. The exit code is the deliberate result-bearing adverse-gate code, not
an infrastructure failure. Six frozen `/completion` requests completed.

Passed gates:

- within-seed generated-token/content identity for seeds 101 and 202;
- between-seed generated-token/content sensitivity;
- `cache_n=[0,0,0,0,0,0]`;
- `prompt_n=[27855,27855,27855,27855,27855,27855]`;
- truncation false for all requests; and
- all six markers complete and ordered for all requests.

The strict choice gate was **ADVERSE**. Seed 101 began with:

```text
 Copy exact bytes; do not infer or guess absent values.
```

Seed 202 began with:

```text
 Do not add any text before or after it.
```

Each prefix was followed by an otherwise valid JSON object. The prospective
gate required the raw content itself to parse directly; all six direct parses
failed, so every retained `sampling_choice` is `null`. The harness and packet do
not extract or reparse the embedded object and do not weaken the gate.

Exact terminal:

```text
P1_SAB_LONGSEED_MECHANISM_ADVERSE__ONE_OR_MORE_FROZEN_GATES_FAILED__NONCOMPOSABLE__JOB_3534250__PRODUCTION_BLOCKED__COST_CANNOT_CHECK
```

## Shared-root cleanup repair

The first cleanup invocation used the wrong expected cleanup-script SHA-256
`e40de806908f254621468601519beb580897a8f2f07babafdf8a441d56731f6ce`.
Its fail-closed hash check exited before the cleanup script ran; a subsequent
live check showed the root still present and the exact script SHA-256
`8d6fba1a8d22853338db44ae422327f8002e517e6a7a13174257c761fd1d1d36`.
The repaired command used that exact hash and removed the shared isolated root.

The retained cleanup receipt proves only 66 files / 18,557,665,195 file bytes,
18,557,674,982 pre-cleanup `du` bytes, and root deletion/absence. Job and process
absence are `CANNOT_CHECK_FROM_RETAINED_CLEANUP_RECEIPT`.

Scientific authority delta: `NONE`.

## Byte-exact raw receipts and accounting coverage

The two retained `nvidia-smi` text receipts are preserved byte for byte,
including the vendor-formatted trailing spaces before LF:

- `remote-job-3534250/ENVIRONMENT.txt`: 2,228 bytes, SHA-256
  `4559a9c377ca9849390e9ba03e0c298593b4b2a1c579a70caf3c558ced70bcaf`;
  line 15 is `Mon Aug 24 16:19:05 2026` followed by seven spaces and LF.
- `remote-job-3534250/NVIDIA_SMI_AFTER.txt`: 1,689 bytes, SHA-256
  `a5a3ccf9bdb29b107eae0a223bc9656d759e78798b9308d781caeba02e08fbd5`;
  line 1 is `Mon Aug 24 16:20:30 2026` followed by seven spaces and LF.

The packet-local `.gitattributes` disables Git whitespace diagnostics for only
those two byte-frozen raw paths. It does not normalize or strip them. The
focused validator asserts the exact attribute bytes, raw hashes, and whitespace
lines, and `SHA256SUMS` binds the attributes and both raw receipts.

The mechanism `REMOTE_RUN_SHA256SUMS` already includes `SACCT_V1.txt` with
SHA-256 `ede5e0c90943396377fceec1ab0a83961960665dec8a6e8778a5fc1282a1b8df`.
The top packet receipt now binds that post-job accounting hash independently as
well, and the packet `SHA256SUMS` covers both the top receipt and SACCT file.
