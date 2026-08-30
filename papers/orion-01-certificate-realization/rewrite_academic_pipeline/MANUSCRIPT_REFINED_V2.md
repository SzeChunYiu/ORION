# Alphabet-Sensitive Zero-Sum Normal Forms for Multi-Tag Quantum Compilation

## Abstract

Auxiliary Pauli frames enlarge a compilation grammar, but an optimum need not use all of the apparent support. We give a conditional deletion theorem that identifies the exact combinatorial quantity controlling this reduction. Let active coordinates of a constrained generator carry signatures from an alphabet \(A\) in a finite abelian group \(H\), and let \(zsf(H;A)\) denote the largest length of a word over \(A\) with no nonempty zero-sum subsequence. If deleting any zero-sum subsequence preserves the represented compiler semantics and does not increase the declared objective, then every admitted instance has an exact optimum whose support is at most \(zsf(H;A)\).

For binary signatures the alphabet-sensitive statement simplifies further than an ambient-rank bound. A zero-sum-free word over \(\mathbb F_2^d\) is exactly a linearly independent sequence, so
\[
zsf(\mathbb F_2^d;A)=\operatorname{rank}(\operatorname{span}A).
\]
The effective rank of the realized signature alphabet, rather than the ambient syndrome dimension, is therefore the exact binary certificate ceiling.

We instantiate the theorem for an arbitrary-block MultiTag-TARE grammar. With \(b\ge2\) ordered blocks, minimum frame-support coefficient \(\mu\), and Restore coefficient \(t_R\), changing one local Restore letter increases the \(b\)-way Restore functional by at most \(b-1\), and this bound is attained. Consequently, throughout the objective cone \(\mu\ge(b-1)t_R\), every frame has an exact optimum with
\[
\operatorname{supp}(R)\le
\operatorname{rank}(\operatorname{span}A_R)\le s+1,
\]
where \(s\) is the number of shared Tags. A one-Tag, three-block control has an independent lower witness and is intrinsically sharp at support two. The result is a compiler-specific normal-form theorem, not a claim of physical quantum advantage or general multi-Tag sharpness.

## 1. Introduction

Compiler representations often gain flexibility by admitting auxiliary objects that appear to scale with problem size. This flexibility can improve optimization, but it also obscures a basic structural question: how much auxiliary support can an exact optimum actually require?

A familiar answer attaches a finite binary signature to each active coordinate. Once the support exceeds the signature dimension, linear dependence identifies a subset whose signatures cancel. If that subset can be removed without changing the represented operation or increasing cost, support can be reduced. This reasoning is often described as a rank argument. Rank, however, is only the binary specialization of the object used by the deletion proof. The proof needs a zero-sum subsequence in the alphabet that the grammar actually realizes.

This paper separates the three obligations that are otherwise compressed into one slogan:

1. a combinatorial zero-sum statement over the realized alphabet;
2. a compiler-semantic statement that zero-sum deletion preserves feasibility;
3. an objective statement that the deletion is non-increasing.

The separation matters because the obligations have different scopes. The zero-sum invariant is general finite-group combinatorics. Semantic preservation is grammar-specific. Objective dominance can hold only in a declared coefficient cone. A support ceiling becomes intrinsic compiler complexity only after a separate lower witness shows that smaller support cannot always suffice.

## 2. Alphabet-sensitive zero-sum support

Let \(H\) be a finite abelian group written additively and \(A\subseteq H\) a finite allowed signature alphabet. A word
\[
W=(a_1,\ldots,a_m),\qquad a_i\in A,
\]
is zero-sum-free when no nonempty subsequence of positions has sum zero. Define
\[
zsf(H;A)=\max\{|W|: W \text{ is zero-sum-free over }A\}.
\]

Coordinates may repeat, and a removable subsequence need not be contiguous. The definition is chosen to match the compiler operation: deletion acts on an arbitrary selected set of active coordinates.

