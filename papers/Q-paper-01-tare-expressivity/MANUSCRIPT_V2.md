# Sharp Support-Two Normal Forms and Coupling Regimes in Shared-Tag TARE Quantum Compilation

**Manuscript V2 — 2026-08-22.** This version supersedes `MANUSCRIPT_V1.md` for publication planning but preserves V1 unchanged as a historical research snapshot. Every quantitative statement below is tied to a committed ORION-Q receipt. The TARE primitive and its underlying Tag/Restore construction are donor-owned. No internal receipt grants novelty, physical quantum advantage, or R6 authority.

---

## Abstract

Tag-and-Restore Encoding (TARE) converts linear combinations of Pauli strings into block encodings by introducing mutually anticommuting auxiliary Pauli frames, shared Tag operators, and Restore corrections. Those auxiliary choices create a large joint compilation space whose exact structural complexity is not obvious from the construction itself. We characterize that space for a frozen three-block shared-one-bit-Tag TARE-M2 grammar with donor-owned three-way Restore factoring under a frozen support-count objective.

Our main result is a **sharp all-size normal-form theorem**. Let `kappa_R6M` be the smallest integer `k` such that every admitted instance at every qubit count has an exact optimum in which every auxiliary frame Pauli has support at most `k`. A machine-checked exchange proof establishes `kappa_R6M <= 2`: for every `n`, every target six-tuple, matching, permutation, and central choice, support-three-or-larger frame Paulis can be reduced without increasing cost, so the support-two family `D++` always attains the unrestricted optimum. The proof reduces the global statement to an `F_2^2` zero-sum exchange lemma and an exhaustive 18,432-case local cost inequality. The bound is tight. An exact two-qubit counterexample has unrestricted cost 5 while every all-support-one frame compilation costs at least 6, giving `kappa_R6M > 1`. Hence

`kappa_R6M = 2`.

The proof boundary is itself informative: the exchange construction fails exactly on four weight-two class patterns, and those patterns coincide with the previously discovered frame-for-Tag coupling mechanism that makes support two strictly optimal. A second exact mechanism trades shared-Tag support for split frame anchors. On registered finite domains, a structural split/borrow predicate classifies donor exactness with zero error over 9,771 instances without calling the unrestricted dynamic program, and a prospectively frozen prediction on a previously unread public benzene DUCC subject is confirmed on all 15 matchings. The all-size support theorem is independent of this finite-domain taxonomy: later adversarial follow-up work finds additional support-two subregimes at higher `n`, leaving the sharp support threshold intact while preventing promotion of the finite classifier to an all-`n` trade taxonomy.

The result turns an apparently arbitrary-support compiler representation into an exact support-two normal form and identifies the smallest support at which global coupling can genuinely pay. Supporting results include a coefficient-majorization theorem for split-TARE normalization and an implementation-aware Pareto point on a public 20-qubit H2O Hamiltonian with 8,082 nonidentity Pauli terms. All claims remain bounded to the declared compiler grammar and objective; no general block-encoding, fault-tolerant-resource, or physical quantum-advantage claim is made.

---

## 1. Introduction

Block encodings are a central input model for quantum signal-processing and singular-value-transformation algorithms, but the cost of constructing the encoding can dominate the useful computation. The recently introduced Tag-and-Restore Encoding (TARE) method of Schillo, Sturm and Quay addresses one part of this problem for linear combinations of Pauli strings: coefficient magnitudes are absorbed into an anticommuting auxiliary unitary, a Tag distinguishes branches, and Restore operations map the auxiliary frame back to the target Pauli strings. TARE therefore avoids conventional ancilla state preparation while exposing a new compilation problem: the physical operator being encoded is fixed, but the auxiliary frame, Tag, target assignment, and Restore realization are not.

This paper asks a structural question rather than proposing another heuristic search rule:

> **How complicated must an exact optimum of that auxiliary design space be?**

