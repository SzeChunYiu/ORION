# Prior-free GMI: known-form reduction v1

## Status

This is a bottom-up stress test of the frozen `REDUCTION_VOCABULARY_V1.md`. The vocabulary was committed before this mapping. The purpose is not to claim that known architectures have been prospectively derived. It is to test whether materially different machine-intelligence families require a primitive absent from the architecture-neutral chart.

The unit of analysis is an architecture **family**, not a product/model name. Resource statements below describe standard dense/reference realizations and are not universal lower bounds unless explicitly stated.

---

## 1. Feed-forward function approximators

**R1 persistence.** Training-lifetime parameter state; no required run-time recurrent state beyond activations.

**R2 access.** Layer-local access to preceding activations; convolutional variants impose local/shared spatial access.

**R3 update.** Run time: acyclic deterministic/stochastic transition through activations. Development: parameter update under an external training process.

**R4 topology.** Acyclic layered composition, optionally with skip/branch structure.

**R5 counterfactuals.** None required by the family.

**Conclusion.** Fits the chart. “Neural” is not a new primitive; the operational distinction is the acyclic compute graph plus persistence/resource profile.

---

## 2. Recurrent networks, gated recurrent networks, and reservoir systems

**R1.** Training-lifetime parameters plus step-to-step retained state.

**R2.** Compressed recurrent access: the history influences the future through a bounded or declared-dimensional recurrent state.

**R3.** Deterministic/stochastic recurrent transition; gated variants implement weighted overwrite. Reservoir families may fix the recurrent core and train only the readout.

**R4.** Recurrent loop with sequential dependency.

**R7.** Standard inference work grows linearly with sequence length for fixed state/update width; parallel depth generally retains a sequential dependency unless algebraic structure permits scan-style parallelization.

**Conclusion.** Fits the chart. The essential reduction is persistent compressed recurrence, not the gate names.

---

## 3. Dense self-attention sequence models

**R1.** Training-lifetime parameters plus a transient sequence/context store; autoregressive implementations commonly retain a key/value cache.

**R2.** Dense content-addressed read: a query can weight many retained positions.

**R3.** Context is appended/constructed during the run; persistent parameters are normally fixed at inference in the basic family.

**R4.** Parallel branch-and-merge inside a layer with data-dependent routing weights.

**R7.** Standard full attention has quadratic pairwise interaction work/memory in context length if all pair scores are materialized; implementation details can change constants and storage strategies.

**Conclusion.** Fits R1--R8. “Attention” reduces to a particular access geometry and resource response.

---

## 4. Linear/sparse attention and retention-style sequence models

**R1.** Persistent parameters plus transient/recurrent summaries or sparsified context structures.

**R2.** Content-dependent access constrained by a kernel factorization, sparse pattern, recurrence, or retention summary rather than unrestricted dense pairwise access.

**R3.** Append/update of compressed statistics or sparse memory.

**R4.** Hybrid parallel/recurrent topology is common.

**R7.** The family exists precisely because access/resource scaling differs from standard dense attention; exact scaling is implementation specific.

**Conclusion.** No new primitive. These models occupy different points in access-geometry/resource space.

---

## 5. Structured state-space sequence models

**R1.** Training-lifetime parameters plus recurrent latent state.

**R2.** Compressed recurrent access; structured kernels may admit parallel training/evaluation transformations.

**R3.** State transition with input-dependent or fixed dynamics; selective variants make transition/read parameters data dependent.

**R4.** Recurrent dynamical topology with possible parallel scan/convolutional realization.

**R7.** Standard motivation is linear-in-sequence recurrent execution with a fixed-size state, trading exact token-addressable context for compressed dynamics.

**Conclusion.** Fits the same chart as recurrent systems but differs in transition structure, parallelizability, and resource response. The distinction is physical/operational, not a new logical primitive.

---

## 6. Test-time-learning and neural long-term-memory sequence models

This family includes systems whose run-time retained state is itself a parameterized learner and systems combining transient attention with a slower adaptive memory.

**R1.** Multiple persistence bands: transient context, within-run adaptive memory, and training-lifetime parameters.

**R2.** May combine dense/local context access with reads from an adapted parametric memory.

**R3.** Gradient or approximate-gradient update occurs inside the forward/inference process; a slower outer training process updates the update rule and/or initial parameters.

**R4.** Nested inner/outer loops.

**Key reduction result.** The family is exactly why “state update”, “learning”, and “morphology change” cannot be primitive categories without a declared clock. Under R1/R3, the apparent novelty is a new persistence/update timescale composition.

