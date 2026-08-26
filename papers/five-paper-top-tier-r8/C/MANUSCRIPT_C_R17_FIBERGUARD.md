# FiberGuard: Exact Representation Certificates Around Learned Algorithm Selection

## Abstract

Algorithm selectors act on representations, not on the full optimization instance. When two states share the selector's input but demand different actions, confidence calibration cannot remove the information loss. We develop **FiberGuard**, a finite exact calculus for auditing that loss at the level of downstream decisions. For a frozen representation, finite action portfolio and statewise cost matrix, FiberGuard computes deterministic and randomized minimax action regret, epsilon-safe action sets, constant-size worst-fibre certificates, and exact feature conflicts. Minimum-cost static repair is an induced weighted set-cover problem. Adaptive acquisition with state-dependent feature cost requires statewise loss profiles rather than a scalar Bellman value; Pareto pruning is exact, and the scalar recursion is valid exactly under cell-constant charges. Randomized adaptive policies admit small mixed-tree upper certificates and dual adversarial-prior lower certificates.

The theory changes the role of exact representation audits. FiberGuard is not a replacement for learned action maps: it certifies the information budget within which they operate. A complete-corpus SAT study finds a sparse representation with large exact decision value, but a prospectively frozen held-out audit refutes strict robust transfer while retaining mean gains. In three untouched non-SAT scenarios, a timeout-first tail-aware selector transfers in answer-set programming and graph matching but fails in MiniZinc/CSP. Finally, on three further untouched scenarios, per-solver random-forest regression outperforms FiberGuard's exact robust cell action on the same selected representation in Bayesian-network and travelling-salesperson selection, while mixed-integer programming is tied because the exact selector chooses no features. The resulting claim is deliberately hybrid: exact fibres provide representation-owned impossibility, safety and failure certificates; learned runtime models may provide the operational action map. We preserve every adverse domain and separate complete-corpus exactness, held-out risk, learned comparison and external authority.

## 1. Introduction

A learned combinatorial optimizer receives a representation `Phi(x)` of an underlying state `x`. Its model confidence concerns uncertainty conditional on that representation. It does not answer a more basic question: whether the representation itself contains enough information to support the requested action.

FiberGuard treats the preimage

`F_y = {x : Phi(x)=y}`

as the scientific object. A representation-only policy must behave consistently on each fibre. Exact variation within a fibre is therefore an information certificate independent of model architecture, training procedure and calibration. Earlier representation audits focused on scalar target diameter. This paper moves to action cost, feature price and adaptive control.

The paper makes four contributions.

First, it develops exact deterministic and randomized action-regret certificates for finite fibres. The certificate is operational: different oracle labels do not necessarily imply large decision loss, while a small target difference can induce catastrophic action regret. Every deterministic worst fibre has a certificate on at most the action count.

Second, it characterizes exact representation repair. Minimal sets of states with no common epsilon-safe action are hyperedges of an action-conflict system. A static feature set is globally epsilon-safe exactly when it separates every minimal conflict, so minimum-cost repair is weighted set cover on a representation-owned hypergraph.

Third, it gives the exact adaptive theory. With state-dependent acquisition cost, a single scalar fibre value is generally insufficient because the state maximizing acquisition cost need not maximize continuation loss. The exact Bellman state is a statewise sunk-cost profile; equivalently, policies form a Pareto antichain of achievable statewise excess-loss profiles. Cell-constant feature charges are the exact universal boundary at which scalar dynamic programming becomes valid. Randomized adaptive policies are finite zero-sum games over those profiles and admit compact primal/dual receipts.

Fourth, it supplies a staged application study with hostile controls. The evidence rejects a simple selector-superiority story. Exact complete-corpus value is large, robust held-out transfer fails, failure-aware tail/timeout value transfers in two of three untouched non-SAT domains, and common learned runtime regression beats the exact robust cell action on the same representation in two of three further untouched domains. This adverse sequence is central to the final thesis rather than omitted.

## 2. Finite decision setup

Let `X` be a finite state space, `Phi:X->Y` a frozen representation and `A` a finite nonempty action set. Let `C(a,x)` be a prospectively declared finite deterministic cost. Define the statewise oracle

`C*(x)=min_{b in A} C(b,x)`

and action regret

`R(a,x)=C(a,x)-C*(x)`.

All acquisition, action, defer and route costs that enter one recursion use the same physical unit and the same statewise oracle baseline. If a route or defer leaf has absolute cost `D_abs(x)`, its terminal excess profile is `D_abs(x)-C*(x)`. Equal units without equal baseline are not additive.

