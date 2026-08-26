# FiberGuard: Exact Representation Certificates and Their Failure at the Inductive Boundary

## Abstract

A learned or heuristic optimizer acts through a representation. If two exact states share that representation, every representation-only policy must treat them identically even when their targets, optimal actions, or downstream costs differ. FiberGuard turns this elementary observation into a proof-carrying finite theory of representation authority.

For complete finite fibres, we derive exact target diameter, deterministic and randomized action regret, epsilon-safe action sets, constant-size worst-fibre witnesses, minimal action-conflict hyperedges, and minimum-cost static repair. For sequential feature acquisition, state-dependent costs require complete statewise loss profiles; componentwise Pareto pruning is exact, while a scalar Bellman recursion is universally valid exactly when each reached observation cell has one acquisition charge. Randomized adaptive policies form a finite convex-profile game with small mixed-tree upper certificates and adversarial-prior Bayes-tree lower certificates. A final route layer separates learned-action calibration from fallback alignment, pre-acquisition routing from post-acquisition abstention, and source calibration from transfer under a registered relative-loss drift margin.

The experiments deliberately include both positive and adverse terminals. An exact three-domain census contains 230,378 finite instances. A complete seven-vertex graph atlas shows that a repair successful at six vertices need not transfer. On pinned ASlib SAT12-ALL, exhaustive same-corpus evaluation selects two feature steps with robust total excess 1712, versus 12000 with no features and 16906.55 with all feature steps. Prospectively frozen held-out tests then refute the inductive interpretation: exact numeric equality recurs on only 3.22% of official-CV test instances and 5.08% under family shift, and its decision rule is strongly dominated by a same-information nearest-neighbor baseline. A later cross-scenario study shows that marginal learned-action calibration can coexist with harmful fallback alignment and can reverse sign across scenarios.

The resulting conclusion is not that exact fibres solve inductive algorithm selection. It is sharper: exact fibres are exact closed-world certificates, and every move beyond that boundary requires an independently named authority premise—completeness, a valid structural extension law, or an explicitly statistical guarantee that includes both the deployed and fallback actions. The paper therefore provides exact certificates, impossibility results, hostile controls, and a map of which claims survive each evidence regime.

## 1. Introduction

Algorithm selection, learned branching, solver routing, and cost-aware feature acquisition all ask a common question: what decisions are justified by the information actually available to the policy? Conventional evaluation answers distributionally, through average loss, held-out accuracy, or selective risk. Those quantities are important, but they do not expose the strongest finite obstruction. If a frozen representation maps two exact states to the same value, a deterministic representation-only policy must choose one common action on both states. No amount of training can distinguish states that the policy is not allowed to distinguish.

That observation is often used informally as a collision example. FiberGuard develops it into a complete finite certificate language. The representation fibre—not a confidence score, model class, or training procedure—is the authority-bearing object. On a complete fibre, one can compute the exact attainable target interval, exact minimax action regret, exact safe action set, and exact witness showing why a requested tolerance is impossible. Refinement then becomes an explicit finite decision problem: which additional features separate every critical conflict, what do they cost, and when should they be acquired adaptively?

The central difficulty is that certificate authority changes when the problem changes. A complete finite corpus supports exact transductive fibre claims. It does not support an unseen-state upper bound merely because an unseen state shares a numeric signature. A statistical interval can support marginal held-out claims, but not a deterministic worst-fibre statement. A learned-action certificate can be valid while routing is harmful because the fallback is worse exactly on the rejected states. A post-acquisition rejector cannot refund feature cost already paid. A source-scenario route certificate cannot be carried to a target scenario without a bridge and a drift margin.

This paper makes those boundaries load-bearing rather than relegating them to limitations. Its positive same-corpus result and its prospective inductive refutations are parts of one story: exact certificates are strong precisely because their authority is narrow and explicit.

### 1.1 Contributions

The paper makes seven scoped contributions.

