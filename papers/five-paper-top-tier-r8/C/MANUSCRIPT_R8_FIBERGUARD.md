# FiberGuard: Exact Representation Audits for Learned Combinatorial Optimization

## Abstract

A learned optimizer can fail for two different reasons: its model may be inadequate, or its input representation may map instances with different exact answers to the same feature vector. The second failure cannot be repaired by more training or model capacity while the representation is fixed. We develop **FiberGuard**, an exact audit that partitions a finite combinatorial instance space into representation fibres, solves the target exactly on every instance, emits maximum-diameter collisions, and evaluates proposed feature refinements over the complete panel.

The general radius-of-information statement is elementary: for a scalar target, the exact worst-case error of every representation-only predictor is one half of the largest target diameter within a fibre; randomization does not improve worst expected absolute loss, and any exact uncertainty interval must span the fibre diameter. The scientific contribution is an exact multi-domain realization. We exhaust all 32,768 labeled six-vertex graphs for chromatic number, all 155,106 covering five-set families over a five-element universe for minimum cover size, and all 42,504 five-clause 2-CNF formulas on four variables for satisfying-assignment count. Each target is checked by two exact procedures.

The frozen low-order representations have maximum target diameters 1, 1, and 4, respectively. For every domain we publish endpoint witnesses and evaluate candidate refinements. A collision-guided feature removes all ambiguity on the declared panel, while a matched plausible baseline leaves ambiguity: four-cycle count versus connected-component count for graph colouring, pairwise-union multiset versus element-frequency multiset for set cover, and labeled signed pair profiles versus global clause-sign counts for 2-CNF. These are exact finite representation audits, not computational-hardness or real-distribution claims. They provide a reproducible safety test for feature maps used by surrogate optimizers, learned branching policies, and algorithm-selection systems.

## 1. Introduction

Machine learning is increasingly used inside combinatorial optimization: to select branch-and-bound variables, predict objective values, prioritize constraints, choose algorithms, or propose complete solutions. Evaluation usually combines a trained model, an instance distribution, and aggregate prediction or runtime metrics. That protocol can conceal a more basic defect. If two exact instances have the same model input but different targets, then no downstream architecture receiving only that input can be exact on both.

This paper treats representation adequacy as a first-class object. Let `Phi(x)` be the exact input available to a model and `T(x)` the exact query of interest. The relevant object is not an average feature importance score. It is the fibre

`F_y={x: Phi(x)=y}`

and the range of `T` inside that fibre.

The approach is query-specific. A representation can decide whether a baseline is optimal while failing to determine the improvement value, uncertainty width, or optimizer structure. Conversely, a feature map can be sufficient on one finite domain and insufficient after scaling. FiberGuard therefore reports the exact domain, target, representation, solver, collision multiplicity, and authority boundary.

### Contributions

1. An exact deterministic and randomized fibre-radius theorem for scalar targets, with integer, squared-loss, interval, and structural-classification consequences.
2. A complete collision-audit protocol with independent target checks and content-bound witnesses.
3. Three exhaustive combinatorial domains: graph colouring, set cover, and 2-CNF model counting.
4. A frozen candidate-feature experiment showing how exact collisions can guide representation repair and how plausible baseline features can fail to close the same fibres.
5. A deployment contract for learned optimization: enrich, abstain, or widen uncertainty when the representation has unresolved target diameter.

## 2. Representation fibres and exact information radius

Let `X` be a finite instance set, `Phi:X->Y` a representation, and `T:X->R` a scalar target. For `y in Phi(X)`, define

`a_y=min_{x in F_y} T(x)`, `b_y=max_{x in F_y}T(x)`, and `d_y=b_y-a_y`.

### Theorem 1 — exact absolute radius

For every fibre,

`inf_z max_{x in F_y}|z-T(x)|=d_y/2`.

The midpoint `(a_y+b_y)/2` is optimal. Hence the global representation-only minimax radius is `(1/2) max_y d_y`.

**Proof.** Any common estimate must approximate both endpoints. The sum of its endpoint errors is at least `d_y`, so one is at least `d_y/2`. The midpoint attains that radius for every value between the endpoints. ∎

### Corollaries

