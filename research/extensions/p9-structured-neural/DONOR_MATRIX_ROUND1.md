# P9 donor matrix — primary-source round 1

**Status:** research input only; not novelty authority; not protocol freeze.

This matrix records the **scientific/computational essence** of close work, where it is strongest, where its current evidence or abstraction is insufficient for P9, what ORION should absorb, and the exact discriminator that remains after absorption.

The operating rule is:

`DONOR -> ESSENCE -> STRENGTH FRONTIER -> FAILURE/OPEN FRONTIER -> ABSORB -> STRONG BASELINE -> INCREMENTAL DISCRIMINATOR`.

A donor that solves the proposed P9 atom is a successful research outcome: use the donor and delete the redundant ORION claim.

## 1. Heterogeneous Graph Transformer — Hu et al., 2020 — arXiv:2003.01332

### Essence
Type-dependent node/edge attention parameters plus relative temporal encoding make heterogeneity a first-class part of message passing rather than flattening every node/relation into one homogeneous graph.

### Strength frontier
Large heterogeneous graphs with many node/edge types and temporal structure; the original work demonstrates strong performance and scaling on the Open Academic Graph.

### Failure/open frontier for P9
Type-aware attention does not itself define local representation transport, global mapping consistency, mechanic precondition/effect semantics, admitted failure history, or epistemic `UNKNOWN`.

### Absorb
- typed node/relation parameters;
- temporal relation encoding where history is represented as graph events;
- HGT-class model as the minimum serious typed-graph baseline.

### P9 discriminator after absorption
Same typed topology and node/edge types, but different **transport values / mechanic effects / admitted history** require different answers. If HGT with those values supplied as ordinary edge features matches every richer P9 model, use HGT and strike architecture novelty.

---

## 2. GraphGPS — Rampášek et al., 2022 — arXiv:2205.12454

### Essence
Decouple local real-edge message passing from global attention, with explicit positional/structural encodings; treat graph-Transformer design as a modular recipe rather than one monolithic architecture.

### Strength frontier
General graph learning across heterogeneous benchmarks with a strong modern local+global recipe and linear-complexity design.

### Failure/open frontier for P9
GraphGPS does not require multiple local representation spaces, explicit transport obligations, mechanic contracts, or epistemic failure semantics.

### Absorb
- local + global computation decomposition;
- structural/positional encoding discipline;
- modular architecture recipe and strong graph-training baseline.

### P9 discriminator after absorption
Any claimed P9 architecture gain must survive a GraphGPS-class baseline with the same typed information and matched recipe. A weak vanilla GNN is not an acceptable comparator.

---

## 3. Knowledge Sheaves — Gebhart, Hansen & Schrater, 2021 — arXiv:2110.03789

### Essence
Represent each entity/relation through local vector spaces and restriction maps; a coherent knowledge embedding is an approximate global section satisfying schema-induced local consistency constraints.

### Strength frontier
Knowledge-graph representation where relations can act as transport/constraint maps and composite relation reasoning is important.

### Failure/open frontier for P9
The framework targets knowledge-graph embedding, not a dynamic epistemic trajectory with failures, mechanics, inquiry, protected authority or non-monotonic reopening.

### Absorb
- local representation spaces rather than mandatory universal embedding;
- relation-specific transport maps;
- global consistency as a distinct objective from local fit.

### P9 discriminator after absorption
Construct worlds with identical typed graph topology but different transport maps and global consistency. Test whether a sheaf/local-map representation adds value beyond typed edge features and explicit cycle features.

---

## 4. Neural Sheaf Diffusion — Bodnar et al., 2022 — arXiv:2202.04579

### Essence
Learn non-trivial cellular sheaves and diffuse through matrix-valued local maps, extending ordinary graph diffusion and giving greater control over heterophily/oversmoothing behavior.

### Strength frontier
Graph problems where neighboring nodes need not share labels/features and ordinary scalar message-passing geometry is restrictive.

