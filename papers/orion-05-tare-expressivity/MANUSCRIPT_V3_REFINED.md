# A Sharp Support-Two Normal Form for Shared-Tag TARE Quantum Compilation

**Recursively refined V3 — 2026-08-22**  
**Stretch target:** PRX Quantum  
**Fallback:** npj Quantum Information

## Abstract

Quantum block-encoding compilers can expose auxiliary representation spaces whose apparent complexity grows with system size. We ask whether that complexity is intrinsic in a shared-Tag Tag-and-Restore Encoding (TARE) compiler family. For the frozen three-block TARE-M2 grammar under its support-count objective, we prove that the intrinsic uniform support number is exactly

\[
\kappa_{\mathrm{R6M}}=2.
\]

Every admitted instance, for arbitrary qubit count, has an exact optimum in which each auxiliary frame Pauli acts on at most two qubits. The upper bound follows from a local exchange argument. Active coordinates carry a two-bit class recording frame anticommutation and shared-Tag syndrome. For any frame of support at least three, a nonempty proper zero-sum subset of at most two classes can be removed while preserving both constraints. The corresponding Restore penalty is at most two per removed coordinate and never exceeds the minimum frame-support refund. Repeating the exchange yields a support-two optimum. The bound is sharp: a complete search over the entire support-one family has optimum 6 on an exact two-qubit instance whose unrestricted optimum is 5.

The support-two boundary is mechanistic rather than a loose proof artifact. The exchange fails at exactly the weight-two parity pattern exploited by the optimal frame-for-Tag coupling trade. Machine enumeration and fresh exact-DP stress independently corroborate the analytic proof, and a prospectively frozen regime prediction on a previously unread public benzene Hamiltonian is confirmed on all 15 registered matchings. The theorem is specific to the declared TARE grammar and objective; it is not a general block-encoding, fault-tolerant-resource, or quantum-advantage claim. It establishes instead that an apparently unbounded compiler representation can possess a sharp, system-size-independent optimal coupling scale.

## Popular summary

A quantum compiler often has many mathematically equivalent ways to represent the same operation. More freedom can improve a circuit, but it can also create a search space that grows rapidly with the number of qubits. In the TARE block-encoding family studied here, auxiliary Pauli operators are in principle allowed to spread over arbitrarily many qubits. We prove that this apparent complexity is unnecessary. No matter how large the admitted instance is, an optimal representation exists in which every auxiliary frame acts on at most two qubits. Two is also the best possible universal bound: we give an exact two-qubit example where restricting every frame to one qubit makes the optimum worse. The proof explains why. High-support coordinates can be removed in parity-preserving groups without increasing total cost, but one specific two-coordinate pattern cannot be simplified. The exact optimizer uses precisely that pattern to trade local frame complexity against the cost of a shared global Tag. The result gives a sharp normal form for this compiler family and replaces an open-ended auxiliary search space with a constant-support structural description.

---

## 1. Intrinsic representation complexity in quantum compilation

Block encoding is a common interface between structured operators and quantum algorithms based on Hamiltonian simulation, phase estimation and singular-value transformation. For Pauli Hamiltonians, the cost of the final algorithm can depend strongly on how the operator is represented before the high-level algorithm begins. This motivates increasingly expressive compiler families, but expressivity creates a second question: **how much of the representation freedom can an optimum actually need?**

TARE, introduced by Schillo, Sturm and Quay, represents a linear combination of Pauli strings using mutually anticommuting auxiliary frames together with Tag and Restore operations. We take the TARE primitive, its shared-Tag identity, Restore factoring and the underlying anticommuting-unitary construction as prior work. Our question is about the exact optimization geometry of one nontrivial joint compiler family built from those primitives.

In the three-block shared-Tag TARE-M2 grammar studied here, auxiliary frame Paulis are not restricted a priori to local support. A frame may act on a number of qubits that grows with the system. It is therefore not obvious that low support is without loss. An additional frame coordinate incurs local cost, but it can also change the cheapest globally compatible Tag and the factorization pattern of multiple Restore strings. A local sparsity heuristic cannot decide the joint problem.

We characterize the required support exactly. Define

\[
\kappa_{\mathrm{R6M}}
=\min\left\{k:\text{every admitted instance has an exact optimum with all frame supports}\le k\right\}.
\]

Our main result is

\[
\boxed{\kappa_{\mathrm{R6M}}=2.}
\]

This statement has two independent parts. First, support three or larger can always be exchanged away without increasing cost. Second, support one is not uniformly sufficient. The first part is an all-size theorem; the second is an exact finite counterexample over the complete support-one family.