For the shared-Tag TARE-M2 family studied here, the unrestricted representation allows frame Paulis with support spread over an arbitrary number of system qubits. A priori, a high-support frame might be worthwhile because additional frame letters can alter several coupled costs at once: the Uanti implementation cost, the minimum shared Tag needed to label the branches, and the amount of common-factor cancellation available across three Restore strings. Local intuition is therefore unreliable. A letter that is expensive in one component can make a global Tag or Restore factor cheaper elsewhere.

The main result is that this apparent unboundedness is unnecessary but not trivial. The family has an exact intrinsic support number of two:

\[
\boxed{\kappa_{\mathrm{R6M}}=2.}
\]

Here `kappa_R6M` denotes the minimum uniform support cap guaranteed to contain an optimum for **every** admitted instance and **every** qubit count under the frozen grammar and objective. The two directions of this equality come from different kinds of evidence. The upper bound is an all-`n` composition theorem: every support-three-or-larger frame Pauli admits a cost-nonincreasing exchange to a smaller support. The lower bound is an explicit exact counterexample where every support-one frame family loses to a support-two optimum.

This sharpness matters. A theorem of the form “support at most two suffices” could otherwise be an artifact of a loose proof. Here the proof itself fails precisely at weight two, and the failing combinatorial patterns are exactly the structures realized by the independently discovered weight-two coupling trade. Thus the obstruction is not merely observed in a benchmark; it is visible simultaneously in the optimizer, the counterexample, and the proof boundary.

The paper makes five contributions.

1. **Sharp all-size normal form.** We prove that support at most two always suffices and that support one does not, establishing `kappa_R6M = 2` for the frozen R6M grammar/objective.
2. **Mechanistic support boundary.** A machine-checked local dominance analysis and an `F_2^2` exchange argument explain why support `>=3` is removable and why weight two is exceptional.
3. **Exact coupling counterexamples.** We exhibit two minimal mechanisms that break the simplest weight-one donor family: Tag-for-anchor splitting and frame-for-Tag borrowing.
4. **Finite-domain structural prediction.** On registered finite panels, a closed-form split/borrow predicate predicts donor exactness without the unrestricted dynamic program, and a prospectively frozen public-subject test confirms the prediction on every matching.
5. **Applied grounding with strict claim boundaries.** We connect the structural theory to coefficient partitioning and public chemistry Hamiltonians while explicitly separating proxy/structural cost from full compiled-resource claims.

The result is deliberately narrower than a general theorem about Pauli compilers. Pauli-frame optimization, binary-symplectic simplification, commuting/anticommuting grouping, and Clifford synthesis have substantial prior literatures. Our claim concerns the exact normal form and coupling structure of one declared shared-Tag TARE grammar. That restriction is scientifically load-bearing: later work under different objectives and related grammars exhibits different support phases.

---

## 2. Frozen compiler family

### 2.1 Pauli representation

An `n`-qubit Pauli is represented by local letters in `{I,X,Y,Z}` or equivalently by its binary symplectic `(x,z)` representation. `w(P)` denotes the number of nonidentity letters of Pauli `P`.

The target instance contains six nonidentity Pauli strings grouped into three ordered two-term blocks `A`, `B`, and `C`. Each block selects two anticommuting auxiliary frame Paulis `(R_j0,R_j1)`, a target permutation, and one of the two branches as the cheaper central branch. A global shared one-bit Tag `S` must give a common label orientation across the three blocks. Restore strings are target-frame products.

The exact frozen definitions and the dynamic-programming referee are in:

- `research/extensions/orion-q/MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json`;
- `research/extensions/orion-q/max_r6m_exact_three_tare2_shared_factor_dp.py`;
- the R6P/R6S protocols under `development/orion-q-max-r0/`.

### 2.2 Frozen support-count objective

For each block, the noncentral frame branch pays multiplier 4 per support unit beyond the first and the central branch pays multiplier 2. The shared Tag pays twice its support. Restore cost uses the donor-owned all-three common-factor rule `F3`, which charges one unit on a coordinate when all three Restore letters agree and are nonidentity, and otherwise charges their summed local supports.

