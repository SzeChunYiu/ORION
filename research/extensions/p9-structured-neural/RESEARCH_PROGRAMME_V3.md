# ORION-P9 Research Programme V3 — Structured Epistemic Neural Computation

**Status:** ACTIVE RESEARCH / NO PAPER CLAIM / DONOR SATURATION OPEN

**Paper parent:** #391  
**Saturation:** #469  
**Protocol:** #426  
**Execution:** #428  
**Verification:** #283  
**Novelty authority:** #287

This document consolidates the current P9 research programme after the August 18, 2026 refoundation and subsequent ORION-style nearest-work sweeps. It is not a manuscript and does not authorize a scientific positive.

## 1. Current scientific question

The broad aspiration is:

> Can a learning/reasoning system operate over a dynamic, typed epistemic state — including claims, observations, representations, mechanics, mappings, evidence, failures, dependencies and explicit unresolved structure — and thereby improve compositional/OOD problem solving beyond the strongest simpler and donor-complete alternatives?

After nearest-work pressure, P9 must **not** claim any of the following broadly:

- graph/relational reasoning;
- typed/heterogeneous graph attention;
- sheaf/local-chart representations;
- neural algorithmic reasoning;
- reusable skill/module/library discovery;
- rule templates and entity binding;
- reasoning outside language / continuous latent reasoning;
- mechanism-centric world models;
- causal invariance / independent mechanisms / sparse mechanism shift;
- uncertainty estimation or abstention;
- active learning / information gain / counterexample search;
- value-of-computation / adaptive compute;
- program synthesis / symbolic operators;
- object-centric representation;
- compositional representation alone.

These are donor fields to absorb.

## 2. Research doctrine — competitors are donors

For every serious competing model or parent field:

`PRIMARY SOURCE`
→ `EXTRACT SCIENTIFIC ONTOLOGY / PHILOSOPHY`
→ `DECOMPOSE ATOMIC MECHANICS`
→ `IDENTIFY STRENGTH FRONTIER`
→ `IDENTIFY FAILURE FRONTIER`
→ `ADOPT THE STRONG PART`
→ `PRESERVE ITS FAILURE AS A HOSTILE TEST`
→ `BUILD THE STRONGEST DONOR-COMPLETE BASELINE`
→ `ADD ONE ORION COORDINATE`
→ `TEST ITS MARGINAL VALUE`
→ `KEEP OR DELETE IT`.

“Beat the competitor” therefore means:

> outperform or meaningfully dominate the strongest appropriate donor-complete baseline on the **pre-frozen discriminator introduced for that exact residual**, under matched admissible information and explicit resource accounting.

Global leaderboard superiority on unrelated native tasks is neither required nor sufficient.

If the donor is sufficient, ORION uses it and strikes the redundant novelty claim.

## 3. Current atomic decomposition

The decomposition remains open to revision. Ten atoms are currently necessary.

### A1 — Representation (#474)

Question: what is the minimum sufficient state substrate?

Candidate families:

- flat features / MLP;
- sets / Deep Sets / Set Transformer;
- sequences/events;
- homogeneous graphs;
- HGT/GraphGPS typed graphs;
- hypergraphs/cell/simplicial complexes;
- sheaves/local-chart transport;
- object-centric slots;
- probabilistic belief states;
- VSA/TPR/associative binding representations;
- symbolic operators/programs;
- hybrid explicit + latent state.

Critical donor lesson: richer topology is not automatically better. A 2026 inductive sheaf benchmark found restriction maps meaningful while modern surrounding GNN choices explained more variance and the tested SNNs did not automatically beat the strongest baselines.

Promotion rule: use the simplest representation that identifies and learns the frozen target. Sheaf/higher-order machinery enters only if typed graph + explicit features fails a transport/higher-order discriminator.

### A2 — Mechanics / operators (#475)

Question: can reusable problem-solving operations be learned with reliable applicability/effect/failure boundaries?

Donor families:

- DreamCoder / Stitch / LILO;
- neural module networks;
- symbolic operator/action-model learning;
- neuro-symbolic planning skills;
- neural algorithmic reasoning;
- latent/reusable reasoning modules learned from compound traces.

Claim contraction: P9 does not own reusable skills, libraries, modules or learned operators.

Residual test: explicit applicability/effect/failure/preservation structure must add OOD composition/failure value beyond donor-complete operator/module/NAR systems.

