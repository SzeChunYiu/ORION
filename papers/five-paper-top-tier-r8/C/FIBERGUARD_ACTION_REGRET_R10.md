# FiberGuard Action-Regret Extension R10

Date: 2026-08-26

Status: analytic extension for solver selection, branching, routing, and other finite-action decisions. Generic minimax decision theory is donor-owned; the paper-specific contribution is the exact fibre formulation and its integration with representation refinement.

## 1. Setup

Let `X` be a finite exact instance/state space, `Phi:X->Y` a frozen representation, `A` a finite action set, and `C(a,x)` the declared deterministic cost of action `a` on instance `x`.

Examples:

- solver selection: `a` is a solver/configuration and `C` is frozen runtime, node count, or another deterministic registered cost;
- branch selection: `a` is a candidate branch and `C` is the exact downstream cost under a frozen solver state/protocol;
- compiler routing: `a` is a rewrite/search backend;
- triage: `a` is answer/refine/defer when the downstream costs are explicitly modeled.

Define the oracle cost and regret

`C*(x)=min_{b in A} C(b,x)`

and

`R(a,x)=C(a,x)-C*(x) >= 0`.

For a representation value `y`, let `F_y={x:Phi(x)=y}`.

## 2. Exact deterministic representation regret

### Theorem C-R10.1

The exact worst-case regret of the best deterministic policy that receives only `Phi(x)` is

`rho_det(Phi)=max_y min_{a in A} max_{x in F_y} R(a,x)`.

### Proof

A deterministic representation-only policy must choose one common action `a_y` for every state in the same fibre. Its worst regret on fibre `F_y` is therefore `max_{x in F_y}R(a_y,x)`. Minimizing over the common action gives the fibre value

`rho_det(F_y)=min_a max_{x in F_y}R(a,x)`.

Choices for distinct fibres are independent, so the global worst case is the maximum of these exact fibre values. ∎

This result is stronger than a label-collision statement. Two states may have different oracle actions while a single action has very small regret on both; conversely a seemingly small target collision may create large operational regret.

## 3. Epsilon-safe action sets

Define

`Safe_epsilon(F_y)={a in A : max_{x in F_y}R(a,x) <= epsilon}`.

### Corollary C-R10.2

`Safe_epsilon(F_y)` is nonempty if and only if `rho_det(F_y)<=epsilon`.

Thus FiberGuard can return a **certified action set** rather than only a scalar uncertainty interval. If the set is empty, no deterministic policy receiving only the current representation can satisfy the requested regret tolerance on that fibre.

For `epsilon=0`, the safe set consists exactly of actions that are oracle-optimal for every instance in the fibre.

## 4. Randomized policies

A randomized representation-only policy chooses `p in Delta(A)` on a fibre. Its expected regret on state `x` is

`sum_a p_a R(a,x)`.

### Theorem C-R10.3

The exact minimax expected regret on fibre `F` is the finite zero-sum game value

`rho_rand(F)=min_{p in Delta(A)} max_{x in F} sum_a p_a R(a,x)`.

It is computed by the linear program

minimize `t`

subject to

- `sum_a p_a = 1`;
- `p_a >= 0` for every action;
- `sum_a p_a R(a,x) <= t` for every `x in F`.

The global randomized representation-only value is `max_y rho_rand(F_y)`.

Unlike scalar absolute-error estimation, randomization can strictly reduce finite-action regret. The manuscript must therefore use the LP value rather than inherit the scalar endpoint argument.

## 5. Refinement monotonicity

Let `Psi` refine `Phi`, so every `Psi`-fibre is contained in a `Phi`-fibre.

### Theorem C-R10.4

Both deterministic and randomized exact minimax regret are non-increasing under refinement:

`rho_det(Psi) <= rho_det(Phi)`

and

`rho_rand(Psi) <= rho_rand(Phi)`.

### Proof

A policy using `Psi` can ignore the additional information and implement any `Phi`-policy. Equivalently, splitting a fibre allows the optimization to choose actions/distributions independently on smaller child fibres. ∎

This is an exact information monotonicity statement. It does not say that acquiring the refinement is worthwhile once acquisition cost is charged.

## 6. Cost-aware action/refine/defer Bellman recursion

For a current fibre `F`, define:

- terminal deterministic action cost `A_det(F)=rho_det(F)` or randomized action cost `A_rand(F)=rho_rand(F)`;
- abstention/defer cost `D(F)`;
- candidate refinements `r` with acquisition cost `c(r,F)` and child fibres `Child(r,F)`.

For adversarial/worst-case downstream state, the exact finite-horizon value is

`V(F)=min{ A(F), D(F), min_r [ c(r,F) + max_{G in Child(r,F)} V(G) ] }`.

The proof is standard finite dynamic programming once the state is the exact information fibre. The important FiberGuard contract is that every leaf action is justified by an exact fibre-regret certificate.

## 7. Solver-selection experiment contract

Freeze:

1. a solver portfolio `A` and exact versions/configurations;
2. an instance corpus before representation outcome review;
3. deterministic run protocol, time/resource treatment, and tie policy;
4. the exact feature map `Phi` used by the selector;
5. cost matrix `C(a,x)`;
6. candidate feature refinements and acquisition costs.

Emit per fibre:

- multiplicity;
- oracle-action set of every instance;
- deterministic `rho_det` and safe-action sets for registered tolerances;
- randomized LP value `rho_rand`;
- minimum-cost refinement/defer policy;
- endpoint/worst-regret witnesses.

Compare:

- learned selector on `Phi`;
- robust fibre action `argmin_a max_x R(a,x)`;
- randomized minimax selector where appropriate;
- always-full representation;
- uncertainty-only refinement;
- random refinement;
- oracle.

Report total cost, regret distribution, worst regret, refinement cost, defer rate, and solver overhead.

## 8. Learned branch-and-bound contract

At a frozen branch-and-bound state, let `A` be candidate branching variables/actions. Use full strong branching or another predeclared exact oracle to define `C(a,x)` or a deterministic branch-quality loss.

If two B&B states have the same model input but no common `epsilon`-safe action, then no deterministic branching policy receiving exactly that input can meet the tolerance on both states. FiberGuard then supplies a principled trigger for richer features or strong branching.

This is an information statement about the frozen input, not a lower bound for a model receiving richer solver state.

## 9. Publication boundary

Potential headline after external validation:

> Exact representation fibres yield model-independent regret certificates for solver/branch selection and an optimal finite refine-or-defer controller under declared feature costs.

Not inferred without experiments:

- prevalence of high-regret fibres in production;
- average runtime improvement;
- neural-model calibration;
- a lower bound for richer representations;
- computational hardness of learning the optimal policy.

## 10. Current external positioning

Relevant active areas include neural solver selection (ICML 2025), learned combinatorial optimization and GNN reasoning, algorithm selection from learned high-level representations (CP 2025), combinatorial optimization with predictions (ICLR 2025), and 2026 work on LLM feature extraction/algorithm selection. The exact nearest-work audit must distinguish the generic decision-theoretic minimax game from the proposed complete-fibre certificates and exact acquisition controller.
