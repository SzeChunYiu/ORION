# P1 source-native target semantics V8

Bounded G16 successor using public primary target-vocabulary evidence only.
No main-checkout or manuscript file is modified by this lane.

## Read first

1. `SCIENTIFIC_REPORT_V8.md`
2. `P1_RESULT_V8.json`
3. `P1_V8_ADAPTER_ADJUDICATION_RESULT.json`
4. `P1_V8_CONDITIONAL_EQUIVALENCE_THEOREM.{json,md}`

## Registries and completion contract

- `P1_V8_PUBLIC_TARGET_SOURCE_REGISTRY.json`
- `P1_V8_RIGHTS_REGISTRY.json`
- `P1_V8_TARGET_SEMANTIC_REGISTRY.json`
- `P1_V8_720_ADAPTER_REGISTRY.json`
- `P1_V8_REQUIRED_FIELD_CUSTODIAN_REGISTRY.json`
- `P1_V8_REQUIRED_OWNER_ALGEBRA_SCHEMA.json`

## Direct reproduction

```bash
rtk python build_v8_freeze.py
rtk python capture_and_adjudicate_v8.py \
  --repo-root /Users/billy/Documents/Codex/2026-08-23/can-x20/work/orion-takeover \
  --predecessor ../p1-source-native-action-adapter-v2
rtk python verify_v8.py --online \
  --repo-root /Users/billy/Documents/Codex/2026-08-23/can-x20/work/orion-takeover \
  --predecessor ../p1-source-native-action-adapter-v2
rtk sha256sum -c SHA256SUMS
```

The online capture hashes public commit-specific bodies in memory and discards
them. No remote source payload, case text, outcome row, protected datum, or
system output is retained in this directory.
