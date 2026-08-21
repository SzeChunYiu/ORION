# MAX-R6L three-TARE2 shared-Tag / Restore-factor donor protocol

Date: 2026-08-21
Parent programme: #679 / PR #689
Status: FROZEN BEFORE R6L OUTCOME.
Authority: donor-absorption development only; not R6 and no novelty authority.

## Purpose and donor ownership

The frozen six-term discriminator has so far been represented as two TARE-3 blocks. R5H already absorbs TARE-M2 and arbitrary direct anticommuting clique blocks as donor capability. R6L therefore gives the donor the strongest natural six-term M2 composition before any original mixed-cardinality claim:

> partition the six terms into three TARE-M2 blocks, share one complete one-bit Tag across all three blocks, and factor exact common Pauli components from the three branch-specific Restore operations.

TARE-M2, common-subcircuit factoring, and branchwise Pauli factoring are donor-owned; R6L receives zero novelty credit.

## Frozen subjects and batch

Use only already-open H4 and equilibrium-N2 evidence. Reconstruct exactly the R6B six-term batch. The protected stretched-N2 discriminator remains unread.

Enumerate **all 15 unordered perfect matchings** of the six source terms into three two-term blocks. Canonicalize a matching by sorting each pair, sorting the three pairs lexicographically, and retaining each matching once. No pair or term substitution is permitted after outcome.

All six frozen terms commute on both subjects, so no pair in this batch qualifies for the already-absorbed direct-anticommuting-clique route. This fact is verified, not assumed.

## Frozen weight-one TARE-M2 representation grammar

For each two-term block:

1. choose a system qubit q;
2. choose any ordered pair of two distinct Paulis from `{X_q,Y_q,Z_q}`; these are weight-one and anticommute;
3. choose the one-bit branch labels `(0,1)` or `(1,0)`;
4. solve the minimum-weight Tag Pauli `S` satisfying `<S,R_k>=label_k` exactly;
5. enumerate both target permutations;
6. derive both Restore Paulis and exact Hermitian multiplication phases.

The one-bit Tag key is `K=(S,labels)`. Three pair representations may share a Tag iff all three have exactly the same K. Frames, target permutations, Restore Paulis and Restore phases remain pair-specific.

Weight-one frames have zero Uanti parity-support charge under the same frozen structural-support objective used in the R6 exact-TARE lane. Each M2 block retains the frozen Uanti rotation count `2m-1 = 3`; the three-block batch therefore has exactly 9 Uanti arbitrary rotations, versus 10 for two M3 blocks. Rotation count is recorded as a non-compensatory coordinate and is not folded into the structural support scalar.

## Three-way Restore factoring

For each branch k in {0,1}, let the three signed Hermitian Restore Paulis be `T_1k,T_2k,T_3k` with exact phases.

Factor the exact support-minimizing common Hermitian Pauli `G_k` across **all three** outer-selected blocks. Per system qubit:

- if all three local Restore letters are the same non-identity Pauli, place that letter in `G_k` and identity in all three residuals; local support falls from 3 to 1, saving 2;
- otherwise place identity in `G_k` and retain the original three local letters in the residuals.

This all-three factor requires no additional outer-block predicate. Subset-only common factors are excluded from R6L because they would require an additional selector predicate/resource coordinate and need a separate protocol.

For every branch reconstruct residual Hermitian Paulis and exact phases so common factor times each residual equals the original signed Restore operation.

## R6L objective

For one compatible triple of M2 representations,

`C_R6L = 2 w(S) + sum_{k=0}^1 [ w(G_k) + sum_{j=1}^3 w(U_jk) ]`.

The common Tag/Tag-dagger pair is paid once. Uanti parity support is zero for the frozen weight-one frames. Keep the exact minimum over every compatible representation triple for each of the 15 pair matchings.

The normalization coordinate is

`Lambda_R6L = sum_{pairs (i,j)} sqrt(2) * sqrt(a_i^2+a_j^2)`.

No coefficient or sign may be changed.

## Strongest incumbent envelope

Recompute and absorb the full known six-term donor stack:

- R6B full transformation reuse;
- independent `B_FRAME_ONLY_STRONG` two-M3 implementation;
- R6H common-Tag weight-one M3 donor;
- R6J common-Tag plus branchwise Restore-factor M3 donor.

At each R6L Lambda compare against the minimum incumbent cost among all known points with `Lambda <= Lambda_R6L + 1e-12`.

The non-compensatory Uanti rotation count must also be no worse than the compared incumbent point. R6L has 9 rotations; the two-M3 incumbent has 10. Ancilla/control-width coordinates are recorded separately and must be instantiated before any R6 promotion.

Concurrent pre-outcome R6F/R6G/R6K lanes remain live counterfactuals. Any stronger positive must be absorbed before prospective promotion.

## Hostile and proof gates

R6L must pass:

1. exactly 15 perfect matchings of six terms;
2. all six chemistry terms pairwise commute on both open subjects, so direct-pair substitution is unavailable;
3. complete ordered weight-one M2 frame grammar;
4. one-bit Tag labels are exactly distinct and reproduced by S;
5. exact target/Restore Hermitian-Pauli identity and phase;
6. a synthetic three-block common-Tag case with different Restore strings is accepted;
7. a synthetic local Restore triple with identical non-identity letters saves exactly two support units;
8. a mixed-letter triple gives no false saving;
9. all three blocks are disjoint and conserve all six source terms/coefficients;
10. cost and `Lambda_R6L` recompute from the serialized witness;
11. the full R6J/R6H/R6B/frame-only incumbent replay passes;
12. Uanti rotation count is exactly 9 and no worse than the compared two-M3 incumbent's 10;
13. observed source blobs equal frozen identities;
14. stretched-N2 remains unread.

## Development sign

A strict point requires both:

- `C_R6L < C_incumbent_envelope` at matched-or-better Lambda;
- Uanti rotation count is no worse than the incumbent.

`MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_POSITIVE__ABSORB__NOT_R6` requires at least one strict point on both H4 and equilibrium N2 plus every integrity gate.

A one-subject positive is retained only as a matched counterfactual. A negative closes this donor mixed-cardinality composition and returns the residual to original method-language search.

## Authority ceiling

R6L can never set `r6_earned=true`. Any positive is donor capability, immediately absorbed with zero novelty credit. An original successor must beat the strengthened R6L envelope and all concurrent stronger donors, then pass circuit/non-compensatory instantiation, current literature/donor replay, final novelty subtraction, and a separately frozen protected-subject prospective primary plus independent replay.
