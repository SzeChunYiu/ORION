# P1 ScienceAgentBench LUNARC open-weight synthetic smoke — handoff

## Terminal

`P1_SAB_OPENWEIGHT_ADVERSE__RR_PHASE1_LENGTH_512__SAME_SEED_101_NONREPLAY__DIFFERENT_SEEDS_3_DISTINCT__LONG_CONTEXT_27764_PASS__JOBS_3533950_3533966__COST_CANNOT_CHECK__REMOTE_CLEANUP_PASS__NO_BENCHMARK_OR_PROTECTED_INPUTS`

## Verdict

**Adverse infrastructure result. Do not promote this route into an official
ScienceAgentBench run plan yet.** The fully pinned local-GGUF/Ollama/A40 route
generated all 11 synthetic requests and passed the different-seed and bounded
long-context probes. It failed two frozen gates:

1. RR phase 1 exhausted the matched fixture's 512-token cap
   (`done_reason=length`); and
2. two byte-identical requests at seed 101 produced different response bytes.

This is synthetic nonbenchmark evidence only. No protected archive, benchmark
task, outcome, gold program, evaluator, rubric, credential, manuscript, PDF,
CI, or pytest path was opened or run.

## Exact pinned route

| Fiber | Pin / observed identity |
|---|---|
| GGUF repository | `unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF` |
| Repository revision | `b17cb02dd882d5b6ab62fc777ad2995f19668350` |
| GGUF | `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` |
| Bytes | `18,556,689,568` |
| GGUF SHA-256 | `fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad` |
| Source tokenizer | `Qwen/Qwen3-Coder-30B-A3B-Instruct@b2cff646eb4bb1d68355c01b18ae02e7cf42d120` |
| Ollama | site module/API `0.32.14` |
| Ollama binary SHA-256 | `d0758d38ac5882a2c68fd930d0c1220af1952469fa9f30c268746d4021709bf4` |
| GPU | NVIDIA A40, UUID `GPU-f35f8ed1-f2a1-2ae4-b9b1-d96fff2203d0`, driver `580.95.05` |
| Endpoint | `http://127.0.0.1:11471` |
| Decoding | `num_ctx=32768`, temperature `0.8`, top-p `0.95`, top-k `20`, repeat penalty `1.0` |
| Seeds | RR `101`, OS `202`, NR `303` |

The content-addressed Ollama blob independently reproduced the GGUF SHA-256.
All four source-tokenizer files and the runtime executable were size/hash
checked before each job. `PINNED_ROUTE_V1.json`, both `PRE_RUN_SHA256SUMS`
files, and both `OLLAMA_STORE_SHA256SUMS` files retain the exact bindings.

## Jobs and failure chain

| Job | Partition / node | Elapsed | SLURM state | Exact disposition |
|---|---|---:|---|---|
| `3533950` | `gpua40i` / `cg13` | 363 s | `FAILED 1:0` | Ten requests completed, then the harness hit `TypeError: zip() takes no keyword arguments` before constructing the long prompt. Preserved; never promoted. |
| `3533966` | `gpua40i` / `cg13` | 288 s | `FAILED 2:0` | All 11 requests completed. Harness deliberately returned 2 because frozen probes were adverse. This is the result-bearing job. |

The job-level `MaxRSS` values cover the batch process, not the separately
running Ollama server. NVIDIA telemetry observed 22,838 MiB maximum VRAM in the
result-bearing job and 100% maximum GPU utilization.

Scheduler repairs used the same pending job IDs—never parallel duplicate GPU
allocations. Exact queue fields and failed/accepted updates are in
`SCHEDULER_REPAIR_RECEIPT_V1.txt` and the failure log.

## Result-bearing synthetic probes (`3533966`)

### RR / OS / NR transport

