# Saturated p-arc scalar uniqueness and a second integral direction-floor bump — V1

Status: **proved prime-uniform analytic theorem for odd primes `p>=11`, with independent finite hostile controls**. The p-arc completion theorem and conic geometry are donor-owned. No exact generalized Davenport value is asserted here.

## 1. From p full directions to a unique conic

Let `p>=11` be prime and let a first-failure sequence over `C_p^3` have `p` full-multiplicity projective directions. They form a p-arc.

Segre's classical theorem says every p-arc in `PG(2,p)`, p odd, is contained in a `(p+1)`-arc; the latter is a conic. The completion is unique: two distinct conics cannot contain the same `p>=5` arc points.

Write the unique completion as

`C=F union {R}`,

where `F` is the p-point full arc and `R` is the one missing conic point.

Donor attribution: Segre's p-arc extension theorem, as recorded for example in J. A. Thas, *Complete arcs and algebraic curves in PG(2,q)*, Journal of Algebra 106 (1987), 451--464.

## 2. Off-conic minimal-deficit centers still impose a quadratic profile

Let `D` be an occupied direction outside the completed conic `C`, with deficit exactly `q-1`.

Projection from `D` pairs conic points along secants, with at most two tangent fixed points. Among the p full points `F`, at most

- two tangent points, and
- one point whose secant partner is the missing completion point `R`

fail to lie on a full-full secant through `D`.

Every remaining full-full secant has two full directions and `D`, hence line deficit exactly `q-1`; no additional occupied direction can lie on it by the strict rich-plane deficit inequality. Therefore the plane is saturated and the same reciprocal-quadratic formula from `SATURATED_CONIC_SCALAR_UNIQUENESS_V1.md` holds at every such full conic point.

In canonical coordinates `C(t)=(1,t,t^2)`, for `D=(d_0,d_1,d_2)`,

`lambda(t)=mu_D (d_0d_2-d_1^2)/(d_0t^2-2d_1t+d_2)`

on all finite full parameters except at most three exceptional full points.

## 3. At most one off-conic minimal center when p>=11

Suppose distinct off-conic occupied directions `D,E` both have deficit `q-1`.

The p-point full arc contains at least `p-1` finite conic parameters. Each center excludes at most three full points from its saturated-secant profile. Hence the two profiles agree on at least

`p-7>=4`

finite full parameters. In particular they agree at at least three distinct field values.

Cross-multiplication makes the two quadratic denominators proportional at those values. Hence the quadratics are proportional identically, forcing `D=E` projectively, contradiction.

> **p-arc scalar uniqueness theorem.** For every prime `p>=11`, relative to a p-point full arc and its unique conic completion, at most one occupied direction outside the conic can have deficit exactly `q-1`.

The completion point `R` is exceptional: it lies on no secant through two full arc points and need not satisfy the off-conic lower deficit `q-1`.

The threshold is not cosmetic. Direct finite hostile replays find compatible distinct off-conic minimal centers for p-full arcs at `p=5` and `p=7`; no claim is made there.

## 4. Deficit bound with exactly p full directions

Suppose exactly p directions are full and put

`n=r-p`

for the number of deficient directions.

- The completion point `R`, if occupied, contributes deficit at least one.
- Every occupied direction outside the conic lies on a full-full conic secant and therefore has deficit at least `q-1`.
- At most one off-conic direction has deficit exactly `q-1`; all remaining off-conic directions have deficit at least `q`.

Thus for `n>=2`,

> `Delta >= qn-q`.

If `R` is not occupied, the stronger bound is `Delta>=qn-1`.

## 5. The p-full integral boundary

Put

`S=(N-p)/(p-2)`.

Assume `S` is an integer. The existing full-direction arc bound gives

`r>=ceil((N-p-1)/(p-2))=S`.

Suppose equality `r=S` holds and set

`n=S-p`.

Then

`Delta=r(p-1)-N=n`

and the elementary full-direction count gives at least p full directions. There are only two cases.

### Exactly p full directions

For `n>=2`, the preceding bound requires

`n>=qn-q`,

or

`(q-1)n<=q`.

### All p+1 conic directions full

Then there are `n-1` deficient off-conic directions. The full-conic theorem gives, uniformly for `n>=2`,

`Delta=n >= q(n-1)-1`,

or

`(q-1)n<=q+1`.

The second condition is weaker and therefore controls the combined boundary.

> **Second integral direction-floor bump.** If `p>=11`, `S=(N-p)/(p-2)` is integral, and
>
> `(q-1)(S-p)>q+1`,
>
> then equality `r=S` is impossible and
>
> `r>=S+1`.

Concrete thresholds in terms of `n=S-p` are:

- q=2: n>=4;
- q=3: n>=3;
- q>=4: n>=2.

This is the corrected case split; a q=2 boundary with n=3 can still survive the present theorem via a full conic plus deficient pattern `(1,2)`.

## 6. Infinite q=2 family for p=3 mod 4

Let

`p congruent 3 (mod 4)`, `p>=19`,

and consider the admissible first-failure arithmetic slice

`q=2`,

`m=(5p-15)/4`.

Then

`S=(N-p)/(p-2)=(5p+1)/4`

and

`n=S-p=(p+1)/4>=5`.

The second integral bump therefore gives

> `r >= (5p+5)/4`.

This complements the full-conic family already proved for primes `p congruent 1 (mod 4)`, `p>=13`:

`q=2`, `m=(5p-13)/4`, `r>=(5p+7)/4`.

Hence every prime `p>=13` belongs to one of two explicit q=2 high-level families where the raw full-direction arc floor is provably strict.

## 7. Hostile finite controls

`verify_saturated_p_arc_scalar_uniqueness_independent_v1.py` fixes a conic and deletes one conic point, then checks all pairs of distinct off-conic centers using only saturated full-full secant gain constraints.

The finite pair counts are:

- p=5: 125 compatible, 175 incompatible;
- p=7: 84 compatible, 1092 incompatible;
- p=11: 0 compatible, 7260 incompatible;
- p=13: 0 compatible, 14196 incompatible.

Thus the finite boundary agrees with the analytic p>=11 threshold and explicitly rejects any p=7 extrapolation.

The primary arithmetic checker verifies the integral-bump identities for all primes through 401 and freezes the two q=2 congruence families.

## 8. Interface with the general formalism

The full-arc interpolation method now has two layers:

1. `(p+1)` full directions: complete conic, at most one minimal off-conic center for p>=7;
2. `p` full directions: unique conic completion, at most one **off-conic** minimal center for p>=11, with the missing conic point as one controlled exceptional direction.

This shows how large-arc completion theorems can systematically convert finite-geometry proximity to a conic into scalar interpolation rigidity.

## Boundary

- The p-full theorem is stated only for primes p>=11.
- The exceptional missing conic point is explicitly retained.
- No assertion is made yet for `(p-1)` full arcs, which need not extend uniformly to a conic in the small prime cases.
- No exact value of `D_k(C_p^3)` follows from this theorem alone.