The result is useful as a structural law rather than as a claim about one optimizer run. The unrestricted representation allows auxiliary support growing with `n`, whereas every optimum lies in a constant-support normal form. For the fixed six-slot grammar, this gives a direct raw candidate family of size

\[
\left(3n+9\binom n2\right)^6=O(n^{12}),
\]

before feasibility constraints. This is a representation-count corollary, not a claim that the existing production dynamic program is accelerated from exponential to polynomial.

### Contributions

1. **Sharp normal form.** We prove support at most two suffices for every admitted instance and every qubit count in the declared grammar/objective.
2. **Sharpness.** We exhibit an exact instance on which the complete support-one family is strictly suboptimal.
3. **Mechanistic boundary.** The only weight-two obstruction to the exchange corresponds to the actual optimal frame-for-Tag trade.
4. **Independent corroboration.** Machine checks and fresh exact-DP stress reproduce the theorem's finite core without providing the all-size logical step.
5. **Prospective structural evidence.** A regime prediction fixed before reading a fresh public Hamiltonian's exact answer is confirmed on all registered matchings.

---

## 2. Compiler family and objective

An instance contains six target Pauli strings grouped into three ordered two-term blocks `A`, `B` and `C`. Block `j` chooses two mutually anticommuting frame Paulis `(R_{j0},R_{j1})`, a permutation assigning its targets to the branches, and one branch as the cheaper central multiplier. All blocks share one Tag Pauli `S`. A common label orientation requires the symplectic relation of `S` to the first and second frame branches to agree across blocks and to differ between the two branches.

For target `P_{j,\pi_j(k)}`, the local Restore string is

\[
T_{jk}=P_{j,\pi_j(k)}R_{jk}.
\]

Let `w(P)` denote Pauli support. The noncentral and central frame branches have multipliers 4 and 2 respectively. After subtracting the constant weight-one baseline used by the frozen exact referee, the variable frame contribution is

\[
\sum_{j,k}m_{jk}\bigl(w(R_{jk})-1\bigr),\qquad m_{jk}\in\{2,4\}.
\]

The shared Tag contributes `2w(S)`. For a fixed branch `k`, the three Restore strings use the donor-owned three-way common-factor rule. At one qubit, with local letters `(a,b,c)`, define

\[
F_3(a,b,c)=
\begin{cases}
1,&a=b=c\neq I,\\
w(a)+w(b)+w(c),&\text{otherwise}.
\end{cases}
\]

The objective is the sum of the frame, Tag and Restore contributions. `C_DP` denotes the unrestricted exact optimum. `C_{D^{++}}` denotes the optimum after restricting every frame Pauli to support at most two while still minimizing all remaining choices exactly.

### Feasibility invariants used by the exchange

The proof changes one frame Pauli at a time and relies only on the following local invariants.

1. The modified frame Pauli remains nonidentity.
2. Its symplectic parity with its partner remains odd, so the frame remains anticommuting.
3. Its symplectic parity with the common Tag is unchanged, so all shared label constraints remain satisfied without Tag repair.
4. Target assignment, the partner frame, all other blocks and the central-branch choice are unchanged.
5. Restore strings change only at the removed frame coordinates and are re-evaluated by the same frozen `F_3` rule.

No other feasibility condition in the frozen grammar depends on the removed local letters.

---

## 3. All-size support-two theorem

### Theorem 1

For every qubit count `n`, every admitted six-target instance, every matching, every target permutation and every central-branch choice in the frozen R6M grammar,

\[
C_{DP}=C_{D^{++}}.
\]

Equivalently, every exact optimum has an equally good representative in which every frame Pauli has support at most two.

### 3.1 A two-bit local invariant

Take a feasible configuration with a frame Pauli `R` of support `w\ge3`. Let `R'` be its anticommuting partner and `S` the shared Tag. For each `q\in\operatorname{supp}(R)`, define

\[
\alpha_q=\langle R_q,R'_q\rangle,
\qquad
\beta_q=\langle S_q,R_q\rangle,
\]

and

\[
c_q=(\alpha_q,\beta_q)\in\mathbb F_2^2.
\]

Because `R` and `R'` anticommute,

\[
\sum_q \alpha_q=1\pmod 2.
\]

A subset of coordinates whose class sum is `(0,0)` can be deleted from `R` without changing either the frame anticommutation parity or the Tag syndrome.

### Lemma 1 — small zero-sum subset

Any multiset of `w\ge3` elements of `\mathbb F_2^2` whose total first coordinate is odd contains a nonempty proper zero-sum subset of size at most two.

