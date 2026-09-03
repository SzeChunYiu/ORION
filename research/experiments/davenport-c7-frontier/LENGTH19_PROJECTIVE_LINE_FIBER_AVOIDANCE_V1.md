# Length-19 corridors: projective line-fiber avoidance — V1

Status: **proved analytic reduction plus two exact finite checkers at `p=7`**. Both `(8,10,19)` and `(9,9,19)` remain open after this reduction.

## 1. Setup from factorization theory

Let `G=C_p^3`. Let `U` and `V` be atoms such that

- `|U|=D(G)=3p-2`, and
- the product `UV` has no factorization into three nonempty zero-sum sequences.

The proper-subsum avoidance lemma in `CROSS_CONTEXT_REFRAME_V1.md` gives, for each occurrence `u|U`,

`u notin Sigma_{2..|V|-1}(V)`.

Fix a projective direction `L=<e>` and write the terms of `V` on that direction as the scalar sequence

`A=(a_1,...,a_r)` in `F_p^*`, so the corresponding vectors are `a_i e`.

Assume additionally that

- `A` is zero-sumfree in `C_p`, and
- `|V|-r>=2`.

Both conditions hold in the two `p=7` length-19 corridors: the full obstruction is 7-short-zero-free, `r<=6`, and `|V|` is 9 or 10.

Define

`R(A)=F_p^* \ (Sigma_{>=2}(A) union -Sigma_{>=1}(A))`.

> **Line-fiber avoidance lemma.** If an occurrence of `U` lies on `L` with scalar `x`, then `x in R(A)`.

### Proof

If `x` is a sum of at least two terms of `A`, the corresponding line subsequence is a proper subsequence of `V` of size at least two and sum `x e`, contradicting proper-subsum avoidance.

If `x=-sigma(X)` for a nonempty subsequence `X|A`, then `V\X` has sum `x e`. It is proper, and

`2<=|V|-r<=|V\X|<=|V|-1`.

Applying proper-subsum avoidance to `V\X` gives the second exclusion.

This converts the global non-refactorization condition into a restricted-subsum filter on each one-dimensional projective fiber.

## 2. Prime-uniform long-fiber bound

Let `A` be zero-sumfree in `C_p` with length `r>p/2`, and put `d=|R(A)|`.

Savchev and Chen prove that, after multiplication by a nonzero scalar, `A` is represented by positive integers `b_1,...,b_r` with total `S<p` whose nonempty subsums fill the complete interval `1,...,S`. Ribas later isolates the same complete-subsum formulation.

In this normalization, the negative subsums occupy `p-S,...,p-1`. Therefore any `x in R(A)` satisfies

`1<=x<=p-S-1<S`.

It is consequently a subsum of `A`; since sums of two or more terms are also forbidden in the definition of `R(A)`, `x` must be a singleton term. Thus

`R(A) subset supp(A)`.

Now `R(A)` contains `d` distinct positive term values and all are at most `p-S-1`, so `S<=p-d-1`. A positive sequence of length `r` containing `d` distinct values has total at least

`r+d(d-1)/2`.

Combining the two inequalities gives

> `d(d+1)/2<=p-1-r`.

Equivalently, the number of maximal-atom scalars surviving on a long projective fiber is at most

`floor((sqrt(1+8(p-1-r))-1)/2)`.

This is the prime-uniform restricted-sumset mechanism. In particular, an almost saturated direction has a vanishing or singleton scalar list rather than a generic `p-1`-element list.

### Donor attribution

- S. Savchev and F. Chen, *Long zero-free sequences in finite cyclic groups*, Discrete Mathematics 307 (2007), 2671--2679, DOI `10.1016/j.disc.2007.01.012`, arXiv `math/0602568`.
- S. Ribas, *The subsums of zero-sum free sequences in finite cyclic groups*, arXiv `1811.03914`.

The donor theorem receives zero ORION novelty credit. The deduction to `R(A)` is the branch-local use.

