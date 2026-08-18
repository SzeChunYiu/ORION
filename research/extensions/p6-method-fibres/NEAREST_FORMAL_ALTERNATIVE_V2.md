# P6 method-fibre nearest-formal-alternative note — V2

Date: 2026-08-18. Purpose: #419 comparator/ownership closure. This note is additive to the existing P6 literature/saturation record and does not create a new novelty claim.

## Primary mechanisms assimilated

### Behavioral equivalence / bisimulation

Abate, Giacobbe & Schnitzer, **Bisimulation Learning** (arXiv:2405.15723, 2024) learns candidate state partitions/ranking functions and verifies stutter-insensitive bisimulation by counterexample-guided SMT checking. P6 **ADOPTS the pressure** that a claimed abstraction/equivalence must preserve relevant transition behavior and should admit counterexamples; P6 does not claim bisimulation itself as ORION novelty.

Primary source: https://arxiv.org/abs/2405.15723

### Bisimulation-inspired state abstractions

Zhang, Sodhani, Khetarpal & Pineau, **Learning Robust State Abstractions for Hidden-Parameter Block MDPs** (arXiv:2007.07206) formalizes transferable state abstractions from shared latent dynamics. P6 **ADAPTS the pressure** that transfer/generalization requires behavior-relevant state similarity rather than labels alone.

Primary source: https://arxiv.org/abs/2007.07206

Wang et al., **Building Minimal and Reusable Causal State Abstractions for Reinforcement Learning** (arXiv:2401.12497) learns task-specific causal abstractions using dynamics/reward relations. P6 **ADOPTS the pressure** that an abstraction should retain task-relevant causal/dynamic variables rather than indiscriminately compressing state.

Primary source: https://arxiv.org/abs/2401.12497

Dadashi et al., **Offline Reinforcement Learning with Pseudometric Learning** (ICML 2021, PMLR 139) learns a pseudometric closely related to bisimulation metrics from logged transitions. P6 uses a **mechanism-matched behavioral comparator** inspired by this family, not the authors' implementation.

Primary source: https://proceedings.mlr.press/v139/dadashi21a.html

## What is not ORION novelty

The following ideas are treated as donor-owned/common formal machinery, not as standalone P6 novelty:

- behavioral/state equivalence;
- bisimulation or approximate bisimulation;
- state abstraction by transition/effect similarity;
- simulation/refinement/homomorphism-style preservation;
- ordinary graph isomorphism;
- ordinary input/output effect equivalence;
- action-model precondition/effect semantics;
- generic state machines, transition systems, partial orders or composition.

## Bounded residual tested by `P6.MethodFibreEval.v2`

The discriminator asks a narrower ORION-specific systems question: when downstream scientific use depends simultaneously on **declared claim purpose, assumptions/preconditions, protected invariants, effects, termination/progress, reconstruction to the original target, unresolved evidence, provenance/lineage and authority/footprint constraints**, does a typed claim-relative receipt prevent false fibre/substitution/composition promotion that simpler surface/effect/untyped/behavior-only reductions admit?

The V2 comparator called `behavioral_bisimulation_style` is deliberately described as **mechanism matched**, not as an official reproduction of any cited implementation. It checks preconditions/effects/termination and therefore gives the external formal family substantially more semantic information than topology/effect-only baselines, while intentionally omitting the ORION-specific reconstruction/provenance/authority obligations whose incremental value is under test.

## Claim ceiling

Even a perfect score on the closed V2 fixtures does not establish that ORION's formalism is generally superior to bisimulation, MDP-homomorphism, refinement or category-theoretic frameworks. It only establishes the bounded countermodels encoded by the frozen protocol. Any broader theorem of subsumption/equivalence remains outside #419 and would require a dedicated formal comparison.
