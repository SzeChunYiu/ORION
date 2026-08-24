# PROTECTED_PROMPT_FIT_PREFLIGHT_V1 handoff

## Bounded status

This additive lane implements and synthetically hostile-validates an
outcome-blind protected packet-binding and prompt-fit preflight for the merged
ScienceAgentBench direct route. No protected source was opened during
development. No task, model, provider, candidate program, evaluator, rubric,
gold, outcome, LUNARC, CI, pytest, manuscript, or PDF route was run.

The packet does **not** establish production admissibility. It does not modify
or authorize the Runner, adapter, direct generation driver, evaluator,
analysis, or any other lane.

## What is now bound

- Exact merged mask manifest and verified Parquet identity.
- Hardcoded model repository, revision, filename, 18,556,689,568-byte size,
  GGUF SHA-256, server SHA-256, and llama.cpp identity; a mutable contract and
  matching mutable ledger cannot redefine them.
- Mandatory production agreement between an independent live-staging receipt
  and a separate full byte-count/SHA-256 measurement of the staged GGUF from a
  held descriptor. An external source-receipt SHA-256 is provenance only.
- Exact direct-route contract, prompt bundle, driver, canonical insertion
  rule, paired seeds, context window, and phase output caps.
- Exact seven-field authorized row shape with no extra fields.
- Every task ID/domain and all five source values against the corresponding
  manifest record's type, canonical byte count, field SHA-256, and aggregate
  binding SHA-256.
- Exact masked and recovered packet byte counts/hashes without packet bodies.
- Exact UTF-8 byte counts/hashes for 1,224 state-independent prompts across
  102 tasks and three attempts without prompt bodies.
- Three RR phase-1 dynamic records per task, retained as typed
  `CANNOT_CHECK` because generated RR phase-0 state is required.
- Optional exact-GGUF token-ledger identity, prompt-hash completeness, and
  context arithmetic without claiming independent token remeasurement.
- Component-wise no-follow `openat` traversal with every input/upstream file
  descriptor and directory edge held until completion; output creation uses
  the held parent descriptor, verifies the final output-name identity and
  digest, and rolls back only an unchanged created receipt. A replacement at
  the output name is detected without deleting the replacement.

## Production input contract

The preflight does not decode Parquet. An authorized owner must extract only
the seven permitted columns from the exact verified Parquet into one canonical
JSON-plus-LF file:

```json
{
  "authority": "OWNER_AUTHORIZED_PROTECTED_INPUT_ONLY__NO_OUTCOME_AUTHORITY",
  "rows": [
    {
      "dataset_folder_tree": "<exact source string>",
      "dataset_preview": null,
      "domain": "<exact source string>",
      "domain_knowledge": "<exact source string or null>",
      "instance_id": "1",
      "output_fname": "<exact source string>",
      "task_inst": "<exact source string>"
    }
  ],
  "schema_version": "orion.p1.scienceagentbench.authorized-row-source.v1",
  "source": {
    "dataset": "osunlp/ScienceAgentBench",
    "extraction_mode": "STRICT_JSON_AUTHORIZED_EXTRACTION",
    "official_outcomes_opened": false,
    "revision": "9c6e96c9e74572e979b0930ee735041cef528cb7",
    "split": "verified",
    "verified_parquet_sha256": "c6f937863a220bd1762a00c20a0f79cc8dfca900b819bdb552150310731ae147"
  }
}
```

The example shows shape only. Do not commit the real extraction, any packet
body, rendered prompt body, token-ledger body if it is treated as protected,
or production receipt unless separate retention authority explicitly permits
it. The real `rows` array must contain task IDs 1 through 102 exactly once and
in manifest order.

## CLI

All paths must be absolute. The destination must not exist.

```text
rtk env PYTHONDONTWRITEBYTECODE=1 python3 \
  development/p1-scienceagentbench-protected-prompt-fit-preflight-v1-2026-08-24/protected_prompt_fit_preflight_v1.py \
  --row-source /absolute/authorized_rows.json \
  --mask-manifest /absolute/MASK_MANIFEST_V1.json \
  --prompt-bundle /absolute/DIRECT_ROUTE_PROMPT_BUNDLE_V1.json \
  --live-gguf /absolute/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf \
  --live-staging-receipt /absolute/live_gguf_staging_receipt.json \
  --output /absolute/new_protected_prompt_fit_receipt.json
```

The live staging receipt must be canonical JSON plus one LF, use schema
`orion.p1.scienceagentbench.live-gguf-staging-receipt.v1`, carry authority
`INDEPENDENT_LIVE_GGUF_STAGING_MEASUREMENT__NO_TASK_OR_OUTCOME_AUTHORITY`,
copy the exact hardcoded `model_binding`, and record an independent full-file
SHA-256/byte-count measurement completed before preflight. The CLI then
independently reads and hashes the entire `--live-gguf` through its already-
held descriptor. Both measurements must match the hardcoded identity. A
`source_receipt_sha256` may be null or an exact external receipt hash, but it
never replaces live byte count or SHA-256.

`--token-ledger /absolute/exact_gguf_token_ledger.json` is optional. Without
it, all live token counts remain null and static fit is
`CANNOT_CHECK_EXACT_GGUF_TOKEN_LEDGER_NOT_SUPPLIED`. Never use a substitute
tokenizer. A ledger must use schema
`orion.p1.scienceagentbench.exact-gguf-token-ledger.v1`, copy the exact
`tokenizer_binding` and `source_bindings`, and contain exactly one record for
each `(instance_id, phase_id, attempt)` state-independent prompt with its
bound prompt SHA-256 and nonnegative integer token count.

All inputs and static upstreams are opened before any body is read. Symlinked
components, aliases, or path changes fail closed. The receipt is created with
`openat` against a held parent descriptor; input or parent replacement during
the write triggers verified rollback of only the unchanged created receipt.
The final output-name identity and digest are reverified; a concurrent
replacement at that name fails closed and is never deleted as rollback.

## Interpretation

Even with a complete ledger and all 1,224 state-independent prompts fitting,
the overall result stays:

```text
RR_PHASE1 = CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_REQUIRED
production_admissibility = CANNOT_CHECK
semantic_choice_sensitivity = NOT_ESTABLISHED
billed_cost_usd = null
billed_cost_status = CANNOT_CHECK
scientific_authority_delta = NONE
```

If any supplied static token count plus its frozen phase cap exceeds 32,768,
the adverse `DOES_NOT_FIT_FROM_BOUND_TOKEN_LEDGER` result is retained. Do not
truncate, shift context, change the cap, drop the task, or revise the design
after seeing tasks or outcomes.

## Review and next authority gate

Run only the local bounded checks listed in `DEVELOPMENT_PACKET.md`. Review in
a `[skip ci]` pull request and do not merge from this handoff. A separate,
owner-authorized protected staging step must create the extraction, produce
the independent staging receipt, expose the exact live GGUF for full preflight
rehashing, optionally produce exact prompt-token counts, inspect the body-free
receipt, and decide whether any direct generation run may proceed.
