# FiberGuard R13 prior-art subtraction — Pareto profiles, randomization, and active acquisition

Date: 2026-08-26

Status: current primary-source positioning, not an external novelty opinion.

| Primary source | Donor contribution relevant here | Subtraction from R13 |
|---|---|---|
| Etessami, Kwiatkowska, Vardi, Yannakakis, *Multi-Objective Model Checking of Markov Decision Processes* (2008), arXiv:0810.5728 | Multiobjective MDP feasibility, randomized/memory strategies, approximate Pareto curves. | Generic vector-policy Pareto analysis and randomized strategy requirements are donor-owned. |
| Li, Ju, Shroff, *How to Find the Exact Pareto Front for Multi-Objective MDPs?* (2024 preprint), arXiv:2410.15557 | Exact Pareto-front structure; deterministic policy vertices of a convex polytope. | Convexification of deterministic policy outcomes and exact Pareto discovery are not claimed as new. |
| Tal, Sabag, *Optimal Online Bookmaking for Any Number of Outcomes* (COLT 2025) | Explicit “Bellman-Pareto frontier” in vector repeated games. | R13 must not claim the phrase or the generic Bellman/Pareto synthesis. |
| Bazgan, Ruzika, Thielen, Vanderpooten, *The Power of the Weighted Sum Scalarization for Approximating Multiobjective Optimization Problems* (2019), arXiv:1908.01181 | Supported solutions and limits of weighted-sum approximation. | Unsupported Pareto points and weighted-sum incompleteness are donor theory. |
| Valancius, Lennon, Oliva, *Acquisition Conditioned Oracle for Nongreedy Active Feature Acquisition* (ICML 2024) | Nongreedy sequential feature acquisition balancing cost and inference/decision value. | Sequential cost-aware acquisition is not new to FiberGuard. |
| Li, Oliva, *Towards Cost Sensitive Decision Making* (AISTATS 2025) | Active-Acquisition POMDP and learned cost-sensitive acquisition policies. | POMDP/RL acquisition machinery and learned policies are donor-owned. |
| Nan, Wang, Saligrama, *Feature-Budgeted Random Forest* (ICML 2015) | Prediction-time feature acquisition under a budget. | Budgeted feature-cost prediction is prior art. |
| Demirović, Hebrard, Jean, *Blossom: an Anytime Algorithm for Computing Optimal Decision Trees* (ICML 2023) | Exact/anytime optimal decision-tree search. | Exact tree search as a generic algorithmic paradigm is donor-owned. |

## Conservative residual under review

The proposed residual is not generic Pareto or minimax theory. It is the exact combination of:

- common-oracle statewise excess-loss profiles for finite representation fibres;
- recursive exact profile generation with state-dependent acquisition cost;
- a unique minimal attainable summary for all monotone risk functionals;
- exact sparse primal/dual receipts for randomized worst-state expected loss; and
- a typed authority boundary separating expected mixtures from pathwise certificates.

No search completed in this tranche establishes that this exact combination is absent from all prior work. The correct novelty terminal is `NOVELTY_NOT_ESTABLISHED` pending specialist review.

## Reviewer search targets

A specialist review should search beyond the sources above for:

1. vector-valued dynamic programming under arbitrary monotone utility/risk functions;
2. minimal sufficient Pareto sets or antichains for all isotone scalarizations;
3. robust decision trees with mixed policies and statewise dual certificates;
4. multiobjective active feature acquisition with exact finite fibres;
5. behavioral-versus-mixed policy equivalence in adaptive acquisition trees; and
6. safety literature distinguishing expected randomization from seedwise/pathwise guarantees.
