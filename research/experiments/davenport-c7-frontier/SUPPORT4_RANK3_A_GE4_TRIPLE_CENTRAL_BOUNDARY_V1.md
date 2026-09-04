# Rank-three `a>=4` central boundary is killed by the scalar three — V1

Status: **proved prime-uniform structural elimination on an explicit central region**. After the doubling reduction, a rank-three support-four equality box of type `a>=4` is impossible whenever four simple boundary/capacity inequalities hold. The resulting forbidden zero-sum has length exactly `m-1`.

No claim is made that these four inequalities cover the whole boundary for every prime.

## 1. Boundary setup

Let

`p=2H+1`, `m=3H+1`,

and consider a rank-three exact-support-six companion

`V=s^c g^d x^r y^t`

of canonical maximal type `a>=4`.

By `SUPPORT4_SIMULTANEOUS_OVERLAP_SUM_BOUND_V1.md`, put

`S=c+d<=a-2`.

By `SUPPORT4_RANK3_A_GE4_DOUBLING_BOUNDARY_REDUCTION_V1.md`, every survivor can be written

`r=H-k`, `t=p-S+k`,

with

`0<=k<=S-1`.

Assume the four inequalities

`boxed{3k<=H-2,}`

`boxed{3(S-k)<=2H,}`

`boxed{2c<=a,}`

`boxed{2d<=p-a.}`

We prove the box is impossible.

## 2. New-value residues under the scalar three

Triple the companion relation.

For x,

`3r=3(H-k)=p+(H-3k-1)`.

The first boundary inequality gives

`H-3k-1>=1`,

so the least residue is

`boxed{R=H-3k-1.}`

Clearly `R<=H-k=r`.

For y, write

`t=p-(S-k)`.

The second boundary inequality gives

`3(S-k)<p`.

Therefore

`boxed{T=p-3(S-k).}`

Since `S-k>=1`, one has

`T<=p-(S-k)=t`.

Thus

`x^R y^T`

is an actual subsequence of V.

Its coefficient length is

`R+T`

`=H-3k-1+p-3S+3k`

`=boxed{3H-3S.}`

## 3. Literal cancellation of the overlap target

The tripled relation shows that the new-value subsequence has sum

`-3c s-3d g`.

The pair contains

`a+c`

actual copies of s and

`p-a+d`

actual copies of g.

The last two assumed inequalities are exactly

`3c<=a+c`,

`3d<=p-a+d`.

Hence the pair contains the literal cancelling subsequence

`s^(3c) g^(3d)`.

The resulting zero-sum has length

`R+T+3c+3d`

`=3H-3S+3S`

`=boxed{3H=m-1.}`

This contradicts pair short-freeness.

## 4. Theorem

> **Scalar-three central-boundary theorem.** Every first-corridor rank-three exact-support-six box of maximal type `a>=4` satisfying
>
> `3k<=H-2`, `3(S-k)<=2H`, `2c<=a`, `2d<=p-a`
>
> is impossible.

Consequently every surviving boundary box must violate at least one of these four inequalities.

The four failure modes have distinct meanings:

1. **right new-value edge:** `k>(H-2)/3`;
2. **left new-value edge:** `S-k>2H/3`;
3. **light-heavy imbalance toward s:** `c>a/2`;
4. **light-heavy imbalance toward g:** `d>(p-a)/2`.

This gives a finite set of structural edge regimes for the next scalar argument.

## 5. Verification receipt

`check_support4_rank3_a_ge4_triple_central_boundary_v1.py` verifies every residue identity, capacity inequality, and exact `m-1` length formula for every prime through `2003`, every `a>=4`, every positive `(c,d)` under `c+d<=a-2`, and every boundary index k satisfying the four theorem hypotheses.

A separate bounded diagnostic compares the theorem against the coefficient-atom boundary census; that percentage is discovery metadata only and grants no theorem authority beyond the stated four inequalities.

## Boundary

- Boxes violating one or more of the four inequalities remain.
- Types `a=2,3` remain separate exceptional rank-three mechanisms.
- No `D_3(C_p^3)` value or all-k formula is claimed.
