# Constant-Size Exact Witnesses for Fibre Action Regret — R10

Date: 2026-08-26

Status: analytic FiberGuard theorem. Helly's theorem and finite zero-sum game/minimax machinery are classical donor-owned. The residual result is the exact compression of representation-fibre regret certificates to at most the action-portfolio size, with direct consequences for collision auditing and feature refinement.

## 1. Setup

Let `F` be any finite representation fibre, let the finite action/solver portfolio be

`A={1,...,m}`,

and let `R(a,x)>=0` be the exact regret matrix relative to the full-information oracle.

Define deterministic and randomized fibre values

`V_det(F)=min_{a in A} max_{x in F} R(a,x)`,

and

`V_rand(F)=min_{p in Delta_m} max_{x in F} sum_a p_a R(a,x)`.

These are the exact worst-case losses of policies that see only the shared representation value of states in `F`.

## 2. Deterministic witness compression

### Theorem C-R10.9 — deterministic m-state witness

For every finite fibre `F`, there exists a subset `W subseteq F` with

`|W|<=m`

such that

`V_det(W)=V_det(F)`.

Equivalently,

`V_det(F)=max_{W subseteq F, |W|<=m} V_det(W)`.

### Proof

Let `v=V_det(F)`. For every action `a`, choose a state `x_a in F` attaining its worst regret on `F`:

`R(a,x_a)=max_{x in F} R(a,x)`.

Let `W={x_a:a in A}` after removing duplicates. Then `|W|<=m` and for every action

`max_{x in W} R(a,x)=max_{x in F} R(a,x)`

because `x_a in W`. Taking the minimum over actions gives

`V_det(W)=V_det(F)`.

Monotonicity under subset inclusion gives the max formulation. ∎

The witness is constructive once the exact regret matrix is available.

## 3. Randomized witness compression

### Theorem C-R10.10 — randomized m-state Helly witness

For every finite fibre `F`, there exists a subset `W subseteq F` with

`|W|<=m`

such that

`V_rand(W)=V_rand(F)`.

Equivalently,

`V_rand(F)=max_{W subseteq F, |W|<=m} V_rand(W)`.

### Proof

For tolerance `epsilon`, define

`K_x(epsilon)={p in Delta_m : sum_a p_a R(a,x)<=epsilon}`.

These are closed convex subsets of the affine simplex, whose dimension is `m-1`.

Let `v=V_rand(F)`. For any `epsilon<v`, the family `{K_x(epsilon):x in F}` has empty intersection. By Helly's theorem, some subfamily indexed by `W_epsilon` with `|W_epsilon|<=m` already has empty intersection. Hence

`V_rand(W_epsilon)>epsilon`.

There are only finitely many state subsets of size at most `m`. Suppose every such subset had randomized value strictly less than `v`. Their finite maximum would be some `u<v`; choosing `epsilon` with `u<epsilon<v` contradicts the Helly conclusion above. Therefore some subset `W`, `|W|<=m`, satisfies `V_rand(W)>=v`.

Because `W subseteq F`, monotonicity gives `V_rand(W)<=V_rand(F)=v`. Thus equality holds. ∎

## 4. Small exact certificates

The two theorems imply that **fibre cardinality is not certificate cardinality**.

Even if a lossy representation collapses millions of instances into one fibre, a worst-case regret lower certificate needs at most `m` endpoint states for an `m`-action portfolio.

A machine-readable deterministic certificate can contain:

- the common representation digest;
- at most `m` state identifiers;
- their exact regret rows;
- the claimed value `v`;
- a check that every action incurs worst regret at least `v` on the witness;
- one action attaining value `v` on the full fibre or an independently computed upper certificate.

A randomized certificate can contain:

- at most `m` state identifiers;
- their exact regret rows;
- the exact/verified finite minimax LP value;
- a primal mixed policy giving the upper bound; and
- a dual/adversarial distribution or exact LP witness giving the lower bound.

The exact certificate format should be frozen separately from the algorithm used to discover the witness.

## 5. Threshold form

### Corollary C-R10.11

For either deterministic or randomized policies and any tolerance `epsilon`, a fibre is unsafe

`V(F)>epsilon`

if and only if it contains an unsafe subset of at most `m` states.

Thus exact safety auditing for a fixed small portfolio can search for constant-cardinality witness subsets rather than reason about the whole fibre simultaneously.

The number of candidate subsets can still be large, but the witness rank is bounded by the action count rather than the number of instances.

## 6. Connection to the feature-cover theorem

The minimal deterministic and randomized conflict hypergraphs in the companion R10 notes are precisely the inclusion-minimal threshold witnesses of Corollary C-R10.11.

The witness-compression theorem therefore provides two complementary views:

1. **value view:** exact minimax fibre regret is attained on a subfibre of size at most `m`;
2. **repair view:** to guarantee regret at most `epsilon`, selected features must separate every minimal unsafe witness of size at most `m`.

This makes the action portfolio size a structural parameter of both certification and representation repair.

## 7. Solver-selection consequence

Neural/exact solver portfolios are often deliberately small even when benchmark suites contain many thousands of instances. If the final decision chooses among `m` solvers, every representation insufficiency at worst-case regret level has a certificate involving at most `m` exact instances.

This suggests a scalable hostile benchmark construction:

1. bucket instances by frozen representation;
2. search within each bucket for small high-regret witness sets;
3. publish the witness states and exact solver-cost rows;
4. verify the minimax value independently;
5. use the witness hypergraph to drive feature acquisition or abstention.

The certificate remains valid against any downstream model that receives exactly the frozen representation, regardless of model capacity or training method.

## 8. Limits

- The action portfolio must be finite and frozen. Adding actions can change both the value and witness rank.
- The theorem is worst-case; average-case risk may require distributional information.
- Exact regret rows require exact or otherwise authority-bound action costs.
- For continuous action spaces, the finite-m bound does not apply directly; an appropriate convex dimension would replace it if a suitable Helly theorem applies.
- A richer representation can separate the witness states and escape the lower certificate.

## 9. Prior-art boundary

The deterministic proof is elementary; the randomized proof is a direct Helly consequence for a finite minimax problem. Neither Helly nor small LP certificates are claimed as generic novelty.

The paper-specific contribution is their use as an exact **representation-fibre certificate theorem** for learned/exact optimization:

> with an `m`-action portfolio, every deterministic or randomized worst-case regret of a frozen representation fibre is exactly witnessed by at most `m` instances, and the same bounded-rank witnesses generate the exact feature-repair conflict hypergraph.

A current optimal-recovery, robust-classification, scenario-optimization, LP-type, and solver-selection literature audit is required before final novelty language.
