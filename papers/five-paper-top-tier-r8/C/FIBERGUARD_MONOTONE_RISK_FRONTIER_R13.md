# FiberGuard R13 — a risk-complete deterministic profile frontier

Date: 2026-08-26

Status: narrow analytic child of `FIBERGUARD_PROFILE_BELLMAN_R12.md`. Randomized minimax policies and dual Bayes certificates belong to PR #1456 and are deliberately excluded here. Held-out coverage and inductive transfer belong to PRs #1457 and #1460.

## Review lenses

This tranche was reviewed as a finite decision-theory statement, a multiobjective-order statement, an active-acquisition instantiation, a certificate-design claim, and a hostile novelty/authority claim.

## 1. Frozen profile universe

Let `F` be a finite information fibre and let `Pi_D(F,Q)` be the finite deterministic adaptive policy language frozen in R12. Every policy has one common-oracle statewise excess-loss profile

`L_pi in R_+^F`.

Let

`P(F,Q)={L_pi: pi in Pi_D(F,Q)}`

and order profiles componentwise. Its lower Pareto frontier is

`A(F,Q)={p in P: no distinct q in P satisfies q<=p}`.

A risk functional `rho:R_+^F -> R` is **monotone** when `p<=q` implies `rho(p)<=rho(q)`. No convexity, continuity, differentiability, or linearity is assumed.

Examples include maximum loss, any fixed nonnegative weighted expectation, maximum over a registered family of priors, top-k mean, fixed-distribution CVaR, and threshold-excess penalties.

## 2. Universal monotone-risk sufficiency

### Theorem C-R13M.1 — risk-complete frontier

For every monotone risk functional `rho`,

`min_(pi in Pi_D) rho(L_pi) = min_(p in A(F,Q)) rho(p)`.

#### Proof

Every profile outside the finite frontier is dominated by another attainable profile. Repeating strict dominance terminates at a frontier profile `a<=p`. Monotonicity gives `rho(a)<=rho(p)`. Therefore no deleted profile can improve the optimum, while every frontier profile remains attainable. ∎

The exact R12 profile frontier is thus a reusable deterministic certificate for every monotone risk evaluated on the same frozen states, oracle baseline, acquisition costs, observation map, and policy language.

A change to any of those objects invalidates automatic reuse.

## 3. Minimality among attainable-profile summaries

### Theorem C-R13M.2 — unique inclusion-minimal attainable summary

Among subsets of `P(F,Q)`, the frontier `A(F,Q)` is the unique inclusion-minimal subset that preserves the optimum of every monotone risk functional.

For each frontier profile `a`, define

`rho_a(z)=max_(x in F) max(0,z(x)-a(x))`.

Then `rho_a(a)=0`, while `rho_a(p)>0` for every distinct attainable profile `p`.

#### Proof

If a distinct attainable `p` had `rho_a(p)=0`, then `p<=a`, contradicting nondominance of `a`. Hence `a` is the unique minimizer of the monotone functional `rho_a`. Every summary preserving every monotone-risk optimum must retain `a`. Theorem C-R13M.1 proves that retaining all frontier points is sufficient. ∎

The qualifier **attainable-profile** is essential. A synthetic relaxation or lower-bound object can be smaller, but it is not a policy certificate until realized.

### Corollary C-R13M.3 — post-registration reuse

After the exact frontier is content-bound, a newly registered monotone risk can be optimized by evaluating only frontier profiles; the adaptive tree search need not be rerun. This is valid only when the new risk does not change the policy universe or profile coordinates.

## 4. Weighted sums are not risk-complete

### Proposition C-R13M.4 — unsupported deterministic robust optimum

For the attainable profiles

`p_1=(0,3)`, `p_2=(3,0)`, `p_3=(2,2)`,

`p_3` is the unique minimizer of worst-state loss, with value 2. No weighted sum with nonnegative normalized weights `(w,1-w)` selects it.

Indeed, `p_3` can beat `p_1` only when `w<=1/3`, and can beat `p_2` only when `w>=2/3`. The requirements are incompatible.

Therefore sweeping expected-loss weights is not an exact replacement for the deterministic robust frontier. The generic supported/unsupported distinction is donor-owned multiobjective theory.

## 5. Exact certificate format

A deterministic risk-complete receipt should bind:

1. the ordered hidden-state coordinates and common-oracle definition;
2. the deterministic policy-language digest;
3. every frontier profile and one realizing policy-tree digest;
4. pairwise nondominance;
5. a domination witness for every removed profile, or a replayable recursive pruning trace;
6. the selected monotone-risk functional and value on every frontier profile; and
7. a typed terminal separating deterministic profile authority from randomized expected and pathwise semantics.

For large frontiers, the receipt may store content hashes and immutable external locations, but the verifier must reconstruct the coordinate order and dominance relation.

## 6. Relation to the other FiberGuard children

- PR #1456 owns randomized convexification, sparse mixed-policy upper certificates, dual adversarial priors, and Bayes recursion.
- PR #1457 establishes the adverse held-out result for exact numeric equality.
- PR #1460 owns coverage tax and valid inductive certificate boundaries.

This child contributes only the deterministic universal monotone-risk sufficiency/minimality theorem and the unsupported-scalarization control. It neither duplicates nor widens those other claims.

## 7. Prior-art and novelty boundary

Pareto antichains, isotone objectives, multiobjective dynamic programming, supported versus unsupported points, and active feature acquisition are donor-owned. The theorem is elementary order theory.

The candidate paper-specific value is that R12's exact common-oracle adaptive loss profiles become one content-bound certificate reusable across all monotone deployment risks, with an explicit proof that every retained attainable policy profile is necessary for some monotone criterion.

External novelty review remains required. The correct current terminal is `NOVELTY_NOT_ESTABLISHED`.

## 8. Verification

`verify_fiberguard_monotone_risk_frontier_r13.py` checks:

- all 766 nonempty subsets of `{0,1,2}^2` and `{0,1}^3`;
- 1,058 strict isotone separators;
- 16,080 complete-small-panel monotone-risk equalities;
- 80 generated adaptive FiberGuard systems using the R12 exact profile generator; and
- 101 weighted-sum grid points rejecting the unsupported robust optimum.

The analytic proofs own the universal statements. The verifier is finite corroboration only.

## 9. Peer-review gates

Before top-tier submission, require:

1. independent proof reconstruction of C-R13M.1–C-R13M.4;
2. a structurally independent frontier generator/checker;
3. specialist review against multiobjective-DP and isotone-optimization literature;
4. exact receipt-size and resource reporting on the intended application subjects;
5. clear separation from randomized expected, pathwise, and inductive-coverage claims; and
6. external adjudication of whether the common-oracle certificate instantiation is a publishable residual.

Green CI does not establish novelty, held-out value, production utility, peer-review acceptance, or journal authority.