**[C19-T1] Complete-fibre decision quantities.** For a frozen finite representation, FiberGuard gives exact target diameter, deterministic minimax action regret, randomized worst-state expected regret, and epsilon-safe action sets. These are model-independent quantities owned by the representation and the declared action-cost matrix.

**[C19-T2] Small finite certificates.** A deterministic worst-fibre value is witnessed by at most the action count, and every minimal unsafe action conflict has size at most the action count. Large corpora can therefore admit small exact adverse receipts.

**[C19-T3] Exact static repair.** Target-identifying and action-safe static feature selection reduce exactly to weighted covering problems over representation-induced conflicts. Classical set-cover algorithms and hardness are donor-owned; the new object is the exact conflict family induced by the frozen representation and decision tolerance.

**[C19-T4] State-dependent adaptive acquisition.** Exact adaptive value is represented by recursively achievable statewise loss profiles. Componentwise dominated profiles may be pruned at every child. A scalar acquisition charge is universally sufficient exactly when the charge is constant within each reached observation cell.

**[C19-T5] Randomized adaptive receipts.** Randomized adaptive value is the minimax value over the convex hull of deterministic policy profiles. Some optimum mixes at most the fibre size many deterministic trees. A matching adversarial prior and Bayes decision-tree trace give an exact lower certificate. Expected-loss improvement is kept distinct from pathwise or tail safety.

**[C19-T6] The inductive authority boundary.** Finite training fibres do not constrain unseen same-signature states without completeness, a structural extension law, or a statistical authority class. We prove the extension impossibility, give a valid Lipschitz escape hatch, and prospectively demonstrate the failure of exact-equality induction.

**[C19-T7] Paired route authority.** Safe routing requires paired learned and fallback evidence, direct relative-loss sign separation, correct acquisition timing, route measurability from pre-acquisition information, and a sign margin under transfer drift.

### 1.2 Evidence contributions

The empirical evidence is intentionally nonmonotone.

**[C19-E1]** The registered R8 census exhausts 230,378 finite instances across graph coloring, set cover, and 2-SAT, with two exact target formulations per instance and preserved refinement successes and failures.

**[C19-E2]** The complete seven-vertex graph atlas refutes transfer of one six-vertex repair while exhibiting stronger target-sufficient refinements.

**[C19-E3]** On pinned ASlib SAT12-ALL, the exact same-corpus static objective selects `Pre + lobjois` with robust total excess 1712, versus 12000 without features and 16906.55 with all feature steps.

**[C19-E4]** A prospectively frozen held-out study refutes exact numeric equality as an inductive selector: recurrence is low and decision loss is poor.

**[C19-E5]** A prospectively frozen coarsening improves mean behavior but does not earn the declared robust transfer terminal.

**[C19-E6]** Across a frozen SAT16, SAT18, and SAT20 sequence, marginal learned-action calibration does not imply selective routing value; fallback-minus-learned loss on rejected states changes sign across scenarios.

**[C19-E7]** Independent finite implementations within the programme corroborate the profile, randomization, conflict, alignment, timing, and transfer identities while preserving external authority as open.

## 2. Finite representation authority

Let `X` be a nonempty finite state space, `Phi:X->Y` a frozen representation, and `F_y={x:Phi(x)=y}` an attained fibre. Let `t:X->R` be an exact scalar target and `A` a finite action set with declared finite cost `C(a,x)`. Define the statewise oracle

`C*(x)=min_(a in A) C(a,x)`

and regret

`R(a,x)=C(a,x)-C*(x)`.

Every quantity in one additive decision objective must use one frozen unit and one common statewise oracle baseline. Time, node count, memory, and prediction error cannot be added merely because they are numbers. Timeouts and crashes require a frozen finite convention or a separate resource-incomparable terminal.

### 2.1 Target fibres

The target diameter of a fibre is

`diam_t(F)=max_(x in F)t(x)-min_(x in F)t(x)`.

For absolute-error estimation, the minimax constant estimate is the interval midpoint and the minimax error is half the diameter. Exact target identifiability is equivalent to zero diameter on every attained fibre. This is a deterministic information statement, not a claim about the probability of encountering the fibre.