Schematically,

\[
C = \sum_j Uanti_j + 2w(S) + \sum_{k\in\{0,1\}}F_3(T_{Ak},T_{Bk},T_{Ck}).
\]

The unrestricted exact optimum `C_DP` is computed by a proof-carrying dynamic program that was independently checked against brute force on frozen hostile domains.

### 2.3 Nested compilation families

We use three restricted families.

- **R6L / D:** weight-one frames sharing a common anchor and a weight-one Tag.
- **D+:** all frame Paulis remain weight one, but block anchors may differ and the compatible shared Tag is chosen at minimum weight.
- **D++:** every frame Pauli may have global support at most two and the shared Tag is optimized exactly.

Because these are nested restrictions of the same grammar,

\[
C_{DP}\le C_{D^{++}}\le C_{D^+}\le C_{R6L}.
\]

The central question is whether any of those inequalities must remain strict.

---

## 3. Main theorem: the intrinsic support number is exactly two

### 3.1 All-`n` support-two sufficiency

**Theorem 1 (R6S support-two normal form).** For every qubit count `n`, every admitted target six-tuple, every perfect matching into three blocks, every relative target permutation, and every central-branch choice in the frozen R6M grammar under the frozen support-count objective,

\[
C_{DP}=C_{D^{++}}.
\]

Equivalently, there always exists an exact optimum in which every auxiliary frame Pauli has global support at most two.

**Proof mechanism.** Consider a support-`w` frame Pauli `R` with `w>=3`, its anticommuting partner, and the shared Tag. For every qubit in `supp(R)`, form the two-bit class

\[
(\alpha,\beta)
=
(\langle R_q,\text{partner}_q\rangle,
 \langle S_q,R_q\rangle)
\in \mathbb F_2^2.
\]

Because the full frame pair anticommutes, the class multiset has odd total `alpha`. The R6S zero-sum lemma proves that every such multiset of size at least three contains a nonempty proper subset `Q` of at most two coordinates with zero `alpha` and zero `beta` sum. Zeroing `R` on those coordinates therefore preserves both the required frame anticommutation parity and the Tag syndrome: no Tag repair is needed.

It remains to show that the Restore penalty caused by zeroing those letters cannot exceed the Uanti refund. This is a finite local statement. Lemma E exhaustively enumerates 18,432 local configurations and finds zero violations; the maximum Restore-factor increase is exactly the minimum central support refund, and ties occur only at the central multiplier. Applying this exchange repeatedly decreases total frame support without increasing cost. A lexicographically minimum optimum therefore contains no frame with support at least three. The exact Tag-relaxation identity inherited from R6P then yields `D++ = DP`.

The machine receipt additionally checks 43,688 odd-alpha class tuples and 70 fresh `n=3,4` DP-versus-D++ instances, with 210 seeded exchange descents reproducing every predicted cost delta. These checks corroborate rather than replace the exchange proof.

Source: `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`.

### 3.2 Support one is insufficient

**Proposition 2 (exact support-one refutation).** There exists an admitted two-qubit R6M instance whose unrestricted optimum is strictly smaller than the optimum over all support-one frame compilations.

The smallest registered structured counterexample (`R6O`, `instance_index = 16`) has

\[
C_{DP}=5 < 6=C_{D^+}.
\]

`D+` contains the full frozen support-one frame family: every block may choose an arbitrary weight-one anchor and the shared Tag is chosen at minimum compatible weight. The exact DP witness spends a support-two frame Pauli on the cheap central branch, purchasing a lower-weight shared Tag and better Restore-factor alignment. The witness is independently re-evaluated in the R6P closure receipt.

Source: `research/extensions/orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json` and `MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json`.

### 3.3 Sharp normal-form corollary

Define

