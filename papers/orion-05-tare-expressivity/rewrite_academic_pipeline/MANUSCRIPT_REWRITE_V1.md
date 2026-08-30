# A Sharp Support-Two Normal Form for Shared-Tag Quantum Compilation

## Abstract

Expressive quantum-compilation grammars can introduce auxiliary Pauli representations whose nominal support grows with system size. We show that this apparent complexity is unnecessary in a nontrivial shared-Tag TARE family. For the frozen three-block grammar under its declared support-count objective, every admitted instance at every qubit count has an exact optimum in which each auxiliary frame Pauli acts on at most two qubits. The bound is sharp: an exact two-qubit instance has unrestricted optimum 5 while the complete support-one family has optimum 6. Thus the intrinsic uniform support number of the studied family is exactly two.

The all-size upper bound follows from a local exchange argument. Each active frame coordinate is assigned a two-bit signature recording partner anticommutation and shared-Tag syndrome. Any frame of support at least three contains a nonempty proper zero-signature subset of size at most two. Removing that subset preserves the relevant symplectic constraints. The associated Restore cost can increase by at most two per removed coordinate, never exceeding the minimum frame-support refund, so repeated exchanges terminate at an equally good support-two optimum. The sharp lower witness exploits exactly the weight-two parity pattern at which this exchange cannot continue: one additional local frame coordinate enables a cheaper global Tag/Restore configuration.

Finite exact enumerations, seeded exchange descents and fresh dynamic-programming stress corroborate the theorem but do not supply its all-size authority. A prospectively frozen regime prediction on a previously unread public benzene Hamiltonian is confirmed on all 15 registered matchings. Later hostile work finds additional support-two subregimes, showing that a sharp normal form need not imply a complete compact regime formula. The result is specific to the declared TARE grammar and objective and makes no fault-tolerant-resource or quantum-advantage claim.

## 1. Main result and assumptions

Quantum compilers often optimize over representations that are far more expressive than the structures ultimately used by an optimum. Determining the smallest structural family that is guaranteed to contain an optimum can therefore be as important as accelerating the optimizer itself.

We study an exact three-block shared-Tag TARE grammar. Six target Pauli strings are arranged into three ordered two-term blocks. Each block chooses two mutually anticommuting frame Paulis and all blocks share one Tag Pauli. The objective charges frame support, Tag support and a coupled Restore term. Frames are not restricted a priori to local support.

Define

\[
\kappa=\min\{k:\text{every admitted instance has an exact optimum with every frame support}\le k\}.
\]

Our main theorem is

\[
\boxed{\kappa=2.}
\]

The result has two independent obligations. An all-size exchange theorem proves support two is sufficient. A complete support-one search gives an exact counterexample proving support one is not uniformly sufficient. Both are required for sharpness.

The theorem is indexed by the declared grammar and objective. It does not transfer to arbitrary block encodings, arbitrary resource weights or arbitrary quantum compilers.

## 2. Compiler family and objective

Each block \(j\) chooses a pair of mutually anticommuting frames \(R_{j0},R_{j1}\), a target assignment, and a central branch. The three blocks share a Tag Pauli \(S\). A global label constraint couples the symplectic relation between \(S\) and the two frame branches across blocks.

For a target \(P_{j,k}\), the local Restore string is the product of that target with its frame. The objective combines three ingredients: a positive frame-support charge, a Tag-support charge, and a three-way Restore functional. The Restore functional rewards a local position at which the three relevant nonidentity letters agree, otherwise charging ordinary nonidentity support.

The proof uses only a small set of feasibility facts. Changing one frame while holding its partner, Tag, target assignment and the other blocks fixed is valid when partner anticommutation and Tag syndrome are preserved. The Restore contribution is then recomputed under the unchanged objective.

These assumptions are stated early because they are the exact boundary of the theorem. The result is not a generic sparsity principle detached from the compiler semantics.

## 3. A two-bit signature for removable support

