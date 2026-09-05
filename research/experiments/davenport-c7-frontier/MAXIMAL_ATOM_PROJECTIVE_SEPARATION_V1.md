# Maximal-atom projective separation and near-`D_2` complements — V1

Status: **analytic structural reduction from donor results**. No corridor elimination claim yet.

Let `G=C_7^3` and suppose `B` is a zero-sum sequence of length 37 with packing number `z(B)<=3`.

## Donor theorem: maximal zero-sumfree sequences are projectively separated

Gao--Geroldinger, *Zero-sum problems and coverings by proper cosets* (European J. Combin. 24 (2003)), Corollary 6.3, proves that if `S` is a maximal-length zero-sumfree sequence in an elementary `p`-group, then every two **distinct support elements** of `S` are linearly independent.

For `C_7^3`, `D(G)=19`, so a maximal zero-sumfree sequence has length 18.

Let `U` be an atom of length 19. For any term `x|U`, the sequence `Ux^{-1}` is zero-sumfree of length 18 and hence maximal. Also `U` cannot be supported in a two-dimensional subgroup, since `D(C_7^2)=13<19`; therefore `supp(U)` contains at least three projective directions.

Given distinct `g,h in supp(U)`, choose `x` from a third support direction. Then `g,h` both remain in `Ux^{-1}`, so Gao--Geroldinger implies that `g` and `h` are linearly independent. Consequently:

> Every two distinct support elements of a length-19 atom in `C_7^3` determine distinct projective points.

This is donor-derived structure, not an ORION novelty claim.

## Stronger short-free conditions in the two length-19 corridors

The two atom triples containing a maximal atom are

- `(8,10,19)`,
- `(9,9,19)`.

Their two-atom complements have lengths 29 and 28 and packing number exactly two.

### Length 29

If a total-zero length-29 sequence `C` with `z(C)=2` had a nonempty zero-sum subsequence `A` with `|A|<=9`, then the zero-sum complement `CA^{-1}` would have length at least 20. Since `D(C_7^3)=19`, that complement contains a nonempty zero-sum subsequence disjoint from `A`. Its remaining complement is also zero-sum and nonempty, yielding three disjoint zero-sums in `C`, contradiction.

Hence every such length-29 complement is **9-short-zero-free**.

### Length 28

The same argument shows that a total-zero length-28 sequence with packing number two is **8-short-zero-free**: removing a zero-sum of length at most eight leaves at least 20 terms, above the classical Davenport threshold.

## Consequence for the residual

The hard corridors can now be restated as inverse problems with two simultaneous structures:

1. the length-19 atom is projectively separated on its support; and
2. the whole two-atom complement is substantially more short-zero-free than the ambient length-37 obstruction.

A complete classification of maximal atoms in rank three is not assumed. The pairwise projective-separation theorem is used only as a verified donor constraint.
