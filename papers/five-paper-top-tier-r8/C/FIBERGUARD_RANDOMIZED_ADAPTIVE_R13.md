# FiberGuard R13 — randomized adaptive refinement, dual priors, and small policy certificates

Date: 2026-08-26

Status: analytic extension of the exact R12 loss-profile Bellman theory. The generic finite minimax theorem, linear-programming duality, mixed-versus-behavioral strategy equivalence, and decision-tree adaptivity mechanisms are donor-owned. The FiberGuard-specific object is the complete-fibre excess-loss game under one statewise oracle baseline, together with exact upper/lower certificates that remain valid when feature costs are state dependent.

## 1. Semantics

Fix a finite current fibre `F`, a finite set `Q` of still-admissible refinements, and the R12 set `P(F,Q)` of deterministic adaptive policy loss profiles. Every profile `p` records, for each hidden state `x in F`, the complete total excess

`p(x) = acquired feature cost on x + terminal cost on x - C*(x)`.

The same statewise oracle `C*(x)` is used by every policy, action, defer leaf, and route-to-exact-solver leaf. A terminal absolute cost `D_abs(x)` therefore enters as `D_abs(x)-C*(x)`. Equal units without this common baseline remain insufficient.

A randomized policy is evaluated by **worst-case expected excess**:

1. the policy distribution is declared;
2. the adversary observes that distribution and chooses `x`;
3. the policy's private random draw is realized;
4. loss is averaged over that draw.

The adversary does not observe the private draw before choosing `x`. This is the same ex-ante expected-regret semantics already frozen in R10. It is not a pathwise, tail, high-probability, or adaptive-adversary guarantee.

The policy may draw one complete deterministic decision tree at the root. Nodewise behavioral randomization has the same attainable statewise expected profiles in this finite perfect-recall tree. That equivalence is classical extensive-form game theory and receives no novelty credit here.

## 2. Exact randomized adaptive value

Let the deterministic profiles be `P={p_1,...,p_M}`. A mixed policy chooses `lambda in Delta_M`. Its expected profile is

`z_lambda(x)=sum_j lambda_j p_j(x)`.

### Theorem C-R13.1 — convex-profile minimax formula

The exact randomized adaptive FiberGuard value is

`V_RA(F,Q) = min_{lambda in Delta_M} max_{x in F} sum_j lambda_j p_j(x)`

`             = min_{z in conv(P(F,Q))} ||z||_infinity`.

It is the linear program

minimize `t`

subject to

- `sum_j lambda_j = 1`;
- `lambda_j >= 0`;
- `sum_j lambda_j p_j(x) <= t` for every `x in F`.

#### Proof

Drawing deterministic tree `j` with probability `lambda_j` produces expected loss `z_lambda(x)` on every fixed state. Every root mixture gives one convex combination, and every convex combination is implemented by such a mixture. The adversary chooses the largest state coordinate. Minimizing that maximum gives the formula and its epigraph LP. ∎

The result remains exact with state-dependent acquisition charges because each deterministic profile already contains the complete statewise sum. Randomization is applied only after those exact profiles are formed.

## 3. Pareto pruning survives randomization

Write `p <= p'` when `p(x)<=p'(x)` for all states.

### Theorem C-R13.2 — dominated deterministic policies may be removed before mixing

Deleting every componentwise dominated deterministic profile leaves `V_RA` unchanged.

#### Proof

If a mixture assigns mass `alpha` to `p'` and `p<=p'`, move that mass from `p'` to `p`. Every coordinate of the expected profile weakly decreases. Repeating this replacement removes all dominated profiles without increasing the objective. ∎

Thus the exact randomized LP may use the R12 Pareto antichain rather than every deterministic policy profile. This is an exact reduction, not a claim that the surviving antichain is polynomially bounded.

## 4. A small upper certificate

### Theorem C-R13.3 — at most `|F|` deterministic trees suffice

There exists an optimal randomized adaptive policy supported on at most `|F|` deterministic policy trees.

#### Proof

Take an optimal basic solution of the LP in Theorem C-R13.1. Suppose exactly `s` mixture weights are positive. The zero weights supply `M-s` active nonnegativity constraints. Besides the simplex equality, a basic solution needs `s` linearly independent active state-loss constraints. There are only `|F|` such constraints, hence `s<=|F|`. ∎