### 2.2 Deterministic action regret

A deterministic representation-only policy must choose one action for the entire fibre. Its exact value is

`rho_det(F)=min_(a in A) max_(x in F) R(a,x)`.

The global representation value is the maximum over attained fibres. For tolerance `epsilon`, define

`Safe_epsilon(F)={a:max_(x in F)R(a,x)<=epsilon}`.

The set is nonempty exactly when `rho_det(F)<=epsilon`. FiberGuard can therefore return a certified action set instead of only an uncertainty scalar.

### 2.3 Randomized expected regret

A randomized representation-only policy declares a distribution `p` over actions. Under worst-state expected-loss semantics,

`rho_rand(F)=min_(p in Delta(A)) max_(x in F) sum_a p_a R(a,x)`.

This is a finite zero-sum game and a linear program. The adversary sees the declared distribution but not the private action draw before choosing the state. The result is not a pathwise or tail guarantee. If the adversary may choose after observing the draw, mixing cannot improve the deterministic value.

### 2.4 Small worst-fibre witnesses

For each action, choose one state attaining that action's maximum regret on the fibre. The union contains at most `|A|` states. Restricting the fibre game to that union leaves the deterministic value unchanged. Thus a large worst fibre always has a compressed adverse receipt of size at most the action count.

The same Helly-style finite argument applies to epsilon-safe action conflicts. Give each state its set of epsilon-safe actions. A minimal collection with empty intersection has at most `|A|` states: for each state in a minimal conflict, choose an action excluded only by that state's necessity argument. The registered construction shows tightness and shows why pairwise conflicts are insufficient for three or more actions.

## 3. Static representation repair

A candidate feature separates a state pair when it gives different values. For exact scalar target recovery, the critical universe is the set of same-base-representation pairs with unequal targets. For error tolerance `epsilon`, the critical pairs are those with target gap greater than `2epsilon`.

A selected feature set is sufficient exactly when it separates every critical pair. Minimum-cost static repair is therefore weighted set cover over those pair constraints. The reduction is exact in both directions: an uncovered pair is an impossibility certificate, while a selected cover is a proof-carrying sufficiency certificate.

For action regret, pair constraints are not enough in general. The critical objects are minimal state sets whose epsilon-safe action intersection is empty. A selected feature set guarantees regret at most `epsilon` on every refined fibre exactly when it separates every minimal action conflict. Minimum-cost static action-safe repair is weighted set cover over the induced conflict hypergraph.

Classical set-cover complexity, approximation, and parameterized algorithms are not claimed as new. The contribution is the representation-owned construction of the universe and the exact equivalence between covering it and satisfying the global decision requirement.

## 4. Adaptive acquisition with state-dependent cost

A static feature set pays for every selected feature on every state. An adaptive policy may acquire a refinement, observe its value, and choose different continuations on different children. This can be strictly better, but state-dependent feature cost prevents a naive scalar recursion.

### 4.1 Loss profiles

For a current fibre `F` and remaining refinements `Q`, a deterministic policy tree has a complete statewise total-excess profile `p in R_+^F`. Terminal action `a` contributes profile `R(a,x)`. A refinement `q` with observation `h_q(x)` and statewise charge `c_q(x)` combines one child profile per observation:

`p(x)=c_q(x)+p_(h_q(x))(x)`.

The exact adaptive value is the minimum infinity norm over all recursively achievable profiles.

### 4.2 Exact Pareto pruning

If profile `p` is componentwise no larger than `p'`, then `p'` can be deleted. Adding the same future statewise charges preserves dominance, and combining independent child profiles preserves it coordinatewise. Therefore every dynamic state may retain only the Pareto antichain of achievable profiles. The antichain can still be exponential; the result is exactness, not a polynomial-time claim.

### 4.3 Why scalar child cost can fail

