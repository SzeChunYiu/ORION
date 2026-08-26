# Certificate Complexity Can Exceed Intrinsic Support in Exact Quantum Compilation

**Paper B — publication-candidate manuscript**

## Abstract

Support bounds are often used to make exact compiler optimization finite, but the bound certified by a proof system need not be the smallest support intrinsically required by the compiler. We make this distinction exact in two frozen quantum-compilation families. Consider a rank-only deletion proof system over an `F_2^d` production alphabet: a certificate may shorten a nonzero-total word only by deleting a nonempty proper zero-XOR subsequence. If the alphabet spans `F_2^d` and contains a basis, the exact uniform terminal length of this proof system is `d`. Linear dependence gives the upper bound, while the basis word is a matching zero-sum-free lower witness. We then compare two production compilers using the same proof schema. In the one-Tag R6M signature system, the rank-only certificate complexity is two and the independently established intrinsic support number is also two: the certificate is tight. In the R6I production system, both block alphabets have rank five and contain exact basis obstructions, so the same rank-only proof language has certificate complexity five, whereas an independent whole-system Tag-relocation normalization proves intrinsic support exactly one. Thus

`beta_rank-only(R6I)=5 > 1=kappa_R6I`.

For `t` explicitly independent R6I components under a summed support budget, the exact separation amplifies to `5t` versus `t`, giving unbounded additive gap `4t` and correspondingly different degrees for direct support-bounded enumeration. The theorem is not a lower bound for every local proof formalism or for unrestricted proofs. Its point is sharper: a certificate can be mathematically optimal **inside its proof language** and still overestimate the structural complexity of the optimized compiler by an arbitrarily large additive amount.

## 1. Introduction

A support theorem answers an algorithmic question: how large a structural object must an exact optimizer enumerate? A proof of such a theorem usually reveals a finite invariant—rank, syndrome dimension, width, treewidth, conserved charge or another quotient. It is tempting to treat that invariant as the complexity of the underlying compiler.

That inference needs a lower witness at the level of the compiler itself. Without one, the theorem may instead expose the expressive limit of its own proof language.

This paper formalizes that difference for a particularly transparent proof mechanism. A coordinate carries an `F_2^d` signature. The proof is allowed to delete coordinates only when their signatures XOR to zero. Linear dependence then guarantees a support ceiling `d`. The standard-basis word shows that no smaller uniform ceiling can be proved **by that deletion language**. These two facts make the certificate exact.

The new scientific question is whether that exact certificate is also intrinsic to the compiler. Two production cases give opposite answers. The R6M one-Tag grammar is a tight control: rank two and intrinsic support two coincide. R6I is the separation case: a rank-five deletion certificate is exactly optimal in its restricted language, yet a whole-system transformation that relocates and reconstructs the shared Tag leaves that language and proves intrinsic support one.

The contrast is important because a loose proof can still be sound, sharp and useful. The failure is not mathematical correctness; it is an ontological misclassification of what the number measures.

### 1.1 Contributions

**B1 — exact rank-only certificate theorem.** A spanning `F_2^d` production alphabet containing a basis has uniform rank-only deletion certificate complexity exactly `d`.

**B2 — tight compiler control.** The R6M signature alphabet instantiates `d=2`, and its independent intrinsic support number is `kappa_R6M=2`.

**B3 — strict compiler separation.** The R6I production alphabets instantiate `d=5`, while `kappa_R6I=1`; thus the exact certificate-to-object gap is four in one component.

**B4 — product amplification.** For `t` independent R6I components with a summed support budget, certificate budget is exactly `5t` and intrinsic budget is exactly `t`.

The generic zero-sum facts, finite-field dependence, direct sums and support sparsity are donor mathematics. The candidate contribution is the exact production-compiler realization and the proof-language/object separation.

## 2. Three quantities that should not be conflated

Fix a compiler family `F` and objective `C`.

### 2.1 Intrinsic support

Let `kappa(F,C)` be the least integer `k` such that every admitted instance has an exact optimum with structural support at most `k`, with a matching lower witness showing `k-1` does not suffice.

### 2.2 A normalization ceiling

A named semantics-preserving transformation `N` may prove that every configuration can be mapped to support at most `B_N` at no larger cost. `B_N` belongs to the pair `(compiler, normalization proof)` unless separately shown to be tight.

### 2.3 Proof-system certificate complexity

A proof system `P` specifies what information a certificate can inspect and which reductions it may perform. Let `beta_P(F,C)` be the least uniform support budget that `P` can certify for every instance in its encoded scope. A sound proof system satisfies

`kappa(F,C) <= beta_P(F,C)`,

but equality is not automatic.

