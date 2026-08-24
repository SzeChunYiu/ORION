# P1 ScienceAgentBench LUNARC deterministic-seed repair — development packet

Date: 2026-08-24  
Scope: synthetic nonbenchmark inference only  
Authority: diagnostic infrastructure witness only; scientific-authority delta `NONE`

## Frozen question

PR #1130 retained an adverse same-request/same-seed replay result from the
Ollama `/api/generate` route. This follow-up asks the smallest discriminator:

> With the same pinned public GGUF and the `llama-server` shipped by site
> Ollama 0.32.14 (whose source pin is llama.cpp `b10434`), does direct
> `/completion` replay produce identical returned token arrays for alternating
> seeds `101,202,101,202,101,202` when prompt caching is disabled per request?

The primary gate requires all of the following in one fresh server process:

1. the three token arrays for seed 101 are identical;
2. the three token arrays for seed 202 are identical;
3. the representative arrays for seeds 101 and 202 differ;
4. every `timings.cache_n` is zero; and
5. every `timings.prompt_n` is the same.

The route is frozen to one A40, one server slot, no continuous batching, f16 K
and V caches, temperature 0.2, fixed CPU and batch thread counts, and the exact
public model/runtime hashes recorded by the prior adverse packet.

## Required evidence order

Before spending another GPU allocation, the two PR #1130 replay payloads are
copied byte-for-byte under `source-pr1130/` and canonicalized after removing
only timestamp and duration fields. The canonicalization must decide whether
the response text and returned Ollama `context` token arrays really differed;
it must not infer non-replay from raw response hashes alone.

Only after that check may the fresh direct-server experiment run. After the
primary cache-off condition, the server is restarted and the same sequence is
run with `cache_prompt=true` as a negative control.

## Bounded diagnostics

If and only if the primary cache-off condition fails, at most two one-variable
diagnostics run within the same allocation:

1. add `CUBLAS_WORKSPACE_CONFIG=:4096:8`, retaining the fixed server geometry
   and fixed `--threads 8 --threads-batch 8`; then
2. remove that environment change and change only `--flash-attn on` to
   `--flash-attn off`.

No greedy-decoding substitution is admissible: it would answer a different
production question by suppressing the tested stochastic route.

## Reopen triggers

- Any model, Ollama, llama-server, or linked-library hash mismatch fails closed.
- Missing returned tokens, `cache_n`, `prompt_n`, raw request/response bytes,
  scheduler accounting, telemetry, or cleanup evidence fails closed.
- Cache-off token-array mismatch is adverse even if response text happens to
  normalize to the same string.
- Equal outputs across seeds fail sensitivity; determinism without sensitivity
  is not an adequate witness that request seeds are honored.
- A negative control that does not reuse cache is retained as observed, not
  rewritten to fit an expectation.
- Owner-authoritative allocation-to-currency conversion absence produces
  `CANNOT_CHECK`, never zero or an invented USD estimate.

## Forbidden inputs and actions

No protected ScienceAgentBench archive, task, outcome, gold program, evaluator,
rubric, credential, or secret may be opened, mounted, copied, or inferred. No
official benchmark run is authorized. No manuscript, PDF, CI, or pytest path is
within scope.