Replacing a varying child charge by its maximum gives a safe upper bound but may be strict because the state maximizing acquisition cost need not maximize continuation loss. A three-state hostile example changes the root decision: the exact profile recursion refines at value 2, while childwise maximum-charge scalarization acts immediately at value 3.

A scalar Bellman recursion is universally exact exactly when each refinement charge is constant on every reached observation cell. In that case accumulated sunk cost is one scalar within the child and can be pulled outside the maximum. If the charge is not constant, no continuation-independent scalar `kappa(c)` can satisfy

`max_x[c(x)+ell(x)]=kappa(c)+max_x ell(x)`

for every continuation profile `ell`.

### 4.4 Unbounded adaptive advantage

There are binary-feature systems with feature charges in `{0,1}` whose exact best static value is `k` while adaptive value is 1. Free index bits reveal which branch matters; an adaptive controller buys one branch-specific bit, while a static policy must buy all `k` branch bits or suffer a larger terminal mismatch. The ratio is unbounded.

## 5. Randomized adaptive certificates

Let `P(F,Q)` be the Pareto antichain of deterministic adaptive profiles. A randomized policy mixes profiles with weights `lambda`. Its expected statewise profile is their convex combination. The exact worst-state expected value is

`min_(lambda in Delta) max_(x in F) sum_j lambda_j p_j(x)`.

### 5.1 Small upper receipt

An optimal basic solution uses at most `|F|` deterministic trees. A complete upper certificate therefore contains the selected tree profiles, exact rational mixture weights, and the resulting expected profile.

### 5.2 Dual lower receipt

The dual chooses a distribution over hidden states. For a fixed adversarial prior, the best deterministic adaptive tree is found by a scalar Bayes decision-tree recursion: expected acquisition cost plus the sum of child continuation values. A rational adversarial prior and Bayes trace showing that every deterministic tree has expectation at least `v` form a lower certificate. Matching upper and lower values certify exact minimax optimality.

### 5.3 Expected versus pathwise authority

Worst state and worst random seed equals the best deterministic profile value; mixing cannot help that objective. Randomization may improve only the declared expected-loss semantics. The finite construction gives an unbounded separation between deterministic/pathwise and randomized expected value, so the semantic qualifier is load-bearing.

Randomized-static and deterministic-adaptive policies are also incomparable: either can beat the other by an arbitrarily large factor on different finite families. A serious experiment must therefore compare all four deterministic/randomized by static/adaptive arms.

## 6. The inductive boundary

Exact fibre authority assumes a complete finite fibre. In a held-out problem, the training states sharing a signature need not be the complete set of states that can share it. The exact training certificate therefore has no unseen-state upper-bound authority by itself.

### 6.1 Extension impossibility

Fix all training bytes, including representations, targets, costs, certificates, and decisions. Add one unseen state with an existing signature. One admissible extension can give the state zero learned loss and arbitrarily large fallback loss; another can reverse them. No training-only procedure can distinguish the worlds without an additional premise.

This is not a statistical lower bound. It is a finite authority statement: the training object does not logically determine the unseen value.

### 6.2 Three legitimate escape hatches

There are only three honest ways to cross the boundary.

1. **Closed-world completeness.** The declared finite corpus is the whole subject. This is the authority class of the exact graph atlases and the same-corpus R11 ASlib result.
2. **Structural deterministic extension.** A proved law, such as a valid Lipschitz bound under a declared metric, transports anchor values to new states.
3. **Statistical authority.** A prospectively calibrated procedure states its distributional assumptions, coverage unit, conditioning, and failure probability. Its result is statistical, not exact-fibre authority.

A neighborhood, coarsening, or nearest-neighbor rule is not automatically a certificate. It becomes a structural certificate only with a valid law, or a statistical selector only with an explicit statistical guarantee.

### 6.3 Valid Lipschitz extension

If relative or absolute loss is `K`-Lipschitz under a declared metric, exact anchor values induce lower and upper envelopes. Adding anchors monotonically tightens the interval. Underestimating `K` can reverse a route decision and is therefore a fail-closed hostile control.

