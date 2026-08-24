# P1 ScienceAgentBench direct-seed witness — handoff

## Terminal

`P1_SAB_DIRECT_SEED_REPAIR_PASS__CACHE_OFF_WITHIN_SEED_TOKEN_IDENTITY__BETWEEN_SEED_SENSITIVITY__CACHE_N_ZERO__PROMPT_N_CONSTANT__JOB_3534123__COST_CANNOT_CHECK__NO_BENCHMARK_OR_PROTECTED_INPUTS`

Exact interpretation fields:

```text
27764_TOKEN_CACHE_OFF_REPLAY=NOT_RUN
PR1130_EXACT_REPLAY_FIXTURE_DIRECT_ROUTE=NOT_RUN
PRODUCTION_ADMISSIBILITY=NOT_ESTABLISHED
WITNESS_COMPOSITION=FORBIDDEN
```

## Verdict

**Bounded direct-server witness pass.** The PR #1130 Ollama replay evidence was
first canonicalized and remains genuinely adverse: its response content and
generated token arrays differ even after volatile timestamp/timing fields are
removed. A new direct `/completion` route using the same pinned GGUF and the
site Ollama 0.32.14 `llama-server` (llama.cpp `b10434`) passed its own distinct
synthetic cache-off replay gate on one LUNARC A40.

This does not retroactively turn PR #1130 into a pass and is not a causal
repair of its fixture. The prompt, sampling, token cap, context size, and route
differ. The observations therefore cannot identify prompt caching or transport
as the cause of PR #1130's adverse result.

## Non-composability

| Witness | Route and frozen parameters | Status here |
|---|---|---|
| This direct witness | 70-token direct prompt; temperature 0.2; cap 128; context 4096; `llama-server /completion` | Run |
| PR #1130 adverse witness | 42-token Ollama prompt; temperature 0.8; cap 96; context 32768; `/api/generate` | Canonicalized only; exact fixture was not run through the direct route |
| Long-context witness | 27,764-token prompt | Cache-off replay not run |

These witnesses must not be composed. The direct pass cannot be transferred to
the PR #1130 exact replay fixture or to the 27,764-token long-context witness.

## Exact route and result

| Fiber | Exact identity / observation |
|---|---|
| GGUF | 18,556,689,568 B; SHA-256 `fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad` |
| Ollama module | `ollama/0.32.14`; executable SHA-256 `d0758d38ac5882a2c68fd930d0c1220af1952469fa9f30c268746d4021709bf4` |
| llama.cpp | release pin `b10434`; commit `7e4c0a96880dae4fc4268ad441f8a6446bd5460a` |
| llama-server | SHA-256 `234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b` |
| CUDA backend | v13 `libggml-cuda.so`; SHA-256 `fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb` |
| GPU | NVIDIA A40, UUID `GPU-06bb5356-4a6f-8c40-d27d-a0de37505a16`, driver 580.95.05 |
| Geometry | one slot, no continuous batching, 4096 context, 8/8 threads, 512/512 batch, f16 K/V, flash attention on |
| Sampling | temperature 0.2; seeds `101,202,101,202,101,202`; 128-token cap |
| Primary cache | `cache_prompt=false` on every request |
| Primary cache counts | `cache_n=[0,0,0,0,0,0]`; `prompt_n=[70,70,70,70,70,70]` |
| Seed 101 | three identical 61-token arrays; SHA-256 `35ea602a3d475ac1a522d066969b89c26532b5f2504e0409e805ad9153f75659` |
| Seed 202 | three identical 58-token arrays; SHA-256 `10fa4f4e19f20c3a957b25bd572f293a35227972f59901656701d6f901791e8f` |

The two representative seed hashes differ, satisfying the sensitivity gate.
All content hashes also replayed within seed. Raw response hashes differ due to
volatile timings and are not substituted for the required token-array check.

## Negative control

After a server restart, `cache_prompt=true` produced cache reuse:
`cache_n=[0,69,69,69,69,69]`, `prompt_n=[70,1,1,1,1,1]`. Seed 101 failed
within-seed identity across the first uncached and later cached requests; seed
202 replayed across its three cached requests. This is a negative-control
observation within the distinct direct fixture. It does not establish a
mechanism for PR #1130 and does not authorize cache-on production.

## Jobs and resources

| Job | State | Exact disposition |
|---|---|---|
| `3534108` | `CANCELLED by 6350`, top elapsed `00:02:29`; batch `00:03:00`, `0:9` | Missing `GGML_BACKEND_PATH` caused CPU fallback. Partial outputs retained but not result-bearing. |
| `3534123` | `COMPLETED`, `00:01:03`, `0:0` | Exact CUDA backend bound; result-bearing primary and negative control completed. |

- SLURM top-level allocation elapsed: 212 GPU-s total; batch elapsed: 243 s.
- Sampled allocation interval: 135.801 GPU-s total.
- Sample-integrated energy: 1.2592378833333315 Wh total.
- Result-job maximum observed VRAM: 19,581 MiB; utilization reached 100%.
- Job `3534108` top-level SLURM `ConsumedEnergyRaw`: `null`; status
  `CANNOT_CHECK` because the retained top-level field is unreported. Its batch
  and extern step fields are separately observed as `0` and `0`.
- Job `3534123` SLURM `ConsumedEnergyRaw`: top-level `0`, batch step `0`, and
  extern step `0`, each retained separately.
- Billed USD: `null`.
- Cost status:
  `CANNOT_CHECK_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION_UNAVAILABLE`.

These resource measures are not currency and no billed cost was invented.

## Cleanup

The retained cleanup receipt establishes only the recorded counts/bytes and
deletion of the specified remote root:

- `du` bytes before cleanup: 18,556,938,228;
- file bytes removed: 18,556,917,097 across 87 files;
- cleanup UTC: `2026-08-24T12:59:30Z`;
- recorded postcondition: the specified remote root was absent after cleanup.

The retained cleanup receipt does **not** establish a post-termination GGUF
rehash or contemporaneous absence of active jobs or matching processes. Both
are `CANNOT_CHECK_FROM_RETAINED_CLEANUP_RECEIPT`; no retrospective evidence is
added.

## Focused verification

From this packet directory:

```bash
python3 validate_seed_repair_packet_v1.py
sha256sum -c SHA256SUMS
```

No CI, pytest, manuscript, or PDF path is required or authorized.

## Scientific boundary

`scientific_authority_delta = NONE`. This is synthetic nonbenchmark
infrastructure evidence. It opens no protected archive/task/outcome, tests no
official evaluator, and supports no superiority, task-quality, manuscript, or
publication claim. `PRODUCTION_ADMISSIBILITY=NOT_ESTABLISHED`, and the witnesses
must not be composed. It must not be used as official ScienceAgentBench
execution authorization on its own.
