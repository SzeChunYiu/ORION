# P1 ScienceAgentBench exact GGUF tokenizer probe V1

Date: 2026-08-24
Lane: `development/p1-scienceagentbench-exact-tokenizer-probe-v1-2026-08-24/`
Fresh base: `origin/main` at `9e35809a45f96458fe8d52459140e533aa27b3da`
LUNARC job: `3537594`

## Bounded verdict

One bounded A40 job validated the exact frozen GGUF tokenizer route on four
invented prompts only. The allocation completed with state `COMPLETED`, exit
code `0:0`, and elapsed time `00:01:00`. Its exact stdout terminal was:

```text
P1_SAB_EXACT_GGUF_TOKENIZER_PROBE_PASS__JOB_3537594__NO_GENERATION__NO_PROTECTED_INPUTS__COST_CANNOT_CHECK
```

`POST /tokenize` returned identical integer token-ID arrays across all three
repeats of each of eight records: four invented prompts times two explicit
tokenizer modes. This establishes exact route repeatability for the frozen
runtime and those invented probes. It does **not** establish protected prompt
fit, production admissibility, generation correctness, benchmark performance,
or any outcome claim.

## Required completion-equivalent mode

The completion-equivalent request is explicit and must not be inferred:

```json
{"content":"<exact UTF-8 prompt>","add_special":true,"parse_special":true}
```

It is sent only to the loopback `POST /tokenize` route. A ledger producer must
hash the exact UTF-8 prompt bytes and serialized request, repeat the request
three times, require identical integer arrays, and retain token IDs, count, and
response hashes.

Mode is scientifically material. The invented prompt containing the literal
marker `<|im_start|>` produced 13 tokens in `true,true` mode, including special
token ID `151644`, versus 16 tokens in `false,false` mode. The arrays were not
identical. The three invented probes without a literal special marker had
identical arrays across the two modes, which does not remove the need to bind
the mode explicitly.

## Repeatability evidence

| Invented prompt label | UTF-8 bytes | `true,true` tokens | `false,false` tokens | Repeats per mode |
|---|---:|---:|---:|---:|
| `ascii` | 36 | 14 | 14 | 3 |
| `unicode` | 56 | 13 | 13 | 3 |
| `json_like` | 185 | 46 | 46 | 3 |
| `literal_special_marker` | 74 | 13 | 16 | 3 |

All eight token records satisfy:

- declared count equals array length;
- every token ID is an integer and not a Boolean;
- `repeat_count` is exactly `3`;
- all three raw-response SHA-256 values are identical;
- `repeatable_token_ids` is `true`.

The token IDs and request/prompt/response SHA-256 values are retained in
`TOKENIZER_PROBE_V1.json`; invented prompt bodies exist only in the frozen job
script. No protected body is present.

## Frozen runtime and geometry

- model bytes: `18556689568`;
- model SHA-256: `fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad`;
- llama-server SHA-256: `234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b`;
- CUDA backend SHA-256: `fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb`;
- llama.cpp: `b10434`, commit `7e4c0a96880dae4fc4268ad441f8a6446bd5460a`;
- loopback: `127.0.0.1:11479`;
- context: `32768` tokens, one parallel slot;
- continuous batching: off;
- context shift: off;
- prompt cache: not applicable to `/tokenize` and unused;
- model tokenizer metadata: add BOS `false`, add EOS `false`.

The frozen job script independently verified the full model, server, and CUDA
backend hashes before startup and the model hash again after cleanup. The
validator binds the copied script itself to its exact remote SHA-256.

## Allocation and cleanup

Job `3537594` used account `lu2026-2-51`, partition `gpua40i`, one A40, eight
CPUs, and 64 GiB with a 20-minute limit. `SACCT_V1.txt` records the completed
allocation and step rows. `CLEANUP_V1.json` reports both process-group and
loopback-listener absence. Exactly one SLURM job was used; this packaging lane
submits no job.

Billed USD remains:

```text
CANNOT_CHECK_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION_UNAVAILABLE
```

No dollar estimate is substituted for owner-authoritative accounting.

## Exact remote bindings

`REMOTE_ARTIFACT_SHA256SUMS` was captured from the remote job root and binds:

- `job.slurm` -> `FROZEN_JOB_SCRIPT_V1.slurm`;
- `slurm-3537594.out` -> `TERMINAL.txt`;
- `JOB_RECEIPT_V1.json`;
- `TOKENIZER_PROBE_V1.json`;
- `CLEANUP_V1.json`;
- `FROZEN_RUNTIME_HASHES.txt`;
- `FROZEN_TOKENIZER_GEOMETRY.json`;
- `SLOTS.json`.

The fail-closed validator maps each remote path to the repository copy and
requires its exact bytes and SHA-256. `SHA256SUMS` separately binds every lane
file other than the manifest itself.

## Artifact inventory

- `EXACT_TOKENIZER_RESULT_V1.json` - bounded typed result and claim boundary.
- `JOB_RECEIPT_V1.json` - exact remote job receipt.
- `TOKENIZER_PROBE_V1.json` - exact token IDs, counts, modes, and repeat hashes.
- `CLEANUP_V1.json` - process-group and loopback-listener cleanup receipt.
- `FROZEN_RUNTIME_HASHES.txt` - exact runtime identities.
- `FROZEN_TOKENIZER_GEOMETRY.json` and `SLOTS.json` - route geometry evidence.
- `FROZEN_JOB_SCRIPT_V1.slurm` - exact invented-only remote job script.
- `SACCT_V1.txt` - completed allocation evidence.
- `TERMINAL.txt` - exact one-line stdout terminal.
- `REMOTE_ARTIFACT_SHA256SUMS` - remote-to-repository integrity bridge.
- `validate_exact_tokenizer_probe_v1.py` - fail-closed static validator.
- `HANDOFF_V1.md` and `SHA256SUMS` - reviewer handoff and integrity manifest.

## Explicit exclusions and authority boundary

This lane contains no GGUF/model binary, server/backend binary, server log,
protected task/prompt/packet body, generated completion, evaluator, rubric,
gold answer, official outcome, API credential, or external API payload. The
remote server log and SLURM stderr were unnecessary to validate the completed
PASS and are excluded. No generation or evaluation endpoint was invoked.

The exact typed boundaries remain:

- protected prompt fit: `CANNOT_CHECK_NO_PROTECTED_PROMPT_OPENED_OR_TOKENIZED`;
- production admissibility: `CANNOT_CHECK`;
- generation correctness: `CANNOT_CHECK_NOT_INVOKED`;
- benchmark/outcome claim: `NONE`;
- official tasks opened: `0`;
- official outcomes opened: `0`;
- scientific-authority delta: `NONE`.

## Validation

Run from the repository root:

```bash
rtk python -m py_compile development/p1-scienceagentbench-exact-tokenizer-probe-v1-2026-08-24/validate_exact_tokenizer_probe_v1.py
rtk python development/p1-scienceagentbench-exact-tokenizer-probe-v1-2026-08-24/validate_exact_tokenizer_probe_v1.py
rtk proxy sh -c 'cd development/p1-scienceagentbench-exact-tokenizer-probe-v1-2026-08-24 && sha256sum -c SHA256SUMS'
rtk git diff --check origin/main...HEAD
```

No pytest, CI, manuscript build, or PDF workflow is part of this result.
