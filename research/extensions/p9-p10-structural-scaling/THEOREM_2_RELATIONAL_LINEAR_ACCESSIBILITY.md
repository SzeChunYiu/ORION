# Theorem 2 — Bijective relational coordinates change linear accessibility

Status: **PROVED FOR THE CONTROLLED CLASS**

Date: 2026-08-20

This theorem is elementary restricted-class mathematics. The novelty claim is not the XOR fact itself; its role is to make the P9 representation-accessibility hypothesis mathematically exact and to define a controlled bridge to the empirical scaling experiments.

## Setup

Let `d >= 3` be odd. Let

`x,c in {-1,+1}^d`

and define

`h(x,c) = sign(sum_{i=1}^d x_i c_i)`.

Because `d` is odd, the sum cannot be zero.

Define two representations.

### Flat representation

`F(x,c) = (x_1,...,x_d,c_1,...,c_d)`.

### Relational representation

Let

`r_i = x_i c_i`.

Define

`R(x,c) = (x_1,...,x_d,r_1,...,r_d)`.

## Theorem

For every odd `d >= 3`:

1. `F` and `R` are bijectively information-equivalent representations of `(x,c)`;
2. `h` is linearly separable in `R`;
3. `h` is not linearly separable in `F`.

Thus, for the hypothesis class of affine binary classifiers, a bijective change of coordinates can reduce zero-one approximation error from strictly positive on the complete finite support to zero without adding latent task information.

## Proof

### 1. Bijection

`R` clearly computes from `(x,c)` by `r_i=x_i c_i`.

Conversely, because `x_i^2=1`, from `(x,r)` recover

`c_i = x_i r_i`.

Therefore `(x,c) <-> (x,r)` is a bijection. Since `F` is just the direct coordinates `(x,c)`, `F` and `R` preserve exactly the same latent pair.

### 2. Linear separability in relational coordinates

In representation `R`,

`h = sign(sum_i r_i)`.

Choose affine-classifier weights zero on every `x_i`, weight `1` on every `r_i`, and intercept `0`. Since the sum is never zero, this classifier is correct on every point of the support.

Hence `h` is linearly separable under `R`.

### 3. Non-separability in flat coordinates

Assume for contradiction that an affine classifier separates `h` under `F`.

Fix coordinates `2,...,d` so their pairwise products cancel exactly. This is possible because `d-1` is even. For example set every `x_j=+1`, assign exactly `(d-1)/2` of the corresponding `c_j` values to `+1` and the remaining `(d-1)/2` to `-1`. Then

`sum_{j=2}^d x_j c_j = 0`.

On this restricted four-point subcube only `(x_1,c_1)` varies, and

`h(x,c) = sign(x_1 c_1)`.

The positive points in the varying coordinates are

`(+1,+1)` and `(-1,-1)`,

while the negative points are

`(+1,-1)` and `(-1,+1)`.

Any affine separator in the full flat space restricts, after the fixed-coordinate contribution is absorbed into its intercept, to an affine separator of these four points in `(x_1,c_1)`.

But their positive convex hull contains the origin as the midpoint of `(+1,+1)` and `(-1,-1)`, and their negative convex hull also contains the origin as the midpoint of `(+1,-1)` and `(-1,+1)`. Two strictly linearly separable finite classes must have disjoint convex hulls. Contradiction.

Therefore no affine classifier separates `h` under `F`.

QED.

## Corollary: exact computational-accessibility separation

Let `H_lin` be the affine binary-classifier family and let the evaluation distribution give positive probability to every support point. Then

`Risk_Hlin(R) = 0`

while

`Risk_Hlin(F) > 0`.

Since the representations are bijectively equivalent, this difference cannot be attributed to missing latent information. It is a representation-relative accessibility difference for the restricted hypothesis class.

## Why this controlled theorem is a better bridge than a target-coordinate toy

The relational representation does **not** append the target label. It appends pairwise state-candidate relations `x_i c_i`, from which the original candidate is exactly recoverable. The target remains a separate threshold over the relation vector.

This mirrors the substantive P9 distinction between raw/serialized fields and candidate-relative relational coordinates: the issue is not whether the facts exist somewhere in the input, but whether the relevant relation is exposed in a form a bounded learner can use directly.

## Limits

This theorem does not imply:

- that all structured encodings help;
- that LLMs are affine classifiers;
- that relational features always lower sample complexity;
- that the empirical P9 D1 effect is caused by this exact mechanism;
- that more model scale cannot recover the flat representation;
- that the coordinate transform is computationally free in a deployment system.

Those are empirical questions addressed by the frozen benchmark and, for LLMs, the separate structure-scaling protocol.