## 7. Paired fallback alignment and routing

Selective deployment compares at least two actions. A learned-action certificate alone does not describe the fallback.

Let learned and fallback total excess be `L(x)` and `F(x)`. Define relative loss

`Delta(x)=F(x)-L(x)`.

A valid interval for `Delta` directly certifies ordering: an upper endpoint at most zero certifies fallback no worse, and a lower endpoint at least zero certifies learned no worse. An interval crossing zero certifies no order. Absolute and relative certificates answer different questions and must remain separate receipt fields.

### 7.1 Exact routed mean identity

For a reject indicator `G=1` on rejected states and routed loss `S=(1-G)L+GF`,

`E[S-L]=P(G=1) E[F-L | G=1]`.

The same identity holds for any binary catastrophic event. This exposes the missing term in marginal selective-risk reporting: the fallback-minus-learned difference on the rejected subset.

### 7.2 Robust routed identity

The maximum routed loss is the maximum of learned loss on deployed states and fallback loss on rejected states. A learned-action upper certificate on the deployed set says nothing about the rejected-set fallback maximum.

### 7.3 Optimal fixed-cardinality rejection

For a fixed number of rejected states and known paired losses, the mean-optimal rejection set contains the states with smallest `F-L`. Confidence, learned loss, and fallback loss alone need not order states correctly. This finite result motivates direct relative-loss prediction rather than treating uncertainty as a proxy for route value.

## 8. Acquisition timing and route observability

A post-acquisition rejector pays the feature cost before deciding to fall back. A pre-acquisition router avoids that cost on fallback paths. If the same gate is available before acquisition, their pointwise difference is exactly the acquisition charge on rejected states.

A route can be moved before acquisition if and only if it is constant on every fibre of the free pre-acquisition information map. If it depends on the paid representation, it is not implementable before acquisition. Relabeling it as a pre-route silently gives the policy unavailable information.

The timing gap is unbounded even in a one-state problem with no prediction error. Consequently acquisition timing belongs in the theorem statement, the experiment arm, and the receipt.

## 9. Cross-scenario transfer

Suppose a source relative certificate is `[A_s,U_s]`, and a content-bound source-to-target bridge guarantees relative-loss drift at most `tau`. The only generally valid transported interval is

`[A_s-tau,U_s+tau]`.

A route sign transfers only if its source margin exceeds the drift. Reusing one representation or model configuration across scenarios is not certificate transfer. The bridge, matched state meaning, and drift budget are separate evidence obligations.

## 10. Exact finite-domain evidence

### 10.1 Three-domain collision census

The R8 registry exhausts:

- all 32,768 labeled simple graphs on six vertices, using sorted degree sequence and triangle count to predict chromatic number;
- 155,106 covering five-set families over a five-element universe, using set-size and pairwise-intersection multisets to predict minimum cover size;
- 42,504 five-clause 2-CNF formulas on four variables, using signed occurrence counts and labeled variable-pair co-occurrence to predict satisfying-assignment count.

The maximum target diameters are respectively 1, 1, and 4. Candidate refinements include both exact repairs and failures: four-cycle count closes the six-vertex graph fibres while component count does not; pairwise-union multiset closes the set-cover panel while element-frequency multiset does not; labeled signed-pair profiles close the 2-SAT panel while global sign-type counts do not.

These are complete finite statements. They do not establish production prevalence or learned-model failure rates.

### 10.2 Seven-vertex graph atlas

The complete atlas contains 1,044 unlabeled seven-vertex graphs. The base representation has 58 ambiguous fibres and maximum chromatic-number diameter 1. The six-vertex induced-C4 repair leaves 17 ambiguous fibres; clique number leaves 18 and one-WL leaves 20. An induced four-vertex graphlet profile and a registered combined refinement close the target ambiguity on the full atlas.

This is a preserved nontransfer result. A repair can be exact at one finite size and fail at the next.

## 11. Public algorithm-selection evidence

### 11.1 Positive same-corpus result

