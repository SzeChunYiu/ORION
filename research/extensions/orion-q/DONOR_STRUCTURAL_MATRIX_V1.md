# ORION-Q donor structural matrix V1

**Status:** `S0_DONOR_MAP_PROVISIONALLY_FROZEN`  
**Literature cutoff:** 2026-08-20  
**Parent:** #633  
**S0 ledger:** #638  

This is a bounded donor/attribution freeze, not a novelty certificate. Reopen when a benchmark maps to an unsaturated donor family, a direct parent appears for a frozen discriminator, protected results force a claim/baseline change, or the literature changes materially before external novelty review.

## Operating rule

For each close parent:

`extract structure -> adopt it -> make it a baseline/tool when faithful -> strike the occupied claim -> retain only the marginal ORION discriminator`.

A specialist verifier is not something ORION must beat on its native theorem. ORION may only earn value above a donor-complete system on a pre-frozen marginal discriminator.

## A. Automated quantum algorithm/program discovery

| Donor | Structure absorbed | Claim struck | ORION use |
|---|---|---|---|
| Finger et al., *Automated near-term quantum algorithm discovery for molecular ground states*, arXiv:2603.26359 | Hive LLM-driven distributed evolutionary program synthesis; evolves algorithm code; held-out chemistry transfer; interpretability; hardware/emulator validation | LLM/evolution discovers resource-efficient quantum heuristic algorithms | mandatory prospective/chemistry discovery baseline |
| Rouillard et al., *Automated quantum algorithm design using a domain-specific language*, arXiv:2503.08449 / EPJ QT 2026 | parametric DSL + evolutionary search; scalable `n -> algorithm(n)`; QFT/Grover/DJ reconstruction from small n | parametric quantum algorithm discovery from small instances | QC-3 baseline |
| QSynth, POPL 2024, DOI 10.1145/3632901 | recursive/inductive quantum program synthesis; logical/SMT verification; explicit language/representation limitations | recursive verified quantum-program-family synthesis | QC-3 formal baseline; limitation pressure |
| Sarra et al., *Discovering Quantum Circuit Components with Program Synthesis*, arXiv:2305.01707 | DreamCoder-style wake/sleep library learning and reusable composite gate discovery | reusable quantum gate/library discovery | QC-2/QC-3 language-growth baseline |
| Learned-gadget RL, Communications Physics 2025, DOI 10.1038/s42005-025-02475-6 | extract composite gates from strong circuits and add them to RL action space | discovered gadgets expand search language/action space | direct QC-2 baseline |
| Heitritter et al., *Evolving Quantum Error-Correcting Encodings for Molecular Simulation*, arXiv:2606.25870 | LLM evolutionary constructor search + exact external verifier; parametric interpretable encodings | `LLM + evolution + verifier` quantum discovery | protected-generation baseline |
| ResearchEVO, arXiv:2604.05587 | LLM-guided co-evolution of logic/architecture; blind QEC mechanism discovery; discover-then-explain pipeline | broad blind AI quantum/QEC mechanism discovery | QC-5 scientific-agent donor |
| PhyNex, arXiv:2606.14266 | feedback-driven computational-physics search; memory from successes/failures; quantum/physics tasks | broad failure-aware LLM physics/quantum method search | QC-5 donor |
| SCALAR, arXiv:2605.10327 | simulation + symbolic conjecture generation + LLM interpretation for quantum circuits | LLM-assisted automated quantum conjecture discovery | conjecture-generation donor |
| DLP, arXiv:2602.08880 | differentiable structural/logical circuit discovery and adaptation | differentiable quantum circuit-structure search | circuit-discovery baseline |

## B. Adaptive quantum methods / operator pools / control

