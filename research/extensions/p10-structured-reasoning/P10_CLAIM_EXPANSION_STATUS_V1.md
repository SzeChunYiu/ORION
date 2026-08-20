# P10 claim-expansion execution status V1

Status date: 2026-08-20

## Earned now

The existing P10 V2.1 source-projection result remains the strongest completed positive experiment:

- 457 selected Mathlib files across 31 active top-level modules;
- 4,825 recognized theorem/lemma trajectories;
- 16,667 projected tactic-family actions;
- leave-top-module-out Markov accuracy `0.3842` versus pooled unigram `0.2796`;
- absolute difference `+0.1046`;
- module bootstrap 95% interval approximately `[0.0863, 0.1223]`;
- bigram/trigram coverage `0.9959` / `0.9450`;
- observed cross-module macro counts in the significant lower tail under every frozen seed and both frozen null families;
- native eight-file audit and mutation/identity controls already pass within their stated scope.

The new module-robustness analysis is derived from the already-frozen 31 block receipts. It may strengthen the breadth/sensitivity description of this source-transfer result but cannot create a proof-state or prover-success claim.

## Frozen but not yet earned

`P10_NATIVE_STATE_INCREMENTAL_VALUE_PROTOCOL_V1.md` freezes the next mechanism experiment:

- B1 exact tactic-history comparator;
- B2 native state only;
- B3 history + native state;
- B4 history + native state + leakage-safe dependency summaries;
- B5 faithful TacMiner-class comparator when implementable;
- primary B4-B1 held-out-module endpoint;
- block-bootstrap, module breadth, log-loss, leakage and mutation gates.

No R1/R2/R3 native-state result is claimed until those executions exist.

## Publication strategy

P10 should expose the strongest completed positive source-transfer result and its robustness analysis as a bounded formal-mathematics evaluation paper/note. Native-state, invariant-state and verifier-backed search extensions remain a clearly separated prospective escalation until exact executions clear their frozen gates.

No null or unavailable extension may be relabeled as support for the stronger claim.
