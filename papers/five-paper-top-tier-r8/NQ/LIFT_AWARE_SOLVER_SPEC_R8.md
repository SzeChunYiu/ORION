# Lift-Aware 27-Diagonal Solver Specification R8

## Scientific target

The first target is the full source-level branch

`S=e_1^4 e_2^4 X`

in `C_5^3`, where `X` consists of 23 distinct singleton points. The repeated stratum is the unique `4,4` rank-two orbit on `s+c_4=27`. The second target is the five registered `4,2,2` orbits. This specification does not assume either satisfiability or unsatisfiability.

## Why compressed search is insufficient

The quotient-atom theorem and weighted short-free contract are exact necessary conditions, but the R6 weighted countermodel passes those conditions without a proved lift to 23 distinct source singletons. Therefore the solver must retain source identities and check cross-block sums before any negative conclusion.

## Exact variables

Represent `C_5^3` by integers `0..124` with primitive coordinatewise addition mod 5. Fix repeated points `a=(1,0,0)`, `b=(0,1,0)`. For every other point `v`, use Boolean `x_v` indicating singleton selection.

For the `4,4` target:

- `sum_v x_v=23`;
- selected points are automatically distinct;
- `a,b` are excluded from the singleton pool;
- total sum is `4a+4b+sum_v x_v v=0`;
- at least one selected point lies outside `span(a,b)`.

## Short-zero-sum constraints

Precompute every source submultiset type of total length 1 through 5 using:

- 0..4 copies of `a`;
- 0..4 copies of `b`; and
- a subset of distinct candidate singleton points.

Whenever the type sums to zero, forbid simultaneous selection of its singleton members unless the type exceeds available repeated multiplicities. This is a complete source-level short-free encoding.

Two independent generators must agree on the forbidden-hyperedge digest:

1. recursive bounded-multiplicity enumeration;
2. length-indexed dynamic generation with canonical singleton ordering.

## Saturation defects

For every selected singleton `x`, require at least one selected/source-available subsequence `R` such that:

- `|R|<=3`;
- `x` is not used;
- `sigma(R)=-2x`.

For every selected double point in the later `4,2,2` targets, require a certificate of length at most two with sum `-3x`. Certificate choices must be source-valid and may use repeated occurrences within their available multiplicities.

## Factorization constraint

A candidate is an obstruction only if it has no five pairwise disjoint nonempty zero-sum submultisets. Implement an exact adversary whose state tracks five labeled partial sums and nonemptiness, quotienting only by proved bin permutation symmetry. The adversary must produce either:

- an explicit five-factor witness, causing candidate rejection; or
- an independently replayable certificate that no five-factorization exists.

For a complete UNSAT result, every master candidate must be rejected by a primitive short-sum, saturation, rank, total-sum, or five-factor witness, with digest-addressed rejection records.

## Symmetry and completeness

Use the full stabilizer of the repeated multiset, not an informal basis normalization. The canonicalizer must:

1. enumerate or generate the stabilizer exactly;
2. map every admitted candidate within the fixed target stratum;
3. choose one lexicographic representative; and
4. pass orbit-size and random round-trip controls.

If the first outside singleton is normalized to `e_3`, prove transitivity of the relevant stabilizer action and retain any residual stabilizer in later canonicalization.

## Partitioning

A distributed search partitions canonical prefixes by immutable prefix ids. A manifest records each interval/prefix, expected count, job id, result digest, and terminal. A final checker proves exact, disjoint union of the frozen prefix space.

## Required outputs

- source and build environment;
- forbidden-short-sum digest from both generators;
- stabilizer and canonicalization tests;
- per-partition manifests;
- every survivor or rejection certificate;
- independent replay results;
- exact resource accounting; and
- one machine-readable terminal from the execution packet.

## Claim boundary

Closing these six rank-two orbits advances the length-31 obstruction analysis but does not determine `D_4(C_5^3)` unless every other stratum is closed. A survivor must additionally be checked against the exact extremal/factorization implication used to connect the sequence to `D_4=31`.
