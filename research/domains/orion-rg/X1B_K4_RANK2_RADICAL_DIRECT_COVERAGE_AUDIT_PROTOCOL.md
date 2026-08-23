# X1-B k=4 — hostile direct-coverage audit for the complete rank-2 radical family

Parent: #900.
Audit branch: `shadow/orion-rg-c15-hostile-audit`.

## Evidence status

**PROSPECTIVE HOSTILE AUDIT.** This audit is deliberately independent of the committed pipeline

`24.4M assignments -> 8,984 signatures -> 639 inclusion-minimal signatures -> two new classes`.

No result from the direct coverage computation described below has been inspected before this protocol is committed.

## Goal

Independently verify the only load-bearing conclusion needed from the earlier radical census:

> every normalized rank-2 radical realization has a forbidden prefix set containing a linear image of a forbidden pattern whose length-10 prefix problem has already been independently proved NO.

If this statement holds directly for all normalized assignments, the earlier signature/minimal-set classification is no longer a single implementation point of failure in the k=4 proof.

## Frozen normalized universe

Use the separately proved shear/scaling normalization:

- residual radical coordinates satisfy `r_0=r_1=0`;
- either `r_2=...=r_12=0`, or the first nonzero coordinate among `r_2,...,r_12` is 1.

This gives exactly

`12,207,032`

representatives for each of the two surviving quotient orbits, hence

`24,414,064`

normalized assignments total.

The fixed rank-2 base coordinates of the 13 residual positions are

```text
position 0:       (2,0)
positions 1..4:   (0,4)
positions 5..8:   (4,4)
positions 9..12:  (1,0)
```

and the full kernel coordinate is `(base_j,r_j) in F_5^3`.

## Primitive forbidden-set construction

For each of the two surviving quotient orbit specifications (`942777` and `1470123`):

1. expand its exact 13 quotient positions in `F_3^3`;
2. enumerate every nonempty quotient-zero-sum position mask by primitive mod-3 addition;
3. enumerate every unordered disjoint pair `(Z,W)` of such masks;
4. for each normalized radical assignment, sum the fixed base coordinates and radical coordinates over Z and W to obtain `z_Z,z_W in F_5^3`;
5. form the exact forbidden prefix set

   `F_r = {0} union {-z_Z,-z_W,-(z_Z+z_W) : Z cap W = empty}`.

No previously serialized forbidden signatures are read.

## Closed pattern library

Use only forbidden patterns whose ten-prefix NO has an independent exact replay:

1. the seven-point planar obstruction `S_bad`;
2. R3-10;
3. R3-11;
4. R3-12;
5. R2R-11;
6. R2R-12.

For each pattern P, independently enumerate all invertible linear maps in `GL(3,5)` and retain every distinct image `M(P)` lying inside the 35-point union of the seven possible base fibers of a rank-2 radical forbidden set.

This precomputation is performed from the canonical pattern point sets, not from the earlier radical-census output.

## Direct coverage test

For a freshly constructed forbidden set `F_r`, declare it covered iff there exists one precomputed image Q of one closed pattern with

`Q subseteq F_r`.

This uses only monotonicity of the prefix problem: a prefix avoiding `F_r` would also avoid Q, contradicting the independently proved NO for Q.

A cache keyed by the freshly constructed 35-bit forbidden set is permitted solely to avoid repeating the same direct containment scan. The audit may record how many distinct sets were encountered, but it must not compute inclusion-minimal signatures or rely on the earlier 8,984/639 classification.

## Required outputs

Per quotient orbit and aggregate:

- exact normalized assignments processed;
- number of distinct freshly encountered forbidden sets (diagnostic only);
- number directly covered by each first matching closed-pattern family;
- number of uncovered assignments;
- number of uncovered distinct forbidden sets;
- explicit first uncovered assignment/set if any;
- digest of the sorted freshly encountered forbidden sets, for comparison only after the result is frozen.

## Strong terminal

`DIRECT_COVERAGE_ALL_24414064`: every normalized radical realization is independently eliminated without using inclusion-minimal classification.

Any uncovered assignment is a mandatory counterexample to the prior radical-census reduction and reopens k=4 immediately.

## Authority boundary

A successful audit removes a software-single-point risk from the candidate C15 proof. It does not by itself grant theorem, novelty, publication, or infinite-family authority.