### A3 — Latent / recurrent computation (#476)

Question: does typed explicit latent state add value beyond anonymous continuous/recurrent reasoning after serial-compute matching?

Donors:

- Coconut;
- recurrent-depth reasoning;
- structured latent/SFT variants;
- symbol-equivariant recurrent reasoners;
- world-model latent-state sufficiency.

Claim contraction: `reasoning need not occur in language` is prior work.

Residual test: explicit typed/auditable state must improve surface-reminting, structural near-miss, failure/OOD or compute efficiency beyond strong latent baselines.

### A4 — Failure, UNKNOWN and inquiry (#477)

Question: when does explicit negative history/non-identifiability improve what the system tries next?

Donors:

- Epistemic Neural Networks;
- selective/conformal prediction;
- counterexample-guided learning/synthesis;
- Bayesian experimental design / information gain;
- rational metareasoning / value of computation;
- modular memory / selective replay;
- three-valued neural logic systems.

Required distinction:

1. logical three-valued UNKNOWN;
2. probabilistic uncertainty;
3. structural non-identifiability;
4. P4/P8 evidence/authority `CANNOT_CHECK`.

P9 primarily studies (3); it may consume (1–2). It never owns (4).

### A5 — Inference engine (#478)

Question: once the state exists, should the next state be produced by a neural predictor at all?

Candidate engines:

- neural transition prediction;
- probabilistic graphical inference;
- differentiable logic / ILP;
- energy/constraint optimization;
- classical graph/search planning;
- SAT/SMT/constraint solving;
- program search;
- hybrids.

Critical donor lesson: energy-based/global inference can add coherence but latent optimization can also drift off the decoder/training manifold. A neural controller is not privileged.

### A6 — Data / ground truth (#479)

Question: can structural supervision be constructed without LLM pseudo-gold or hidden-chain-of-thought labels?

Data ladder:

- D0 exact synthetic worlds;
- D1 deterministic algorithms/program traces;
- D2 formal mathematics/proof traces;
- D3 auditable ORION episodes;
- D4 expert-reviewed natural scientific methods only after agreement/recoverability gates.

P1/P3 deliberately stopped at exact-ground-truth structure panels; broad natural scientific structure is therefore a real P9 obligation, not something to fabricate retrospectively.

### A7 — Scale / resource regime (#480)

Question: is structure valuable asymptotically, or primarily for sample efficiency, compute efficiency, OOD transfer or lower failure cost?

Mandatory axes include:

- training examples and diversity;
- parameter count;
- training/inference compute;
- recurrent depth;
- search expansions;
- retrieval/tool calls;
- preprocessing/annotation cost;
- latency/memory/energy where reliable.

Strong graph foundation models and object-centric scaling studies make one-point small-model comparisons scientifically inadequate.

### A8 — Learning law (#482)

Question: is a gain due to architecture, or to supervision/curriculum/RL/meta-learning?

Donors/pressures:

- compound-trace module learning;
- SFT vs RL module extraction;
- compositional curriculum theory;
- probabilistic compositional meta-learning;
- CLRS/NAR intermediate hints;
- self-supervised reconstruction;
- contrastive/equivariant learning.

Key lesson: a structured/factorized representation does **not** imply compositional generalization. Data statistics and implicit bias can still drive memorization/shortcuts.

### A9 — Template / binding / instantiation (#484)

Question: is the reusable object a concrete mechanic, or an abstract template plus role/entity binding?

Major donors:

- Neural Production Systems (NeurIPS 2021);
- production-system / ACT-R / Soar procedural-rule lineage;
- neural program synthesis;
- TPR/VSA role-filler binding;
- symbolic operator grounding;
- Transformer variable-binding analyses.

Current factorization hypothesis:

`MechanicTemplate`
+ `MechanicBinding(role -> current atom)`
→ `InstantiatedMechanic`.

Important contraction: explicit binding is not universally necessary. ICML 2025 work shows a standard Transformer can learn a systematic variable-dereferencing algorithm internally in controlled symbolic programs.

Residual test: explicit/auditable binding must improve role/entity OOD, ambiguity handling, failure localization or resource efficiency beyond learned Transformer binding and Neural Production Systems.

### A10 — Causal / intervention-stable mechanics (#485)