### Failure/open frontier for P9
Strong theory for sheaf diffusion does not imply a generic advantage on inductive reasoning, composition, or scientific-state tasks.

### Absorb
- learned relation-specific linear transport;
- matrix-valued edge operations as a candidate P9 representation primitive;
- explicit comparison against trivial-sheaf/ordinary GNN cases.

### P9 discriminator after absorption
Only retain sheaf machinery if learned transport improves a frozen local-to-global or incompatible-view benchmark beyond GraphGPS/HGT with matched information.

---

## 5. Deep Neural Sheaf Diffusion — Bourgerie, Girdzijauskas & Fodor, 2026 — arXiv:2605.19021

### Essence
Replace the sheaf Laplacian with a sheaf-adjacency operator and add normalization/gating so matrix-valued edge functions remain useful at depth.

### Strength frontier
Deep aggregation and long-range graph tasks; reported large gains on synthetic long-range settings and improvements on real graph benchmarks.

### Failure/open frontier for P9
Long-range sheaf performance is not evidence that deep sheaf computation is useful for epistemic state or mechanic reasoning.

### Absorb
If a sheaf branch survives P9-A1, use the stronger deep recipe rather than comparing against obsolete shallow NSD alone.

### P9 discriminator after absorption
The P9 result must be attributable to the local-map/epistemic structure, not merely depth, normalization, gating or additional capacity.

---

## 6. Benchmarking Sheaf Neural Networks for Inductive Tasks — Fiorini, Coppola & Liò, 2026 — arXiv:2608.02558

### Essence
Systematically vary sheaf diffusion, restriction maps, stalk dimensions and modern GNN components under inductive cross-graph protocols.

### Strength frontier
A direct reality check on whether sheaf-specific design survives modern inductive evaluation.

### Key negative result for ORION
Restriction maps matter, but surrounding architectural components explain more performance variation than the sheaf-specific design space, and the evaluated SNNs do not reach the strongest baselines under the matched protocol.

### Absorb
- do not make sheaves the default P9 architecture;
- use general restriction maps if testing sheaves;
- tune/match the surrounding architecture before attributing gains to topology.

### P9 discriminator after absorption
Sheaf/local-chart structure must earn value on a task where transport is truly load-bearing. Generic graph-classification gains are insufficient.

---

## 7. CLRS / Generalist Neural Algorithmic Learner — Ibarz et al., 2022 — arXiv:2209.11142

### Essence
A graph processor can learn to execute many different algorithms and generalize algorithmic behavior out of distribution when the representation/training/processor encode the right algorithmic structure.

### Strength frontier
Exact algorithmic traces, diverse classical algorithms, and OOD execution/size generalization.

### Failure/open frontier for P9
The algorithm family and execution semantics are externally defined; the work does not claim a scientific epistemic state with representation obstructions, negative-history semantics or authority boundaries.

### Absorb
- exact algorithmic trace supervision;
- graph-processor architecture as a mechanic-execution baseline;
- CLRS-style OOD evaluation;
- generalist-vs-specialist analysis.

### P9 discriminator after absorption
P9 mechanic structure must improve unseen composition/failure-conditioned execution beyond a strong NAR processor. If not, use NAR.

---

## 8. TransNAR — 2024 — arXiv:2406.09308

### Essence
Separate natural-language processing from algorithmic computation by coupling a Transformer interface to a graph-based neural algorithmic reasoner.

### Strength frontier
Tasks where text specifies a problem but the internal solution follows algorithmic structure; explicit evidence that the language model need not be the only computation substrate.

### Failure/open frontier for P9/P10
The internal reasoner is algorithmic rather than a general typed epistemic/mechanic workspace.

### Absorb
- architecture pattern: language interface + non-language reasoner;
- mandatory P10 baseline;
- clean ownership split between P9 substrate and P10 language application.

### P9/P10 discriminator after absorption
P10 must beat or complement TransNAR-style composition on tasks where failure/representation/obstruction/UNKNOWN structure matters, not claim the interface split itself.

---

## 9. DreamCoder / library learning — Ellis et al., 2020 — arXiv:2006.08381

