# Mathematical Extensions R5 — Exact Cyclic-Axis Budgets and Quotient Upper Bounds

Date: 2026-08-25

Canonical predecessors: `MANUSCRIPT_V3_PIPELINE.md` and `MATHEMATICAL_EXTENSIONS_R4.md`

Status: rigorous theorem addendum. The statements concern the declared alphabet-restricted zero-sum invariant and any compiler grammar that separately proves the V3 deletion hypotheses. They do not assert production-TARE equivalence or physical-resource improvement.

## 1. Why another mathematical pass was useful

R4 supplied direct-sum equality, quotient lower bounds, a finite multiplicity formulation, and controlled objective defects. Two gaps remained. First, the invariant was not evaluated exactly for the most common heterogeneous axis alphabet. Second, quotients were used only as lower-bound obstructions, although the kernel also gives a useful upper bound. This addendum closes both gaps.

## 2. Exact value for the standard cyclic-axis alphabet

Let

`H = C_{n_1} direct_sum ... direct_sum C_{n_r}`

and let `e_i` be the standard generator of the `i`th cyclic factor. Put

`A_std={e_1,...,e_r}`.

**Theorem A8 (standard-generator formula).**

`zsf(H;A_std)=sum_{i=1}^r (n_i-1)`.

**Proof.** A word over `A_std` is specified by multiplicities `u_i`. If some `u_i>=n_i`, then `n_i` copies of `e_i` form a zero-sum subsequence. Hence a zero-sum-free word has `u_i<=n_i-1` for every `i`, giving the upper bound.

Conversely, take exactly `n_i-1` copies of every `e_i`. Any zero-sum subsequence selects `v_i` copies with `0<=v_i<=n_i-1`. Its `i`th coordinate is zero only when `v_i=0`, because `n_i` is the order of `e_i`. Thus every coordinate count is zero and the selected subsequence is empty. The word is zero-sum-free and attains the bound. ∎

This is an alphabet theorem, not the general Davenport formula for `H`. The unrestricted Davenport constant can be larger in groups where the usual lower-bound expression is not exact. Here exactness follows because the alphabet is restricted to independent cyclic axes.

**Corollary A9 (heterogeneous compiler axes).** If a deletion certificate uses one standard generator for each independent cyclic signature factor, its exact abstract terminal budget is the sum of the factor orders minus one. No ambient-rank replacement is needed.

## 3. An alphabet-sensitive quotient upper bound

Let `phi:H->K` be a homomorphism, let `N=ker(phi)`, and put `B=phi(A)`. Define

`atom(K;B)=max{|U|: U is a minimal nonempty zero-sum word over B}`.

The maximum exists for a finite nonempty alphabet. If `0 in B`, the one-letter zero word is an allowed atom. Let `D(N)` denote the ordinary Davenport constant of the kernel, with `D({0})=1`.

**Theorem A10 (quotient-kernel upper bound).**

`zsf(H;A) <= zsf(K;B) + (D(N)-1) atom(K;B)`.

**Proof.** Let `W` be zero-sum-free over `A`. In the image word `phi(W)`, repeatedly remove an inclusion-minimal nonempty zero-sum block until the remaining image word is zero-sum-free. Call the removed blocks `U_1,...,U_q` and the remainder `V`.

The remainder has length at most `zsf(K;B)`, and every removed block has length at most `atom(K;B)`. Lift each block back to its original positions in `W`, and let `n_i in N` be the sum of that lifted block. No `n_i` is zero, because then the corresponding source positions would form a zero-sum subsequence of `W`. More generally, no nonempty subsequence of `n_1,...,n_q` sums to zero: the union of the associated source blocks would be a zero-sum subsequence of `W`. Hence `n_1...n_q` is zero-sum-free over `N`, so `q<=D(N)-1`.

Therefore

`|W|=|V|+sum_i |U_i|`

`<=zsf(K;B)+(D(N)-1)atom(K;B)`.

Taking the maximum over `W` proves the claim. ∎

**Corollary A11 (coarse quotient bound).** Since every minimal zero-sum word over `B` is a minimal zero-sum sequence over `K`,

`atom(K;B)<=D(K)`

and therefore

`zsf(H;A)<=zsf(K;B)+(D(N)-1)D(K)`.

For the unrestricted alphabet this recovers the familiar product-style subgroup/quotient estimate `D(H)<=D(N)D(K)`. The new content here is the retained dependence on the realized image alphabet and its maximal atom length.

## 4. Two-sided quotient bracketing

Combining R4 Theorem A3 with Theorem A10 gives

`zsf(K;phi(A)) <= zsf(H;A)`

`<= zsf(K;phi(A))+(D(ker phi)-1)atom(K;phi(A))`.

A quotient is therefore more than a fail-fast lower obstruction. When the kernel is small or the image alphabet has short atoms, it gives a certified interval for the exact support budget. A chain of quotients can be selected to trade computational cost against interval width.

## 5. Compiler consequence

Assume the V3 deletion hypotheses hold for a compiler signature alphabet `A subseteq H`. A quotient may be chosen because its alphabet invariant and atom length are easy to compute. Theorem A10 then supplies a sound support cap without solving the full multiplicity program of R4 Proposition A4. This is especially useful when the signature group has a small semantic kernel added to a simple axis quotient.

The theorem does not say that the resulting cap is intrinsic. As in Papers A and B, intrinsic support still requires a production lower witness and exclusion of stronger production moves.

## 6. Verification

`papers/verify_five_math_extensions_r5.py` checks:

1. Theorem A8 on several heterogeneous products;
2. the quotient upper inequality on an explicit `C_2 direct_sum C_4` alphabet; and
3. the finite minimal-atom calculation used in that check.

The executable checks protect arithmetic and enumeration, while the displayed decomposition proof carries the general theorem.

## 7. Prior-art calibration

Subgroup and quotient methods for ordinary Davenport constants are classical. Restricted alphabets, weighted variants, and zero-sum invariants are also established subjects. No blanket novelty is claimed for decomposing a sequence through a quotient. The paper-specific residual is the alphabet-sensitive bound in the exact normal-form pipeline: the image remainder uses `zsf(K;B)`, each extracted image block uses `atom(K;B)`, and the kernel obstruction counts how many such blocks can coexist in a source zero-sum-free word.

## 8. Atomic status

- Standard-generator formula: `VERIFIED` by a two-sided proof.
- Quotient-kernel upper bound: `VERIFIED` by minimal-block extraction.
- Coarse product bound: `VERIFIED` as a corollary.
- Compiler support cap: `CONDITIONAL` on the V3 deletion hypotheses.
- Intrinsic production support: `NOT_INFERRED`.
- Physical compiler benefit: `NOT_CLAIMED`.

## 9. Remaining scientific frontier

The central external gate is no longer a missing algebraic support formula. It is semantic realization: identify a production-relevant compiler whose exact edit system satisfies persistent deletion soundness, measure whether the sharper alphabet/quotient cap changes an exact search, and supply a production obstruction if intrinsic language is desired. Further abstract refinements without such a realization would now have diminishing scientific value.
