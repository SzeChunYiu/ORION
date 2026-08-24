# P1 ScienceAgentBench full-context replay discriminator

## Development question

Can the exact synthetic PR #1130 short replay prompt and exact synthetic PR
#1130 six-marker long prompt satisfy same-seed replay on the already-bound
direct `llama-server` cache-off A40 route, without opening any protected
ScienceAgentBench material?

## Frozen fibers

1. Reuse the PR #1130 short prompt bytes, but run the prospective order
   `101,202,101,202,101,202` at temperature `0.8`, cap `96`, context `32768`.
2. Reuse the PR #1130 long prompt bytes, but run that same order at temperature
   `0.2`, cap `128`, context `32768`.
3. Bind the exact model, GGUF, `llama-server`, and CUDA backend identities already
   retained by PRs #1130 and #1139.
4. Require prompt token-ID receipts, within-seed generated-token and content
   identity, between-seed sensitivity, `cache_n=0`, constant `prompt_n`,
   no truncation, and complete ordered markers for the long condition.

## Saturation and challenge

The discriminator changes neither the model nor the backend. This packet tests
two prompt-specific full-context conditions; it does not isolate prompt length,
prompt content, context, sampling, or cap effects relative to PR #1139. The
prospective gate is not weakened after observation. A failure remains adverse;
a pass is only a bounded synthetic infrastructure witness.

Competing explanations left open include backend nondeterminism at full context,
prompt-length-dependent kernels, seed handling, and application-level caching.
The direct route records `cache_prompt=false`, one slot, no continuous batching,
and observed `cache_n`; these observations do not causally isolate application
caching from the other changed conditions or competing explanations.

## Reopen triggers

- runtime, GGUF, CUDA backend, or tokenizer identity mismatch;
- any cache reuse, prompt-count drift, truncation, or marker loss;
- any within-seed mismatch or absent between-seed sensitivity;
- unavailable owner-authoritative cost conversion;
- any protected benchmark, outcome, evaluator, or credential access.

## Frozen implementation hypothesis

Both conditions will pass all gates on one LUNARC A40 using the pinned direct
`llama-server` route. Prompt bodies are staged from fixed PR #1130 Git objects
for execution but are not retained in this additive packet; only full hashes,
byte counts, token IDs, and source object paths are retained.

The PR #1130 short source context prefix had 42 retained token IDs and its
Ollama `prompt_eval_count` was 43. Those are source-route identities, not a
preregistered equality gate for the direct `/tokenize` endpoint. Direct raw and
effective token arrays/counts/hashes are retained as observations. The replay
gate requires only constant direct `prompt_n` within each frozen condition.

Scientific authority delta: `NONE`.