Timeouts, crashes and censored observations require a frozen finite convention or a resource-incomparable terminal. The application panels use each ASlib scenario's PAR10 convention and measured feature-step time. This convention is an experimental choice, not a claim that PAR10 is uniquely correct.

## 3. Exact fibre action certificates

### Theorem 1: deterministic representation regret

For an attained fibre `F`, the exact worst-case regret of the best deterministic representation-only action is

`rho_det(F)=min_{a in A} max_{x in F} R(a,x)`.

The global value is `max_y rho_det(F_y)`.

Define the epsilon-safe action set

`Safe_epsilon(F)={a : max_{x in F}R(a,x)<=epsilon}`.

It is nonempty exactly when `rho_det(F)<=epsilon`. FiberGuard therefore returns a certified action set, not merely a scalar uncertainty interval.

### Theorem 2: randomized representation regret

For ex-ante randomization, where the state adversary observes the declared distribution but not the private draw,

`rho_rand(F)=min_{p in Delta(A)} max_{x in F} sum_a p_a R(a,x)`.

This is a finite linear program. It is an expected-loss guarantee, not pathwise, tail or high-probability safety. Worst-state, worst-seed evaluation removes the randomization benefit.

### Theorem 3: refinement monotonicity

If `Psi` refines `Phi`, then deterministic and randomized minimax action regret cannot increase. A refined policy can ignore the additional information. This is an information monotonicity statement before acquisition cost.

### Theorem 4: compressed deterministic witnesses

For `m=|A|`, every deterministic fibre value is witnessed by at most `m` states. For each action choose one state attaining its maximum regret; the minimum over actions on the selected set equals the full-fibre value.

This gives a small adversarial receipt even when the fibre is large. The R11 SAT application instantiates the theorem with a 31-solver portfolio: a 1,614-state no-feature fibre needs seven witness states, and the worst fibre of the optimal static representation needs three.

## 4. Static representation repair

For tolerance `epsilon`, each state has a safe-action set. A **minimal action conflict** is an inclusion-minimal state set whose safe-action intersection is empty.

### Theorem 5: conflict size and feature-cover equivalence

Every minimal conflict has size at most `|A|`, and the bound is tight. Pairwise conflicts are insufficient for three or more actions.

A selected static feature set guarantees regret at most `epsilon` on every refined fibre if and only if it separates every minimal action conflict. Consequently, minimum-cost static repair is exactly weighted set cover on the induced conflict hypergraph.

Classical set-cover complexity and approximation results are donor-owned. The paper-specific object is the exact conversion from global action safety to a representation-derived conflict system, together with explicit uncovered-conflict impossibility certificates.

## 5. Adaptive acquisition requires loss profiles

Let `Q` be the remaining finite refinements. A deterministic adaptive policy is a finite decision tree: internal nodes acquire a feature, edges are observations and leaves select terminal profiles. For a policy `pi`, define its statewise total excess

`L_pi(x)=sum_{q acquired on x's path} c_q(x)+R(a_pi(x),x)`.

The robust value is `max_x L_pi(x)`.

### Theorem 6: exact profile recursion

Let `P(F,Q)` be the set of recursively achievable loss profiles on fibre `F`. It contains every terminal action-regret profile. For refinement `q`, choose independently one child profile for each attained observation and add the statewise acquisition charge. Then

`V(F,Q)=min_{p in P(F,Q)} max_{x in F} p(x)`.

Componentwise dominated profiles can be deleted at every node without changing any ancestor optimum. Dominance is preserved by adding the same statewise prefix charges and by child combination. The exact implementation may therefore retain the Pareto antichain, although that antichain can be exponential.

An equivalent Bellman state retains the statewise sunk-cost vector `b`:

`W(F,Q;b)=min { min_a max_x[b(x)+R(a,x)], min_q max_o W(F_o,Q\{q};(b+c_q)|_{F_o}) }`.

### Theorem 7: scalar-collapse boundary

A continuation-independent scalar `kappa(c)` can satisfy

`max_x[c(x)+ell(x)]=kappa(c)+max_x ell(x)`

for every nonnegative continuation profile `ell` if and only if `c` is constant on the current observation cell.

Thus the familiar scalar recursion is exact when every reachable feature charge is determined by the observation available to the controller. Replacing a varying charge by its child maximum is a safe upper bound but can change the root decision. A three-state hostile control has exact refine value two while the scalar upper-bound controller acts immediately at value three.

### Theorem 8: adaptivity gap

Adaptive acquisition weakly dominates every fixed static feature set. The gap is unbounded: for every `k`, a binary-feature system with acquisition cost in `{0,1}` has exact best static value `k` and exact adaptive value one.

