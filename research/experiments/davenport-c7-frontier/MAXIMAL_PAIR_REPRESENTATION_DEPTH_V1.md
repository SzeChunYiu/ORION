# Exact representation-depth criterion for support-four maximal pairs — V1

Status: **proved prime-uniform criterion plus independent finite replay**. This converts the maximal-pair short-free condition into a shortest-representation metric on the maximal atom and gives a closed one-parameter depth formula for every support-four maximal atom. No generalized Davenport value or novelty/priority claim is made here.

## 1. The graded depth criterion

Let `U,V` be atoms over `G=C_p^3`, with `U` maximal:

`|U|=3p-2`.

In a prime-uniform maximal corridor write

`|V|=m=p+b`,

where `b=(p+1)/2-j`. Hereditary rigidity gives `z(UV)=2`, and the pair-complement lemma gives the exact short-free window

`UV` has no nonempty zero-sum subsequence of length at most `m-1`.

For `x in G`, define the U-representation depth

`rho_U(x)=min{|T| : T|U, sigma(T)=x}`,

with `rho_U(0)=0` and `rho_U(x)=infinity` if no such subsequence exists.

Let `W|V` be nonempty and proper. Since `V` is an atom, `sigma(W)!=0`.

A mixed zero-sum using exactly the V-part `W` exists with minimum possible length

`|W|+rho_U(-sigma(W))`.

Therefore:

> **Graded depth criterion.** The pair `UV` is `(m-1)`-short-zero-free if and only if, for every nonempty proper `W|V`,
>
> `boxed{|W|+rho_U(-sigma(W)) >= m.}`

The pure-U and pure-V cases cause no extra condition: `U` and `V` are atoms and both full zero-sums have length greater than `m-1`.

Equivalently,

`boxed{rho_U(-sigma(W)) >= m-|W|.}`

Taking the complementary subsequence `Y=V W^{-1}` gives the symmetric form

`boxed{rho_U(sigma(Y)) >= |Y|.}`

Thus for every nonempty proper `Y|V`, both orientations obey

`rho_U(sigma(Y)) >= |Y|`,

`rho_U(-sigma(Y)) >= m-|Y|`.

In particular

`rho_U(sigma(Y))+rho_U(-sigma(Y)) >= m`.

This strictly organizes the earlier one- and two-term avoidance statements inside a maximal corridor: the exclusion depth changes linearly with the size of the companion subsequence rather than stopping at a fixed depth two.

## 2. Closed depth formula for a support-four maximal atom

Assume now that `U` has support four. By the prime-uniform classification, after an automorphism

`U=e1^(p-1)e2^(p-1)e3^a g4^(p-a)`,

where

`g4=e3-a^{-1}(e1+e2)`, `1<=a<=(p-1)/2`.

Write a target as

`x=(x1,x2,x3) in F_p^3`.

A subsequence of `U` has count vector

`(c1,c2,c3,t)`

with

`0<=c1,c2<=p-1`, `0<=c3<=a`, `0<=t<=p-a`.

Its sum is

`(c1-a^{-1}t, c2-a^{-1}t, c3+t)`.

For a fixed value of `t`, the first two coordinates determine uniquely

`c1=[x1+a^{-1}t]_p`,

`c2=[x2+a^{-1}t]_p`,

where `[.]_p` is the least residue in `{0,...,p-1}`. The third coordinate requires

`c3=[x3-t]_p<=a`.

Hence:

> **Exact support-four depth formula**
>
> `rho_U(x) = min_t ( [x1+a^{-1}t]_p + [x2+a^{-1}t]_p + [x3-t]_p + t )`,
>
> where the minimum is over
>
> `0<=t<=p-a` with `[x3-t]_p<=a`.

Every admissible tuple automatically respects the multiplicity bounds on `e1,e2`; the displayed condition is exactly the remaining `e3` bound. Thus this is an equality, not merely an upper bound.

The depth of any target is therefore computed by at most `p-a+1<=p` scalar trials. No enumeration of the exponentially many subsequences of `U` is needed.

## 3. Exact companion test

Combining the two theorems gives an exact compatibility test for a candidate companion `V` of length `m`:

1. enumerate the nonempty proper companion subsequence sums by cardinality;
2. for every sum `s` arising at cardinality `r`, evaluate the one-parameter formula for `rho_U(-s)`;
3. reject exactly when

`r+rho_U(-s)<=m-1`.

At the final full companion, `sigma(V)=0` and `|V|=m`, so the full atom itself is allowed.

This test is mathematically equivalent to `(m-1)`-short-freeness of `UV` under the atom hypotheses. It replaces the old implementation that first materialized all bounded-cardinality subset sums of the large maximal atom.

The pair multiplicity capacities are still imposed directly:

`v_x(V)<=p-1-v_x(U)`

for every actual group element `x`, since `UV` is p-short-free.

## 4. Independent finite replay

`search_support4_maximal_pair_depth_oracle_v1.cpp` implements only the depth formula and cardinality-indexed companion subset sums. It does **not** build the maximal atom's subset-sum tables used by `search_support4_81019_v1.cpp`.

For the first corridor `j=1` it gives:

### p=5

- `a=1`: 169 compatible length-7 companions;
- `a=2`: 30 compatible length-7 companions.

These are a finite base census only; the p=5 generalized Davenport value is already settled elsewhere and receives no new credit here.

### p=7

- `a=1`: 538 compatible length-10 companions;
- `a=2`: 24;
- `a=3`: 0.

The p=7 counts exactly reproduce the independently frozen first stage of the `(8,10,19)` support-four closure, but through a different state representation. This is a strong regression of both the depth formula and the pair criterion.

A direct p=11 companion enumeration with this unoptimized generic DFS did not complete inside the bounded local run used while developing this file. That is recorded as an implementation/resource boundary, not a mathematical obstruction; the depth theorem itself is prime-uniform.

## 5. Strategic consequence

The remaining all-prime support-four maximal-pair problem can now be attacked as a metric problem on `F_p^3`:

- `rho_U` is explicit;
- every proper companion subsequence of size `r` must land outside the depth ball

`{x : rho_U(-x)<=m-r-1}`;

- complementing inside `V` simultaneously constrains the opposite depth;
- exact support-six normal forms can be tested against these nested depth shells without enumerating U-subsequences.

This creates a natural route to a theorem about the geometry/cardinality of the depth shells. Such a theorem would generalize the finite C7 closure rather than merely replaying it at larger primes.

## Boundary

- This file does not prove that support-six is impossible.
- The p=5 and p=7 counts are bounded finite evidence, not an all-prime census.
- No p=11 count is claimed.
- No `D_3(C_p^3)` value or novelty/priority claim is made.
