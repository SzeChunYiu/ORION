# P10 native-state incremental-value protocol V1

Status: **FROZEN BEFORE NEW OUTCOMES**

Frozen: 2026-08-20

## Scientific question

On the exact frozen P10 Mathlib subject and the existing leave-top-module-out split, does native Lean proof-state and leakage-safe proof-dependency structure add next-action predictability beyond the already-positive tactic-history baseline?

The existing V2.1 source-transfer result remains locked prior evidence and may not tune this protocol.

## Locked subject

- Mathlib commit: `e72c1e277f31441626621f7d0c7207862fc25569`
- Lean toolchain: `leanprover/lean4:v4.34.0-rc1`
- corpus: 457 files in `MATHLIB_CORPUS_V2_MANIFEST.json`
- primary split: leave one top-level Mathlib module out exactly as in V2.1

No file, module, theorem, transition, seed, threshold, or feature family may be removed after inspecting the new outcome except by a prospectively frozen failure rule.

## Native receipt contract

Every eligible transition must bind the exact theorem/source/runtime identity, pre-tactic native proof-state digest, tactic-family label, extractor/verifier command and enough trace digests to detect substitution. Source-text proxies are forbidden as native-state evidence.

The frozen state feature families are:

- goal head/operator signature;
- number of goals;
- local-context cardinality;
- anonymized multiset/count summaries of hypothesis head constructors/types;
- equality, conjunction/disjunction, implication/function, existential/universal, arithmetic/algebraic and proposition/type-class shapes when deterministically derivable;
- fixed syntax size/depth buckets.

File/module/theorem/namespace/path identity is forbidden as a predictive input.

Dependency features may use only pre-tactic, leakage-safe structural summaries. Premise names are not predictive features.

## Comparators

- B0 unigram.
- B1 exact V2.1 tactic-history Markov baseline.
- B2 state-only regularized multinomial linear classifier.
- B3 history + state.
- B4 history + state + dependency.
- B5 faithful TacMiner-class comparator when technically implementable, otherwise `CANNOT_CHECK`.

Regularization grid `{0.01,0.1,1.0,10.0}` is selected within each training fold only by nested leave-one-training-module-out log loss.

## Primary endpoint

`accuracy(B4)-accuracy(B1)` on the identical receipt-eligible transition population.

Primary success requires all of:

1. pooled difference `>0`;
2. top-module block-bootstrap 95% lower bound `>0`;
3. at least 60% of evaluable modules have non-negative B4-B1 delta;
4. B4 paired multiclass log loss lower than B1;
5. hostile controls pass.

## Hostile controls

- fixed-seed label shuffle;
- module-identity attacker;
- future-step mutation leaving pre-state features invariant;
- receipt substitution rejection;
- statement/source/runtime mutation rejection;
- near-duplicate/family leakage audit.

If fewer than 80% of V2.1 transitions are receipt-eligible, native-state promotion is `CANNOT_CHECK` unless a prospectively explainable ecosystem limitation is explicitly accepted. Runtime/corpus mismatch or unprovable split purity is `INVALID`.

## Claim ladder

- R0 existing source-level tactic-history transfer.
- R1 native state/dependency adds incremental held-out-module signal.
- R2 structural transfer survives hostile controls and module heterogeneity.
- R3 standalone novelty only after a faithful current strong-baseline comparison on the identical subject/split.

## Required artifacts

- immutable protocol digest;
- native extractor/runtime/corpus receipts;
- transition manifest;
- per-fold/per-module predictions;
- bootstrap regeneration artifact;
- hostile-control distributions;
- environment lock;
- final automatic claim-disposition receipt.

All nulls, regressions and unavailable comparator arms remain visible.