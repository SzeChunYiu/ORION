# Failure and direct-run correction log

## 1. PR #1130 replay was genuinely adverse

The two retained seed-101 requests from PR #1130 are byte-identical (SHA-256
`68b4bf4bf0c5c59e603bb1c17d0c40edb552ea2173739d4910765b2a5d7e702d`).
After excluding only `created_at` and the four duration fields, the evidence did
not collapse to a timing-only mismatch:

- response text differs;
- the derived 42-token prompt prefixes are identical;
- generated token arrays differ (59 versus 61 tokens); and
- the first generated-token difference is index 16 (full-context index 58).

This confirms and preserves the prior adverse result. It is not rewritten by
the later, non-composable direct-server witness.

## 2. Model staging interruption

The initial single-connection resumable download slowed materially and was
locally interrupted. The same pinned URL was resumed with bounded
multi-connection `aria2c`. Retained pre-run manifests for jobs `3534108` and
`3534123` record the model at exactly 18,556,689,568 bytes and SHA-256
`fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad`.

The retained cleanup receipt does not establish a post-termination GGUF rehash
or contemporaneous process absence. Those claims are not reconstructed
retrospectively.

No model-staging currency receipt exists; cost remains `CANNOT_CHECK`.

## 3. Job 3534108 — exact CUDA backend was not selected

SLURM allocated an A40 on `cg15`, but direct `llama-server` emitted:

```text
warning: no usable GPU found, --gpu-layers option will be ignored
warning: one possible reason is that llama.cpp was compiled without GPU support
```

The first submitted script set `LD_LIBRARY_PATH` but not b10434's explicit
out-of-tree backend selector. The server therefore loaded the 18.6 GB model on
CPU and completed the six-request primary condition there. That partial CPU
condition happened to satisfy its token gates, but it is **not A40 evidence**
and is not result-bearing. The cache-on condition completed only one request.

The job was intentionally cancelled by user `6350` rather than continuing a
route that violated the frozen GPU question:

- top-level state: `CANCELLED by 6350`, elapsed `00:02:29`;
- batch state: `CANCELLED`, elapsed `00:03:00`, exit `0:9`;
- submitted script SHA-256:
  `c526ff9b4f3493f724b868804d2b3f741b8b5bc9a6d93a794cf5351076825ccf`.

All partial requests, responses, logs, telemetry, hashes, and accounting are
retained under `remote-job-3534108/`.

## 4. Backend binding correction for the new direct route

llama.cpp b10434 loads its optional backend through `GGML_BACKEND_PATH`; Ollama
v0.32.14's own `SetupLlamaServerCommandEnv` performs the same binding. The only
direct-route job correction was therefore:

```text
GGML_BACKEND_PATH=/sw/pkg/ollama/0.32.14/lib/ollama/cuda_v13/libggml-cuda.so
```

The backend was pinned at SHA-256
`fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb`.
The corrected direct-route script SHA-256 was
`cf9c19b076b473306b9151c1534226fcc7e6f8b4c47f2ab72ceba3319a82dc24`.
No scientific gate, seed, temperature, prompt, server geometry, KV type, or
request order changed between jobs `3534108` and `3534123`. This corrects the
GPU backend binding for the new direct route only; it is not a causal repair of
the distinct PR #1130 Ollama fixture.

## 5. Job 3534123 — result-bearing direct witness and negative control

The corrected direct-route A40 job completed in `00:01:03` with exit `0:0`.

Primary `cache_prompt=false`:

- seed sequence `101,202,101,202,101,202`;
- seed-101 token-array SHA-256 repeated three times:
  `35ea602a3d475ac1a522d066969b89c26532b5f2504e0409e805ad9153f75659`;
- seed-202 token-array SHA-256 repeated three times:
  `10fa4f4e19f20c3a957b25bd572f293a35227972f59901656701d6f901791e8f`;
- `cache_n = [0,0,0,0,0,0]`;
- `prompt_n = [70,70,70,70,70,70]`.

Raw response bytes still differ because their timing payloads differ. The
content and returned token arrays—not volatile timings—are identical within
seed and sensitive between seeds.

After a server restart, `cache_prompt=true` produced
`cache_n=[0,69,69,69,69,69]` and `prompt_n=[70,1,1,1,1,1]`. Seed 101 did not
replay across the uncached first request and later cached requests; seed 202 did
replay within its three cached requests. This observed negative control is
retained, not normalized, but does not identify the cause of PR #1130's
adverse result.

Because the primary cache-off condition passed, neither conditional diagnostic
(`CUBLAS_WORKSPACE_CONFIG=:4096:8`, flash attention off) ran. Greedy decoding
was forbidden and not run.

## 6. Non-composability and production boundary

The direct witness used a 70-token prompt, temperature 0.2, cap 128, and
context 4096. PR #1130 used a distinct 42-token Ollama prompt, temperature 0.8,
cap 96, and context 32768. The 27,764-token long-context cache-off replay was
not run. Exact interpretation fields are:

```text
27764_TOKEN_CACHE_OFF_REPLAY=NOT_RUN
PR1130_EXACT_REPLAY_FIXTURE_DIRECT_ROUTE=NOT_RUN
PRODUCTION_ADMISSIBILITY=NOT_ESTABLISHED
WITNESS_COMPOSITION=FORBIDDEN
```

These witnesses must not be composed.
