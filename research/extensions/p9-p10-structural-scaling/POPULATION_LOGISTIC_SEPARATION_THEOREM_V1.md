# Population regularized-logistic representation separation

Status: **EXACT CONTROLLED THEOREM — NO EMPIRICAL OUTCOME DEPENDENCE**

## Setup

Let odd `k`, independent uniform

`x,c in {-1,+1}^k`,

relations `r_i=x_i c_i`, sum `S=sum_i r_i`, and signed label

`Z=sign(S)`.

Consider binary logistic population objective with positive L2 regularization `lambda>0` on feature weights:

`J(w,b)=E[ log(1+exp(-Z(w^T phi + b))) ] + (lambda/2)||w||^2`.

The intercept b is unregularized. The feature representation phi is either

- flat `F=(x,c)`, or
- relational `R=(x,r)`.

The distribution has full support, k is odd so S is never zero, and the label is balanced.

## Theorem 1 — flat population logistic optimum is the zero classifier

For flat features `F=(x,c)`, the unique population minimizer is

`w*=0, b*=0`.

### Proof

The logistic objective is differentiable and convex in `(w,b)`. Positive L2 regularization makes it strictly convex in w, while the population logistic term is strictly convex in b because both labels occur with positive probability.

At `(w,b)=(0,0)`, the gradient is

`grad_w J = -(1/2) E[Z F] + lambda w`,

`dJ/db     = -(1/2) E[Z]`.

The label is balanced, so `E[Z]=0`.

From Structural Accessibility Theory V2,

`E[Z x_i]=E[Z c_i]=0`

for every coordinate, hence `E[Z F]=0`.

Therefore the full gradient vanishes at `(0,0)`. For a differentiable convex objective, any stationary point is a global minimizer. Strict convexity gives uniqueness. QED.

The predicted probability is therefore 1/2 everywhere. Any deterministic tie convention gives population accuracy 1/2 because the labels are balanced.

This is stronger than saying the task is not linearly separable: for the exact regularized logistic population objective, flat raw coordinates asymptotically select the chance classifier.

## Lemma — x is independent of (r,Z)

The map `(x,c) -> (x,r=x*c)` is a bijection of the uniform Boolean cube. Hence `(x,r)` is uniform on `{-1,+1}^{2k}`: x and r are independent uniform sign vectors. Since Z is a deterministic function of r, x is also independent of `(r,Z)`.

## Theorem 2 — relational population optimum ignores x

For relational features `R=(x,r)`, every population minimizer has zero weight on x.

### Proof

Fix any relation weights v and intercept b, and write the logit as

`a(r)=v^T r+b`

plus nuisance term `u^T x`.

Condition on `(r,Z)`. Because x is independent and symmetric with `E[x]=0`, the logistic loss as a function of the logit is convex, so Jensen gives

`E_x[ell_Z(a(r)+u^T x)] >= ell_Z(a(r)+E_x[u^T x]) = ell_Z(a(r))`.

Positive L2 regularization adds `(lambda/2)||u||^2`, strictly increasing for nonzero u. Thus replacing u by zero strictly improves the objective whenever u is nonzero. QED.

## Theorem 3 — relation weights are equal and the intercept is zero

The unique relational population minimizer has the form

`w_x=0`,

`w_r=alpha * (1,...,1)`,

`b=0`

for some scalar alpha.

### Proof

After Theorem 2, the objective depends only on r, Z, relation weights and b.

The joint distribution of `(r,Z)` is invariant under every permutation of the k relation coordinates. The objective is also invariant under the corresponding permutation of the relation weights. Because the L2-regularized population objective has a unique minimizer, that minimizer must be fixed by every coordinate permutation; therefore all relation weights are equal to a common alpha.

The transformation `r -> -r` preserves the distribution of r and sends `Z -> -Z`. With equal relation weights, this symmetry maps intercept b to `-b` without changing the objective. Uniqueness therefore forces `b=0`. QED.

## Theorem 4 — alpha is strictly positive

At alpha=0, b=0, the directional derivative along the all-ones relation vector is

`-(1/2) E[Z S] = -(1/2) E[|S|] < 0`.

The L2 derivative is zero at alpha=0. Hence moving to positive alpha decreases the objective, so the unique minimizer must satisfy `alpha>0`. QED.

## Corollary — relational population classification is exact

The learned population logit is

`alpha sum_i r_i = alpha S`

with alpha positive. Therefore its sign is

`sign(alpha S)=sign(S)=Z`

on every point in the support.

Thus the population 0-1 classification accuracy is exactly 1.

## Controlled representation-learning separation

For every odd k and every positive L2 regularization strength:

- flat raw coordinates: population regularized-logistic optimum predicts probability 1/2 everywhere and has accuracy 1/2;
- relational coordinates: population regularized-logistic optimum has accuracy 1.

Yet the flat and relational full-state representations are bijectively equivalent and both determine the label exactly.

This is an exact **algorithm-and-representation-specific population separation**. It complements the finite-sample experiments, which quantify how quickly empirical regularized logistic regression approaches these qualitatively different population regimes.

## Nonclaims

The theorem does not say:

- every linear classifier trained with every loss is limited to 1/2 on flat coordinates;
- no finite-sample flat logistic fit can exceed chance;
- all invertible reparameterizations create the same separation;
- transformers optimize this population objective;
- explicit multiplication is computationally free in an arbitrary architecture.

It establishes the separation only for the stated distribution, representations and regularized logistic population objective.