A randomized FiberGuard upper certificate therefore consists of at most `|F|` deterministic tree receipts, rational mixture weights, and the resulting expected loss at each state. This bound depends on the fibre size, not on the potentially much larger number of policy trees.

## 5. Exact dual lower certificate

LP duality gives a distribution over hidden states.

### Theorem C-R13.4 — adversarial-prior dual

`V_RA(F,Q)` equals

`max_{mu in Delta(F)} min_{p in P(F,Q)} sum_{x in F} mu(x)p(x)`.

Equivalently, the dual LP is

maximize `v`

subject to

- `mu(x)>=0`;
- `sum_x mu(x)=1`;
- `sum_x mu(x)p(x)>=v` for every deterministic adaptive profile `p`.

A feasible `mu` proves a lower bound `v` when every deterministic adaptive tree has expected excess at least `v` under that prior.

#### Proof

The matrix with rows indexed by deterministic policies and columns indexed by states is a finite zero-sum loss game. The displayed programs are the primal and dual LPs, so finite strong duality gives equality. ∎

This dual is scientifically useful. The upper certificate shows a small mixed policy whose worst expected state loss is at most `v`; the lower certificate gives a state distribution under which no deterministic adaptive policy has expectation below `v`. Matching values certify exact randomized minimax optimality.

## 6. The dual separation oracle is scalar

Worst-case state-dependent acquisition requires the R12 profile or offset state. Expected loss under a fixed state prior is different: linearity restores a scalar dynamic program.

Let `w` be nonnegative, not necessarily normalized, weights on a current fibre `G`. Define `B(G,Q;w)` as the minimum weighted expected future excess of a deterministic policy.

### Theorem C-R13.5 — exact Bayes Bellman recursion

`B(G,Q;w)` satisfies

`B(G,Q;w) = min {`

`  min_a sum_{x in G} w(x)R(a,x),`

`  min_{q in Q} [ sum_{x in G} w(x)c_q(x)`

`                 + sum_o B(G_o,Q\{q};w|_{G_o}) ]`

`}`,

with registered defer/route profiles included among the terminal alternatives.

Consequently,

`V_RA(F,Q) = max_{mu in Delta(F)} B(F,Q;mu)`.

#### Proof

Condition on the first deterministic policy decision. At a terminal leaf, weighted loss is the displayed action sum. If refinement `q` is acquired, its expected charge is the first sum. Observation children are disjoint, and a deterministic continuation can be selected independently in each child, so their minimum weighted losses add. Induction on `|Q|` proves the Bellman equation. The final identity follows from Theorem C-R13.4 because `B(F,Q;mu)` is exactly the minimum `mu`-weighted loss over deterministic profiles. ∎

This yields an exact lower-certificate checker without enumerating every policy tree: run the scalar Bayes recursion once on the proposed adversarial prior. It also supplies a separation oracle for column-generation or cutting-plane implementations of the randomized LP.

The contrast with R12 is structural:

- worst-case state choice does not distribute over child states, so exact statewise profiles are required;
- a fixed expectation is linear and decomposes across observation children, so one scalar per Bayes subproblem is sufficient.

## 7. Pathwise safety does not improve under randomization

Define the worst-state, worst-random-seed value

`V_path = inf_randomized_policy max_{x,omega} L(x,omega)`.

### Theorem C-R13.6 — pathwise value equals the deterministic adaptive value

`V_path = V_DA`, where `V_DA=min_{p in P(F,Q)} max_x p(x)` is the R12 deterministic adaptive value.

#### Proof

Every fixed random seed resolves all random choices into one deterministic policy tree. For any randomized policy, the maximum over states and seeds is at least the minimum worst-state value of a deterministic tree. Conversely, putting all probability on a deterministic R12 optimum attains that value. ∎

Therefore every randomized improvement in this addendum is an expected-loss improvement only. A manuscript or application must not promote it into a guarantee for every seed, a tail-risk guarantee, or a catastrophic-loss bound.

## 8. Randomization alone can have an unbounded ratio