- Integer-valued output has exact radius `ceil(d_y/2)`.
- Randomization cannot reduce worst expected absolute loss: take expectations in the endpoint triangle inequality.
- Worst squared-loss radius is `d_y^2/4`.
- Every exactly covering interval has width at least `d_y`, attained by `[a_y,b_y]`.
- If a Boolean optimizer property differs in one fibre, every randomized representation-only classifier has worst-case error at least `1/2`.
- If `Psi=h o Phi` is a deterministic coarsening, its maximum fibre diameter cannot be smaller.

These statements are information bounds, not time-complexity bounds.

## 3. FiberGuard audit protocol

A valid exact audit binds:

1. a finite instance generator and exact count;
2. a canonical representation function;
3. an exact target definition;
4. two structurally different target solvers;
5. a fibre map and endpoint-witness serializer;
6. candidate refinements frozen before their aggregate outcomes are inspected;
7. a matched baseline-selection rule;
8. a machine-readable result with content digest; and
9. a statement of what the finite panel cannot establish.

The first target solver is allowed to exploit domain structure. The second must use a different search order or mathematical formulation. Agreement is checked instance by instance. A target mismatch aborts the audit.

A refinement is evaluated by appending one candidate feature to the original representation and recomputing every fibre. FiberGuard reports refined fibre count, ambiguous fibre count, and maximum remaining diameter. A feature “closes” a panel only when every refined fibre has diameter zero. This does not prove sufficiency outside the frozen panel.

## 4. Domain I: graph colouring

### 4.1 Exact domain

The domain contains every labeled simple graph on six vertices. There are `2^15=32,768` instances.

The original representation is:

- sorted vertex-degree sequence; and
- triangle count.

The target is chromatic number.

One exact solver enumerates colour assignments by increasing palette size. The second uses an independent subset/independent-set cover recursion. Their answers agree on all graphs.

### 4.2 Exact collision

The representation forms 136 fibres. The largest chromatic-number diameter is one. A maximum fibre contains 720 graphs and includes graphs with chromatic numbers three and four. The artifact records edge masks 6011 and 6014 as endpoint witnesses and rechecks them independently.

### 4.3 Frozen refinements

The candidate features are clique number, connected-component count, and four-cycle count. Four-cycle count was selected by inspecting the structural difference between registered endpoint collisions, while connected-component count is the matched plausible baseline.

Appending four-cycle count produces 146 refined fibres and zero ambiguous fibres. Appending component count produces 137 fibres but leaves five ambiguous fibres with diameter one. Clique number leaves two ambiguous fibres.

The result says that four-cycle count is sufficient on all six-vertex graphs relative to the original representation and chromatic-number query. It does not claim sufficiency for larger graphs.

## 5. Domain II: set cover

### 5.1 Exact domain

Let the universe have five labeled elements. An instance is a five-set subfamily of the 31 nonempty subsets whose union covers the universe. The domain has 155,106 instances.

The original representation is:

- multiset of the five set sizes; and
- multiset of all ten pairwise intersection sizes.

The target is minimum cover size.

One solver searches subsets of the five sets by cardinality. The second uses an independent dynamic program over covered-universe masks. Every answer agrees.

### 5.2 Exact collision

The representation forms 909 fibres. The maximum minimum-cover-size diameter is one. A 1,740-member maximum fibre contains values two and three. Endpoint set-mask families are `[1,3,5,14,26]` and `[1,3,12,21,22]`.

### 5.3 Frozen refinements

Candidate features are element-frequency multiset, pairwise-union multiset, and triple-intersection multiset. The collision-guided pairwise-union feature closes all declared fibres, yielding 1,511 refined fibres. Element frequencies leave 58 ambiguous fibres, as does the triple-intersection candidate.

This is a precise warning against assuming that local incidence frequencies replace relational union information for the exact cover-value query.

## 6. Domain III: 2-CNF model counting

### 6.1 Exact domain

Use four labeled Boolean variables and the 24 non-tautological binary clauses. An instance is a five-clause subset, giving 42,504 formulas.

The original representation is:

- positive and negative occurrence counts for each variable; and
- labeled variable-pair co-occurrence counts, ignoring literal signs within the pair.

The target is the number of satisfying assignments.

One solver enumerates the 16 truth assignments. The second uses a separate clause-state recursion with memoization. They agree on every formula.

