# Saturated-conic scalar uniqueness and integral direction-floor bumps — V1

Status: **proved prime-uniform analytic theorem for odd primes `p>=7`, with finite hostile controls**. Rank-two saturation and Segre's oval theorem are donor-owned. No exact generalized Davenport value is asserted here.

## 1. Setup

Let `p>=7` be an odd prime. In `PG(2,p)` fix a full `(p+1)`-arc. By Segre's theorem it is a nondegenerate conic. After projective normalization write

`C(t)=[1:t:t^2]` for `t in F_p`, together with `C(infinity)=[0:0:1]`.

Suppose a zero-sum first-failure sequence has full multiplicity `p-1` on every conic direction. Let `D=[d_0:d_1:d_2]` be an occupied off-conic direction of deficit exactly `q-1`, so its weight is `p-q`.

Every conic secant through `D` contains exactly two full directions and `D`: any extra occupied deficient direction would make the strict rich-plane deficit requirement exceed the maximum available extra deficit. Thus every such secant has line deficit exactly `q-1` and saturates the q-dependent plane bound.

The rank-two inverse grammar therefore forces, for the actual nonzero group elements on the three directions,

`x_D=x_t+x_u`

whenever `C(t),C(u),D` are collinear on a secant.

## 2. The scalar function forced by one saturated center

Choose vector representatives

`C(t)=(1,t,t^2)`

and write

`x_t=lambda(t) C(t)`, `x_D=mu_D D`,

with nonzero scalars.

For finite distinct `t,u`, collinearity is equivalent to

`d_0 t u-d_1(t+u)+d_2=0`.

Write

`Delta_D=d_0d_2-d_1^2`.

Since `D` is off the conic, `Delta_D !=0`. If `t` is not a tangent point from `D`, the saturated-secant equation gives

> `lambda(t)=mu_D Delta_D / Q_D(t)`,
>
> where `Q_D(t)=d_0t^2-2d_1t+d_2`.

Indeed, writing `D=alpha C(t)+beta C(u)`, direct elimination gives

`alpha=Delta_D/Q_D(t)`.

The same formula remains valid when the partner of `C(t)` is the point at infinity; then `t=d_1/d_0` and both sides equal `mu_D d_0`.

The zeros of `Q_D` are exactly the finite tangent points from `D`, so at most two finite parameters are excluded.

## 3. Two distinct saturated centers are impossible

Assume two distinct occupied off-conic directions `D,E` both have deficit `q-1`. Their saturation equations must use the same actual conic elements `x_t`, hence at every finite `t` that is non-tangent for both centers,

`mu_D Delta_D / Q_D(t) = mu_E Delta_E / Q_E(t)`.

Each quadratic has at most two roots. Therefore at least

`p-4>=3`

finite values of `t` satisfy the identity. Rearranging,

`Q_E(t)=c Q_D(t)`

for the same nonzero constant `c` at at least three field elements. Two quadratic polynomials agreeing up to the same scalar at three points are proportional identically. Since

`D -> Q_D(t)=d_0t^2-2d_1t+d_2`

is an invertible linear encoding of projective coordinates in odd characteristic, `Q_E` proportional to `Q_D` implies `E=D` as projective points, contradiction.

> **Saturated-conic scalar uniqueness theorem.** For every odd prime `p>=7`, a full conic of multiplicity `p-1` can coexist with **at most one** occupied off-conic direction of deficit `q-1` whose conic secants saturate the q-dependent rank-two bound.

In the first-failure setting the secant saturation is automatic for every deficit-`q-1` off-conic direction.

The threshold `p>=7` is load-bearing. Direct finite hostile control at `p=5` finds compatible distinct saturated centers, so no `p=5` claim is made.

## 4. Conic deficit corollary

Suppose a first failure has all `p+1` conic directions full and `n>=1` additional occupied projective directions. Every off-conic occupied direction lies on at least one conic secant.

- A deficient direction of deficit `<q-1` is impossible by the three-direction plane deficit bound.
- By scalar uniqueness, at most one deficient direction has deficit exactly `q-1`.
- Every remaining deficient direction has deficit at least `q`.