| Call | Seed | Prompt tokens | Output tokens | Throughput (tok/s) | Wall s | Done reason |
|---|---:|---:|---:|---:|---:|---|
| RR phase 0 | 101 | 154 | 185 | 75.217 | 8.769 | `stop` |
| RR phase 1 | 101 | 364 | 512 | 75.091 | 7.495 | **`length`** |
| OS phase 1 | 202 | 162 | 96 | 152.603 | 1.108 | `stop` |
| NR phase 0 | 303 | 147 | 221 | 82.792 | 3.076 | `stop` |
| NR phase 1 | 303 | 171 | 98 | 78.332 | 1.740 | `stop` |

RR phase 1 included the phase-0 state bytes. OS used one recovered one-shot
call. NR phase 1 was a fresh stateless request with no phase-0 output included.
These are transport observations, not task-quality scores.

### Same-seed replay — adverse

Both request SHA-256 values were exactly:

`68b4bf4bf0c5c59e603bb1c17d0c40edb552ea2173739d4910765b2a5d7e702d`

At seed 101, response-text SHA-256 values differed:

- replay 1: `3c9ae2bcb19e36b9b3c6f15aa0436ba7284dc6b6ffe6f80450079dbe0c5cf42c`
- replay 2: `ebeedd347bd50185bc414a472b0a2d616eaf1345c20c72866ecdf0502f8005b2`

The current witness does not discriminate GPU/kernel nondeterminism from
Ollama/llama.cpp prompt-cache or seed behavior. A cold/warm × CPU/GPU replay
matrix would be a new preregistered experiment, not a repair of these data.

### Different-seed sensitivity — pass

Seeds 101, 202, and 303 produced three distinct response-text hashes. This
confirms sensitivity for the frozen creative prompt but does not repair the
same-seed replay failure.

### Long context — bounded pass

- Source-tokenizer raw precheck: 27,756 tokens.
- Live Ollama `prompt_eval_count`: **27,764**.
- Requested context: 32,768.
- Done reason: `stop`.
- All six frozen markers from positions spanning the beginning through the end
  were reproduced exactly and in order.

This is a no-silent-truncation witness for one frozen synthetic prompt, not a
universal context guarantee.

### Totals and timing

- 11 requests
- 28,974 reported input tokens
- 1,374 generated tokens
- 37.104 s harness wall time
- 79.715 generated tokens/s weighted over generation durations

## GPU seconds, energy, and cost boundary

- SLURM allocated GPU seconds: 363 + 288 = **651 GPU-s**.
- Sampled generation-interval GPU seconds: **126.995 s** total.
- Sample-integrated NVIDIA energy: **3.787746 Wh** total.
- Maximum observed VRAM: **22,838 MiB** of 46,068 MiB.
- SLURM `ConsumedEnergyRaw`: `0`; retained separately rather than substituted
  for the sampled estimate.
- Billed USD: **null**.
- Cost status:
  `CANNOT_CHECK_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION_UNAVAILABLE`.

`projinfo` exposed project core-hours/allocation, and SLURM exposed TRES billing
units. Neither exposed an owner-authoritative conversion to USD or SEK. No
currency value was invented. See `COST_AUTHORITY_PROBE_V1.txt`.

## Network and cleanup boundary

Ollama listened on `127.0.0.1:11471`; all proxy variables were cleared; the
model was imported from the verified local GGUF and no pull was requested or
logged. Ollama's local manifest namespace contains the literal
`registry.ollama.ai`; the observed template-selection line is not a pull event.
This is a bounded configuration/log witness, not a kernel-level egress audit.

Both job traps stopped Ollama and removed imported model stores. After local
receipt/manifest verification, the entire LUNARC root was removed:

- 18,565,097,014 bytes
- 131 files
- cleanup UTC `2026-08-24T12:17:39Z`
- postcondition: root absent

## Focused verification

From the packet directory:

```bash
python3 validate_openweight_packet_v1.py
sha256sum -c SHA256SUMS
```

The validator expects the adverse gates. Changing them to pass makes validation
fail.

## Scientific boundary

`scientific_authority_delta = NONE`. This smoke neither tests nor supports a
Paper 1 superiority or mechanism claim. It shows that the pinned route can run
locally and exposes two reasons it is not yet suitable for official execution:
non-replay at the same seed and RR truncation under the frozen cap.

