# Exact Certificate Complexity versus Intrinsic Support in Quantum Compilation

## Abstract

A finite-support certificate can be perfectly sharp for its proof language and arbitrarily loose as a description of the compiler it certifies. We formalize this separation using an alphabet-restricted zero-sum invariant. Let `H` be a finite abelian signature group and `A subseteq H` an allowed alphabet. Define `zsf(H;A)` as the maximum length of a zero-sum-free word over `A`. In the abstract deletion proof system whose legal step removes a nonempty proper zero-sum subword from a nonzero-total word, the exact uniform terminal complexity is `zsf(H;A)`: every longer word is reducible, while a maximum zero-sum-free word is a matching terminal witness. For a production compiler, this remains an exact certificate lower bound only when that witness is realizable.

Two quantum-compilation families provide opposite controls. In one-Tag R6M, the production signature alphabet realizes `F_2^2`, the rank-only certificate complexity is two, and independent compiler upper/lower results give intrinsic support `kappa_R6M=2`. In R6I, both production alphabets realize basis obstructions in `F_2^5`, so the rank-only certificate complexity is exactly five, while an independent whole-system Tag-relocation theorem gives intrinsic support exactly one. Hence

`beta_rank-only(R6I)=5 > 1=kappa_R6I`.

For `t` registered independent components, certificate and intrinsic budgets are `5t` and `t`; the additive gap is `4t`, and a direct support enumerator incurs an asymptotic search-volume ratio `Theta(n^(4t))` for fixed local alphabet and `t`. The result is not an unrestricted proof lower bound. It establishes a precise reporting principle: a support number belongs to the compiler only after an intrinsic lower witness; otherwise it is a property of a normalization or certificate language.

## 1. Introduction

Support bounds make otherwise unbounded exact compiler searches finite. Their numerical value, however, can answer three different questions:

1. What support does the compiler intrinsically require?
2. What support can a named normalization reach?
3. What support can a restricted proof system certify?

These questions coincide in some families and diverge sharply in others. Paper A provides the positive normal-form theorem. This paper identifies its exact proof-language complexity and compares it with independently established intrinsic support.

The central refinement is to replace ambient rank by `zsf(H;A)`, the longest zero-sum-free word over the actual signature alphabet. In elementary binary systems this equals dimension when a basis is present, but the general definition makes the quantifiers and lower-witness obligation explicit.

### 1.1 Contributions

1. **Exact abstract certificate theorem:** the zero-sum deletion language has terminal complexity `zsf(H;A)`.
2. **Realization criterion:** a compiler inherits the matching lower bound only if it realizes a maximum zero-sum-free word.
3. **Tight control:** R6M has certificate and intrinsic support both equal to two.
4. **Strict separation:** R6I has exact rank-only certificate five and intrinsic support one.
5. **Product/search amplification:** registered products give `5t` versus `t` and direct-enumeration ratio `Theta(n^(4t))`.

## 2. Three support quantities

Fix a compiler family `F` and objective `C`.

### 2.1 Intrinsic support

`kappa(F,C)` is the least `k` such that every instance has an exact optimum of support at most `k`, with an independent witness showing `k-1` cannot suffice.

### 2.2 Normalization ceiling

A transformation `N` may prove every configuration has a no-more-expensive representative of support at most `B_N`. Without a matching compiler lower witness, `B_N` belongs to `(F,C,N)` rather than intrinsically to `(F,C)`.

### 2.3 Certificate complexity

A proof system `P` restricts visible information and legal inference. `beta_P(F,C)` is the least uniform support budget that `P` can certify for its production scope. Soundness gives

`kappa(F,C) <= beta_P(F,C)`,

but equality is additional mathematics.

## 3. Alphabet-restricted zero-sum deletion

Let `H` be a finite abelian group and `A subseteq H`. A certificate word `v_1...v_w` has nonzero total. The only legal shortening removes a nonempty proper subword summing to zero.

Define

`zsf(H;A)=max{|W|: W is a zero-sum-free word over A}`.

**Theorem 1 (exact abstract certificate complexity).** The maximum terminal length of the abstract deletion language over all nonzero-total words on `A` is exactly `zsf(H;A)`.

**Proof.** A word longer than `zsf` contains a nonempty zero-sum subword. Its nonzero total prevents that subword from being the whole word, so a legal deletion exists. Conversely, a maximum zero-sum-free word has nonzero total and admits no deletion. ∎

This theorem is generic zero-sum mathematics. The compiler question begins with realization.

**Corollary 2 (production realization).** If every production word lies over `A`, the certificate ceiling is at most `zsf(H;A)`. If a production state realizes a maximum zero-sum-free word and no other certificate rule can reduce it, the ceiling is exact.

For `H=F_2^d`, `zsf<=d`; any alphabet containing a basis has `zsf=d`.

## 4. Tight control: R6M

A one-Tag R6M frame coordinate carries partner and Tag bits. The production alphabet realizes a basis of `F_2^2`; hence the rank-only certificate language has

`beta_rank-only(R6M)=2`.

Independent all-size normalization and exact support-one obstruction results establish

`kappa_R6M=2`.

Therefore R6M is a tight control:

`beta_rank-only(R6M)=kappa_R6M=2`.

The existence of this control matters. It shows that the certificate is not generically loose; tightness depends on whether its obstruction is also an intrinsic compiler obstruction.

