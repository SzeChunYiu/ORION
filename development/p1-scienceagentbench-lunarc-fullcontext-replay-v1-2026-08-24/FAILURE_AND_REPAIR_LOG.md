# Failure and repair log

## Boundary

All executions used synthetic prompts recovered from fixed public Git objects.
No protected archive, benchmark task, outcome, gold program, evaluator, rubric,
or credential was opened.

## Pre-submission model-hash command

The first remote hash-extraction command used an invalid escaped `awk` program:

```text
awk: cmd. line:1: {print \}
awk: cmd. line:1:        ^ backslash not last character on line
awk: cmd. line:1: {print \}
awk: cmd. line:1:        ^ syntax error
```

No job was submitted by that command. The repair re-ran `sha256sum`, extracted
the first field with `cut`, and required exact size `18556689568` plus SHA-256
`fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad`.

## Scheduler-only change before job 3534209 ran

Job `3534209` was submitted to `gpua40i` and remained `PENDING` with reason
`Resources`. Before it began, its state and partition were verified as
`PENDING/gpua40i`; `scontrol update JobId=3534209 Partition=gpua40` moved only
the scheduler partition to another LUNARC A40 pool. It then ran on `cg01`.
Model, server, CUDA backend, prompt bytes, sampling, order, cache flag, context,
and gates did not change. The repaired job `3534213` was submitted directly to
`gpua40` and ran on `cg04`.

## Job 3534209: not result bearing

Exact accounting: `FAILED`, `00:00:55`, exit `1:0`, `cg01`. The frozen harness
incorrectly treated a source-route 42-token identity as a required direct
`/tokenize` count and raised:

```text
RuntimeError: short_pr1130_replay: raw prompt-token count
```

There were zero `/completion` calls. Postprocessing then tried to open an absent
`results/HARNESS_RECEIPT_V1.json` and raised `FileNotFoundError`. Therefore this
job is `NOT_RESULT_BEARING_INFRASTRUCTURE_PRECHECK_FAILURE`, not a scientific
adverse replay. Its emitted terminal is preserved verbatim even though its
wording predates the classification repair:

```text
P1_SAB_FULLCONTEXT_REPLAY_COMPLETE__TWO_SEPARATE_CONDITIONS_RETAINED__ONE_OR_MORE_ADVERSE__NO_COMPOSITE_SCIENTIFIC_WITNESS__JOB_3534209__COST_CANNOT_CHECK__NO_BENCHMARK_OR_PROTECTED_INPUTS
```

## Smallest repair and failure preflight

Prompt bytes, hashes, parameters, order, backend, and scientific replay gates
were unchanged. The repair:

1. retained direct raw/effective `/tokenize` arrays, counts, and hashes as
   observations rather than equality gates against Ollama source receipts;
2. required only the prospectively specified constant direct `prompt_n` gate;
3. made the harness write explicit infrastructure-failure receipts; and
4. made job postprocessing produce a receipt even when harness/energy receipts
   are missing or invalid.

A local forced connection failure produced durable infrastructure receipts for
both conditions. A separate missing-harness/missing-energy preflight produced a
robust `NOT_RESULT_BEARING_INFRASTRUCTURE_FAILURE` job receipt and terminal.

## Job 3534213: result-bearing mixed/adverse result

Exact accounting: `FAILED`, `00:02:06`, exit `2:0`, `cg04`. Twelve unchanged
direct `cache_prompt=false` requests completed.

The generic shell `ERR` trap also wrote `JOB_FAILURE_V1.json` when the harness
returned the deliberate adverse-gate exit code `2`; its `FAIL_UNPLANNED_COMMAND`
label is overbroad. The receipt is preserved verbatim, but the exact failed
command is the completed harness invocation and the authoritative classification
is the result-bearing adverse `JOB_RECEIPT_V1.json` plus terminal below. It is
not a second infrastructure failure.

- Short PR #1130 replay condition: `PASS_FROZEN_FULLCONTEXT_REPLAY_GATES`.
- Long PR #1130 six-marker condition:
  `ADVERSE_FROZEN_FULLCONTEXT_REPLAY_GATE_FAILURE` because seeds 101 and 202
  produced identical generated token arrays and content.
- The long result still passed within-seed identity, `cache_n=0`, constant
  `prompt_n=27756`, no truncation, and all six markers complete/in order in all
  six requests. The sensitivity gate was not weakened.

Exact result-bearing terminal:

```text
P1_SAB_FULLCONTEXT_REPLAY_COMPLETE__TWO_SEPARATE_CONDITIONS_RETAINED__ONE_OR_MORE_SCIENTIFICALLY_ADVERSE__NO_COMPOSITE_SCIENTIFIC_WITNESS__JOB_3534213__COST_CANNOT_CHECK__NO_BENCHMARK_OR_PROTECTED_INPUTS
```

## Prompt-echo sanitization

`llama-server` echoed each full prompt in its raw response envelope. Before
packet retention, `sanitize_prompt_echoes_v1.py` verified each echoed prompt's
exact byte count and SHA-256, preserved the unretained raw-response hash, removed
the prompt body, wrote a hash/byte receipt in its place, and re-hashed the
sanitized response. Generated content, token IDs, timings, and gates did not
change. A recursive retained-file scan found neither the short prompt prefix nor
`FILLER_0000` after sanitization.

## Cleanup

After all receipts were copied and verified, the isolated remote root was
removed: 68 files, 18,557,293,301 file bytes, 18,557,303,002 `du` bytes. The
root, both jobs, and matching processes were confirmed absent.
