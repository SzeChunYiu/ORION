# FiberGuard: Exact Representation Audits and Cost-Aware Refinement for Combinatorial Optimization

**R9 research manuscript — 2026-08-26**

## Abstract

A learned or hand-designed optimizer can be computationally powerful and still fail because its input representation identifies instances with different exact answers. We develop **FiberGuard**, an exact audit for this failure mode. For a representation `Phi:X->Y` and scalar target `T`, the diameter of `T` inside a fibre `Phi^{-1}(y)` is the precise worst-case ambiguity hidden from every representation-only method. The deterministic and randomized minimax absolute radius is half the diameter; the squared-loss radius is one quarter of its square; and every exactly valid uncertainty interval has width at least the diameter. A Boolean optimizer property that takes both values in one fibre has randomized worst-case classification error at least one half. These are information limits, not computational-hardness results.

The main algorithmic extension is a cost-aware refinement theorem. A finite family of additional features induces a refinement lattice over each current fibre. At a fibre `F`, a robust system may answer, acquire a refinement, or abstain. Under worst-case absolute loss and additive acquisition cost, the exact optimal value satisfies a Bellman recursion: answering costs half the target diameter, a refinement costs its acquisition price plus the worst optimal child value, and abstention costs its declared penalty. The recursion yields a proof-carrying `answer/refine/abstain` policy and exposes refinements whose cost exceeds their maximum possible reduction in information radius.

We instantiate the audit in an exact Pauli-string partition model. For every `m>=5`, unary optimality is decided by clauses involving at most four term indices. Nevertheless, scalable pairs with identical ordered weights and complete labeled pair-gain matrices have improvements `12t-2` and `10t-1` and opposite optimal-block structure. A second construction agrees on all labeled common-factor counts through order `m-2` while its exact value gap grows linearly in a padding parameter; Möbius inversion identifies the unique invisible integer direction. A registered multi-domain atlas, now reproduced by a structurally independent generator and exact target solvers, provides exact fibre certificates, endpoint witnesses, and refinement outcomes across 230,378 instances. The replay is internal independent corroboration rather than external replication.

FiberGuard is intended as a safety layer for learned combinatorial optimization, surrogate solvers, compiler triage, selective prediction, and benchmark design. It does not claim that exact collisions are frequent in production. The remaining promotion gate is to measure collision or near-collision prevalence, acquisition cost, and decision value on larger and production-derived domains.

## 1. Representation failure is not solver failure

Combinatorial optimizers are increasingly paired with compressed feature maps, graph encodings, learned embeddings, low-order statistics, and surrogate targets. Performance is normally evaluated as a property of the estimator or search procedure. A different failure occurs before computation begins: the representation may map two exact instances to the same input even though the target values or optimizer structures differ.

No increase in model capacity can recover a distinction that is absent from the input. The correct object is therefore not only an algorithm `g`, but the triple

`(instance family X, representation Phi, target query T)`.

A representation can be sufficient for one query and insufficient for another. In the Pauli partition model below, complete pair information exactly decides whether the unary partition is optimal for all sufficiently large instances, yet it does not determine the improvement value or whether an exact optimum contains a triple block.

FiberGuard has three layers:

1. **audit:** find or bound target diameter inside representation fibres;
2. **certificate:** publish endpoint instances, feature equality, and exact target values;
3. **action:** answer when the radius is tolerable, acquire a costed refinement when valuable, or abstain.

The framework separates deterministic exact coverage from statistical calibration. A fibre interval is a worst-case validity statement; it does not claim a probability model.

## 2. Fibres and exact information radius

Let `X` be an instance set, `Phi:X->Y` a representation, and `T:X->R` a bounded target on every nonempty fibre. For `y in Phi(X)`, define

`F_y={x:Phi(x)=y}`,

`a_y=inf_{x in F_y}T(x)`, `b_y=sup_{x in F_y}T(x)`, and `d_y=b_y-a_y`.

