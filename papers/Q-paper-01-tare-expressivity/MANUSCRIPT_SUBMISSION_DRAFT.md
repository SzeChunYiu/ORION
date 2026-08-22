# Sharp Support-Two Normal Forms for Shared-Tag TARE Quantum Compilation

**Submission-oriented draft — 2026-08-22**

This draft is the current publication-facing Q1 version. It incorporates the final closed ORION-Q results and the analytic proof derivation in `HUMAN_PROOF_R6S_2026-08-22.md`. Earlier manuscript versions remain in the directory as historical snapshots. TARE and all donor-owned primitives are explicitly credited; no internal authority string is treated as external novelty certification.

---

## Abstract

Tag-and-Restore Encoding (TARE) block-encodes linear combinations of Pauli strings through auxiliary mutually anticommuting frames, a shared Tag operator, and Restore corrections. The freedom to choose those auxiliary objects creates a coupled compiler space in which a high-support frame can trade implementation cost against shared-Tag support and Restore factoring. We determine the exact support complexity of a frozen three-block shared-one-bit-Tag TARE-M2 family.

Let `kappa` denote the smallest integer such that every admitted instance, at every qubit count, has an exact optimum in which every auxiliary frame Pauli acts nontrivially on at most `k` qubits. We prove

\[
\boxed{\kappa=2.}
\]

The upper bound is analytic. For any support-three-or-larger frame Pauli, each active qubit is labeled by a two-bit class recording its contribution to frame anticommutation and the shared-Tag syndrome. Odd global anticommutation forces a nonempty proper zero-sum subset of at most two classes. Removing the corresponding frame letters preserves both constraints. The three-way Restore cost can be written as ordinary local support minus a two-unit discount when all three Restore letters coincide; changing one frame letter can therefore increase Restore cost by at most two, never more than the minimum frame-support refund. Iterating the exchange yields a support-two optimum for arbitrary system size. The bound is tight: an exact two-qubit instance has unrestricted cost 5 while the complete all-support-one frame family has optimum 6.

The sharp threshold is mechanistic rather than accidental. The zero-sum exchange fails precisely on the weight-two parity patterns realized by the optimal frame-for-Tag coupling trade. A second exact mechanism trades increased shared-Tag support for split frame anchors. On registered finite domains, closed-form tests for these first two mechanisms classify donor exactness with zero error over 9,771 instances without invoking the unrestricted dynamic program; a prospectively frozen prediction on a previously unread public benzene DUCC Hamiltonian is subsequently confirmed on all 15 matchings. We explicitly do not promote this finite-domain two-mechanism classifier to an all-size taxonomy: later adversarial follow-up work finds additional support-two subregimes while leaving the support-two theorem intact.

The result gives a sharp exact normal form for a nontrivial TARE compiler family: arbitrary-support auxiliary frames are unnecessary, but two-qubit support is genuinely required. Supporting studies provide a coefficient-majorization rule for split-TARE normalization and a public 20-qubit H2O Pareto point. The theorem is grammar- and objective-specific and makes no claim of general block-encoding, fault-tolerant-resource, or physical quantum advantage.

---

## 1. Introduction

Block encoding is a common gateway from a classical operator description to quantum algorithms based on signal processing, singular-value transformation, Hamiltonian simulation and phase estimation. For Pauli Hamiltonians, the representation chosen for the block encoding can be as important as the abstract algorithm: coefficient normalization, ancillary state preparation, controlled Pauli structure and basis changes can dominate the realized resource cost.

Tag-and-Restore Encoding (TARE), introduced by Schillo, Sturm and Quay, replaces conventional amplitude-state preparation for a Pauli linear combination with an auxiliary anticommuting unitary together with Tag and Restore operations. The construction deliberately leaves substantial compiler freedom. Even for a fixed set of target Paulis one may vary the auxiliary frame, target-to-frame assignment, shared Tag realization and placement of cheaper implementation branches.

