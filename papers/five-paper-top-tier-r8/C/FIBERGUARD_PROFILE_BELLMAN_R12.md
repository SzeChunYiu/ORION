# FiberGuard R12 — exact adaptive refinement with loss-profile Bellman states

Date: 2026-08-26

Status: analytic correction and extension of the deterministic action/refine/defer layer in `FIBERGUARD_ACTION_REGRET_R10.md`. Generic finite decision-tree dynamic programming, Pareto pruning, and value-of-information ideas are donor-owned. The paper-specific contribution is the exact fibre-level formulation, the same-oracle accounting contract, and the resulting static-versus-adaptive representation theorem.

## 1. Why a scalar fibre value is not always a sufficient Bellman state

The R10 recursion writes a refinement branch as

`c(r,F) + max_G V(G)`.

That formula is exact when the charge paid on a branch is a single number shared by every state in the resulting information cell. It is not an exact universal formula when acquisition time depends on the hidden state inside that cell. In that case,

`max_x [c(x) + continuation(x)]`

cannot in general be reconstructed from the two scalars `max_x c(x)` and `max_x continuation(x)`: the states attaining the two maxima may differ. Replacing a varying charge by its child maximum is safe as an upper bound, but can be strict and can change the optimal root decision.

This distinction matters for the R11 ASlib application. Its static objective is already exact because it evaluates the complete statewise sum before taking the maximum. An adaptive extension must retain the statewise loss profile, or must explicitly freeze acquisition cost as part of the revealed observation so that every child charge becomes constant.

## 2. Common-baseline setup

Let `X` be a finite exact state space. At a current information fibre `F subseteq X`, let:

- `A` be a finite set of terminal actions;
- `R(a,x) = C(a,x) - C*(x)` be action regret relative to one common statewise oracle `C*(x)`;
- `Q` be a finite set of still-admissible refinements;
- `h_q(x)` be the observation returned by refinement `q`;
- `c_q(x) >= 0` be its statewise acquisition charge, expressed in the same frozen unit as `R`.

A defer, abstain, or route-to-exact-solver leaf is represented by another terminal loss profile. If its registered absolute cost is `D_abs(x)`, the profile entering this recursion is

`D_abs(x) - C*(x)`,

not `D_abs(x)` itself. Thus every terminal and every accumulated feature charge is measured as total excess over the same oracle baseline. Same units without the same baseline are insufficient.

A deterministic adaptive policy is a finite decision tree. An internal node acquires one admissible refinement and follows the edge labelled by its observation. A leaf chooses one terminal action/profile. Refinements are not repeated; dependency or history restrictions are handled by limiting the admissible set at each node.

For a policy `pi`, define its complete statewise excess-loss profile

`L_pi(x) = sum_{q acquired on the path of x} c_q(x) + R(a_pi(x),x)`.

Its robust value on `F` is `max_{x in F} L_pi(x)`.

## 3. Exact profile recursion

For an ordered finite fibre `F`, a **loss profile** is a vector in `R_+^F`. Define `P(F,Q)` recursively.

### Terminal profiles

For every action `a`, include

`p_a(x) = R(a,x)` for `x in F`.

Registered defer/route profiles are included in the same way after conversion to common-oracle excess loss.

### Refinement profiles

For `q in Q`, let the nonempty observation children be

`F_o = {x in F : h_q(x)=o}`.

Choose independently one child profile `p_o in P(F_o,Q\{q})` for every attained observation. Their parent profile is

`p(x) = c_q(x) + p_{h_q(x)}(x)`.

Include every such profile.

### Theorem C-R12.1 — exact deterministic adaptive value

The exact robust value of deterministic adaptive refinement is

`V(F,Q) = min_{p in P(F,Q)} max_{x in F} p(x)`.

#### Proof

Proceed by induction on `|Q|`. With no remaining refinement, every policy is a terminal leaf, exactly the terminal-profile set above. For nonempty `Q`, the root of any policy is either a terminal leaf or one refinement `q`. After observing `o`, the continuation is an arbitrary policy on `F_o` using `Q\{q}`; by induction its statewise losses are exactly one profile in `P(F_o,Q\{q})`. Adding the statewise acquisition charge produces exactly the refinement profile above. Conversely, every recursively constructed profile specifies a root choice and one valid continuation per child, hence a valid policy. Taking the minimum infinity norm therefore gives the exact robust policy value. ∎

This theorem does not require acquisition charge to be constant on a fibre or child. It only requires the statewise charges, observations, terminal profiles, and admissible finite decision-tree language to be frozen.

## 4. Exact Pareto pruning

For profiles on the same fibre, write `p <= p'` when `p(x) <= p'(x)` for every state.

### Theorem C-R12.2 — dominated profiles may be deleted

