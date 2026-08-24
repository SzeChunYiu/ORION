# P1 ScienceAgentBench direct-seed repair — handoff

## Terminal

`P1_SAB_DIRECT_SEED_REPAIR_PASS__CACHE_OFF_WITHIN_SEED_TOKEN_IDENTITY__BETWEEN_SEED_SENSITIVITY__CACHE_N_ZERO__PROMPT_N_CONSTANT__JOB_3534123__COST_CANNOT_CHECK__NO_BENCHMARK_OR_PROTECTED_INPUTS`

## Verdict

**Bounded direct-server repair pass.** The PR #1130 Ollama replay evidence was
first canonicalized and remains genuinely adverse: its response content and
generated token arrays differ even after volatile timestamp/timing fields are
removed. A new direct `/completion` route using the exact site Ollama 0.32.14
`llama-server` (llama.cpp `b10434`) and the exact prior GGUF passed the frozen
cache-off replay gate on one LUNARC A40.

This does not retroactively turn PR #1130 into a pass. It discriminates prompt
caching/runtime transport as a sufficient route difference for this fixture.

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
202 replayed across its three cached requests. The negative control therefore
supports the mechanism discriminator without authorizing cache-on production.

## Jobs and resources

| Job | State | Exact disposition |
|---|---|---|
| `3534108` | `CANCELLED by 6350`, top elapsed `00:02:29`; batch `00:03:00`, `0:9` | Missing `GGML_BACKEND_PATH` caused CPU fallback. Partial outputs retained but not result-bearing. |
| `3534123` | `COMPLETED`, `00:01:03`, `0:0` | Exact CUDA backend bound; result-bearing primary and negative control completed. |

- SLURM top-level allocation elapsed: 212 GPU-s total; batch elapsed: 243 s.
- Sampled allocation interval: 135.801 GPU-s total.
- Sample-integrated energy: 1.2592378833333315 Wh total.
- Result-job maximum observed VRAM: 19,581 MiB; utilization reached 100%.
- SLURM `ConsumedEnergyRaw`: 0 for both jobs, retained separately.
- Billed USD: `null`.
- Cost status:
  `CANNOT_CHECK_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION_UNAVAILABLE`.

These resource measures are not currency and no billed cost was invented.

## Cleanup

The exact 18.6 GB model was rehashed after terminating a stale download
process. After both local job manifests verified, the complete remote root was
removed:

- `du` bytes before cleanup: 18,556,938,228;
- file bytes removed: 18,556,917,097 across 87 files;
- cleanup UTC: `2026-08-24T12:59:30Z`;
- postcondition: root absent, no active job, no matching process.

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
publication claim. It must not be used as official ScienceAgentBench execution
authorization on its own.
