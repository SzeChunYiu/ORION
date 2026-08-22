# X1-B k=4 / 13-point residual — anchored local-scalarization protocol

Parent: reopened #900.
Prerequisites: committed residual reduction `414659ff...`; committed p-group local scalarization `b57b9209...`.

## Evidence status

**PROSPECTIVE FROZEN FINITE THEOREM TEST.** No outcome of the enumeration described below has been inspected before this packet is committed.

A positive finite result may close the k=4 quotient residual when composed with the already committed local-scalarization theorem, but it does not by itself prove `D(C_15^3)=43`; the k=3 residual must be independently discharged as well.

## Exact residual class

Let `A` be a 13-position multiset over `F_3^3` arising in the surviving k=4 branch after ten disjoint quotient zero-sum triples have been removed from a hypothetical 43-term zero-sum-free sequence over `C_15^3`.

The finite verifier admits exactly the following quotient-side conditions:

1. `A` contains no nonempty zero-sum subset of size at most 3;
2. `A` has no three pairwise-disjoint nonempty zero-sum subsets;
3. `A` has at least two pairwise-disjoint nonempty zero-sum subsets.

Condition 3 is donor-guaranteed in the k=4 reduction, but the verifier checks it explicitly rather than assuming it.

Because of condition 1, zero is absent, opposite pairs are absent, and every element has multiplicity at most 2. Hence any admitted 13-position multiset necessarily has support size 7 or 8; this may be used only as a derived enumeration bound.

## Anchored scalarization test

For every admitted `A`, enumerate every nonempty zero-sum position subset `Z` such that there exists another nonempty zero-sum subset `W` disjoint from `Z`.

Interpret `Z` as the residual block held fixed together with the ten already-removed quotient blocks. Then `W` is the twelfth block in a maximal 12-block quotient packing.

By the committed p-group local-scalarization theorem, fixing those eleven blocks yields a nonzero linear functional on the kernel `C_5^3` under which the lifted sum of **every legal replacement** of `W` has one common nonzero scalar value. Every quotient zero-sum subset `C` contained in the complement `A \ Z` is such a legal replacement.

Therefore a hypothetical C15 counterexample requires a position-labelled function

`f : A \ Z -> F_5`

satisfying

`sum_{a in C} f(a) = 1`

for **every** nonempty zero-sum subset `C <= A \ Z`, after rescaling the nonzero common value to 1.

Call `Z` a **closing anchor** when this affine system is inconsistent over `F_5`.

## Frozen finite theorem target

> Every admitted 13-position multiset `A` has at least one closing anchor `Z`.

If true, choose the disjoint partner `W` witnessing that `Z` belongs to a 2-block packing. The local-scalarization theorem supplies the forbidden affine system on `A \ Z`; inconsistency contradicts the hypothetical C15 lift. Thus the k=4 residual is closed.

## Counterexample terminal

If some admitted `A` has **no** closing anchor, serialize the full canonical multiset and, for every pair-compatible anchor `Z`:

- the anchor mask and size;
- at least one disjoint zero-sum partner `W`;
- the complete zero-sum family of `A \ Z`;
- a witness solution `f` to the common-RHS system.

Such an `A` is an exact obstruction to the frozen one-functional anchor strategy. It does not imply a C15 counterexample; it identifies the next missing coupling/state coordinate.

## Enumeration and independence discipline

Use primitive `F_3^3` addition on positions. Symmetry reduction may quotient by the full `GL(3,3)` action, but every final orbit must be replayed from its explicit 13-position multiplicity vector.

Required result coordinates:

- raw candidate count after no-short-zero-sum generation;
- canonical GL orbit count;
- number with packing number exactly 2;
- support-size histogram;
- distribution of numbers of pair-compatible anchors;
- distribution of closing-anchor counts;
- count of admitted orbits with zero closing anchors;
- digest of all admitted canonical encodings;
- full serialization of every zero-closing-anchor obstruction.

## Authority boundary

- `zero_closing_anchor_orbit_count == 0` licenses only `K4_FINITE_QUOTIENT_RESIDUAL_CLOSED_GIVEN_LOCAL_SCALARIZATION`.
- It grants no k=3 closure, C15 theorem authority, infinite-family authority, or novelty authority by itself.
- Solver/resource exhaustion is `CANNOT_CHECK_RESOURCE_BOUND`, never negative evidence.
