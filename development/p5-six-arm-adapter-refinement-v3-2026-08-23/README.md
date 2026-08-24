# P5 six-arm adapter refinement V3

Outcome-free, synthetic-only successor to
`../p5-six-arm-terminal-adapters-v2`. Nothing in this directory licenses
comparator execution or a performance claim.

## Read first

1. `SCIENTIFIC_REPORT_V3.md`
2. `P5_RESULT_V3.json`
3. `P5_V3_SYNTHETIC_CONFORMANCE_RECEIPT.json`
4. `P5_V3_EXECUTION_BLOCKER_LEDGER.{json,md}`

## Frozen contract

- `P5_V3_REFINED_ADAPTER_PROTOCOL.json`
- `P5_V3_CANDIDATE_VISIBLE_CERTIFICATE_SCHEMA.json`
- `P5_V3_ACTION_WRITE_SURFACE_SCHEMA.json`
- `P5_V3_EIGHT_CLASS_FRONT_REGISTRY.json`
- `P5_V3_NATIVE_TERMINAL_RETENTION_RULES.json`
- `P5_V3_DECLARED_SYNTHETIC_DOMAIN.json`
- `P5_V3_MATCHED_RESOURCE_MANIFEST_TEMPLATE.json`

## Reproduction

```bash
rtk python build_p5_v3_freeze.py
rtk python p5_v3_contract_validator.py
rtk sha256sum -c SHA256SUMS
```

The build uses a fixed freeze timestamp and the validator is deterministic.
It opens no comparator output, benchmark row, protected datum, or performance
table. Do not interpret the 231 synthetic case records as scientific units or
performance observations.