When \(A=H\setminus\{0\}\), this quantity is the classical Davenport ceiling minus one. A restricted alphabet can have a smaller value because it may span only a proper subgroup or omit configurations that realize the ambient extremum. The relevant compiler certificate is therefore indexed by \(A\), not only by \(H\).

## 3. Conditional deletion theorem

Consider an optimization grammar in which each constrained generator \(R\) has active coordinates carrying signatures
\[
v_q\in A_R\subseteq H_R.
\]
Assume:

1. the total signature of every feasible constrained generator is nonzero;
2. deleting any nonempty zero-sum subsequence preserves all semantic constraints represented by the signature map;
3. the same deletion does not increase the declared objective.

**Theorem 1 (alphabet-sensitive normal form).** Every admitted instance has an exact optimum satisfying
\[
\operatorname{supp}(R)\le zsf(H_R;A_R)
\]
for every constrained generator \(R\).

**Proof.** Start from an optimum. If the signature word of \(R\) is longer than \(zsf(H_R;A_R)\), it contains a nonempty zero-sum subsequence. The total signature is nonzero, so that subsequence is not the whole generator. Delete it. Assumption 2 preserves feasibility and Assumption 3 does not increase cost. Support strictly decreases. Repeating the operation terminates at support at most \(zsf(H_R;A_R)\). Applying the same argument to each constrained generator yields an equally good optimum in the claimed normal form. \(\square\)

The theorem is intentionally conditional. It does not infer semantic deletion from the group structure. The compiler-specific proof must establish why cancellation in the signature language corresponds to a valid transformation of the represented program.

## 4. Exact binary specialization

Let \(H=\mathbb F_2^d\). In characteristic two, a zero-sum subsequence is exactly a linearly dependent selected sequence.

**Proposition 2 (effective-rank identity).**
\[
zsf(\mathbb F_2^d;A)=\operatorname{rank}(\operatorname{span}A).
\]

**Proof.** Any zero-sum-free word contains no repeated nonzero element and is linearly independent, so its length is at most the rank of \(\operatorname{span}A\). Conversely, a basis extracted from \(A\) is a zero-sum-free word of that length. The zero element, if present in \(A\), cannot appear in a zero-sum-free word and does not affect the span. \(\square\)

This identity corrects a common over-broad formulation. The binary result is not merely
\[
zsf(\mathbb F_2^d;A)\le d
\]
with equality only when \(A\) contains an ambient basis. The exact value is the rank of the subgroup realized by the alphabet. Ambient rank remains a valid final ceiling, but it can be loose.

The identity also sharpens the distinction between certificate complexity and intrinsic compiler complexity. Effective signature rank gives the exact ceiling of this deletion proof. A lower witness is still required before that ceiling can be called necessary support.

## 5. MultiTag-TARE grammar

