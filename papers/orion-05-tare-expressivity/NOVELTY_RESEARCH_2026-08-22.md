# Q1 fresh hostile novelty research — 2026-08-22

Purpose: submission-oriented novelty threat map for the **final closed ORION-Q result**, not a self-grant of novelty. Search date: 2026-08-22. The result remains `NOT_R6` internally until external scientific review.

## Exact candidate claim searched

The strongest Q1 candidate is now:

> In the frozen three-block shared-one-bit-Tag TARE-M2 compiler grammar with donor-owned all-three Restore factoring and the frozen support-count objective, the smallest uniform frame-support bound containing an optimum for every instance and every qubit count is exactly two: `kappa_R6M = 2`. Support >=3 is exchange-removable without cost increase; an exact n=2 instance proves support one is insufficient.

Secondary claims searched:

- exact support-dominance/exchange mechanism;
- Tag-anchor and frame-for-Tag coupling counterexamples;
- structural regime prediction without unrestricted DP on frozen finite domains;
- coefficient-partition majorization and real-Hamiltonian grounding.

## Closest located literature / donor threats

### 1. TARE itself — direct donor, zero novelty credit

Niclas Schillo, Andreas Sturm, Ruediger Quay, **“TARE: Block Encoding Linear Combinations of Pauli Strings Without Ancilla State Preparation,”** arXiv:2601.05740 (2026).

TARE introduces the Tag-and-Restore block-encoding primitive, including mutually anticommuting auxiliary Pauli strings, transformation to target Paulis, logarithmic ancilla scaling, and width/depth tradeoffs. Q1 must not claim the primitive, Tag/Restore identity, or the existence/value of auxiliary-frame choices as novel.

### 2. Anticommuting unitary partitioning — direct conceptual donor

Artur F. Izmaylov, Tzu-Ching Yen, Robert A. Lang, Vladyslav Verteletskyi, **“Unitary Partitioning Approach to the Measurement Problem in the Variational Quantum Eigensolver Method,”** J. Chem. Theory Comput. 16, 190 (2020), DOI: 10.1021/acs.jctc.9b00791.

This literature owns the basic observation that mutually anticommuting Pauli sums can be normalized into unitaries and grouped/implemented as such. Q1 must not present anticommuting grouping or unitary partitioning as new.

### 3. Pauli-frame / Pauli-IR compiler optimization — strong adjacent threat

Jennifer Paykin et al., **“PCOAST: A Pauli-based Quantum Circuit Optimization Framework,”** arXiv:2305.10966; IEEE QCE 2023.

PCOAST represents Clifford action through Pauli frames and optimizes Pauli-parameterized circuit structures. It includes local-frame/factor-node support notions and greedy reduction of Pauli support. This is an important terminology/mechanism neighbor: Q1 should distinguish its result as an **exact uniform normal-form theorem for a particular block-encoding grammar**, not as the invention of Pauli-frame reduction.

### 4. High-level BSF Hamiltonian-simulation compilers — current adjacent threat

Zhaohui Yang et al., **“PHOENIX: Pauli-Based High-Level Optimization Engine for Instruction Execution on NISQ Devices,”** arXiv:2504.03529 (2025).

Zhaohui Yang et al., **“Efficient Compilation for Hamiltonian Simulation via Global Binary Symplectic Form Simplification,”** arXiv:2608.11579 (Symphony, 2026).

PHOENIX and Symphony optimize Pauli programs in binary symplectic form through Clifford transformations that reduce active Pauli weights/support and improve gate count/depth. Symphony is especially relevant because it performs holistic global BSF simplification and was posted in August 2026. The bounded search did **not** locate an all-instance theorem in these works equivalent to `kappa_R6M = 2`, but they substantially narrow any broad claim such as “first structural theory of Pauli support reduction.”

### 5. Pauli-cluster Hamiltonian-simulation optimization — adjacent donor

Ewout van den Berg and Kristan Temme, **“Circuit optimization of Hamiltonian simulation by simultaneous diagonalization of Pauli clusters,”** Quantum 4, 322 (2020), arXiv:2003.13599.