The R11 audit pins ASlib SAT12-ALL, including algorithm runs, feature values, feature costs, and feature runstatus. It evaluates all 513 dependency-closed feature-step representations on 1,614 instances and 31 solvers. Feature acquisition and PAR10 solver runtime use the same scenario time unit and the same statewise virtual-best baseline.

With no features, all instances form one fibre and robust total excess is 12000. All feature steps nearly eliminate action ambiguity but incur a maximum recorded feature cost of 16906.55, making robust total excess worse than no features. Exhaustive evaluation selects exactly `Pre + lobjois`:

- robust total excess: 1712;
- robust action-only regret: approximately 11.53;
- mean feature cost: approximately 22.74;
- mean total excess: approximately 23.01;
- 1,595 representation fibres;
- maximum fibre size: 20.

The worst fibre's exact value is witnessed by three states, despite the 31-action portfolio and 20-state fibre. This instantiates the small-witness theorem on a public solver portfolio.

The result is exact for the pinned complete corpus. It is transductive evidence.

### 11.2 Prospectively frozen held-out refutation

R14 freezes the split and training-only representation selection before aggregate outcomes. On official cross-validation, the selected exact-equality policy has only 3.22% held-out exact-signature coverage, mean total excess about 5380.23, and catastrophic wrong-action rate about 44.55%. A same-information 16-nearest-neighbor arm reaches mean excess about 1465.09 and catastrophic rate about 11.96%.

Under zero-family-overlap shift, exact-signature coverage is 5.08%, mean excess about 5341.59, and catastrophic rate about 44.24%, while 16-nearest-neighbor reaches about 1982.36 and 16.23%.

`Pre + lobjois` remains frequently selected during training, so the failure is not mainly representation-menu instability. The failure is authority: continuous exact signatures rarely recur, and the complete-corpus fibre problem has become an inductive prediction problem.

This adverse result narrows rather than invalidates R11. R11 remains an exact complete-corpus decision certificate. R14 refutes its inductive reinterpretation.

### 11.3 Coarsening and coverage tax

A prospectively frozen coarsening increases coverage and improves some mean outcomes but does not earn the registered robust transfer terminal. R15 formalizes why this is unsurprising. Coverage, correctness conditional on coverage, fallback loss, and acquisition cost enter separate terms in the total objective. Increasing coverage may increase or decrease value depending on which states become covered and what decisions are made there.

The paper therefore rejects “coverage increased” as a certificate claim. Coverage is an operational quantity; certificate validity requires an authority premise.

### 11.4 Cross-scenario calibration and fallback sign reversal

R16 freezes development on SAT16, validation on SAT18, and an untouched test on SAT20. The selected learned-action model has useful predictive value on all three scenarios, and the registered marginal certificate behaves as designed. Nevertheless, the fallback is substantially worse than learned on rejected states in development and validation, and slightly better on the test scenario.

R17 decomposes the exact rejected-set differences:

- SAT16: fallback minus learned mean approximately `+4994.18`, catastrophic difference approximately `+0.1011`;
- SAT18: approximately `+26604.07` and `+0.54`;
- SAT20: approximately `-686.71` and `-0.015625`.

The sign reversal is the decisive observation. A marginal learned-action certificate can be valid while selective routing has no portable value because the fallback alignment term is different and unstable.

## 12. What the evidence proves—and what it refutes

The combined evidence supports four conclusions.

First, complete representation fibres yield exact, compact, model-independent decision certificates. This is established analytically and instantiated on finite exact domains and a public solver portfolio.

Second, acquisition cost changes the optimum. More information can reduce action ambiguity while worsening total decision cost. Static and adaptive policies require explicit feature pricing, and state-dependent pricing requires profile rather than scalar state.

Third, complete-corpus exactness does not imply inductive value. The prospectively frozen equality experiment is a direct refutation, not merely a missing experiment.

Fourth, selective routing is a paired-action problem. Learned-action calibration, fallback alignment, acquisition timing, and transfer drift are distinct obligations.