### Theorem C-R13.7 — deterministic versus randomized expected regret

For every integer `n>=2`, there is an `n`-state, `n`-action fibre with no refinements such that

- deterministic/pathwise value is `n`;
- randomized worst-case expected value is `1`.

Hence the ratio is `n`.

#### Construction and proof

Let states and actions be indexed by `1,...,n`, and set

`R(a_i,x_j)=n` if `i=j`, and `0` otherwise.

At every state at least one action has zero regret, so this is a valid regret matrix. Every deterministic action has worst regret `n`. For a mixture with probabilities `lambda_i`, state `x_i` has expected regret `n lambda_i`; therefore the worst state has value at least

`n max_i lambda_i >= 1`.

The uniform mixture makes every state loss exactly one, proving optimality. ∎

This theorem deliberately exposes the semantic boundary. The same uniform policy still has pathwise loss `n`, because every sampled action has one bad state.

## 9. Adaptivity retains an unbounded advantage after terminal randomization

The R12 static/adaptive separation might conceivably disappear once static leaves may randomize. It does not.

### Theorem C-R13.8 — randomized static value `k`, randomized adaptive value `1`

For every integer `k>=1`, there is a finite system with binary features, feature costs in `{0,1}`, and terminal regrets in `{0,2k+1}` such that

- the best **randomized static** representation has exact value `k`;
- the best randomized adaptive policy has exact value `1`.

Thus the ratio is `k` and the additive gap is `k-1`.

#### Construction

Use states `x_(i,b)` for `i in {0,...,k-1}` and `b in {0,1}`. There is one action for each state. Its regret is zero on its matching state and `L=2k+1` on every other state.

Provide:

1. `ceil(log2 k)` zero-cost binary features revealing `i`;
2. one paid feature `q_i` for each branch, costing one on every state, whose output is `b` on branch `i` and zero outside that branch.

#### Static lower and upper bounds

If a fixed static representation omits `q_i`, states `x_(i,0)` and `x_(i,1)` remain in one fibre. On any fibre containing `r>=2` states, the best randomized action distribution has exact regret

`L(1-1/r) >= L/2 = k+1/2`:

uniform mixing over the `r` matching actions attains this value, while some state receives matching-action probability at most `1/r`, giving the lower bound. Hence any static policy with value at most `k` must acquire every paid `q_i`.

Acquiring all paid features and the free index bits identifies every state, costs exactly `k`, and leaves zero terminal regret. The randomized static optimum is therefore `k`.

#### Adaptive upper and lower bounds

An adaptive policy reads the free index, acquires only the corresponding `q_i`, and chooses the matching action. Its value is one.

For the lower bound, put prior probability `1/2` on the two states of one fixed branch. Any deterministic tree that acquires a paid feature incurs expected acquisition cost at least one. A deterministic tree acquiring no paid feature cannot distinguish the pair and has expected terminal regret at least `L/2>1`. Therefore every deterministic adaptive tree has expectation at least one under this prior. Theorem C-R13.4 gives randomized adaptive value at least one. ∎

## 10. Randomization and adaptivity are incomparable axes

Let

- `V_DS`: deterministic static value;
- `V_RS`: randomized static expected value;
- `V_DA`: deterministic adaptive value;
- `V_RA`: randomized adaptive expected value.

Always

`V_RA <= V_RS <= V_DS`

and

`V_RA <= V_DA <= V_DS`.

There is no universal ordering between `V_RS` and `V_DA`.

### Corollary C-R13.9 — unbounded incomparability

- In Theorem C-R13.7 there are no useful refinements, so `V_DA=V_DS=n` while `V_RS=V_RA=1`.
- In Theorem C-R13.8 the deterministic adaptive construction has value one while `V_RS=k`.

Each middle arm can therefore beat the other by an arbitrarily large factor. A serious application must compare all four arms rather than treating “randomized” and “adaptive” as interchangeable improvements.

## 11. Exact certificate packet

A complete randomized adaptive certificate for one finite fibre contains:

### Upper certificate

- at most `|F|` content-bound deterministic policy trees;
- rational mixture weights summing to one;
- each tree's complete statewise total-excess profile;
- the mixed expected profile and its maximum coordinate.

