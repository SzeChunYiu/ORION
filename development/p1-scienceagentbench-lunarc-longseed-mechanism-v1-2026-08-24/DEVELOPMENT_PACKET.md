# P1 long-context seed-plumbing mechanism discriminator

## Question

Does the pinned direct full-context route exhibit between-seed sensitivity when
the exact 90,575-byte six-marker prompt is retained as a prefix and a frozen
synthetic suffix creates eight explicitly equally valid continuations under a
higher-entropy temperature `0.8` condition?

## Prospective design

- One frozen combined prompt: exact PR #1130 long prefix plus a 451-byte suffix.
- One frozen request order: `101,202,101,202,101,202`.
- Across requests, seed is the only changed field.
- Same pinned GGUF/runtime/backend, context `32768`, cap `128`, one slot,
  `cache_prompt=false`, and no continuous batching.
- Gates: within-seed generated-token and content identity; between-seed token
  and content sensitivity; `cache_n=0`; constant `prompt_n`; no truncation; all
  six markers complete and ordered; suffix choice in the frozen allowed set.

The result is retained whether pass or fail. No gate will be changed after
observation.

## Non-composability

This is not a rerun or repair of PR #1150's exact temp-`0.2` long condition. It
does not alter the adverse exact-long witness, and it cannot be composed with
that witness to establish production replay, task quality, or official
ScienceAgentBench authorization. A pass can only diagnose seed plumbing when
the output has an explicitly sampling-sensitive continuation at temperature
`0.8`; a failure remains adverse for this mechanism probe.

## Reopen triggers

- prefix, suffix, or combined prompt byte/hash mismatch;
- runtime/model/backend mismatch;
- any cache reuse, prompt-count drift, truncation, or marker loss;
- within-seed mismatch or absent between-seed sensitivity;
- output choice outside the frozen allowed set;
- any protected input access;
- unavailable owner-authoritative billed-cost conversion.

Prompt bodies are staged only for execution. The packet retains hashes, byte
counts, token IDs, response content/tokens, and provenance—not prompt bodies.

Scientific authority delta: `NONE`.

## Observed disposition

Job `3534250` was result bearing and **ADVERSE**. Same-seed generated-token and
content identity passed for both seeds, while between-seed token/content
sensitivity, `cache_n=0`, constant `prompt_n=27855`, no truncation, and complete
ordered markers also passed. The frozen strict choice gate failed in all six
requests because each raw content string included prefix text before an
otherwise valid JSON object. Direct `json.loads(content)` therefore failed and
the recorded choices remained `null`. The content was not extracted, reparsed,
or promoted after observation.

Exact terminal:

```text
P1_SAB_LONGSEED_MECHANISM_ADVERSE__ONE_OR_MORE_FROZEN_GATES_FAILED__NONCOMPOSABLE__JOB_3534250__PRODUCTION_BLOCKED__COST_CANNOT_CHECK
```

This adverse result remains separate from the later structured-output
discriminator. Production replay remains **BLOCKED**.
