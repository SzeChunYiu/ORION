# Randomized Safe Feature Cover via Helly Conflicts — R10

Date: 2026-08-26

Status: analytic extension of the FiberGuard action-regret and static safe-feature results. Helly's theorem and weighted SET COVER are donor-owned. The residual statement is the exact translation from randomized within-fibre regret safety to a finite conflict hypergraph over representation refinements.

## 1. Randomized action safety

Let `A={1,...,m}` be a finite action/solver portfolio and let `R(a,x)>=0` be exact regret. A randomized representation-only decision is a probability vector

`p in Delta_m`.

On state `x`, expected regret is

`rho_x(p)=sum_a p_a R(a,x)`.

For tolerance `epsilon>=0`, define the closed convex set

`K_x(epsilon)={p in Delta_m : rho_x(p)<=epsilon}`.

For a state set `W`, a common randomized decision with worst-case expected regret at most `epsilon` exists exactly when

`intersection_{x in W} K_x(epsilon) != empty`.

This is equivalent to the randomized minimax value of `W` being at most `epsilon`, as in the existing FiberGuard action-regret formulation.

## 2. Minimal randomized conflicts

A **minimal randomized epsilon-conflict** is a finite state set `W` such that:

1. all states lie in one base representation fibre;
2. `intersection_{x in W} K_x(epsilon)=empty`; and
3. every proper subset has nonempty intersection.

### Theorem C-R10.7 — Helly rank bound

Every minimal randomized epsilon-conflict has size at most `m=|A|`.

### Proof

Each `K_x(epsilon)` is a convex subset of the probability simplex. The simplex lies in the affine hyperplane `sum_a p_a=1`, which has dimension `m-1`.

If a finite family of these convex sets has empty intersection, Helly's theorem in dimension `m-1` implies that some subfamily of at most `m` members already has empty intersection. A minimal empty-intersection family therefore has cardinality at most `m`. ∎

### Tightness

Fix `m` states and choose regrets

`R(i,x_i)=1`,

`R(a,x_i)=0` for `a != i`.

For any `epsilon<1/m`, state `i` imposes `p_i<=epsilon`. All `m` inequalities are infeasible because their sum would give `1=sum_i p_i<=m epsilon<1`. Any `m-1` states are feasible by putting all mass on the omitted action. Hence the bound is tight.

## 3. Randomization changes the conflict hypergraph

Deterministic and randomized conflicts need not coincide.

With two states and two actions, let the regret rows be

`(0,1)` and `(1,0)`.

At `epsilon=1/2`, no deterministic action has regret at most `1/2` on both states, but the randomized action `p=(1/2,1/2)` has expected regret exactly `1/2` on both. Thus the pair is a deterministic conflict but **not** a randomized conflict.

A paper comparing deterministic and randomized FiberGuard policies must therefore build the appropriate conflict universe for each decision class rather than reusing deterministic labels.

## 4. Exact feature-cover theorem

Let `Phi` be the frozen base representation and let candidate finite-valued features be `f_j` with costs `c_j`.

Let `H_rand,epsilon(Phi)` be the family of all minimal randomized epsilon-conflicts contained in base fibres.

A feature `f_j` covers conflict `W` when it is nonconstant on `W`.

### Theorem C-R10.8 — randomized safe-feature cover

A selected static feature set `J` guarantees randomized minimax regret at most `epsilon` on every refined representation fibre if and only if every conflict in `H_rand,epsilon(Phi)` is separated by at least one selected feature.

Consequently minimum-cost static refinement for the randomized policy class is exactly weighted SET COVER on the randomized conflict hypergraph.

### Proof

If a conflict `W` is not separated, all its states remain in one refined fibre, whose randomized safe-region intersection is empty. Hence the guarantee fails.

Conversely, suppose some refined fibre has randomized minimax value greater than `epsilon`. Its family of `K_x(epsilon)` has empty intersection. By finiteness, it contains an inclusion-minimal empty-intersection subfamily `W`, which is a registered randomized conflict. Since all states of the refined fibre have identical selected feature values, no selected feature separates `W`, contradicting the cover assumption. ∎

The proof does not require Helly's theorem for equivalence; Helly supplies the rank bound that makes the conflict family structurally small relative to the action portfolio.

## 5. Algorithmic consequence

For fixed portfolio size `m`, every randomized conflict can be found among state subsets of size at most `m` within a base fibre. Each candidate subset is tested by a small linear-feasibility problem over the `m`-action simplex.

Thus an exact pipeline is:

1. enumerate within-fibre subsets through size `m`;
2. solve the randomized regret feasibility LP for each subset;
3. retain inclusion-minimal infeasible subsets;
4. map every candidate feature to the conflicts it separates;
5. solve the resulting weighted feature cover;
6. independently replay the refined-fibre randomized minimax LP.

For small fixed solver portfolios, the expensive dependence is in fibre size and candidate features, not the ambient model parameter count.

## 6. Static versus adaptive randomized refinement

The theorem certifies one static feature subset. The existing FiberGuard Bellman controller may instead observe a feature value and then adaptively acquire another feature, answer with a randomized policy, or defer to an exact solver.

The static cover is useful as:

- a globally safe baseline;
- an upper bound on the optimal adaptive acquisition cost;
- a certificate for deployments that require one fixed representation schema;
- a hostile comparator demonstrating whether adaptivity provides genuine acquisition savings.

It is not a lower bound on adaptive cost.

## 7. Neural solver-selection experiment

For a solver portfolio with exact or high-confidence per-instance cost matrix:

- compute deterministic conflicts and randomized conflicts separately;
- report conflict rank, count, multiplicity and target fibres;
- solve/approximate the static deterministic and randomized feature-cover problems;
- run the adaptive Bellman policy;
- compare regret, feature acquisition cost, inference latency, solver runtime and total decision cost.

A particularly informative regime is one in which deterministic conflicts are common but randomized conflicts are rare: it would show that portfolio randomization can substitute for expensive feature acquisition. The opposite regime would show that representation refinement is necessary even for mixed policies.

## 8. Prior-art boundary

Helly's theorem, randomized minimax optimization, active feature acquisition, minimum feature-set selection, and SET COVER are established. Classical minimum-feature-set formulations already separate pairs of examples with contradictory single-valued targets.

The residual claim requiring current nearest-work review is narrower:

> exact action-regret fibres induce deterministic and randomized minimal-conflict hypergraphs of rank at most the action-portfolio size; static feature acquisition guarantees a prescribed worst-case regret tolerance exactly when it covers the relevant conflict hypergraph.

The randomized conflict family is defined by convex feasibility inside the action simplex and can differ strictly from the deterministic acceptable-action conflict family.
