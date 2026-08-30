# A Sharp Support-Two Normal Form for Shared-Tag TARE Quantum Compilation

## Abstract

Expressive quantum-compilation grammars can introduce auxiliary Pauli representations whose nominal support grows with system size. We prove that this apparent complexity is unnecessary in a nontrivial shared-Tag TARE family. For the declared three-block grammar under its frozen support-count objective, every admitted instance at every qubit count has an exact optimum in which each auxiliary frame Pauli acts on at most two qubits. The bound is sharp: an exact two-qubit instance has unrestricted optimum 5 while the complete support-one family has optimum 6. The intrinsic uniform support number of the studied family is therefore exactly two.

The all-size upper bound follows from a local exchange. Each active frame coordinate receives a two-bit signature encoding partner anticommutation and shared-Tag syndrome. Any frame of support at least three contains a nonempty proper zero-signature subset of size at most two. Removing that subset preserves the load-bearing symplectic constraints. The local Restore penalty can increase by at most two per removed coordinate, which never exceeds the minimum frame-support refund in the frozen objective. Repeating the exchange produces an equally good support-two optimum. The lower witness exploits precisely the weight-two parity pattern at which the exchange cannot continue: an extra local frame coordinate enables a cheaper global Tag/Restore configuration.

Finite exact enumeration and dynamic-programming stress corroborate the proof but do not provide its all-size authority. A prospectively frozen structural prediction on a previously unread public benzene Hamiltonian is confirmed on all 15 registered matchings. Later hostile work finds additional optimal support-two subregimes, demonstrating that a sharp normal form does not imply a complete compact regime formula. The result is specific to the stated grammar and objective and is not a fault-tolerant resource, hardware-performance, or quantum-advantage claim.

## 1. Main results and assumptions

Quantum's current author guidance asks that the main results and assumptions be recoverable in the first couple of pages. We therefore state the exact claim boundary before the construction details.

The paper studies a fixed three-block shared-Tag TARE compiler grammar. Six target Pauli strings are arranged into three ordered two-term blocks. Each block chooses two mutually anticommuting frame Paulis and all blocks share one Tag Pauli. The cost function charges frame support, Tag support and a coupled Restore term. Frames may have support growing with the qubit count before optimization.

Define

`kappa = min{k : every admitted instance has an exact optimum with every frame support <= k}`.

### Theorem A — all-size sufficiency

For every admitted system size under the declared grammar and objective, an unrestricted optimum has an equally good representative in which every frame has support at most two.

### Theorem B — sharpness

There exists a two-qubit admitted instance for which the unrestricted optimum is 5 and the complete support-at-most-one family has optimum 6. Therefore `kappa = 2`.

### Evidence hierarchy

- Theorems A and B carry the normal-form authority.
- Finite exact panels check implementation and proof transcription.
- The prospective benzene case tests forward use of the structural picture.
- Compact regime classifiers are explanatory objects and remain falsifiable independently of the theorem.

The theorem is objective-indexed. Changing resource weights can invalidate the local non-increase argument and requires a new proof or counterexample analysis.

## 2. Compiler family

Each block `j` chooses mutually anticommuting frames `(R_j0,R_j1)`, a target assignment and a central branch. A shared Tag Pauli `S` imposes a global label relation across blocks. The Restore strings couple local frame choices back to the target strings.

The proof uses only three classes of invariants: the modified frame remains nonidentity, partner anticommutation is preserved, and the shared Tag syndrome is preserved. Other blocks and target assignments remain fixed. These are exactly the assumptions under which the local exchange is sound.

The contribution does not include the TARE primitive, Tag/Restore construction, or anticommuting-unitary machinery; those are donor mechanisms.

## 3. Two-bit removable-support signature

Consider a feasible frame `R` with support at least three, its anticommuting partner `R'`, and the shared Tag `S`. At each active coordinate `q`, define

`alpha_q = <R_q,R'_q>`

and

`beta_q = <S_q,R_q>`

in the binary symplectic form. Let `c_q=(alpha_q,beta_q) in F_2^2`.

Because `R` and `R'` anticommute, the XOR of the first signature coordinates is one.

**Lemma 1.** Any multiset of at least three vectors in `F_2^2` with odd total first coordinate contains a nonempty proper zero-sum subset of size at most two.

If `(0,0)` occurs, remove that singleton. Otherwise a repeated nonzero class supplies a zero-sum pair. If exactly three active classes are distinct and nonzero, they are the three nonzero vectors of `F_2^2`, whose first coordinates sum to zero, contradicting the odd total. Larger supports force repetition.

Deleting the identified subset preserves partner anticommutation and shared-Tag syndrome.

