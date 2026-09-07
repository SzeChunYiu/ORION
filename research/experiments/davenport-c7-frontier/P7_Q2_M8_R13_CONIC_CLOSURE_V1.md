# Exact closure of the `p=7, q=2, m=8, r=13` saturated-conic branch — V1

Status: **complete bounded elimination with two structurally independent finite verifiers**. This file proves only the declared first-failure face. It does not determine `D_3(C_7^3)` or eliminate the remaining `q=2,m=8,r>=14` branch.

## 1. The first-failure face

Work in `G=C_7^3`. Suppose a first counterexample to the candidate generalized-Davenport line has

\[
q=2,
\qquad
m=8,
\qquad
N=7m+15+q=73.
\]

By `RANK2_Q_PLANE_CAP_AND_WEIGHTED_ARC_V1.md`, every rank-two subgroup / projective line contains at most

\[
3p-q-2=17
\]

term occurrences, and any line with at least four occupied projective directions has occupancy at most 16. The same file raises the projective-direction floor in this slice to

\[
r\ge13.
\]

This note eliminates the equality case `r=13`.

## 2. Forced weight pattern at r=13

Let the 13 occupied projective directions have occurrence weights

\[
1\le w_i\le6,
\]

and deficits

\[
d_i=6-w_i,
\qquad
\Delta=\sum_i d_i=13\cdot6-73=5.
\]

For `q>=2`, the full-multiplicity directions `d_i=0` form an arc in `PG(2,7)`, hence there are at most `p+1=8` of them.

On the other hand, at most `Delta=5` directions can have positive deficit, so at least `13-5=8` directions are full. Therefore exactly eight directions have weight 6, exactly five directions have positive deficit, and since the five positive deficits sum to five, each of them equals one. Thus the weight pattern is forced:

\[
\boxed{6^8 5^5.}
\]

The eight full directions form an 8-arc. By Segre's odd-order oval theorem, every 8-arc in `PG(2,7)` is a conic. After a projective transformation we may therefore fix the canonical conic

\[
\mathcal C=
\{[1:t:t^2]:t\in\mathbf F_7\}\cup\{[0:0:1]\}.
\]

The five weight-5 directions lie among the 49 off-conic points.

## 3. No four occupied directions are collinear

For `q=2`, a line containing four occupied directions must carry line deficit at least

\[
(p-1)+q=8.
\]

But the total deficit of the entire sequence is only five. Hence no projective line contains four occupied directions.

Thus every candidate direction support is a 13-point `(13,3)`-arc consisting of the fixed conic plus five off-conic points.

The line capacities relative to the fixed conic are exact:

- a conic secant already contains two conic points and may contain at most one chosen off-conic point;
- a conic tangent contains one conic point and may contain at most two chosen off-conic points;
- an external line contains no conic point and may contain at most three chosen off-conic points.

The primary backtracking generator and the independent direct-combination generator both produce exactly

\[
\boxed{5166}
\]

five-point off-conic extensions satisfying all these capacities. Their canonical candidate-list digest is

`0eb3a99b0bb1c30595f9b6b58e74b980c094c5d5754a50f726d82aed4711d82c`.

This count is an exhaustive coordinate cover after the conic normalization; it is not a projective-equivalence class count.

## 4. Every conic secant through a deficient point is saturated

Let `D` be one of the five weight-5 directions. A point outside a conic in `PG(2,7)` lies on either three or four conic secants. If such a secant meets the conic at full directions `P_i,P_j`, then its term occupancy is

\[
6+6+5=17,
\]

which is exactly the q-dependent plane cap.

Hence every such secant is a saturated plane. The rank-two inverse theorem from `RANK2_Q_PLANE_CAP_AND_WEIGHTED_ARC_V1.md` applies to the **entire** sequence lying in that plane and forces the exact actual-element grammar

\[
x_i^6 x_j^6 (x_i+x_j)^5.
\]

In particular:

1. each direction participating in one of these saturated planes is monochromatic at the actual group-element level;
2. if `x_i` and `x_j` are the actual elements on the two full conic directions and `x_D` is the actual element on `D`, then