### Lower certificate

- a rational adversarial distribution `mu` on states;
- the Bayes Bellman trace proving `B(F,Q;mu)>=v`;
- the common value `v`.

The checker requires the upper maximum and lower Bayes value to agree exactly. Decimal-only weights are not an exact certificate unless a separately bounded rational interval proves the same terminal.

## 12. Finite verification

`fiberguard_randomized_adaptive_r13_core.py` implements an exact `Fraction` zero-sum solver by primal/dual support enumeration, the scalar Bayes recursion, exact randomized static fibre values, and the pathwise comparator.

`verify_fiberguard_randomized_adaptive_r13.py` checks:

- 300 generated finite systems;
- all 4,696 explicit deterministic root profiles against 606 Pareto-frontier profiles;
- 300 exact primal/dual randomized equilibria;
- the support bound on every equilibrium;
- 1,200 additional nonequilibrium prior checks comparing the Bayes recursion with explicit profile expectation;
- a two-state upper/lower hostile certificate;
- the randomization-gap family through `n=16`, with the general exact solver replayed through `n=8`;
- the randomized static/adaptive gap through `k=10`, with the general static solver cross-checked through `k=3`.

The finite verifier is implementation corroboration. The analytic arguments carry the theorem statements.

## 13. Application contract after the positive R11 static result

The inherited R11 SAT12-ALL result identifies `{Pre,lobjois}` as the exact best static dependency-closed representation on the pinned corpus, with robust total excess `1712`, compared with `12000` for no features and `16906.55` for all features. R12 supplies the exact deterministic adaptive profile recursion. R13 now supplies the randomized extension and exact certificate pair.

A same-corpus adaptive experiment should report all four policy classes:

1. deterministic static;
2. randomized static;
3. deterministic adaptive;
4. randomized adaptive.

It must additionally report:

- mixed-policy support size and exact rational weights;
- adversarial-prior support and Bayes lower-certificate value;
- worst expected excess and pathwise worst excess separately;
- tail quantiles and catastrophic PAR10 frequency;
- profile-frontier size and Bayes-oracle calls;
- every state/fibre on which randomization changes the chosen action distribution;
- every history on which adaptivity avoids an unnecessary feature step.

The R11 held-out/generalization gate remains separate and prior in the manuscript-readiness order. A positive same-corpus randomized/adaptive value does not establish learned-selector generalization or deployment value.

## 14. Prior-art boundary

The following mechanisms are explicitly donor-owned:

- mixed and behavioral strategy equivalence in finite perfect-recall trees: Kuhn, *Extensive Games and the Problem of Information* (1953);
- finite minimax, LP duality, basic-solution support bounds, and adversarial-prior certificates;
- adaptive diagnosis/decision trees optimizing worst and expected test costs: Cicalese, Laber, and Saettler, ICML 2014;
- value-dependent test costs and worst/expected tradeoffs: Saettler, Laber, and Cicalese, 2014;
- active feature acquisition and nongreedy learned acquisition policies: Valancius, Lennon, and Oliva, ICML 2024; Guney et al., ICML 2025; Li and Oliva, AISTATS 2025;
- evaluation of active feature acquisition under acquisition-induced distribution shift: von Kleist et al., JMLR 2025;
- generic sharp adaptive versus nonadaptive query separations, including Li et al., arXiv:2607.22799 (2026).

Accordingly, neither randomization, active feature acquisition, minimax duality, nor an adaptivity gap is claimed as generic novelty. The residual candidate contribution is the exact complete-fibre action-regret instantiation with common-oracle state-dependent cost accounting, loss-profile/Pareto construction, small mixed-tree upper certificates, Bayes-tree lower certificates, and the four-arm solver-selection discriminator.

External nearest-work review and novelty authority remain `CANNOT_CHECK`.

## 15. Authority ceiling

This addendum supports finite analytic theorems and internal implementation corroboration only. It does not establish:

- randomized or adaptive value on ASlib;
- tail or pathwise safety from expected minimax value;
- unseen-instance generalization;
- learned-selector superiority;
- cross-scenario transfer;
- production value;
- external independence;
- novelty; or
- journal authority.
