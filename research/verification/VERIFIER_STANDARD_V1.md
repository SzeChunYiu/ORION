# Independent verifier standard V1

**Protocol id:** `ORION.scientific-result-verification.v1`  
**Status:** DESIGN_FROZEN 2026-08-17, before confirmatory audit outcomes.  
**Issue:** #283.

This freezes the independent scorer, leakage, and denominator protocols. Changing a margin, detector threshold, or pass rule after inspecting a claim outcome requires a new protocol version. The evaluated system is not edited to make an audit pass.

## Independent scorer protocol

1. Implement metrics from the paper's written specification (metrics registry, statistical plan, gold schema, protocol JSON). Do not import original scorer internals as an oracle.
2. Hash both the original scorer/source artifact and the independent implementation.
3. Compare case-level decisions when raw records exist. Deterministic metrics must agree exactly or the disagreement is preserved in an adjudication ledger.
4. If only aggregates exist in the public tree, reconstruct what those aggregates uniquely imply and label the reconstruction assumption. That is not case-level independence.
5. Missing required raw records fail closed: the layer is `CANNOT_CHECK` or `FAIL`, never silent success.

## Leakage / shortcut protocol

Mandatory detectors, applied where the artifact surface exists:

- exact gold-label token in candidate-visible text (planted cases must fire);
- lexical/substring label predictor;
- metadata-only / case-family template predictor;
- label permutation (accuracy should collapse);
- split overlap / duplicate ids;
- hidden-field co-location (gold in the same object as visible fields);
- published protected-path / network telemetry, without claiming strace replay if the raw trace is not in-tree.

A detector hit bounds construct validity. It does not authorize deleting the case or changing the headline count.

## Denominator / statistics protocol

Independently verify:

- eligible n and unit (task/case, not repeat);
- repeats nested, not inflating n;
- CANNOT_CHECK/invalid/transport handling;
- frozen margins and decision rules;
- no post-outcome exclusions;
- no pilot/confirmatory pooling.

Planted mutations (wrong n, permuted labels, missing artifact) must make the checker fail. Wilson and paired percentile bootstrap are reimplemented from the written formulas, not imported from `publication_stats.py`.

## State machine

Allowed terminal states: `VERIFIED`, `BOUNDED_VERIFIED`, `INVALIDATED`, `CANNOT_CHECK`.

- `VERIFIED` requires present hashed raw artifacts, independent exact agreement, denominator pass, leakage pass, and an actually-run holdout/cross-host layer, with no unresolved high-severity integrity item.
- Unrun holdout or missing protected raw is `BOUNDED_VERIFIED` at best.
- The receipt `self_authorizing` is always `false`.
