# Mathematical Extensions R4 — Fiber Diameter, Randomized Estimation, and Structural Prediction

Date: 2026-08-25

Canonical predecessor: `MANUSCRIPT_V3_PIPELINE.md`

Status: theorem addendum for integration into the next manuscript version. All general results below are representation theorems; the Pauli partition families in V3 provide exact fibers to which they apply.

## 1. Purpose

The V3 manuscript proves sharp lower bounds from two pair-indistinguishable compiler families. This addendum extracts the general information theorem behind those examples and extends it to randomized estimators, squared loss, valid uncertainty intervals, and optimizer-property prediction.

The result is a query-dependent theory of representation sufficiency. It applies to any finite exact optimization problem, not only the declared Pauli partition model.

## 2. Representations and fibers

Let `X` be a finite instance set, let

`Phi:X -> Y`

be a representation, and let

`T:X -> R`

be a target quantity. For `y in Phi(X)`, define the fiber

`F_y={x in X:Phi(x)=y}`

and its target range

`a_y=min_{x in F_y} T(x)`,

`b_y=max_{x in F_y} T(x)`,

`d_y=b_y-a_y`.

The number `d_y` is the target diameter invisible to the representation at `y`.

A representation-only estimator is a function `g:Y->R`. Its worst absolute error on the fiber is

`R_y(g)=max_{x in F_y}|g(y)-T(x)|`.

## 3. Exact deterministic minimax theorem

**Theorem C1 (fiber-diameter minimax law).** For every fiber,

`inf_z max_{x in F_y}|z-T(x)| = d_y/2`.

The midpoint

`z_y=(a_y+b_y)/2`

attains the infimum. Consequently,

`inf_g max_{x in X}|g(Phi(x))-T(x)| = (1/2) max_y d_y`.

**Proof.** Any common estimate `z` must approximate both endpoints. The triangle inequality gives

`|z-a_y|+|z-b_y| >= b_y-a_y=d_y`,

so at least one endpoint error is at least `d_y/2`. The midpoint has endpoint error exactly `d_y/2`, and every other target value in the fiber lies between the endpoints, so it incurs no larger error. The global problem separates fiber by fiber. ∎

This theorem is exact. It is not a hardness result and does not depend on computation time, training data, or model class. Once `Phi` identifies two different target values, the diameter is an irreducible information loss.

## 4. Integer-valued estimators

Suppose `T` takes integer values and the estimator must output an integer.

**Corollary C2 (integer radius).** The exact minimax error on a fiber is

`ceil(d_y/2)`.

**Proof.** The lower bound is the real-valued radius rounded up. An integer nearest to the midpoint attains it. ∎

For the V3 pair fiber, `d_y=2t-1`, so the exact integer radius is `t`.

## 5. Randomization does not improve worst-case absolute loss

A randomized representation-only estimator assigns to every `y` a real random variable `Z_y`; its distribution may depend on `y` but not on the hidden member of the fiber.

**Theorem C3 (randomized absolute minimax law).** For every fiber,

`inf_{Z_y} max_{x in F_y} E|Z_y-T(x)| = d_y/2`.

A deterministic midpoint is optimal.

**Proof.** For every realized value `z`,

`|z-a_y|+|z-b_y| >= d_y`.

Taking expectations gives

`E|Z_y-a_y|+E|Z_y-b_y| >= d_y`,

so one endpoint has expected loss at least `d_y/2`. The deterministic midpoint attains equality and controls every interior target. ∎

Randomization can redistribute error between indistinguishable instances, but it cannot lower the worst expected absolute error.

## 6. Squared-loss theorem

**Theorem C4 (squared minimax law).** Under squared loss,

`inf_{Z_y} max_{x in F_y} E[(Z_y-T(x))^2] = d_y^2/4`.

Again the deterministic midpoint is optimal.

**Proof.** Let `m_y=(a_y+b_y)/2`. For every real `z`,

`((z-a_y)^2+(z-b_y)^2)/2 = (z-m_y)^2+d_y^2/4`.

After taking expectations, the average of the two endpoint risks is at least `d_y^2/4`, so their maximum is at least that value. The deterministic midpoint has squared error at most `d_y^2/4` for every target between the endpoints. ∎

This result gives an exact mean-squared-error obstruction for learned regressors restricted to the representation.

## 7. Valid uncertainty intervals

Let an interval rule assign `I(y)=[L(y),U(y)]` and require exact coverage:

`T(x) in I(Phi(x))` for every `x in X`.

**Theorem C5 (minimum exact interval width).** Every exactly valid interval rule satisfies

`U(y)-L(y) >= d_y`

for every fiber. The interval `[a_y,b_y]` is width-optimal.

**Proof.** Exact coverage must include both endpoint values of the fiber. ∎

A narrow interval can therefore be invalid even when its center is an optimal point estimator. Representation-induced ambiguity must appear somewhere: in point error, interval width, or an explicit abstention.

## 8. Optimizer-property prediction

Let `P:X->{0,1}` be a Boolean property, such as “every optimum contains a block of size at least three.” A randomized representation-only classifier outputs one with probability `q(y)`.

**Theorem C6 (structural classification barrier).** If one fiber contains instances `x_0,x_1` with `P(x_0)=0` and `P(x_1)=1`, then every representation-only randomized classifier has worst-case error at least `1/2` on that fiber.

**Proof.** The two error probabilities are `q(y)` and `1-q(y)`. Their maximum is at least `1/2`; equality is attained by a fair random guess. ∎

