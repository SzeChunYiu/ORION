# `a=3` light-share left-half boundary `e>f` is impossible — V1

Status: **proved prime-uniform branch elimination**. In the exceptional `a=3` first-corridor light-share support-three face, every boundary row with

`e>f`

is impossible for every prime `p>=7`.

Together with `A3_RIGHT_HALF_BOUNDARY_ELIMINATION_V1.md`, this closes the entire `a=3` light-share rank-two boundary. Combined with the all-type light-interior theorem and the all-type heavy-share theorem, maximal type `a=3` has no exact-support-six support-three rank-two companion at all.

No generalized Davenport value or novelty/priority claim is made.

## 1. Setup

Let

`p=2H+1`, `m=3H+1`,

and parameterize a light-share boundary row by

`e=c-d`, `f=d+1`, `e+f=c+1`,

so

`r=H+1-e`, `t=p-f`.

For maximal type `a=3`, the exact overlap theorem gives

`c<=floor(H/2)`.

Assume throughout this file that

`e>f`.

Put

`alpha=2e-1`, `delta=e-f`.

Then

`alpha=c+delta>c`,

and

`2r=p-alpha`.

We use the exact radial surcharge from `A3_EXACT_RADIAL_EXCESS_V1.md`:

`lambda_{3,c}(D)-D = 2 ceil(max(D-c-3,0)/3)`.

There are two exhaustive cases depending on whether the x-multiplicity `r` reaches the coefficient `alpha`.

## 2. Case I: `r>=alpha`

Set

`j=floor(r/alpha)>=1`

and choose the odd multiplier

`n=p-2j`.

Write

`r=j alpha+w`, `0<=w<=alpha-1`.

Since `p=2r+alpha`, this is equivalent to

`boxed{p=(2j+1)alpha+2w.}`

### 2.1 Coefficient capacities

Because `c<alpha` and `j alpha<=r<p/2`,

`2jc<p`.

Hence the light coefficient is

`boxed{D=[nc]_p=p-2jc.}`

For x, using `2r=p-alpha`,

`nr == -2jr == j alpha (mod p)`,

and `j alpha<=r`, so

`boxed{A=[nr]_p=j alpha<=r.}`

Since `e>f`, one has `2f<=c<alpha`. Thus

`2jf<=jc<j alpha<=r<t<p`,

and therefore

`boxed{B=[nt]_p=2jf<=t.}`

The exact coefficient sum is

`D+A+B`

`=p-2jc+j alpha+2jf`

`=p+j(alpha+2f-2c)`

`=boxed{p+j},`

because `alpha+2f=2c+1`.

### 2.2 Radial surcharge fits the remaining budget

Using

`alpha-c=delta`,

and the representation of p above,

`D-c-3`

`=p-(2j+1)c-3`

`=boxed{2w+(2j+1)delta-3.}`

If this quantity is nonpositive, the radial surcharge is zero and there is nothing to prove. Otherwise

`lambda_{3,c}(D)-D`

`<= 2(2w+(2j+1)delta-1)/3`.

Because `delta=e-f<=e-1`,

`lambda_{3,c}(D)-D`

`<= [4w+2(2j+1)(e-1)-2]/3`.

Now

`H-j-1=2j(e-1)+e+w-2`.

Three times the difference between this quantity and the last displayed upper bound is at least

`2j(e-1)+e-2-w`.

Since `j>=1`, `e>=2`, and

`w<=alpha-1=2e-2`,

this is nonnegative. Hence

`boxed{lambda_{3,c}(D)-D<=H-j-1.}`

The lifted zero-sum therefore has length at most

`p+j+(H-j-1)=3H=m-1`,

contradicting pair short-freeness.

Thus no left-half row with `r>=alpha` survives.

## 3. Case II: `r<alpha`

Choose the universal multiplier

`boxed{n=p-3.}`

The inequality `r<alpha` is equivalent to

`H+2<3e`.

Consequently

`3r=3(H+1-e)<p`,

so

`boxed{A=[nr]_p=p-3r.}`

Also `e<=c<=H/2` gives `r>H/2`, hence `p<4r`; therefore

`A=p-3r<=r`.

Because `e>f`,

`2f<=c<=H/2`,

so `4f<=H<p`. Thus

`boxed{B=[nt]_p=3f<=p-f=t.}`

Similarly `3c<p`, and therefore

`boxed{D=[nc]_p=p-3c.}`

The companion length identity gives

`c+r-f=H`.

Hence

`D+A+B`

`=(p-3c)+(p-3r)+3f`

`=2p-3H`

`=boxed{H+2.}`

For the radial surcharge, if it is nonzero then

`D-c-3=p-4c-3<=2H-6`.

Therefore

`ceil((D-c-3)/3)<=H-1`,

and in all cases

`boxed{lambda_{3,c}(D)-D<=2H-2.}`

Thus the lifted zero-sum has length at most

`H+2+(2H-2)=3H=m-1`,

again forbidden.

So no left-half row with `r<alpha` survives either.

## 4. Left-half theorem

The two cases are exhaustive. Therefore:

> **Left-half boundary theorem.** For every prime `p>=7`, an exact-support-six first-corridor support-three rank-two companion of maximal type `a=3` cannot satisfy
>
> `boxed{e>f.}`

Together with `A3_RIGHT_HALF_BOUNDARY_ELIMINATION_V1.md`, every `a=3` light-share boundary row is impossible.

## 5. Complete `a=3` rank-two corollary

`SUPPORT4_ALLTYPE_LIGHT_INTERIOR_ELIMINATION_V1.md` already eliminates every light-share interior row for every type `a>=2`.

`SUPPORT4_HEAVY_SHARE_SUPPORT3_EMPTY_V1.md` eliminates the heavy-share support-three branch for every canonical support-four maximal type.

Combining those theorems with the right- and left-half boundary eliminations gives:

> **Complete type-three rank-two theorem.** For every prime `p>=7`, a first-corridor exact-support-six maximal pair with support-four maximal atom of canonical type `a=3` has no support-three rank-two companion.

Hence every remaining support-three rank-two equality companion is forced into the two exceptional light types

`boxed{a in {1,2}.}`

## Verification receipt

`check_a3_left_half_boundary_elimination_v1.py` exhausts every prime through `1009` and every left-half boundary row under the broader necessary range `1<=c<=floor(H/2)`, not merely the exact `c_light` rows. It checks the case split, all residue identities, coefficient capacities, exact radial surcharge, and final short-zero inequality.

The checker is regression only; theorem authority is the two explicit scalar constructions above.

## Boundary

- Light-share rank-two types `a=1,2` remain.
- The rank-three support-four companion remains open.
- No `D_3(C_p^3)` value or all-k formula is claimed.
