# Alphabet-Davenport Normal Forms for Multi-Tag Quantum Compilation

## Abstract

Finite-support normal forms make exact quantum-compiler optimization
enumerable, but an ambient-rank bound can hide the finer combinatorial object
that controls deletion. Let \(H\) be a finite abelian signature group and
\(A\subseteq H\) an allowed alphabet. Write \(\operatorname{zsf}(H; A)\) for the
largest length of a word over \(A\) with no nonempty zero-sum subword. We prove
that every instance of a deletion-closed compiler grammar has an exact optimum
of support at most \(\operatorname{zsf}(H; A)\), provided each constrained
generator has nonzero total signature and every zero-signature deletion
preserves feasibility without increasing cost. For \(H=\mathbb F_2^d\), this
implies \(\operatorname{zsf}(H; A)\le d\), with equality whenever \(A\) contains
a basis.

We instantiate the theorem in an arbitrary-block MultiTag-TARE grammar. With
\(b\ge2\) ordered blocks, \(s\ge0\) shared Tags, minimum frame coefficient
\(\mu\), and Restore coefficient \(t_R\), changing one local letter increases
the \(b\)-way Restore functional by at most \(b-1\), and this bound is sharp.
Consequently, throughout the sufficient cone

\[
\mu\ge (b-1)t_R,
\]

every instance has an optimum satisfying

\[
|\operatorname{supp}(R)|
\le \operatorname{zsf}(H_R; A_R)
\le \operatorname{rank}(H_R)
\le s+1
\]

for every frame \(R\). The one-Tag, three-block R6M specialization is sharply
intrinsic, with \(\kappa_{\mathrm{R6M}}=2\). We make no necessity claim for
multiple Tags or outside the sufficient cone. The result separates the
alphabet-sensitive certificate, the compiler semantics that make deletion
sound, and the objective inequality that makes deletion profitable.

**Keywords:** quantum compilation; block encoding; exact normal forms; zero-sum
sequences; sparse optimization

## 1. Introduction

TARE is an upstream block-encoding construction that exposes frame, Tag,
branch, and Restore choices. The present work studies exact normal forms for
those auxiliary compiler choices; it does not claim the underlying
block-encoding primitive [1].

A standard support proof attaches a finite binary syndrome to every active
coordinate. When support exceeds the syndrome dimension, linear dependence
produces a removable zero-syndrome subset. The dimension obtained in this way
can look like an intrinsic property of the compiler, although the proof uses
only two ingredients: a sufficiently long signature word contains a zero-sum
subword, and deleting that subword is non-increasing. The primitive threshold
is therefore alphabet-sensitive rather than rank-sensitive.

This distinction matters for three reasons. First, it extends the deletion
argument from binary vector spaces to finite abelian signature groups. Second,
even in \(\mathbb F_2^d\), the alphabet realized by a compiler can have a
smaller zero-sum-free ceiling than the ambient dimension. Third, it keeps the
combinatorial certificate separate from the objective inequality that licenses
the corresponding edit.

Our contributions are:

1. an alphabet-Davenport deletion theorem for deletion-closed optimization
   grammars with persistent soundness and dominance assumptions;
2. the binary rank corollary, including exactness for the deletion language
   when a basis word is allowed;
3. an arbitrary-block MultiTag-TARE instantiation with exact local Restore
   sensitivity \(b-1\) and sufficient cone \(\mu\ge(b-1)t_R\);
4. a sharp frozen R6M control with intrinsic support two; and
5. an explicit boundary between certificate support, intrinsic support, and
   physical resource claims.

## 2. An alphabet-restricted zero-sum invariant

Let \(H\) be a finite abelian group written additively, and let
\(A\subseteq H\) be finite. A word over \(A\) is *zero-sum-free* if none of its
nonempty subwords has sum zero. Define

\[
\operatorname{zsf}(H; A)
=\max\{|W|:W\text{ is a zero-sum-free word over }A\}.
\]

Words permit repetition, matching the multiplicity of compiler coordinates.
For \(A=H\setminus\{0\}\), the invariant equals \(D(H)-1\), where \(D(H)\) is
the classical Davenport constant. Smaller alphabets can yield strictly smaller
values. We use explicit notation to avoid conflating this quantity with other
weighted or restricted zero-sum conventions.