That freedom raises a structural question that is different from designing a heuristic optimizer:

> **How much of the auxiliary representation is intrinsically necessary for an exact optimum?**

An unrestricted frame Pauli may act on arbitrarily many of the `n` system qubits. It is not obvious that spread support is wasteful because all cost components are coupled. Adding one frame letter increases the anticommuting-rotation cost but can alter the minimum Tag compatible with all blocks or change whether several Restore strings share a factorizable local letter. A purely local sparsity argument is therefore insufficient.

We solve this support-complexity problem exactly for the frozen three-block R6M TARE-M2 grammar used throughout the ORION-Q programme. Define the **intrinsic uniform support number**

\[
\kappa_{\mathrm{R6M}}
=\min\{k:\text{every admitted instance has an exact optimum with all frame supports}\le k\}.
\]

Our main theorem is the sharp identity

\[
\kappa_{\mathrm{R6M}}=2.
\]

The upper bound applies for arbitrary `n`, arbitrary admitted targets and every matching/permutation/central choice. The proof is short once the right local invariant is exposed: a two-bit parity class simultaneously tracks frame anticommutation and the shared-Tag label. A zero-sum subset exchange removes support while preserving both. A second elementary inequality bounds the Restore penalty analytically.

The lower bound is independent and exact. The complete support-one family—including arbitrary per-block anchors, every ordered anticommuting local pair, both global label orientations, every target permutation, and the minimum compatible Tag—loses on a two-qubit instance to a support-two optimum.

Three aspects make the result stronger than a loose normal-form upper bound.

1. **Sharpness.** Support two is both sufficient and sometimes necessary.
2. **Proof/optimizer agreement.** The only obstruction to pushing the exchange from support two to support one is exactly the parity pattern realized by the optimal support-two coupling witness.
3. **Predictive structure.** Before the all-size theorem was obtained, exact finite-domain work discovered interpretable coupling regimes and prospectively predicted a fresh public Hamiltonian's donor-exact behavior.

The paper is intentionally narrow about novelty. TARE itself, anticommuting unitary partitioning, Pauli-frame compilation, binary-symplectic simplification and Clifford synthesis all have established literatures. Our contribution is the sharp normal-form theorem and its coupling boundary for this declared TARE grammar/objective.

---

## 2. Compiler family and objective

### 2.1 Three-block shared-Tag TARE-M2 grammar

An instance contains six target Pauli strings grouped into three ordered two-term blocks `A,B,C`. Block `j` chooses two mutually anticommuting frame Paulis `(R_j0,R_j1)`, a permutation assigning its two targets to the two branches, and one branch as the cheaper central multiplier. All three blocks share one Tag Pauli `S`. A common label orientation requires the symplectic bits between `S` and the first/second frame branches to agree across blocks and to differ across the two branches.

The local Restore strings are

\[
T_{jk}=P_{j,\pi_j(k)}R_{jk}.
\]

Local Pauli phases are tracked in the exact referee, while the frozen structural objective depends on support and the donor-owned three-way common-factor rule.

### 2.2 Cost

For one block, each support unit beyond the first costs multiplier 4 on the noncentral branch and multiplier 2 on the central branch. The shared Tag costs `2 w(S)`.

For each branch `k`, the three Restore strings are charged coordinate-wise by

\[
F_3(a,b,c)=
\begin{cases}
1,&a=b=c\ne I,\\
w(a)+w(b)+w(c),&\text{otherwise},
\end{cases}
\]

where local `w` is 0 on identity and 1 otherwise.

The objective is therefore

\[
C=\sum_j Uanti_j +2w(S)+\sum_{k\in\{0,1\}}F_3(T_{Ak},T_{Bk},T_{Ck}),
\]

with the last term understood as a sum over qubit coordinates.

The unrestricted optimum `C_DP` is computed by the frozen exact R6M dynamic program. `D++` denotes the restriction in which every one of the six frame Paulis has global support at most two.

---