## 6. Randomized adaptive certificates

Randomized adaptive policies mix deterministic loss profiles. Let the Pareto profiles be `p_1,...,p_M`.

### Theorem 9: randomized adaptive minimax

`V_RA(F,Q)=min_{lambda in Delta_M} max_{x in F} sum_j lambda_j p_j(x)`.

Dominated deterministic profiles remain removable before mixing. There is an optimal mixture supported on at most `|F|` deterministic trees. The dual is an adversarial distribution over hidden states.

For a fixed adversarial prior, the best deterministic continuation is computed by a scalar Bayes decision-tree recursion because expectation is additive across observation children. A complete exact receipt therefore contains:

- an upper certificate: at most `|F|` deterministic policy profiles with rational mixture weights;
- a lower certificate: a rational adversarial prior and Bayes Bellman trace.

Matching values certify exact randomized minimax optimality. Decimal-only LP output is not treated as a proof.

Randomization and adaptivity are distinct axes. There are families with unbounded randomization benefit, families with unbounded adaptive benefit after static policies may randomize, and families where randomized-static and deterministic-adaptive policies beat one another by unbounded factors. Application studies should therefore distinguish deterministic/randomized and static/adaptive arms whenever randomization is operationally meaningful.

## 7. Exact finite verification

The theory is analytic. Separate standard-library implementations provide finite corroboration.

- Action-regret verifier: 720 deterministic policy cases, 1,120 randomized LP controls, 1,440 refinement checks, 1,698 safe-set checks, and 500 Bellman instances checked against 74,658 explicit policy trees.
- Static conflict cover: 1,000 generated systems with direct refined-fibre comparison, exact optimum-cost checks, higher-order conflicts and tight action-count witnesses.
- Profile Bellman: 240 general systems comparing Pareto profiles, all explicit policy profiles and the offset recursion; 240 cell-constant systems; all 36 registered low-dimensional charge profiles; and the adaptivity family through ratio ten.
- Randomized adaptive: 300 systems, 4,696 explicit deterministic profiles, 606 Pareto profiles, 502 exact equilibria, 1,200 additional prior checks and exact gap families through ratios sixteen and ten.

These checks corroborate implementation. They do not confer external independence, novelty or journal authority.

## 8. Empirical programme

### 8.1 Complete-corpus exact panels

The original finite benchmark exhausts 230,378 instances in graph colouring, set cover and 2-SAT with two exact target formulations. Frozen low-order representations have nonzero fibre diameter in all three domains. Candidate refinements can close, partially close or fail to reduce ambiguity. A seven-vertex graph-atlas extension shows that a six-vertex cycle-count repair does not transfer, while a graphlet profile is target sufficient on the complete atlas.

These panels establish finite deterministic information loss. They do not establish prevalence, large-instance computational hardness or model failure.

### 8.2 R11: positive complete-corpus decision value

On pinned ASlib SAT12-ALL, the complete audit evaluates 513 dependency-closed feature-step sets over 1,614 instances and 31 solvers. The same-unit objective is feature acquisition plus selected-solver PAR10 minus statewise virtual-best runtime.

- no features: robust total excess 12,000;
- all features: robust total excess 16,906.55 because one acquisition path is extremely expensive;
- exact optimum `{Pre,lobjois}`: robust total excess 1,712, mean excess 23.01 and maximum fibre size 20.

This is a strong exact result on the complete historical corpus. It is post-selection evidence and does not estimate unseen-instance performance.

### 8.3 R14: prospective robust transfer failure

Before reading aggregate outcomes, R14 freezes source CV, an outcome-blind path-prefix group split, training quartiles, support threshold two, no-feature fallback and all 513 candidate representations.

The precommitted robust gate fails on both splits:

- source CV: primary 12,002.23 versus no-feature 12,000;
- group split: primary 12,005.83 versus no-feature 12,000.

Mean excess improves by 31.48% and 7.32%, respectively. Exact R11 equality signatures recur for only 20 of 1,614 held-out rows, so 1,594 rows fall back. The source-CV worst row is an unsupported cell; the group-split worst row is a supported cell that transports the wrong action. Representation-support failure and in-cell action drift are distinct.

R14 refutes strict robust transfer for the frozen static procedure. It does not erase the complete-corpus result or the descriptive mean gain.

### 8.4 R15: failure-aware transfer in two of three non-SAT domains

R15 prospectively freezes answer-set programming, MiniZinc/CSP and graph-matching scenarios before reading outcomes. The primary lexicographic training objective minimizes timeout count, empirical worst-five-percent mean, overall mean, robust maximum and feature count in that order.

