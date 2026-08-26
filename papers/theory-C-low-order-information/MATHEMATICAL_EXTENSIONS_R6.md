# Mathematical Extensions R6 — Metric Fiber Radii, Ambiguity Profiles, and Query Portfolios

Date: 2026-08-26

Canonical predecessors: `MANUSCRIPT_V3_PIPELINE.md`, `MATHEMATICAL_EXTENSIONS_R4.md`, and `MATHEMATICAL_EXTENSIONS_R5.md`

Status: rigorous representation-theory addendum with finite exact fixtures. The generic minimax identities are positioned as optimal-recovery closure; the paper-specific scientific contribution remains the construction and solution of scalable compiler fibers.

## 1. Argument and boundary

R5 solved scalar prediction on exact and approximate representation fibers. Many compiler questions are nevertheless vector-valued, and practical feature families are usually nested by interaction order, truncation depth, or ablation level. This addendum supplies the missing exact language for both settings.

The central object is not the diameter of a scalar interval but the Chebyshev radius of the target image inside each representation fiber. That radius gives the exact minimax error for arbitrary metric targets. It is monotone along a nested representation hierarchy and composes exactly across a finite portfolio of queries under the maximum product metric.

These are general optimal-recovery facts. No novelty is claimed for the abstract minimax machinery. Their role is to make the compiler-fiber obstruction query-complete and to define an exact minimum sufficient representation order.

## 2. Metric fiber radius

Let `Phi:X->Y` be a representation and let

`T:X->(Z,d)`

be a target in a metric space. For a nonempty fiber

`F_y=Phi^{-1}(y)`, 
define its target radius by

`rad_T(F_y)=inf_{z in Z} sup_{x in F_y} d(z,T(x))`.

Define the global representation radius

`rho(T|Phi)=sup_y rad_T(F_y)`,

where the supremum ranges over nonempty fibers. Assume this quantity is finite.

## 3. Exact metric minimax identity

**Theorem C12 (metric fiber-radius theorem).**

`inf_{g:Y->Z} sup_{x in X} d(g(Phi(x)),T(x)) = rho(T|Phi)`.

If every fiber has a Chebyshev center and the supremum is finite, a representation-only estimator obtained by choosing one center per fiber attains the bound.

**Proof.** For any estimator `g` and any fiber `F_y`,

`sup_{x in F_y} d(g(y),T(x)) >= rad_T(F_y)`.

Taking the supremum over fibers and then the infimum over `g` gives the lower bound.

For the reverse inequality, fix `epsilon>0`. For every nonempty fiber choose `z_y` with

`sup_{x in F_y} d(z_y,T(x)) <= rad_T(F_y)+epsilon`.

Define `g(y)=z_y` on `Phi(X)`. Then

`sup_x d(g(Phi(x)),T(x)) <= rho(T|Phi)+epsilon`.

Letting `epsilon` tend to zero proves equality. If exact centers exist, set `epsilon=0`. ∎

For scalar targets with absolute loss, the radius is half the fiber diameter, recovering R5. For vector targets, diameter alone generally does not determine the exact radius.

**Corollary C13 (metric sufficiency).**

The target factors exactly through `Phi` if and only if `rho(T|Phi)=0`.

**Proof.** Exact factorization gives zero radius. Conversely, if a fiber contains two target values at positive distance `delta`, every center has maximum error at least `delta/2` by the triangle inequality, so its radius is positive. Thus radius zero forces one target value per fiber. ∎

## 4. Nested ambiguity profiles

Let

`Phi_0, Phi_1, ..., Phi_m`

be representations ordered from coarse to fine, with

`Phi_i = h_i o Phi_{i+1}`.

Every `Phi_i` fiber is therefore a union of `Phi_{i+1}` fibers. Define

`rho_i(T)=rho(T|Phi_i)`.

**Theorem C14 (monotone ambiguity profile).**

`rho_0(T) >= rho_1(T) >= ... >= rho_m(T)`.

**Proof.** Every fine fiber is contained in one coarse fiber. The target radius of a subset is no larger than the radius of the containing set. Take the supremum over fine fibers. ∎

When the hierarchy terminates in a sufficient representation, define the *exact sufficient order*

`q_*(T)=min{i : rho_i(T)=0}`.

This is a target-specific order. A representation can be sufficient for a decision query and insufficient for a value or optimizer query at the same level.

