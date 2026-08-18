# P9 computational search space V1

**Purpose:** prevent P9 from becoming `pick a fashionable graph architecture and rationalize it afterward`.

This is a search-space map, not a frozen architecture. Every family is considered by **function**, and the simplest family that satisfies a frozen atom should win.

## Axis 1 — what is the model state?

### 1A. Flat vector / MLP
Use when the task can be represented by a fixed sufficient statistic.

**Why include:** if a small feature vector solves the protected discriminator, graph/topological machinery is unnecessary.

### 1B. Set / multiset
Donors: Deep Sets, Set Transformer.

Use when identity/order are irrelevant but pairwise/global interactions matter.

**Pressure:** some ORION states may be unordered collections of obligations/evidence; do not force graph edges when a set is sufficient.

### 1C. Sequence / event history
RNN/Transformer/state-space models over typed events.

Use when temporal order/history is load-bearing and current relational structure is secondary.

### 1D. Homogeneous graph
Standard message passing / graph Transformer.

Use when pairwise topology is sufficient and relation types can be encoded simply.

### 1E. Heterogeneous typed graph
Donors: HGT, GraphGPS-class recipes.

Use when object/relation types and temporal relation structure are load-bearing.

### 1F. Hypergraph / cell complex / simplicial complex
Use when higher-order interactions are not recoverable from pairwise edges without ambiguity or combinatorial blow-up.

### 1G. Sheaf / local-chart representation
Use when different nodes/views naturally live in different local vector spaces and learned transport/restriction maps are task-relevant.

**Do not use** merely because P3 has `GLUE/OBSTRUCTION` vocabulary.

### 1H. Object-centric state
Use when factorization into persistent objects/slots gives compositional/sample-efficiency value.

### 1I. Probabilistic belief state
Bayesian/ensemble/ENN/set-valued state when uncertainty over latent hypotheses is itself task-relevant.

### 1J. Symbolic program / operator library
Use when the relevant state is best expressed as executable symbolic structure rather than continuous geometry.

### 1K. Hybrid explicit + latent state
Explicit typed object graph plus continuous internal embeddings.

Candidate default only **after** simpler representations are tested.

## Axis 2 — what performs computation?

### 2A. MLP / local transition head
A mechanic may be nothing more than a learned transition function over sufficient features.

### 2B. Message passing
Local relational update.

### 2C. Global attention
Long-range interaction / content-addressed aggregation.

### 2D. Matrix-valued local transport
Sheaf/relation-specific maps between local feature spaces.

### 2E. Higher-order incidence propagation
Hypergraph/cell/simplicial computation.

### 2F. Recurrent latent update
Repeated computation on a persistent hidden state; includes Coconut/recurrent reasoning families.

### 2G. Neural algorithmic processor
Execute reusable state-transition algorithms, typically with graph processors and exact hints/traces.

### 2H. Modular network / mixture / router
Select and compose reusable learned modules.

### 2I. Symbolic operator execution + neural perception/parameters
Neuro-symbolic planning / bilevel systems.

### 2J. Program search / synthesis
Explicitly search a compositional program space; DreamCoder/Stitch/LILO lineage.

### 2K. External classical search/planning
Beam/A*/MCTS/dynamic programming over learned structural states.

**Pressure:** if classical search over a good learned state solves the task, do not attribute the gain to a novel neural reasoning core.

### 2L. Energy/constraint optimization
Use learned scores/constraints and solve for a globally coherent state instead of purely feed-forward prediction.

### 2M. Probabilistic inference
Message passing / sampling / variational/Bayesian updates over competing hypotheses.

## Axis 3 — how are reusable mechanics represented?

1. class label / router arm;
2. continuous embedding;
3. neural module;
4. symbolic operator with preconditions/effects;
5. program/library primitive;
6. graph rewrite;
7. partial typed transition with `Read/Write/Pre/Req/Eff/Pres/Fail/Cost/Lineage` projection;
8. region-valued applicability set rather than point estimate;
9. distribution over candidate mechanics;
10. unresolved set of incomparable mechanics.

P9 must not assume item 7 is best merely because it matches ORION theory. It must earn predictive/compositional value over 1–6.

## Axis 4 — how is structure learned?

### 4A. Fully supervised
Gold atom/relation/mechanic labels.

Useful only on exact synthetic/formal worlds or independently adjudicated data.

### 4B. Self-supervised reconstruction
Masked atom/relation/state reconstruction.

### 4C. Contrastive / invariant learning
Same structure under donor/surface perturbation should be close; structural near-miss should remain separate.

### 4D. Transition/effect prediction
Learn `state + mechanic -> post-state`.

### 4E. Program/library compression
Recurring computation becomes reusable abstractions.

### 4F. RL decomposition/composition
Learn latent modules/routing from compound successful traces.

### 4G. Failure-conditioned learning
Train on negative/harmful/UNKNOWN outcomes, not success-only trajectories.

### 4H. Meta-learning
Adapt mechanics/competence to new task families.