### Essence
Jointly learn a reusable symbolic library and task-solving programs; compression of recurring program structure changes the hypothesis space for future tasks.

### Strength frontier
Few-shot program induction and reusable abstraction discovery in domains with a suitable DSL and task distribution.

### Failure/open frontier for P9
Library primitives are programs, not necessarily separately modeled by empirical applicability, failure boundary, evidence lineage or epistemic preservation obligations.

### Absorb
- learned reusable library as a serious mechanic-discovery baseline;
- compression/abstraction as a candidate objective;
- explicit distinction between discovering a reusable primitive and merely routing among fixed skills.

### P9 discriminator after absorption
A typed mechanic learner must add value beyond library induction on structural near-misses, negative-history applicability or preserved-invariant composition.

---

## 10. Neural Module Networks / Task-Driven Modular Networks — 2015/2019 — arXiv:1511.02799, arXiv:1905.05908

### Essence
Build task-conditioned computation by composing reusable neural modules instead of using one monolithic network; modularity can support zero-shot composition when the module/task structure aligns.

### Strength frontier
Compositional tasks where subproblems and module reuse are meaningful and can be inferred/routed.

### Failure/open frontier for P9
A module is not automatically a scientific mechanic with explicit preconditions, effects, failures and preservation semantics.

### Absorb
- module composition and routing;
- zero-shot composition protocols;
- strong modular neural baseline before claiming mechanic composition.

### P9 discriminator after absorption
Same modules and router receive the same observations; test whether explicit mechanic contracts/failure history reduce invalid compositions or improve unseen-composition transfer.

---

## 11. Learning Symbolic Operators for TAMP — Silver et al., 2021 — arXiv:2103.00589

### Essence
Learn symbolic operators as a lossy abstraction of a continuous transition model, including the structure needed for efficient planning.

### Strength frontier
Long-horizon task-and-motion planning where learned preconditions/effects can guide symbolic search over continuous domains.

### Failure/open frontier for P9
Predicates/operators are grounded in a specific planning formalism and do not by themselves model epistemic evidence, representation pluralism or authority.

### Absorb
- precondition/effect operator learning;
- operator abstraction as the closest classical baseline to learned mechanics;
- planning utility rather than reconstruction score as an evaluation target.

### P9 discriminator after absorption
Any learned `Pre/Eff` mechanic claim must beat an operator-learning baseline; the residual must come from failure/preservation/epistemic structure, not merely action-model induction.

---

## 12. Learning Neuro-Symbolic Skills for Bilevel Planning — Silver et al., 2022 — arXiv:2206.10680

### Essence
Package learned parameterized policies, symbolic operators and samplers into reusable neuro-symbolic skills, then sequence them with bilevel search.

### Strength frontier
Object-centric continuous planning with sparse feedback and long horizons.

### Failure/open frontier for P9
The hierarchy is task/planning-centric; scientific uncertainty, unresolved mapping and authority are outside scope.

### Absorb
- skill package = learned operator + executor + sampling interface;
- bilevel verification/search pattern;
- modular skill baseline.

### P9 discriminator after absorption
Typed mechanics must demonstrate a function not captured by a neuro-symbolic skill package, or P9 should adopt this decomposition.

---

## 13. From Reasoning Traces to Reusable Modules — Kong et al., 2026 — arXiv:2606.18089

### Essence
Model reasoning traces as compositions of latent atomic modules and routing variables; controlled evidence suggests SFT supplies compound module material while RL extracts/recombines atomic modules for compositional generalization.

### Strength frontier
LLM post-training where compound reasoning traces contain reusable subskills and novel compositions matter.

### Failure/open frontier for P9
The atomic modules are latent computational objects; the framework does not require source-bound epistemic types, explicit failure boundaries, preservation obligations or external authority.

### Absorb
- compound traces may be better training material than isolated hand-labeled atoms;
- module extraction can be learned rather than manually annotated;
- RL/module recombination is a mandatory mechanic-discovery baseline.

