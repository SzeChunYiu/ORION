# X1-C finding — every 12-block C3^3 packing induces a maximal C5^3 zero-sum-free sequence

Parent: #901. Committed before downstream use.

## Setup

Let `U` be any maximal zero-sum-free length-42 sequence in

`K=C_15^3 ≅ C_3^3 ⊕ C_5^3`

that is compatible with the X1-C C45 reduction.

From the committed primary-packing theorem,

`pack_0(pi_3(U))=12`.

Thus at least one, and generally many, choices of 12 pairwise-disjoint nonempty zero-sum blocks exist in the `C_3^3` projection.

Fix **any** such 12-block packing

`B_1,...,B_12`.

Lift the blocks back to U and let their sums in the kernel of `pi_3`, identified with `C_5^3`, be

`h_1,...,h_12 in C_5^3`.

## Zero-sum-freeness of the induced kernel sequence

Let

`H=h_1...h_12`.

If a nonempty subcollection of the h_i summed to zero in `C_5^3`, then the union of the corresponding pairwise-disjoint lifted blocks would sum to zero in both primary projections, hence to zero in `C_15^3`. That would give a nonempty zero-sum subsequence of U, contradicting zero-sum-freeness.

Therefore H is zero-sum-free in `C_5^3`.

## Maximality

The p-group formula gives

`D(C_5^3)=13`,

so

`d(C_5^3)=12`.

Since `|H|=12`, H has maximum possible zero-sum-free length.

Hence:

> **For every admissible 12-block zero-sum packing of pi_3(U), the 12 corresponding lifted block sums form a maximal zero-sum-free sequence in C_5^3.**

This is universal over the choice of packing, not merely existential.

## Consequences available from donor p-group theory

Because `C_5^3` is a p-group, the fresh Geroldinger--Yang result gives the sharp missing-sum invariant

`nu_5(C_5^3)=d(C_5^3)-1=11`.

Accordingly, for every such maximal H and every deletion `H h_i^{-1}`, the nonzero values of `C_5^3` not represented as subsequence sums of the remaining 11 terms lie in a single affine coset of an index-5 subgroup.

This donor consequence may be used in later block-exchange arguments, but no new `nu` claim is made here.

## Why this is stronger than a single selected decomposition

A hypothetical C45 counterexample must survive the maximal-p-group inverse constraints **simultaneously for every 12-block packing** of its C3^3 projection. Any legal exchange between quotient block packings therefore moves between maximal C5^3 zero-sum-free sequences, and the exceptional affine hyperplanes supplied by the donor theorem must remain compatible across the exchange graph.

This creates a concrete compatibility target:

> show that the unique/near-unique C3^3 extremal packing geometry forces two reachable packings whose induced C5^3 missing-sum hyperplane constraints are incompatible.

A proof of that statement would close the corresponding branch; it is not assumed.

## Claim boundary

This is a derived compatibility theorem using previously committed X1-C constraints and donor p-group constants. It does not prove C45, classify the C3^3 packing graph, or establish novelty authority.
