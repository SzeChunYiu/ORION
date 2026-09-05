# First-corridor `a=1` two-share support-three face is impossible — V1

Status: **proved elimination of the shared-multiplicity `c=2` slice for every prime `p>=7`**, with one transparent bounded base case at `p=13`. The proof also records a reusable relation-multiple certificate for the remaining `c>=3` family. No generalized Davenport value is claimed here.

## 1. Setup

Let `p=2q+1>=7` be prime and let

`m=(3p-1)/2=p+q`.

In the saturated coordinates of `A1_LIGHT_SUPPORT3_ONE_SHARE_ELIMINATION_V1.md`,

`U=f1^(p-1) f2^(p-1) f3^(p-1) s`,

where

`s=f1+f2+f3`.

An exact-support-six support-three companion of maximal-atom type `a=1` has

`V=s^c x^r y^t`,

with `r<=t`, `c+r+t=m`, and atom relation

`c s+r x+t y=0`.

The pair `UV` is `(m-1)`-short-zero-free. Since `U` supplies one further copy of `s`, the pair contains `c+1` actual copies of `s`.

## 2. Reusable relation-multiple certificate

For `1<=n<=p-1`, define least positive residues

`d=[nc]_p`, `A=[nr]_p`, `B=[nt]_p`.

Multiplying the atom relation by `n` gives

`d s+A x+B y=0`.

If `A<=r` and `B<=t`, the `x,y` terms are available in `V`. The `d` copies of `s` can be realized inside `UV` with term cost

`lambda_c(d)=d`, if `d<=c+1`,

and

`lambda_c(d)=3d-2c-2`, if `d>c+1`.

Indeed, in the second case use the `c+1` actual copies of `s` and replace each of the remaining `d-c-1` copies by

`s=f1+f2+f3`.

There are enough saturated terms because `d<=p-1`.

Hence:

> **Relation-multiple certificate.** If for some `n`
>
> `A<=r`, `B<=t`, and `lambda_c(d)+A+B<=m-1`,
>
> then the support-three equality branch is impossible: the displayed relation is an actual forbidden zero-sum subsequence of `UV` of length at most `m-1`.

This certificate is symbolic and will also be useful after `c=2`.

### Low-`c` interior corollary

Suppose `c>=2`, `r,t>=q+1`, and

`4c<=p+3`.

Take `n=2`. Then `2c<p`, so `d=2c>c+1`, while

`A=2r-p`, `B=2t-p`.

Since `r+t=m-c`,

`lambda_c(2c)+A+B`

`=(4c-2)+(p-1-2c)`

`=p+2c-3`

`<=m-1`.

Thus:

> `boxed{2<=c<=(p+3)/4 and r,t>p/2 => impossible.}`

Equivalently, any surviving low-`c` branch must already be pushed to the multiplicity boundary `r<=q`.

## 3. Specialize to `c=2`

Assume now

`V=s^2 x^r y^t`.

Then

`r+t=m-2=p+q-2`.

Because each actual value has multiplicity at most `p-1`,

`t<=p-1`, hence

`r>=q-1`.

There are only three cases:

1. `r>=q+1`;
2. `r=q-1`, `t=p-1`;
3. `r=q`, `t=p-2`.

We eliminate them all.

## 4. Interior `r>=q+1`

Then also `t>=q+1`. The low-`c` corollary applies directly. More explicitly, doubling the atom relation has `d=4`, and four copies of `s` cost six terms because the pair contains three actual `s` terms and the fourth is `f1+f2+f3`.

The `x,y` residues contribute

`(2r-p)+(2t-p)=p-5`.

Thus the mixed zero-sum has length

`6+(p-5)=p+1<=m-1`

for every `p>=7`, a contradiction.

## 5. Boundary `r=q-1`, `t=p-1`

Use the relation-multiple certificate with a multiplier chosen only by `p mod 4`.

### `p == 3 mod 4`

Take

`n=q+1=(p+1)/2`.

Then

`d=1`,

`A=(p-3)/4<=q-1=r`,