Hence, for `n>=2`, the total projective deficit satisfies

> `Delta >= (q-1)+q(n-1)=qn-1`.

For `n=1`, `Delta>=q-1`.

This replaces the naive lower bound `(q-1)n` by an extra `n-1` units as soon as two off-conic directions are present.

## 5. Integral bump of the full-direction arc bound

For any first failure with `q>=2`, the existing full-direction arc argument gives

`r >= ceil((N-p-1)/(p-2))`,

where `N=|B|`.

Assume

`R=(N-p-1)/(p-2)`

is an integer and equality `r=R` holds. Then

`Delta=r(p-1)-N=r-p-1`,

so the elementary full-direction count gives

`f>=r-Delta=p+1`.

Thus all `p+1` possible full directions occur and form a conic. The remaining

`n=r-p-1=Delta`

directions have positive deficits summing to `n`, hence every one has deficit one.

Consequences:

1. If `q>=3` and `n>=1`, equality is immediately impossible because deficit one is below `q-1` on an off-conic secant.
2. If `q=2`, every off-conic direction has the minimal deficit `q-1=1`. For `p>=7` and `n>=2`, saturated-conic scalar uniqueness makes equality impossible.

Therefore:

> **Integral direction-floor bump.** Let `p>=7` be odd prime and let a first failure have length `N`.
> - If `q>=3`, `R=(N-p-1)/(p-2)` is an integer, and `R>=p+2`, then `r>=R+1`.
> - If `q=2`, `R` is an integer and `R>=p+3`, then `r>=R+1`.

This is a prime-uniform strict improvement of the previous arc floor on an infinite arithmetic set of first-failure slices.

## 6. Explicit infinite q=2 family

For primes

`p congruent 1 (mod 4)`, `p>=13`,

put

`q=2`,

`m=(5p-13)/4`,

`R=(5p+3)/4`.

These are integral and satisfy the first-failure excess inequality. A direct substitution gives

`(N-p-1)/(p-2)=R`

and

`R-p-1=(p-1)/4>=3`.

Thus the integral bump yields

> `r >= (5p+7)/4`

for this entire infinite family of potential first-failure slices.

The previously machine-closed `p=7,q=2,m=8,r=13` face is the small exceptional congruence analogue: `R=13`, `n=5`, and the same analytic scalar-uniqueness theorem now gives `r>=14` without needing the 5,166-candidate scalar census.

## 7. Analytic simplification of the p=7 conic closures

The finite covers remain valuable independent receipts, but their scalar-incompatibility conclusions are no longer proof-critical.

- `p=7,q=2,m=8,r=13`: five off-conic directions all have deficit one, so scalar uniqueness already contradicts their coexistence.
- `p=7,q=3,m=6,r=11`, `f=8`: three off-conic directions all have deficit two=`q-1`, so scalar uniqueness already contradicts their coexistence.

The 5,166 rank-13 / ratio-cycle checks and the 4,466 rank-11 / gain-graph checks are retained as independent finite controls of the general theorem.

## 8. Interface with the general formalism

This theorem turns saturated planes into a global interpolation obstruction. In conic coordinates, every minimal-deficit off-conic direction tries to impose its own reciprocal quadratic scalar profile on the full conic. For `p>=7`, two distinct profiles cannot agree on enough conic points.

The mechanism combines:

1. rank-two inverse zero-sum structure;
2. finite projective conic geometry;
3. rational-function interpolation over `F_p`; and
4. first-failure direction-deficit arithmetic.

It is therefore a genuine prime-uniform bridge between restricted sumsets and the finite rank-three augmentation problem.

## Boundary

- The theorem requires a **full** `(p+1)`-arc/conic of full-multiplicity directions.
- It does not say that configurations with fewer full directions are impossible.
- The `p=5` case is explicitly excluded; hostile finite checks find compatible distinct centers there.
- No exact value of `D_k(C_p^3)` is claimed by this theorem alone.