## 4. Restore sensitivity makes the exchange non-increasing

The local Restore functional discounts an all-equal nonidentity triple. Removing a frame letter can destroy that discount, so feasibility alone does not prove optimality.

**Lemma 2.** Replacing one frame letter by identity increases the affected local Restore cost by at most two.

Away from the discounted all-equal state, the ordinary nonidentity count changes by at most one. Leaving the discounted state can increase local cost from one to at most three. Hence two is the exact worst-case increase.

Each removed frame coordinate refunds at least two cost units in the frozen objective. The Restore penalty therefore cannot exceed the frame refund. A zero-signature deletion preserves feasibility without increasing total cost.

Iterating strictly decreases total frame support until every frame has support at most two, proving Theorem A.

## 5. Exact lower witness

Sharpness requires an exhaustive support-one comparison, not a sampled search. The support-one referee enumerates anchor qubits, local anticommuting Pauli pairs, label orientations, target permutations and compatible Tags.

On the registered two-qubit witness,

`C_unrestricted = 5 < 6 = C_support<=1`.

The unrestricted optimum uses support two on a cheap central frame branch and obtains a cheaper shared Tag/Restore arrangement. This proves Theorem B.

The lower witness also explains the proof boundary. At support two, a coordinate may be redundant for partner anticommutation while still carrying the shared-Tag syndrome needed for the global cost trade. Support two is therefore not merely where a chosen proof technique stops.

## 6. Finite corroboration and prospective prediction

Finite checks exercise local Restore/refund inequalities, signature tuples, exact dynamic-programming comparisons and seeded exchange descents. They are valuable hostile controls because an implementation defect or omitted boundary case could falsify a claimed specialization of the theorem. They are nevertheless secondary to the all-size proof.

Before the proof was completed, a structural regime prediction was frozen for a previously unread public benzene Hamiltonian and committed before the unrestricted exact referee was opened. The prediction and exact cost were confirmed on all 15 registered matchings. This establishes prospective use on that subject, not all-size truth.

Public Hamiltonian examples also contain regimes in which support one already attains the optimum. The sharp witness therefore must not be read as evidence that support two is typically necessary.

## 7. Normal-form closure versus regime explanation

The complete support-two normal form is closed under the theorem assumptions. A compact human-readable classification of *which* support-two construction wins is a different scientific object.

Later hostile searches produce exact optimal support-two hybrids outside earlier compact explanation families. Those witnesses refute the explanation but remain inside the theorem-certified class. The paper retains them because they demonstrate the advantage of separating theorem authority from interpretive taxonomy.

A finite zero-error classifier is not promoted into an all-size regime law.

## 8. Relation to prior work and significance

TARE, block encoding, Tag/Restore factoring, anticommuting-unitary construction, binary symplectic representations and exact synthesis are established areas. Sparse or low-support transformations also have broad precedents. The novelty claim is therefore not that quantum compilers can sometimes be simplified.

The residual result is a **sharp system-size-independent optimum-support threshold** for a coupled shared-Tag compiler family. The unrestricted grammar permits support to grow with system size, yet the exact optimum always lies inside a constant-support class, and a matching lower witness shows that the constant is intrinsic for the declared objective.

This is the technical/conceptual advance offered to Quantum. It reduces the structural search space and identifies the exact coupling pattern that prevents further universal simplification without converting that structural result into a hardware claim.

## 9. Limitations

The theorem belongs to one grammar and objective. Reweighting the objective can change deletion profitability; no arbitrary-resource theorem is claimed. A complete all-size regime taxonomy inside support two remains open. Public chemistry cases provide grounding, not a population estimate.

No statement is made about fault-tolerant `T` count, depth, logical qubits, physical runtime, noise, end-to-end quantum algorithm performance, or quantum advantage.

## 10. Reproducibility and release

The release should bind the exact grammar and objective, analytic proofs, exhaustive support-one lower witness, exact counterexample data, finite stress tests and prospective prediction record. The submission-facing arXiv version must be posted or cross-listed to `quant-ph`, and the final manuscript should retain the first-page distinction between theorem, finite corroboration, prospective evidence and fallible explanation.

A submission-date literature refresh and independent replay on the exact release commit remain release checks. They do not expand the theorem.

## 11. Conclusion

A compiler can permit auxiliary structures whose nominal support grows without bound while its optimum never needs that complexity. In the studied shared-Tag TARE family, a two-bit symplectic signature exposes removable support and a tight Restore bound pays for every deletion from support three upward. A complete lower witness proves that support one is genuinely insufficient. The resulting support-two normal form is sharp, all-size under its declared assumptions, and deliberately separated from both compact regime explanations and device-level performance claims.