## 5. Strict separation: R6I

R6I has two rank-2 dependent-triple blocks with a shared two-bit Tag. The production block-deletion alphabets span five-dimensional binary quotients and contain realized basis words. The abstract theorem and production binding give

`beta_rank-only(R6I)=5`.

A stronger transformation leaves the rank-only language. It localizes each block to an anticommuting core and then relocates/reconstructs the shared Tag globally. That all-size theorem proves support at most one, while support zero is infeasible:

`kappa_R6I=1`.

Thus the exact single-component separation is

`beta_rank-only-kappa=4`.

There is no contradiction. The basis word blocks zero-XOR deletion while the successful proof changes auxiliary Tag structure that the certificate freezes.

## 6. Product amplification

Let `F_R6I^t` be the registered product of `t` independent components on disjoint coordinates with additive support budget and no cross-component move.

**Theorem 3.** For every `t>=1`,

`beta_rank-only(F_R6I^t)=5t`,

`kappa(F_R6I^t)=t`.

**Proof.** Componentwise upper bounds add. A realized basis obstruction in each component gives the certificate lower bound five per component. Support zero is infeasible in each component and the support-one normalization acts independently, giving intrinsic lower and upper value one per component. ∎

The additive gap is `4t`.

### 6.1 Direct enumeration consequence

For fixed local alphabet and fixed support budget `B`, a direct support enumerator over `n` coordinates has leading search growth `Theta(n^B)`. Consequently the registered product's rank-only and intrinsic direct enumerators scale as

`Theta(n^(5t))` and `Theta(n^t)`,

with ratio

`Theta(n^(4t))`.

This is an exact statement about the declared enumeration model, not an algorithm-independent complexity-class lower bound.

## 7. Relation to prior work

General sparse-optimum theory already studies support bounds and lower constructions for integer optimization. Classical and modern zero-sum theory owns Davenport constants, subset/weighted/universal variants, basis obstructions, and direct sums. Proof complexity and formal methods already distinguish object difficulty from lower bounds inside a restricted language.

The residual contribution is the exact production realization in quantum compilation: the same algebraic certificate is tight for R6M, loose by five-to-one for R6I, and unboundedly loose in additive budget under products. The stronger R6I transformation pinpoints the missing proof operation—whole-system Tag reconstruction—rather than merely reporting a smaller number.

## 8. Reproducibility

The production R6I alphabets, basis witnesses, source/generic/native agreement, and intrinsic support-one parent are commit-bound in the B1 package. The R6M all-size upper theorem and its exact support-one obstruction witness are commit-bound in the A1 parent package at `research/extensions/orion-qg/paper_a_a1_multitag_tare.py` and `research/extensions/orion-qg/PAPER_A_A1_MULTITAG_TARE_RESULTS_2026-08-24.json`; that package records `multitag_sharpness_authority: false`, so it binds the `kappa_M = 2` boundary corollary and does not carry general multitag-sharpness authority. The R2 verifier checks alphabet invariants on small nonbinary and binary groups, basis obstructions through dimension four, and the exact product formulas.

All-size authority comes from Theorems 1 and 3. Internal independent implementations remain distinct from external replication.

## 9. Limitations

1. The abstract exactness theorem concerns the stated zero-sum deletion language.
2. A compiler lower bound requires realization of the zero-sum-free witness.
3. No lower bound is proved for every local, syndrome-preserving, or unrestricted proof system.
4. The product amplifies one mechanism and forbids cross-component transformations by definition.
5. `Theta(n^(4t))` concerns a direct support enumerator, not arbitrary algorithms.
6. Structural support is not a physical quantum-resource advantage.
7. Submission-date novelty and independent proof review remain external.

## 10. Discussion and conclusion

A certificate can be sound, useful, and internally optimal while measuring the wrong layer for an intrinsic interpretation. `zsf(H;A)` identifies the exact expressive ceiling of zero-sum deletion. R6M shows that this ceiling can coincide with intrinsic support. R6I shows that a stronger global transformation can cross it dramatically.

The practical reporting rule is simple: label a number as intrinsic only after a compiler lower witness; otherwise state the normalization or proof system that owns it. This turns later improvements from apparent contradictions into interpretable increases in proof-language expressivity.

## Selected references

- I. Aliev et al., *The Support of Integer Optimal Solutions*, SIAM J. Optim. 28, 2152–2157 (2018), DOI `10.1137/17M1162792`.
- G. Wang, *The universal zero-sum invariant and weighted zero-sum for infinite abelian groups*, Commun. Algebra 53 (2025), DOI `10.1080/00927872.2024.2418017`.
- M. Freeze and W. A. Schmid, *Remarks on a generalization of the Davenport constant*, Discrete Math. 310, 3373–3389 (2010), arXiv:0905.4248.

## Publication decision record

**Primary target:** `Quantum`, provided the introduction makes the compiler/proof-language consequence immediate and the reproducibility archive is external-review ready.
**Stretch:** `PRX Quantum` only under an independently endorsed exceptional-connection case.
**R2 status:** `HIGH_SELECTIVITY_SPECIALIST_CANDIDATE__EXACT_TIGHT_VS_LOOSE_CONTROLS`.
**External-only gates:** hostile proof audit, full primary-source overlap check, figures, exact formatting, permanent archive.
