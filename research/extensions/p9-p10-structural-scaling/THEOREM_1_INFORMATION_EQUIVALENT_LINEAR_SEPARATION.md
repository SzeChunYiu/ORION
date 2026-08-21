# Theorem 1 — Information-Equivalent Representation Can Change Linear Accessibility

Status: **PROVED CONTROLLED THEOREM**
Date: 2026-08-20

This theorem is elementary and is not claimed as a new result in learning theory. Its role is to provide an exact mathematical control demonstrating the distinction used by the P9/P10 structural-scaling program: equal information does not imply equal accessibility for a restricted computation class.

## Setup

Let `n >= 2` and latent state

`z = (z_1,...,z_n) in {-1,+1}^n`.

Define the target

`y(z) = product_{i=1}^n z_i`.

Thus `y` is parity in the `{-1,+1}` convention.

Define two representations.

### Flat representation

`E_f(z) = (z_1,...,z_n)`.

### Structured representation

`E_s(z) = (z_1,...,z_{n-1}, y(z))`.

## Proposition 1 — Information equivalence

`E_f` and `E_s` are bijectively related.

### Proof

`E_f` is the identity. From `E_s(z)` we know `z_1,...,z_{n-1}` and `y`.

Because every coordinate is `+1` or `-1`, multiplication is its own inverse, so

`z_n = y * product_{i=1}^{n-1} z_i`.

Hence `z` is uniquely recoverable from `E_s(z)`. Conversely `E_s(z)` is deterministically computed from `E_f(z)`.

Therefore the two encodings contain exactly the same latent-state information and are related by an explicit bijection. QED.

## Theorem 1 — Linear accessibility separation

For every `n >= 2`:

1. `y` is perfectly linearly separable from `E_s(z)`.
2. `y` is not linearly separable from `E_f(z)` over the full hypercube.

### Proof of part 1

In `E_s`, the last coordinate equals `y` exactly. The affine classifier

`sign(w^T E_s(z) + b)`

with `w=(0,...,0,1)` and `b=0` returns `y` on every point. QED.

### Proof of part 2

Fix arbitrary values for coordinates `z_3,...,z_n` when `n>2`. Their product is a constant `c in {-1,+1}` on this two-dimensional face. Restricted to this face,

`y = c z_1 z_2`.

Multiplying labels by fixed `c` only swaps the two classes, so linear separability would imply that XOR/parity on the four points `(z_1,z_2) in {-1,+1}^2` is linearly separable.

The positive-label points for `z_1 z_2` are `(1,1)` and `(-1,-1)`, while negative-label points are `(1,-1)` and `(-1,1)`.

Their class convex hulls intersect at the origin:

`0 = 1/2 (1,1) + 1/2 (-1,-1)`

and

`0 = 1/2 (1,-1) + 1/2 (-1,1)`.

Two finite classes whose convex hulls intersect cannot be strictly separated by an affine hyperplane. Therefore no affine linear classifier separates parity on this face. Any affine separator on the full `n`-cube would restrict to an affine separator on every face, giving a contradiction.

Thus `y` is not linearly separable from `E_f`. QED.

## Corollary — Same information, different restricted risk

Under the uniform distribution on the hypercube and 0-1 loss, let `F_lin` be affine linear classifiers.

The structured representation has

`Risk_F_lin(E_s) = 0`.

The flat representation has

`Risk_F_lin(E_f) > 0`.

Therefore

`CAG_F_lin(E_s,E_f) = Risk_F_lin(E_f) - Risk_F_lin(E_s) > 0`

while `E_s` and `E_f` are bijectively information-equivalent.

The exact optimal flat linear risk is not needed for this corollary and is deliberately not asserted here.

## Interpretation

This construction proves a narrow but load-bearing point:

> Information equivalence alone does not determine computational accessibility for a restricted learner class.

The structured encoding has not added Shannon information about latent state. It has changed coordinates so that a target interaction that was inaccessible to an affine classifier becomes directly accessible.

## What this theorem does NOT prove

It does not prove:

- that LLMs are linear classifiers;
- that P9's natural structured representation is equivalent to this parity transform;
- that real-world chain-of-thought is caused by representation failure;
- that structured state always helps;
- any lower bound for transformers.

Those require empirical or additional theoretical work.

## Why it matters for P9/P10

The theorem supplies an exact existence result underlying the prospective empirical question:

> Can natural task representations used in P9/P10 create an analogous accessibility gap for bounded modern models, visible as a shift in model-scale or inference-compute requirements?

The correct experiment is therefore not merely `structured vs flat`; it is `structured vs mechanically verified same-information encoding`, crossed with computational capacity and inference budget.

## Next theorem targets

1. quantify the optimal uniform-distribution affine error for selected variants;
2. construct a naturalistic binding/composition family closer to P9 rather than parity;
3. prove a bounded-memory/finite-state separation for sequential history versus explicit predictive state;
4. formalize one controlled theorem in Lean so the mathematical foundation is machine-checked inside the same formal ecosystem used by P10.