\[
\kappa_{R6M}=
\min\{k:\ \forall\text{ admitted instances, an optimum exists with frame support}\le k\}.
\]

Theorem 1 gives `kappa_R6M <= 2`; Proposition 2 gives `kappa_R6M > 1`. Therefore:

**Corollary 3 (sharp intrinsic support number).**

\[
\boxed{\kappa_{R6M}=2.}
\]

The threshold is already attained at `n=2`.

This is the paper's primary theorem statement.

### 3.4 Candidate-family corollary

The number of nonidentity `n`-qubit Paulis of support at most two is

\[
M_2(n)=3n+9\binom{n}{2}.
\]

There are six frame slots in the fixed three-block grammar, so R6S places every optimum inside at most

\[
M_2(n)^6=O(n^{12})
\]

raw frame tuples before anticommutation/Tag constraints are enforced. Target permutations and central choices contribute only constant factors. A minimum compatible Tag never needs support outside the union of the six frame supports, which contains at most 12 qubits; letters elsewhere affect no frame-Tag syndrome and only increase support cost.

Thus the theorem converts the unrestricted representation into a **polynomial-size direct normal-form candidate family** for this fixed six-term grammar. This is a representational-search corollary, not a statement that the existing exact DP had exponential running time.

---

## 4. Why the threshold is two: coupling trades

The sharp theorem emerged from a sequence of deliberately refuted closure hypotheses. Those refutations identify the global coupling that a purely local support argument misses.

### 4.1 Local support dominance

R6N first tested whether additional frame support can ever buy enough Restore/factor saving to repay its Uanti cost. Three complete local domains were checked:

| component | configurations | violations | maximum savings/cost |
|---|---:|---:|---:|
| R6M per-qubit support dominance | 536,870,912 | 0 | 1.000 |
| R6M letterwise F3 exchange | 175,616 | 0 | — |
| R6I rank-2 local support dominance | 150,994,944 | 0 | 0.333 |

Total local configurations: **688,041,472**, zero violations.

This proves that spread support cannot profit through the local Uanti/Restore accounting alone. R6N deliberately left one global gap: changing frame anchors can change the minimum compatible Tag.

### 4.2 Trade I: Tag for anchor freedom

The declared R6N gap immediately produced an exact counterexample. On the frozen panel `n2_b`, the unrestricted optimum uses weight-one frames anchored on different qubits and a weight-two shared Tag `Y tensor Y`:

\[
C_{DP}=8 < 9=C_{R6L}.
\]

The expanded all-weight-one family `D+`, which allows arbitrary per-block anchors and optimizes the compatible Tag, recovers cost 8. The local frames did not need to become more complicated; the global Tag did.

Interpretation: **pay one unit of Tag support to free the block anchors and improve the total compilation.**

### 4.3 Trade II: frame support for Tag compression

R6O then asked whether `D+` was complete. It was not. On 486 of 9,261 exhaustive structured `n=2` instances and 73 of 240 seeded random instances, the unrestricted DP beats every all-support-one frame compilation. The minimal witness has

\[
C_{DP}=5 < 6=C_{D^+}.
\]

Here the compiler does the converse of Trade I: it spends support two on a central frame Pauli, where support is relatively cheap, to compress the shared Tag and improve Restore alignment.

Interpretation: **pay frame complexity to save Tag/Restore complexity.**

### 4.4 The proof fails exactly on the same weight-two obstruction

The later R6S exchange proof identifies four failing `w=2` class tuples. In each, the locally commuting coordinate of the frame still anticommutes with the shared Tag, so removing that coordinate requires a Tag-syndrome change. This is exactly the structural circumstance exploited by the R6O support-two optimum.

At `w>=3`, the zero-sum subset lemma guarantees a proper subset whose removal preserves both relevant parities. At `w=2`, it need not exist.

Thus the optimization counterexample and the all-size proof independently locate the same boundary. That is the main mechanistic reason the number two is scientifically meaningful.

---

