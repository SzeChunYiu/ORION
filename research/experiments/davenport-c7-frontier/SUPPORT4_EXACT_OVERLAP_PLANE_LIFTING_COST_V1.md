# Exact overlap-plane lifting cost and rank-three scalar certificate — V1

Status: **proved prime-uniform structural theorem**. For a canonical support-four maximal atom, this file computes the exact shortest `U`-subsequence representing an arbitrary target in the plane spanned by the two unsaturated maximal-atom values. It then turns every rank-three support-four companion into a multiplicity-only scalar test before any geometry of the two new values is used.

No support-seven theorem, generalized Davenport value, or novelty/priority claim is made here.

## 1. Canonical maximal atom

Let

`U=e1^(p-1)e2^(p-1)s^a g^(p-a)`,

where

`g=s-u(e1+e2)`, `u=a^(-1) mod p`, `1<=a<=(p-1)/2`.

The two unsaturated support values `s,g` span a rank-two plane. For coefficients

`C,D in {0,...,p-1}`,

let

`nu_a(C,D)`

be the minimum number of terms in a subsequence of `U` whose sum is

`C s+D g`.

## 2. Exact overlap-plane formula

Take a subsequence of `U` with counts

`alpha,beta,z,q`

on `e1,e2,s,g`. Its sum is

`(alpha-uq)e1+(beta-uq)e2+(z+q)s`.

The target is

`C s+D g`

`=-Du e1-Du e2+(C+D)s`.

Therefore the saturated coordinates force

`alpha == beta == u(q-D) (mod p)`.

Since `0<=alpha,beta<=p-1`, both counts are uniquely determined as

`boxed{alpha=beta=[u(q-D)]_p.}`

The radial coordinate forces

`z+q == C+D (mod p)`.

The resource bounds are

`0<=q<=p-a`, `0<=z<=a`.

Hence every representation has length

`z+q+2[u(q-D)]_p`

for a feasible pair `(q,z)`, and every feasible pair produces exactly such a representation.

Thus:

> **Exact overlap-plane lifting theorem.**
>
> `boxed{nu_a(C,D)=min (z+q+2[u(q-D)]_p),}`
>
> where the minimum is over
>
> `0<=q<=p-a`, `0<=z<=a`, `z+q==C+D (mod p)`.

Equivalently, for each `z=0,...,a`, set

`q=[C+D-z]_p`

and retain it only when `q<=p-a`. Therefore the exact cost needs at most `a+1` scalar trials.

## 3. Recovery of the one-direction depth formulas

The formula contains the previous radial interfaces as special cases at the `U`-only level:

- `D=0` gives the exact cost of a light target `C s` using only the maximal atom;
- `C=0` gives the exact cost of a heavy target `D g` using only the maximal atom.

The earlier pair-radial theorems can be strictly cheaper because they also permit the companion's actual overlap copies. The present theorem deliberately uses only `U`; this is what makes it usable when a scalar subsequence is chosen entirely from the two genuinely new companion values.

## 4. Rank-three support-six companion

Now work in the first maximal corridor and suppose the exact-support-six equality face is rank three:

`V=s^c g^d x^r y^t`,

with all four multiplicities positive and

`c+d+r+t=m`, `m=(3p-1)/2`.

Here `x,y` are the two genuinely new support values.

For any scalar

`n in {1,...,p-1}`,

put

`C=[nc]_p`, `D=[nd]_p`, `R=[nr]_p`, `T=[nt]_p`.

Because the full companion relation is

`c s+d g+r x+t y=0`,

one has in the group

`R x+T y = -C s-D g`.

This identity is valid even when `C>c` or `D>d`; subtracting multiples of `p` from the scalar coefficients does not change the group sum.

If

`R<=r`, `T<=t`,

then

`W=x^R y^T`

is an actual nonempty subsequence of `V`. Since `R,T` are nonzero for nonzero n and `r,t<p`, the subsequence is nonempty. If `W` were all of `V`, it would omit the positive `s,g` multiplicities, so it is proper.

The overlap-plane theorem supplies a `U`-subsequence of length `nu_a(C,D)` cancelling its sum. Therefore:

> **Rank-three scalar-plane certificate.** If some nonzero scalar n satisfies
>
> `boxed{R<=r, T<=t, R+T+nu_a(C,D)<=m-1,}`
>
> then the exact-support-six rank-three companion is impossible.

The resulting zero-sum lies in `UV`, is nonempty, and has forbidden length at most `m-1`.

## 5. Why this is a useful reduction

The rank-three equality face originally involves two unrestricted new values in `C_p^3`. The scalar-plane certificate removes them from the first obstruction test entirely:

1. choose the support-four maximal type `a`;
2. choose only the four multiplicities `(c,d,r,t)`;
3. apply the exact light/heavy overlap ceilings;
4. scan scalar residues of `r,t`;
5. evaluate `nu_a(C,D)` by at most `a+1` one-dimensional trials.

Only multiplicity boxes surviving this exact arithmetic test require any further projective geometry or simultaneous quotient-atomicity analysis.

## 6. Discovery control

`check_support4_overlap_plane_rank3_scalar_v1.py` has two roles that are kept separate.

First, it verifies the exact formula against an occurrence-level shortest-path dynamic program on bounded small primes. This is regression for the theorem.

Second, as **discovery only**, it enumerates first-corridor rank-three multiplicity boxes on a bounded prime range, enforces the exact light/heavy multi-copy ceilings and coefficient-atom condition, and applies the scalar-plane certificate. In that bounded scan, every residual with maximal type `a>=4` disappears; the remaining arithmetic residuals occur only for the exceptional types `a=2,3`.

That bounded residual pattern is not promoted to an all-prime theorem in this file. It is the next theorem-discovery target.

## Boundary

- Absence of a scalar-plane certificate does not imply a companion exists.
- The theorem does not use the simultaneous quotient-atom constraints; those remain available for residual boxes.
- The bounded `a>=4` disappearance is discovery evidence only until a symbolic argument is written.
- No `D_3(C_p^3)` value or all-k formula is claimed.
