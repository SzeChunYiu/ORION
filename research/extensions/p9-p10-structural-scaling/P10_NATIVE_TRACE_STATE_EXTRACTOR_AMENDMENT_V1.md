# P10 Native `trace_state` Extractor Amendment V1

Status: **FROZEN BEFORE NATIVE-STATE OUTCOMES**

Frozen: 2026-08-20

This amendment implements the already-frozen `P10_NATIVE_STATE_INCREMENTAL_VALUE_PROTOCOL_V1.md`. It does not change the B1–B4 scientific endpoint or success thresholds.

## Native-state acquisition

For each file in the exact 457-file P10 manifest at Mathlib commit `e72c1e277f31441626621f7d0c7207862fc25569` and Lean toolchain `leanprover/lean4:v4.34.0-rc1`:

1. verify original source bytes against the frozen corpus manifest;
2. identify exactly the same V2.1 collapsed coarse tactic-family actions with the frozen source projector;
3. transiently insert, immediately before the first source line of each collapsed action, a unique no-op logging tactic followed by Lean's native `trace_state` tactic;
4. run `lake env lean <exact-path>` inside the exact Mathlib checkout;
5. restore the original source bytes regardless of execution outcome;
6. parse only states immediately following an `ORION_P10_STATE::<transition-id>` marker.

The logging tactic is defined locally in the transient source using Lean's elaborator/logging API and has no instances, simp lemmas, tactics affecting goals, or domain declarations. `trace_state` and the marker are observational only. Original uninstrumented source digests remain the scientific source identity.

A transition row at action position `j >= 1` binds:

- previous collapsed action family `H_{j-1}`;
- true current/next action family `Y_j`;
- native proof state immediately before `Y_j`;
- exact source/theorem/action position identity;
- source SHA-256, Mathlib revision, Lean toolchain, extractor revision and trace-state SHA-256.

If the instrumented file fails while the restored original succeeds, transitions from that file are ineligible with reason `INSTRUMENTATION_UNSUPPORTED`; they are never silently converted to source proxies.

## Native state features

Predictive features are derived only from the emitted native `trace_state` text. Raw text, names, paths, theorem names and namespace identifiers are never model features.

Frozen state features:

- number of goals;
- local-context declaration count;
- goal-head shape category: equality, iff, conjunction, disjunction, implication/function, forall, exists, order/comparison, arithmetic/algebraic, proposition/type/sort, or other;
- histogram of the same anonymized shape categories across local-context types;
- Boolean shape flags for equality, conjunction/disjunction, implication/function, quantification, arithmetic/algebraic and proposition/type-class-looking forms;
- native-state token-count bucket `{0-31,32-63,64-127,128-255,256-511,512+}`;
- maximum visible bracket-nesting bucket `{0-2,3-5,6-9,10+}`.

## Leakage-safe dependency features

Local names are used transiently only to count structural references and are discarded before fitting. Frozen B4-only dependency features are:

- number of context-to-context reference edges;
- number of context variables referenced in the goal;
- maximum context-reference indegree;
- fraction of context declarations with at least one reference to another local;
- normalized state-digest duplicate-group size bucket.

Premise, theorem, namespace, file and module names are not predictive features.

## Exact-state near-duplicate hostile analysis

Primary rows are retained exactly as required by the parent protocol. Additionally, normalize each native state by replacing identifier-like tokens with `<ID>` while retaining logical/operator punctuation and hash the result.

Run a secondary strict analysis after removing every held-out transition whose normalized-state digest also appears in its training-module population. Hostile near-duplicate control passes only if B4-B1 accuracy on this strict population is non-negative. This secondary filter does not alter the primary endpoint.

## Identity/future-step hostile controls

The implementation must automatically verify:

- **future-step mutation:** changing only `true_action` in a copied row leaves all state/dependency feature bytes unchanged;
- **receipt substitution:** swapping state/receipt material across transition IDs fails a transition receipt verifier;
- **source mutation:** changing one source digest fails verification;
- **runtime mutation:** changing the Mathlib commit or Lean toolchain fails verification;
- **forbidden-feature scan:** serialized predictive vectors contain no source path, theorem name, namespace, top-module string or trace text.

All must pass.

## Module-identity attacker

The attacker is a leakage detector rather than a domain-invariance claim. Fit a multinomial linear model to **forbidden identity material only** after the extractor's predictive-vector serialization. Because no such material is permitted, the attacker input must be empty and the check passes only when the feature serializer proves that zero forbidden identity fields enter B2/B3/B4. Natural module predictability from legitimate structural state is reported separately and is not called identity leakage.

## Label shuffle

Within every outer training fold, apply frozen seed `914033` to permute training action labels and refit B4 at the selected regularization. Report shuffled held-out accuracy. The hostile control passes when pooled shuffled accuracy does not exceed the corresponding held-out unigram accuracy by more than `0.02` absolute. The shuffle result cannot rescue or tune the primary model.

## Model fitting

Frozen models and regularization remain exactly as in the parent protocol:

- B1 history Markov;
- B2 state-only multinomial L2 logistic regression;
- B3 history + state;
- B4 history + state + dependency;
- `C in {0.01,0.1,1.0,10.0}`.

For every leave-top-module-out outer fold, each B2/B3/B4 C is selected using only the outer training modules by nested leave-one-training-module-out multiclass log loss. Ties select the smaller C. No held-out-module outcome participates in selection.

## Eligibility gate

Eligibility coverage denominator is the exact V2.1 leave-top-module transition population, 11,842 transitions. Coverage must be at least 80%. Below that, terminal is `CANNOT_CHECK_NATIVE_STATE_COVERAGE` regardless of observed model accuracy.

## Final positive terminal

Unchanged primary conditions plus these explicit hostile controls are required for `P10_NATIVE_STATE_INCREMENTAL_VALUE_SUPPORTED`:

- B4-B1 pooled accuracy > 0;
- module-block bootstrap 95% lower bound > 0;
- >=60% evaluable modules non-negative;
- B4 log loss < B1 log loss;
- eligibility >=80%;
- label-shuffle, identity, future-step, receipt/source/runtime substitution and exact-state near-duplicate controls all pass.

B5 TacMiner-class comparison remains separately required for standalone tactic-mining novelty and cannot be inferred from this experiment.
