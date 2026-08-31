# Alphabet-Davenport Normal Forms for Multi-Tag Quantum Compilation

## Abstract

Finite-support normal forms make exact quantum compiler optimization enumerable, but a rank bound can obscure the more general combinatorial object controlling deletion. We formulate that object for a finite abelian signature group. For an allowed signature alphabet `A subset H`, let `zsf(H;A)` be the maximum length of a sequence over `A` containing no nonempty zero-sum subsequence. Consider any compiler grammar in which active coordinates carry signatures in `A`, the total signature of each constrained generator is nonzero, and deletion of a zero-signature subword preserves feasibility without increasing the objective. We prove that every admitted instance has an exact optimum with support at most `zsf(H;A)`. The proof is an iterative proper-subword deletion; nonzero total signature prevents the removable zero-sum subword from being the whole generator. For `H=F_2^d`, `zsf(H;A)<=d`, and equality holds whenever `A` contains a basis. Thus the familiar constraint-rank normal form is a sharp corollary for the deletion language rather than the primitive theorem.

We instantiate the result in an explicit arbitrary-block MultiTag-TARE grammar. With `b>=2` ordered blocks, `s>=0` shared Tags, minimum frame coefficient `mu`, and Restore coefficient `t_R`, changing one local letter increases the `b`-way Restore functional by at most `b-1`, exactly. Hence throughout

`mu >= (b-1)t_R`,

every instance has an optimum satisfying

`support(R) <= zsf(H_R;A_R) <= rank(H_R) <= s+1`

for every frame `R`, with the middle rank inequality specialized to the elementary binary signature quotient. The one-Tag, three-block R6M specialization remains sharply intrinsic with `kappa_R6M=2`. No sharpness is claimed for multiple Tags or outside the proof-validity cone. The result reframes constraint rank as one computable instance of an alphabet-sensitive zero-sum certificate and exposes which part of the theorem belongs to compiler semantics, which to the objective, and which to the proof language.

## 1. Introduction

TARE is an upstream block-encoding construction. It exposes frame, Tag, branch, and Restore choices; this paper studies exact normal forms for those auxiliary choices and assigns no novelty to the donor primitive.

A common compiler proof attaches a finite binary syndrome to each active coordinate. If support exceeds syndrome dimension, linear dependence yields a removable zero-syndrome subset. The resulting dimension can look intrinsic, but the argument actually uses only two facts: sufficiently long signature words contain a zero-sum subword, and deleting that subword is non-increasing. This observation suggests replacing ambient rank by an alphabet-sensitive zero-sum invariant.

That replacement matters in three ways. First, it applies to finite abelian signature groups beyond elementary binary quotients. Second, even inside `F_2^d`, a restricted realized alphabet can have a smaller zero-sum-free ceiling than the ambient dimension. Third, it separates a combinatorial certificate from the objective inequality that licenses deletion.

### 1.1 Contributions

1. **Alphabet-Davenport deletion theorem.** `zsf(H;A)` is a universal support ceiling for every deletion-dominant grammar with nonzero total signature.
2. **Binary rank corollary.** For `F_2^d`, `zsf<=d`; a realized basis makes the deletion-language ceiling exactly `d`.
3. **Arbitrary-block MultiTag instantiation.** The exact local Restore sensitivity is `b-1`, giving the cone `mu>=(b-1)t_R` and an instance-adaptive realized-alphabet ceiling.
4. **Sharp one-Tag control.** R6M has intrinsic support two by independent upper and lower evidence.
5. **Boundary semantics.** The paper distinguishes alphabet ceiling, realized rank, intrinsic support, objective cone, and physical resources.

## 2. The alphabet zero-sum invariant

Let `H` be a finite abelian group written additively, and let `A subseteq H` be a finite allowed alphabet. A word over `A` is **zero-sum-free** when none of its nonempty subwords has sum zero. Define

`zsf(H;A) = max{|W| : W is a zero-sum-free word over A}`.

This is a subset/alphabet Davenport invariant. We use the explicit `zsf` notation to avoid conflating it with several established weighted, universal, or subset Davenport conventions.

