# First-corridor `a=1` three-share support-three face is impossible — V1

Status: **proved elimination of the shared-multiplicity `c=3` slice for every prime `p>=7`**. For `p>=11`, all but one small arithmetic boundary are killed by explicit relation multiples; the remaining `p=7` and `p=13` bases are exact depth checks. No generalized Davenport value is claimed here.

## 1. Setup

Use the saturated-coordinate normal form and relation-multiple certificate from

`A1_LIGHT_SUPPORT3_TWO_SHARE_ELIMINATION_V1.md`.

Write

`p=2q+1`, `m=p+q=(3p-1)/2`,

and assume

`V=s^3 x^r y^t`, `r<=t`,

so

`r+t=m-3=p+q-3`.

Since `t<=p-1`,

`r>=q-2`.

Thus only four multiplicity regions exist:

- `r>=q+1`;
- `r=q-2`, `t=p-1`;
- `r=q-1`, `t=p-2`;
- `r=q`, `t=p-3`.

For a relation multiple `n`, put

`d=[3n]_p`, `A=[nr]_p`, `B=[nt]_p`.

The `s`-term cost is

`lambda_3(d)=d` for `d<=4`,

`lambda_3(d)=3d-8` for `d>4`.

Whenever `A<=r`, `B<=t`, and `lambda_3(d)+A+B<=m-1`, pair short-freeness is contradicted.

## 2. Interior `r>=q+1`

For every prime `p>=11`, doubling works. Here

`d=6`, `lambda_3(6)=10`,

`A=2r-p`, `B=2t-p`,

and

`A+B=p-7`.

Hence the forbidden zero-sum has length

`p+3<=m-1`

for `p>=11`.

The only prime below this threshold is `p=7`, handled in the bounded base section.

## 3. Boundary `r=q-2`, `t=p-1`

### `p == 2 mod 3`

Take

`n=(p+1)/3`.

Then

`d=1`,

`A=(p-5)/6`,

`B=(2p-1)/3`.

All coefficients fit, and the length is

`1+(p-5)/6+(2p-1)/3=(5p-1)/6<m-1`.

### `p == 1 mod 3`

For the symbolic range `p>=13`, take

`n=(2p+4)/3`.

Then

`d=4`,

`A=(p-10)/3`,

`B=(p-4)/3`,

and the length is

`4+(p-10)/3+(p-4)/3=(2p-2)/3<m-1`.

Thus this boundary is empty outside the small `p=7` base.

## 4. Boundary `r=q-1`, `t=p-2`

### `p == 1 mod 3`

Take

`n=(p+5)/3`.

Then

`d=5`, `lambda_3(d)=7`,

`A=(p-5)/2`,

`B=(p-10)/3`.

The total length is

`(5p+7)/6<=m-1`.

### `p == 2 mod 3`

Take

`n=(2p+5)/3`.

Then

`d=5`, `lambda_3(d)=7`,

`A=(p-5)/2`,

`B=2(p-5)/3`.

The total length is

`(7p+7)/6<=m-1`

for every prime in the present range `p>=11`.

Hence this boundary is empty outside `p=7`.

## 5. Boundary `r=q`, `t=p-3`

### `p == 2 mod 3`

Take

`n=(p+4)/3`.

Then

`d=4`,

`A=(p-2)/3`,

`B=p-4`.

The total length is

`p+(p-2)/3<=m-1`.

### `p == 1 mod 3`, `p>=19`

Take

`n=(2p+7)/3`.

Then

`d=7`, `lambda_3(d)=13`,

`A=(p-7)/6`,

`B=p-7`.

The total length is

`13+(p-7)/6+(p-7)=(7p+29)/6`.

This is at most `m-1` exactly for `p>=19`.

The only uncovered prime in this congruence class above `7` is therefore `p=13`.

## 6. Exact small bases

Two bounded checks remain.

### `p=7`

Here `q=3`, `m=10`, and the complete `c=3` multiplicity list is

`(3,1,6)`, `(3,2,5)`, `(3,3,4)`.

For each triple, solve the atom relation for `x` after choosing `y`. Exhausting all `7^3` possible `y` vectors produces **zero** choices for which the separate radial depth inequalities hold simultaneously for every available power of `x` and `y`.

### `p=13`

The symbolic arguments already remove the interior and the first two boundaries. The sole uncovered triple is

`(c,r,t)=(3,6,10)`.

The same exact radial check over all `13^3` possible `y` vectors again produces **zero** survivors.

These bases use only the explicit `a=1` depth formula

`rho(z)=S(z)-2` off the saturated coordinate hyperplanes and `rho(z)=S(z)` on them.

## 7. Theorem

> **Theorem.** For every prime `p>=7`, an exact-support-six first-corridor maximal pair with support-four maximal atom of type `a=1` cannot have a support-three rank-two companion with
>
> `v_e3(V)=3`.

Combining the one-, two-, and three-share eliminations,

`boxed{v_e3(V)>=4}`

in every hypothetical `a=1` support-three equality companion.

## Verification receipt

`check_a1_light_support3_three_share_elimination_v1.py` verifies every symbolic multiplier and coefficient/length inequality through prime `1009`, and exactly enumerates the `p=7` and `p=13` depth bases.

The relation-multiple arguments are theorem authority in the symbolic range; the bounded exact loops are authority only for the stated small bases.

## Boundary

- Shared multiplicity `c>=4` remains open in the `a=1` support-three face.
- The `a=2` light-share support-three face remains open.
- Rank-three four-support companions remain open.
- No `D_3(C_p^3)` value, all-`k` formula, or novelty/priority claim is made.
