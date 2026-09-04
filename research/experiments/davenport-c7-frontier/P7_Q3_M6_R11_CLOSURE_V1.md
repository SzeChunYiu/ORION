# Exact closure of the `p=7, q=3, m=6, r=11` minimum-direction face — V1

Status: **complete bounded elimination with analytic low-deficit reduction and two structurally independent finite scalar verifiers**. This file proves only the declared first-failure face.

## 1. Arithmetic of the face

Let `G=C_7^3` and suppose a first counterexample has

`q=3`, `m=6`, `N=7*6+15+3=60`,

and exactly `r=11` occupied projective directions.

The total direction deficit is

`Delta=11*6-60=6`.

Let `f` be the number of full weight-6 directions. Since the full directions form an arc and at most six directions can have positive deficit,

`5<=f<=8`.

The low-deficit tangent-packing theorem in `LOW_DEFICIT_TANGENT_PACKING_V1.md` strengthens this immediately to

`f>=7`.

Thus only `f=7` and `f=8` remain.

## 2. The f=7 branch is impossible

There are four deficient directions with positive deficits summing to six. Hence at least two have deficit one.

A deficit-one direction cannot lie on a secant of the seven full directions, because every trisecant requires line deficit at least `q-1=2`. Therefore at least two points would have to be secant-free relative to the full 7-arc.

But a 7-arc in `PG(2,7)` has at most one secant-free extension point:

- if `D` is secant-free, adjoining `D` gives an 8-arc;
- by Segre's odd-order oval theorem, that 8-arc lies on a nondegenerate conic;
- if two distinct secant-free points `D,E` existed, the two resulting conics would each contain the same seven original arc points;
- two distinct conics cannot share seven points, so the conics coincide;
- a conic in `PG(2,7)` has exactly eight points, leaving only one point outside the original 7-arc.

Contradiction. Hence `f=7` is impossible.

The primary checker additionally regenerates every frame-normalized 7-arc and confirms that each has exactly one secant-free point; this is a finite hostile control, not the proof authority.

## 3. The f=8 branch has forced weights 6^8 4^3

Now there are exactly three deficient directions with positive deficits summing to six.

The eight full directions form an 8-arc and hence a conic. Every point outside a conic in `PG(2,7)` lies on three or four conic secants. A deficit-one point is forbidden on every full secant, so none of the three deficient directions can have deficit one. Therefore all three deficits equal two.

Thus the projective weight pattern is forced:

`6^8 4^3`.

After projective normalization, fix the canonical conic

`C={ [1:t:t^2] : t in F_7 } union {[0:0:1]}`.

The three weight-4 directions are off-conic points.

## 4. Projective support cover

For deficit two, every conic secant through a deficient point has line deficit exactly `q-1=2`, hence saturates the rank-two plane cap. Lines with four occupied directions are impossible at this total local deficit. Relative to the fixed conic this gives the same geometric capacities:

- at most one selected off-conic point on a conic secant;
- at most two on a conic tangent;
- at most three on an external line.

The primary recursive-capacity generator and an independent direct `C(49,3)` filter both produce exactly

`4466`

valid three-point off-conic extensions. Canonical candidate-list SHA-256:

`7f858cbd83b9922d4fc0122baa2a34680216033f28bd948aa225bde055c85cce`.

Every candidate's saturated conic secants collectively cover all eight conic directions.

The saturated-secant count distribution is

- 9 secants: 1204 candidates;
- 10 secants: 1848 candidates;
- 11 secants: 1176 candidates;
- 12 secants: 238 candidates.

## 5. Primary scalar compatibility

Let `C_1,...,C_8` be fixed vector representatives of the conic directions and `D_1,D_2,D_3` the selected deficient representatives. Write the actual group elements as

`x_i=lambda_i C_i`, `x_{D_j}=mu_j D_j`,

with all scalars nonzero in `F_7`.

Every saturated secant with conic endpoints `C_a,C_b` and deficient point `D_j` has plane grammar

`x_a^6 x_b^6 (x_a+x_b)^4`,

so it forces

`lambda_a C_a + lambda_b C_b - mu_j D_j = 0`.

The primary checker stacks all three coordinate equations for every saturated secant into a homogeneous matrix with eleven scalar variables

`lambda_1,...,lambda_8,mu_1,mu_2,mu_3`.

> **Primary receipt:** all 4466 matrices have rank exactly 11 over `F_7`.

Hence every system has only the zero solution and no candidate has an all-nonzero scalar lift.

## 6. Independent multiplicative constraint graph

The second verifier never performs row reduction.

For a saturated secant, write uniquely

`D_j=alpha C_a+beta C_b`,

with nonzero `alpha,beta`. The saturation equation is equivalent to the two multiplicative constraints

`lambda_a=alpha mu_j`, `lambda_b=beta mu_j`.

Thus each saturated secant supplies two labelled edges in a bipartite gain graph on eleven scalar variables: eight conic variables and three deficient variables.

The independent verifier:

1. enumerates all `C(49,3)` triples directly and filters projective line violations without using primary backtracking;
2. recovers the same 4466 candidates and digest;
3. constructs the labelled bipartite gain graph by direct two-coordinate solving; and
4. propagates multiplicative values in `F_7^*` around every graph cycle.

For every candidate the graph is connected and contains an inconsistent multiplicative cycle.

> **Independent receipt:** all 4466 candidates are ratio-inconsistent.

This independently proves scalar impossibility.

## 7. Closed face

Both `f=7` and `f=8` are impossible, while tangent packing already excluded `f=5,6`. Therefore:

> **Theorem.** A first counterexample over `C_7^3` with `(q,m)=(3,6)` cannot use exactly eleven projective directions.

Hence

`(p,q,m)=(7,3,6) => r>=12`.

This strictly improves the previous weighted-projective floor `r>=11` in this slice.

## 8. Reusable mechanism

This closure exposes a second boundary pattern complementary to the earlier `q=2,m=8` conic argument:

1. tangent packing converts total deficit into a large full-direction arc;
2. near-maximal arcs severely limit secant-free low-deficit points;
3. maximal full arcs force a conic;
4. conic secants saturate the rank-two inverse bound and become labelled scalar equations;
5. the resulting gain graph is globally unbalanced.

The gain-graph formulation is the natural interface between rank-two inverse zero-sum theory and a future rank-three augmentation theorem.

## Boundary

- Only `p=7,q=3,m=6,r=11` is eliminated.
- The `q=3,m=6,r>=12` branch remains.
- No value of `D_3(C_7^3)` follows from this bounded closure.
- Segre's oval theorem and rank-two inverse structure are donor-owned.
