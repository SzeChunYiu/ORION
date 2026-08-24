# P1 full-context replay handoff

## Exact disposition

Two prospectively frozen synthetic conditions were retained separately on the
pinned direct LUNARC A40 route. They are not composed into one scientific
witness.

### Short exact PR #1130 replay prompt

- Prompt: 186 UTF-8 bytes; SHA-256
  `afb432d64085e79f36da380ce0dbc79aa8b5efe221921da06d511480947b4a3b`.
- Sampling: temperature `0.8`, cap `96`, order
  `101,202,101,202,101,202`, `cache_prompt=false`, server context `32768`.
- Result: PASS within-seed generated-token/content identity for both seeds;
  PASS between-seed token/content sensitivity; `cache_n=[0,0,0,0,0,0]`;
  `prompt_n=[35,35,35,35,35,35]`; truncation all false.
- The source Ollama context/prompt-eval identities `42/43` and direct raw/
  effective `/tokenize` counts `35/35` are retained separately. Equality across
  API routes is not a gate.

### Long exact PR #1130 six-marker prompt

- Prompt: 90,575 UTF-8 bytes; SHA-256
  `6c52c9055c03367832e9e61c31f49489194cecd94e732fbc7ca59caeb40cf918`.
- Sampling: temperature `0.2`, cap `128`, order
  `101,202,101,202,101,202`, `cache_prompt=false`, server context `32768`.
- PASS: within-seed generated-token/content identity for both seeds.
- **ADVERSE:** seeds 101 and 202 produced the same 63-token array hash
  `dcbc46bd932fe88f58d183d29a8506dbb51526bceb1458b5335acfeeacdc4cb7`
  and content hash
  `8cd4e6368957918c4a729d5bf43f153cda82812efee137568f814154583f8711`.
- PASS: `cache_n=[0,0,0,0,0,0]`,
  `prompt_n=[27756,27756,27756,27756,27756,27756]`, truncation all false,
  and all six markers complete/in order in every request.
- The source Ollama `prompt_eval_count=27764` and direct raw/effective counts
  `27756/27756` are observations, not cross-route equality gates.

## Runtime and accounting

- GGUF SHA-256:
  `fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad`.
- `llama-server` b10434 / commit
  `7e4c0a96880dae4fc4268ad441f8a6446bd5460a`, executable SHA-256
  `234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b`.
- CUDA v13 backend SHA-256
  `fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb`.
- Jobs: `3534209` infrastructure-only failure, 55 allocated seconds;
  `3534213` result-bearing mixed/adverse, 126 allocated seconds.
- Sampled total: 80.87 GPU-s and 5.874718534722224 Wh.
- Billed USD: `null` / `CANNOT_CHECK_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION_UNAVAILABLE`.
- Cleanup: PASS; isolated remote root absent.

## Claim boundary

Job `3534209` is not result bearing. Job `3534213` does not repair the exact
long-context seed-sensitivity gate. The short pass and long adverse result are
non-composable. This packet does not authorize or support protected benchmark
execution, official task quality, superiority, manuscript, publication, or
production replay claims. Production replay remains **BLOCKED**.

Scientific authority delta: `NONE`.
