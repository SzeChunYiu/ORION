# Exact support-six normal form inside support-four maximal corridors — V1

Status: **proved prime-uniform structural reduction**. This starts from the all-corridor support-six theorem and describes the equality case when the maximal atom itself has support four. It does not eliminate support six and does not determine any new generalized Davenport constant.

## 1. Setup

Let `p>=5` be prime and work in `G=C_p^3`. At the critical three-atom completion length, suppose a maximal corridor has atom lengths

`C_j(p)=(p+j, p+b, 3p-2)`,

where

`b=(p+1)/2-j`, `1<=j<=floor((p+1)/4)`.

Let `U` be the maximal atom and `V` the longer nonmaximal companion, so

`|U|=3p-2`, `|V|=p+b`.

Assume

- `z(UV)=2` by hereditary first-failure rigidity;
- `UV` is zero-sum-free through length `p+b-1` by the pair-complement lemma; and
- `U` has support exactly four.

By the prime-uniform support-four maximal-atom theorem, after an automorphism

`U=e1^(p-1)e2^(p-1)g^a h^(p-a)`,

with

`1<=a<=(p-1)/2`

and `{e1,e2,g,h}` a projective four-circuit. In particular every three of these four support vectors are linearly independent.

Assume now that the all-corridor support bound is attained:

`|supp(UV)|=6`.

## 2. The saturated maximal-atom values are unavailable to the companion

Because `UV` is `p`-short-zero-free, no actual group element can occur `p` times in the pair. Hence

`v_x(UV)<=p-1`

for every nonzero `x in G`.

But `e1` and `e2` already occur `p-1` times in `U`. Therefore

> `boxed{v_e1(V)=v_e2(V)=0.}`

Since `supp(U)` has four elements and `supp(UV)` has six, exactly two actual support values of `V` lie outside `supp(U)`. Call them `x,y`.

The only support values that `V` can share with `U` are `g` and `h`.

Moreover `|V|=p+b>p=D(C_p)`. An atom of length greater than `p` cannot be supported on at most two elements: two dependent support elements lie in a cyclic subgroup, while two independent support elements admit no nontrivial relation with coefficients in `1..p-1`.

Thus `V` must share at least one of `g,h` and

> `boxed{|supp(V)| in {3,4}.}`

More precisely:

- support 3 means `supp(V)={x,y,g}` or `{x,y,h}`;
- support 4 means `supp(V)={x,y,g,h}`.

If `|supp(V)|=3`, then the three support vectors must be linearly dependent because the positive multiplicity vector of `V` is a nontrivial relation. Hence

> `boxed{|supp(V)|=3 => rank <supp(V)> <=2.}`

## 3. Exact term-mass forced onto the two new values

Pair `p`-short-freeness also caps the amount by which `V` can reuse the two unsaturated maximal-atom values:

`v_g(V)<=p-1-a`,

`v_h(V)<=a-1`.

Therefore the two new values carry the following minimum total multiplicity.

### Only `g` is shared

`v_x(V)+v_y(V) >= |V|-(p-1-a)=b+a+1`.

### Only `h` is shared

`v_x(V)+v_y(V) >= |V|-(a-1)=p+b-a+1`.

### Both `g,h` are shared

The total available overlap is at most

`(p-1-a)+(a-1)=p-2`,

so

`v_x(V)+v_y(V)>=b+2`.

These are actual-value multiplicity bounds, not merely projective-support bounds.

A useful endpoint occurs in the heavy-share-only case. Since `a<=(p-1)/2`,

`v_x(V)+v_y(V)>=p+2-j`.

Every projective line of a `p`-short-zero-free sequence contains at most `p-1` terms, because `D(C_p)=p`. Consequently, for `j<=2`, the two new actual values cannot lie on the same projective line:

> if `supp(V)={x,y,h}` and `j<=2`, then `boxed{<x> != <y>}`.

In the light-share-only case, the same argument gives projective separation of `x,y` at `j=1` in the extremal type `a=(p-1)/2`, where the lower bound also reaches `p`.

## 4. Plane budget for a rank-two companion

Let `K` be a rank-two subgroup containing all of `V`. The pair-specific short-free depth is

`H=p+b-1`.

