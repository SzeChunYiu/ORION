# FiberGuard R13 — risk-complete profile frontiers and the randomized-certificate boundary

Date: 2026-08-26

Status: analytic extension of `FIBERGUARD_PROFILE_BELLMAN_R12.md`. The R12 loss-profile recursion supplies the finite attainable profile set. This note identifies the exact information carried by its Pareto frontier, separates deterministic robust certification from randomized expected guarantees, and gives finite primal/dual receipts. Generic Pareto theory, scalarization theory, finite minimax duality, and active feature acquisition are donor-owned. Novelty and journal authority remain open.

## Review roles used in this tranche

The argument was developed and attacked from five independent perspectives:

1. **Finite decision theorist** — freezes the policy language, common-oracle losses, and risk semantics.
2. **Multiobjective optimizer** — audits Pareto sufficiency, minimality, and unsupported solutions.
3. **Game theorist** — owns the mixed-policy LP, dual adversarial distribution, and sparse support certificate.
4. **Active-acquisition specialist** — separates this exact finite result from learned AFA and POMDP methods.
5. **Hostile authority reviewer** — prevents an expected mixed guarantee from being reported as a pathwise certificate and preserves null/novelty-subsumed terminals.

These are analysis roles, not external peer-review credentials.

## 1. Frozen deterministic profile set

Let `F` be a nonempty finite information fibre. Let `Pi_D(F,Q)` be the finite deterministic adaptive policy class declared in R12, including terminal actions, registered defer/route profiles, admissible refinements, observation partitions, dependency constraints, and statewise acquisition charges.

Every policy `pi` has a complete common-oracle excess-loss profile

`L_pi = (L_pi(x))_(x in F) in R_+^F`.

Write

`P(F,Q) = {L_pi : pi in Pi_D(F,Q)}`.

All profiles use the same statewise oracle baseline. A vector with feature cost plus absolute defer cost is not admissible until the defer cost is converted to common-oracle excess as in R12.

For profiles `p,q`, write `p <= q` when `p(x) <= q(x)` for every state. The deterministic lower Pareto frontier is

`A(F,Q) = {p in P(F,Q) : no distinct q in P(F,Q) satisfies q <= p}`.

R12 proves that `A(F,Q)` can be computed recursively by deleting componentwise dominated child profiles.

A **monotone risk functional** is any map `rho : R_+^F -> R` satisfying `p <= q => rho(p) <= rho(q)`. Examples include worst-state loss, a fixed weighted expectation, maximum over a registered scenario family, top-k mean, fixed-distribution CVaR, and threshold-excess penalties. No convexity, continuity, or linearity is required below.

## 2. The frontier is a risk-complete certificate

### Theorem C-R13.1 — universal monotone-risk sufficiency

For every coordinatewise nondecreasing risk functional `rho`,

`min_(pi in Pi_D) rho(L_pi) = min_(p in A(F,Q)) rho(p)`.

#### Proof

Every profile outside `A(F,Q)` is dominated by another attainable profile. Because the set is finite, repeatedly following a strict dominance relation terminates at a frontier profile `a <= p`. Monotonicity gives `rho(a) <= rho(p)`. Hence no deleted profile can improve the optimum, while every frontier profile remains attainable. ∎

The R12 frontier is therefore not merely a data structure for the infinity norm. It is an exact reusable certificate for every subsequently registered monotone risk criterion on the same frozen policy language and statewise loss coordinates.

### Theorem C-R13.2 — unique inclusion-minimal attainable summary

Among subsets of the attainable set `P(F,Q)`, the frontier `A(F,Q)` is the unique inclusion-minimal subset that preserves the optimum of **every** monotone risk functional.

For each `a in A(F,Q)`, define the monotone separator

`rho_a(z) = max_(x in F) max(0, z(x)-a(x))`.

Then `rho_a(a)=0`, while `rho_a(p)>0` for every distinct `p in P(F,Q)`.

#### Proof

If a distinct attainable `p` had `rho_a(p)=0`, then `p <= a`, contradicting that `a` is nondominated. Thus `a` is the unique minimizer of `rho_a` over the attainable profiles. Any attainable-profile summary preserving all monotone-risk optima must retain every `a`. Theorem C-R13.1 shows that retaining exactly the frontier is sufficient. ∎

This minimality is restricted to summaries made of attainable profiles. Synthetic lower bounds or relaxations can be smaller but are not policy certificates unless separately realized.

