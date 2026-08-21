# P10 Native Line-Receipt Correction V1

Status: **FROZEN BEFORE NATIVE-STATE OUTCOMES**

Frozen: 2026-08-20

The first `p10-native-trace-state-v1` workflow was still queued when this correction was committed; no Mathlib file had been instrumented and no native-state outcome existed.

This correction replaces the custom no-op marker tactic described in `P10_NATIVE_TRACE_STATE_EXTRACTOR_AMENDMENT_V1.md` with a simpler observational mechanism:

- insert **only** Lean's built-in `trace_state` immediately before each frozen collapsed action;
- during deterministic instrumentation, record the unique 1-based instrumented source line of each inserted `trace_state` and bind that line to the transition ID;
- parse Lean's native diagnostic header `<path>:<line>:<column>: info:` and accept a state only when the diagnostic line exactly matches a recorded inserted `trace_state` line;
- restore and re-hash the original source bytes exactly as before.

No custom tactic, namespace, declaration, logging elaborator, instance or helper code is inserted. This reduces intervention surface and removes any risk that a custom elaborator changes local proof behavior.

All scientific feature, coverage, model and hostile-control gates remain unchanged.
