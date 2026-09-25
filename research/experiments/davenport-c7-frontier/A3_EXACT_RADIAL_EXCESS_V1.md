# Exact `a=3` light radial excess — V1

Status: **proved prime-uniform exact formula**. For the canonical support-four maximal type `a=3`, the exact pair radial cost above the target coefficient has a closed staircase form. This upgrades the radial component of `A3_LIGHT_EXACT_DEPTH_AND_TWO_PARAMETER_FACE_V1.md` and is used by the upper-boundary elimination.

## 1. Setup

Let

`p>=7` be prime, `u=3^(-1) mod p`,

and suppose the companion contributes `c>=1` additional copies of the light value `s` to

`U=e1^(p-1)e2^(p-1)s^3 g^(p-3)`.

Thus the pair has `c+3` literal copies of `s`.

For `1<=D<=p-1`, let `lambda_{3,c}(D)` be the exact minimum number of pair terms whose sum is `D s`.

The general exact radial theorem gives

`lambda_{3,c}(D)=min (z+q+2[uq]_p)`

over

`0<=z<=c+3`, `0<=q<=p-3`, `z+q==D (mod p)`.

## 2. Wrapped radial representations are never optimal

If `z+q=D+p`, then the contribution `z+q` alone is `D+p`, so the excess above the target is at least `p`.

A nonwrapped admissible representation exists and will have excess strictly below `p`. Therefore every minimizer may be taken with

`z+q=D`.

Put `q=D-z`. The allowed q-values form the integer interval

`I_D=[max(0,D-c-3), min(D,p-3)]`.

Hence

`boxed{lambda_{3,c}(D)-D = 2 min_{q in I_D} [u q]_p.}`

## 3. Residues of the inverse of three below `p-3`

Write either

`p=3M+1`, so `u=2M+1`,

or

`p=3M+2`, so `u=M+1`.

For every `q<=p-3`, write `q=3j+r`, `r in {0,1,2}`.

In both congruence classes one has

`[u(3j)]_p=j`,

while the residues for `r=1,2` are strictly larger than `j` throughout the allowed range `q<=p-3`.

Explicitly:

- if `p=3M+1`, the two nonzero classes give `j+2M+1` and `j+M+1`;
- if `p=3M+2`, they give `j+M+1` and `j+2M+2`.

No displayed expression wraps in its allowed range.

Therefore, on any interval of at least three consecutive integers inside `[0,p-3]`, the smallest `u`-residue is attained at the **first multiple of three** in the interval.

The interval `I_D` always contains such a multiple: if it starts at zero this is immediate; otherwise its inclusive length is at least three because `c>=1`, including at the endpoint targets `D=p-2,p-1`.

## 4. Exact staircase formula

Set

`L=max(0,D-c-3)`.

The first multiple of three at or above `L` is

`3 ceil(L/3)`,

and its `u`-residue is exactly `ceil(L/3)`.

Thus:

> **Exact radial-excess theorem.** For every prime `p>=7`, every `c>=1` in the pair-capacity range, and every `1<=D<=p-1`,
>
> `boxed{lambda_{3,c}(D)-D = 2 ceil(max(D-c-3,0)/3).}`

Equivalently,

`boxed{lambda_{3,c}(D)=D+2 ceil(max(D-c-3,0)/3).}`

In particular the radial cost is literal, `lambda=D`, exactly on

`1<=D<=c+3`.

## 5. Strategic consequence

Any scalar-multiplier certificate in the `a=3` light face now needs no radial minimization. Once its light residue `D` is known, the radial surcharge is the explicit staircase

`0,0,...,0,2,2,2,4,4,4,...`.

This turns both the non-upper index-one interface and the upper odd-multiplier interface into pure residue inequalities.

## Verification receipt

`check_a3_exact_radial_excess_v1.py` compares the closed formula to the general exact radial oracle for every prime through `401`, every admissible `c` under the first-corridor light overlap ceiling, and every nonzero target `D`.

The checker is regression only; theorem authority is the inverse-three residue proof above.

## Boundary

- This is a radial cost theorem only.
- It does not by itself establish a compatible scalar multiplier.
- No generalized Davenport constant or novelty/priority claim is made.