### Corollary C-R13.3 — one computation, many preregistered risks

Once the exact deterministic frontier is frozen and content-bound, evaluating a new monotone risk does not require rerunning the adaptive search. It requires only evaluating `rho` on the frontier. If the policy language, observation map, cost profile, oracle baseline, or state set changes, the old frontier has no automatic authority.

## 3. Weighted sums do not recover every robust policy

Weighted sums recover supported points of a lower convex envelope; they need not recover every deterministic Pareto point.

### Proposition C-R13.4 — an unsupported deterministic minimax optimum

Consider the attainable profiles

`p1=(0,3)`, `p2=(3,0)`, `p3=(2,2)`.

The deterministic worst-state optimum is `p3` with value `2`. Yet no nonnegative weighted sum with weights `(w,1-w)`, `0<=w<=1`, selects `p3`:

- `p3` beats `p1` only if `2 <= 3(1-w)`, hence `w <= 1/3`;
- `p3` beats `p2` only if `2 <= 3w`, hence `w >= 2/3`.

The conditions are incompatible.

Therefore a sweep over expected losses or preference weights is not an exact substitute for the deterministic FiberGuard frontier. This is a standard multiobjective-optimization limitation, not a standalone novelty claim.

## 4. Randomized adaptive policies convexify the frontier

A randomized policy may randomize at the root or after observations. In the finite perfect-recall tree used here, sampling all local coins in advance induces a distribution over deterministic policy trees. Conversely, any distribution over deterministic trees is implementable. Hence the statewise **expected** loss profiles of randomized policies are exactly

`conv(P(F,Q)) = conv(A(F,Q))`.

The second equality holds because every dominated deterministic profile can be replaced in a mixture by an attainable frontier profile that is componentwise no larger.

Define the worst-state expected-loss value

`V_exp(F,Q) = min_(v in conv(A)) max_(x in F) v(x)`.

### Theorem C-R13.5 — exact mixed-policy minimax dual

Let `Delta(A)` be distributions over frontier policies and `Delta(F)` distributions over states. Then

`V_exp = min_(lambda in Delta(A)) max_(x in F) sum_(p in A) lambda_p p(x)`

`      = max_(mu in Delta(F)) min_(p in A) sum_(x in F) mu_x p(x)`.

Moreover, an optimal policy mixture exists with support at most `|F|`.

#### Proof

The first expression is the definition of the convexified worst-state expected profile. The equality is finite zero-sum minimax/linear-programming duality. In a primal basic feasible solution, if `s` policy weights are positive, the simplex equality and `s` independent active state-loss constraints determine those weights and the value. There are at most `|F|` state constraints, so `s<=|F|`. ∎

### Exact receipt

A finite randomized certificate should include:

- frontier-profile digests and the common coordinate order;
- exact rational policy weights `lambda`;
- the resulting expected loss at every state;
- exact rational dual state weights `mu`;
- the common primal/dual value;
- active policy and state constraints;
- direct feasibility and complementary-slackness checks; and
- an explicit semantics tag: `WORST_STATE_EXPECTED_LOSS`.

The dual `mu` is an adversarial certificate, not an empirical prevalence estimate.

## 5. Expected and pathwise authority are different

For a randomized policy distribution `lambda`, define its pathwise value

`R_path(lambda) = max_{p in supp(lambda)} max_{x in F} p(x)`.

This requires every realized random seed to satisfy the bound.

### Theorem C-R13.6 — randomization cannot improve a pathwise robust certificate

`min_lambda R_path(lambda) = min_(p in A) max_x p(x)`.

#### Proof

Every nonempty mixture support contains at least one deterministic profile, so its pathwise maximum is at least the best deterministic robust value. A point mass on a best deterministic profile attains equality. ∎

Thus a mixed policy may improve worst-state **expected** loss while providing no better per-execution certificate. Manuscripts, APIs, and experiments must report which semantics is used. A claim about expected randomization may not be promoted as a hard answer/refine/defer safety guarantee.

## 6. Exact hostile controls

### C-R13.H1 — unsupported robust point and strict randomization gain

For `((0,3),(3,0),(2,2))`:

- deterministic worst-state value: `2`, attained by the unsupported profile `(2,2)`;
- randomized worst-state expected value: `3/2`, attained by the half-half mixture of `(0,3)` and `(3,0)`;
- dual certificate: the uniform distribution over the two states;
- pathwise randomized value: `3` for that half-half mixture, and exact optimal pathwise value `2` using the deterministic robust profile.