## 3. Sharp support theorem

### 3.1 A two-bit local class

Choose any feasible configuration and a frame Pauli `R` of support `w>=3`. Let `R'` be its anticommuting partner in the same block and `S` the shared Tag.

For every `q` in the support of `R`, define

\[
\alpha_q=\langle R_q,R'_q\rangle,\qquad
\beta_q=\langle S_q,R_q\rangle,
\]

and class

\[
c_q=(\alpha_q,\beta_q)\in\mathbb F_2^2.
\]

Global frame anticommutation gives

\[
\sum_q\alpha_q=1\pmod2.
\]

### 3.2 Zero-sum subset lemma

**Lemma 1.** If `w>=3` and the class multiset has odd total `alpha`, it contains a nonempty proper subset of size at most two whose class sum is `(0,0)`.

**Proof.** If class `(0,0)` occurs, choose that singleton. Otherwise the possible classes are `(0,1),(1,0),(1,1)`. If any repeats, two equal classes sum to zero and form a proper pair because `w>=3`. If no class repeats, there can be at most three entries; `w>=3` forces exactly the three nonzero classes, whose alpha-sum is `0+1+1=0`, contradicting odd total alpha. `square`

Let `Q` be the subset supplied by Lemma 1. Replace `R_q` by identity on every `q in Q`.

The total change in frame-partner symplectic parity is `sum_Q alpha=0`, so anticommutation is preserved. The change in the shared-Tag syndrome is `sum_Q beta=0`, so the **same Tag remains feasible**. Because `Q` is proper and has at most two elements, the modified `R` remains nonidentity.

### 3.3 Restore-cost lemma

The remaining issue is cost.

Write

\[
F_3(a,b,c)=W(a,b,c)-2\mathbf 1[a=b=c\ne I],
\]

where `W` is the number of nonidentity letters in the triple.

Consider zeroing one nonidentity frame letter `f` in one block at one qubit. If the target letter is `p`, that block's Restore letter changes from

\[
t_{old}=pf
\]

to

\[
t_{new}=p.
\]

**Lemma 2.** For arbitrary fixed Restore letters in the other two blocks,

\[
F_3(t_{new},u,v)-F_3(t_{old},u,v)\le2.
\]

**Proof.** Only one Restore letter changes, so the ordinary support count `W` can increase by at most one. If the old triple does not receive the all-equal discount, the result follows immediately (and any new discount only decreases cost).

Suppose instead that the old triple consists of three equal nonidentity letters, so losing the special factorization can add two units. Because `f` is nonidentity and `pf` is nonidentity, `p=f` is impossible. If `p=I`, the changed slot becomes identity and `W` decreases by one. If `p` is a nonidentity letter different from `f`, old and new slot letters are both nonidentity, so `W` does not increase. Thus destroying the old two-unit discount is accompanied by `Delta W<=0`, and the total increase is at most two. `square`

Every removed frame-support coordinate refunds at least two units: multiplier 2 on the central branch or 4 on the noncentral branch. Hence Lemma 2 implies that the exchange on each `q in Q` never increases total cost.

### 3.4 Global normal form

**Theorem 3 (support-two sufficiency).** Every feasible configuration can be transformed without increasing cost until every frame Pauli has support at most two. Consequently

\[
C_{DP}=C_{D^{++}}
\]

for every qubit count and admitted instance.

**Proof.** Whenever a frame has support at least three, apply Lemmas 1 and 2. Feasibility is preserved, cost does not increase, and total frame support strictly decreases. Repeating must terminate. Starting from an unrestricted optimum therefore yields a support-two optimum of the same cost. Since `D++` is itself a subset of the unrestricted family, the two optima are equal. `square`

The original R6S implementation independently exhausts the local cost table (18,432 cases, zero violations), checks 43,688 odd-alpha class tuples, performs 210 support-reduction descents, and verifies fresh `n=3,4` DP-versus-D++ panels. These computations are retained as regression/corroboration rather than as necessary logical steps of the proof.

