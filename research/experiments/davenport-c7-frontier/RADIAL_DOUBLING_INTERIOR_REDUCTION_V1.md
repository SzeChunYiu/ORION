# Prime-uniform radial doubling reduction for light-share interiors — V1

Status: **proved structural reduction**. This extracts the common mechanism behind the first few `a=1` and `a=2` light-share eliminations. It replaces infinitely many interior multiplicity rows by a boundary problem. It does not close the boundary rows and does not determine a generalized Davenport constant.

## 1. Common first-corridor parametrization

Let

`p=2H+1`, `m=(3p-1)/2=3H+1`,

and suppose an exact-support-six first-corridor support-three companion has light-share form

`V=s^c x^r y^t`, `r<=t<=p-1`,

with atom relation

`c s+r x+t y=0`.

Since `c+r+t=m` and `t<=p-1=2H`, write uniquely

`r=H+1-c+d`, `t=2H-d`, `d>=0`.

Assume `d>=c`. In every range used below one has `d<=H-1`, so doubling the atom relation gives the least-residue relation

`2c s+(2d-2c+1)x+(p-2d-2)y=0`.

Both new-value coefficients are positive and fit inside the available multiplicities `r,t`. Thus it remains only to realize the radial target `2c s` cheaply from the maximal-pair resources.

## 2. Type `a=1`: uniform low-overlap interior elimination

For the canonical type `a=1`, write

`U=e1^(p-1)e2^(p-1)s g^(p-1)`,

where

`g=s-e1-e2`.

The pair contains `c+1` actual copies of `s`. For `2c<p`, realize `2c s` by

- `c+1` actual copies of `s`, and
- `(c-1)g+(c-1)e1+(c-1)e2=(c-1)s`.

The radial term cost is therefore

`lambda_{1,c}(2c)<=4c-2`.

The doubled zero-sum then has total term length

`(4c-2)+(2d-2c+1)+(p-2d-2)=p+2c-3`.

If

`c<=floor((p+3)/4)=floor((H+2)/2)`,

then

`p+2c-3 < 3H+1=m`.

Hence:

> **`a=1` low-overlap interior theorem.** For every prime `p>=7`, if an exact-support-six first-corridor `a=1` light-share support-three companion satisfies
>
> `c<=floor((p+3)/4)`,
>
> then it cannot have `d>=c`. Equivalently every survivor in this entire low-overlap range satisfies
>
> `boxed{0<=d<=c-1.}`

This explains in one statement why doubling removes the interiors of the previously treated `c=1,2,3` layers whenever the layer lies in the stated range.

## 3. Type `a=2`: every admissible interior is impossible

For the canonical type `a=2`, write

`U=e1^(p-1)e2^(p-1)s^2 g^(p-2)`,

where

`g=s-2^(-1)(e1+e2)`.

The exact light multi-copy criterion gives

`c<=2 floor(H/2)<=H`.

In particular `2c<p`, so the doubled coefficient of `s` is exactly `2c`.

The pair contains `c+2` actual copies of `s`. Cheap realizations of `2c s` are:

- `c=1`: two actual `s` terms, cost `2`;
- even `c>=2`: use `c+2` actual `s` terms and `q=c-2` copies of `g`; since `q` is even,
  `q g+(q/2)e1+(q/2)e2=q s`, giving total radial cost `3c-2`;
- odd `c>=3`: use `c+1` actual `s` terms and `q=c-1` copies of `g`; again `q` is even, giving total radial cost `3c-1`.

All displayed resources lie within the multiplicities of `UV`.

Consequently the doubled zero-sum has term length

- `p-1` when `c=1`;
- `p+c-3` when `c` is even;
- `p+c-2` when `c>=3` is odd.

Each is strictly smaller than `m=3H+1`. Indeed the overlap ceiling gives `c<=H`; in the odd case the even-valued ceiling forces in fact `c<=H-1` whenever needed.

Therefore:

> **`a=2` all-overlap interior theorem.** For every prime `p>=7`, every hypothetical exact-support-six first-corridor `a=2` light-share support-three companion satisfies
>
> `boxed{0<=d<=c-1.}`
>
> Equivalently, after the exact overlap ceiling is imposed, doubling eliminates **every interior multiplicity row for every admissible shared multiplicity `c`**.

Thus the whole remaining `a=2` rank-two light-share problem is a boundary catalogue rather than a two-dimensional multiplicity region.

## 4. Strategic consequence

For `a=2`, a fixed overlap `c` now has at most `c` multiplicity rows:

`(r,t)=(H+1-c+d,2H-d)`, `d=0,...,c-1`.

The one-, two-, and three-share theorems close their boundary catalogues completely. The present theorem shows that this was not an accident of small `c`: the interior is gone uniformly, and all future work belongs on the boundary.

For `a=1`, the same phenomenon holds throughout the low-overlap range. The only place where doubling can cease to beat the inherited short-free threshold is the genuinely high-overlap regime beyond `floor((p+3)/4)`.

This sharpens the next target: prove a boundary multiplier/stability lemma rather than continuing a full multiplicity search.

## Verification receipt

`check_radial_doubling_interior_reduction_v1.py` verifies the parametrization, doubled residues, radial-cost formulas, resource bounds, and strict length inequalities for every prime through `1009`. It also compares the displayed `a=1` and `a=2` radial costs with an independently enumerated radial resource oracle on a bounded prime set.

The checker is regression only; theorem authority is the symbolic calculation above.

## Boundary

- The theorem does not eliminate `d=0,...,c-1`.
- The `a=1` statement deliberately stops at the exact range where the doubled radial cost is guaranteed to beat `m`.
- The `a=2` rank-three four-support equality branch is outside this theorem.
- No `D_3(C_p^3)` value, all-`k` formula, or novelty/priority claim is made.
