# X1-B k=4 — prospective global bilinear min-rank discriminator

Parent: #900.
Prerequisite theorem: `X1B_C5CUBED_GLOBAL_TWO_EXTENSION_FORM_2026-08-22.md`.
Input obstruction set: the six canonical k=4 quotient orbits committed in `X1B_K4_13PT_ANCHORED_SCALAR_FIRST_RESULT_2026-08-22.md`.

## Evidence status

**PROSPECTIVE FROZEN DISCRIMINATOR.** No min-rank outcome described below has been computed or inspected before this packet is committed.

## Necessary condition to test

For one of the six 13-position quotient obstruction multisets A, let `E(A)` be the set of ordered/unordered pairs `(Z,W)` of disjoint nonempty quotient-zero-sum position subsets.

The committed global two-extension theorem shows that any actual C15 counterexample projecting to A must admit residual kernel vectors `y_j in F_5^3` and one symmetric bilinear form M such that

`(sum_{j in Z} y_j)^T M (sum_{k in W} y_k)=1`

for every `(Z,W) in E(A)`.

Define the symmetric position matrix

`B[j,k]=y_j^T M y_k`.

Then B is symmetric, has rank at most 3, and satisfies the affine linear edge equations

`sum_{j in Z, k in W} B[j,k]=1`.

Conversely, over the odd field `F_5`, every symmetric B of rank at most 3 has a congruence factorization through a symmetric bilinear form on a space of dimension at most 3. Thus the relaxed finite problem is exactly:

> Does there exist a symmetric `13x13` matrix B over `F_5`, rank(B)<=3, satisfying every edge equation of A?

No catalecticant realizability or individual C15-term condition is imposed at this stage.

## Frozen algorithm

For each of the six canonical orbits:

1. reconstruct the explicit 13 positions from the committed multiplicity vector;
2. enumerate every nonempty zero-sum position mask by primitive addition in `F_3^3`;
3. enumerate every unordered disjoint pair of zero-sum masks;
4. create 91 variables for the upper-triangular entries of a symmetric `13x13` matrix B over `F_5`;
5. build the affine linear system from all edge equations and row-reduce it over `F_5`;
6. record consistency, affine dimension, a canonical particular solution, and a canonical nullspace basis;
7. determine the minimum rank in that affine space.

### Rank determination hierarchy

Use the cheapest exact route that closes each orbit:

- if the affine system itself is inconsistent: terminal rank `INF`;
- if its solution is unique: compute rank directly;
- if affine dimension is small enough for exhaustive coefficient enumeration within the frozen resource cap, enumerate the full affine space;
- otherwise solve the polynomial condition `all 4x4 minors = 0` over the affine parameterization using an exact finite-field solver / Gröbner basis / exhaustive branch-and-bound with independently replayable witness or UNSAT certificate.

Do not replace an exhausted exact search by heuristic rank minimization.

## Frozen resource cap

- exhaustive affine enumeration: at most `5^10` parameter assignments per orbit;
- otherwise exact algebraic solver wall-clock cap: 30 minutes per orbit in the authoritative harness environment;
- cap exhaustion => `CANNOT_CHECK_RESOURCE_BOUND`.

A cheap preliminary computation may report dimensions and choose the exact route, but may not alter the rank<=3 success criterion.

## Required outputs

For every orbit:

- canonical orbit code;
- zero-sum mask count;
- disjoint-pair edge count;
- linear equation rank;
- affine solution-space dimension;
- minimum symmetric rank if exactly determined;
- whether rank<=3 is feasible;
- if feasible: full symmetric B witness, primitive edge-equation replay, rank certificate/factorization;
- if infeasible: exact method/certificate proving no rank<=3 solution.

Aggregate:

- number of the six orbits eliminated by the relaxed bilinear condition;
- number surviving with rank<=3 witnesses;
- digest of serialized orbit outcomes.

## Scientific terminals

- `ALL_SIX_BILINEAR_MINRANK_INFEASIBLE`: the k=4 residual is closed, because the tested system was only a necessary relaxation of a true C15 lift.
- `SOME_ORBITS_ELIMINATED`: retain only exact survivors and reframe there.
- `ALL_OR_SOME_SURVIVE`: serialize witnesses and restore the next omitted condition, beginning with ten-factor catalecticant realizability.
- `CANNOT_CHECK_RESOURCE_BOUND`: no scientific inference on unresolved orbits.

## Authority boundary

A rank<=3 witness is not a C15 counterexample. It witnesses only the relaxed global bilinear block-packing model. An infeasibility proof, however, genuinely eliminates that quotient orbit from any C15 counterexample because the bilinear equations are necessary consequences of the admitted group-algebra theorem.