For `A=H\{0}`, `zsf(H;A)=D(H)-1`. For a smaller alphabet it may be strictly lower. The invariant concerns words with repetition, matching compiler coordinates.

## 3. General deletion theorem

Fix an optimization grammar. For each constrained generator `R`, every active coordinate `q` carries a signature `v_q in A_R subseteq H_R`.

Assume:

1. **nonzero total:** `sum_q v_q != 0` for every feasible constrained generator;
2. **zero-sum deletion soundness:** setting `R` to identity on any nonempty zero-sum subword preserves all semantic constraints represented by the signatures;
3. **deletion dominance:** the same operation does not increase the objective.

**Theorem 1 (alphabet-Davenport normal form).** Every admitted instance has an exact optimum in which

`support(R) <= zsf(H_R;A_R)`

for every constrained generator `R`.

**Proof.** Start from an optimum. If the signature word of `R` is longer than `zsf(H_R;A_R)`, it contains a nonempty zero-sum subword. Because the total signature is nonzero, that subword is proper. Delete its coordinates. Soundness preserves feasibility and dominance preserves optimality. Support strictly decreases, so iteration terminates at a word of length at most `zsf(H_R;A_R)`. Repeat for every generator. ∎

The theorem is intentionally abstract but not vacuous: all compiler-specific work is concentrated in the signature map, the nonzero-total invariant, and the objective accounting needed for deletion dominance.

## 4. Rank is a binary corollary

Let `H=F_2^d`. Every word longer than `d` is linearly dependent, hence has a nonempty zero-XOR subword. Therefore

`zsf(F_2^d;A) <= d`

for every alphabet `A`. If `A` contains a basis, the basis word is zero-sum-free, so equality holds.

**Corollary 2.** In an elementary binary signature system, an ambient rank-`d` deletion theorem is exact for the deletion language whenever a basis word is allowed. It is intrinsic to the compiler only if a separate compiler lower witness establishes necessity.

This distinction is developed fully in Paper B.

## 5. MultiTag-TARE grammar

Fix `b>=2` ordered two-target blocks and `s>=0` shared Tag Paulis `S_1,...,S_s`. Each frame Pauli `R` has an anticommuting partner `R'`. At every active coordinate define the binary signature

`v_q=(<R_q,R'_q>,<S_1q,R_q>,...,<S_sq,R_q>) in F_2^(s+1)`.

The XOR of the first components is one, so total signature is nonzero.

The structural objective contains frame support charged by coefficients at least `mu`, arbitrary nonnegative Tag-support charges, and coefficient `t_R>=0` times the local `b`-way Restore functional

`F_b(a_1,...,a_b)=1`

when all letters are the same nonidentity Pauli, and otherwise the number of nonidentity letters.

## 6. Exact local Restore sensitivity

**Lemma 3.** Replacing one argument of `F_b` increases its value by at most `b-1`, and the bound is attained.

**Proof.** Away from the all-equal nonidentity state, `F_b` is ordinary nonidentity Hamming weight, so one replacement raises it by at most one. Entering the special state lowers the value to one. Leaving that state while keeping the changed letter nonidentity changes the value from one to `b`, giving the exact increase `b-1`. ∎

The additive verifier exhausts all local Pauli tuples for `b=2,...,7`; the all-`b` authority is the proof.

## 7. MultiTag normal form

Let `A_R` be the alphabet actually realized by the local partner/Tag signatures of frame `R`, and let `H_R` be its generated subgroup.

**Theorem 4.** If

`mu >= (b-1)t_R`,

then every admitted MultiTag-TARE instance has an exact optimum in which

`support(R) <= zsf(H_R;A_R) <= rank(H_R) <= s+1`

for every frame.

**Proof.** A zero-signature subword preserves partner anticommutation and every Tag label; Tags themselves remain fixed. Each deleted coordinate refunds at least `mu` in frame cost and can add at most `(b-1)t_R` in Restore cost by Lemma 3. Thus the deletion is non-increasing in the stated cone. Theorem 1 applies. Since `H_R` is an elementary binary subgroup of `F_2^(s+1)`, its zero-sum-free ceiling is at most its rank. ∎

