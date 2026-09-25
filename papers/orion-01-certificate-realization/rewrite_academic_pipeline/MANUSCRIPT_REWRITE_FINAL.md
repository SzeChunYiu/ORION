# Alphabet-Sensitive Zero-Sum Normal Forms for Multi-Tag Quantum Compilation

**ORION-01 — recursive academic-paper-pipeline final editorial master**  
**Scientific cut:** compiler-specific normal-form theorem with an alphabet-sensitive zero-sum certificate  
**Primary route:** Quantum / theory-oriented quantum-information journal  
**Specialist fallback:** Theoretical Computer Science  
**Authority:** `BOUNDED_PAPER_RETAINED__THEORY_OR_EXACT_COMPUTE_ROUTE__SUBMISSION_PACKAGE_OPEN`

## Abstract

Exact quantum-compilation grammars can expose auxiliary Pauli representations whose apparent support grows with system size even when an optimum never needs that freedom. We identify an alphabet-sensitive zero-sum invariant that controls when support can be removed without changing the represented constraints or increasing cost. Let a constrained generator carry local signatures in a finite alphabet `A` contained in a finite abelian group `H`, and let `zsf(H;A)` be the maximum length of a word over `A` containing no nonempty zero-sum subsequence. Whenever zero-signature deletion preserves the compiler semantics and is non-increasing for the declared objective, every admitted instance has an exact optimum with generator support at most `zsf(H;A)`.

For elementary binary signature groups this yields the familiar rank ceiling, `zsf(F_2^d;A) <= d`, with equality when the realised alphabet contains a basis. We instantiate the theorem for an arbitrary-block MultiTag-TARE grammar. With `b>=2` ordered blocks, minimum frame-support coefficient `mu`, and Restore coefficient `t_R`, changing one local Restore letter increases the `b`-way Restore functional by at most `b-1`, and that bound is tight. Hence throughout the objective cone

`mu >= (b-1)t_R`,

every frame has an exact optimum satisfying

`support(R) <= zsf(H_R;A_R) <= rank(H_R) <= s+1`,

where `s` is the number of shared Tags. The first inequality is alphabet-sensitive; the later inequalities are convenient binary ceilings. In the one-Tag, three-block specialization, independent all-size upper and exact lower evidence establish the intrinsic sharp value two. We do not claim sharpness for general MultiTag instances or outside the proof-validity cone.

The contribution is a compiler-specific normal-form theorem that separates three objects often collapsed into one number: the combinatorial certificate language, the objective-dependent deletion law, and the intrinsic support complexity of the compiler. The abstract zero-sum invariant is donor-owned; the residual lies in its semantic binding to MultiTag-TARE, the exact Restore accounting, and the sharp control case.

## 1. Introduction

Expressive compilation systems often trade a smaller immediate representation for a larger optimization space. Auxiliary Pauli frames illustrate the tension. They can expose global algebraic structure that reduces a coupled objective, yet permitting arbitrary support appears to create a family whose structural complexity grows with the number of qubits.

The relevant scientific question is not simply whether an exact optimizer can search that family. It is whether an optimum admits a **normal form** whose support is bounded independently of system size.

A common proof strategy assigns a finite binary syndrome to each active coordinate. Once support exceeds the syndrome dimension, a linear dependence identifies coordinates whose aggregate syndrome vanishes. If deleting those coordinates preserves feasibility and does not increase cost, the support can be reduced. This reasoning is often summarized as a rank bound.

Ambient rank is not the primitive combinatorial object. The proof only needs the following property of the signatures that the compiler can actually realise: every sufficiently long word over that realised alphabet contains a removable zero-sum subsequence. A restricted alphabet can therefore yield a tighter ceiling than the ambient group rank, and the same reasoning can extend beyond elementary binary groups.

This observation leads to an alphabet-sensitive normal form. The paper contributes:

1. a general zero-sum deletion theorem indexed by the realised signature alphabet;
2. binary rank as a corollary rather than the foundational invariant;
3. an exact local Restore-sensitivity lemma for arbitrary-block MultiTag-TARE;
4. an explicit objective cone in which the deletion is non-increasing;
5. a sharp one-Tag control that distinguishes a proof ceiling from intrinsic compiler support.

The theorem is conditional by design. A combinatorial zero-sum relation does not itself license deletion. The compiler-specific work is to prove that the signature contains every load-bearing semantic constraint and that the declared objective cannot increase under the edit.

## 2. Alphabet-sensitive zero-sum support

Let `H` be a finite abelian group written additively, and let `A` be a finite allowed alphabet contained in `H`. A word

`W=(a_1,...,a_m)`

over `A` is **zero-sum-free** when no nonempty subsequence of positions has group sum zero. Define