## 3. The deletion theorem

Fix an optimization grammar. For each constrained generator \(R\), every active
coordinate \(q\) carries a signature
\(v_q\in A_R\subseteq H_R\). Assume the following conditions hold initially
and after every admitted deletion:

1. **Nonzero total.** Every feasible constrained generator satisfies
   \(\sum_q v_q\ne0\).
2. **Deletion closure and soundness.** Replacing \(R\) by the identity on any
   nonempty zero-sum subword remains inside the admitted grammar and preserves
   every semantic constraint represented by the signatures.
3. **Persistent deletion dominance.** The same operation does not increase the
   objective.

**Theorem 1 (alphabet-Davenport normal form).** Every admitted instance has an
exact optimum for which

\[
|\operatorname{supp}(R)|\le \operatorname{zsf}(H_R; A_R)
\]

for every constrained generator \(R\).

**Proof.** Begin with an optimum. If the signature word of \(R\) is longer than
\(\operatorname{zsf}(H_R; A_R)\), it contains a nonempty zero-sum subword. The
nonzero total prevents that subword from being the whole word. Delete its
coordinates. Closure and soundness preserve feasibility, while dominance
preserves optimality. Support strictly decreases. Because all three assumptions
persist, the process terminates with support at most
\(\operatorname{zsf}(H_R; A_R)\). Repeating the argument for each constrained
generator gives a simultaneous normal form. ∎

The abstract statement localizes the compiler-specific burden: one must define
the signature map, prove nonzero total and deletion closure, and account for the
objective change. The zero-sum threshold alone supplies none of those facts.

## 4. Binary rank as a corollary

Let \(H=\mathbb F_2^d\). Every word longer than \(d\) is linearly dependent and
therefore contains a nonempty zero-XOR subword. Hence

\[
\operatorname{zsf}(\mathbb F_2^d; A)\le d
\]

for every \(A\subseteq\mathbb F_2^d\). If \(A\) contains a basis, the basis
word is zero-sum-free, so equality holds.

**Corollary 2.** A rank-\(d\) deletion bound in an elementary binary signature
system is exact for the stated deletion language when a basis word is allowed.
It becomes an intrinsic compiler lower bound only when an independent compiler
witness proves that support below \(d\) is impossible.

## 5. MultiTag-TARE grammar

