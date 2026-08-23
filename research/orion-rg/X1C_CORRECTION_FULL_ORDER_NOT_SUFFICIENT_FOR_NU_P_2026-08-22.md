# X1-C correction — full-order maximal atoms do not imply sharp nu_p

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Parent issue: #901

## Incorrect exploratory implication withdrawn

An earlier exploratory discussion suggested that proving every term of every maximal-length minimal zero-sum sequence over `C_15^3` has full order 15 would give the sharp statements

`nu_3(C_15^3)=41` and/or `nu_5(C_15^3)=41`.

That implication is **not justified** and is withdrawn.

## Exact donor statement

Geroldinger--Yang, arXiv:2608.19090, Proposition 3.2(1), prove the one-way implication:

If

`nu_p(G)=d(G)-1`,

then for every maximal-length minimal zero-sum sequence `U in A_max(G)`,

`supp(U) intersection pG = empty`.

For homocyclic `G=C_n^r`, sharp `nu_p=d-1` for every prime divisor p therefore implies that all support elements of every maximal atom have full exponent. This is a **necessary consequence** of sharp `nu_p`.

The converse is not stated or proved there. Avoidance of `pG` alone does not force the entire set of missing subsequence sums of every `(d-1)`-term zero-sum-free sequence into one common affine index-p coset.

## Correct use in X1-C

- Finding an order-3 term in a maximal atom of `C_15^3` refutes sharp `nu_5=41`.
- Finding an order-5 term in a maximal atom of `C_15^3` refutes sharp `nu_3=41`.
- Proving that all maximal-atom terms have order 15 is only a necessary-condition theorem / obstruction removal. It does **not** establish either sharp `nu_p` value.
- A positive sharp-`nu_p` result still requires the actual missing-subsequence-sum coset containment for every zero-sum-free sequence of length 41.

## Claim boundary

This correction prevents a one-way donor implication from being reversed. No new theorem authority is claimed.