Deleting every componentwise dominated profile at every recursive state leaves `V(F,Q)` unchanged. More strongly, a dominated child profile can never be needed by any ancestor policy.

#### Proof

At the current node, replacing `p'` by `p <= p'` cannot increase `max_x p(x)`. At an ancestor refinement, both profiles receive the same nonnegative statewise charges on the same child coordinates, so the dominance relation is preserved. Cartesian combination with profiles from other children also preserves it coordinatewise. Induction up the tree proves that no dominated child can improve an ancestor profile. ∎

Therefore an exact implementation may retain only the Pareto antichain of achievable loss profiles. The antichain can still be exponentially large; this is an exact finite certificate, not a polynomial-time claim.

## 5. Equivalent offset Bellman recursion

The same information can be carried as a statewise sunk-cost vector. For `b in R_+^F`, define

`W(F,Q;b) = min_pi max_{x in F} [b(x) + L_pi^future(x)]`.

### Theorem C-R12.3 — exact state-augmented Bellman equation

`W` satisfies

`W(F,Q;b) = min {`

`  min_a max_{x in F} [b(x)+R(a,x)],`

`  min_{q in Q} max_o W(F_o,Q\{q}; (b+c_q)|_{F_o})`

`}`.

The root value is `V(F,Q)=W(F,Q;0)`.

#### Proof

Condition on the first policy decision. A terminal action gives the first term. A refinement incurs `c_q(x)` for the hidden state and then enters exactly one observation child; adversarial state choice is therefore the maximum child value. The continuation choices in distinct children are independent. This is the same structural induction as Theorem C-R12.1, with the accumulated prefix profile carried explicitly. ∎

The vector `b` is the profile of possible sunk costs under the common history. It need not reveal the hidden state to the policy. If realized elapsed acquisition time is itself available to the controller and may be used as information, that quantity must be included in `h_q`; doing so can split the child fibres and changes the declared representation.

## 6. Exact criterion for scalar collapse

A refinement is **cell-constant** on a current fibre when, for each attained observation `o`, there is one number `kappa(q,o)` such that

`c_q(x)=kappa(q,o)` for every `x in F_o`.

Equivalently, the acquisition charge is determined by the observation available at that child.

### Corollary C-R12.4 — valid scalar Bellman recursion

If every admissible refinement charge is cell-constant at every reachable history, then all accumulated sunk costs are constant within the current fibre and the exact recursion collapses to

`V(F,Q) = min {`

`  A(F),`

`  min_{q in Q} max_o [kappa(q,o) + V(F_o,Q\{q})]`

`}`,

where `A(F)=min_a max_{x in F} R(a,x)` after adding any registered terminal defer profiles.

#### Proof

The root offset is constant. On a child, adding a child-constant charge preserves a constant offset; sums of charges along a fixed observation history remain constant. Subtracting that common offset leaves exactly the displayed scalar recursion. ∎

### Theorem C-R12.5 — cell constancy is the universal scalarization boundary

For a nonempty finite child `G` and charge vector `c in R_+^G`, there exists a scalar `kappa(c)` satisfying

`max_{x in G}[c(x)+ell(x)] = kappa(c) + max_{x in G} ell(x)`

for **every** nonnegative continuation profile `ell` if and only if `c` is constant on `G`. In that case `kappa(c)` is that common value.

#### Proof

If `c` is constant, the identity is immediate. Conversely, set `ell=0`; then any valid scalar must be `kappa(c)=max_x c(x)=M`. If `c` is nonconstant, choose `y` with `c(y)<M` and choose a continuation profile supported only at `y`, with value `t>M-c(y)`. The left side is `c(y)+t`, while the right side is `M+t`, a strict mismatch. ∎

Nonconstant charge does not imply that every particular finite application is misvalued by a scalar approximation. It means there is no continuation-independent scalar summary that is exact in general. The profile/offset state is therefore the fail-closed exact object.

## 7. Hostile same-unit counterexample

Take three states and three terminal actions with regret profiles

- `a = (0,2,100)`;
- `b = (100,100,0)`;
- `c = (3,3,3)`.

A single refinement returns observations `(0,0,1)` and has statewise acquisition charges `(2,0,0)`. All numbers use the same excess-cost unit and the same oracle baseline.

- Immediate action value is `3`, using `c`.
- On child `{x0,x1}`, action `a` has total profile `(2,2)` after acquisition.
- On child `{x2}`, action `b` has total loss `0`.
- The exact adaptive value is therefore `2`, so refinement is optimal.

The childwise-max scalar approximation charges `max(2,0)=2` and then adds the raw child action value `2`, assigning value `4` to refinement. It consequently chooses immediate action and reports root value `3`. The approximation is an upper bound, but it changes the policy decision.

## 8. Static policies are contained in adaptive policies

For a fixed feature set `J`, let its exact static robust value be