## 5. Finite-domain regime classification and prospective prediction

The all-size support theorem does not by itself enumerate every possible support-two subregime. ORION-Q separately studied a smaller finite-domain taxonomy based on the first two discovered mechanisms.

### 5.1 R6Q finite-domain predicate

R6Q defines a structural predicate using two closed-form profitability tests:

1. whether splitting weight-one anchors lowers cost (`R6L` versus `D+`);
2. whether the frozen weight-one-Tag borrow family `B(t)` beats the donor.

The selected predicate contains no unrestricted DP call. It has zero classification error on the registered panels:

- 9,261 structured `n=2` instances;
- 240 held-out seeded instances;
- 240 post-freeze fresh-seed instances;
- 30 H4/N2 chemistry matchings.

Total: **9,771 classified instances**, zero errors.

On the same domains,

\[
C_{DP}=\min(C_{R6L},C_{D^+},f_B).
\]

This equality is machine-evidenced on the registered finite domains, not proven for all `n`.

Source: `research/extensions/orion-q/MAX_R6Q_REGIME_PREDICATE_RESULTS.json`.

### 5.2 R6R prospective fresh-subject test

A stronger test froze the subject-selection rule before reading any candidate coefficients. The rule selected a previously unread public benzene `cc-pVDZ` DUCC2 Hamiltonian from a pinned public library commit. The regime prediction and digest were printed before the unrestricted R6M DP referee ran.

All 15 perfect matchings were predicted `donor_exact`; all 15 were confirmed, with exact cost agreement and witness checks passing.

Source: `research/extensions/orion-q/MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json`.

### 5.3 Known limitation from subsequent work

The Q1 claim is intentionally split into two authority levels:

- **all-`n` theorem:** support-two normal form and `kappa_R6M = 2`;
- **finite-domain evidence:** the specific R6Q two-trade closed form and predicate.

Subsequent ORION-QG adversarial work, performed after the ORION-Q programme closed, found additional support-two subregimes at higher `n`. Those results do not weaken the sharp support theorem. They do show that the R6Q finite-domain split/borrow taxonomy is not an all-size complete list of support-two mechanisms. We therefore make no such claim here.

This distinction is important for publication integrity: **the normal form is general within the frozen grammar; the simple regime classifier is not.**

---

## 6. Real-Hamiltonian grounding

### 6.1 Why the recorded chemistry batches are donor-exact

Across the frozen H4 (`n=8`) and equilibrium N2 (`n=12`) six-term batches, all 30 recorded matchings satisfy

\[
C_{DP}=C_{D^{++}}=C_{D^+}=C_{R6L}.
\]

R6Q's structural diagnostics explain this finite observation: the recorded batches are dominated by overlapping Z structure, the common weight-one anchor realizes the needed alignment, the split gain vanishes, and the borrow family cannot repay its support surcharge. The point is therefore not that the unrestricted optimizer “failed” on chemistry; within those batches, the simpler donor family is exactly sufficient.

### 6.2 Split-TARE coefficient majorization

A separate R4B theorem treats the coefficient coordinate. For equal-size split-TARE groups, sorting coefficients by magnitude and taking contiguous groups minimizes the outer-LCU subnormalization. The deterministic verification reports zero failures across 8,700 exhaustive partition evaluations.

On the public LiH subject, the optimal split has normalization 0.90085 versus random-split mean 1.10415, an 18.4% reduction relative to random splitting and 0.415% overhead over the Pauli-L1 value. On a 100-subject disordered-Heisenberg panel, the median reduction relative to random splitting is 12.4%.

This theorem concerns the coefficient coordinate only; it does not assert total compiled-resource optimality.

Source: `research/extensions/orion-q/MAX_R4B_TARE_SPLIT_MAJORISATION_RESULTS.json`.

### 6.3 Public H2O Pareto point