The theorem applies equally to any optimizer property that is well-defined at the instance level: existence of a triple, uniqueness, a symmetry class, or a prescribed support pattern.

## 9. Set-valued optimizer certificates

Let `Opt(x)` be the set of exact optimizers. A representation-only procedure may return a candidate family `S(y)` guaranteed to contain at least one exact optimizer for every instance in the fiber.

**Proposition C7 (union lower bound).** Exact validity requires

`S(y) intersect Opt(x) != empty`

for every `x in F_y`. If the optimizer sets of two fiber members are disjoint, no single optimizer can be certified for both; every valid candidate family must contain at least two elements or a higher-level description intersecting both sets.

This elementary consequence is useful because value ambiguity and optimizer ambiguity need not coincide. A representation can determine the optimum value while failing to identify a common optimizer, or conversely.

## 10. Application to the pair-indistinguishable families

For the V3 families `A_t,B_t`, the representation consisting of term count, ordered weights, and complete labeled pair-gain matrix has one fiber containing target values

`Delta_A=12t-2`,

`Delta_B=10t-1`.

Thus `d_y=2t-1`.

Theorems C1–C5 give:

- exact deterministic and randomized absolute minimax error `(2t-1)/2`;
- exact integer radius `t`;
- exact worst-case squared risk `(2t-1)^2/4`;
- minimum exactly valid interval width `2t-1`.

The optimizer property “an exact optimum contains a triple block” differs across the two families: every optimum of `A_t` contains the distinguished triple, while every optimum of `B_t` uses only pairs and singletons. Theorem C6 therefore gives worst-case structural classification error at least `1/2` to every pair-information-only randomized classifier.

These conclusions strengthen the V3 result: the obstruction applies to randomized learning procedures and uncertainty quantification, not only deterministic point estimates.

## 11. Application to the high-order parity fibers

For fixed `m>=5` and `L>=1`, the V3 parity construction has a representation that records all labeled common-factor counts through order `m-2`, while its exact improvements differ by

`G(m,L)=[m(ceil(log2 m)+1)-1]L`.

Therefore every representation-only method using those proper interactions satisfies:

- worst expected absolute error at least `G(m,L)/2`;
- worst expected squared error at least `G(m,L)^2/4`;
- exact interval width at least `G(m,L)`.

For fixed `m`, every bound is unbounded in `L`. The Möbius theorem in V3 additionally shows that the invisible integer direction producing this ambiguity is the unique parity direction and has exponentially large signed support.

## 12. Representation design consequences

### 12.1 Query-specific sufficiency

A representation should be evaluated against a target query, not labeled globally “sufficient.” In the declared compiler model, pair data is complete for unary-optimality decision but incomplete for improvement value and triple-block structure.

### 12.2 Learned combinatorial optimizers

When a learned model uses only low-order features, fiber diameter supplies an architecture-independent lower bound. More data or a larger neural network cannot close a gap caused by identical inputs. The remedy is to enrich the representation, narrow the target, widen uncertainty, or abstain.

### 12.3 Benchmark construction

Indistinguishable fiber pairs are adversarial controls for surrogate optimizers. A benchmark that lacks such pairs may overstate value or structural prediction quality because it does not test whether the feature map has discarded target-relevant information.

### 12.4 Certified uncertainty

Theorem C5 gives the smallest interval that is valid solely from the representation. Any narrower interval requires additional information or a weaker coverage guarantee.

### 12.5 Static compiler triage

The four-index theorem can be used as a cheap exact decision gate. Instances that fail the gate may then be sent to a richer optimizer whose value model uses higher-order features. This is a concrete decision architecture suggested by the separation theorem, not a measured runtime result.

## 13. Relation to statistical decision theory

Two-point minimax arguments, indistinguishability, and midpoint estimators are classical. This addendum claims no generic novelty for those tools. The paper-specific contribution is the exact construction of scalable fibers inside one combinatorial compiler model, together with a low-order representation that is simultaneously complete for one global decision and incomplete for value and optimizer structure.

The manuscript should state this donor boundary explicitly: the general minimax law is the interpretive engine; the nontrivial compiler mathematics is constructing and solving the fibers and proving the four-index decision theorem.

## 14. Integration into the manuscript

1. Insert Theorems C1–C6 before the current pair-family specialization.
2. Present the existing additive, integer, and multiplicative bounds as corollaries of the fiber theorem where appropriate.
3. Add the randomized, squared-loss, interval-width, and structural-classification corollaries to the main results.
4. Reframe the Discussion around representation design, certified uncertainty, and query-specific sufficiency.
5. Keep all claims scoped to the frozen structural objective and exact declared feature maps.

## 15. Atomic claim status

- Deterministic fiber-diameter theorem: `VERIFIED`.
- Integer radius: `VERIFIED`.
- Randomized absolute minimax theorem: `VERIFIED`.
- Squared minimax theorem: `VERIFIED`.
- Exact interval-width theorem: `VERIFIED`.
- Boolean structural-classification lower bound: `VERIFIED`.
- Pair-family corollaries: `VERIFIED` from the V3 exact values and optimizer classification.
- High-order corollaries: `VERIFIED` from the V3 value-gap theorem.
- Empirical performance of a learned optimizer: `NOT_CLAIMED`.

## 16. Editorial effect

Paper C is the strongest standalone manuscript in the five-paper portfolio. The general fiber theorem broadens its readership without weakening the exact compiler core. A high-selectivity theory submission still needs a hostile replay of the partition proofs and a final primary-source audit against hierarchical-model and information-based complexity literature, but no new experiment is mathematically necessary for the stated results.