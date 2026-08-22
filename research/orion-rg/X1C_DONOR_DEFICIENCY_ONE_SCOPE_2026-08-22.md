# X1-C donor boundary — deficiency-one C3^3 layer is used, but not generically classified

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Parent issue: #901

## Source

Bhowmik--Schlage-Puchta, arXiv:math/0610416v1.

## Finding

The paper does not stop at the maximum-failing `3k+5` layer of Proposition 8. Its main theorem starts with a sequence of exactly `3d+4` terms in

`Z_3 ⊕ Z_3 ⊕ Z_(3d)`

and projects it to `C_3^3`.

When `(d,3)=1`, the source group is represented as

`C_3^3 ⊕ Z_d`,

so each projected occurrence carries a **scalar cyclic lift label** `f(a) in Z_d`.

The final proof shows that a hypothetical zero-sum-free source sequence would produce a projected multiset of size `3d+4` with at most `d-1` disjoint quotient zero-sums and an admissible scalar lift function. It repeatedly removes short quotient zero-sums and reduces to a 10-point / two-block scalar-lift obstruction, which is ruled out by the preceding theorem.

## What is donor-owned

- Working directly on the deficiency-one size `3d+4` is donor-owned.
- Projecting to `C_3^3` and retaining lift information is donor-owned.
- Removing many short quotient zero-sums and reducing to a bounded obstruction is donor-owned.
- Using equations among lift labels induced by multiple quotient-zero-sum representations is donor-owned.

## What the source does NOT provide for X1-C

The proof does not give a generic classification of **all** `3k+4` multisets in `C_3^3` that fail `k` disjoint zero sums, independent of a lift.

More importantly, its lift state is one-dimensional/cyclic: `f:A -> Z_d`. The live C45 problem has kernel

`K = C_15^3`,

so the lifted block sums form rank-three mixed-primary vectors rather than scalar cyclic labels. The scalar contradiction in the 2006 proof cannot be imported as a proof for C45 without a new correspondence theorem.

## Consequence

A bare claim that 'deficiency-one projection structure matters' would not be novel. A possible new result must be one of:

1. a genuine generic/stability classification of `3k+4` failures not contained in the donor proof;
2. a new lift-compatible theorem for rank-three mixed kernels such as `C_15^3`;
3. a new reduction showing that the mixed-kernel lift constraints collapse to an already-solved donor scalar state;
4. a counterexample showing that no such finite/scalar compression is possible.

## Claim boundary

This note is donor subtraction only. No novelty or theorem authority is claimed.