### 3.5 Support one is impossible uniformly

Define `D+` as the complete all-support-one frame family. Its frozen enumeration sweeps:

- all `n^3` block-anchor triples;
- all six ordered distinct nonidentity local frame pairs per block;
- both common label orientations;
- all eight target-permutation combinations;
- the unique minimum compatible shared Tag.

The R6O protocol proves that using a nonminimum Tag cannot improve a member because Tag support is additive and independent of the Restore term.

An exact structured two-qubit instance (`instance_index=16`) satisfies

\[
C_{DP}=5<C_{D^+}=6.
\]

The unrestricted witness places a support-two frame Pauli on the cheaper central branch, allowing a lower-cost global Tag/Restore arrangement. Therefore no all-support-one frame configuration is optimal on this instance.

### 3.6 Intrinsic support number

Combining Theorem 3 with the exact support-one refutation gives:

**Corollary 4.**

\[
\boxed{\kappa_{\mathrm{R6M}}=2.}
\]

The threshold is attained already at two qubits.

---

## 4. Why two is the coupling boundary

The sharp support theorem was preceded by two exact closure refutations that expose the relevant global trades.

### 4.1 Local support dominance

R6N exhaustively tested local support-dominance inequalities over 688,041,472 configurations with zero violations. The result rules out a local reason for spread support to pay: each added frame-support unit costs at least as much as the maximum local Restore/factor saving.

The R6N protocol nevertheless declared one unresolved coupling before seeing the result: changing frame anchors changes the minimum shared Tag satisfying all blocks.

### 4.2 Tag-for-anchor trade

The declared gap produces an exact counterexample. In the `n2_b` instance, weight-one frames on split block anchors together with a weight-two `Y tensor Y` shared Tag give

\[
8=C_{DP}<9=C_{R6L}.
\]

The expanded weight-one family `D+` repairs this instance.

Here the compiler **pays Tag support to gain anchor freedom**.

### 4.3 Frame-for-Tag trade

R6O then refutes `D+` itself. The smallest witness has

\[
5=C_{DP}<6=C_{D^+}.
\]

A support-two frame on the cheap central branch buys a smaller Tag/better Restore alignment.

Here the compiler **pays frame support to save global Tag/Restore cost**.

### 4.4 The proof obstruction is the same mechanism

At support `w>=3`, Lemma 1 always supplies a proper subset preserving both parities. At `w=2`, it can fail. The four failing two-class patterns in the original R6S receipt have one coordinate locally commuting with the partner (`alpha=0`) while still anticommutes with the Tag (`beta=1`); deleting it flips the Tag syndrome.

That is exactly the coupling exploited by the R6O support-two optimum. The theorem cannot be sharpened to support one because the real optimizer realizes the combinatorial obstruction.

---

## 5. Consequence: polynomial-size direct normal-form family

The number of nonidentity `n`-qubit Paulis of support at most two is

\[
M_2(n)=3n+9\binom n2.
\]

The fixed R6M grammar has six frame slots, so every optimum lies among no more than

\[
M_2(n)^6=O(n^{12})
\]

raw frame tuples before feasibility constraints are imposed.

For a fixed frame tuple, no minimum-cost Tag needs support outside the union of the frame supports: all frame letters are identity there, so a Tag letter outside the union affects no symplectic label and only increases the Tag cost. The union contains at most twelve qubits. Therefore even brute-force Tag minimization over the union contributes only a grammar-constant factor.

This yields a simple polynomial-size direct candidate family for the fixed six-term grammar. We do **not** claim an algorithmic speedup over the production exact dynamic program, which already exploits stronger finite-state structure; the corollary is about representational complexity.

---

## 6. Finite-domain regime prediction

The all-size normal form does not require a complete taxonomy of all support-two optima. ORION-Q separately fitted/tested a smaller structural description around the first two discovered trades.

### 6.1 R6Q

