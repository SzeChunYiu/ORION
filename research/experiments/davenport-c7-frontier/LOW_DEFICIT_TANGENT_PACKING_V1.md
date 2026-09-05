# Low-deficit tangent packing in first-failure projective supports — V1

Status: **proved analytic reduction**. Donor inputs are the q-dependent rank-two restricted-sum cap and its equality grammar from `RANK2_Q_PLANE_CAP_AND_WEIGHTED_ARC_V1.md`. No generalized Davenport value is asserted here.

Let `p>=5` be prime and let `B` be a first-failure core over `C_p^3` with overshoot `q>=3`. Write the occupied projective directions as `P_i` with weights `w_i<=p-1`, deficits

`d_i=(p-1)-w_i`,

and total projective deficit `Delta=sum d_i`. Let `F` be the set of full directions (`d_i=0`) and put `f=|F|`.

For

`a=floor((q-1)/2)`,

call a deficient direction **low** if `1<=d_i<=a`, and let `L` be the number of low directions.

## 1. Low directions avoid every full secant

If a low direction `D` lay on a projective line with two full directions, the line deficit would be at most

`a<q-1`,

contradicting the three-direction weighted-secant inequality

`sum_line d_i >= q-1`.

Thus a low direction is secant-free relative to the full-direction arc `F`.

## 2. At most one low direction on each remaining line through a full point

Fix `P in F`. The `f-1` lines joining `P` to the other full directions are unavailable by the preceding paragraph. Hence only

`(p+1)-(f-1)=p+2-f`

lines through `P` remain available to low directions.

No one of those lines can contain two low directions `D_1,D_2`.

- If the line contains only `P,D_1,D_2`, then its total deficit is at most `2a<=q-1`. Strict inequality contradicts the plane cap. Equality also contradicts the exact saturated-plane grammar: equality requires deficit pattern `{0,0,q-1}`, whereas here both nonfull deficits are positive.
- If the line contains `s>=1` further occupied deficient directions, then there are `t=3+s>=4` occupied directions. Each extra deficient direction has deficit at most `p-2`, so the total line deficit is at most

  `2a+s(p-2) <= (q-1)+s(p-2)`.

  The strict rich-plane inequality requires

  `s(p-1)+q`,

  larger by at least `s+1`.

Therefore every remaining line through `P` contains at most one low direction. Hence

> **Low-deficit tangent-packing bound**
>
> `L <= p+2-f`.

This is prime-uniform for every first failure with `q>=3`.

## 3. Deficit arithmetic forces a lower bound on L

Let `r` be the total number of occupied projective directions. There are `r-f` deficient directions. Every low direction has deficit at least one, while every non-low deficient direction has deficit at least `a+1`. Therefore

`Delta >= L+(a+1)(r-f-L)=(a+1)(r-f)-aL`.

So

`L >= ceil(((a+1)(r-f)-Delta)/a)`

whenever the numerator is positive. Combining with tangent packing gives the convenient full-direction lower bound

> `f >= (a+1)r-Delta-a(p+2)`.

It should be combined with the elementary bound `f>=r-Delta` and the arc bound `f<=p+1`.

For `q=3`, `a=1`, so the formulas simplify to

`L >= 2(r-f)-Delta`,

`L <= p+2-f`,

and hence

`f >= 2r-Delta-(p+2)`.

## 4. p=7 consequences

At `p=7,q=3`, the first-failure slice `(m,r)=(6,11)` has

`N=60`, `Delta=11*6-60=6`.

The tangent-packing inequality gives

`f >= 2*11-6-9=7`.

Thus the previously possible full-direction counts `f=5,6` disappear analytically. Only `f=7,8` remain.

For `(m,r)=(5,10)`, `N=53`, `Delta=7`, and the same inequality gives

`f>=4`.

Thus the `f=3` subcase of the minimum-direction `(q,m,r)=(3,5,10)` face is also eliminated.

## 5. Strategic interpretation

The q-dependent plane theorem does more than bound total plane occupancy. It imposes a packing constraint in every tangent pencil of the full-direction arc. Low-deficit projective points behave like a partial transversal of the `p+2-f` nonsecant lines through every full point.

This is a reusable finite-geometry front end before scalar/kernel enumeration:

1. use total deficit to force many low directions;
2. use tangent packing to force many full directions;
3. use arc extension/conic structure when the number of full directions approaches `p+1`;
4. only then impose saturated-plane scalar compatibility.

## Boundary

- The result is necessary structure only; it does not eliminate an entire `(m,q)` level by itself.
- Exact rank-two restricted-sum values and equality structure remain donor-owned.
- No claim is made for `q=2`, where `a=0` and this low-deficit argument has no content.