| Donor | Structure absorbed | Claim struck | ORION use |
|---|---|---|---|
| AutoQResearch, arXiv:2604.24283 | LLM edits solver-control policy from stagnation/infeasibility/concentration diagnostics; scout/promote/confirm/replay | failure-conditioned quantum solver-policy adaptation | QC-0/QC-5 router baseline; evaluation discipline |
| ADAPT-VQE / qubit-ADAPT complete-pool line | adaptive operator selection from predefined pools; pool completeness analyses | adaptive operator-pool growth/selection | QC-2 baseline |
| Viswanathan et al., *An Optimal Framework for Constructing Lie-Algebra Generator Pools*, arXiv:2511.22593 | polynomial-scaling optimal minimal complete generator pools for target Lie algebra | automatic minimal complete quantum generator pool construction | exact ceiling/specialist tool where faithful |
| finite-dimensional quantum controllability / Lie-algebra rank-condition literature | algebraic reachability/controllability certificates from generated dynamical Lie algebra | quantum algebra can certify supplied controls are insufficient | specialist verifier, not ORION contribution |
| *Engineering precise and robust effective Hamiltonians*, PRA 113, 042409 (2026) | minimal toggling-frame subspace; achievable effective-Hamiltonian sets | structured Hamiltonian/control reach characterization | control donor |
| *Enhancing reachability of VQAs via input-state design*, Communications Physics 2026 | input-state redesign to enlarge reachable ansatz set | change quantum input/representation to improve reachability | representation-change donor |

## C. QSP/QSVT / block encoding / data loading

| Donor | Structure absorbed | Claim struck | ORION use |
|---|---|---|---|
| standard QSP/QSVT + QSP phase tools | polynomial/singular-value transform framework and phase-factor solving | QSVT/QSP or phase optimization itself | fixed framework/baseline |
| Chakraborty et al., arXiv:2504.02385; randomized QSVT arXiv:2510.06851 | block-encoding-free/minimal-ancilla/randomized QSVT routes with regime-dependent trade-offs | conventional block encoding is mandatory; route change itself is novel | QC-4 alternative-route donor |
| U(N)-QSP/QSVT, arXiv:2408.01439 | expanded matrix-polynomial transform language | broad transform-language extension | QC-4 donor |
| arbitrary-matrix eigenvalue transformation, arXiv:2604.19688 | `n`-regular block encodings enabling new transform classes | redesigning encoding constraints to unlock transforms broadly | QC-4 donor |
| Ko, *Exact and Efficient Circuit Construction for Block Encoding Matrix Polynomials*, arXiv:2608.15161 | exact near-optimal classical compiler for polynomial block encodings | automated exact efficient polynomial block-encoding construction | specialist compiler |
| Petrič & Zander, Qrisp BlockEncoding Interface, arXiv:2604.18276 | composable high-level block-encoding programming abstraction + applications/resource estimation | reusable block-encoding interface | implementation donor |
| Rullkötter et al., arXiv:2507.17658 | variational compact/symmetry-aware block-encoding compilation | learn compact block-encoding circuit | specialist baseline |
| Alonso-Linaje et al., *Quantum compilation framework for data loading*, arXiv:2512.05183 | automated selection among QROM/sparse/MPS/Fourier/Walsh/etc. under approximation/resource trade-offs; new subroutine improvements | automatic quantum encoding/representation method selection and broad compiler-discovered encoding improvements | mandatory QC-4 multi-route compiler baseline |
| Over et al., *Operator Learning for efficient Quantum Computation*, arXiv:2606.20184 | full-stack variational circuit learning for arbitrary operators, including one-ancilla block-encoding route | learn efficient operator/block-encoding circuit | QC-4 baseline |

## D. Full-stack resource/design automation

| Donor | Structure absorbed | Claim struck | ORION use |
|---|---|---|---|
| AutoQuREO, arXiv:2608.12936 | user-defined stack abstraction; reusable stack components; surrogate layer resource models; integrated multi-objective full-stack optimization | broad automated full-stack quantum co-design/resource trade-off exploration | mandatory QC-4 donor-complete optimizer |
| Campbell et al., arXiv:2604.01376 | compilation-driven resource estimation under configurable hardware assumptions; regime-dependent bottlenecks | cross-layer hardware/resource feedback as ORION abstraction | resource specialist |
| Su et al., arXiv:2608.04573 | programmer-visible QEC abstractions + cross-layer program/hardware resource analysis | typed cross-layer fault-tolerant resource interface | resource-programming donor |
| QEC design-automation literature, e.g. arXiv:2507.12253 | synthesis/transpilation/layout/verification automation across FTQC | broad FTQC design automation | donor field |