The evidence refutes three tempting headlines:

- exact training fibres do not certify unseen same-signature states;
- higher coverage does not imply better certificate value;
- marginal learned-action calibration does not imply beneficial fallback routing.

## 13. Relation to prior work

FiberGuard does not claim the generic invention of algorithm selection, selective prediction, conformal calibration, learning to defer, active feature acquisition, minimax decision theory, set cover, Lipschitz extension, or domain adaptation. Those mechanisms are donor-owned.

The residual candidate contribution is the exact integration of:

1. complete representation fibres as closed-world authority objects;
2. one statewise oracle baseline for every action and acquisition cost;
3. small deterministic and randomized finite receipts;
4. conflict-induced static repair;
5. statewise adaptive loss profiles and the exact scalarization boundary;
6. explicit separation of closed-world, structural, and statistical authority;
7. paired fallback-minus-learned routing certificates;
8. pre/post acquisition measurability and sunk-cost accounting;
9. prospective positive, partial, null, and refuting application terminals in one paper.

A current primary-source matrix and independent specialist subtraction remain required before any novelty statement is promoted.

## 14. Limitations

The complete-fibre computations are finite and may be exponential. Pareto profile antichains can grow exponentially. Exact rational randomized certificates do not provide pathwise safety. The public algorithm-selection results use ASlib scenarios and PAR10 conventions; they do not establish production deployment value. The non-SAT or production-derived paired-route discriminator remains open. No structural metric or Lipschitz constant has been validated for the ASlib representation. External reproduction and specialist novelty adjudication remain absent.

The adverse results are not optional caveats. They determine the correct claim: FiberGuard certifies what a declared finite information state supports and identifies the exact additional premise required to say more.

## 15. Reproducibility and authority

Every registered finite result binds source revision, input subject, cost convention, representation, action set, terminal, hostile controls, and authority ceiling. Same-owner CI, byte-stable replay, or a second solver over the same generated clauses is implementation corroboration, not external independence.

The theorem and evidence DAG requires every reader-visible conclusion to include both the positive transductive path and the inductive/fallback refutation paths. The claim ledger forbids restoring a stronger inductive or routing interpretation in the abstract, introduction, or conclusion.

Current manuscript terminal:

`FIBERGUARD_R19_THEORY_AND_STORY_SYNTHESIS_COMPLETE__EXTERNAL_EVIDENCE_OPEN`

Current publication terminal:

`NOT_SUBMISSION_READY`

## 16. Decisive remaining experiment

The next study is no longer exploratory. It must prospectively freeze a paired solver-routing problem with:

- learned and fallback total losses under one oracle;
- direct relative-loss prediction and calibration;
- separate pre- and post-acquisition information maps;
- action-specific acquisition costs;
- deterministic and randomized static/adaptive arms;
- no-route, one-sided, paired-absolute, direct-relative, Bellman, nearest-neighbor, current algorithm-selection, and oracle baselines;
- one untouched non-SAT or production-derived portfolio;
- complete raw and durable archive custody.

A positive result requires matched-cost improvement and valid paired certificates. A null, sign reversal, no-coverage terminal, or stronger-baseline loss remains scientifically admissible and must be imported without rewriting the theory.

## 17. Conclusion

FiberGuard begins with a simple finite fact: a policy cannot distinguish states that its representation identifies. Following that fact to its logical end yields a broad but disciplined theory. Complete fibres support exact target and action certificates. Static repair is a covering problem over induced conflicts. Adaptive acquisition requires statewise profiles when prices vary. Randomization has exact upper and lower receipts but only expected-loss authority. Unseen states require completeness, structure, or statistics. Routing requires paired action evidence, correct timing, observability, and transfer margin.

The experiments validate the finite theory and expose its boundary. The same-corpus ASlib result is strongly positive. The prospectively frozen inductive and fallback studies are adverse. Together they support a more durable conclusion than either alone: exact representation certificates are useful because they say precisely what is known, and a rigorous system must make every step beyond that boundary explicit.