\[
\boxed{x_D=x_i+x_j.}
\]

Both finite verifiers also check that in every one of the 5166 candidate extensions, the saturated conic secants collectively cover **all eight** conic directions. Thus all thirteen direction fibers are monochromatic and the scalar compatibility equations below are mandatory globally.

## 5. Primary scalar-compatibility system

Choose fixed nonzero vector representatives

\[
C_1,\ldots,C_8
\]

of the conic directions and

\[
D_1,\ldots,D_5
\]

of the five deficient directions.

Write the actual group elements as

\[
x_i=\lambda_i C_i,
\qquad
x_{D_j}=\mu_jD_j,
\]

with all `lambda_i,mu_j in F_7^*`.

For every saturated conic secant through `D_j` with conic endpoints `C_a,C_b`, the inverse grammar gives the three-coordinate linear equation

\[
\lambda_a C_a+\lambda_b C_b-\mu_jD_j=0.
\]

Collect all these equations into a homogeneous matrix over `F_7` with 13 scalar variables

\[
(\lambda_1,\ldots,\lambda_8,\mu_1,\ldots,\mu_5).
\]

`check_p7_q2_m8_r13_conic_closure_v1.py` regenerates all 5166 direction candidates and constructs this matrix independently for each candidate.

> **Primary receipt.** Every one of the 5166 matrices has rank exactly 13 over `F_7`.

Therefore every system has only the zero solution. In particular, no system has the required all-nonzero scalar solution. Hence none of the 5166 direction candidates lifts to a first-failure sequence.

## 6. Independent ratio-cycle verifier

The second verifier does not compute matrix rank.

For a saturated secant through `D_j` and conic endpoints `C_a,C_b`, write uniquely

\[
D_j=\alpha C_a+\beta C_b
\]

for nonzero `alpha,beta in F_7`. The saturation equation is equivalent to the scalar ratio constraint

\[
\frac{\lambda_b}{\lambda_a}=\frac{\beta}{\alpha}.
\]

Thus every selected deficient point contributes three or four labelled edges to a graph on the eight conic scalar variables. A valid lift requires these multiplicative edge ratios to be consistent around every cycle.

`verify_p7_q2_m8_r13_conic_closure_independent_v1.py`

- enumerates all `C(49,5)` five-point subsets directly, filtering them by pair/triple/quadruple collinearity rather than the primary line-capacity backtracking;
- recovers exactly the same 5166 valid direction supports and the same canonical digest;
- derives every secant ratio by direct two-coordinate solving; and
- propagates multiplicative scalar ratios around the conic graph.

> **Independent receipt.** All 5166 candidates contain an inconsistent scalar-ratio cycle. None admits a nonzero conic-scalar assignment.

This independently proves the same impossibility without row reduction.

## 7. The closed slice

Combining the forced weight pattern, conic normalization, exhaustive direction cover, and two scalar incompatibility verifiers gives:

> **Theorem.** A first counterexample over `C_7^3` with `(q,m)=(2,8)` cannot use exactly 13 projective directions.

Therefore

\[
\boxed{(p,q,m)=(7,2,8)\quad\Longrightarrow\quad r\ge14.}
\]

This strictly improves the weighted-arc direction floor `r>=13` in this one first-failure slice.

## 8. Why the argument is reusable

The closure uses a four-stage mechanism that may recur at other boundary slices:

1. a tiny total direction deficit forces an extremal weight pattern;
2. the full-weight directions hit the maximum arc size and normalize to a conic;
3. every secant through a low-deficit point saturates the q-dependent rank-two plane bound, converting projective incidence into exact scalar addition; and
4. the resulting scalar equations become overdetermined globally.

This is stronger than a pure projective-support exclusion: the projective 13-point extensions **do exist**, but none is compatible with the rank-two extremal scalar grammar.

## Boundary

- Only the exact face `p=7,q=2,m=8,r=13` is eliminated.
- The branch `p=7,q=2,m=8,r>=14` remains.
- No value of `D_3(C_7^3)` follows from this bounded closure.
- Rank-two inverse structure and Segre's oval theorem are donor-owned.