**Proof.** If `(0,0)` occurs, remove that singleton. Otherwise, if any class repeats, the equal pair sums to zero. If neither occurs, all active classes are distinct and nonzero. There are only three nonzero classes. At `w=3` they must be `(0,1)`, `(1,0)` and `(1,1)`, whose first coordinates have even total parity, contradicting the assumed odd total. For `w>3`, repetition is unavoidable. ∎

Thus at least one and at most two coordinates can be removed while preserving both relevant symplectic constraints. Because `w\ge3`, the modified frame remains nonidentity.

### 3.2 The Restore penalty cannot exceed the frame refund

Write

\[
W(a,b,c)=w(a)+w(b)+w(c).
\]

Then

\[
F_3(a,b,c)=W(a,b,c)-2\,\mathbf 1[a=b=c\neq I].
\]

Zeroing one local frame letter changes only one of the three Restore letters at that qubit.

### Lemma 2 — local Restore bound

Changing one frame letter to identity increases the affected local `F_3` cost by at most two.

**Proof.** If the old triple does not receive the all-equal discount, only one ordinary-support term changes, so `W` can rise by at most one, while a new discount can only reduce cost. If the old triple is all equal and nonidentity, its cost is 1. Destroying the discount leaves two unchanged nonidentity letters and at most one additional nonidentity letter, so the new cost is at most 3. Hence the increase is at most 2. ∎

Removing one frame coordinate refunds multiplier `m\in\{2,4\}`. Therefore

\[
\Delta C\le2-m\le0
\]

at every removed coordinate. The selected subset has zero `\beta` sum, so the Tag is unchanged and no global repair cost is introduced.

### 3.3 Descent

Apply the exchange to any frame of support at least three. Cost never increases and total frame support strictly decreases. Repeating terminates with support at most two everywhere. Starting from an optimum proves Theorem 1. ∎

---

## 4. Why the bound is exactly two

The all-size proof establishes `\kappa_{\mathrm{R6M}}\le2`. To prove sharpness, the support-one family must be exhausted rather than sampled.

The frozen `D+` referee enumerates arbitrary support-one anchor qubits for every block, all ordered anticommuting local Pauli pairs, both global label orientations, every target permutation and the minimum compatible Tag. For this objective, replacing any compatible Tag by the minimum compatible Tag cannot worsen Restore terms, so `D+` is the complete support-one frame family.

On a registered two-qubit instance,

\[
C_{DP}=5<6=C_{D+}.
\]

The unrestricted optimum spends support two on the cheap central frame branch and obtains a cheaper global Tag/Restore configuration. Therefore support one cannot be a uniform normal form and

\[
\boxed{\kappa_{\mathrm{R6M}}=2.}
\]

### The proof obstruction is the compiler mechanism

The zero-sum exchange has exactly four failing ordered class pairs at support two. In those patterns, a coordinate can be locally redundant for frame anticommutation while still carrying shared-Tag syndrome. Removing it breaks the global label relation. The exact `5<6` optimizer realizes precisely this structure: it pays one extra local frame coordinate to reduce the globally shared Tag/Restore cost.

This correspondence matters because it makes the threshold interpretable. Support two is not merely where our proof stops; it is where the compiler contains a real nonlocal coupling trade.

---

## 5. Independent corroboration and prospective prediction

The analytic proof is independent of extrapolation from finite data. The original exact campaign nevertheless supplies useful corroboration:

- 18,432 complete local cost cases with zero violation of the Restore/refund inequality;
- 43,688 odd-`\alpha` class tuples through support eight, with zero failures for support 3–8 and the same four support-two failures;
- 70/70 fresh `n=3,4` comparisons with `C_{DP}=C_{D^{++}}`;
- 210 seeded exchange descents in which predicted and observed cost changes agree step by step.

Before the all-size proof was obtained, a finite structural classifier around the first discovered split/borrow mechanisms had zero error on 9,771 registered rows. A fresh-subject protocol then selected a previously unread public benzene/cc-pVDZ DUCC2 Hamiltonian, committed the donor-exact prediction before invoking the unrestricted referee, and confirmed that prediction and exact cost on all 15 matchings.

We retain this evidence as corroboration of structural understanding, not as proof of the all-size theorem. Later adversarial QG work finds additional support-two subregimes, showing that a simple normal form need not imply a simple complete taxonomy.

---

## 6. Public-Hamiltonian grounding

On the 30 registered H4 and equilibrium-N2 six-term matchings,

\[
C_{DP}=C_{D^{++}}=C_{D+}=C_{R6L}.
\]

These cases show a useful opposite regime: the exact optimizer has no incentive to exercise the nontrivial support-two trade.

