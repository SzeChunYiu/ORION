# Minimum Safe Feature Cover for Exact Action-Regret Certificates — R10

Date: 2026-08-26

Status: analytic extension of the FiberGuard action-regret framework. Generic SET COVER optimization/approximation is donor-owned. The paper-specific theorem identifies the exact universe that a representation repair must cover: minimal within-fibre action conflicts.

## 1. Setup

Let `X` be a finite exact instance/state space, `Phi:X->Y` a frozen base representation, `A` a finite nonempty action set, and `R(a,x)>=0` the exact regret of action `a` on state `x` under the frozen cost model.

Fix a tolerance `epsilon>=0` in the same declared unit as regret. For each state define its individually epsilon-safe action set

`B_x={a in A : R(a,x)<=epsilon}`.

For a nonempty set of states `W`, define

`Safe_epsilon(W)=intersection_{x in W} B_x`.

A state set is **unsafe** when this intersection is empty.

Only state sets contained in one base fibre of `Phi` matter, because states in different base fibres are already distinguishable.

Let candidate refinements be finite-valued features

`f_j:X->V_j`

with nonnegative acquisition costs `c_j`. A selected static feature set `J` refines the representation to

`Psi_J(x)=(Phi(x),(f_j(x))_{j in J})`.

The goal is to choose the cheapest `J` such that every `Psi_J` fibre has deterministic minimax regret at most `epsilon`, equivalently every refined fibre has a nonempty epsilon-safe action set.

## 2. Minimal action conflicts

A **minimal epsilon-conflict** is a finite state set `W` satisfying:

1. all states in `W` lie in one base `Phi` fibre;
2. `Safe_epsilon(W)=empty`; and
3. every proper subset `W' proper subset W` has `Safe_epsilon(W')` nonempty.

Let `H_epsilon(Phi)` denote the family of all minimal epsilon-conflicts.

### Theorem C-R10.5 — conflict-size bound

Every minimal epsilon-conflict has cardinality at most `|A|`.

### Proof

Let `W={x_1,...,x_m}` be minimal. For each `i`, minimality gives an action

`a_i in intersection_{j != i} B_{x_j}`.

Because the full intersection is empty, necessarily `a_i notin B_{x_i}`.

The actions `a_i` are pairwise distinct. If `a_i=a_l` for `i != l`, then the definition of `a_i` gives `a_i in B_{x_l}`, whereas the definition of `a_l` gives the same action outside `B_{x_l}`, a contradiction.

Thus `m` distinct actions exist in `A`, so `m<=|A|`. ∎

This bound is tight: with `m` actions, take `m` states where state `i` declares every action safe except action `i`.

## 3. When does a feature repair a conflict?

A feature `f_j` **separates** conflict `W` when it is not constant on `W`. Equivalently, at least two members of `W` receive different feature values.

For each candidate feature define its covered-conflict set

`C_j={W in H_epsilon(Phi) : f_j is nonconstant on W}`.

### Theorem C-R10.6 — exact safe-feature cover theorem

A selected feature set `J` guarantees deterministic regret at most `epsilon` on every refined fibre if and only if

`union_{j in J} C_j = H_epsilon(Phi)`.

Consequently, the minimum-cost static representation repair is exactly the weighted set-cover instance

- universe: `H_epsilon(Phi)`;
- set for feature `j`: `C_j`;
- weight: `c_j`.

### Proof

(**Only if.**) Suppose some minimal conflict `W` is not covered by the selected features. Then every selected feature is constant on `W`. Since `W` already lies in one base fibre, every state in `W` has the same `Psi_J` value. Therefore one refined fibre contains all of `W`, and its epsilon-safe action intersection is empty. The repair fails.

(**If.**) Suppose every minimal conflict is covered, but some refined fibre `F` is unsafe. Because `F` is finite, it contains an inclusion-minimal unsafe subset `W`. That `W` is a minimal epsilon-conflict. Since every state in `F` has the same selected feature values, every selected feature is constant on `W`, contradicting that `W` is covered. ∎

The theorem is exact for the frozen finite domain and action-cost matrix. It does not say candidate features are cheap to compute or useful off-domain.

## 4. Algorithmic consequences

The conflict-size bound makes the conflict universe explicitly enumerable for a fixed action portfolio.

For each base fibre `F`, enumerate state subsets of size at most `|A|`, test whether their safe-action intersection is empty, and retain inclusion-minimal conflicts. A direct bound is

`sum_F sum_{i=1}^{|A|} binom(|F|,i)`

candidate subsets before pruning.

Once the conflict family is materialized, exact minimum-cost repair is a weighted SET COVER instance. Standard integer programming, subset DP for small conflict universes, and standard greedy/logarithmic approximation results are donor-owned algorithms that may be applied to this derived instance.

The important FiberGuard contribution is not SET COVER itself; it is the proof that this derived conflict cover is **exactly equivalent** to a global worst-case action-regret guarantee under the selected representation.

## 5. Pair conflicts are not always enough

For two actions, every minimal conflict has size at most two, so the repair universe consists only of unsafe singletons/pairs.

For three or more actions, genuinely higher-order conflicts can occur. Example with actions `{a,b,c}`:

- state `x_1` allows `{b,c}`;
- state `x_2` allows `{a,c}`;
- state `x_3` allows `{a,b}`.

Every pair has a common safe action, but the triple has empty intersection. Any repair algorithm that searches only for pairwise label conflicts misses this unsafe fibre.

This is operationally important for solver portfolios: different instances may have different best solvers while still sharing one acceptable fallback pairwise, yet no single solver is safe across the entire representation fibre.

## 6. Dynamic versus static acquisition

The theorem above concerns a **static** selected feature set used for all states.

The existing FiberGuard Bellman recursion addresses adaptive acquisition: after observing a feature value, later refinements may depend on the child fibre. Static safe-feature cover can therefore serve as:

- a globally safe baseline;
- a lower/upper-bound ingredient for adaptive policy evaluation;
- a certificate that a published fixed feature set guarantees the requested regret tolerance.

Static and adaptive acquisition costs must not be conflated. An adaptive policy may be cheaper because it purchases different features on different branches.

## 7. Learned solver-selection application

For a frozen solver portfolio, exact cost matrix, and discrete/quantized representation:

1. compute per-instance epsilon-safe solver sets;
2. enumerate minimal within-fibre conflicts;
3. evaluate candidate features by which conflicts they separate;
4. solve or approximate the resulting weighted feature-cover problem;
5. independently replay the refined fibre regret.

Required baselines include:

- always coarse;
- always full feature set;
- cheapest individual feature;
- random feature subset at matched acquisition cost;
- uncertainty-only refinement;
- the exact or approximated conflict-cover solution;
- oracle full-information action.

Report worst and average regret separately. The theorem licenses the worst-case finite-domain certificate; average-case or deployment claims require a distribution/corpus protocol.

## 8. Prior-art boundary

Robust/minimax-regret optimization, active feature acquisition, test selection, SET COVER, and decision-sufficient representations are established subjects. Recent work also studies hardness of decision-sufficient compressed data for linear optimization.

The residual claim requiring nearest-work review is:

> exact representation fibres induce a finite family of minimal action-conflict hyperedges of rank at most the action-portfolio size, and static feature acquisition guarantees a prescribed deterministic regret tolerance exactly when the chosen features cover every such conflict.

No generic SET COVER novelty or universal learning lower bound is claimed.