## E. Quantum architecture / representation selection

| Donor | Structure absorbed | Claim struck | ORION use |
|---|---|---|---|
| Tung et al., *Towards Automated Selection of Quantum Encoding Circuits via Meta-Learning*, arXiv:2604.19076 | dataset-feature meta-learning recommends encoding circuit | learn/select quantum representation/encoding from problem features | QC-0/QC-4 selection baseline |
| Quantum Architecture Search survey arXiv:2406.06210; RL-QAS arXiv:2509.11198; QArchSearch arXiv:2310.07858 | automated PQC architecture generation/selection under task/hardware constraints | automated circuit architecture search | baseline field |

## F. Formal verification / exact synthesis / unrealizability

| Donor | Structure absorbed | Claim struck | ORION use |
|---|---|---|---|
| Lean-QIT, arXiv:2607.09632; Lean-QEC, arXiv:2605.16523; SQIR/VOQC/QWIRE/Qbricks/VyZX line | theorem-prover-backed quantum semantics/circuit/code verification | formal quantum verification | specialist authority/verifier stack |
| Hu et al., *Proving Unrealizability for Syntax-Guided Synthesis*, arXiv:1905.05800 | proof that no program in a supplied grammar satisfies spec; cost optimality via lower-cost unrealizability | generic proof current search grammar cannot solve task; generic minimality proof | conceptual/QC-2 verifier donor |
| Kim et al., *Unrealizability Logic*, arXiv:2211.07117 | checkable Hoare-style proof of unrealizability over infinite program spaces | interpretable/checkable proof of search-space inadequacy | formal donor |
| syntax-guided automated program repair (CAV repair line, DOI 10.1007/978-3-031-65633-0_1) | property-preserving repair search / transparency | generic minimal semantics-preserving repair | QC-2 parent-domain baseline |
| CEGIS(T), abstraction-refinement synthesis | counterexample/proof-driven search and theory-solver communication | generic verifier-guided repair/search | methodology donor |

## G. Routing / tools / telemetry / abstention / authority

| Donor | Structure absorbed | Claim struck | ORION use |
|---|---|---|---|
| Select-then-Solve, arXiv:2604.06753 | learned per-task reasoning-paradigm router; oracle-router gap | choose reasoning/search paradigm per task | QC-0 baseline |
| AutoTool dynamic selection, arXiv:2512.13278 | learned dynamic selection across 1,000+ tools; unseen-tool generalization | dynamic specialist-tool selection | QC-0 baseline |
| AutoTool graph routing, arXiv:2511.14650 | history/transition graph for efficient tool selection | tool-history structural routing | history baseline |
| AgentAbstain, arXiv:2607.10059 | paired should-act/should-abstain executable tasks under ambiguity/tool/runtime failures | paired abstention controls / know when not to act | QC-0/QC-2 hostile methodology |
| Agentic Abstention, arXiv:2606.28733 | sequential answer/abstain/gather-evidence decision; stopping rules from trajectories | failure history drives gather/stop | abstention donor |
| EG-VAR, arXiv:2607.12650 | tool-attested evidence + Lean-kernel verification + replayable abstention and scope boundaries | generic proof-carrying evidence-governed claim/action | authority donor |
| provenance-sensitivity audit, arXiv:2607.20827 | hold proposition/policy fixed, perturb only source authority | source-authority perturbation controls | hostile test donor |
| TelemetrySuffBench, arXiv:2608.07899 | separates detection/localization/abstention; exact-equal ambiguous pairs; telemetry masks and ceilings | generic richer-telemetry failure-origin benchmark | mandatory QC-0 methodology/baseline |
| Canary Tools, arXiv:2608.04719 | semantic decoys, parameter traps, capability mirages, prerequisite blindness, temporal/granularity traps | diagnostic tool-selection decoys | QC-0 hostile tools |
| Ojewale & Venkatasubramanian, arXiv:2606.02965 | specification/verification/authority abstention gaps | generic gap taxonomy | QC-0 abstention taxonomy donor |