**Conclusion.** Fits the chart and supports the v2 decision to treat inference/learning separation as gauge-like until timescale is declared.

---

## 7. External differentiable memory systems

**R1.** Controller state plus a separately retained read/write memory.

**R2.** Indexed or content-addressed random access.

**R3.** Explicit read/write/erase/add operations, often differentiable.

**R4.** Central controller with memory peripheral.

**R6.** If the memory is external to the controller boundary, its bandwidth/latency/state must be counted as a composition boundary.

**Conclusion.** Fits the chart. “Memory-augmented” is a composition of persistence and access coordinates.

---

## 8. Retrieval-augmented systems

**R1.** Local controller/context plus a persistent corpus/index whose lifetime can exceed the model run.

**R2.** Sparse content-addressed or indexed access.

**R3.** Retrieval store may be fixed, appended, or separately maintained.

**R6.** Explicit external retrieval boundary with query/response bandwidth, latency, error and index-update costs.

**Conclusion.** Fits the chart. Any comparison that counts the controller but not the retrieval substrate violates R6.

---

## 9. Associative-memory and energy-based systems

**R1.** Persistent parameters/memory templates plus an iterative candidate state.

**R2.** Associative/content-dependent access through an energy or similarity landscape.

**R3.** Iterative state refinement or settling.

**R4.** Recurrent/continuous dynamical loop.

**R8.** Convergence can be exact in restricted models or heuristic/approximate in richer systems.

**Conclusion.** Fits the chart as iterative dynamics over a persistent energy/memory structure.

---

## 10. Graph neural/message-passing systems

**R1.** Node/edge state plus learned parameters.

**R2.** Topology-restricted neighborhood access.

**R3.** Local message aggregation and state update.

**R4.** Graph-local parallel message passing, possibly recurrent across rounds.

**R7.** Resource use depends on graph size, edge count, message dimension and number of rounds.

**Conclusion.** Fits the chart. Graph structure enters as an access/routing topology rather than a separate intelligence primitive.

---

## 11. Symbolic production systems and theorem provers

**R1.** Persistent rule/axiom store plus current symbolic state/proof state.

**R2.** Indexed/random symbolic access and constraint-dependent lookup.

**R3.** Rule rewrite, unification, constraint propagation, or proof-state transition.

**R4.** Often dynamic branch/search composition.

**R5.** Explicit alternatives are common: candidate rules, subgoals, proof branches.

**Conclusion.** Fits the chart. Symbolic representation changes the state and update encoding, not the causal primitives.

---

## 12. Bayesian filters, probabilistic programs, and belief-state systems

**R1.** Persistent model/hypothesis structure plus a belief/sufficient-statistic state.

**R2.** Access through model factorization, hypothesis enumeration, particles, messages, or sufficient statistics.

**R3.** Evidence-driven weight/posterior update or approximate inference transition.

**R4.** Factor-graph message passing, sequential filtering, sampling, or nested inference depending on realization.

**R8.** Exact and approximate inference must be distinguished.

**Conclusion.** Bayesian form is an update/representation realization, not a prerequisite of the prior-free ecology order.

---

## 13. Program induction, synthesis, MDL and universal-search families

**R1.** Candidate-program/hypothesis state plus search bookkeeping; optional persistent learned proposal model.

**R2.** Indexed candidate access and/or generated candidate enumeration.

**R3.** Proposal, execution/evaluation, scoring, pruning and reweighting.

**R4.** Search tree/DAG or population-like topology.

**R5.** Counterfactual proposal structure is central.

**R7.** Search cost is determined by description space, proposal order, evaluator cost, pruning and compute budget; universal asymptotic dominance claims do not imply practical resource equivalence.

**Conclusion.** Fits R1--R8. Algorithmic priors are one candidate weighting rule within this morphology, not a primitive of GMI.

---

## 14. Planning, tree search, and model-predictive control

**R1.** Current state/belief plus temporary or retained search tree/value statistics.

**R2.** Iterative access to candidate future states.

**R3.** Expand, evaluate, back up, prune/select.

**R4.** Tree/DAG search, often nested inside an environment-action loop.

**R5.** Explicit counterfactual generation is defining.

**Conclusion.** Fits the chart. Planning is a proposal/counterfactual topology, not synonymous with symbolic representation.

---

## 15. Model-free reinforcement learners

**R1.** Policy/value parameters and optional recurrent/episodic state.