`zsf(H;A) = max{|W| : W is zero-sum-free over A}`.

The subsequence is a selected set of positions and need not be contiguous. Repetitions are permitted. These conventions are stated explicitly because nearby zero-sum invariants use different alphabets, weights and sequence notions.

When `A=H\{0}`, `zsf(H;A)` is the classical Davenport ceiling minus one. For a proper realised alphabet, it can be smaller. That distinction matters for compilation: a grammar can live in a large ambient syndrome group while realising only a restricted set of local signatures.

## 3. General deletion theorem

Consider an optimization grammar in which every constrained generator `R` has active coordinates carrying signatures

`v_q in A_R subseteq H_R`.

Assume:

1. the total signature of every feasible constrained generator is nonzero;
2. deleting any nonempty zero-sum subsequence preserves every compiler constraint represented by the signature map;
3. the same deletion does not increase the declared objective.

### Theorem 1 — alphabet-sensitive normal form

Every admitted instance has an exact optimum in which

`support(R) <= zsf(H_R;A_R)`

for every constrained generator `R`.

**Proof.** Start from an exact optimum. If the signature word of `R` is longer than `zsf(H_R;A_R)`, it contains a nonempty zero-sum subsequence. Because the total signature is nonzero, that subsequence cannot be the entire generator. Delete the selected coordinates. Assumption 2 preserves feasibility, Assumption 3 preserves or improves the objective, and support strictly decreases. Repetition terminates at the stated bound. Applying the same descent to every constrained generator produces an equally good optimum in normal form. ∎

The theorem separates the proof into three auditable obligations:

- a combinatorial zero-sum guarantee;
- a semantic statement about what the signature preserves;
- an objective statement about the cost of deletion.

Failure of any obligation blocks the normal-form conclusion.

## 4. Binary rank as a corollary

Let `H=F_2^d`. Any word longer than `d` is linearly dependent and therefore contains a nonempty zero-XOR subsequence. Hence

`zsf(F_2^d;A) <= d`.

If the realised alphabet contains a basis, the word listing the basis elements once is zero-sum-free, and equality holds.

This corollary clarifies two different meanings of “support complexity.” A rank-`d` deletion proof supplies an exact upper bound under its assumptions. It becomes an intrinsic compiler support number only when a separate lower witness shows that support below `d` is sometimes insufficient. Without that witness, `d` can be a property of the proof language rather than the smallest support an optimum genuinely needs.

## 5. MultiTag-TARE grammar

We now instantiate the theorem in a MultiTag-TARE family with `b>=2` ordered two-target blocks and `s>=0` shared Tag Paulis. Each frame Pauli `R` has an anticommuting partner `R'`.

At every active coordinate `q`, define the binary signature

`v_q = (<R_q,R'_q>, <S_1q,R_q>, ..., <S_sq,R_q>) in F_2^{s+1}`,

where the brackets denote the local symplectic contribution. The XOR of the first components is one because `R` and `R'` anticommute, so the total signature is nonzero. Deleting a zero-signature subsequence preserves partner anticommutation and every shared-Tag relation represented by the remaining components.

The remaining scientific obligation is objective dominance.

## 6. Exact Restore sensitivity

Let the minimum objective coefficient charged for one active frame coordinate be `mu`. Let `t_R>=0` multiply the local `b`-way Restore functional. The registered local Restore rule equals one when all `b` local letters are the same nonidentity Pauli and otherwise equals the number of nonidentity letters.

### Lemma 2 — tight one-letter sensitivity

Changing one argument of the local `b`-way Restore functional increases its value by at most `b-1`, and the bound is attained.

Away from the discounted all-equal configuration, changing one local letter alters ordinary support by at most one and may create a discount. Leaving an all-equal nonidentity configuration changes the local contribution from one to at most `b`, giving the exact worst-case increase `b-1`. ∎

Deleting one frame coordinate refunds at least `mu` and can increase Restore cost by at most `(b-1)t_R`. The deletion is therefore non-increasing whenever

`mu >= (b-1)t_R`.

This inequality is an objective condition, not a universal fact about the grammar.

## 7. MultiTag normal form

Combining Theorem 1 with the semantic signature and Lemma 2 gives:

### Theorem 3 — MultiTag-TARE support normal form

Throughout the objective cone

`mu >= (b-1)t_R`,

every admitted MultiTag-TARE instance has an exact optimum satisfying

`support(R) <= zsf(H_R;A_R) <= rank(H_R) <= s+1`

for every frame `R`.

The first bound adapts to the realised alphabet. The rank and `s+1` bounds are binary-group ceilings that may be loose. The theorem is silent outside the cone. Silence means that this deletion certificate no longer proves non-increase; it does not imply that larger support is necessary.

