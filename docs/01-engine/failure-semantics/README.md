# Failure semantics

ORION treats failure as knowledge, but it does not equate an observed failure with its cause.

A failure plan separates at least:

```text
failure mode / observed abnormal behavior
-> propagated effects
-> competing cause hypotheses
-> detection signals + rule
-> recovery / compensating actions
-> falsifier
-> acceptance rationale
```

This follows a transferable pattern from reliability engineering and model-based diagnosis: bottom-up failure-mode/effect analysis and top-down causal diagnosis answer different questions. Repeated output mismatch is evidence that a mode recurs; it does not prove which component, assumption or method caused the mismatch.

## V0 universal baseline

Before step-specific hazard analysis, every mechanic receives six fail-closed baseline modes:

1. contract/invariant/interface violation -> `FAILED`;
2. mandatory prerequisite unavailable -> `BLOCKED`;
3. required observation/verifier unavailable -> `CANNOT_CHECK`;
4. resource bound reached while obligations remain open -> `CANNOT_CHECK`;
5. local/surrogate improvement without root-relevant progress -> `PARTIAL` / false progress;
6. independent expectation rejects an apparently successful result -> `FAILED` / silent degradation.

The baseline answers the structural question "what failure language and fail-closed outcomes does this mechanic support?" It does not claim to enumerate the mechanic's real domain-specific failure modes. Every cell retains an explicit empirical-open coordinate for step-specific failure-mode/effect/cause/detectability analysis and hostile validation.

## Failure as experience

Actual runtime outcomes are recorded separately as immutable episodes. Cross-variation recurrence may propose a `FailurePatternCandidate`; replay, fresh transfer and protected verification are still required before a guard becomes conditionally reusable. Failure plans therefore define the language of possible/observed failure, while experience supplies evidence about which modes actually occur and whether a repair generalizes.
