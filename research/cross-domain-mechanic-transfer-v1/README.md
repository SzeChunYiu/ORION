# Cross-domain mechanic-contract transfer V1

Additive #286 engineering freeze. **Not scientific transfer evidence.**

## Authority

`LOCAL_ENGINEERING_ONLY`. Existing `orion.transfer` / `orion.transfer.v2` tests remain the #136 substrate and are labelled engineering-only. They do not establish H-T1–H-T4.

## Frozen now

1. Transfer-object schema: `schemas/TRANSFER_OBJECT_SCHEMA_V1.json`
2. Independent source/target family slots + hostile falsifiers: `fixtures/BENCHMARK_DESIGN_V1.json` (`outcomes_accessed=false`)
3. Literature dispositions: `LITERATURE_MATRIX.md` and `fixtures/LITERATURE_MATRIX_V1.json` (local citations only; no arXiv API)
4. Evidence-bound selector + toy hostile/ablation tests under `src/orion/transfer/scientific/`

## Explicitly not established (CANNOT_CHECK)

- Independent held-out cross-domain experiment with target authority
- Matched memory/trajectory/insight/skill baselines on those held-out families
- #283 verification / cross-model reproduction
- Any scientific terminal other than remaining `CANNOT_CHECK`

Promote later only if mechanic contracts beat NL insights **and** applicability receipts beat surface similarity, across more than one source-target family, with every harmful candidate preserved.