## 8. Sharp one-Tag control

The one-Tag, three-block specialization has a two-dimensional binary signature. Its realised alphabet contains a basis, so the deletion certificate gives support at most two. Independent all-size proof establishes the upper bound, while an exhaustive support-one referee produces an exact instance whose unrestricted optimum is strictly lower than the complete support-one optimum.

Consequently, the intrinsic support number in this specialization is exactly two.

This control demonstrates the full evidentiary chain:

- the alphabet invariant supplies a candidate ceiling;
- the compiler semantics and objective make deletion valid;
- an all-size proof supplies sufficiency;
- a separate exact obstruction supplies necessity.

Only the specialization completes all four steps. The general MultiTag theorem does not claim a sharp lower bound.

## 9. What the alphabet-sensitive view adds

The reformulation has three consequences.

### 9.1 Realised language can be smaller than ambient rank

A compiler whose local signatures occupy a strict subset of `H` may have `zsf(H;A)` below `rank(H)`. Reporting only ambient rank can therefore overstate the support needed by the proof.

### 9.2 Certificate complexity and compiler complexity remain separate

Even an exact alphabet ceiling can be loose if the compiler admits whole-system transformations not represented by the deletion signature. A lower witness is still required before calling the bound intrinsic.

### 9.3 Objective validity is first-class

The same signature relation can remain semantically valid while deletion ceases to be cost-nonincreasing after the objective is reweighted. The normal form belongs to a `(grammar, objective)` pair.

## 10. Relation to prior work

The donor landscape includes TARE and related block-encoding constructions, anticommuting-unitary partitioning, Pauli and binary-symplectic compilation, sparse-optimum theorems and zero-sum theory in finite abelian groups. The paper does not claim the Davenport invariant, linear dependence, Pauli support reduction or the generic idea of a sparse normal form.

The residual is their compiler-specific conjunction: a MultiTag semantic signature, a tight arbitrary-block Restore bound, an explicit proof-validity cone, an alphabet-sensitive exact normal form and a separately sharp one-Tag control. The claim concerns when an optimum can be represented without high-support auxiliary frames, not the physical cost of arbitrary quantum computation.

## 11. Verification and reproducibility

The all-size authority lies in the analytic proofs. A structurally separate standard-library checker exercises the theorem statements, local Restore bound, boundary cases and sharp control without importing production ORION or PyZX code. These checks improve defect detection but do not replace the proof or create external replication.

The release should bind:

- the formal MultiTag grammar and objective;
- the signature map and realised alphabet definition;
- proofs of Theorems 1 and 3 and Lemma 2;
- the sharp one-Tag lower witness and complete support-one referee;
- the independent checker and planted failure controls;
- the novelty and proof-repair dispositions;
- an exact source/PDF/archive manifest.

## 12. Limitations

The theorem requires zero-signature deletion to preserve all relevant semantics and satisfy the objective inequality. Computing `zsf(H;A)` can be nontrivial for a general alphabet. General MultiTag sharpness is open. Outside `mu >= (b-1)t_R`, the present proof supplies no conclusion.

Auxiliary frame support is not a complete physical resource metric. No claim is made about fault-tolerant `T` count, depth, qubit overhead, end-to-end compiler runtime or quantum advantage. The source-complete production successor is a separate frozen study and contributes no outcome to this bounded paper.

## 13. Conclusion

The natural support certificate for an exact compiler is not always its ambient syndrome rank. It is the longest zero-sum-free word that can be formed from the signatures the compiler actually realises. When zero-sum deletion preserves semantics and is non-increasing, that alphabet invariant yields an exact normal form; binary rank follows as a useful ceiling.

In MultiTag-TARE, the number of blocks controls deletion cost through the tight `(b-1)` Restore penalty, the shared Tags control ambient signature dimension, and the realised alphabet controls the sharper sufficient support. The one-Tag control shows how an upper certificate becomes an intrinsic support theorem when paired with a separate exact obstruction. This separation makes the normal form auditable and prevents proof-language complexity from being mistaken for universal compiler complexity.

---

## Editorial production note — not manuscript prose

This master consolidates the repaired bounded V3 theory package. Before adoption, reconcile it with `v3-bounded-closeout-2026-08-29/theory-A-MANUSCRIPT_V3.md`, `theory-B-MANUSCRIPT_V3.md`, `PROOF_REPAIR_DISPOSITION_V3.md`, `NOVELTY_AUDIT_V2.md` and `proof_checker_v3.py`. Build a single target-specific manuscript, refresh the exact primary-source literature, and regenerate the PDF, figures, manifest, archive and licence from the adopted bytes. The separate source-complete successor must remain outside this paper until it has an admissible outcome.
