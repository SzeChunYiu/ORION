# X1-C finding — P5 split route reduces to one correction outside one affine coset

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Parent issue: #901

## Setting

Use the split CRT projection

`C_45^3 ≅ C_5^3 ⊕ C_9^3 -> C_5^3`,

with kernel `K=C_9^3`.

From the donor short-zero-sum bounds over `C_5^3`, the exact extraction recurrence gives

`D_k(C_5^3) <= 5k+18` for all `k>=3`,

hence a length-133 source sequence admits at least 23 pairwise-disjoint quotient-zero-sum blocks.

Let their lifted block sums be

`T=t_1...t_23 in K=C_9^3`.

If the source sequence is zero-sum-free, T is zero-sum-free.

For K, `d(K)=24`. Geroldinger--Yang prove for p-groups

`nu_3(K)=d(K)-1=23`.

Therefore the set of nonzero kernel elements not representable as a nonempty subsequence sum of T is contained in one affine coset `A` of an index-3 subgroup of K.

## One-correction lemma

Suppose there exists **one additional** quotient-zero-sum block `C`, disjoint from the 23 selected blocks, whose lifted kernel sum is `c in K`, and suppose

`-c notin A`.

Because `-c` is not in the exceptional missing-sum coset, it is represented by a nonempty subcollection of T:

`sum_{i in I} t_i = -c`

for some nonempty `I subseteq {1,...,23}`.

The union of C with the corresponding selected quotient blocks is zero in the `C_5^3` quotient and has kernel sum

`c + sum_{i in I} t_i = 0`.

Hence it is a nonempty zero-sum subsequence of the original source sequence, contradiction.

Thus, after the 23-block packing and sharp p-group `nu_3` theorem are admitted, the nominal ordinary-Davenport deficit of two blocks (`23` available versus `D(C_9^3)=25`) becomes a **single additional correction-block problem**.

## More general exchange version

A fresh disjoint block is sufficient but not necessary. The same argument applies to any legal exchange that produces a new quotient-zero-sum block C disjoint from whichever subset of the original 23 blocks is retained to represent `-c`, provided the exchange is checked on original indices and does not reuse elements.

The core obstruction is exact:

> every attainable legal correction sum c must have `-c` trapped inside the single exceptional affine coset A associated with the retained 23-term kernel sequence.

## Research target

The P5 route should therefore search for a theorem of the form:

> Every hypothetical length-133 zero-sum-free sequence over `C_45^3` admits a 23-block `C_5^3` quotient packing and one legal additional/exchanged quotient-zero-sum block whose kernel correction escapes the exceptional affine index-3 coset of the packing's lift sums.

A proof closes the C45 target. A counterexample must serialize the exact quotient/lift structure forcing all legal corrections into A.

## Claim boundary

This is a direct consequence of the donor p-group `nu_3` theorem plus split-block bookkeeping. It is a programme reduction, not a novelty claim. Any novelty must lie in the all-sequence exchange-escape theorem or an obstruction theorem discovered from its failure.
