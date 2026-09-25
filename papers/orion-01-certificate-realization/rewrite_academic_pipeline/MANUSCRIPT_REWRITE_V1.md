# Alphabet-Sensitive Zero-Sum Normal Forms for Multi-Tag Quantum Compilation

## Abstract

Exact quantum-compilation grammars can expose auxiliary Pauli representations whose apparent support grows with system size even when an optimum never needs that freedom. We identify an alphabet-sensitive zero-sum invariant that controls when such support can be deleted without changing the represented compilation constraints or increasing cost. Let a constrained generator carry local signatures in a finite alphabet \(A\subseteq H\), where \(H\) is a finite abelian group, and let \(zsf(H;A)\) be the maximum length of a word over \(A\) containing no nonempty zero-sum subsequence. Whenever zero-signature deletion preserves the compiler semantics and is non-increasing for the declared objective, every admitted instance has an exact optimum with support at most \(zsf(H;A)\).

For elementary binary signature groups this recovers the familiar rank ceiling, \(zsf(\mathbb F_2^d;A)\le d\), with equality when the realized alphabet contains a basis. We then instantiate the theorem for an arbitrary-block MultiTag-TARE grammar. With \(b\ge2\) ordered blocks, frame-support coefficient at least \(\mu\), and Restore coefficient \(t_R\), changing one local Restore letter increases the \(b\)-way Restore functional by at most \(b-1\), and this bound is tight. Hence throughout the objective cone \(\mu\ge(b-1)t_R\), every frame admits an exact optimum satisfying

\[
\operatorname{supp}(R)\le zsf(H_R;A_R)\le \operatorname{rank}(H_R)\le s+1,
\]

where \(s\) is the number of shared Tags. In the one-Tag, three-block specialization, independent upper and lower evidence makes support two intrinsically sharp. We do not claim sharpness for general MultiTag instances or outside the proof-validity cone. The contribution is a compiler-specific normal-form theorem that separates the combinatorial certificate language, objective-dependent deletion law, and intrinsic support complexity.

## 1. Introduction

Expressive compilation schemes often trade a smaller immediate representation for a larger optimization space. Auxiliary Pauli frames are a representative case: they can encode useful global structure, but allowing arbitrary support appears to create a search space whose structural complexity grows with the number of qubits. A natural question is therefore not only how to optimize inside that space, but how much of it an exact optimum can ever require.

A common proof strategy attaches a finite binary syndrome to each active coordinate. Once support exceeds syndrome dimension, linear dependence yields a subset whose syndrome cancels; if removing that subset preserves feasibility and does not increase the objective, support can be reduced. This argument is often summarized as a rank bound. The rank, however, is not the primitive combinatorial object. The proof only requires that sufficiently long words over the *realized* signature alphabet contain a removable zero-sum subsequence.

That observation leads to an alphabet-sensitive normal form. It matters for three reasons. First, it extends beyond elementary binary groups. Second, a restricted realized alphabet can impose a stronger ceiling than ambient rank. Third, it cleanly separates a combinatorial zero-sum statement from the compiler semantics and objective inequality that make deletion scientifically valid.

The paper makes four contributions. We give a general alphabet-zero-sum deletion theorem; derive binary rank as a corollary rather than the foundational statement; prove the exact local Restore sensitivity needed to instantiate the theorem for arbitrary-block MultiTag-TARE; and retain a separately sharp one-Tag control in which the certificate ceiling is known to equal intrinsic compiler support.

## 2. Alphabet-sensitive zero-sum support

Let \(H\) be a finite abelian group written additively, and let \(A\subseteq H\) be a finite allowed alphabet. A word \(W=(a_1,\ldots,a_m)\) over \(A\) is **zero-sum-free** when no nonempty subsequence of positions has sum zero. Define

\[
zsf(H;A)=\max\{|W|:W\text{ is zero-sum-free over }A\}.
\]