### Theorem 1 — exact scalar sufficiency

There exists a function `g:Y->R` satisfying `g(Phi(x))=T(x)` for every `x` if and only if every fibre has diameter zero.

Thus sufficiency is exactly the statement that the target factors through the representation.

### Theorem 2 — deterministic minimax radius

For every fibre,

`inf_z sup_{x in F_y}|z-T(x)|=d_y/2`.

A midpoint of the target range attains the value. Globally,

`inf_g sup_x |g(Phi(x))-T(x)| = (1/2) sup_y d_y`.

### Corollary 3 — integer targets

When `T` and the estimate are integer-valued, the exact radius is `ceil(d_y/2)`.

### Theorem 4 — randomization does not improve worst expected absolute loss

For any random variable `Z_y` chosen from the representation alone,

`inf_{Z_y} sup_{x in F_y} E|Z_y-T(x)|=d_y/2`.

The pointwise inequality

`|z-a_y|+|z-b_y|>=d_y`

survives expectation, and the deterministic midpoint is optimal.

### Theorem 5 — squared-loss radius

Under squared loss,

`inf_{Z_y} sup_{x in F_y} E[(Z_y-T(x))^2]=d_y^2/4`.

### Theorem 6 — exact uncertainty width

Every interval rule with exact coverage of all members of a fibre has width at least `d_y`. The endpoint interval `[a_y,b_y]` is optimal.

### Theorem 7 — optimizer-property barrier

Let `P:X->{0,1}` be a well-defined optimizer property. If one fibre contains instances with opposite values of `P`, every representation-only randomized classifier has worst-case error at least `1/2` on that fibre.

These theorems are exact optimal-recovery statements. The paper-specific work is constructing nontrivial exact fibres inside optimization families and solving their endpoints.

## 3. Data processing and approximate collisions

### Theorem 8 — deterministic coarsening cannot help

If `Psi=h o Phi`, every `Psi` fibre is a union of `Phi` fibres, so

`sup_z diam T(Psi^{-1}(z)) >= sup_y diam T(Phi^{-1}(y))`.

Consequently, the exact absolute, integer, squared, and interval radii cannot improve under deterministic feature coarsening.

### Theorem 9 — Lipschitz near-collision law

Let the feature space be metric and restrict the estimator to be `L`-Lipschitz. If

`dist(Phi(x),Phi(x'))<=epsilon`

and `Delta=|T(x)-T(x')|`, then

`max(error(x),error(x')) >= (Delta-L epsilon)_+/2`.

The analogous squared-error lower bound is `(Delta-L epsilon)_+^2/4`.

The theorem supports graded benchmark pairs when floating-point pipelines contain near-collisions rather than exact duplicate feature vectors. Its scope depends on a measured or certified Lipschitz constant.

## 4. Cost-aware representation refinement

An impossibility certificate is useful only if it changes the system's behavior. We therefore add a finite refinement model.

Let `F subseteq X` be the current fibre. A refinement action `r` has acquisition cost `c(r,F)>=0` and partitions `F` into nonempty child fibres `Child(r,F)`. The target remains `T`. The system may:

1. **answer** with one scalar;
2. **refine** by acquiring `r`; or
3. **abstain** at declared penalty `A(F)>=0`.

Assume a finite acyclic refinement family: every refinement strictly separates at least one pair, and only finitely many feature sets are available.

### Theorem 10 — exact robust refinement recursion

Define `V(F)` as the minimum worst-case total loss from fibre `F`, with absolute prediction loss and additive feature-acquisition cost. Then

`V(F)=min{ diam_T(F)/2, A(F), min_r [c(r,F)+max_{G in Child(r,F)}V(G)] }`.

A policy selecting an attaining action at each reachable fibre is minimax optimal.

