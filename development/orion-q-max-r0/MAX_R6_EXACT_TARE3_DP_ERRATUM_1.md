# MAX-R6 exact TARE-3 joint DP erratum 1

Date: 2026-08-20
Applies before any exact-joint-DP outcome.

Two implementation-only clarifications are frozen.

## E1 — deterministic tie rule

Scientific authority depends on the exact minimum `C_joint` and a valid proof-carrying witness, not on which of several equal-cost local DP paths is called lexicographically first.

The solver therefore:

1. computes the exact minimum cost;
2. selects the smallest final `(target_permutation, central_axis, final_parity_state)` among equal minima;
3. reconstructs a deterministic equal-cost predecessor by ascending local option code and then ascending predecessor-state index;
4. hashes the resulting witness.

Independent replay must reproduce the minimum cost exactly and must validate its own optimal witness; identical witness hashes are required only when the independent replay implements the same tie rule.

## E2 — open-subject expensive-verifier panel

The candidate-blind rank-2 scan still examines every eligible non-direct triple. The expensive 1024-state all-frame DP is applied to the deterministic **top four** rank-2 improvements per subject rather than top eight.

This changes no search variable, comparator, threshold, or fresh-subject rule. It only bounds the constant factor of the exact verifier while retaining multiple independent chemistry triples on both open subjects.