### 6.2 Exact collision

The representation creates 13,032 fibres. The maximum target diameter is four. An 11-formula fibre contains an unsatisfiable formula and a formula with four satisfying assignments. The exact clauses of both endpoints are stored in the result record.

### 6.3 Frozen refinements

Candidate features are global clause-sign-type counts, an unlabeled multiset of signed pair profiles, and the full labeled variable-pair signed profile. The full labeled profile closes all 42,504 instances. Global sign-type counts leave 5,888 ambiguous fibres with diameter four; the unlabeled signed-profile multiset improves the diameter to two but leaves 2,468 ambiguous fibres.

The result isolates the lost information: sign structure must remain bound to the labeled variable pair for exact model count on this panel.

## 7. Using collisions to repair representations

A collision is not only a lower-bound witness. It is a controlled design object.

Given endpoint instances with the same `Phi` and different `T`:

1. compute structurally meaningful candidate distinctions;
2. freeze a candidate set and a baseline-selection rule;
3. append each candidate to every instance, not only the endpoints;
4. recompute the complete fibre diameter; and
5. retain the smallest or cheapest feature that achieves the required target radius.

The three R8 panels show that an endpoint-inspired feature can close the complete finite panel while a plausible aggregate baseline does not. The correct conclusion is panel-specific sufficiency. Scaling must be tested in a successor freeze.

## 8. Implications for learned optimization

### 8.1 Surrogate objective prediction

If a model receives only `Phi`, the fibre radius is an architecture-independent worst-case error floor. More samples or parameters cannot distinguish identical inputs. A production system should detect known ambiguous fibres and either enrich the input, return the exact interval `[a_y,b_y]`, or abstain.

### 8.2 Learned branching and algorithm selection

The target need not be an objective value. It can be the best branching action, whether every optimum has a structural property, or which solver wins. Opposite labels in one fibre force classification error. An exact candidate set can replace an overconfident single action.

### 8.3 Benchmark construction

Training/test suites should include exact collisions and near-collisions. Random splits can miss them, especially when the feature map groups rare but structurally important instances. Collision multiplicity, target diameter, and train/test leakage should be reported.

### 8.4 Query-specific representations

The same representation may be exact for a decision query and inadequate for a value query. “Sufficient representation” is incomplete language unless the domain and target are named.

## 9. Relation to prior work

Radii of information, two-point minimax bounds, sufficient statistics, invariant-representation tradeoffs, and graph-representation expressivity are established. Learned combinatorial optimization already uses graph, variable-constraint, and clause representations. FiberGuard does not claim those ideas.

The residual contribution is the exact audit object: complete finite domains across three different combinatorial structures, independently checked exact targets, maximum-diameter collision witnesses, and whole-panel representation-refinement experiments. The final bibliography must compare the theorem and benchmark with optimal recovery, invariant representation learning, Weisfeiler–Leman/GNN expressivity, learned branch-and-bound, and SAT representation learning.

## 10. Reproducibility and limitations

The reference artifact is deterministic and emits a content hash. It enumerates 230,378 instances in total. The finite results are exact for the declared generators.

Limitations are substantive:

- panel closure does not imply all-size sufficiency;
- exact collision prevalence on a uniform finite census is not prevalence in production data;
- the selected candidate features may be expensive or equivalent to nearly complete instance recovery;
- the benchmark does not train or compare neural architectures;
- no runtime improvement follows merely from feature sufficiency; and
- a richer model input is outside the lower bound.

The next external gate is a clean-room replay plus a scaling experiment on at least one domain.

## 11. Conclusion

A representation is a scientific assumption. FiberGuard makes that assumption falsifiable before model training: solve the frozen domain exactly, compute target diameters inside feature fibres, publish the hardest collisions, and test repairs over the whole panel.

Across graph colouring, set cover, and 2-CNF model counting, ordinary low-order summaries collapse instances with different exact answers. Collision-guided refinements close the declared panels while matched aggregate baselines do not. The result is a practical exact safety layer for learned combinatorial optimization, with explicit boundaries between finite representation sufficiency, model performance, and computational hardness.

## Tool-use disclosure

A generative language model assisted manuscript organization, code generation, and language revision. The author remains responsible for every theorem, implementation, source, and claim.
