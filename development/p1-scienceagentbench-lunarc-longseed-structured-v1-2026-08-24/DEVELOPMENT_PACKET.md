# P1 long-context structured-output discriminator

## Frozen question

With the exact job-3534250 prompt, runtime binaries/pins, cache/context geometry,
sampling, cap, and seed order held fixed, does adding only a byte-frozen `json_schema`
constraint yield strict-schema outputs while retaining same-seed replay and
between-seed sensitivity?

## One changed request field

Only `json_schema` is added. It permits exactly an object with:

- `markers`: the six exact marker strings in exact order; and
- `sampling_choice`: exactly one of the eight frozen allowed strings.

No extra keys or extra prefix/suffix text are allowed. The raw `content` string
must parse directly as JSON before any semantic checks. The gate will not be
weakened or reparsed after observation.

The isolated server listened on port `11475` rather than job `3534250`'s
`11474`, and used a separate remote code/run directory. Those are disclosed
operational isolation changes, not `/completion` request fields; model/runtime
binaries, server geometry, prompt, sampling, order, and gates were unchanged.

## Other gates

Within-seed generated-token/content identity, between-seed token/content
sensitivity, `cache_n=0`, constant direct `prompt_n` equal to the unconstrained
job-3534250 value `27855`, no truncation, exact marker order, and allowed choice.

## Non-composability

This is a structured-output mechanism diagnostic. It leaves job `3534250`
adverse and leaves PR #1150's exact temp-`0.2` long result adverse. Even a pass
does not compose with either result, does not establish production replay, and
does not authorize protected or official ScienceAgentBench execution.

The exact verified staged model is reused before a single shared-root cleanup;
availability is reverified before submission and is not inferred from prior
cleanup claims.

Scientific authority delta: `NONE`.

## Observed disposition

Job `3534486` passed every prospectively frozen structured-output gate. All six
raw content strings parsed directly as JSON with exactly the two allowed keys,
the exact ordered markers, and an allowed choice. Same-seed generated-token and
content identity, between-seed token/content sensitivity, `cache_n=0`, constant
`prompt_n=27855`, and no truncation also passed.

Both seeds selected `iris`. The between-seed token/content difference was JSON
formatting, while the parsed objects were identical. Therefore semantic-choice
sensitivity is **NOT_ESTABLISHED**; it was not a frozen gate and is not inferred
from formatting sensitivity.

Exact terminal:

```text
P1_SAB_LONGSEED_STRUCTURED_PASS__STRICT_RAW_JSON_EXACT_SCHEMA__WITHIN_SEED_TOKEN_CONTENT_IDENTITY__BETWEEN_SEED_SENSITIVITY__CACHE_N_ZERO__PROMPT_N_27855__NO_TRUNCATION__NONCOMPOSABLE__JOB_3534486__PRODUCTION_BLOCKED__COST_CANNOT_CHECK
```

Job `3534250` remains adverse. The two jobs are non-composable and production
replay remains **BLOCKED**.
