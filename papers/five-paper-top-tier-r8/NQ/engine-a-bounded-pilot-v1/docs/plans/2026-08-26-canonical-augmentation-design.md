# Lossless Canonical-Augmentation Design

## Authority boundary

This is engineering-only work under `ENGINE_B_EXPOSURE_IN_PRIOR_CONTEXT__CANNOT_CHECK` and
`EXPECTED_OUTCOME_EXPOSURE`. It does not consume frozen full counts as tests or acceptance
criteria, launch a census, restore independence, or change paper authority.

## Alternatives considered

1. **Continue raw multiset generation.** Formally simple but its raw domain grows as
   `binomial(|G|+n-1,n)` and is unusable at the target scale.
2. **Enumerate all of GL for every parent.** Exact, but `|GL(3,5)|` makes repeated stabilizer
   scans wasteful.
3. **Canonical construction path with support-basis stabilizers (selected).** Extend one
   canonical representative per class by one representative from each stabilizer orbit on
   group elements. Retain only children whose invariant canonical deletion returns that parent,
   then deduplicate canonical children.

## Canonical parent

For a nonempty multiset `S`, first compute its local GL canonical form `C(S)`. Delete one
occurrence of the lexicographically largest element and canonicalize again:

`P(S) = C(C(S) minus max(C(S)))`.

`P` depends only on the GL orbit. Every child orbit therefore has one invariant parent orbit.

## Stabilizer orbit grammar

For a canonical parent spanning the first `r` coordinate axes, compute its intrinsic
stabilizer on the span. A stabilizer map is determined by the image of one reference support
basis. Enumerate ordered independent support bases, construct the induced linear maps, and
retain exactly those preserving the parent multiset. Their orbits partition elements inside
the span. If `r<d`, all elements outside the span form one additional orbit: the subgroup
fixing the span pointwise has arbitrary quotient GL action and arbitrary complement-to-span
shear, hence is transitive on the outside.

Generate `C(parent plus x)` for the minimum `x` in every extension orbit. Accept its class only
when `P(child)=parent`. Canonical-child set insertion collapses the rare case in which distinct
canonical augmentation edges reach the same child class. Output levels are therefore unique.

## Lossless pruning

Only hereditary predicates may prune:

- absence of a nonempty zero sum of length at most a declared cutoff;
- absence of `k` pairwise-disjoint nonempty zero sums.

Both are inherited by submultisets. The short predicate uses exact weight-indexed subset-sum
DP. The factor predicate uses the existing exact multi-bin DP. A state/resource limit produces
`CANNOT_CHECK_RESOURCE_BOUND`; a partial level is never returned as complete. Rank and donor
normalization are not used as prefix prunes.

## Verification design

- brute-force small GL stabilizer orbits versus the support-basis stabilizer grammar;
- every emitted record canonical, unique, and with the correct canonical parent;
- exhaustive equality with raw canonical filtering on C2, C3, C2-squared, C3-squared, and
  bounded C5-cubed panels;
- exact equality after short-zero-sum and no-k-factor filters;
- hostile noncanonical parents, malformed profiles, forged coverage, and resource truncation;
- no published full count appears in targets, stopping conditions, or tuning.