The explicit notation is useful because the literature contains several related Davenport-type and weighted zero-sum conventions. Here the invariant is chosen to match the compiler object: coordinates may repeat, and removal acts on an arbitrary selected subsequence rather than necessarily on a contiguous factor.

When \(A=H\setminus\{0\}\), the quantity coincides with the classical Davenport ceiling minus one. For smaller \(A\), the value can be strictly smaller. This is precisely the feature needed for compiler normal forms: a grammar may realize only a restricted subset of the ambient signature group.

## 3. General deletion theorem

Consider an optimization grammar in which each constrained generator \(R\) has active coordinates carrying signatures \(v_q\in A_R\subseteq H_R\). Assume three properties.

1. The total signature of every feasible constrained generator is nonzero.
2. Deleting any nonempty zero-sum subsequence preserves every semantic constraint represented by the signature map.
3. The same deletion does not increase the declared objective.

**Theorem 1 (alphabet-sensitive normal form).** Every admitted instance has an exact optimum in which

\[
\operatorname{supp}(R)\le zsf(H_R;A_R)
\]

for every constrained generator \(R\).

**Proof.** Start from an optimum. If the signature word for \(R\) is longer than \(zsf(H_R;A_R)\), it contains a nonempty zero-sum subsequence. Because the total signature is nonzero, the removable subsequence cannot be the whole generator. Delete those coordinates. By the second assumption feasibility is preserved; by the third, objective value does not increase. Support strictly decreases, so repeated deletion terminates at support at most \(zsf(H_R;A_R)\). Applying the argument to every constrained generator yields an equally good optimum in the claimed normal form. ∎

The theorem is deliberately conditional. It does not say that every zero-sum signature system admits deletion; the compiler-specific scientific work is to prove the signature semantics and objective dominance that license the exchange.

## 4. Binary rank as a corollary

Let \(H=\mathbb F_2^d\). Any word longer than \(d\) is linearly dependent, hence contains a nonempty zero-XOR subsequence. Therefore

\[
zsf(\mathbb F_2^d;A)\le d.
\]

If \(A\) contains a basis, the word consisting of those basis elements is zero-sum-free, and equality follows.

This distinction prevents an important overinterpretation. A rank-\(d\) deletion theorem establishes an exact ceiling for the *proof language* when a basis is realizable; it establishes intrinsic compiler complexity only if a separate lower witness shows that support \(d\) is sometimes necessary. The normal-form certificate and the intrinsic minimum are different scientific objects.

## 5. MultiTag-TARE instantiation