## 3. Exact `p=7` endpoint

For `p=7`, every line fiber has `1<=r<=6`. The two independent scripts

- `check_corridor_line_fiber_avoidance_v1.py`, using unordered scalar multisets and occurrence-subset masks; and
- `verify_corridor_line_fiber_independent_v1.py`, using multiplicity vectors and bounded-subsum dynamic programming,

enumerate all 96 zero-sumfree scalar multisets. They freeze the same detailed SHA-256 digest

`d8f81eb780c8ecc9671de0f02e13879decf846d0607c5295225f61838895bcf4`.

| line occupancy `r` | zero-sumfree multisets | scale orbits | distribution of `|R(A)|` | maximum |
|---:|---:|---:|---:|---:|
| 1 | 6 | 1 | `5:6` | 5 |
| 2 | 18 | 3 | `2:6, 3:12` | 3 |
| 3 | 30 | 5 | `0:6, 1:24` | 1 |
| 4 | 24 | 4 | `0:12, 1:12` | 1 |
| 5 | 12 | 2 | `0:6, 1:6` | 1 |
| 6 | 6 | 1 | `0:6` | 0 |

For `r=3`, the five scale representatives are

`111`, `112`, `113`, `114`, `123`,

with survivor sets respectively `1`, `1`, `1`, `4`, and empty. For `r>=4`, the prime-uniform long-fiber theorem already implies the maxima `1,1,0`.

Hence, at `p=7`:

- if `3<=r<=5`, the maximal atom can use at most one scalar on this projective direction, and that scalar already occurs in `V`;
- if `r=6`, the maximal atom cannot use this projective direction at all.

## 4. Application to `(8,10,19)`

Let `U` be the 19-atom and `V` the 10-atom. Existing donor subtraction proves that the actual support values of `U` are projectively separated. Existing factorization reasoning also proves that `UV` is 9-short-zero-free.

The support-complement lemma in `SHORTFREE_COMPLEMENT_SUPPORT_BARRIER_V1.md` now gives

`|supp(UV)|>=6`.

For every projective direction with `r=|V cap L|`:

- `r=6`: `U` is disjoint from `L`;
- `3<=r<=5`: any shared direction is necessarily shared at one actual value of `V`, and the total directional capacity gives `v_x(U)<=6-r`;
- `r=1,2`: the exact residual scalar-list sizes are at most 5 and 3.

Thus every heavy line fiber of the 10-atom collapses to a singleton or empty maximal-atom choice.

## 5. Application to `(9,9,19)`

Let `U` be the 19-atom and `V` either 9-atom. The product `UV` is 8-short-zero-free and again satisfies

`|supp(UV)|>=6`.

The identical line-fiber grammar applies. The only change is the off-line complement lower bound: since `r<=6`, `|V|-r>=3`, still safely inside the proper-subsum avoidance range.

## 6. Graver/Hilbert and matching interpretation

After projective normalization, a maximal atom is a positive primitive kernel vector of a `3 x s` matrix over `F_p`. The line-fiber lemma restricts which scalar columns can coexist with the companion atom before any global kernel enumeration begins.

A corridor checker should therefore enumerate in the following order:

1. projective support geometry;
2. companion-atom line fibers and their exact `R(A)` lists;
3. projectively simple maximal-atom columns chosen from those lists;
4. positive full-support kernel vectors;
5. atom minimality / Graver primitiveness;
6. conformal splitting, equivalently a matching of at least three zero-sum hyperedges in `UV`.

This ordering is materially smaller than enumerating two atoms first and only then testing proper-subsum avoidance.

## Retained failure and boundary

- Global cardinality of `Sigma_{2..}(V)` alone is not yet strong enough: its complement can be large and low-rank in different ways. The projective-fiber decomposition is the retained repair.
- Neither corridor is eliminated here.
- The exact `p=7` table grants no all-prime statement at the endpoint `r<=p/2`.
- No novelty or priority claim is made for the cyclic inverse theorem or for the resulting bound.
