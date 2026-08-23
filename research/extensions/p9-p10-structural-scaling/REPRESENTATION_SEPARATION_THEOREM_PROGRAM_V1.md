# Representation Separation Theorem Program V1

Status: **THEORY PROGRAM — NO THEOREM CLAIMED**
Frozen: 2026-08-20

## Objective

Build an exact controlled family in which two encodings are information-equivalent but have provably different complexity for a restricted learner/computation class. Then test whether empirical LLM scaling tracks the proved separation.

## Core setup

Let latent state be `x=(pi,z,c)` where `pi` is a hidden permutation/binding map, `z` are local typed values, and `c` is a compositional query. Let target `y=T(x)` be exact.

Construct two deterministic bijective encodings:

- `E_struct(x)`: binding map and typed coordinates are directly addressable.
- `E_flat(x)`: same atoms are serialized under a reversible permutation/indirection convention, so no information is lost.

Require an explicit polynomial-time inverse between encodings so that information equivalence is mechanically checkable.

## Candidate theorem families

### T1. Linear separability gap

Choose a task where `y` is linearly separable under `E_struct`, while `E_flat` requires interaction terms of order at least `k` under a specified feature map. Prove the statement for the exact generator distribution and feature class, not by empirical observation.

### T2. Decision-tree depth gap

Construct a parity/binding/composition family where a bounded-depth tree can solve `E_struct` with depth `O(log n)` or constant depth, while any deterministic tree for `E_flat` requires depth `Omega(n)` under a stated distribution or worst-case decision-tree model.

### T3. Finite-state memory gap

For sequential tasks, expose a predictive sufficient state in `E_struct`; force `E_flat` to reconstruct it from a longer history. Establish a lower bound on states/memory for the flat streaming recognizer and an upper bound for the structured recognizer.

### T4. Sample-complexity gap for a frozen hypothesis class

Show that the structured representation belongs to a lower-complexity subclass (VC/Rademacher or exact finite-class counting where tractable), yielding a tighter sample-complexity upper bound, while flat representation requires a richer class to represent the same target.

Only one rigorous theorem is necessary for the first paper; additional families are replication/generalization.

## Non-negotiable conditions

1. Same latent task distribution.
2. Encodings are bijectively related or share a mechanically verified canonical fact set.
3. No target information is added by the structured encoding.
4. Lower bound states the exact computation/hypothesis class and does not generalize to arbitrary neural networks without proof.
5. Empirical LLM results are presented as correspondence with the controlled separation, not as proof that transformers obey the lower bound.

## Preferred first target

Prioritize the finite-state / bounded-memory construction because it links directly to P9 history compression and P10 proof-state-as-predictive-state hypotheses.

Let a latent automaton state `s_t` summarize all task-relevant history. Structured representation supplies `s_t` explicitly; flat representation supplies a reversible event history from which `s_t` can be reconstructed.

Aim to establish:

- structured predictor requires `O(|S|)` state and one-step access;
- a deliberately obfuscated but reversible flat encoding requires a larger memory/state complexity under the frozen streaming interface;
- both encodings decode to the identical event sequence and target.

Do not choose an obfuscation so artificial that the theorem has no correspondence to actual P9 flattening. Include a naturalistic canonical serialization arm between native transcript and adversarial construction.

## Bridge to LLM experiment

For each theorem family, generate difficulty parameter `n`. Fit empirical scaling curves for R1 same-info flat versus R2 structured and measure:

- accuracy versus `n`;
- model scale needed for fixed quality;
- inference tokens needed for fixed quality;
- semantic-orbit robustness under symbol/order transformations.

A compelling correspondence is a growing structured-flat gap with `n` in the regime where the theoretical restricted-class gap also grows.

## Proof discipline

Any theorem manuscript artifact must include:

- formal definitions;
- assumptions;
- exact proposition/theorem statement;
- proof or machine-checked proof when feasible;
- counterexamples showing why assumptions matter;
- no extrapolation from restricted class to all LLMs.

## Strongest eventual claim

If both theorem and experiments succeed:

> Information-equivalent representations can have provably different accessibility for bounded computation, and modern language-model scaling empirically reflects the same direction of separation on matched controlled tasks.

This claim remains forbidden until both halves are complete.
