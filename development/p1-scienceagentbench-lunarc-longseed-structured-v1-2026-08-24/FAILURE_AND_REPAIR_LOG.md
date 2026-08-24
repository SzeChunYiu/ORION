# Failure and repair log

## Boundary

The job changed only the `/completion` request field `json_schema` relative to
job `3534250`. The exact prompt, model, runtime binaries/pins, cache/context geometry,
sampling, cap, and order were unchanged. No protected archive, benchmark task,
outcome, gold program, evaluator, rubric, or credential was opened. Prompt
bodies are absent from the retained packet.

For operational isolation, the server listen port changed from `11474` to
`11475` and separate remote code/run directories were used. These are not
`/completion` request fields and are not hidden as scientific-condition changes.

## Local forced-failure preflight

Before submission, the harness was invoked with `/dev/null` as the prompt. It
failed closed with exit `1` and durable status
`NOT_RESULT_BEARING_INFRASTRUCTURE_FAILURE`, error `combined prompt bytes`, and
the frozen prompt/schema hashes and byte counts. This was an intentional local
failure-path test, not a scientific execution.

## Job 3534486: result-bearing pass

Exact accounting: `COMPLETED`, exit `0:0`, `00:01:38`, node `cg04`, partition
`gpua40`. Six requests completed and all frozen gates passed:

- direct raw JSON parse, exact two keys, exact schema, exact ordered markers,
  and allowed choice for all requests;
- within-seed generated-token/content identity for both seeds;
- between-seed generated-token/content sensitivity;
- `cache_n=[0,0,0,0,0,0]`;
- `prompt_n=[27855,27855,27855,27855,27855,27855]`, prospectively matching
  unconstrained job `3534250`; and
- truncation false for all requests.

The exact-schema constraint succeeded, but both seeds selected `iris`. Seed 101
used pretty-printed JSON and seed 202 used compact JSON; their token/content
hashes differed, while their parsed objects were identical. Thus the frozen
token/content sensitivity gate passed, but semantic-choice sensitivity is
`NOT_ESTABLISHED`. No stronger claim is made after observation.

The reused telemetry helper retained its inherited schema label
`longseed-mechanism-gpu-energy.v1`; the authoritative structured classification
is the job/condition receipt. The numeric telemetry fields are preserved
unchanged.

Exact terminal:

```text
P1_SAB_LONGSEED_STRUCTURED_PASS__STRICT_RAW_JSON_EXACT_SCHEMA__WITHIN_SEED_TOKEN_CONTENT_IDENTITY__BETWEEN_SEED_SENSITIVITY__CACHE_N_ZERO__PROMPT_N_27855__NO_TRUNCATION__NONCOMPOSABLE__JOB_3534486__PRODUCTION_BLOCKED__COST_CANNOT_CHECK
```

## Shared-root cleanup repair

The first cleanup invocation used the wrong expected cleanup-script SHA-256
`e40de806908f254621468601519beb580897a8f2f07babafdf8a441d56731f6ce`.
Its fail-closed check exited before cleanup and the root remained present. The
repair used the freshly observed exact script SHA-256
`8d6fba1a8d22853338db44ae422327f8002e517e6a7a13174257c761fd1d1d36`
and removed the shared root.

The retained receipt proves only 66 files / 18,557,665,195 file bytes,
18,557,674,982 pre-cleanup `du` bytes, and root deletion/absence. Job and process
absence are `CANNOT_CHECK_FROM_RETAINED_CLEANUP_RECEIPT`.

Scientific authority delta: `NONE`.
