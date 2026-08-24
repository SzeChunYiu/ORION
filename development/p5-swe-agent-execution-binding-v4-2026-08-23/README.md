# P5 C1 SWE-agent execution binding V4

Outcome-blind successor lane for the C1 SWE-agent fields in the P5 six-arm
panel. This directory does not license comparator execution or any performance
claim.

## Read first

1. `SCIENTIFIC_REPORT_V4.md`
2. `P5_C1_V4_RESULT.json`
3. `P5_C1_V4_FIELD_REGISTRY.json`
4. `P5_C1_V4_NEGATIVE_LEDGER.{json,md}`

## Core bindings

- `P5_C1_V4_EXECUTION_BINDING_PROTOCOL.json`
- `P5_C1_V4_SOURCE_RIGHTS_MANIFEST.json`
- `P5_C1_V4_NATIVE_OUTPUT_SCHEMA.json`
- `P5_C1_V4_WRITE_SURFACE_SCHEMA.json`
- `P5_C1_V4_NATIVE_TERMINAL_RULES.json`
- `P5_C1_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json`
- `P5_C1_V4_CUSTODY_HANDOFF_SCHEMA.json`
- `p5_c1_native_parser.py`
- `p5_c1_isolated_runner.py`
- `SWE_AGENT_DEPENDENCY_LOCK_V4.uv.lock`
- `UPSTREAM_SIMPLE_INSTANCE.yaml`

## Outcome-free verification

```bash
rtk python build_p5_c1_v4_freeze.py
rtk python p5_c1_v4_validator.py
rtk sha256sum -c SHA256SUMS
```

No pytest or repository CI is part of this lane. The isolated runner's
preflight must refuse with 12 blockers; execution is forbidden until every
required field is independently BOUND.