**Proof.** If the system answers immediately, Theorem 2 gives exact cost `diam_T(F)/2`. Abstention has declared cost `A(F)`. If it refines, it pays `c(r,F)` before learning which child contains the hidden instance, after which the adversary selects the child with largest continuation value. No other information is revealed. Acyclicity permits backward induction from terminal fibres. Every policy begins with one of the three action classes, so the lower and upper recursions coincide. ∎

### Corollary 11 — zero-value refinements

A refinement `r` is dominated at `F` when

`c(r,F) >= diam_T(F)/2 - max_G V(G)`.

In particular, a positive-cost refinement that leaves every relevant target diameter unchanged cannot be optimal unless all immediate alternatives cost at least as much.

### Corollary 12 — exact decision certificates

A FiberGuard policy can return one of:

- `ANSWER(value, radius, endpoint certificates)`;
- `REFINE(feature, acquisition cost, child certificate digests)`; or
- `ABSTAIN(penalty, unresolved diameter certificate)`.

This makes the representation audit executable and reviewable. Computing every fibre or optimal refinement may itself be difficult; Section 8 treats scaling as an explicit evidence gate.

## 5. Pauli-string partition model

An instance is an ordered tuple of nonidentity Pauli strings. A partition groups terms into blocks and extracts common Pauli factors. The fixed structural objective is the one declared in the accompanying source package; it is a mathematical model motivated by block-wise Pauli compilation, not a physical fault-tolerant resource formula.

For each pair define the labeled pair gain

`g_ij = 4 f({i,j})-(w_i+w_j)`,

where `w_i` is term weight and `f(S)` counts columns carrying one common nonidentity Pauli across every term in `S`.

### Theorem 13 — four-index unary-optimality certificate

For every `m>=5`, the unary partition is globally optimal exactly when:

1. `g_ij<=0` for every pair; and
2. `g_ij+g_kl+1<=0` for every two disjoint pairs.

The largest clause touches four indices. A four-term exact counterexample satisfies both clause families while a one-block partition is cheaper, so the threshold is sharp.

The theorem demonstrates query-specific sufficiency: low-order information completely resolves the unary-optimality decision on the stated range.

## 6. Complete pair information misses value and structure

Two five-term Pauli gadgets have identical ordered weights and complete labeled pair-gain matrices. Taking `t` disjoint copies produces instances `A_t` and `B_t` with exact improvements

`Delta_A(t)=12t-2`,

`Delta_B(t)=10t-1`.

Every optimum of `A_t` contains a distinguished triple block in every gadget, while every optimum of `B_t` uses only pairs and singletons.

### Corollary 14 — exact pair-representation limits

The pair representation has fibre diameter `2t-1`, hence:

- exact real and randomized absolute radius `(2t-1)/2`;
- exact integer radius `t`;
- exact squared radius `(2t-1)^2/4`;
- exact interval-width floor `2t-1`;
- structural-classification error at least `1/2`; and
- no uniform symmetric multiplicative factor below `sqrt(6/5)` on the family.

The obstruction is information loss, not computational hardness.

## 7. Proper interactions still miss exact value

For every `m>=5` and `L>=1`, a parity construction agrees on ordered weights and every labeled common-factor count through order `m-2`, yet the exact improvements differ by

`[m(ceil(log2 m)+1)-1]L`.

For fixed `m`, the ambiguity is unbounded in `L`.

### Theorem 15 — proper-marginal kernel

Represent a trade column by a subset of `q=m-1` variable terms and let `delta` be the signed multiplicity difference. If every proper upper marginal vanishes, then

`delta(S)=(-1)^{q-|S|}c`.

Thus the only nonzero integer direction invisible to all proper labeled marginals is the dense parity direction. A primitive trade uses every Boolean cell and has mass at least `2^{m-2}` on each side. This proves minimality of the difference trade, not of the common padding used to force the desired optimum.

## 8. Exact atlas and clean-room replay

