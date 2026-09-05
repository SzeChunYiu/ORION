# First-corridor `a=2` light-share multiplicity three is impossible — V1

Status: **proved prime-uniform branch elimination for every prime `p>=7`**. The prime `p=7` is excluded by the exact multi-copy ceiling; every prime `p>=11` is eliminated symbolically by explicit scalar multiples of the companion relation. No finite exceptional base remains.

This file advances `A2_LIGHT_SUPPORT3_ONE_TWO_SHARE_ELIMINATION_V1.md` from `c>=3` to `c>=4`. It does not close the whole light-share family and does not determine a generalized Davenport constant.

## 1. Setup

Let

`p=2h+1`, `m=(3p-1)/2=3h+1`,

and use the support-four maximal atom of type `a=2`

`U=e1^(p-1)e2^(p-1)s^2 g^(p-2)`,

where

`s=e3`, `g=s-2^(-1)(e1+e2)`.

Assume an exact-support-six first-corridor support-three companion shares the light value exactly three times:

`V=s^3 x^r y^t`, `r<=t<=p-1`.

The companion is an atom, the pair `UV` is `(m-1)`-short-zero-free, and

`3s+r x+t y=0`,

`r+t=m-3=3h-2`.

Since `t<=p-1=2h`, write

`r=h-2+d`, `t=2h-d`,

where

`0<=d<=floor((h+2)/2)`.

## 2. Radial lifting costs

The light-direction identity from the one/two-share theorem is

`boxed{2s=2g+e1+e2.}`

The pair contains five actual copies of `s`: three from `V` and two from `U`. We use the following certified realizations of a residue multiple `D s`:

- `D=4`: four actual `s` terms, cost `4`;
- `D=5`: five actual `s` terms, cost `5`;
- `D=6`: four actual `s` terms plus `2g+e1+e2=2s`, cost `8`;
- `D=7`: five actual `s` terms plus `2g+e1+e2=2s`, cost `9`.

For a scalar multiplier `n`, put

`D=[3n]_p`, `A=[nr]_p`, `B=[nt]_p`.

Whenever `A<=r`, `B<=t`, and the declared radial cost plus `A+B` is less than `m`, the multiplied relation yields a forbidden nonempty zero-sum subsequence of `UV` of length at most `m-1`.

## 3. Interior multiplicities

Assume `d>=3` and take `n=2`. Then

`D=6`,

`A=2d-5`,

`B=p-2d-2`.

Both new-value coefficients fit their multiplicities. Using the eight-term realization of `6s`, the total length is

`8+(2d-5)+(p-2d-2)=p+1<m`

for every prime `p>=11`.

Thus every interior row is impossible.

Only the three boundary rows `d=0,1,2` remain.

## 4. Boundaries when `p=6k+1`

Here

`h=3k`, `m=9k+1`, `k>=2`.

### Boundary `d=0`

Then `(r,t)=(3k-2,p-1)`. Take

`n=4k+2`.

The residue relation has coefficient triple

`(D,A,B)=(4,2k-3,2k-1)`.

All coefficients fit, and its term length is

`4+(2k-3)+(2k-1)=4k<m`.

### Boundary `d=1`

Then `(r,t)=(3k-1,p-2)`. Take

`n=2k+2`.

The residues are

`(D,A,B)=(5,3k-2,2k-3)`.

The length is

`5+(3k-2)+(2k-3)=5k<m`.

### Boundary `d=2`

Then `(r,t)=(3k,p-3)`. Take

`n=4k+3`.

The residues are

`(D,A,B)=(7,k-1,p-7)`.

Using the nine-term realization of `7s`, the total length is

`9+(k-1)+(p-7)=7k+2<m`.

Hence all three boundaries are impossible when `p=6k+1`.

## 5. Boundaries when `p=6k-1`

Here

`h=3k-1`, `m=9k-2`, `k>=2`.

### Boundary `d=0`

Then `(r,t)=(3k-3,p-1)`. Take

`n=2k`.

The multiplied coefficient vector is

`(D,A,B)=(1,k-1,4k-1)`.

It is componentwise bounded by `(3,r,t)` and is a nonempty proper coefficient relation inside `V`. This contradicts that `V` is an atom.

### Boundary `d=1`

Then `(r,t)=(3k-2,p-2)`. Take

`n=4k+1`.

The residues are

`(D,A,B)=(5,3k-3,4k-4)`.

The length is

`5+(3k-3)+(4k-4)=7k-2<m`.

### Boundary `d=2`

Then `(r,t)=(3k-1,p-3)`. Take

`n=2k+1`.

The residues are

`(D,A,B)=(4,2k-1,p-4)`.

The length is

`4+(2k-1)+(p-4)=8k-2<m`.

Hence all three boundaries are impossible when `p=6k-1`.

## 6. The prime `p=7`

The exact light multi-copy criterion for `a=2` gives

`c_light=2 floor((p-1)/4)`.

At `p=7`, this is `c_light=2`. Therefore a companion with `c=3` is already impossible before the new values `x,y` are considered.

No finite depth enumeration is needed.

## 7. Theorem and combined consequence

> **Theorem.** For every prime `p>=7`, an exact-support-six first-corridor maximal pair with support-four maximal atom of type `a=2` cannot have a support-three rank-two light-share companion with
>
> `v_e3(V)=3`.

Combining this with the one- and two-share theorem gives

`boxed{v_e3(V)>=4}`

for every hypothetical `a=2` light-share support-three equality companion over every prime `p>=7`.

The exact multi-copy criterion also gives

`v_e3(V)<=2 floor((p-1)/4)`.

Thus the surviving arithmetic window is

`boxed{4<=v_e3(V)<=2 floor((p-1)/4).}`

At `p=7` this window is empty, reproducing the analytic closure of the full `a=2` support-three branch. At `p=11`, only the single layer `c=4` remains.

## 8. ORION verification architecture

`check_a2_light_support3_three_share_elimination_v1.py` verifies every symbolic residue, capacity, and length identity through prime `1009`. It then performs a complete all-multiplier scan over every atom-compatible multiplicity row after the exact multi-copy ceiling. The scan contains **9826** rows and leaves zero residuals.

`verify_a2_light_support3_three_share_independent_v1.cpp` does not follow the symbolic congruence split. It:

- computes the shortest cost of each radial target `D s` by bounded enumeration of the actual resources `s^5 g^(p-2)e1^(p-1)e2^(p-1)`;
- scans every scalar multiplier for every atom-compatible row through prime `1009`;
- again returns zero residuals.

A hostile mutation disables the synthesis identity and permits only the five actual copies of `s`. That mutation leaves **1309** residual rows through prime `1009`, with SHA-256

`2e7593e3c4af58ff9781fe569253fbd94280aa6fb2ebce2bb8a60c0ca5cfa35e`.

This positive control demonstrates that the radial synthesis mechanism is load-bearing rather than decorative.

The branch workflow runs the primary replay, the independent optimized replay, and the independent replay under AddressSanitizer and UndefinedBehaviorSanitizer.

## Boundary

- The `a=2` light-share family with shared multiplicity `c>=4` remains open.
- The `a=2` support-four rank-three equality branch remains open.
- The theorem assumes the first maximal corridor and a support-four maximal atom.
- No `D_3(C_p^3)` value, all-`k` formula, or novelty/priority claim is made.
