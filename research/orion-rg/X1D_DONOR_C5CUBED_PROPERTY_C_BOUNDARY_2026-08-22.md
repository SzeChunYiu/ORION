# X1-D donor absorption — exact C_5^3 short-zero-sum boundary structure

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Parent issue: #909

## Source

W. D. Gao, Q. H. Hou, W. A. Schmid, R. Thangadurai, *On short zero-sum subsequences II*, INTEGERS 7 (2007), #A21.

## Donor facts

For `G=C_5^3`:

1. Theorem 1.7 specialized to `n=5` gives

   `s(G)=37`, `eta(G)=33`.

2. Proposition 5.6 proves `C_5^3` has Property D.

3. The paper recalls that Property D implies Property C. Hence every sequence S of length

   `eta(G)-1 = 32`

   with no nonempty zero-sum subsequence of length at most 5 has the form

   `S = T^4`.

Because five equal nonzero elements already sum to zero in exponent 5, T cannot repeat an element in such an extremal S. Thus T is squarefree of length 8, and `supp(S)` is an 8-point cap. This is also consistent with Proposition 5.3, which proves the cap property at the eta-extremal boundary.

Therefore the complete structural boundary immediately below `eta(C_5^3)=33` is:

> every 32-term short-zero-sum-free sequence is four copies of an 8-point cap.

## Relevance to X1-D

The P5 C45 route repeatedly extracts quotient zero-sums of length at most 5 from `C_5^3` until a final >=33-term base residual is reached. The donor structure above means that any stage which comes within one term of the short-zero-sum threshold has a highly rigid alternative if no new short zero sum remains.

This does **not** by itself guarantee a 24th quotient block or an E0 correction. The active research question is whether the rigidity of the 32-term `T^4` boundary forces either:

- a second/alternative short zero-sum block with a kernel correction outside the exceptional C9 affine coset; or
- a finite cap-structured obstruction that can be carried into the mixed source lift and analyzed exactly.

## Claim boundary

The values of eta/s, Property D/C, and the T^4 cap structure are wholly donor-owned. This note only binds them into the X1-D proof state. No novelty or C45 theorem authority is claimed.