Fix \(b\ge2\) ordered two-target blocks and \(s\ge0\) shared Tag Paulis
\(S_1, \ldots, S_s\). Each frame Pauli \(R\) has an anticommuting partner \(R'\).
At every active coordinate, define

\[
v_q=\bigl(\langle R_q, R'_q\rangle,
\langle S_{1q}, R_q\rangle, \ldots,
\langle S_{sq}, R_q\rangle\bigr)
\in\mathbb F_2^{s+1},
\]

where \(\langle\cdot, \cdot\rangle\) is the local symplectic commutation form.
The XOR of the first components is one, so the total signature is nonzero.

The structural objective charges every active frame coordinate by a coefficient
of at least \(\mu\), permits arbitrary nonnegative Tag-support charges, and
adds \(t_R\ge0\) times the local Restore functional

\[
F_b(a_1, \ldots, a_b)=
\begin{cases}
1, & a_1=\cdots=a_b\ne I, \\
|\{i:a_i\ne I\}|, & \text{otherwise}.
\end{cases}
\]

## 6. Exact local Restore sensitivity

**Lemma 3.** Replacing one argument of \(F_b\) increases its value by at most
\(b-1\), and the bound is attained.

**Proof.** Away from the all-equal nonidentity state, \(F_b\) is the ordinary
nonidentity Hamming weight, so one replacement raises it by at most one.
Entering the exceptional state lowers the value to one. Leaving that state
while keeping the changed letter nonidentity changes the value from one to
\(b\), giving the exact increase \(b-1\). ∎

## 7. MultiTag normal form

Let \(A_R\) be the alphabet actually realized by the partner/Tag signatures of
frame \(R\), and let \(H_R=\langle A_R\rangle\).

**Theorem 4.** If \(\mu\ge(b-1)t_R\), every admitted MultiTag-TARE instance has
an exact optimum satisfying

\[
|\operatorname{supp}(R)|
\le \operatorname{zsf}(H_R; A_R)
\le \operatorname{rank}(H_R)
\le s+1
\]

for every frame \(R\).

**Proof.** A zero-signature subword preserves partner anticommutation and every
Tag label; the Tags remain fixed. Deleting each selected coordinate refunds at
least \(\mu\) in frame cost and can add at most \((b-1)t_R\) in Restore cost by
Lemma 3. The deletion is therefore non-increasing in the stated cone. Its
effect stays within the same grammar, and the signature invariants persist, so
Theorem 1 applies iteratively. Finally, \(H_R\) is an elementary binary subgroup
of \(\mathbb F_2^{s+1}\), which gives the rank inequalities. ∎

The alphabet ceiling can be strictly smaller than realized rank when the
allowed alphabet contains no basis word of its generated subgroup. This is the
instance-adaptive refinement that an ambient dimension alone cannot express.

## 8. Sharp R6M specialization

For the frozen one-Tag, three-block R6M grammar,

\[
b=3, \qquad s=1, \qquad \mu=2, \qquad t_R=1.
\]

The objective lies on the sufficient-cone boundary. The signature alphabet
realizes a basis of \(\mathbb F_2^2\), so the deletion certificate ceiling is
two. An independent all-size normalization proves support at most two, and an
exact support-one obstruction proves necessity. Thus

\[
\kappa_{\mathrm{R6M}}=2.
\]

Only this frozen specialization receives an intrinsic sharpness claim.

## 9. Relation to prior work

Sparse optimal solutions [2], Davenport constants, restricted zero-sum
invariants [3],
finite-field dependence, Pauli symplectic algebra, and exact synthesis are
established areas. In particular, general sparse integer optimization provides
objective-independent support bounds, while zero-sum theory provides sequence
thresholds for selected alphabets and weights. Those results own the generic
ideas of sparse optima and zero-sum thresholds.

The residual contribution here is their compiler-specific conjunction: a
TARE-derived semantic signature, exact arbitrary-block Restore sensitivity, a
sufficient objective cone, an alphabet-sensitive support normal form, and a
separately sharp R6M control.

## 10. Reproducibility and limitations

Finite-group controls, binary basis obstructions, and the exact local Restore
sensitivity have been checked independently for bounded instances. The proofs
above carry the all-size authority.

The theorem applies only when zero-sum deletion is grammar-closed,
semantics-preserving, and non-increasing after every prior deletion.
Computing \(\operatorname{zsf}(H; A)\) may itself be difficult. The MultiTag
result applies only to the explicit grammar and objective. Outside
\(\mu\ge(b-1)t_R\), the proof is silent; it does not imply that larger support
is necessary. General multi-Tag sharpness remains open. Structural support is
not physical T count, runtime, circuit depth, qubit count, or quantum advantage.

## Data and code availability

The exact bounded controls and deterministic verification scripts supporting the
finite-group, basis-obstruction, and Restore-sensitivity checks accompany the
submission source. They are corroborative: the displayed proofs carry the
all-size claims. A permanent archival identifier must be inserted before the
final journal upload.

## 11. Conclusion

Ambient rank is not the primitive deletion threshold. The exact threshold is
the longest zero-sum-free word expressible by the realized signature alphabet.
Rank remains a convenient binary upper bound and is exact for the deletion
language when a basis is realized. Only a separate compiler witness can turn
that certificate ceiling into intrinsic support.

For MultiTag-TARE, block count controls deletion profitability through the
\(b-1\) Restore penalty, while the realized alphabet controls sufficient
support. The frozen R6M case aligns certificate and intrinsic complexity at two.
Beyond that case, the result is a strong normal form, not a necessity theorem.

## References

1. N. Schillo, A. Sturm, and R. Quay, “Block Encoding Linear Combinations of
   Pauli Strings Using the Stabilizer Formalism,” arXiv:2601.05740 (2026).
2. I. Aliev, J. A. De Loera, F. Eisenbrand, T. Oertel, and R. Weismantel,
   “The Support of Integer Optimal Solutions,” *SIAM Journal on Optimization*
   **28**, 2152-2157 (2018). DOI: 10.1137/17M1162792
3. G. Wang, “The universal zero-sum invariant and weighted zero-sum for
   infinite abelian groups,” *Communications in Algebra* **53**(4), 1581-1599
   (2025).
   DOI: 10.1080/00927872.2024.2418017
