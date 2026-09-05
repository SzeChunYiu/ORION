# All-type heavy-share interior elimination — V1

Status: **proved prime-uniform structural theorem**. For every canonical support-four maximal type, every first-corridor support-three equality companion that shares only the heavy unsaturated value is forced onto the boundary strip `d<c`. The interior is killed by doubling with a zero-sum of length exactly `p-1`.

This is independent of the earlier `a=2` heavy boundary theorem and does not close all heavy-share boundary rows. No generalized Davenport or novelty/priority claim is made.

## 1. Setup

Let

`p=2H+1>=7`, `m=3H+1`,

and

`U=e1^(p-1)e2^(p-1)s^a g^(p-a)`,

`1<=a<=H`.

Suppose an exact-support-six support-three companion shares only the heavy value:

`V=g^c x^r y^t`, `r<=t<=p-1`.

Pair `p`-short-freeness bounds the shared multiplicity by

`c<=a-1`,

because `U` already contains `p-a` copies of `g`.

As in the light-share parametrization, write

`r=H+1-c+d`, `t=2H-d`, `d>=0`.

The atom relation is

`c g+r x+t y=0`.

## 2. Heavy radial reserve

The pair contains

`p-a+c`

actual copies of `g`.

Since

`c<=a-1<=H-1<p-a`,

we have

`2c<=p-a+c`.

Thus the pair contains at least `2c` literal copies of `g`. Equivalently, the exact heavy radial theorem gives

`mu_{a,c}(2c)<=2c`.

Also `2c<p`, so doubling does not wrap the shared coefficient.

## 3. Interior doubling

Assume `d>=c`. Doubling the companion relation gives

`2c g+A x+B y=0`,

where

`A=2d-2c+1`,

`B=p-2d-2`.

Exactly as in the light-share interior calculation,

`1<=A<=r`, `1<=B<=t`,

and

`A+B=p-2c-1`.

Use `2c` of the literal copies of `g` from `UV`. The resulting actual zero-sum subsequence has length

`2c+A+B`

`=2c+p-2c-1`

`=boxed{p-1}.`

Since

`p-1<m`,

this contradicts inherited `(m-1)`-short-freeness.

Therefore:

> **All-type heavy interior theorem.** For every prime `p>=7` and every canonical support-four type `a`, a hypothetical exact-support-six first-corridor support-three companion sharing only the heavy value must satisfy
>
> `boxed{0<=d<c.}`
>
> Every heavy-share interior row `d>=c` is impossible.

## 4. Relation to the existing `a=2` theorem

For `a=2`, pair capacity gives `c<=1`. Hence the only heavy-share layer has `c=1`, and its boundary strip consists only of `d=0`.

`A2_HEAVY_SUPPORT3_DOUBLE_TRIPLE_V1.md` eliminates precisely that remaining boundary row. Thus the earlier theorem plus the present all-type interior result completely explain the disappearance of the `a=2` heavy-share support-three face.

For larger `a`, the present theorem removes every interior row at once, leaving only the finite boundary strip `d=0,...,c-1` for `1<=c<=a-1`.

## 5. Strategic consequence

Both overlap directions now have all-type interior reductions:

- **light share:** every interior is impossible for `a>=2`; only the exceptional high-overlap `a=1` regime can evade doubling;
- **heavy share:** every interior is impossible for every `a`, with no exception.

Therefore the rank-two part of the first-corridor theorem is increasingly a **boundary classification problem**, not a bulk multiplicity problem.

The natural next theorem is a unified boundary multiplier/stability lemma using the exact light and heavy radial cost functions.

## Verification receipt

`check_support4_alltype_heavy_interior_elimination_v1.py` exhausts the meaningful parameter interface on bounded primes and checks the pair-capacity, literal `2c` resource, doubled residues, coefficient capacities, and exact `p-1` certificate length. A large-prime arithmetic control verifies the load-bearing inequalities through prime `1009`.

The checker is regression only; theorem authority is the symbolic calculation above.

## Boundary

- Heavy-share boundary rows `0<=d<c` remain open in general.
- The theorem assumes the support-four maximal-atom equality normal form and first corridor.
- Rank-three support-four companions remain a separate mechanism.
