# Development packet — issue #1086 P9 replay-divergence closure

## Atomic questions

1. Can the locked 0.50-vs-0.75 serialized-arm divergence be resolved
   mechanistically, with both numbers reproduced on demand by toggling exactly
   one factor?
2. Can determinism be enforced at the protocol level (a pinned replay entry
   point with an environment fingerprint that actually discriminates the
   computation), rather than by hardcoding a constant?
3. Do two clean replays under the pinned stack produce identical case-level
   predictions and digests?

## Scope

Adds a single documented pinned entry point (`top_tier/replay_d1v1_2_pinned.py`)
whose numeric canary fingerprints the executing numerical build below the
recorded version manifest and predicts which attractor a run lands on before
any accuracy is read; a two-phase toggle demonstrator
(`top_tier/demonstrate_d1v1_2_build_toggle.py`) that feeds bit-identical design
inputs to different binary builds and records both outcomes; three evidence
receipts (binary-build toggle plus two pinned replays R1/R2); a binding checker
over the committed tree; and focused unit tests that assert the
environment-independent contract.

The deciding factor is established to be the binary build of the numerical
stack executing lbfgs, not the version manifest, seed, dataset, code path, or
arm config. No claim row changes, no historical terminal is relabelled, and
`P9_D1V1_2_LOCKED_ENV_REPRODUCTION_FAILED` stays append-only.

## Honest limits

The divergent side is demonstrated by same-class conda builds, not by the exact
binary of the #1096 preflight (not recoverable from the repo). Sides A and B
also differ in CPython/NumPy patch versions, so binary-build-vs-patch-version
attribution is not fully separated by the toggle alone; the operative fact —
the version manifest cannot pin this replay — is unaffected. All executions are
on one machine; no fresh-container or independent-custody replication is
claimed.

## Verification

```bash
python papers/orion-19-structured-epistemic-learning/top_tier/replay_d1v1_2_pinned.py --require-attractor ARCHIVE_MATCH
python papers/orion-19-structured-epistemic-learning/top_tier/check_d1v1_2_pinned_replay_v1.py
python -m pytest -q tests/unit/study/p9/test_p9_d1v1_2_pinned_replay.py
```
