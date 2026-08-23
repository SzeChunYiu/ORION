# P10 Native Feature Correction V1

Status: **FROZEN BEFORE NATIVE-STATE OUTCOMES**

Frozen: 2026-08-20

This outcome-blind correction supersedes one implementation bullet in `P10_NATIVE_TRACE_STATE_EXTRACTOR_AMENDMENT_V1.md` and `P10_NATIVE_FEATURE_ENCODING_V1.md`.

`normalized state-digest duplicate-group size` is **not a B4 predictive feature**. Computing a corpus-frequency bucket for a held-out state would make the feature transductive because it depends on what other evaluation states exist.

The normalized state digest is retained only for the exact-state near-duplicate hostile audit. B4 dependency features are therefore only the four strictly pre-tactic, per-state quantities:

- context-to-context reference-edge count;
- context variables referenced in the goal;
- maximum context-reference indegree;
- fraction of context declarations referencing another local.

No native outcome existed when this correction was frozen.