A separate public H2O/cc-pVTZ DUCC instance contains 8,082 nonidentity Pauli terms on 20 qubits. A frozen structural compiler point reduces the registered `C` coordinate from 8,078 to 4,972, approximately 38.45%, at relative normalization overhead `9.087\times10^{-6}`. This is supporting implementation-aware evidence only. It is not a complete fault-tolerant resource estimate and does not contribute to the proof of Theorem 1.

---

## 7. Relation to prior work

TARE, Tag/Restore, anticommuting unitary partitioning and auxiliary-frame freedom are donor-owned. Pauli-frame, stabilizer and binary-symplectic compiler literatures also already contain powerful support/weight-reduction transformations. We therefore do not claim the first sparse Pauli representation or the first support-reducing compiler.

The narrower theorem delta is the **sharp uniform optimum-support threshold** for the declared shared-Tag TARE-M2 family. Our bounded searches did not locate a prior equivalent statement in TARE, Pauli-frame/symplectic compilation or unitary-partitioning language, but this search record is not a novelty certificate.

The result also differs from general gate-synthesis complexity bounds. It characterizes the representation support required to contain an optimum under a specific coupled compiler objective; it does not lower-bound or upper-bound the optimal circuit complexity of arbitrary quantum operations.

---

## 8. Discussion

### A system-size-independent optimal coupling scale

The main conceptual result is that representation support and system size separate. The grammar permits arbitrarily spread auxiliary Paulis, but the exact optimum never needs a frame coupling scale larger than two. Such normal forms can matter even when an exact optimizer already exists: they identify which structures are fundamentally relevant, provide smaller direct candidate families, and expose which coupling mechanisms any approximate or hardware-aware successor must preserve.

### Normal-form complexity and regime complexity are different

The finite R6Q classifier initially suggested a small trade taxonomy. Later QG counterexamples refine that taxonomy without requiring support three. This distinction is useful: the set guaranteed to contain an optimum can be simple even when the phase diagram inside that set is richer.

### The next scientific question is objective dependence

Our proof uses the frozen support-count weights. Hardware projections can change the value of a frame refund relative to Restore/Tag cost. Determining the objective regions in which the normal form survives is therefore a separate problem; later work studies that question and is not back-ported as a ORION-01 claim.

---

## 9. Claim boundary

We establish only the following.

- `\kappa_{R6M}=2` for the frozen three-block shared-Tag TARE-M2 grammar and frozen support-count objective.
- The support-two upper bound holds for arbitrary admitted `n` and instance choices.
- An exact two-qubit instance proves support one is not uniformly sufficient.
- The proof obstruction matches an exact optimal frame-for-Tag coupling mechanism.
- Registered finite and prospective results provide corroborating structural evidence.

We do **not** establish a universal TARE theorem, a universal two-trade taxonomy, a production-DP complexity improvement, a fault-tolerant resource advantage, or physical quantum advantage.

---

## Code and data availability

The exact protocols, result receipts, analytic proof notes, independent finite-core checker and manuscript claim ledger are committed in the ORION repository. The principal result artifacts are:

- `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`;
- `research/extensions/orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json`;
- `development/orion-q-max-r0/MAX_R6O_ENLARGED_TAG_DONOR_PROTOCOL.md`;
- `papers/orion-05-tare-expressivity/HUMAN_PROOF_R6S_2026-08-22.md`;
- `papers/orion-05-tare-expressivity/independent_human_proof_sanity.py`.

`REPRODUCE.md` gives the intended clean-checkout reproduction route. Before archival publication, the cited code/results should be tagged or deposited in a DOI-minting repository and the permanent identifier inserted here.

## AI-assisted research and writing disclosure

ORION and external language-model tooling were used as research-control, analysis and manuscript-refinement instruments. They are not authors and grant no scientific or novelty authority. Human authors remain responsible for the theorem statement, proof, literature positioning, code/results, interpretation and submitted text. Exact disclosure wording should be updated to the target journal's policy at submission time.

---

## References — anchors to be rendered in target style

- Schillo, Sturm & Quay. *TARE: Block Encoding Linear Combinations of Pauli Strings Without Ancilla State Preparation* (2026).
- Izmaylov et al. Unitary partitioning for mutually anticommuting Pauli structures (2020).
- van den Berg & Temme. Simultaneous diagonalization of Pauli clusters (2020).
- Paykin et al. PCOAST (2023).
- Yang et al. PHOENIX (2025).
- Relevant current Pauli/symplectic compiler and block-encoding complexity work listed in `NOVELTY_RESEARCH_2026-08-22.md` and `NOVELTY_REFRESH_FINAL_2026-08-22.md`.
