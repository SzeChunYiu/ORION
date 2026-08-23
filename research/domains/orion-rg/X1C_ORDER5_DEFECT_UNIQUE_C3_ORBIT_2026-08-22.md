# X1-C finding — a single order-5 defect forces one unique C3^3 quotient-support orbit

Parent: #901. Committed before downstream use.

## Setup

Let `U` be a maximal zero-sum-free length-42 sequence in `K=C_15^3` compatible with the X1-C C45 reduction. The committed full-order theorem gives at most one order-5 term.

Assume the extremal defect case

`b=1`,

and let `g` be the unique order-5 term.

Under the primary projection

`pi_3 : C_15^3 -> C_3^3`,

we have `pi_3(g)=0`.

The committed primary packing theorem gives

`pack_0(pi_3(U))=12`.

Hence, after deleting the singleton zero `pi_3(g)`, the remaining 41-term sequence

`A = pi_3(U g^{-1})`

has packing number exactly 11 and in particular fails to contain 12 pairwise disjoint nonempty zero-sum subsequences.

Since the exact donor threshold is

`D_12(C_3^3)=42`,

A has the maximum possible size 41 for a sequence failing 12 disjoint zero sums.

## Proposition-8 classification

Bhowmik--Schlage-Puchta Proposition 8 classifies every maximum `D_k(C_3^3)` failure for `k>=3`.

For k=12, A has the form

`A = C * b_1^(3 kappa_1) * ... * b_7^(3 kappa_7)`,

where

- `B={b_1,...,b_7}` consists of seven distinct nonzero points in `C_3^3`;
- `C=b_1^2 ... b_7^2` is the 14-point doubled base extremal used in Lemma 2;
- `kappa_i >=0` and

  `kappa_1+...+kappa_7 = 12-3 = 9`.

Therefore the multiplicity of each support point is

`v_(b_i)(A)=2+3 kappa_i`,

so all seven multiplicities are congruent to 2 modulo 3 and their sum is 41.

## Unique support orbit

Lemma 2 of the same paper proves that the relevant 14-point doubled-base extremal `C` is unique up to linear equivalence in `C_3^3`.

Consequently, in the b=1 branch, the **support** of the 41 nonzero projected terms of U is not an arbitrary seven-point subset. Up to `GL(3,3)`, it is the unique seven-point support underlying the Lemma-2 doubled extremal.

Thus every b=1 candidate is determined on the quotient side by only:

1. one fixed seven-point support orbit B;
2. a weak composition/partition `(kappa_1,...,kappa_7)` of 9, modulo the automorphism stabilizer of B;
3. the C5^3 lift values assigned to the 41 occurrences;
4. the single kernel-only order-5 term g.

This is a major finite-state reduction relative to arbitrary 41-term C3^3 projection data.

## Total quotient sum

The added `3 kappa_i` copies contribute zero to the total sum in exponent 3. Therefore

`sigma(A)=sigma(C)`.

In the explicit Lemma-2 representative, the paper records

`sigma(C)=(2,2,2) !=0`.

Hence, invariantly under linear equivalence,

`sigma(pi_3(U)) = sigma(A) !=0`

in the b=1 branch.

Thus the total sum of U has a nonzero 3-primary component. In particular, the completion term `-sigma(U)` in the associated maximal atom cannot have order 5.

## Why this matters

The b=1 order-defect branch has collapsed to a unique quotient geometry rather than a generic mixed-rank inverse problem. The remaining freedom is almost entirely in the C5^3 lifts and the partition of nine triple-multiplicity units among the seven support points.

This creates a concrete theorem/computation target:

> show that no assignment of C5^3 lift values to a Proposition-8 k=12 extremal quotient, together with one kernel-only order-5 term, can be zero-sum-free of total length 42 in C15^3; or serialize the first exact assignment that survives all current constraints.

A finite solver result on bounded lift assignments would be obstruction evidence only unless independently converted to an all-assignment proof/certificate.

## Donor-reading note

Proposition 8's base configuration is the Lemma-2 doubled extremal. Lemma 2 states the relevant extremal condition as excluding short zero-sums and long zero-sums (length >=12) and proves uniqueness up to linear equivalence. This resolves an earlier OCR/sign ambiguity in the Proposition-8 text; no alternative `<=12` interpretation is used here.

## Claim boundary

This result is a specialization of donor inverse classification plus already-earned X1-C packing constraints. It does not eliminate the b=1 branch, prove C45, or establish novelty authority.