Priyanka Mukhopadhyay, Nathan Wiebe, Hong Tao Zhang, **“Synthesizing efficient circuits for Hamiltonian simulation,”** npj Quantum Information 9, 31 (2023).

These works establish substantial circuit savings by exploiting algebraic structure of Pauli collections. They are important related work but appear to optimize different simulation/synthesis objects than the shared-Tag TARE expressivity problem.

### 6. Block-encoding complexity is rapidly becoming theorem-heavy

Yuxin Zhang and Changpeng Shao, **“Low-ancilla block encodings via Hamiltonian simulation,”** arXiv:2607.01843 (2026), gives approximate low-ancilla alternatives to standard LCU constructions and discusses lower-bound barriers for exact constructions.

Tongyang Li et al., **“Optimal T Counts under Sparsity: from QROM to State Preparation and Block Encoding,”** arXiv:2607.28260 (2026), proves asymptotically optimal fault-tolerant T-count bounds for sparse QROM/state preparation/block encoding.

These papers do not appear to address the shared-Tag TARE frame-support normal form, but they mean Q1 should **not** be framed as a general block-encoding complexity theorem. Its exact scope must stay compiler-grammar specific.

## Bounded search conclusion

### Strongest residual novelty candidate

The bounded 2026-08-22 search did **not locate a direct prior statement equivalent to**:

\[
\kappa_{\mathrm{R6M}}=2
\]

for the frozen shared-Tag TARE-M2 grammar/objective, with:

1. an all-`n` exchange proof excluding support >=3;
2. an exact support-one counterexample proving sharpness;
3. the weight-two obstruction matching the failure boundary of the proof itself.

This is therefore the claim that deserves the most aggressive formal novelty review and should be the scientific center of Q1.

### Secondary residuals

- The explicit Tag-for-anchor and frame-for-Tag coupling mechanisms appear highly grammar-specific and were not located as named/exact TARE expressivity mechanisms in the searched literature.
- The R6Q finite-domain regime classifier is useful evidence but should not be sold as a universal taxonomy: later ORION-QG work found additional support-two subregimes at higher `n`.
- The R4B coefficient partition theorem should be treated cautiously as supporting mathematics; sorted-contiguous optimality may have classical rearrangement/majorization antecedents even if its TARE instantiation is useful.
- The H2O result is an applied confirmation, not a novelty anchor.

## Claims the revised paper should avoid

Do **not** claim any of the following without a substantially broader literature proof:

- first use of anticommuting Pauli grouping;
- first Pauli-frame optimization;
- first support-reducing Pauli compiler;
- first exact block-encoding complexity theorem;
- first hardware-aware/Pareto quantum compiler;
- universal support-two sufficiency beyond the frozen R6M objective/grammar;
- all-`n` completeness of the R6Q two-trade predicate;
- physical quantum advantage or full fault-tolerant resource advantage.

## Recommended submission claim

A defensible high-value abstract claim is:

> We give a sharp exact normal form for a nontrivial shared-Tag TARE compilation family. Under the specified grammar and resource objective, the unrestricted optimum always has frame support at most two for arbitrary system size, and support one is provably insufficient. The all-size exchange proof fails precisely on the weight-two class patterns realized by an explicit optimal coupling trade. Finite-domain exact classification and a prospectively frozen fresh-subject test provide additional evidence for the resulting regime picture.

## Search status

This is a **bounded hostile search**, not a novelty certificate. Before submission, repeat the search against:

- Google Scholar / Semantic Scholar / arXiv exact-phrase and citation-neighborhood searches;
- papers citing arXiv:2601.05740 after 2026-08-22;
- Pauli-network / Clifford-frame / symplectic-synthesis literature under alternative terminology;
- patents/software where exact support restrictions may be stated operationally rather than as theorems;
- any new versions of TARE, PHOENIX/Symphony, PCOAST, and related block-encoding manuscripts.
