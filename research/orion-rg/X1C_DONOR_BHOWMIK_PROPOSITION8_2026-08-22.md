# X1-C donor absorption — Bhowmik–Schlage-Puchta Proposition 8

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Parent issue: #901

## Source

Gautami Bhowmik and Jan-Christoph Schlage-Puchta, *Davenport's constant for groups of the form Z_3 ⊕ Z_3 ⊕ Z_{3d}*, arXiv:math/0610416v1 (2006), Proposition 8.

Source URI: `https://arxiv.org/html/math/0610416v1`

## Exact donor statement absorbed

For every `k >= 3`,

`D_k(C_3^3) = 3k + 6`.

More strongly, the paper classifies **all** multisets `A` of the maximum failing size `3k+5` which do not contain `k` pairwise-disjoint nonempty zero-sum submultisets.

They are exactly constructed as follows.

1. Choose a seven-point set `B={b_1,...,b_7}` of distinct elements of `C_3^3` having no zero-sum subsum of length at most 3.
2. Require that the doubled multiset `C=B^2` (each `b_i` twice) has no zero-sum subsequence of length at least 12.
3. Choose nonnegative integers `kappa_1,...,kappa_7` with

   `kappa_1+...+kappa_7 = k-3`.

4. Set the multiplicity of `b_i` to

   `2 + 3 kappa_i`.

Equivalently, every maximum failing multiset has support on exactly seven special points and all seven multiplicities are congruent to `2 mod 3`.

The proof also establishes that there are no other maximum failing examples.

## Consequence for ORION-RG

The earlier X1-C inverse route through an arbitrary 42-term `D_12` extremal is not the strongest available donor compression for the live C45 target.

For C45, the projected hypothetical counterexample has length 133 and must fail to contain 43 disjoint quotient zero sums. Since

`D_43(C_3^3)=135`,

maximum failing size is `134 = 3*43+5`, and Proposition 8 completely classifies that maximum layer.

Therefore the correct next residual is a **deficiency-one near-extremal classification** at size 133, not a fresh classification of the maximum layer.

## Claim boundary

The seven-point support/multiplicity classification is wholly donor-owned. ORION may only claim a new result if it proves something not contained in Proposition 8, such as a deficiency-one extension/classification theorem, a lift-compatible refinement, or a new C45/infinite-family theorem. No novelty or scientific authority is granted by this absorption note.