## H. Scientific-agent systems

| Donor | Structure absorbed | Claim struck | ORION use |
|---|---|---|---|
| OR-Agent, arXiv:2602.13769 | branching research tree, backtracking, short/long reflection, compressed memory | structured failure-aware scientific research trajectory management | QC-5 agent baseline |
| Weidener et al., arXiv:2601.12542 | specialist agents + persistent research world state | multi-agent research with persistent world state | systems donor |
| PhysVEC, arXiv:2604.00149 | quantum many-body agent with separate programming/scientific verifiers and auditable self-correction | broad verifiable/self-correcting AI quantum physicist | QC-5 donor |
| LADeQ, arXiv:2606.20729 | test-time cross-domain method construction/implementation/benchmarking | broad test-time LLM scientific method invention | QC-5 parent |
| sign-embedding human-AI co-discovery, arXiv:2606.24899 | problem formation, route expansion, connection/proof/complexity assistance with human scientific judgment | broad AI-assisted quantum discovery | workflow donor |

## I. Quantum debugging / failure diagnosis

| Donor | Structure absorbed | Claim struck | ORION use |
|---|---|---|---|
| Quetschlich & Di Matteo, arXiv:2509.03280 | quantum bug taxonomy; many bugs arise from interactions of multiple algorithm/workflow aspects; no simple bug-class→debug-strategy mapping | rhetoric that quantum failure diagnosis is multi-factor/quantum-specific | QC-0 interaction pressure |
| Yousuf & Sofi, arXiv:2506.10397 | rule-based quantum software bug classification at scale | learned P9 needed for basic bug classification | simple-rule baseline |
| Zappin et al., arXiv:2506.17306 | practitioner testing/debugging practices and tool gaps | none; motivation only | external motivation |

## Frozen ORION-Q residuals after saturation

### R-Q0 — P9 marginal quantum structural state

Does **any genuinely quantum structural coordinate** provide held-out failure-regime / next-action value beyond a donor-complete generic state containing telemetry, history, router/tool metadata, provenance/abstention information and specialist evidence?

Required equation:

`DONOR_COMPLETE_GENERIC_STATE + Q_COORDINATE -> incremental value`

Delete the coordinate if the marginal value disappears. Generic routing/telemetry evaluation is not the contribution.

### R-Q2 — P10 marginal escalation chain

Conditional on independently valid failure diagnosis, does the typed chain

`failure receipt -> unmet quantum capability -> edit -> repair receipt`

reduce false escalation or improve held-out repair over donor-complete synthesis/library/control baselines? Individual unrealizability proofs, gate libraries, control certificates and minimal-repair primitives are donor-owned.

### R-Q4 — obstruction-justified algorithmic abstraction change

Can verified obstruction evidence justify moving outside a frozen incumbent algorithmic abstraction/interface and yield independently verified held-out reach/Pareto gain beyond strong multi-method compilation and full-stack optimization (AutoQuREO-class) inside the incumbent route set?

Representation/encoding selection itself is donor-owned. The residual is the **marginal value of obstruction-conditioned abstraction change** after donor-complete route optimization.

### R-Q5 — prospective result

Only after R-Q0/R-Q2/R-Q4 gates survive: produce a prospectively frozen quantum result that external verification/novelty review cannot reduce to known-method retrieval, ordinary composition, search within an existing language, or a donor mechanism above.

## Frozen non-claims

ORION-Q does not own, by itself:

- LLM/evolution/verifier quantum discovery;
- reusable-gate or library learning;
- recursive/parametric quantum program synthesis;
- adaptive quantum operator-pool or solver-policy growth;
- expressivity vs bounded reachability;
- Lie/control obstruction certificates;
- unrealizability proofs or minimal repair;
- dynamic tool/reasoning routing;
- agent abstention/provenance/verified-evidence governance;
- automated quantum encoding/architecture selection;
- QSP/QSVT or block-encoding construction;
- full-stack resource/co-design optimization;
- broad verifiable multi-agent quantum science.

The programme can only earn bounded marginal results beyond this donor-complete state.