Paper A gives an example of a useful normalization ceiling based on realized constraint rank. Here we ask when the rank-only version of that idea is itself maximally expressive.

## 3. Rank-only zero-sum deletion

Let `A` be a production alphabet contained in `F_2^d`. A certificate sees a finite word

`v_1,...,v_w in A`

with nonzero total XOR. Its only legal reduction is to delete a nonempty proper subsequence whose XOR is zero. The certificate is terminal when no such deletion is available.

The nonzero-total condition matters: if the whole word XOR were zero, the full word itself would be a zero-sum set but deleting it would not leave a valid nontrivial certificate for the compiler relation being represented.

**Theorem 1 (exact rank-only certificate complexity).** Suppose `A` spans `F_2^d` and contains a basis. Then the exact maximum terminal word length of the rank-only deletion proof system is `d`.

**Upper bound.** Any word of length greater than `d` is linearly dependent. Therefore some nonempty subset XORs to zero. Since the total word XOR is nonzero, that subset cannot be the whole word and is a legal deletion. Repeating reduces every certificate to length at most `d`.

**Lower bound.** Let `e_1,...,e_d` be a basis contained in `A`. The basis word has nonzero total and no nonempty zero-XOR subset. It is therefore terminal at length `d`. ∎

This is elementary finite-field/zero-sum mathematics. Its role here is to identify exactly what the proof system measures.

### 3.1 Machine corroboration

The publication verifier exhausts dimensions `d=1,2,3`: every nonzero-total word of length `d+1` has a proper zero-XOR subsequence, while every standard basis is zero-sum-free. The all-`d` authority is the proof above.

## 4. Tight control: R6M

In the one-Tag R6M setting, a frame coordinate carries two binary constraints: partner anticommutation and the shared Tag relation. Paper A's signature realization shows that the two-bit signature space is genuinely realized and contains a basis. The rank-only deletion language therefore has

`beta_rank-only(R6M)=2`.

Independently, the R6M all-size upper theorem and an exact support-one obstruction establish

`kappa_R6M=2`.

Hence

`beta_rank-only(R6M)=kappa_R6M=2`.

This control is important: the rank certificate is not inherently loose. Under a grammar whose intrinsic obstruction is already visible to the signature language, it can be exact both as a certificate and as a compiler invariant.

## 5. Separation case: R6I

R6I contains two rank-2 dependent-triple blocks coupled by a shared two-bit Tag. Its production block-deletion signatures span a five-dimensional quotient. The production alphabets contain the analytic basis words identified by the QG6 calculation. Each basis word has nonzero total and no nonempty zero-XOR subset.

Theorem 1 therefore gives

`beta_rank-only(R6I)=5`.

A different theorem subsequently changes the proof language. It first localizes each rank-2 block to one anticommuting core, then permits whole-system Tag relocation/reconstruction instead of preserving the old column-wise Tag representation. That normalization proves every exact optimum has support at most one, while support zero is infeasible. Thus

`kappa_R6I=1`.

Combining the independently proved statements gives the exact separation

`beta_rank-only(R6I) - kappa_R6I = 4`.

### 5.1 Why there is no contradiction

The basis word blocks only a zero-XOR deletion in the frozen five-bit signature language. The support-one proof does not discover a hidden zero-XOR subset. It performs a transformation the certificate language forbids: it changes auxiliary Tag structure globally after block localization.

The lower bound is therefore a lower bound on the **certificate language**, not on the compiler family.

## 6. Direct-product amplification

Take `t>=1` independent R6I components on disjoint coordinate sets. The registered product objective and support budget add by component, and no cross-component transformation is admitted in this product family.

**Theorem 2 (product gap).** In this product family,

`beta_rank-only = 5t`,

whereas

`kappa = t`.

**Proof.** The upper bounds add componentwise. For the certificate lower bound, take a length-five basis word independently in each component; legal deletions cannot reduce the registered sum below five per component. For the intrinsic lower bound, each component requires nonzero support, while the support-one normalization applies independently to each component. ∎

Therefore the additive gap is exactly

`4t`.

If a direct enumerator's polynomial degree is identified with its certified support budget for a fixed local alphabet, the registered product has degree `5t` under the rank-only certificate and degree `t` at intrinsic support. This is an enumeration-model statement, not a complexity-class lower bound.

## 7. Relation to prior work

Sparse optimal solutions are a mature topic in integer optimization. Aliev et al. give objective-independent support bounds for integer optimal solutions and nearly matching asymptotic lower bounds. The present work neither introduces sparse support nor claims a general optimization theorem of that breadth.