A closed-form predicate compares the donor with:

- the split-anchor all-support-one family `D+`;
- a frozen weight-one-Tag borrow family `B(t)`.

It contains no unrestricted DP call and has zero donor-exactness classification errors over:

- 9,261 exhaustive structured `n=2` rows;
- 240 held-out seeded rows;
- 240 post-freeze fresh-seed rows;
- 30 recorded H4/equilibrium-N2 matchings.

Total: **9,771 registered instances**.

On those same domains, `C_DP=min(C_R6L,C_D+,f_B)`.

This is finite-domain exact evidence, not an all-`n` theorem.

### 6.2 Prospective R6R test

A selection rule frozen before reading candidate coefficients chooses a previously unread public benzene `cc-pVDZ` DUCC2 subject from a pinned Hamiltonian library. The regime prediction is committed and digest-printed before the unrestricted R6M DP is invoked.

All 15 perfect matchings are predicted `donor_exact`; all 15 later match the exact regime and cost.

### 6.3 Later counterexamples delimit the claim

After ORION-Q closed, the separate QG programme deliberately attacked the finite closed-form taxonomy and found additional support-two subregimes at higher `n`. This follow-up does **not** refute the support-two normal form or `kappa=2`. It demonstrates that normal-form complexity and taxonomy complexity are separate problems.

We disclose that later evidence here and make no universal two-trade claim.

---

## 7. Public-Hamiltonian grounding

### 7.1 H4 and equilibrium N2

For the 30 registered matchings across frozen H4 (`n=8`) and equilibrium N2 (`n=12`) six-term batches,

\[
C_{DP}=C_{D^{++}}=C_{D^+}=C_{R6L}.
\]

The finite R6Q diagnostics identify no profitable split/borrow move on those rows. These subjects therefore illustrate a useful consequence of the structural analysis: the expensive unrestricted optimizer can agree exactly with a simple donor because the relevant couplings are absent.

### 7.2 Coefficient majorization

A separate split-TARE result proves that, for equal-size coefficient groups, sorting coefficients and taking contiguous groups minimizes the outer-LCU normalization coordinate. The deterministic receipt reports zero failures across 8,700 exhaustive partition evaluations.

On a public LiH example the optimal split normalization is 0.90085 versus a random-split mean of 1.10415, with only 0.415% overhead relative to the Pauli-L1 value. The theorem is explicitly coefficient-coordinate only.

### 7.3 H2O structural Pareto point

The public H2O/cc-pVTZ DUCC instance contains 8,082 nonidentity Pauli terms on 20 qubits. A frozen implementation-aware structural compiler point reduces `C` from 8,078 to 4,972 (38.45%) with relative normalization overhead `9.087e-6`.

This is not a full fault-tolerant resource estimate and is included as grounding rather than as the theorem's novelty anchor.

---

## 8. Related work and exact novelty boundary

### TARE

Schillo, Sturm and Quay introduced TARE. We claim no novelty for the Tag/Restore primitive, anticommuting auxiliary unitary, or the existence of its compiler degrees of freedom.

### Anticommuting unitary partitioning

Prior unitary-partitioning work already exploits mutually anticommuting Pauli sets and normalized unitary combinations. This principle is donor-owned.

### Pauli-frame and binary-symplectic compilation

Frameworks including PCOAST, PHOENIX and Symphony use Pauli-frame or binary-symplectic transformations to optimize circuits and reduce Pauli support/weight. Therefore this paper does not claim the first support-reducing Pauli compiler or first Pauli-frame optimization.

### Hamiltonian-simulation synthesis and block-encoding complexity

Pauli-cluster diagonalization, Pauli-network methods, low-ancilla block encodings and recent sparse T-count lower/upper bounds form additional adjacent literatures. Our theorem is not a general block-encoding complexity bound.

A bounded hostile search dated 2026-08-22 did not locate a prior result equivalent to the **sharp uniform support theorem `kappa_R6M=2` for the declared shared-Tag TARE grammar**, but this is not external novelty certification. The exact theorem statement must be searched again before submission.

