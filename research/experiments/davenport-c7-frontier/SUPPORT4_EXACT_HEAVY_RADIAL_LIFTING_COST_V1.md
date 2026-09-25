# Exact heavy-direction radial lifting cost for support-four maximal pairs — V1

Status: **proved prime-uniform structural theorem**. This is the heavy-direction companion to `SUPPORT4_EXACT_RADIAL_LIFTING_COST_V1.md`. It computes the exact shortest realization of a multiple of the heavy unsaturated direction when the companion reuses that value. No support-seven, generalized Davenport, or novelty/priority claim is made.

## 1. Setup

Let

`U=e1^(p-1)e2^(p-1)s^a g^(p-a)`,

`g=s-u(e1+e2)`, `u=a^(-1) mod p`, `1<=a<=(p-1)/2`.

Suppose the companion contributes `c` additional copies of `g`. Pair `p`-short-freeness gives

`c<=a-1`,

so the pair contains the radial resources

`e1^(p-1)e2^(p-1)s^a g^(p-a+c)`,

with `p-a+c<=p-1`.

For `D in {0,...,p-1}`, let `mu_{a,c}(D)` be the minimum number of these terms whose sum is `D g`.

## 2. Exact formula

> **Theorem.** For every `D`,
>
> `boxed{mu_{a,c}(D)=min (z+q+2[u(q-D)]_p),}`
>
> where the minimum is over
>
> `0<=q<=p-a+c`, `0<=z<=a`, `z+q == D (mod p)`.

Equivalently, for fixed `q`, put `z=[D-q]_p` and retain only the values with `z<=a`.

## 3. Proof

Take a radial representation with counts

`alpha,beta,z,q`

on `e1,e2,s,g`. Its sum is

`(alpha-uq)e1+(beta-uq)e2+(z+q)s`.

The target is

`Dg=-Du e1-Du e2+D s`.

Thus

`z+q ==D (mod p)`

and

`alpha == beta == u(q-D) (mod p)`.

Since `0<=alpha,beta<=p-1`, both saturated-axis counts are uniquely forced to

`[u(q-D)]_p`.

Therefore every representation has length

`z+q+2[u(q-D)]_p`

for a feasible `(q,z)`, and conversely every feasible pair produces the required subsequence. Minimizing proves the formula.

## 4. Literal-copy regime

A particularly useful case is `D<=p-a+c`, when the pair contains `D` literal copies of `g`. Taking

`q=D`, `z=0`

gives

`mu_{a,c}(D)<=D`.

Since no nonempty subsequence can have length below one, this is the natural radial baseline; for the doubling application below only the displayed upper bound is needed.

For a heavy-share support-three companion, `c<=a-1` and `a<=(p-1)/2`, so

`c<=p-a`.

Hence

`2c<=p-a+c`,

and therefore

`boxed{mu_{a,c}(2c)<=2c.}`

In fact the target is realized by `2c` actual copies of `g`, with no saturated-axis synthesis at all.

## 5. Relation to the light radial theorem

The two exact formulas differ only by the target coordinates forced on the saturated axes:

- light target `D s`: axis count `[u q]_p`;
- heavy target `D g`: axis count `[u(q-D)]_p`.

Thus both overlap directions now have exact one-dimensional radial cost oracles. Boundary multiplier arguments may optimize the appropriate oracle rather than deriving separate ad hoc identities.

## Verification receipt

`check_support4_exact_heavy_radial_lifting_cost_v1.py` compares the formula with an occurrence-level shortest-cost DP on the bounded primes `5,7,11`, across every canonical support-four type, every admissible heavy overlap, and every radial target. A larger arithmetic control checks the literal-copy `2c` regime through prime `401`.

The checker is regression only; theorem authority is the coordinate-forcing proof above.

## Boundary

- The theorem is a radial cost theorem, not a companion-existence theorem.
- It assumes the heavy actual-value overlap count satisfies the pair capacity `c<=a-1`.
- Boundary multiplicity rows and rank-three companions require additional arguments.