Consider \(b\ge2\) ordered two-target blocks and \(s\ge0\) shared Tag Paulis. Each frame Pauli \(R\) has an anticommuting partner \(R'\). At an active coordinate \(q\), define the binary signature
\[
v_q=
\bigl(
\langle R_q,R'_q\rangle,
\langle S_{1q},R_q\rangle,\ldots,
\langle S_{sq},R_q\rangle
\bigr)
\in\mathbb F_2^{s+1}.
\]

The first coordinate records partner anticommutation; the remaining coordinates record shared-Tag labels. The total first coordinate is one, so the total signature is nonzero. Deleting a zero-XOR subset preserves partner anticommutation and all shared-Tag labels. These facts discharge the semantic part of Theorem 1 for the declared grammar.

The remaining question is whether the deletion can increase objective cost.

## 6. Tight local Restore sensitivity

Let the local \(b\)-way Restore functional equal one when all \(b\) local letters are the same nonidentity Pauli and otherwise equal the number of nonidentity letters.

**Lemma 3 (Restore sensitivity).** Changing one local letter can increase the Restore functional by at most \(b-1\), and the bound is attained.

Away from the all-equal discounted state, changing one letter changes ordinary nonidentity support by at most one. Leaving the all-equal nonidentity state can move the functional from one to \(b\), which gives the exact increase \(b-1\).

Suppose one deleted frame coordinate refunds at least \(\mu\), while Restore cost is multiplied by \(t_R\ge0\). The worst possible Restore penalty is \((b-1)t_R\). Deletion is therefore non-increasing whenever
\[
\mu\ge(b-1)t_R.
\]

This coefficient inequality is not a technical afterthought. It is the objective boundary under which the semantic deletion becomes an optimization theorem.

## 7. MultiTag normal form

Combining Theorem 1, Proposition 2, and Lemma 3 gives the compiler result.

**Theorem 4 (MultiTag normal form).** Throughout the cone
\[
\mu\ge(b-1)t_R,
\]
every admitted MultiTag-TARE instance has an exact optimum satisfying
\[
\operatorname{supp}(R)
\le zsf(H_R;A_R)
=\operatorname{rank}(\operatorname{span}A_R)
\le s+1
\]
for every frame \(R\).

The first equality is specific to the binary signature group. The effective-rank term can be strictly smaller than \(s+1\) when the realized alphabet spans a proper subspace. The theorem therefore adapts to the grammar's actual signature language rather than assigning every instance the ambient ceiling.

No necessity statement follows from the theorem alone. It proves that an optimum exists inside the normal form, not that every smaller normal form fails.

## 8. Sharp one-Tag control

In the one-Tag, three-block specialization, the realized signature alphabet spans \(\mathbb F_2^2\), so the effective-rank ceiling is two. Independent all-size upper evidence and an exact lower witness show that support one is not uniformly sufficient. The intrinsic support number is therefore exactly two.

This control illustrates the required two-sided argument. The deletion theorem establishes sufficiency; the lower witness establishes necessity. General multi-Tag instances currently have only the sufficiency result and may admit smaller exact normal forms.

## 9. Donor boundary and scientific scope

Zero-sum theory, linear dependence, Pauli and symplectic representations, sparse optimal solutions, and TARE-derived compiler grammars supply the donor concepts. The paper does not claim those primitives.

The residual contribution is their exact compiler-specific composition: a signature map whose cancellation preserves MultiTag semantics, a tight arbitrary-block Restore sensitivity law, an explicit objective cone, and a normal form indexed by the effective realized alphabet. The one-Tag control then identifies the special case in which the certificate ceiling is also intrinsic support.

Analytic proof carries the all-size claims. Finite enumerators and independent implementations are defect-detection tools for local identities, boundary cases, and transcription. Internal independent implementations are not external replication.

## 10. Limitations

The theorem applies only when the declared signature map is semantically complete for the deletion and the objective lies in the proof-validity cone. Outside
\[
\mu\ge(b-1)t_R,
\]
the argument supplies no support ceiling. Computing \(zsf(H;A)\) can be difficult for nonbinary groups. General multi-Tag sharpness remains open.

Auxiliary Pauli support is also not a complete physical resource measure. The result does not establish a reduction in fault-tolerant gate count, circuit depth, qubit overhead, wall-clock compilation time, or end-to-end quantum advantage.

## 11. Conclusion

The correct combinatorial certificate for support deletion is the zero-sum-free length of the signature alphabet actually realized by the compiler. In binary signature systems, that quantity equals the rank of the alphabet's span, not merely an ambient-rank upper bound. MultiTag-TARE supplies the semantic and objective conditions needed to turn the certificate into an exact normal form: zero-signature deletion preserves the grammar, and the tight \(b-1\) Restore sensitivity identifies the coefficient cone in which deletion cannot hurt. The result makes explicit where finite-group combinatorics ends, where compiler semantics begins, and when a sufficient certificate becomes intrinsic complexity.