This control simultaneously catches weighted-sum incompleteness and expected/pathwise laundering.

### Theorem C-R13.7 — unbounded price of deterministic certification

For every `n>=1`, take `n` states and `n` deterministic profiles `e_1,...,e_n`, where `e_j` has loss one at state `j` and zero elsewhere.

- every deterministic profile has worst-state value `1`;
- every randomized expected profile has coordinate sum one, hence maximum at least `1/n`;
- the uniform mixture attains `(1/n,...,1/n)`;
- the deterministic-to-randomized expected ratio is exactly `n`;
- the optimal pathwise value remains `1`.

The gap is a semantics theorem, not evidence that randomized deployment is safer. It quantifies how much expected mixing can outperform a certificate that must hold for each realized policy.

## 7. Exact algorithmic consequence

For one frozen FiberGuard instance:

1. compute the deterministic R12 frontier once;
2. retain it as the unique minimal attainable certificate for all monotone risks;
3. optimize any registered deterministic monotone risk directly over that frontier;
4. for worst-state expected randomization, solve the finite LP over the same frontier;
5. emit primal and dual rational receipts;
6. report the deterministic robust, randomized expected, and randomized pathwise values separately.

The frontier may be exponentially large. The LP is polynomial in the materialized frontier size, but this note makes no polynomial-time claim for frontier generation.

## 8. Nearest-work subtraction

The following areas are expressly donor-owned:

- multiobjective dynamic programming and Pareto curves for MDPs;
- exact or approximate Pareto-front discovery;
- Bellman–Pareto constructions in vector games;
- weighted-sum, Chebyshev, and hypervolume scalarization;
- finite minimax duality and sparse mixed strategies;
- active feature acquisition, feature-cost decision trees, and active-acquisition POMDPs.

In particular, the phrase **Bellman–Pareto frontier** is already used in current learning theory and is not claimed here. The conservative paper-specific residual is:

1. the common-oracle statewise loss-profile object induced by exact finite representation fibres;
2. its unique minimal attainable sufficiency for all monotone risk criteria;
3. an exact sparse primal/dual receipt for worst-state expected randomization; and
4. a fail-closed distinction between deterministic/pathwise certification and randomized expected performance in answer/refine/defer systems.

Even this residual may be subsumed by broader multiobjective decision theory. External novelty review remains required.

## 9. Consequences for the ASlib experiment

R13 adds two optional arms to the prospectively frozen adaptive SAT12-ALL experiment requested under issue #1386:

1. deterministic exact profile-frontier policy with hard worst-state total-excess semantics;
2. randomized frontier mixture with worst-state expected total-excess semantics and a primal/dual receipt.

The randomized arm must not replace the deterministic arm. It must report seedwise/pathwise maxima, expected values, mixture support, and dual states. Same-corpus adaptive improvement remains distinct from held-out or multi-domain transfer.

## 10. Verification

`verify_fiberguard_risk_complete_frontier_r13.py` performs independent finite controls:

- every nonempty subset of `{0,1,2}^2` and `{0,1}^3`;
- strict monotone separators for every frontier point;
- 16,080 monotone-risk preservation equalities;
- 298 generated finite zero-sum games with exact rational primal/dual equality, support bounds, and full-set/frontier equality;
- 60 generated adaptive FiberGuard systems using the R12 exact profile generator;
- the unsupported robust profile and exact `3/2` mixed value;
- the deterministic/randomized/pathwise gap family through `n=12`.

The analytic proofs own the all-finite statements. The verifier is finite corroboration and mutation-sensitive receipt generation only.

## 11. Peer-review and authority gates

Before a top-tier submission may present this as more than a scoped exact theorem, require:

1. independent rederivation of C-R13.1–C-R13.7;
2. an independent LP/game implementation and receipt checker;
3. a current multiobjective-DP/AFA/scalarization novelty audit;
4. the exact adaptive ASlib experiment, with null and resource-exhaustion terminals;
5. held-out and multi-domain evaluation selected without target-outcome inspection;
6. explicit expected-versus-pathwise language in theorem, experiment, abstract, and limitations; and
7. external reviewer adjudication of the claimed residual.

Internal CI, exact finite receipts, or a positive same-corpus result do not grant unseen-instance generalization, production value, novelty, peer-review acceptance, or journal authority.
