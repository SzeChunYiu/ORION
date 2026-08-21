# QG-3 hostile novelty-threat freeze — 2026-08-21

Status: **FROZEN BEFORE QG-3 OUTCOME**
Programme: ORION #740 / child #745
Search cutoff: 2026-08-21

## Candidate novelty object

Not TARE itself, not block encoding, not compiler optimization, and not resource prediction.

Candidate object under hostile review:

> **Compilation regime geometry** — exact characterization of a structured quantum-compilation family by (i) donor-optimal region, (ii) finite elementary trade basis with minimal witnesses, (iii) sufficiency/closure bound, (iv) decidable structural membership predicate not requiring full optimization, and (v) prospective exact cost/regime forecasts.

The current ORION-Q R6 instance additionally carries a machine-checked all-n support bound inside the frozen grammar.

## Strong parents searched and absorbed

### Compiler/device prediction

**MQT Predictor — Quetschlich, Burgholzer, Wille, ACM TQC 2025.**
Automatically predicts a suitable device and learns device-specific compilation flows across compiler passes. Strong parent for *selection/prediction of a good compiler/device*. It does not, in the searched paper, provide an exact family-optimal region, finite trade basis, family-closure theorem, or exact structural membership predicate for a compilation grammar.

DOI: 10.1145/3673241.

### Quantum compiler optimization and comparisons

Current compilation papers and surveys optimize circuits, routing, placement, gate/depth/fidelity objectives, or compare compiler representations/strategies. Examples searched include 2025 phase-polynomial-vs-DAG compiler comparisons and 2025–2026 mapping/routing surveys/optimization papers. These own compiler optimization/comparison, not the exact regime-geometry object above.

### T-complexity / structural cost models

**The T-Complexity Costs of Error Correction for Control Flow in Quantum Computation** (POPL 2024) provides a program-level T-cost model plus rewrites that recover asymptotic efficiency. Strong parent for analytic cost models and structural compiler optimization. It does not map an optimization family into exact donor/trade regimes with an induced membership predicate.

### Sparsity-dependent optimal bounds

**Li et al., Optimal T Counts under Sparsity: from QROM to State Preparation and Block Encoding, arXiv:2607.28260 (2026).**
Provides asymptotically optimal T-count bounds as functions of sparsity/support. Strong parent for structural resource bounds and support-dependent optimality. It does not appear to provide a finite empirical/algebraic trade basis with exact regime membership and prospective family forecast of the ORION-Q type.

### Lower bounds / mapping bounds

Lightcone bounds and other mapping lower-bound work provide provable minimal-overhead constraints for specific mapping problems. These are parents for lower bounds and certified overhead estimates, not family-regime decomposition.

### Automated compiler/search systems

Automated circuit/compiler synthesis, MQT-style pass search, AutoQuREO/full-stack resource optimization, RL/evolutionary compiler design and related systems are absorbed as optimization/search parents. A regime map must add explanatory/decidable structure beyond repeatedly invoking the optimizer.

## Current threat conclusion

`NO_CLOSE_PARENT_FOUND_FOR_EXACT_COMPILATION_FAMILY_REGIME_GEOMETRY_AS_DEFINED__NOVELTY_NOT_AUTHORIZED`

This means only that the search did not reveal a close parent owning the *combined* object at the cutoff. It is not a novelty certificate.

## Reopen triggers

Reopen immediately if a donor is found that supplies, for the same or a closely analogous quantum-compilation family:

- a complete finite set of elementary optimization trades;
- an exact family-closure/sufficiency theorem;
- a direct structural predicate classifying which restricted family attains the unrestricted optimum;
- prospective exact regime/cost prediction without re-running the full optimizer;
- or an equivalent formal object under different terminology (phase diagram, normal-form regions, optimizer active-set geometry, parametric compilation partition, etc.).

A single compiler predictor, resource estimator, or family-specific optimizer is not by itself equivalent.

## QG-3 claim ceiling

Even if QG-3 is positive, the allowed statement is only that the existing R6Q structural predictor prospectively located and exactly forecast one donor-suboptimal matching under the frozen grammar. The broader regime-geometry novelty claim remains `CANNOT_CHECK_EXTERNAL_NOVELTY_AUTHORITY` until independent literature/peer review.