The first inequality can be strictly stronger than realized rank when the allowed signature alphabet lacks a basis of its generated subgroup. This is the new alphabet-sensitive refinement.

## 8. Sharp R6M specialization

For the frozen one-Tag, three-block R6M grammar,

`b=3`, `s=1`, `mu=2`, `t_R=1`.

The objective sits on the cone boundary. The signature alphabet realizes a basis of `F_2^2`, so the deletion certificate ceiling is two. Independent all-size upper and exact lower results give

`kappa_R6M=2`.

Only this specialization receives an intrinsic sharpness claim.

## 9. Relation to prior work

Sparse optimal solutions, Davenport constants, subset/universal zero-sum invariants, finite-field dependence, Pauli symplectic algebra, and exact synthesis are established donor areas. Aliev et al. provide general objective-independent sparsity bounds for integer optimal solutions. Modern zero-sum work provides flexible invariant frameworks over selected sequence families and weights. These results own the general ideas of sparse optima and zero-sum thresholds.

The residual theorem is the compiler-specific conjunction: a TARE-derived semantic signature, exact arbitrary-block Restore sensitivity, an objective cone, and an alphabet-sensitive support normal form with a separately sharp R6M control.

## 10. Reproducibility

The R6M parent theorem and necessity witness are commit-bound in the A1 evidence package. The R2 verifier independently checks small finite-group alphabet controls and the complete binary rank mechanism through dimension four. The analytic proofs carry all-size authority. Internal independent implementations are not described as external replication.

## 11. Limitations

1. The abstract theorem applies only where zero-sum deletion is semantics-preserving and non-increasing.
2. `zsf(H;A)` may be hard to compute for a general alphabet.
3. The MultiTag result is scoped to the explicit grammar and objective.
4. Outside `mu>=(b-1)t_R`, the proof is silent; no larger-support necessity follows.
5. General multi-Tag sharpness is open.
6. Structural support is not physical T count, runtime, depth, qubits, or quantum advantage.
7. Author-side donor review is not an external novelty certificate.

## 12. Discussion and conclusion

The most useful support bound is not always ambient rank. The exact deletion threshold is the longest zero-sum-free word that the realized signature alphabet can express. Rank supplies a simple universal upper bound in binary quotients and becomes exact when a basis is realized. This refinement makes the proof more transferable while clarifying its ontology: `zsf` and rank first measure a certificate language; only a matching compiler witness turns them into intrinsic support.

For MultiTag-TARE, the number of blocks controls deletion profitability through the `b-1` Restore penalty, whereas the signature alphabet controls sufficient support. The one-Tag R6M case aligns both certificate and intrinsic complexity at two. Beyond that case, the paper reports a strong normal form without pretending that its ceiling is necessary.

## Selected references

- N. Schillo, A. Sturm and R. Quay, *TARE: Block Encoding Linear Combinations of Pauli Strings Without Ancilla State Preparation*, arXiv:2601.05740v4 (2026).
- I. Aliev, J. A. De Loera, F. Eisenbrand, T. Oertel and R. Weismantel, *The Support of Integer Optimal Solutions*, SIAM J. Optim. 28, 2152–2157 (2018), DOI `10.1137/17M1162792`.
- G. Wang, *The universal zero-sum invariant and weighted zero-sum for infinite abelian groups*, Commun. Algebra 53 (2025), DOI `10.1080/00927872.2024.2418017`.

## Publication decision record

**Primary target:** `Quantum`, whose current criteria require a very significant technical or conceptual contribution beyond the state of the art.
**Stretch:** `PRX Quantum` only if independent editors view the alphabet-zero-sum/compiler connection as an exceptional cross-area insight.
**R2 status:** `HIGH_SELECTIVITY_SPECIALIST_CANDIDATE__PRX_EXCEPTIONALITY_EXTERNAL`.
**External-only gates:** full donor PDF audit, independent proof replay, final figures, exact journal packaging, archive deposition.
