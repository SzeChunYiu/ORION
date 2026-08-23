# X1-B k=4 — prospective exact minimal-forbidden classification for the rank-2 radical family

Parent: #900.
Normalization: `X1B_K4_RANK2_RADICAL_NORMALIZATION_2026-08-22.md`.

## Evidence status

**PROSPECTIVE FROZEN DISCRIMINATOR.** No complete normalized forbidden-signature census or inclusion-minimal result described below has been computed before this packet is committed.

## Exact forbidden signature

For one normalized radical assignment r and one of the two surviving quotient orbits, construct every disjoint pair `(Z,W)` of nonempty quotient-zero-sum position subsets.

Using the fixed rank-2 base coordinates and radical coordinates r, form the full kernel block sums `z_Z,z_W in F_5^3`.

The ten-block prefix must avoid

- zero;
- `-z_Z`;
- `-z_W`;
- `-(z_Z+z_W)`

for every disjoint pair.

All such forbidden points project to the same seven fixed base values. Encode the exact set as a 35-bit signature (seven base fibers times five radical values).

## Complete normalized enumeration

For each quotient orbit separately:

1. enumerate exactly the `12,207,032` shear/scaling-normalized radical assignments;
2. construct the exact forbidden signature;
3. deduplicate equal signatures;
4. record signature-size distribution and a representative radical assignment for every distinct signature.

No random sampling or post-outcome symmetry reduction is allowed.

## Inclusion-minimal reduction

For forbidden signatures A and B, if `A subseteq B`, then any prefix avoiding B also avoids A. Therefore:

> if the ten-prefix problem is NO for A, it is automatically NO for every B containing A.

After the complete census, retain exactly the signatures minimal under set inclusion.

Only those inclusion-minimal signatures require independent ten-prefix existence tests to close the entire radical family.

## Required outputs

Per quotient orbit:

- normalized assignments processed;
- number of distinct forbidden signatures;
- forbidden-set cardinality histogram;
- number of inclusion-minimal signatures;
- serialized minimal signatures and representative normalized radical assignments;
- digest of the complete deduplicated signature set.

## Interpretation

- If every inclusion-minimal signature is already a `GL(3,5)` image of a previously closed forbidden class, the radical family closes by donor/previous-result absorption.
- Otherwise freeze exact ten-prefix searches for the genuinely new minima.
- A length-10 witness for any minimum is an obstruction, not a C15 counterexample; it restores original-index realization.

## Authority boundary

This finite classification cannot by itself prove `D(C_15^3)=43`; it is a complete reduction of the last rank-2 radical branch.