The R4D implementation-aware study uses a blob-locked public H2O/cc-pVTZ DUCC Hamiltonian with 10 spatial orbitals, 20 qubits, and 8,082 nonidentity Pauli terms. The coefficient-optimal point has `C=8078`. A greedy 1% normalization-slack compiler point gives

- normalization `82.2671701 -> 82.2679177`;
- relative normalization overhead `9.087e-6`;
- structural cost `8078 -> 4972`;
- reduction `38.45%`;
- direct pairs `2 -> 1555`.

This is a real-public-Hamiltonian structural/Pareto confirmation, not a full circuit, fault-tolerant, or physical quantum-advantage result.

Source: `research/extensions/orion-q/MAX_R4D_H2O_DUCC_CONFIRMATION_RESULTS.json`.

---

## 7. Related work and donor subtraction

The scientific claim of this paper starts **after** several well-established ingredients.

**TARE.** Schillo, Sturm and Quay introduced Tag-and-Restore Encoding and own the block-encoding primitive, Tag/Restore construction, use of mutually anticommuting auxiliary Paulis, and associated width/depth design space (`arXiv:2601.05740`).

**Anticommuting unitary partitioning.** Earlier unitary-partitioning work, including Izmaylov, Yen, Lang and Verteletskyi (JCTC 2020), establishes the value of grouping mutually anticommuting Pauli terms and normalizing their linear combination into a unitary. We claim no novelty for that principle.

**Pauli-frame and symplectic compilation.** Pauli-based compiler frameworks such as PCOAST (`arXiv:2305.10966`), PHOENIX (`arXiv:2504.03529`), and the recent Symphony global-BSF compiler (`arXiv:2608.11579`) optimize quantum programs through Pauli-frame or binary-symplectic transformations and explicitly reduce Pauli support/weight as part of synthesis. These works make broad claims such as “first Pauli support reduction” inappropriate here.

**Hamiltonian-simulation compilation.** Simultaneous diagonalization of Pauli clusters, circuit-level Hamiltonian-simulation synthesis, Pauli-network methods, and related Clifford/symplectic techniques provide an extensive donor neighborhood.

**Block-encoding complexity.** Recent 2026 work studies low-ancilla approximate block encodings and asymptotically optimal sparse-data T-count bounds (`arXiv:2607.01843`, `arXiv:2607.28260`). Our theorem is not a general block-encoding lower bound or a fault-tolerant-resource theorem.

The residual claim investigated here is narrower: **the exact sharp support normal form of the declared shared-Tag TARE-M2 joint compiler grammar, and the coupling obstruction that makes its support threshold equal to two.** A bounded novelty review dated 2026-08-22 is recorded in `NOVELTY_RESEARCH_2026-08-22.md`; it is not a substitute for an external submission-time search.

---

## 8. Discussion

### 8.1 A compiler representation can be globally complicated but intrinsically local

The unrestricted grammar permits auxiliary Paulis with support growing with `n`. The theorem says that no optimum needs that freedom: a support-two representative always exists. Yet support two is not removable universally. The optimal representation complexity therefore does not grow with the system size in this family, but it does retain a nontrivial two-qubit coupling scale.

### 8.2 The boundary comes from coupling, not local implementation cost alone

R6N's 688-million-configuration support-dominance check rules out a purely local reason for spread support to help. The successful support-two witness exploits the coupling between frame cost, Tag syndrome, and Restore factoring. This is why the proof needs to preserve both anticommutation and Tag parity simultaneously.

### 8.3 Normal-form complexity and regime-taxonomy complexity are different

The sharp support result survives later adversarial discovery of additional support-two regimes. This separation is useful conceptually. One can prove that every optimum lives in a small structural normal form without yet possessing a complete closed-form taxonomy of all optima inside that normal form.

### 8.4 What would raise the practical significance

The present resource objective is deliberately structural. A stronger applied claim would require mapping the normal form into compiled Clifford+T/native-resource models, incorporating PREP/SELECT/Tag/Restore implementation, routing, ancillas, error correction, and wall-clock cost. The N2 projection study already shows that hardware projection can reverse which representation is preferred; we therefore avoid a universal practical-superiority claim.