### 4I. Continual/selective replay
Update over time while retrieving compatible prior experience.

### 4J. Active inquiry
Choose new observations/computations/experiments based on uncertainty, information gain, counterexamples, value of computation, or dependency/defeater structure.

## Axis 5 — what is the supervision object?

1. final task label only;
2. next action;
3. intermediate algorithmic hint;
4. structural transition;
5. precondition/effect pair;
6. failure mode;
7. invariant preservation;
8. representation map;
9. compatibility/obstruction;
10. uncertainty/UNKNOWN;
11. cost/progress;
12. external verified outcome.

**Key ablation:** richer supervision can itself explain gains. P9 must distinguish a representation advantage from simply giving the model more labels.

## Axis 6 — memory

### 6A. In-weight only
Classical training; no explicit episodes.

### 6B. In-context trajectory
Current episode/history in context.

### 6C. Episodic external memory
Retrieve prior cases/failures.

### 6D. Modular semantic memory
Reusable mechanic/library records.

### 6E. Negative/failure archive
Explicit harmful/null outcomes.

### 6F. Hybrid memory
In-weight generalization + retrieved episodes + stable modules.

Any history benefit must compare against selective replay/modular-memory donors.

## Axis 7 — uncertainty and non-identifiability

1. softmax confidence;
2. ensemble;
3. Bayesian/variational posterior;
4. Epistemic Neural Network;
5. conformal/set-valued prediction;
6. OOD detector;
7. explicit structural `UNKNOWN` due missing coordinate;
8. explicit `OBSTRUCTION` due incompatible known structure;
9. multiple incomparable candidate mechanics/hypotheses.

`UNKNOWN` is only useful if it adds operational value beyond calibrated probabilistic uncertainty.

## Axis 8 — inference strategy

1. one-shot feed-forward;
2. fixed recurrent depth;
3. adaptive recurrent depth;
4. language chain-of-thought;
5. continuous latent thought;
6. explicit structural trajectory;
7. search over mechanics;
8. active test/query selection;
9. planner + verifier loop;
10. mixed strategy selected by value-of-computation.

Inference resource must be recorded so extra serial compute cannot masquerade as a representation gain.

## Axis 9 — symmetry / invariance

1. surface-name permutation;
2. symbol/color permutation;
3. graph isomorphism;
4. donor implementation substitution;
5. coordinate/unit transform;
6. representation-chart transform;
7. domain vocabulary change;
8. semantically irrelevant nuisance transformation.

Where a symmetry is known exactly, compare architectural equivariance to data augmentation and learned invariance.

## Axis 10 — what counts as generalization?

1. IID holdout;
2. surface randomization;
3. donor/implementation holdout;
4. graph/problem size OOD;
5. whole-domain holdout;
6. combinatorial holdout;
7. hidden-precondition near-miss;
8. failure-conditioned recovery;
9. representation-change transfer;
10. fresh task after continual learning;
11. P10 application with frozen P9 weights.

No P9 paper claim should rest primarily on IID accuracy.

## Axis 11 — evaluation outcome

### Representation outcomes
- exact view identifiability;
- false merge/split;
- mapping/cycle error;
- obstruction/UNKNOWN correctness.

### Mechanic outcomes
- applicability calibration;
- effect/post-state prediction;
- invalid composition;
- invariant violation;
- repeated dead end.

### Generalization outcomes
- held-out domain/composition/donor success;
- size extrapolation;
- surface/symbol robustness.

### Problem-solving outcomes
- externally verified task success;
- cost/compute/tool use;
- failure recovery;
- harmful transition rate.

### Inquiry outcomes
- verified progress per acquisition cost;
- decision-relevant evidence gain;
- false closure rate.

### Authority outcome
Always external. P9 output never directly upgrades scientific/adoption authority.

## Axis 12 — non-neural baselines

Mandatory where applicable:

- rule-based exact ORION state machine;
- logistic regression / linear model;
- random forest / gradient boosting;
- nearest neighbor / case-based reasoning;
- symbolic planning/search;
- program enumeration/compression;
- Bayesian inference / experimental design.

A neural paper is scientifically weak if a simple non-neural baseline explains the effect.

# Search-space reduction logic

The search should be **sequentially eliminative**, not combinatorial architecture search.

1. Freeze an atomic discriminator.
2. Find the simplest representation/computation family that can identify the target.
3. Train the strongest reasonable version of that family.
4. Add exactly one richer structural assumption.
5. Keep it only if it adds protected value under matched information/resources.
6. Retain the defeated model and its failure case as a permanent baseline/hostile fixture.
7. Move to the next atom.

Only after several atoms survive separately should P9 test a combined model.

# Current first build

PR #473 implements only the evaluator layer needed by this search:

- exact typed worlds;
- restricted model views;
- relation-semantics hostile pair;
- local-transport GLUE/OBSTRUCTION pair;
- negative-history pair;
- deterministic surface permutation;
- exact view-identifiability analysis.

No model family is promoted by this file.