**R2.** Determined by the chosen function/memory representation.

**R3.** Experience-driven value/policy update; run-time action selection may be fixed between updates or online.

**R4.** Environment-action feedback loop.

**R5.** Explicit planning is not required.

**Conclusion.** Fits the chart; “reinforcement learning” specifies an update/evaluation regime more than one morphology.

---

## 16. World-model and model-based reinforcement systems

**R1.** Learned predictive model plus policy/controller state and often a planning workspace.

**R2.** Predictive-state/model access, possibly recurrent or attention-based.

**R3.** Model learning plus policy/value learning; planning may update transient search state.

**R5.** Counterfactual rollouts are common and operationally distinguish this family from purely reactive policies.

**Conclusion.** Composition of predictor, planner and controller fits the chart without a new primitive.

---

## 17. Evolutionary algorithms, genetic programming, population-based search

**R1.** Population state across generations plus evaluator/archive state.

**R2.** Population access and selection.

**R3.** Proposal/mutation/recombination/selection update.

**R4.** Population-parallel outer loop.

**R5.** Multiple explicit alternatives are intrinsic.

**Conclusion.** Fits the chart; the population is a persistence/proposal geometry rather than a special intelligence atom.

---

## 18. Spiking, neuromorphic, reservoir-dynamical, and continuous-time systems

**R1.** Physical dynamical state at one or more decay/persistence scales.

**R2.** Topology-restricted or continuous-field access through physical coupling.

**R3.** Event-driven or differential state evolution; learning can be local, global, online, or absent.

**R4.** Continuous/recurrent physical network.

**R7.** Energy/latency/communication coefficients can differ radically from digital matrix implementations and therefore belong in \(\theta\) and \(\rho\), not in a universal architecture ranking.

**Conclusion.** Fits the operational chart. Exact analog/noncomputable idealizations may fall outside the effective-simulation theorem while remaining inside the broader causal morphology language.

---

## 19. Neural ODEs and continuous-depth computation

**R1.** Continuous latent state plus persistent parameters.

**R2/R3.** Continuous-field/differential evolution.

**R4.** Continuous dynamical flow rather than a fixed discrete layer count.

**R8.** Actual digital realizations introduce numerical-solver error/tolerance and adaptive compute.

**Conclusion.** Fits the chart and demonstrates why numerical approximation contracts must be explicit.

---

## 20. Diffusion and iterative generative/refinement systems

**R1.** Persistent model parameters plus an evolving candidate sample/state.

**R2.** Current-state/local conditioning and optional external context access.

**R3.** Stochastic or deterministic iterative refinement across a declared schedule.

**R4.** Recurrent refinement loop, often with fixed number or tolerance-controlled steps.

**R5.** Multiple stochastic alternatives can be sampled, but explicit search is not required.

**Conclusion.** Fits the chart as iterative stochastic transition with a characteristic resource/error schedule.

---

## 21. Mixture-of-experts and dynamically modular systems

**R1.** Multiple persistent expert parameter stores plus routing state.

**R2.** Sparse selected access to modules.

**R3.** Standard expert transitions plus router update during development/training.

**R4.** Dynamic conditional routing and parallel branch/merge.

**R7.** Total stored parameters and activated-per-input work become separate resource coordinates.

**Conclusion.** Fits the chart. Modularity is routing/access structure, not a new semantic primitive.

---

## 22. Neuro-symbolic hybrids

**R1--R5.** Union/composition of learned continuous/subsymbolic state transitions with explicit symbolic stores, constraints, programs, proof/search states or solvers.

**R6.** The boundary between modules is operationally relevant when it carries latency, bandwidth, verification or external-solver costs.

**Conclusion.** Fits by composition. The hybrid label describes which representation/update modules are coupled, not a new causal category. Recent survey taxonomies likewise describe sequential, parallel, differentiable and unified integration patterns, all expressible in R3/R4/R6.

---

## 23. Tool-using agents

**R1.** Controller/context state plus tool/session state that may persist externally.

**R2.** Local reasoning access combined with tool-mediated reads.

**R3.** Controller transition plus external delegated updates/actions.

**R4.** Centralized or modular orchestration.

**R5.** Planning/candidate generation optional.

**R6.** Tool/API boundaries are defining and must be included in the system boundary for capability/resource claims.

**Conclusion.** Fits by causal composition. A tool agent is not reducible to its language-model controller if the tools carry indispensable computation or state.

---

## 24. Multi-agent and decentralized systems

**R1.** Distributed persistent local states.

