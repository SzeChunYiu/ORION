# Exact theorem: relation coordinates reduce interaction order

Status: **PROVED CONTROLLED STATEMENT — INDEPENDENT OF EMPIRICAL OUTCOMES**

## Setup

Let odd `k >= 1`, with

`x,c in {-1,+1}^k`

and binary target

`y = 1[sum_i x_i c_i > 0]`.

Define

- flat coordinates `F(x,c)=(x_1,...,x_k,c_1,...,c_k)`;
- relational coordinates `R(x,c)=(x_1,...,x_k,r_1,...,r_k)` with `r_i=x_i c_i`.

`R` and `F` are bijectively information-equivalent because `c_i=x_i r_i`.

## Theorem 1 — linear separability in relational coordinates

The target is affine-linearly separable in `R`.

### Proof

Use weight zero on the first `k` nuisance coordinates, weight one on every relation coordinate, and threshold zero. The score is

`sum_i r_i = sum_i x_i c_i`.

Because `k` is odd, the sum cannot equal zero, so its sign determines the target exactly. QED.

## Theorem 2 — no affine linear separator in flat coordinates

For every odd `k >= 1`, the target is not affine-linearly separable in `F`.

### Proof

Fix coordinates `2,...,k` so that

`sum_{i=2}^k x_i c_i = 0`.

This is possible because `k-1` is even: choose exactly `(k-1)/2` fixed pairs with product `+1` and `(k-1)/2` with product `-1`.

On this four-point restriction, the target becomes

`y = 1[x_1 c_1 > 0]`,

so the positive points in the `(x_1,c_1)` plane are `(1,1)` and `(-1,-1)`, while the negative points are `(1,-1)` and `(-1,1)`.

This is the XOR/XNOR square. The convex hull of the two positive points and the convex hull of the two negative points both contain `(0,0)`, so no affine hyperplane separates them. Any affine separator of the full flat cube would restrict to an affine separator of this four-point subset, contradiction. QED.

## Theorem 3 — exact quadratic separability in flat coordinates

The target is a degree-2 polynomial threshold in flat coordinates.

### Proof

Use polynomial score

`q(x,c)=sum_i x_i c_i`.

Every term is degree 2 in flat coordinates and, because `k` is odd, `q` is never zero on the domain. Therefore `sign(q)` classifies every point exactly. QED.

## Corollary — exact interaction-order separation

For this task family:

- relational representation requires degree `1`;
- flat representation cannot be solved by degree `1` affine thresholds;
- flat representation is solved by degree `2` polynomial thresholds.

This is an exact **representation-induced interaction-order separation** under information equivalence.

## Feature-dimension comparison used by Experiment A

A linear model on relational coordinates uses `2k` explicit input features.

The experiment's interaction-only degree-2 expansion of the `2k` flat coordinates has

`2k + C(2k,2)`

features, equal to

`2k + (2k)(2k-1)/2 = 2k^2 + k`.

Thus the expanded-flat to relational feature-dimension ratio is exactly

`(2k^2+k)/(2k) = k + 1/2`.

Across increasing `k`, relational feature dimension is linear in `k`, while the generic flat quadratic expansion is quadratic in `k`.

This dimension comparison is not a lower bound saying every flat algorithm must materialize all pairwise features. A specialized algorithm could compute the `k` correct products directly; doing so would itself amount to injecting the relation structure that the experiment is designed to study.

## ORION claim boundary

The theorem establishes a restricted but exact mathematical fact: a bijective reparameterization can reduce the interaction order needed by a bounded hypothesis class without adding information. It does not prove that transformer depth, parameter count, inference tokens, or Lean proof-search complexity obey the same separation. Those are empirical claim rungs requiring their own experiments.