---

## 9. Claim boundary

This paper **does claim**, within the frozen R6M family and support-count objective:

1. the all-`n` support-two theorem `C_DP = C_D++`;
2. the sharp intrinsic support number `kappa_R6M = 2`;
3. exact counterexamples demonstrating the two original coupling mechanisms;
4. the R6Q finite-domain zero-error predicate on its registered 9,771 instances;
5. the R6R one-subject prospective confirmation;
6. bounded real-Hamiltonian grounding from H4/N2/H2O and the R4B coefficient theorem.

This paper **does not claim**:

- that TARE itself is new here;
- that support two suffices for other TARE grammars or other resource objectives;
- that the R6Q two-trade taxonomy is complete for all `n`;
- that support two is universally optimal for Pauli/block-encoding compilers;
- that the structural objective equals fault-tolerant physical cost;
- quantum advantage, algorithmic speedup, or a new quantum algorithm;
- first use of Pauli frames, anticommuting grouping, Clifford/symplectic reduction, or support-reducing Pauli compilation.

---

## 10. Reproducibility and evidence hierarchy

The result sequence is intentionally stronger than a benchmark-only claim:

1. exact local dominance audit with zero violations on complete finite domains;
2. explicit exact counterexamples to successive closure hypotheses;
3. exact finite-domain closure at support two;
4. finite-domain structural classifier fixed before post-freeze panels;
5. prospective public-subject prediction recorded before exact ground truth;
6. all-`n` support-two composition theorem with machine-checked finite lemmas.

All cited result files are committed under `research/extensions/orion-q/`; protocols were frozen before their result-bearing runs under `development/orion-q-max-r0/`. The protected stretched-N2 subject was not opened by the cited Q programme.

Before external submission we require:

- independent human proof audit of the R6S composition argument;
- fresh external novelty search against the exact `kappa_R6M = 2` theorem statement;
- clean reproduction script for the principal theorem certificate, counterexamples, R6Q panels, and figures;
- explicit separation of the later QG follow-up from this paper's Q-only primary claim set.

---

## References / related-work anchors

1. N. Schillo, A. Sturm, R. Quay, *TARE: Block Encoding Linear Combinations of Pauli Strings Without Ancilla State Preparation*, arXiv:2601.05740 (2026).
2. A. F. Izmaylov, T.-C. Yen, R. A. Lang, V. Verteletskyi, *Unitary Partitioning Approach to the Measurement Problem in the Variational Quantum Eigensolver Method*, J. Chem. Theory Comput. 16 (2020), DOI 10.1021/acs.jctc.9b00791.
3. E. van den Berg, K. Temme, *Circuit optimization of Hamiltonian simulation by simultaneous diagonalization of Pauli clusters*, Quantum 4, 322 (2020), arXiv:2003.13599.
4. P. Mukhopadhyay, N. Wiebe, H. T. Zhang, *Synthesizing efficient circuits for Hamiltonian simulation*, npj Quantum Information 9, 31 (2023).
5. J. Paykin et al., *PCOAST: A Pauli-based Quantum Circuit Optimization Framework*, arXiv:2305.10966 / IEEE QCE (2023).
6. Z. Yang et al., *PHOENIX: Pauli-Based High-Level Optimization Engine for Instruction Execution on NISQ Devices*, arXiv:2504.03529 (2025).
7. Z. Yang et al., *Efficient Compilation for Hamiltonian Simulation via Global Binary Symplectic Form Simplification*, arXiv:2608.11579 (2026).
8. Y. Zhang, C. Shao, *Low-ancilla block encodings via Hamiltonian simulation*, arXiv:2607.01843 (2026).
9. T. Li et al., *Optimal T Counts under Sparsity: from QROM to State Preparation and Block Encoding*, arXiv:2607.28260 (2026).
