# P10 Invariant State and Proof-Search Protocol V1

Status: **FROZEN BEFORE NEW OUTCOMES**
Frozen: 2026-08-20

## Dependency

This protocol is downstream of `P10_NATIVE_STATE_INCREMENTAL_VALUE_PROTOCOL_V1.md`. It cannot promote a state/mechanism claim unless that protocol first earns native-state incremental value.

## Questions

1. Does a leakage-safe native representation expose proof-action information beyond tactic history?
2. Is that information approximately invariant across held-out Mathlib top-level modules?
3. Does the representation improve verifier-backed proof search under matched budgets?

## Variables

- `H`: preregistered coarse tactic history.
- `S`: native pre-tactic Lean proof-state features.
- `G`: leakage-safe dependency features available before the action.
- `D`: top-level Mathlib module/domain.
- `Y`: next tactic-family action.
- `Z=g(S,G)`: frozen structural representation.

Direct theorem/module/file/namespace identity is forbidden as a predictive input.

## Stage 1 — predictive information decomposition

Fit the already-frozen simple comparators on identical receipt-eligible transitions:

- B0: unigram.
- B1: history.
- B2: state.
- B3: history+state.
- B4: history+state+dependency.

Use held-out log-loss reductions as the primary operational evidence for incremental predictive information:

- `J_H = LL(B0)-LL(B1)`;
- `J_S|H = LL(B1)-LL(B3)`;
- `J_G|HS = LL(B3)-LL(B4)`.

These are predictive information scores, not claims of exact mutual information. If a variational information interpretation is used, state assumptions and estimator class explicitly.

## Stage 2 — module invariance

Evaluate whether `Z` yields stable conditional behavior across held-out modules.

Report:

1. per-module log loss and accuracy;
2. worst-module risk;
3. variance of calibrated residuals across modules;
4. module-adversary accuracy from `Z` relative to majority and nuisance-matched baselines;
5. conditional action residual by module after controlling for `Z`;
6. leave-module-out calibration transfer.

### Invariance success gate

A bounded `MODULE_INVARIANT_COORDINATES_SUPPORTED` terminal requires:

- native-state incremental protocol already passes;
- positive B4-B1 primary result;
- worst-module performance not catastrophically below B1 by a preregistered tolerance;
- module adversary cannot explain the predictive gain through direct identity leakage;
- calibration and residual heterogeneity pass frozen thresholds;
- near-duplicate/family audit is green.

Use `APPROXIMATE` language. No causal invariance claim is permitted from observational module shifts alone.

## Stage 3 — semantic-orbit robustness

Create semantics-preserving transformations where Lean equivalence can be checked or transformation validity can be proven:

- alpha-renaming of local hypotheses;
- benign local ordering changes where Lean semantics are unchanged;
- equivalent syntactic forms admitted by frozen transformation rules;
- dependency-name anonymization preserving graph structure.

Measure prediction variance and search utility across each semantic orbit. A structural representation should ideally reduce surface-form variance.

Any transformation that changes elaboration, available instances, simplifier behavior, or proof semantics is not a valid orbit member.

## Stage 4 — verifier-backed proof search

Only after stages 1-2 are frozen, embed the scorer into a common search engine.

### Search arms

- S0: history-only B1 scorer.
- S1: native state B3 scorer.
- S2: native state+dependency B4 scorer.
- S3: faithful nearest-work/TacMiner-class or stronger available comparator when technically compatible.

All arms share:

- theorem manifest;
- Lean revision/toolchain;
- tactic/action vocabulary;
- search algorithm;
- max branching policy;
- stopping rules;
- verifier;
- timeout accounting.

Only the scorer differs for S0-S2.

### Primary search endpoint

Verified theorem solve rate under a fixed maximum number of Lean verifier calls.

### Secondary endpoints

- nodes expanded;
- Lean calls per solved theorem;
- wall time;
- proof length;
- top-k proposal recall;
- invalid tactic rate;
- timeout rate;
- search-depth distribution;
- failure categories.

### Search success gate

`STATE_GUIDED_SEARCH_UTILITY_SUPPORTED` requires:

1. S2 solve rate > S0 on the preregistered theorem set;
2. block-bootstrap lower 95% bound >0 or another frozen paired interval excluding 0;
3. no higher verifier-call budget for S2;
4. no hidden retrieval or theorem-identity information unique to S2;
5. gain survives module/family stratification sufficiently to rule out one-module domination;
6. exact proof receipts validate under frozen Lean.

If one-step prediction improves but search does not, retain the predictive result and record search utility as null.

## Stage 5 — strong-baseline gate

Before standalone novelty claim, refresh closest work and implement a faithful comparator when licensing/runtime permit. At minimum assess LeanDojo/ReProver-style state/premise learning, TacMiner-style tactic-dependence structure, and current verifier-grounded agentic Lean systems.

If an exact faithful comparator cannot be executed, use `CANNOT_CHECK_STRONG_BASELINE`; do not replace it with a deliberately weak proxy.

## Claim ladder

- `R0`: existing V2.1 coarse tactic-history transfer.
- `R1`: native proof-state/dependency incremental information.
- `R2`: approximately module-invariant structural coordinates.
- `R3`: semantic-orbit robustness.
- `R4`: verifier-backed search utility under matched calls.
- `R5`: standalone novelty survives strong current baselines.

## Required receipts

- subject/corpus/toolchain digests;
- native-state receipts;
- transition manifest;
- per-fold predictions;
- module-adversary outputs;
- semantic-orbit manifests;
- search tree/proposal logs or content-addressed equivalents;
- verifier-call accounting;
- all generated Lean proof receipts;
- comparator version/configuration;
- final claim-disposition receipt.