The zero-sum portion is likewise classical. For elementary 2-groups, the Davenport constant gives the familiar `d+1` threshold, and a basis is the canonical zero-sum-free word of length `d`. Direct sums and finite-field linear dependence are donor mathematics.

The proof-complexity reading is also conceptually standard: a lower bound for one proof system does not imply that the underlying statement is intrinsically difficult in a stronger system. The residual contribution is the **exact production quantum-compilation realization**: the same rank-only certificate schema is tight in R6M, strictly loose by a factor five in R6I, and unboundedly loose in additive gap under registered products.

Recent verified and global-symplectic quantum compilers reinforce the practical relevance of proof-language choice. They also limit the scope of our claim: global compiler transformations are an active donor idea, not an ORION invention.

## 8. Reproducibility

The R6I rank-five production result is bound to the committed Paper B B1 source, independent generic verifier, native campaign and dual receipt. The R6I intrinsic support-one theorem is a separately protected parent. The R6M intrinsic support-two result is separately bound through Paper A's parent ledger.

`papers/verify_five_theory_upgrades.py` independently checks the finite-field upper/lower mechanism on every nonzero-total word through dimension three and verifies the frozen compiler terminals. Finite enumeration corroborates rather than replaces Theorem 1.

## 9. Limitations

1. The lower bound applies to the explicitly defined rank-only zero-XOR deletion language.
2. It is not a lower bound for every local proof system, every syndrome-preserving proof system, or unrestricted formal verification.
3. In particular, the result establishes no unrestricted proof-system lower bound.
4. The direct product amplifies the same mechanism; it is not a second independent compiler mechanism.
5. The polynomial-degree comparison belongs to a direct support enumerator, not to arbitrary algorithms.
6. Structural support is not a physical T count, runtime or qubit advantage.
7. External replication and fresh submission-date novelty review remain open.

## 10. Discussion

A useful certificate should be judged on two axes. The first is soundness: does it safely bound the search? The second is semantic tightness: does its number describe the object or only the language in which the certificate is written?

R6M and R6I show that the answers can differ under the same algebraic proof pattern. In R6M, the rank-two certificate happens to coincide with an intrinsic support-two obstruction. In R6I, the rank-five basis genuinely prevents any further deletion in the certificate language, yet a global reconstruction reduces the actual compiler to support one. The rank is therefore not wrong. It is correctly measuring the wrong layer for an intrinsic interpretation.

This distinction suggests a practical reporting rule for exact compiler papers: when presenting a support bound, state whether it is (i) an intrinsic support number with a matching lower witness, (ii) a normalization ceiling, or (iii) a certificate-complexity bound for a named proof system. A lower number discovered by a stronger transformation then becomes an interpretable proof-language advance rather than an apparent contradiction.

## 11. Conclusion

Rank-only zero-sum deletion has an exact and simple certificate complexity: dimension. That fact can be tight for a compiler, as in R6M, or sharply loose, as in R6I. The R6I separation `5 versus 1` and its `5t versus t` product amplification demonstrate that a proof-system bound can be mathematically optimal within its language while remaining arbitrarily far away in additive terms from intrinsic compiler support. Constraint rank is therefore a certificate invariant unless a separate lower witness proves it belongs to the compiler itself.

## Selected references

- I. Aliev, J. A. De Loera, F. Eisenbrand, T. Oertel and R. Weismantel, _The Support of Integer Optimal Solutions_, SIAM J. Optim. 28, 2152–2157 (2018), DOI 10.1137/17M1162792.
- M. Freeze and W. A. Schmid, _Remarks on a generalization of the Davenport constant_, Discrete Math. 310, 3373–3389 (2010), arXiv:0905.4248. [Background zero-sum terminology; not a claim that their generalized constants equal the restricted compiler certificate.]
- L. Li et al., _A Verified Compiler for Quantum Simulation_, arXiv:2509.18583 (2025).
- Z. Yang et al., _Efficient Compilation for Hamiltonian Simulation via Global Binary Symplectic Form Simplification_, arXiv:2608.11579 (2026).

---

## Publication decision record

**Primary target posture:** `Quantum` original research, because the current criterion rewards a very significant narrow technical/conceptual advance without requiring broad interdisciplinary scope.  
**Stretch:** `PRX Quantum` only if external experts endorse the compiler/proof-complexity connection as an exceptional cross-area insight.  
**Internal status:** `STRONG_SPECIALIST_SUBMISSION_CANDIDATE__EXACT_TWO_FAMILY_TIGHT_VS_LOOSE_CONTROL`.  
**Remaining pre-submission blockers:** primary-source review of the closest proof-language/normal-form literature; external proof audit; final figures; exact venue formatting and archive.