Consider a feasible configuration with a frame Pauli \(R\) of support at least three. Let \(R'\) be its anticommuting partner and \(S\) the shared Tag. At each active coordinate \(q\), define

\[
\alpha_q=\langle R_q,R'_q\rangle,
\qquad
\beta_q=\langle S_q,R_q\rangle,
\]

and the class

\[
c_q=(\alpha_q,\beta_q)\in\mathbb F_2^2.
\]

Because \(R\) and \(R'\) anticommute, the XOR of the first coordinates is one. A subset of active coordinates whose class sum is \((0,0)\) can be removed from \(R\) without changing either the partner anticommutation parity or the Tag syndrome.

**Lemma 1.** Any multiset of at least three elements of \(\mathbb F_2^2\) whose total first coordinate is odd contains a nonempty proper zero-sum subset of size at most two.

If the zero class occurs, it is removable as a singleton. Otherwise, a repeated nonzero class gives a removable pair. If three active classes are all distinct and nonzero, they are exactly the three nonzero vectors of \(\mathbb F_2^2\), whose first coordinates sum to zero, contradicting the required odd parity. Larger supports force repetition.

Thus every frame of support at least three contains a one- or two-coordinate deletion preserving the two load-bearing symplectic constraints.

## 4. Restore sensitivity pays for the deletion

Preserving feasibility is not enough; the exchange must also preserve optimality. The local three-way Restore functional can receive a discount when all three local letters are the same nonidentity Pauli. Removing one frame coordinate can destroy this discount.

**Lemma 2.** Replacing one frame letter by identity increases the affected local Restore cost by at most two.

Away from the discounted all-equal state, ordinary support changes by at most one. Leaving the discounted state can increase the local cost from one to at most three, giving the exact worst-case increase of two.

Every removed frame coordinate refunds at least two units under the declared objective. Consequently the Restore penalty is never larger than the frame refund. A zero-signature deletion therefore preserves feasibility and does not increase total cost.

Repeatedly applying the exchange strictly decreases total frame support until every frame has support at most two.

**Theorem 1 (all-size support-two normal form).** Every admitted instance at every qubit count has an exact optimum in the support-at-most-two family.

The all-size authority comes from this proof. Finite zero-error checks serve only as corroboration.

## 5. Why support one is not enough

To prove \(\kappa=2\), the support-one family must be exhausted rather than sampled. The registered support-one referee enumerates arbitrary anchor qubits, all local anticommuting Pauli pairs, label orientations, target permutations and compatible Tags.

On a registered two-qubit instance,

\[
C_{\mathrm{unrestricted}}=5<6=C_{\mathrm{support\le1}}.
\]

The unrestricted optimizer uses support two on a cheap central frame branch and thereby obtains a cheaper shared Tag/Restore arrangement. This exact witness establishes that support one is not uniformly sufficient.

The obstruction aligns with the proof boundary. At support two, a coordinate can be locally redundant for partner anticommutation while still carrying the Tag syndrome needed for the globally cheaper solution. The sharpness witness therefore shows that the place where the exchange proof stops is a real compiler coupling mechanism, not merely a weakness of the argument.

## 6. Finite corroboration and prospective evidence

The analytic theorem is accompanied by several independent finite checks: exhaustive local Restore/refund cases, class-tuple enumeration, fresh exact-DP comparisons at larger small sizes, and seeded exchange descents in which predicted and observed cost changes agree step by step. These checks are valuable because they can expose implementation or proof-transcription errors, but they do not replace the all-size argument.

Before the all-size proof was completed, a structural classifier was frozen and then applied to a previously unread public benzene Hamiltonian. The predicted regime and exact cost were committed before opening the unrestricted referee and were confirmed on all 15 registered matchings. This is prospective evidence that the structural understanding can be used before exact optimization; it is not the theorem authority.

Public Hamiltonian examples also include cases in which the support-two freedom is unnecessary and support one already attains the exact optimum. This prevents the sharp lower witness from being misread as a claim that support two is usually required.

## 7. Normal-form complexity is not regime-formula complexity

A sharp normal form can coexist with a complicated internal regime map. Later hostile searches find exact support-two configurations outside earlier compact explanation families. Those counterexamples do not threaten Theorem 1 because they remain within the theorem-certified support-two class.

This distinction is central to the contribution. The theorem says where an optimum can always be found. A compact regime formula tries to explain which support-two construction wins on each instance. The former is closed; the latter can continue to evolve as new exact subregimes are discovered.

The paper therefore does not promote a finite zero-error regime classifier into an all-size structural law.

## 8. Relation to prior work

TARE, Tag/Restore factoring, anticommuting-unitary constructions and the underlying block-encoding primitives are donor work. Pauli-frame, stabilizer, symplectic and exact-synthesis literatures also contain powerful support-reduction transformations. We do not claim the first sparse Pauli representation or the general idea that local algebra can reduce an exact compiler search.

The residual theorem is narrower: a **sharp uniform support threshold for the exact optimum** in the declared shared-Tag TARE family, together with a mechanism-level explanation of the support-two obstruction and a prospectively exercised structural prediction.

The result also differs from circuit-complexity theorems. It characterizes an auxiliary representation family under a fixed compiler objective; it is not a bound on arbitrary unitary synthesis or a full physical resource estimate.

## 9. Reproducibility and release design

The publication package should contain the grammar and objective, the analytic exchange proof, the complete support-one lower-witness search, exact witness data, finite stress tests, and the prospective prediction record. The first pages should keep the theorem assumptions and the distinction between theorem, finite corroboration and prospective evidence visible, consistent with the current Quantum editorial guidance.

A fresh literature check and independent replay on the exact submission commit remain release procedures rather than reasons to reopen the scientific question.

## 10. Limitations

The theorem is tied to one grammar and one objective. Reweighting resource terms can change whether the local exchange is non-increasing. The paper does not establish a complete all-size regime taxonomy inside the support-two family. Public Hamiltonian examples are grounding cases, not a population estimate of compiler advantage.

No claim is made about fault-tolerant \(T\)-count, circuit depth, device noise, wall-clock superiority or quantum advantage. The constant-support normal form is a structural compiler result.

## 11. Conclusion

An exact quantum compiler can permit auxiliary support that grows with system size while never needing that complexity at optimum. In the studied shared-Tag TARE family, a two-bit symplectic signature and a tight Restore-sensitivity bound make every support-three-or-larger frame reducible without cost increase. A complete lower witness shows that support one is genuinely insufficient, fixing the intrinsic uniform support number at two. The result is both exact and bounded: a sharp normal form for one compiler family, not a universal claim that quantum compilation is low-support.
