# Failed bootstraps around the packing-defect formalism — V1

Status: **retained negative route record**. These failures are part of the proof discipline and must not be silently converted into lemmas.

## 1. Appending a pure `p`-block need not preserve defect

Let `B` be zero-sum over an exponent-`p` group and append `g^p`. One always has

`z(Bg^p)>=z(B)+1`.

However cross-factorizations may use terms from both factors and increase the packing number by more than one. Therefore

`delta_p(Bg^p)<=delta_p(B)`,

but equality is not automatic.

Consequently a defect maximizer at one factorization length does not by itself construct maximizers at every larger length. The Freeze--Schmid lower line remains an essential donor input in the equivalence for `C_p^3`.

The valid monotonic statement goes in the reverse direction: if a block contains `g^p`, deleting it cannot decrease defect.

## 2. Eventual linearity does not imply immediate stabilization

The donor theorem that `D_k(G)` is eventually affine-linear with slope `exp(G)` gives a stable intercept after some index. It does not exclude a larger pre-stable value of

`D_k(G)-k exp(G)`.

The defect envelope

`max_k(D_k(G)-k exp(G))`

is precisely designed to retain such overshoots. For `C_p^3`, proving the proposed line from `k=2` requires proving that no later overshoot exceeds `(5p-5)/2`; eventual linearity alone is insufficient.

## 3. Atomic excess signatures are necessary, not sufficient

A terminal factorization above the conjectured defect threshold has atom excesses

`e_i=|U_i|-p`

with bounded sum and pair inequalities. Distinct vector configurations can share the same sorted excess tuple while having completely different alternative factorizations.

Thus signature enumeration is a front-end pruning step. It cannot replace scalar lifts, projective incidence, atom minimality, or an exact conformal-splitting test.

## 4. A generic Graver statement is not yet the missing theorem

The standard Graver test-set theorem says that every non-optimal factorization admits an applicable improving Graver move. This makes “terminal above the threshold” exactly equivalent to a counterexample.

It does **not** prove that such a move always exists. The required new content must use the special modular rank-three geometry, short-freeness, support deficit, or coding structure to rule out high-cost terminal fibers.

Calling the general Graver theorem alone a proof of the Davenport formula would be circular: optimality is exactly the unknown packing number.

## 5. Removing an arbitrary long atom is not defect-monotone

If `A|B` is zero-sum and `R=BA^{-1}`, then

`delta_p(B)<=delta_p(R)+|A|-p`.

For `|A|>p`, the right-hand correction is positive. Hence arbitrary atom peeling can increase or decrease the relevant upper bound and does not produce a monotone induction. The shortest-maximizer argument works specifically for zero-sum subsequences of length at most `p`.

## 6. Global proper-subsum cardinality lost the needed rank information

For the `(8,10,19)` and `(9,9,19)` corridors, a lower bound on the number of proper subsums of the short atom did not by itself exclude a maximal atom. A large complement can still be concentrated on low-rank projective fibers.

The retained repair is `LENGTH19_PROJECTIVE_LINE_FIBER_AVOIDANCE_V1.md`, which records scalar survivor lists direction by direction.

## 7. Search-boundary rule

A finite computation may close only the explicitly generated Apéry/projective/factorization domain. In particular:

- a sampled set of atoms is not the Hilbert basis;
- a circuit list is not automatically the modular Graver basis;
- absence of an improving move in a truncated move set is not terminality;
- duplicate parameterizations are acceptable for elimination only after surjective coverage is proved;
- eventual stabilization or donor analogies do not grant novelty authority.

These failures remain live controls for every implementation of the defect-core programme.