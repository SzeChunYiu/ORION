# X1-C finding — primary projection packing constraints for maximal C15^3 kernel sequences

Parent: #901. Committed before downstream use.

## Setup

Let

`K = C_15^3 ≅ C_3^3 ⊕ C_5^3`

and let `U` be a maximal zero-sum-free sequence over K of length

`|U| = d(K) = 42`,

as forced by the previously committed X1-C maximal-kernel completion reduction for any hypothetical length-133 zero-sum-free sequence over `C_45^3`.

Write

- `pi_3 : K -> C_3^3`, with kernel `C_5^3`;
- `pi_5 : K -> C_5^3`, with kernel `C_3^3`.

For a projected sequence, let `pack_0` denote the maximum number of pairwise disjoint nonempty zero-sum subsequences.

## The C3^3 projection has packing number exactly 12

Freeze--Schmid/Bhowmik--Schlage-Puchta give

`D_12(C_3^3)=42`.

Therefore every length-42 sequence over `C_3^3`, including `pi_3(U)`, contains at least 12 pairwise disjoint nonempty zero-sum subsequences:

`pack_0(pi_3(U)) >= 12`.

Now suppose `pi_3(U)` contained 13 pairwise disjoint zero-sum blocks. Lift those 13 blocks back to U. Each lifted block sum lies in the kernel `C_5^3`, giving a sequence of 13 elements of `C_5^3`.

Since

`D(C_5^3)=13`,

some nonempty subcollection of those 13 kernel block sums sums to zero. The union of the corresponding pairwise-disjoint lifted blocks would then be a nonempty zero-sum subsequence of U, contradicting that U is zero-sum-free.

Hence

`pack_0(pi_3(U)) <= 12`.

Combining both inequalities,

`pack_0(pi_3(U)) = 12`.

## The C5^3 projection has packing number at most 6

Suppose `pi_5(U)` contained 7 pairwise disjoint zero-sum blocks. Their lifted sums lie in the kernel `C_3^3`, giving 7 elements of `C_3^3`.

Since

`D(C_3^3)=7`,

some nonempty subcollection of those 7 kernel block sums sums to zero. The corresponding union of lifted blocks would be a nonempty zero-sum subsequence of U, contradiction.

Therefore

`pack_0(pi_5(U)) <= 6`.

No lower bound of 6 is claimed here. Current donor bounds inspected so far do not justify one from length 42 alone.

## Structural signature forced on every hypothetical C45 counterexample

Any maximal kernel sequence U arising from the X1-C reduction must therefore satisfy the exact/one-sided primary packing signature

`(pack_0(pi_3(U)), pack_0(pi_5(U))) = (12, <=6)`.

This is a compatibility constraint between the two primary projections of a maximal zero-sum-free sequence in the mixed rank-3 group `C_15^3`.

It is stronger than treating U as an arbitrary maximal zero-sum-free sequence and can be used as a hostile discriminator in inverse-structure searches.

## Immediate research questions

1. Does every maximal zero-sum-free sequence of C15^3 automatically satisfy the stronger equality `pack_0(pi_5(U))=6`, or can the second coordinate be <6?
2. Are maximal C15^3 sequences with the forced first coordinate `pack_0(pi_3(U))=12` already classified or constrained by existing inverse Davenport theory?
3. Does the pair of primary packing constraints force order/multiplicity/support restrictions that conflict with the quotient-block realization coming from C45?
4. Can the reverse inductive projection be sharpened through a direct bound on `D_7(C_15^3)`?

## Claim boundary

This file proves only the projection packing constraints from admitted donor constants. It does not classify maximal C15^3 zero-sum-free sequences, prove `D(C_45^3)=133`, or establish novelty.
