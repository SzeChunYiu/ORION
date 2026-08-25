# Mathematical Extensions R5 — Data Processing and Stable Near-Collision Lower Bounds

Date: 2026-08-25

Canonical predecessors: `MANUSCRIPT_V3_PIPELINE.md` and `MATHEMATICAL_EXTENSIONS_R4.md`

Status: rigorous representation-theory addendum. The general minimax ideas are classical optimal-recovery and decision-theory tools; the paper-specific contribution remains the construction and exact solution of scalable compiler fibers.

## 1. Purpose

R4 turned exact feature collisions into deterministic, randomized, squared-loss, interval, and structural lower bounds. Two practical questions remained. Does throwing away still more information ever help? And what remains when features are only approximately equal rather than bitwise identical? This addendum answers both.

## 2. Exact sufficiency criterion

Let `Phi:X->Y` and `T:X->R`. Fibers may now be arbitrary sets, provided `T` is bounded above and below on each nonempty fiber. Define

`d_y=sup_{x in F_y}T(x)-inf_{x in F_y}T(x)`.

**Theorem C8 (exact representation sufficiency).** There exists a representation-only function `g` satisfying

`g(Phi(x))=T(x)` for every `x`

if and only if `d_y=0` for every fiber.

**Proof.** If such `g` exists, all members of a fiber receive the same target value, so the diameter is zero. Conversely, if every fiber has one target value, define `g(y)` to be that value on `Phi(X)`. ∎

Thus sufficiency is query-specific and has an exact test: the target must factor through the representation.

## 3. Global radius beyond finite instance sets

**Theorem C9 (bounded-fiber minimax radius).** For arbitrary `X` with bounded scalar target on every fiber,

`inf_g sup_x |g(Phi(x))-T(x)| = (1/2) sup_y d_y`.

A fiberwise midpoint of the infimum and supremum attains the bound whenever the global right-hand side is finite.

**Proof.** The endpoint argument from R4 applies to the infimum and supremum of each bounded fiber, using limits if an endpoint is not attained. A midpoint controls the whole interval containing the target range. Taking the supremum over fibers gives the result. ∎

The finite theorem in R4 is the attained-endpoint specialization.

## 4. Data processing under representation coarsening

Let `Psi=h o Phi` for an arbitrary map `h`. Then `Psi` is a coarsening of `Phi`: every `Psi` fiber is a union of `Phi` fibers.

**Theorem C10 (representation data processing).** For every scalar target,

`sup_z diam T(Psi^{-1}(z)) >= sup_y diam T(Phi^{-1}(y))`.

Consequently, the exact worst-case absolute, integer, squared-loss, and valid-interval radii from R4 cannot improve after deterministic coarsening.

**Proof.** Every nonempty `Phi` fiber lies inside one `Psi` fiber. The target diameter of a superset is at least the diameter of the subset. Take the supremum and apply the R4 radius formulas. ∎

This gives a monotone partial order on feature maps. Adding information may reduce ambiguity; deterministic post-processing cannot.

## 5. Stable lower bounds for approximate collisions

Let `(Y,d)` be a metric feature space and restrict attention to estimators `g:Y->R` that are `L`-Lipschitz. Suppose two instances satisfy

`d(Phi(x),Phi(x'))<=epsilon`

and have target gap

`Delta=|T(x)-T(x')|`.

**Theorem C11 (Lipschitz near-collision law).** Every such estimator satisfies

`max{|g(Phi(x))-T(x)|, |g(Phi(x'))-T(x')|}`

`>= (Delta-L epsilon)_+/2`,

where `u_+=max(u,0)`.

Under squared loss, the worst of the two squared errors is at least

`(Delta-L epsilon)_+^2/4`.

**Proof.** By the triangle inequality and Lipschitz continuity,

`Delta <= |T(x)-g(Phi(x))| + |g(Phi(x))-g(Phi(x'))| + |g(Phi(x'))-T(x')|`

`<= e_x+L epsilon+e_x'`.

Therefore `e_x+e_x'>=Delta-L epsilon`, so the larger error is at least half the positive part. Squaring gives the second statement. ∎

At `epsilon=0`, the exact two-point fiber law is recovered. For learned surrogates, the theorem says that a smooth predictor cannot jump across a target discontinuity hidden inside a small feature neighborhood.

## 6. Consequences for representation design

### 6.1 Feature ablation

If a low-order representation already has a known exact fiber diameter, removing or aggregating features cannot reduce the information-theoretic radius. Any reported improvement after ablation must come from a changed instance distribution, regularization effect, or evaluation protocol—not from increased worst-case identifiability.

### 6.2 Approximate collision benchmarks

Exact duplicate feature vectors are powerful but rare in floating-point pipelines. Theorem C11 supports a graded benchmark: search for pairs with small feature distance and large exact-target gap, then report the lower bound as a function of the predictor's measured or certified Lipschitz constant.

### 6.3 Abstention and uncertainty

A system can respond to a large fiber or near-collision obstruction by enriching its representation, widening its certified interval, or abstaining. Increasing model capacity alone does not alter the bound when the input map and regularity class are fixed.

## 7. Prior-art calibration

Worst-case optimal recovery, radii of information, two-point minimax arguments, and data-processing intuitions are established mathematics. These general theorems should be presented as the interpretive closure of the exact compiler constructions, not as a claim that midpoint recovery or feature coarsening is newly discovered. The distinctive science is the scalable Pauli-partition example in which one low-order representation is exact for a global decision but provably inadequate for value and optimizer structure.

## 8. Verification

The R5 verifier checks the global fiber radius, a strict increase under coarsening, and an equality case of the Lipschitz near-collision theorem.

## 9. Atomic status

- Exact sufficiency criterion: `VERIFIED`.
- Bounded-fiber global radius: `VERIFIED`.
- Data-processing monotonicity: `VERIFIED`.
- Lipschitz near-collision law: `VERIFIED`.
- Novelty of generic minimax machinery: `NOT_CLAIMED`.
- Exact scalable compiler fibers and their solved targets: retained as the paper-specific contribution.

## 10. Remaining scientific frontier

The next meaningful advance is to move from adversarial construction to measured prevalence. Build a corpus of real or production-derived instances, compute collisions or near-collisions for candidate feature maps, and determine whether the exact lower-bound mechanisms occur at useful scale. A second theoretical route is to characterize the minimum interaction order that makes the target factor through the representation. Repeating additional loss functions without one of those advances would now add little science.
