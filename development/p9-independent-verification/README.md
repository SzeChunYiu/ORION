# P9 independent verification — pre-result verifier freeze

## Verification question

Can every promoted P9 result be independently reproduced and falsified **without importing the original experiment scorer/terminal authority**?

This verifier is frozen before the official M1/D1/A5/A2-A4 result artifacts are read. It implements the P9 slice of programme verification #283.

## Atomic verification fibres

1. Bind exact subject commit, protocol id/version, input manifest digest and result artifact digest.
2. Reject result artifacts whose protocol version is not the latest pre-outcome amendment for that experiment.
3. Regenerate D0 hostile worlds from the frozen generator seed/counts.
4. Derive D0 gold independently from visible/semantic structural contracts rather than trusting result `target/correct` fields.
5. Recompute M1 per-task exact identifiability ceilings independently and require every view-restricted selected model to remain at/below its task ceiling.
6. Verify M1 raw prediction world identities exactly cover the protected split once per task, with no extras/duplicates.
7. Independently recompute M1 accuracy/per-family accuracy and candidate-order invariance from raw predictions.
8. Independently reproduce A5 affine-cycle classification from generated transport maps without importing `a5_explicit.predict_explicit_gluing`.
9. Independently reproduce A2 relation-selector and A4 failure-history expected outputs from generated worlds without importing the original selectors.
10. Regenerate D1 exact authored/procedural test instances from its frozen protocol and independently classify `ALIGNED/OBSTRUCTION/UNRESOLVED` from declared coordinates.
11. Check D1 whole-domain identity, protected double-corruption composition and explicit-unknown denominators.
12. Recompute D1 learned-arm metrics from raw predictions; never trust result `correct` fields.
13. Verify D1 exact comparator from an independent implementation.
14. Audit forbidden metadata/identity overlap and P10/P11 exclusion.
15. Recompute all result terminal conditions from independently recomputed metrics.
16. Produce one `ScientificResultVerification.v1` per promoted P9 claim with `VERIFIED`, `BOUNDED_VERIFIED`, `INVALIDATED`, or `CANNOT_CHECK`.
17. A verifier disagreement is retained and invalidates promotion until adjudicated; the original result is never edited to make verification pass.

## Independence boundary

Allowed imports:
- canonical serialization/hash utilities;
- frozen data object classes/generator constructors needed to reconstruct inputs;
- protocol JSON files.

Forbidden imports for independent scoring:
- original M1 metric/terminal helpers;
- original D1 experiment scorer/comparator;
- original A5 predictor;
- original A2/A4 predictors;
- original result `correct` booleans as truth.

The verifier may use raw structural inputs but must implement its own scoring logic from the written protocol.

## Verification terminal

P9 can reach peer-review readiness only if every promoted claim receives `VERIFIED` or appropriately scoped `BOUNDED_VERIFIED`, no high-severity discrepancy remains, and the final novelty certificate authorizes the exact claim independently.