`S(J)=max_B min_a max_{x in B}[sum_{q in J}c_q(x)+R(a,x)]`,

where `B` ranges over fibres of the joint observation of `J`.

### Theorem C-R12.6 — adaptive dominance

`V(X,Q) <= min_{J subseteq Q} S(J)`.

#### Proof

An adaptive controller can acquire the members of any fixed `J` in a fixed order, ignore all intermediate observations, and choose the same terminal action as the static policy after the complete joint observation. This reproduces its statewise loss profile exactly. The adaptive optimum is no worse. ∎

The inequality can be strict even with binary features, deterministic actions, and cell-constant `0/1` feature costs.

## 9. Unbounded static-versus-adaptive gap

### Theorem C-R12.7 — ratio `k` and additive gap `k-1`

For every integer `k>=1`, there is a finite deterministic FiberGuard system with binary features, feature costs in `{0,1}`, and terminal regret in `{0,k+1}` such that

- the exact best static representation has value `k`;
- the exact adaptive refinement policy has value `1`.

Hence the static/adaptive ratio is `k` and the additive gap is `k-1`.

#### Construction

Let the states be `x_(i,b)` for `i in {0,...,k-1}` and `b in {0,1}`. There is one action for each state, with zero regret on its matching state and regret `L=k+1` on every other state.

Provide:

1. `ceil(log2 k)` zero-cost binary features revealing the branch index `i`;
2. one paid binary feature `q_i` for each branch, costing one on every state, whose output is `b` on branch `i` and zero outside that branch.

#### Static lower and upper bounds

The free index bits may be included without cost. If a static set omits `q_j`, then `x_(j,0)` and `x_(j,1)` remain in the same representation fibre. No single action is correct on both, so that fibre incurs regret at least `L=k+1>k`. Selecting every `q_i` and all free index bits identifies every state, incurs feature cost exactly `k`, and permits zero terminal regret. Thus the static optimum is exactly `k`.

#### Adaptive lower and upper bounds

Read the free index bits, then acquire only `q_i` for the revealed branch and choose the matching action. This costs one with zero terminal regret. A value below one cannot acquire any paid feature and cannot incur the positive integer mismatch loss; the free index bits alone leave the two states of each branch indistinguishable. Thus the adaptive value is exactly one. ∎

This separation is not caused by state-dependent feature costs: every paid feature has the same unit charge on every state. It isolates the value of contingent acquisition itself.

## 10. Exact adaptive ASlib discriminator unlocked by R11

The current R11 head `6f0b9a354c0f71ca744596252c74e2bf8b4a6f5b` records a positive same-corpus static discriminator on SAT12-ALL: `{Pre, lobjois}` has robust total excess `1712`, versus `12000` with no features and `16906.55` with all feature steps. Those observed values are inherited evidence, not recomputed by this R12 theorem lane.

The pinned SAT12-ALL audit can therefore support an exact adaptive comparison without changing its corpus, solver portfolio, PAR10 convention, oracle baseline, or feature-step dependency graph. This theory does not reorder R11's publication gates: the prospectively frozen held-out/generalization discriminator remains separate and should not be displaced by a same-corpus adaptive optimization.

Required adaptive arms:

1. exact profile-frontier policy with measured per-instance step costs;
2. exact offset-Bellman implementation as a differential oracle;
3. a cost-observable variant only if elapsed feature time is prospectively admitted into the representation;
4. the valid cell-constant scalar recursion on deliberately coarsened charge cells;
5. childwise maximum-charge scalarization as a hostile upper-bound control;
6. the exact best static R11 representation;
7. no-feature and all-feature baselines.

Report robust total excess, mean/median/p95 excess, decision-tree depth and leaves, number and maximum size of retained profile frontiers, feature-step use by branch, exact-solver calls, and every root/child decision changed by scalar approximation.

A positive result requires strict matched-corpus improvement over the exact best static representation after all measured feature charges. A null result is retained. Neither outcome establishes unseen-instance generalization, learned-selector superiority, production value, novelty, or journal authority.

## 11. Verification and authority boundary

`verify_fiberguard_profile_bellman_r12.py`, using the separate exact core `fiberguard_profile_bellman_r12_core.py`, independently checks:

- 240 generated general systems, comparing Pareto-frontier profiles, all explicit policy profiles, and the offset Bellman value;
- 240 generated cell-constant systems, comparing exact profiles with the scalar recursion;
- all 36 charge profiles over dimensions two and three in the finite scalar-decomposition control, with a counterexample for every nonconstant profile;
- the three-state hostile decision reversal;
- exact static optima and exact scalar adaptive values for the gap family through `k=10`.

The finite verifier is implementation corroboration only. The analytic proofs carry the finite theorem statements. External independence, nearest-work novelty, the adaptive ASlib outcome, production value, and journal authority remain `CANNOT_CHECK` or false.
