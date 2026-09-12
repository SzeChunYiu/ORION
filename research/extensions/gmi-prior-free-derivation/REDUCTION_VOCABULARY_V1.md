# Prior-free GMI: frozen architecture-reduction vocabulary v1

## Purpose

This file freezes the coordinate vocabulary used for bottom-up architecture reduction. It is written without architecture-family labels so that later recovery exercises can distinguish genuine operational recovery from a taxonomy reverse-engineered around known names.

The coordinates below are not proposed as ontological primitives. They are a finite probe chart on the operational morphology quotient of `FORMAL_CORE_V2.md`. Two implementations that differ on these coordinates may still be equivalent under a coarser probe family; two implementations that agree here may differ under finer physical probes.

---

## R0. External causal interface

Record the externally visible causal signature:

\[
\mathsf E=(\mathcal X_{in},\mathcal X_{out},\text{interaction timing},\text{feedback availability}).
\]

Categories are descriptive, not exclusive:

- one-shot map;
- finite sequence transducer;
- indefinitely recurrent stream transducer;
- environment-action loop;
- multi-party/message-passing interface;
- tool/API mediated interface;
- embodied sensor-actuator interface.

A reduction must not infer internal architecture from this coordinate alone.

---

## R1. Persistence spectrum

For every physically retained information-bearing component, record its persistence scale relative to the task clock. Use the ordered family

\[
\mathsf P=
\{P_0,P_1,\ldots,P_m\},
\]

where a larger index denotes persistence across a longer declared interval. Examples of intervals are operation, token/step, local window, episode, cross-episode, and training lifetime. The vocabulary does not prescribe those names; the study must declare the clock.

For each persistence band record:

1. capacity or asymptotic capacity law;
2. whether contents are fixed, overwritten, appended, or continuously updated;
3. whether the state is externally addressable;
4. whether persistence survives reset boundaries.

The point of this coordinate is to prevent “parameter”, “hidden state”, “memory”, and “context” from becoming primitive categories when they differ mainly by update and persistence timescale.

---

## R2. Access geometry

For each persistence band, record how information is read. Allowed descriptors are generated from the following architecture-neutral relations:

- **local ordered:** access restricted by temporal/spatial neighborhood;
- **compressed recurrent:** previous retained state is summarized into a fixed or bounded-dimensional successor state;
- **dense content-addressed:** many stored items can contribute to one read with data-dependent weights;
- **sparse content-addressed:** a selected subset of stored items is retrieved by content/key relation;
- **indexed/random-access:** explicit address or symbolic key selects storage locations;
- **topology-restricted:** reads follow edges of a declared graph/network;
- **iterative search access:** information is reached by expanding/evaluating candidate states;
- **population access:** information is represented by and selected across a set of concurrent candidates;
- **continuous-field access:** state is read through continuous dynamical evolution rather than discrete address operations.

Record fan-in/fan-out and whether access is parallelizable under the declared substrate.

---

## R3. Write/update geometry

For each mutable persistence band, record the causal update operator by observable form rather than implementation name. The basic descriptors are:

- deterministic state transition;
- stochastic state transition;
- gated/weighted overwrite;
- append-only write;
- associative/content-addressed write;
- local rule rewrite;
- constraint/proof-state rewrite;
- gradient or approximate-gradient adaptation;
- posterior/weight reallocation under an evidence rule;
- proposal-mutation-selection update;
- continuous-time differential evolution;
- externally delegated update.

Also record whether the update law itself changes on a slower timescale. A study must not assume a sharp distinction between “inference” and “learning” unless the clock making that distinction has been declared.

---

## R4. Computation and routing topology

Record the causal graph through which computation is composed within one task step or update cycle. Use the following neutral descriptors:

- acyclic layered composition;
- recurrent loop;
- parallel branch-and-merge;
- dynamic conditional routing;
- graph-local message passing;
- tree/DAG search expansion;
- centralized controller with peripheral modules;
- decentralized peer/message network;
- continuous dynamical flow;
- nested inner/outer optimization loops.

The topology record includes whether routing is fixed, input-dependent, state-dependent, learned, or externally selected.

---

## R5. Counterfactual/proposal structure

Record whether the machine explicitly constructs alternatives not identical to the executed next state. If so, record:

- proposal cardinality/scaling;
- depth/horizon of expansion;
- whether alternatives share state or are separately materialized;
- evaluation rule;
- selection/pruning rule;
- whether proposals are generated internally or obtained from an external system.

This coordinate separates ordinary causal state update from explicit planning/search without requiring a symbolic/neural distinction.

---

## R6. Composition boundary

Record channels that leave the local computational component:

- external persistent store;
- retrieval/index service;
- executable tool/API;
- verifier/solver/compiler;
- other agent/controller;
- physical environment;
- human input.

For every boundary record request/response semantics, latency, bandwidth, error model, and whether the external component's state is included in the system boundary for the claim being tested.

This prevents a nominally “small” controller from hiding most of its cognition in an uncounted external system.

---

## R7. Resource-response profile

For substrate parameter \(\theta\), record the declared resource functions

\[
\rho_\theta(n,d,\ldots)
=
(T,M,C,E,BW,\epsilon,\ldots),
\]

where coordinates may include time/latency, retained memory, communication, energy, bandwidth, error, sample use, fabrication, or other registered costs.

The reduction must distinguish:

1. asymptotic law;
2. constant/technology-dependent coefficients when empirically available;
3. parallel depth versus total work;
4. training/development cost versus run-time cost;
5. amortized versus per-query cost.

No architecture is “better” without a declared partial order or scalar objective over this vector.

---

## R8. Approximation and stochasticity contract

Record what is exact and what is approximate:

- deterministic exact;
- randomized zero-error;
- bounded worst-case error;
- average error under a declared source law;
- asymptotic convergence;
- heuristic/no certified error model.

Also record numerical precision assumptions. This coordinate is mandatory whenever two implementations are compared by an information or capability theorem; exact cut bounds cannot be transferred to average-error systems without an additional theorem.

---

## Reduction record

A bottom-up reduction of machine \(M\) must therefore have the form

\[
\Xi(M)
=
(\mathsf E,\mathsf P,\mathsf A,\mathsf W,\mathsf T,\mathsf C_f,\mathsf B,\rho,\mathsf Z),
\]

corresponding respectively to R0--R8. The symbols are only a compact record format; the semantic definitions above control.

A reduction is admissible only if every claimed coordinate can be supported by an operational or physical probe. Pure naming conventions are excluded.

---

## Equivalence tests

Two implementations are **chart-equivalent** under this frozen vocabulary when all R0--R8 records agree up to relabeling of internal states and modules. Chart-equivalence is weaker than proof of full operational equivalence and stronger than same-task behavioural equivalence.

The chart is intentionally allowed to fail. If a held-out architecture exhibits a repeatable operational distinction that cannot be represented in R0--R8, the correct result is a vocabulary counterexample and a registered extension—not forced encoding.

---

## Held-out protocol

A recovery experiment must:

1. freeze this vocabulary and its probe procedures;
2. choose held-out architecture families before inspecting their reduction;
3. derive a morphology region from ecology/resource conditions without using the held-out labels;
4. reduce the held-out implementations with the frozen chart;
5. test membership in the predicted region;
6. preserve failures and feature collisions;
7. extend the chart only in a successor registration, never retroactively for the scored run.

This protocol is the minimum safeguard against architecture-name leakage in the bottom-up half of GMI.