Question: is the learned effect a predictive association or a stable consequence of applying/intervening with the mechanic?

Major donor:

- Posner, Lei & Schölkopf, *Mechanistic World Models*, arXiv:2607.12474.

Additional donors:

- Variational Causal Dynamics;
- COMET / competitive independent mechanisms;
- WM3C compositional causal world models;
- causal representation learning / sparse mechanism shift;
- intervention-effect meta-learning.

Claim contraction: P9 does not own mechanism-centric world models, `prediction != explanation`, independent mechanisms, sparse mechanism shift or local modular adaptation.

Candidate residual only after absorption:

`template + binding + intervention-conditioned applicability/effect + preservation/failure + negative lineage + explicit unresolved`.

This must earn value on interventional/OOD tests beyond donor-complete causal/mechanistic world models.

## 4. Cross-cutting attribution equation

Every promoted result must attempt to distinguish:

`RESULT`
=
`INFORMATION AVAILABLE`
+ `REPRESENTATION`
+ `INFERENCE/COMPUTATION`
+ `LEARNING RECIPE / SUPERVISION`
+ `DATA COVERAGE`
+ `SCALE / RESOURCE`
+ `SEARCH / TOOLS`
+ `RANDOMNESS`.

A mechanism claim is invalid if the apparent gain is explained by an uncontrolled difference in another term.

## 5. Exact falsification substrate already implemented

### Tranche 0 — merged PR #473

Commit: `8879ba2e3380e414ea811c7de4aa067fb3e02a90`.

Implemented:

- `P9StructuralWorld`;
- typed atoms/relations;
- non-authorizing mechanic views;
- local affine transport maps;
- explicit failure history;
- `GLUE / OBSTRUCTION / UNKNOWN`;
- evaluator-controlled model views;
- surface reminting;
- exact view-identifiability analysis;
- deterministic accuracy ceilings.

Bootstrap six-world information ladder:

- SURFACE: `1/2`;
- TOPOLOGY: `1/2`;
- TYPED: `2/3`;
- CURRENT: `5/6`;
- SEMANTIC: `1`.

These are information ceilings on the exact sample, not learned-model results.

### Tranche 1 — merged PR #481

Commit: `e5504065dcf1f71b371a611b5d5ad8db7f4a8ce0`.

Implemented:

- deterministic hostile-pair generators;
- opaque model-visible identities/surfaces;
- relation-semantics, transport-gluing and failure-history families;
- train/dev/test identity disjointness by construction;
- evaluator/model metadata separation;
- content-bound split/corpus manifests;
- analytic ceilings preserved at arbitrary balanced sample size.

### Tranche 2 — M0 PR #483

Current objective: architecture-neutral task/evaluator validation before learning.

Frozen task types:

- candidate-relative mechanic ranking;
- fixed three-way gluing classification.

Important negative history retained:

1. protocol V0 candidate ordering used the hidden SEMANTIC fingerprint and would have leaked hidden coordinates into weaker-view presentations;
2. pre-execution hostile review caught it;
3. V0 is retained as invalid design history;
4. V0.1 freezes ordering by the selected model-visible view fingerprint only;
5. a second pre-outcome audit caught loss of SURFACE mechanic incidence during task separation; fixed before outcome-bearing execution.

M0 exact semantic oracle is forbidden from reading evaluator gold. Null predictors are view-restricted and checked against exact deterministic ceilings.

## 6. First learned gate — M1 (#486)

P9 will not jump from M0 into Graph Transformers.

M1 gives classical models first right of refusal:

- logistic / linear;
- linear SVM;
- decision tree;
- random forest / gradient boosting;
- nearest-neighbour / case-based;
- shallow MLP only after non-neural models leave a justified nonlinear residual.

Mechanic selection remains candidate-relative. Gluing remains fixed-vocabulary.

A model exceeding its selected-view information ceiling invalidates the run as leakage/evaluator mismatch.

Escalation is residual-specific:

- relational residual → typed graph/HGT/GraphGPS;
- local-transport residual → graph+transport then sheaf/higher-order;
- iterative operator residual → NAR/operator learner;
- recurrent-compute residual → latent/recurrent;
- global coherence/hypothesis residual → probabilistic/search/constraint inference;
- template/entity transfer residual → A9 production/binding;
- intervention transfer residual → A10 causal/mechanistic models.