`B=q<=p-1=t`.

Since `d<=3`, `lambda_2(d)=1`, and

`1+(p-3)/4+q<=m-1`.

So the branch is impossible.

### `p == 1 mod 4`

For primes `p>=7` this means `p>=13`. Take

`n=q+2=(p+3)/2`.

Then

`d=3`,

`A=(p-9)/4<=q-1=r`,

`B=q-1<=t`.

Again `lambda_2(3)=3`, and

`3+(p-9)/4+(q-1)<=m-1`.

So this boundary is impossible for every `p>=7`.

## 6. Boundary `r=q`, `t=p-2`

### `p == 3 mod 4`

Take

`n=q+2=(p+3)/2`.

Then

`d=3`,

`A=(p-3)/4<=q=r`,

`B=p-3<=p-2=t`.

The zero-sum length is

`3+(p-3)/4+(p-3)<=m-1`.

Hence this branch is impossible.

### `p == 1 mod 4`, `p>=17`

Take

`n=q+3=(p+5)/2`.

Then

`d=5`,

`A=(p-5)/4<=q=r`,

`B=p-5<=p-2=t`.

Now `d=5>3`, so

`lambda_2(5)=9`.

The resulting length is

`9+(p-5)/4+(p-5)`.

This is at most `m-1` exactly when `p>=17`. Thus every prime in this congruence class except the single base `p=13` is eliminated symbolically.

## 7. The single base `p=13`

Here

`q=6`, `m=19`, and the only remaining multiplicity triple is

`(c,r,t)=(2,6,11)`.

The relation gives

`x=4(s-y)`.

The `a=1` depth is

`rho(z)=S(z)-2` when all three saturated coordinates are nonzero, and `rho(z)=S(z)` otherwise.

A direct residue check of the radial inequalities for the eleven copies of `y` reduces, up to coordinate permutation, to the seven patterns

`(1,1,12)`, `(1,2,11)`, `(1,3,10)`, `(1,4,9)`, `(1,5,8)`, `(1,6,7)`, `(1,1,6)`.

Substituting `x=4(s-y)` kills them as follows:

- `(1,1,12)` and `(1,1,6)`: `x` lies on a saturated coordinate axis, forbidden by the first-corridor plane condition;
- `(1,2,11)` and `(1,5,8)`: `rho(-x)=5<18=m-1`;
- `(1,3,10)`: `rho(-2x)=10<17=m-2`;
- `(1,4,9)`: `rho(-3x)=15<16=m-3`;
- `(1,6,7)`: `rho(-2x)=10<17=m-2`.

Thus the `p=13` base is empty as well.

The accompanying checker independently loops over all `13^3` choices of `y`, defines `x=4(s-y)`, and finds zero pairs satisfying even the separate radial depth inequalities for `x^1,...,x^6` and `y^1,...,y^11`.

## 8. Theorem

> **Theorem.** For every prime `p>=7`, an exact-support-six first-corridor maximal pair with support-four maximal atom of type `a=1` cannot have a support-three rank-two companion with
>
> `v_e3(V)=2`.

Together with `A1_LIGHT_SUPPORT3_ONE_SHARE_ELIMINATION_V1.md`, every hypothetical `a=1` support-three equality companion now satisfies

`boxed{v_e3(V)>=3.}`

The proof is uniform apart from one explicit `p=13` base table.

## Verification receipt

`check_a1_light_support3_two_share_elimination_v1.py` verifies:

- every symbolic multiplier and length inequality through prime `1009`;
- the low-`c` doubling corollary throughout that range;
- the complete `p=13` radial base by direct enumeration of `13^3` possible `y` vectors.

The symbolic argument is theorem authority outside the single bounded base; the exact `p=13` loop is the authority for that base case.

## Boundary

- Shared multiplicity `c>=3` remains open in the `a=1` support-three face.
- The `a=2` light-share support-three face remains open.
- Rank-three four-support companions remain open.
- No `D_3(C_p^3)` value, all-`k` formula, or novelty/priority claim is made.