## 5. Finite query portfolios

Let `T_j:X->(Z_j,d_j)` for `j=1,...,q`, and equip the product target space with the maximum metric

`d_max(z,z')=max_j d_j(z_j,z'_j)`.

Write

`T=(T_1,...,T_q)`.

**Theorem C15 (query-portfolio law).**

`rho(T|Phi)=max_j rho(T_j|Phi)`.

**Proof.** On a fixed fiber, every joint center has error at least the radius of each coordinate target, so the joint radius is at least their maximum. Conversely, choose an `epsilon`-optimal center for every coordinate. Their product center has maximum-metric error at most the maximum coordinate radius plus `epsilon`. Hence the fiber radii agree. Taking the supremum over fibers commutes with the finite maximum. ∎

**Corollary C16 (portfolio sufficient order).**

For a nested hierarchy,

`q_*(T_1,...,T_q)=max_j q_*(T_j)`

whenever all listed orders exist.

A representation is therefore exact for a declared benchmark suite only when it is exact for the hardest query in that suite. Averaging losses across queries can hide this logical requirement; the maximum-metric radius cannot.

## 6. Finite exact fixture

The R6 verifier uses four instances and three nested representations:

- `Phi_0`: constant;
- `Phi_1`: parity;
- `Phi_2`: identity.

For the value target `T_1(x)=x`, the exact radii are

`3/2, 1, 0`.

For the parity-class target `T_2(x)=0` on even instances and `4` on odd instances, the radii are

`2, 0, 0`.

For the joint target under the maximum metric, Theorem C15 gives

`2, 1, 0`.

The verifier independently groups the fibers and computes every finite Chebyshev radius. The first exact orders are two for `T_1`, one for `T_2`, and two for the joint portfolio.

## 7. Consequences for compiler representations

### 7.1 Interaction-order studies

For nested `k`-body or moment representations, the ambiguity profile

`rho_0 >= rho_1 >= ...`

is a complete worst-case diagnostic. A strict decrease quantifies how much target ambiguity the added interaction order removes. The first zero identifies exact sufficiency for the selected query.

### 7.2 Multi-output benchmarks

A benchmark that reports a global decision, an optimum value, and an optimizer structure should not treat success on one output as evidence of representation sufficiency for the others. Under the maximum metric, the joint obstruction is exactly the largest coordinate obstruction.

### 7.3 Abstention and intervals

When `rho_i>0`, additional model capacity cannot remove the worst-case ambiguity while the representation remains fixed. Valid responses are to enrich the representation, report a set or interval with the required radius, or abstain on ambiguous fibers.

## 8. Empirical protocol

The next empirical study should report an ambiguity profile rather than a single collision pair:

1. choose a nested, frozen feature hierarchy;
2. enumerate or sample exact fibers at every level;
3. solve the exact target on each instance;
4. report the maximum and distribution of fiber radii for every query;
5. identify the first exact or practically negligible order; and
6. retain near-collision Lipschitz lower bounds for floating-point representations.

Distributional prediction accuracy is complementary. It does not replace the worst-case radius.

## 9. Prior-art calibration

Chebyshev radii, radii of information, optimal recovery, and data-processing monotonicity are established mathematical tools. The paper should not frame Theorems C12–C15 as newly invented minimax theory. Their scientific role is to close the logical chain around the exact compiler constructions: the representation fibers are explicit, their targets are solved, and the resulting ambiguity profile states exactly which compiler queries the representation can and cannot determine.

## 10. Atomic status

- Metric fiber-radius identity: `VERIFIED`.
- Metric sufficiency criterion: `VERIFIED`.
- Nested ambiguity monotonicity: `VERIFIED`.
- Query-portfolio maximum law: `VERIFIED`.
- Four-instance hierarchy fixture: `FINITE_EXACT`.
- Generic optimal-recovery novelty: `NOT_CLAIMED`.
- Scalable exact compiler-fiber construction: retained as the paper-specific contribution.
- Prevalence on production-derived corpora: `UNRESOLVED`.

## 11. Remaining scientific frontier

Paper C’s theorem layer is now complete enough for submission preparation. The remaining scientific gate is prevalence: measure the ambiguity profile on real or production-derived compiler instances and determine the minimum interaction order required by each operational query. A second valuable route is a structural theorem that computes this order from the compiler interaction hypergraph. Adding further loss functions without one of these advances would broaden notation more than science.