The primary arm passes all timeout/tail/mean gates on source and hash splits in ASP and graph matching. It fails on both splits in MiniZinc/CSP and that domain remains in the denominator.

- ASP source CV: timeout rate 17.54% to 12.06%; mean excess 683.73 to 359.81.
- ASP hash: 17.31% to 11.82%; mean 669.44 to 345.92.
- Graph source CV: timeouts 183 to 145; worst-five-percent mean about 230.65M to 97.46M; mean about 11.56M to 4.89M.
- Graph hash: timeouts 164 to 150; tail 163.76M to 115.08M; mean 8.21M to 5.77M.

Robust maxima remain a separate estimand because a PAR10-ceiling row can also pay positive feature cost. The empirical tail statistic is not a distribution-free CVaR guarantee.

### 8.5 R16: learned action maps beat exact robust cell actions

R16 freezes three further untouched scenarios and two transparent random-forest formulations. Same-step learned arms receive exactly the FiberGuard-selected representation and pay the identical feature cost.

Per-solver random-forest regression dominates the exact robust cell action on both source and hash splits in BNSL and TSP. MIP is mixed because FiberGuard selects no features in every fold.

- BNSL source CV: timeouts 51 to 36, tail 61,170 to 43,375, mean 3,119 to 2,194.
- BNSL hash: 47 to 34, tail 56,714 to 41,164, mean 2,896 to 2,082.
- TSP source CV: 64 to 43, tail 15,703 to 10,958, mean 816 to 579.
- TSP hash: 68 to 40, tail 16,604 to 10,273, mean 861 to 544.

Oracle-action classification is unstable in BNSL and catastrophic in TSP, where it produces 271–279 timeouts. All-step regression is favorable on timeout/tail/mean in all three scenarios, suggesting the exact representation selector can be overconservative for a smooth learned runtime model.

R16 rejects the claim that FiberGuard's robust cell action is a learned-selector replacement. It supports a complementary architecture: exact representation certificates around learned runtime action maps.

## 9. Relationship to prior work

Algorithm selection, ASlib, configured selector frameworks, random-forest runtime prediction, SUNNY-style neighborhood methods, survival-analysis selectors and risk-aware online selection are established. Active feature acquisition and cost-sensitive prediction also study which information to buy before prediction. FiberGuard claims none of these mechanisms generically.

The residual object is different: the exact complete fibre induced by the selector's declared information, its action-regret/safe-set certificate, its minimal conflict system, and exact state-dependent acquisition accounting. The empirical contribution is not a universal selector win. It is the controlled demonstration that exact certificate value, robust transfer, failure-aware mean/tail value and learned action quality can disagree and must be reported separately.

A current primary-source matrix and explicit subtraction ledger accompany this manuscript. Absence of a matching phrase or construction is not treated as a novelty certificate.

## 10. Limitations and authority

The finite theorem statements are complete for their declared subjects. The broad application claim remains bounded by five facts.

First, ASlib scenarios are historical public benchmarks, not current production deployments. Second, source and hash folds are not domain-expert family splits. Third, the random forests are transparent fixed baselines, not strongest configured or censor-aware selectors. Fourth, all primary implementation and interpretation remains same-owner. Fifth, PAR10 and the empirical worst-five-percent mean are frozen finite conventions, not universal utility or probabilistic safety guarantees.

Therefore this package does not claim external replication, domain-expert validation, production value, novelty adjudication, top-tier acceptance or journal authority.

## 11. Reproducibility

Every application tranche binds the upstream commit and source blobs, freezes the protocol before outcome access, runs twice byte-identically, preserves null/adverse terminals and archives content hashes. Compact in-repository summaries bind the full artifact hashes and all load-bearing metrics. The claim ledger distinguishes analytic proof, finite implementation corroboration, prospective out-of-fold evidence and external authority.

## 12. Conclusion

FiberGuard makes representation adequacy an exact decision object. The theory provides deterministic and randomized regret, safe sets, small witnesses, conflict hypergraphs, exact static repair, state-dependent adaptive profiles and compact randomized certificates. The experiments show why the distinctions matter. Complete-corpus exact value can be large while robust transfer fails; failure-aware tail/mean value can transfer in some domains and fail in another; a learned runtime model can beat the exact robust cell action on the same representation.

The surviving thesis is narrower and stronger than the original selector story: **exact fibres certify the information and failure boundary; learned models choose actions within that audited boundary.** This is the manuscript claim to carry into independent reproduction and specialist review.