We now specialize to an explicit MultiTag-TARE grammar with \(b\ge2\) ordered two-target blocks and \(s\ge0\) shared Tag Paulis. Each frame Pauli \(R\) has an anticommuting partner \(R'\). At each active coordinate define the binary signature

\[
v_q=(\langle R_q,R'_q\rangle,\langle S_{1q},R_q\rangle,\ldots,\langle S_{sq},R_q\rangle)\in\mathbb F_2^{s+1}.
\]

The XOR of the first components is one, so the total signature is nonzero. A zero-signature deletion preserves both partner anticommutation and all shared-Tag labels.

The remaining obligation is objective dominance. Let the minimum coefficient charged for one frame coordinate be \(\mu\), and let \(t_R\ge0\) multiply the local \(b\)-way Restore functional. This functional equals one when all \(b\) local letters are the same nonidentity Pauli and otherwise equals the number of nonidentity letters.

**Lemma 2 (Restore sensitivity).** Changing one argument of the local \(b\)-way Restore functional increases its value by at most \(b-1\), and the bound is attained.

Away from the all-equal discounted configuration, changing one letter changes ordinary support by at most one. Leaving the all-equal nonidentity state can change the Restore contribution from one to \(b\), giving the exact increase \(b-1\).

Each deleted frame coordinate therefore refunds at least \(\mu\) and can add at most \((b-1)t_R\) in Restore cost. Hence deletion is non-increasing whenever

\[
\mu\ge(b-1)t_R.
\]

Combining this inequality with Theorem 1 gives the main compiler result.

**Theorem 3 (MultiTag normal form).** Throughout the cone \(\mu\ge(b-1)t_R\), every admitted MultiTag-TARE instance has an exact optimum satisfying

\[
\operatorname{supp}(R)\le zsf(H_R;A_R)\le\operatorname{rank}(H_R)\le s+1
\]

for every frame \(R\).

The first bound is instance-adaptive through the realized alphabet. The last two are convenient binary-group ceilings. None is promoted to a necessity statement without an independent lower witness.

## 6. Sharp one-Tag control

The one-Tag, three-block specialization sits on the objective-cone boundary. Its realized signature alphabet contains a basis of \(\mathbb F_2^2\), giving a deletion ceiling of two. Independent all-size upper and exact lower evidence establish that support one is not uniformly sufficient. Consequently the intrinsic support number for this specialization is exactly two.

This is the only setting in the present paper for which intrinsic sharpness is claimed. General MultiTag instances may admit a smaller normal form, and the current theorem provides no necessity result outside the one-Tag control.

The sharp example is important methodologically because it shows how certificate complexity becomes compiler complexity: the upper proof supplies sufficiency, while a separate exact witness supplies necessity. Repeating the word “rank” cannot substitute for that lower-bound step.

## 7. Relation to prior work

The donor landscape includes TARE and related block-encoding constructions, Pauli and symplectic compilation, sparse optimal-solution theorems, and zero-sum theory in finite abelian groups. We do not claim the general notions of sparse optima, Davenport invariants, linear dependence, or Pauli support reduction.

The residual contribution is their compiler-specific conjunction: a TARE-derived semantic signature, a tight arbitrary-block Restore sensitivity bound, an explicit objective cone that licenses deletion, and an alphabet-sensitive exact support normal form with a separately sharp control case. The theorem therefore concerns when a specific compiler representation can be reduced *without loss of optimum*, not a generic statement that low-support quantum representations are always best.

## 8. Reproducibility and proof authority

The all-size claims are carried by analytic proofs. Finite enumerators and independent implementations are used as hostile checks on transcription, local lemmas, and boundary cases; they are not treated as substitutes for the theorem. The final publication package should expose the formal grammar, objective, signature map, proof assumptions, one-Tag lower witness, and the finite verification programs needed to reproduce the supporting checks.

The manuscript should also keep the distinction between internal independent implementations and external replication. A second implementation inside the same research programme improves defect detection but does not create independent scientific authority.

## 9. Limitations

The abstract theorem applies only when zero-sum deletion is semantics-preserving and objective-nonincreasing. Computing \(zsf(H;A)\) can itself be nontrivial for a general alphabet. The MultiTag result is tied to the declared grammar and objective, and the proof is silent outside \(\mu\ge(b-1)t_R\). No larger-support necessity follows outside that cone. General multi-Tag sharpness remains open.

Most importantly, auxiliary Pauli support is not a complete physical resource metric. The paper makes no claim about fault-tolerant \(T\)-count, depth, qubit overhead, end-to-end runtime, or quantum advantage.

## 10. Conclusion

The support ceiling in an exact compiler need not be the ambient syndrome rank. The sharper object is the longest zero-sum-free word realizable by the compiler's actual signature alphabet. When zero-sum deletion preserves semantics and is non-increasing, that alphabet invariant gives an exact normal form; binary rank follows as a convenient corollary. In MultiTag-TARE, the number of blocks controls whether deletion is profitable through the tight \((b-1)\) Restore penalty, while the realized signature alphabet controls sufficient support. The result turns a familiar rank argument into a more general, auditable normal-form theorem and makes explicit where proof-language complexity ends and intrinsic compiler complexity begins.