### P9 discriminator after absorption
Do not claim `learn mechanics from traces`. Test whether typed applicability/effect/failure structure adds OOD/failure value beyond the extracted-module baseline.

---

## 14. Coconut — Hao et al., 2024 — arXiv:2412.06769

### Essence
Feed the model's last hidden state directly back as a continuous thought rather than decoding each intermediate reasoning step into language.

### Strength frontier
Certain logical/planning tasks with backtracking; fewer explicit thinking tokens and possible representation of multiple candidate next steps.

### Failure/open frontier for P9
Continuous hidden states are not inherently typed, externally auditable or faithful. Later causal/adversarial work pressures shortcut dependence and interpretability.

### Absorb
- language need not be the inner reasoning substrate;
- continuous recurrent latent computation is mandatory baseline;
- serial latent compute must be matched when comparing P9.

### P9 discriminator after absorption
Explicit typed latent state must improve structural near-miss/symmetry/failure/OOD outcomes at matched recurrence, not merely produce shorter chains.

---

## 15. Latent Reasoning as Vocabulary-Space Superposition / Latent-SFT — Deng et al., 2025 — arXiv:2510.15522

### Essence
Treat unstructured latent space as a learnability problem and constrain latent reasoning to a vocabulary-derived subspace/superposition, improving training and compression.

### Strength frontier
Latent LLM reasoning where hidden-state approaches degrade and a structured latent parameterization improves optimization.

### Failure/open frontier for P9
The imposed structure is lexical/vocabulary-space rather than an epistemic/mechanic state.

### Absorb
- `structured latent` is itself prior art;
- P9 must specify *which structure is task-sufficient and why*, not claim structure-vs-unstructured in the abstract.

### P9 discriminator after absorption
Compare typed epistemic structure to vocabulary-structured/anonymous latent baselines under identical reasoning depth and task information.

---

## 16. Symbol-Equivariant Recurrent Reasoning Models — Freinschlag et al., 2026 — arXiv:2603.02193

### Essence
Enforce symbol permutation equivariance architecturally rather than relying on augmentation, yielding robust generalization across symbol renamings and problem sizes in recurrent reasoning models.

### Strength frontier
Sudoku/ARC-style structured reasoning with arbitrary symbol/color identity and size extrapolation.

### Failure/open frontier for P9
Symbol symmetry is only one invariance and does not define epistemic relation/transport/mechanic semantics.

### Absorb
- surface-label permutation must be a formal benchmark symmetry;
- architectural equivariance is a strong baseline when applicable;
- do not credit P9 for robustness obtainable from standard equivariance.

### P9 discriminator after absorption
P9 must retain advantage on **same-surface/different-structure** cases where symmetry alone cannot solve the problem.

---

## 17. Latent State Design under Sufficiency Constraints — Kim, 2026 — arXiv:2605.01694

### Essence
Judge a latent state by the future function it must support; predictive, control, planning, memory and counterfactual sufficiency differ. The best state is not the one preserving maximal information.

### Strength frontier
A conceptual/evaluation framework for world-model state design that directly pressures maximal latent ontologies.

### Failure/open frontier for P9
This is a design framework rather than evidence for one P9 state representation.

### Absorb
- every proposed P9 coordinate needs a declared downstream sufficiency role;
- run coordinate-removal tests;
- avoid building the maximal ORION ontology into every learner.

### P9 discriminator after absorption
A coordinate is retained only if its removal makes a frozen target non-identifying or materially harms protected generalization/value.

---

## 18. Epistemic Neural Networks — Osband et al., 2021 — arXiv:2107.08924

### Essence
Explicitly represent epistemic uncertainty through a neural family indexed by an epistemic variable and evaluate joint predictive beliefs rather than treating uncertainty as a scalar afterthought.

### Strength frontier
Decision-making and uncertainty-sensitive prediction where posterior-like uncertainty structure matters.

### Failure/open frontier for P9
Epistemic uncertainty does not itself define `UNKNOWN` semantics, failure cause, mapping obstruction or authority.