---

## 9. Discussion

### 9.1 A large representation can have a small intrinsic coupling scale

The unrestricted family permits support growing with `n`, but the exact optimum never needs more than two-qubit frame support. This is stronger than empirical sparsity: the coupling scale is bounded independently of system size.

### 9.2 Sharp normal forms can be easier than complete taxonomies

Later QG counterexamples show that additional support-two mechanisms exist beyond the first finite-domain split/borrow classification. Yet none can require support three. A compiler may therefore admit a simple exact normal form even when the internal phase diagram of that normal form remains rich.

### 9.3 The practical next question is objective dependence

The theorem is proved for the frozen support-count objective. Hardware-aware weights can change which structural trades are profitable, and later QG work explicitly finds objective-dependent support phases. The correct next step for application is not to generalize this theorem by rhetoric but to derive the corresponding phase regions under compiled resource models.

---

## 10. Claim boundary

We claim:

1. an analytic all-`n` support-two normal-form theorem for the frozen R6M grammar/objective;
2. an exact two-qubit support-one counterexample;
3. the sharp intrinsic uniform support number `kappa_R6M=2`;
4. correspondence between the proof's weight-two obstruction and an exact optimal coupling witness;
5. finite-domain zero-error R6Q classification on its 9,771 registered rows;
6. a prospectively frozen R6R fresh-subject confirmation;
7. bounded supporting chemistry/majorization results with their stated scopes.

We do not claim:

- novelty of TARE, unitary partitioning or Pauli-frame/symplectic optimization;
- support-two sufficiency outside the declared grammar/objective;
- a complete all-`n` two-trade taxonomy;
- algorithmic speedup over the existing exact DP;
- a universal block-encoding lower bound;
- full fault-tolerant resource advantage or physical quantum advantage.

---

## Reproducibility artifacts

- Main all-`n` receipt: `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`
- Analytic publication proof: `papers/Q-paper-01-tare-expressivity/HUMAN_PROOF_R6S_2026-08-22.md`
- Exact support-one counterexample: `research/extensions/orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json`
- Finite support-two closure: `MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json`
- Finite classifier: `MAX_R6Q_REGIME_PREDICATE_RESULTS.json`
- Prospective subject: `MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json`
- Fresh bounded novelty map: `NOVELTY_RESEARCH_2026-08-22.md`
- Claim ledger: `CLAIM_LEDGER_V2.md`

Before submission, the remaining non-negotiable gates are independent human proof review, clean public reproduction of headline artifacts, and a fresh external novelty search against the exact sharp theorem.

---

## Related-work anchors

1. N. Schillo, A. Sturm, R. Quay, *TARE: Block Encoding Linear Combinations of Pauli Strings Without Ancilla State Preparation*, arXiv:2601.05740 (2026).
2. A. F. Izmaylov et al., *Unitary Partitioning Approach to the Measurement Problem in the Variational Quantum Eigensolver Method*, JCTC 16 (2020).
3. E. van den Berg, K. Temme, *Circuit optimization of Hamiltonian simulation by simultaneous diagonalization of Pauli clusters*, Quantum 4, 322 (2020).
4. P. Mukhopadhyay, N. Wiebe, H. T. Zhang, *Synthesizing efficient circuits for Hamiltonian simulation*, npj Quantum Information 9, 31 (2023).
5. J. Paykin et al., *PCOAST: A Pauli-based Quantum Circuit Optimization Framework*, arXiv:2305.10966 / IEEE QCE 2023.
6. Z. Yang et al., *PHOENIX: Pauli-Based High-Level Optimization Engine for Instruction Execution on NISQ Devices*, arXiv:2504.03529 (2025).
7. Z. Yang et al., *Efficient Compilation for Hamiltonian Simulation via Global Binary Symplectic Form Simplification*, arXiv:2608.11579 (2026).
