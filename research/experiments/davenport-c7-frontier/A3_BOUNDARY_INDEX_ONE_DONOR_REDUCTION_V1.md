# `a=3` boundary rows reduce to an index-one capacity problem — V1

Status: **proved prime-uniform donor reduction**. Every non-upper boundary row in the exceptional `a=3` light-share support-three face carries a length-four cyclic coefficient sequence to which the classical index-one theorem applies. This reduces arbitrary scalar-multiplier search to a capacity-aware choice among index-one multipliers. It does not yet prove that such a multiplier always fits the companion capacities.

No generalized Davenport value or novelty/priority claim is made.

## 1. Setup

Keep the first-corridor `a=3` notation

`p=2H+1>=7`, `m=3H+1`,

`V=s^c x^r y^t`.

By `A3_LIGHT_EXACT_DEPTH_AND_TWO_PARAMETER_FACE_V1.md`,

`c<=c_light<=floor(H/2)`.

After the all-type interior theorem, write a boundary row as

`r=H+1-c+d`, `t=p-1-d`, `0<=d<c`.

It is convenient to put

`e=c-d`, `f=d+1`.

Then

`e,f>=1`, `e+f=c+1`,

and

`boxed{r=H+1-e, t=p-f.}`

The upper endpoint is `e=1` (equivalently `d=c-1`).

## 2. The augmented coefficient sequence

Append the half coefficient `H+1` to the companion coefficient triple and consider the sequence over `C_p`

`T=(c)(r)(t)(H+1)`.

Its ordinary coefficient sum is

`c+r+t+(H+1)=m+(H+1)=2p`.

Thus `T` is a zero-sum sequence of length four over the cyclic group `C_p`.

## 3. Every non-upper boundary gives a minimal zero-sum sequence

Assume `e>1`.

All four coefficients lie in `1,...,p-1`. Since the total sum is `2p`, a proper zero-sum subsequence can only be a pair summing to `p`: a three-term zero-sum would force the omitted singleton itself to be zero modulo `p`.

We inspect the six pair sums.

Using `e+f=c+1`:

`c+t=p+(e-1)>p`,

`r+(H+1)=p+1-e<p`,

so neither equals `p` when `e>1`.

The remaining pairs cannot equal `p` because `c<=floor(H/2)`:

`c+r=H+f<p`,

`c+(H+1)<p`,

`r+t=p+H-c>p`,

`t+(H+1)>p`.

Hence no proper nonempty subsequence of `T` is zero-sum.

Therefore:

> **Minimal augmented-sequence lemma.** If `e>1`, then
>
> `boxed{T=(c)(r)(t)(H+1)}`
>
> is a minimal zero-sum sequence of length four over `C_p`.

## 4. Donor theorem: index one

Li, Plyley, Yuan and Zeng proved in

Y. Li, C. Plyley, P. Yuan, X. Zeng, *Minimal zero sum sequences of length four over finite cyclic groups*, Journal of Number Theory 130 (2010), 2033–2048, DOI `10.1016/j.jnt.2009.12.005`,

that every minimal zero-sum sequence of length four over a cyclic prime-power group whose order is coprime to `6` has index one.

Here the group order is the prime `p>=7`, so the theorem applies.

Consequently there exists a nonzero scalar `n in F_p` such that, writing least positive residues

`D=[nc]_p`, `A=[nr]_p`, `B=[nt]_p`, `L=[n(H+1)]_p`,

one has

`boxed{D+A+B+L=p.}`

This is a donor-owned theorem application, not an ORION novelty claim.

## 5. Exact capacity identity for an index-one multiplier

Since `t=p-f`,

`B=[n(p-f)]_p=p-[nf]_p`.

Put

`F=[nf]_p`.

The index-one identity becomes

`D+A+(p-F)+L=p`,

hence

> `boxed{F=D+A+L.}`

In particular

`A=F-D-L>0`.

The two new-value capacity conditions now have the exact scalar form

`B<=t <=> F>=f`,

and

`A<=r <=> F-D-L<=H+1-e`.

Thus a donor-produced index-one scalar is capacity-compatible precisely when

`boxed{F>=f, F-D-L<=H+1-e.}`

No three-dimensional group geometry occurs in these two tests.

## 6. Exact radial short-zero criterion

For a capacity-compatible index-one scalar, the multiplied companion relation is

`D s+A x+B y=0`.

Let `lambda_{3,c}(D)` be the exact light-direction radial cost from
`SUPPORT4_EXACT_RADIAL_LIFTING_COST_V1.md`, using the actual resources of `UV`.

The scalar yields a forbidden short zero-sum exactly when

`lambda_{3,c}(D)+A+B<=m-1`.

Using `A+B=p-D-L`, this is equivalent to

> `boxed{lambda_{3,c}(D)-D<=H+L-1.}`

Therefore every non-upper `a=3` boundary row is reduced to the following one-dimensional problem:

> among the index-one multipliers of `(c,r,t,H+1)`, find one satisfying
>
> `F>=f`,
>
> `F-D-L<=H+1-e`,
>
> `lambda_{3,c}(D)-D<=H+L-1`.

This is the **capacity-aware index-one interface**.

## 7. The upper endpoint is exactly the exceptional nonminimal row

If `e=1`, then `f=c`,

`r=H`, `t=p-c`.

The augmented sequence is

`(c)(H)(p-c)(H+1)`.

It is not minimal because it splits into the two zero-sum pairs

`c+(p-c)=p`,

`H+(H+1)=p`.

Thus the failure of the index-one donor interface at the upper endpoint is structural, not an artifact of the proof.

This endpoint must be handled by a separate multiplier or depth argument.

## 8. Verification and discovery control

`check_a3_boundary_index_one_reduction_v1.py` verifies through prime `1009` that every non-upper admissible `a=3` boundary row gives a minimal augmented sequence and that the exact residue identities above hold for every index-one multiplier.

As a non-authorizing discovery control, it additionally scans all such rows through prime `199` and confirms that at least one index-one multiplier satisfies both capacity inequalities and the exact radial short-zero inequality in every row tested.

This strongly isolates the missing analytic step: prove the capacity-aware existence statement prime-uniformly. The finite scan is not used as theorem authority.

## Boundary

- The existence of a **usable** index-one multiplier is not proved here.
- The upper endpoint `e=1` is excluded from the donor reduction and remains separate.
- The rank-three support-four companion remains open.
- No `D_3(C_p^3)` value or all-`k` formula is claimed.