### Absorb
- strong uncertainty baseline;
- preserve uncertainty as a distinct coordinate from validity/authority;
- evaluate calibration jointly where appropriate.

### P9 discriminator after absorption
`UNKNOWN` must provide operational value beyond a calibrated epistemic model; otherwise use the standard uncertainty machinery.

---

## 19. Rational Metareasoning for LLMs — De Sabbata, Sumers & Griffiths, 2024 — arXiv:2410.05563

### Essence
Treat extra reasoning as a costly computation and train the system to invoke intermediate reasoning only when its value justifies its cost.

### Strength frontier
Inference-cost reduction while preserving task performance.

### Failure/open frontier for P9
Scalar value-of-computation does not encode scientific hard obligations or identify which evidence is a load-bearing defeater.

### Absorb
- computation is an action with cost;
- uniform reasoning depth is a weak baseline;
- explicit compute/value accounting.

### P9 discriminator after absorption
Defeater-directed inquiry must beat or reduce cleanly to value-of-computation/information gain. Hard verification obligations remain non-compensatory and belong to P4/P8/P6, not to the learner's utility score.

---

## 20. Active Learning of Model Discrepancy with Bayesian Experimental Design — Yang, Chen & Wu, 2025 — arXiv:2502.05372

### Essence
Choose experiments using expected information gain while simultaneously learning model discrepancy, rather than gathering data passively or assuming the model is already correct.

### Strength frontier
Sequential experimental design under model discrepancy.

### Failure/open frontier for P9
Information gain is not automatically decision relevance and does not encode ORION's dependency/reopening structure.

### Absorb
- expected information gain as mandatory active-inquiry baseline;
- model discrepancy as an explicit alternative to mere predictive uncertainty.

### P9 discriminator after absorption
Construct cases where globally uncertain measurements are irrelevant to the root decision but a lower-entropy load-bearing defeater is decisive. If standard decision-focused information gain captures this exactly, adopt it.

---

## 21. Modular Memory / Transfer-Selective Replay — 2026 — arXiv:2603.01761, arXiv:2607.15587

### Essence
Continual learning should not only avoid forgetting: memory can be modular and replay should be selected for **compatibility/forward transfer**, not indiscriminately applied.

### Strength frontier
Continual adaptation and forward transfer under heterogeneous task streams.

### Failure/open frontier for P9
Compatibility signals need not equal causal failure applicability; replay does not itself model mechanic contracts or epistemic dependencies.

### Absorb
- failure/negative history must be selectively retrieved;
- stale/incompatible history is a hostile case;
- selective replay is a mandatory baseline for any P9 history benefit.

### P9 discriminator after absorption
Explicit failure boundary/dependency structure must improve compatible-vs-incompatible transfer beyond task-signature selective replay.

---

# Cross-donor synthesis after round 1

The donor set strongly argues **against** a single premature `new neural architecture` story.

The most defensible current decomposition is:

1. **typed relational substrate** — HGT/GraphGPS donor;
2. **optional local transport/higher-order substrate** — sheaf/cellular donor, only if A1 earns it;
3. **mechanic/operator execution** — NAR/operator-learning donor;
4. **mechanic discovery/composition** — library/module/RL-decomposition donor;
5. **non-language recurrent compute** — Coconut/recurrent-latent donor;
6. **symmetry/sufficiency discipline** — equivariance/world-state donors;
7. **failure/history** — continual-memory/selective-transfer donor;
8. **uncertainty/inquiry** — ENN/BED/metareasoning/counterexample donors;
9. **authority** — external ORION P4/P8/P6 structure; never learned into permission.

A combined P9 model is justified only if at least two or more of these components show **separate incremental value** over their donor-complete baselines and their composition remains beneficial under held-out domain/composition tests.

# Immediate experimental consequence

PR #473 begins at the correct layer: model-independent hostile worlds and view-identifiability analysis. The first neural implementation should follow only after #474–#477 freeze enough exact benchmark families to prevent architecture-driven target design.