## 7. Planned exact-world expansions before final P9 freeze

The current three families are evaluator bootstrap, not the final paper benchmark.

Required future exact families include:

- unseen mechanic composition;
- precondition/effect structural near-miss;
- invariant/preservation violation;
- explicit template + role/entity binding;
- entity-count extrapolation;
- symmetric unresolved binding;
- pairwise-consistent/global-cycle-inconsistent mappings;
- genuinely higher-order interaction not identified by pairwise projection;
- stale/incompatible negative history;
- decision-relevant defeater vs irrelevant high uncertainty;
- observational equivalence / interventional difference;
- sparse mechanism shift;
- spurious predictive shortcut broken by intervention;
- representation failure vs mechanism failure.

Each family needs an information-lattice analysis before a learned model is allowed to use it.

## 8. External transfer falsifiers

After the exact substrate has located a real residual, consider frozen external tests where task mapping is honest:

- CLRS/NAR OOD algorithmic tasks;
- Ineq-Comp formal compositional reasoning;
- XDomainBench scientific cross-domain composition;
- ClassicLogic/hierarchical strategy tasks;
- formal mathematics/proof traces with exact source/toolchain identity;
- controlled scientific method/procedure transfer after A6 gold quality gates.

External benchmark success cannot repair a failed exact non-vacuity test.

## 9. Paper hypothesis policy

Do **not** freeze a P9 headline claim yet.

The current programme contains several mutually competing possible outcomes:

- typed graph is sufficient;
- local transport adds value;
- NAR/operator learning is sufficient;
- explicit template/binding adds value;
- continuous latent is sufficient;
- probabilistic/search hybrid is best;
- causal/mechanistic world model is sufficient;
- explicit ORION state is useful only for sample efficiency/auditability;
- no structural advantage survives strong donors.

Any of these is a successful scientific terminal if established prospectively.

A standalone paper is justified only after:

1. donor saturation stops materially changing the architecture/baseline/claim for two rounds;
2. exact-world non-vacuity survives;
3. strong donor-complete baselines run;
4. at least one OOD/compositional/interventional residual survives resource matching;
5. null/harmful/failure cases remain visible;
6. promoted positives reproduce independently (#283);
7. current novelty authority (#287) confirms a bounded residual;
8. the manuscript states the actual earned regime rather than the original aspiration.

## 10. Candidate paper shapes — choose only after results

### Shape S1 — representation paper
If the main result is a typed/local/higher-order representation advantage under exact/OOD controls.

### Shape S2 — mechanic-learning paper
If template/binding/effect/failure learning yields robust unseen composition beyond module/NAR/operator donors.

### Shape S3 — causal mechanism paper
If intervention-stable typed mechanics outperform mechanistic/causal world-model donors on sparse shifts and transfer.

### Shape S4 — systems/composition paper
If no individual representation is novel but a verified combination of donor primitives yields a strong problem-solving result with clear ablations.

### Shape S5 — negative/result paper
If strong donors eliminate the residual, publish only if the resulting benchmark/negative finding itself is scientifically valuable; otherwise merge the knowledge into the programme.

Do not select a paper shape before the data.

## 11. Current saturation status

`OPEN`.

Recent rounds materially changed the programme:

- sheaf benchmark pressure prevented premature sheaf default;
- reusable-module work narrowed mechanic discovery;
- Transformer variable-binding work narrowed A9;
- three-valued neural logic narrowed UNKNOWN claims;
- kernel theory separated representation from data/statistics;
- production-system literature created A9 binding;
- Mechanistic World Models / causal modular work created A10.

Therefore no no-material-change saturation round has yet been earned after the latest atom expansion.

## 12. Operating rule for future sessions

Every P9 session must take **one bounded atom/tranche**.

Before code:

1. read this document, #391, #469 and the atom issue;
2. read current main, not a remembered branch;
3. inspect overlapping PRs;
4. update nearest work if material;
5. freeze exact discriminator and resource/information contract;
6. write RED hostile tests;
7. implement the smallest model/feature/mechanic needed;
8. preserve nulls and failed designs;
9. route any positive through #283/#287;
10. do not combine components until each has earned independent incremental value.

The purpose is not to create the most complicated neural architecture. The purpose is to learn the **smallest donor-complete computational structure that actually improves hard problem solving under falsifiable conditions**.