Hence the exact rank-two pair-plane cap gives

`|(UV)_K|<=4p-3-H=3p-b-2`.

Since all `p+b` terms of `V` lie in `K`, the amount of maximal-atom mass that can lie in the same plane is bounded by

> `boxed{|U_K|<=2p-2b-2=p+2j-3.}`

This single inequality controls which additional maximal-atom support points can lie in the companion plane.

### Companion shares both unsaturated values

If `g,h in K`, then

`|U_K|>=a+(p-a)=p`.

Therefore a rank-two support-four companion is possible only if

`p<=p+2j-3`,

i.e.

> `boxed{rank <V> <=2 and supp(V)={x,y,g,h} => j>=2.}`

So the first corridor `j=1` forces every support-four companion in the exact support-six face to have rank three.

### Companion shares only `h`

If the rank-two companion plane also contained either saturated maximal-atom value `e1` or `e2`, then

`|U_K| >= (p-a)+(p-1)`.

But throughout the corridor range

`p-a >= (p+1)/2 > 2j-2`,

so this exceeds `p+2j-3`. Hence:

> in the heavy-share-only rank-two branch, the companion plane contains neither `e1` nor `e2`, for every corridor index `j`.

### Companion shares only `g`

If the plane also contains `e1` or `e2`, the plane budget requires

`a+(p-1)<=p+2j-3`,

or

> `boxed{a<=2j-2.}`

Thus whenever `a>2j-2`, a light-share-only rank-two companion plane also avoids both saturated maximal-atom directions.

Finally, a rank-two companion plane containing both `g` and `h` has maximal-atom mass at least `p`; this is excluded exactly at `j=1` and becomes arithmetically possible from `j=2` onward.

## 5. Sharp first-corridor dichotomy

Set `j=1`. Then the plane budget is

`|U_K|<=p-1`.

Suppose `|supp(UV)|=6`.

### Three-support companion

The companion has support `{x,y,g}` or `{x,y,h}` and spans a rank-two plane `K`. The plane already contains one unsaturated maximal-atom support value. It cannot contain

- either saturated value, because `(p-1)+positive > p-1`; or
- the other unsaturated value, because `a+(p-a)=p>p-1`.

Therefore

> `boxed{K cap supp(U) = supp(V) cap supp(U)}`
>
> and this set has exactly one element.

### Four-support companion

The companion support is `{x,y,g,h}`. If it were rank two, its plane would contain `p` terms of `U` on `g,h`, violating the `p-1` budget. Hence

> `boxed{|supp(V)|=4 => rank <supp(V)>=3.}`

Combining the two cases gives the exact first-corridor support-six normal form:

> **Theorem.** In `C_1(p)`, if a support-four maximal atom has a maximal pair of total support six, then exactly one of the following holds:
>
> 1. `V` has support three, spans a rank-two plane, shares exactly one of `g,h`, and that plane meets `supp(U)` in exactly that one point; or
> 2. `V` has support four, shares both `g,h`, and spans all of `C_p^3`.

For `p=7`, this is the structural equality face underneath the `(8,10,19)` support-four branch.

## 6. Strategic consequence

The previous theorem said only that the maximal pair has support at least six. Equality is now reduced from an arbitrary rank-three six-point configuration to a two-branch companion problem with:

- two fixed new actual values;
- exact overlap capacities;
- a rank-two three-support branch with a one-point intersection plane in the first corridor; or
- a rank-three four-support branch using both unsaturated maximal-atom values.

This is the correct next interface for the U-representation-depth and line-fiber avoidance constraints. In particular, any future support-seven proof may attack the two equality branches separately rather than searching all six-support pair configurations.

## Verification receipt

`check_support4_maximal_pair_support6_normal_form_v1.py` verifies the corridor identities, plane budgets, overlap-capacity inequalities and all stated threshold implications for every prime through 401 and every support-four type `a` and corridor index `j`.

The checker is regression only; theorem authority is the argument above.

## Boundary

- Neither equality branch is eliminated here.
- The theorem assumes the maximal atom has support exactly four.
- Support-six maximal pairs with maximal-atom support at least five remain outside this reduction.
- No `D_3(C_p^3)` value or all-prime formula is claimed.