The R8 package registers three exact optimization domains, their representations, target solvers, fibre summaries, endpoint witnesses, and refinement outcomes. A structurally independent replay uses:

- an independently encoded finite graph/instance atlas;
- a coverage-state breadth-first solver for the set-cover target;
- a DPLL-style exact model counter for the 2-SAT target; and
- independent feature serialization and fibre aggregation.

The replay reproduces every registered count, maximum fibre, endpoint witness, and refinement outcome across 230,378 instances. The clean-room source and result receipts are bound separately from the reference implementation. This is internal structural independence, not external institutional replication.

The atlas establishes correctness of the exact certificate pipeline. It does not establish prevalence in production. The R9 harness therefore measures:

1. collision and near-collision multiplicity as instance scale grows;
2. the cost of each refinement feature;
3. answer/refine/abstain performance under Theorem 10;
4. exact-target solver cost;
5. negative regimes where the full representation is cheaper; and
6. transfer to a production-derived compiler or comparably exact domain.

## 9. Applications

### 9.1 Learned combinatorial optimization

Before training a surrogate, an exact subset of the domain can be partitioned by the proposed input representation. Nonzero target diameter proves an architecture-independent worst-case floor. The remedy is to enrich the representation, narrow the target query, widen uncertainty, or abstain.

### 9.2 Certified selective prediction

Theorem 10 supplies an exact robust policy when feature costs and a finite refinement lattice are declared. A system can answer cheap decision queries at low order and route value/structure queries to richer exact features.

### 9.3 Adversarial benchmark design

Exact collisions and certified near-collisions test whether a benchmark has hidden representation failure. Endpoint certificates prevent a high-capacity model from being credited for distinctions absent from its input.

### 9.4 Compiler triage

The four-index theorem is a cheap exact gate for unary optimality. Failing instances can be refined or sent to a complete optimizer. The theorem does not claim a runtime benefit until feature and solver costs are measured.

### 9.5 Uncertainty and abstention

A fibre interval is the narrowest interval justified by the representation alone. Any narrower exact interval requires additional information. Statistical coverage can be layered on top, but it is a separate claim.

## 10. Prior-art and novelty boundary

Worst-case optimal recovery, two-point minimax arguments, sufficient statistics, data processing, selective prediction, active feature acquisition, Markov bases, hierarchical-model fibres, and Möbius inversion are established. The paper does not claim those generic ideas as new.

The residual contribution is the exact conjunction:

1. a scalable optimization family where one low-order representation is complete for a global decision;
2. exact fibres showing unbounded value ambiguity and opposite optimizer structure under the same representation;
3. a dense unique proper-marginal kernel;
4. a proof-carrying audit implementation; and
5. a cost-aware refinement layer connected to exact endpoint certificates.

A current primary-source matrix is a release gate.

## 11. Limitations

- All theorem transfers are scoped to the declared representation and target query.
- The Pauli objective is structural rather than a physical quantum-resource model.
- Exact fibres may be expensive to enumerate.
- The registered atlas and replay do not establish real-world prevalence.
- Near-collision bounds require a metric and a Lipschitz restriction.
- Worst-case exact intervals are not probabilistic calibration intervals.
- The refinement recursion assumes a finite acyclic feature family and declared costs.

## 12. Conclusion

A representation should not be called sufficient or insufficient without naming the query. Fibre diameter gives an exact answer for scalar targets; opposite properties in one fibre give an exact answer for structural prediction. FiberGuard converts those facts into endpoint certificates and an optimal robust choice among answering, refining, and abstaining.

The remaining question is operational rather than definitional: at what scale and acquisition cost do exact representation audits change decisions on production-derived optimization families? The R9 harness treats that question as a frozen experiment, not as a conclusion already implied by the mathematics.

## Tool-use disclosure

A generative language model assisted organization, language revision, theorem exploration, and executable research planning. The author is responsible for all proofs, code, data, citations, and final claims.