**R2.** Peer/message-network access.

**R3.** Local update plus communication-mediated joint update.

**R4.** Decentralized network, hierarchy, market/auction, blackboard, or dynamically routed collaboration.

**R6/R7.** Communication topology, bandwidth, latency and reliability are first-class resources.

**Conclusion.** Fits the chart. “Number of agents” alone is not a morphology; the communication/control topology is.

---

## 25. Embodied and robotic intelligence

**R0.** Closed perception-action loop with a physical environment.

**R1--R4.** Controller may instantiate any of the preceding computational forms.

**R6.** Physical embodiment is an external/closed-loop composition boundary only if the study boundary excludes body dynamics; otherwise body/environment state belongs in the complete system.

**R7.** Real-time latency, energy, sensor bandwidth, actuator precision and safety constraints can dominate morphology choice.

**Conclusion.** Fits the causal/resource language; embodiment changes the ecology and resource parameters rather than introducing a named computational prior.

---

## 26. Quantum-assisted systems

### Classical external interface

If all external inputs/outputs are classical and quantum computation is invoked as an internal subroutine, the overall system induces a classical stochastic causal transducer. The quantum component appears through R4/R6 and especially the substrate/resource profile.

### Genuinely quantum interface

If external channels carry coherent quantum states, interventions are quantum instruments, or systems share entanglement across the claimed interface, the current classical R0/R8 semantics are insufficient.

**Result.** Classical-interface quantum assistance fits; genuinely quantum interactive intelligence is a registered vocabulary boundary and requires a quantum successor.

---

# Cross-family reductions

The table below records the strongest common operational distinction rather than implementation names.

| Form class | Principal persistence/access structure | Principal update/topology structure | What actually distinguishes it in the chart |
|---|---|---|---|
| Stateless feed-forward | parameters + transient activations | acyclic composition | no task-time persistent state |
| Compressed recurrence | bounded recurrent state | sequential recurrent transition | fixed/compressed history channel |
| Dense addressable context | explicit transient item store | dense content-dependent aggregation | high-fidelity direct historical access |
| Sparse/indexed memory | external/item store | sparse/random access | scalable selective retrieval |
| Structured dynamical memory | recurrent latent state | structured/ selective state transition | compressed dynamics + resource scaling |
| Test-time adaptive memory | multiple persistence bands | inner adaptation inside run | update-timescale relocation |
| Symbolic/constraint state | explicit discrete relational state | rewrite/unification/search | exact structured state/update semantics |
| Probabilistic belief state | weighted hypotheses/statistics | evidence-driven redistribution | uncertainty representation/update |
| Planner/searcher | search workspace | candidate expansion/evaluation | explicit counterfactual topology |
| Population search | population | variation/selection | parallel alternative state set |
| Distributed agent system | multiple local states | communication network | nonlocal coordination resource |
| Tool-composed system | controller + external state | delegated causal calls | system-boundary expansion |
| Continuous/neuromorphic | physical dynamical state | event/differential flow | substrate-dependent dynamics/resources |

This table is deliberately many-to-many with architecture names. One named architecture can combine several rows; one row can be realized by unrelated implementation families.

---

# Result of the bottom-up stress test

At this resolution, no surveyed classical machine-intelligence family requires a primitive outside R0--R8. The reduction succeeds because the chart is expressed in causal persistence, access, update, routing, proposal, composition, resource and approximation terms rather than neural/symbolic labels.

This is **representation coverage**, not morphology recovery. It does not show that the top-down theory would have predicted any listed family before seeing it.

The stress test exposes four live vocabulary boundaries:

1. genuinely quantum external interfaces;
2. claims about internal physical topology finer than the declared probe family;
3. exact analog/noncomputable idealizations outside the effective digital-realization theorem;
4. systems whose identity depends on endogenous creation of new interface/resource types rather than merely new states within the declared domain.

A future architecture falling inside these boundaries is covered. A future architecture crossing one is a falsification/reopen event for the present formal domain.

---

# Next registered test

The next bottom-up result must not be another retrospective table. It should be a held-out recovery experiment:

1. select at least three materially different families and hide their labels/reductions from the derivation step;
2. define ecology/resource regimes using only R0--R8 coordinates;
3. derive predicted admissible/nondominated regions;
4. unblind and reduce the held-out families;
5. score region membership and feature collisions;
6. preserve any failure as evidence against sufficiency of the frozen vocabulary.

Only after that test is it meaningful to claim architecture-family recovery rather than coverage.
