# X1-C finding — every hypothetical C45 counterexample induces a maximal zero-sum-free kernel sequence

Parent: #901. Committed before downstream use.

## Setup

Assume for contradiction that `S` is zero-sum-free over `C_45^3` with `|S|=133`.
Project to `C_3^3` with kernel `K=C_15^3`.

Greedy removal of quotient zero-sum triples leaves a residual of size `3k+1` with `k<=5`. The earlier committed reduction shows `k>=3` (the k=2 case is impossible), so `k in {3,4,5}`.

The number of removed quotient triples is

`44-k`.

Their lifted sums form a zero-sum-free sequence `H` in K of length

`|H|=44-k = 42-(k-2)`.

## Donor residual fact

The Bhowmik--Schlage-Puchta proof of the `Z3⊕Z3⊕Z3d` theorem records that, for the residual `3k+1` quotient terms with `k=3,4,5`, one can find exactly the needed `k-2` pairwise disjoint quotient zero-sum subsequences (their scalar-lift proof then analyzes the induced values).

Only the quotient-side existence of these `k-2` disjoint zero sums is used here; their scalar/cyclic lift equations are not imported.

Let the lifted sums of these residual zero-sum blocks be

`c_1,...,c_(k-2) in K`.

## Maximal-kernel completion lemma

Concatenate the kernel sums

`U = H c_1 ... c_(k-2)`.

Then

`|U| = (44-k)+(k-2) = 42 = d(K)`,

because `D(C_15^3)=43`.

Moreover U is zero-sum-free. Indeed, every term of U is the sum of a block of original S, and all these blocks are pairwise disjoint. If a nonempty subsequence of U summed to zero in K, the union of the corresponding original blocks would be a nonempty zero-sum subsequence of S, contradicting the hypothesis.

Therefore **every hypothetical length-133 C45 counterexample canonically produces, after a donor-valid quotient block selection, a maximal zero-sum-free sequence U of length 42 in the mixed kernel C_15^3.**

This holds uniformly for all surviving cases k=3,4,5.

## Interpretation

The earlier `r=1,2,3` missing-sum cascade is a useful local view, but the stronger global object is the completed maximal sequence U. In particular:

- r=1 corresponds to extending a length-41 H by one residual correction;
- r=2 extends length 40 by two corrections;
- r=3 extends length 39 by three corrections;
- under a hypothetical counterexample, all three extensions land in the same object class: maximal zero-sum-free sequences of C_15^3.

This exactly generalizes the donor scalar-lift phenomenon. For a cyclic kernel `C_d`, a maximal zero-sum-free sequence has the rigid repeated-generator form, which is why the 2007 proof obtains equal induced block values. For the mixed rank-3 kernel `C_15^3`, this inverse structure is not presently available in the same form.

## New highest-value residual

The live mathematical bottleneck is now:

> determine enough inverse structure of maximal zero-sum-free sequences U of length 42 in C_15^3 to rule out their realization as lift sums of the donor-admissible 42-block quotient systems arising from a hypothetical C45 counterexample.

Possible sufficient outputs, in descending strength:

1. classify maximal zero-sum-free sequences in `C_15^3` sufficiently to contradict the quotient-block realization;
2. prove a structural property of every such U (support orders, primary projections, missing-sum geometry, multiplicity, generated subgroup, or another native invariant) incompatible with the block system;
3. prove the property only for maximal U that arise from these quotient block systems;
4. find a realizable maximal U/block-system obstruction, forcing a stronger exchange grammar or new state coordinate.

## Relation to fresh nu_p work

Geroldinger--Yang Proposition 2.5 describes missing sums of length `d(G)-1` sequences through maximal atoms, and Proposition 3.2 relates sharp `nu_p` to the orders of elements in maximal atoms. Thus the fresh `nu/nu_p` programme is not a separate side problem: it is one route into the exact inverse structure of the maximal U now forced by the C45 reduction.

However, no `nu_p(C_15^3)=41` statement is assumed.

## Claim boundary

This is a reduction theorem under donor inputs, not a proof of `D(C_45^3)=133` and not a novelty claim about maximal zero-sum-free sequences. The new research object is the compatibility between maximal C15^3 zero-sum-free sequences and the restricted C3^3 quotient-block realization.
