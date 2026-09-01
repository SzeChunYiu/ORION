# Five-Paper Mathematical Engineering R3

Date: 2026-08-25

Branch: `research/five-paper-math-r3-20260825`

Scope: Papers A, B, C, D, and the non-quantum `C_5^3` generalized-Davenport paper. This campaign focuses on mathematics, proof ownership, reproducibility, and theorem-backed applications. It does not treat polished prose as a substitute for a missing theorem.

## 1. Outcome

The campaign recovered the formally audited V3 paper packages and then added a new theorem layer to every paper.

- **Paper A** now has exact direct-sum composition, quotient diagnostics, a finite multiplicity formulation, and approximate normal forms outside the exact objective cone.
- **Paper B** now has heterogeneous product theorems, a precise production-realization gate, proof-language monotonicity, and exact direct-enumeration asymptotics.
- **Paper C** now has a representation-wide fiber-diameter minimax theorem covering deterministic and randomized estimation, squared loss, exact intervals, and optimizer-property prediction.
- **Paper D** now has a coordinatewise Horn reduction, linear evaluation, a proof-footprint characterization of refutation, and an NP-completeness theorem for minimum seed intervention.
- **The non-quantum paper** now extends the unconditional rank-forcing frontier from `s+c_4<=24` to `s+c_4<=25` for `s>=23`, resolving the first previously silent diagonal by a rank-two Property-C argument.

An executable finite verifier, `verify_five_math_extensions_r4_v2.py`, replays the vulnerable arithmetic and finite reductions. It terminates with status `PASS` on the committed branch. The verifier is a sanity check, not a replacement for the written proofs or external donor theorems.

The honest editorial conclusion is not that five difficult papers became top-tier by declaration. Paper C is now the closest to a top-tier theory submission. Papers A and D are materially stronger selective-specialist candidates. Paper B has a rigorous framework but still lacks the production realization required for its most attractive numerical separation. The non-quantum paper contains genuine new structural progress but remains conditional because `C_0(31)` and the exact generalized-Davenport value are not proved.

## 2. Structured expert council

The following is an internal multi-role review council, not a claim that external named scholars participated.

### 2.1 Additive-combinatorics lead

**Background:** finite abelian groups, Davenport constants, inverse zero-sum theory, block monoids.

**Primary responsibility:** Paper A's restricted-alphabet invariant and the non-quantum paper's multiplicity, rank, and atom arguments.

**Adversarial question:** does every claimed support or rank bound follow from a proved deletion/inverse theorem, or is a computational observation being promoted to a universal statement?

### 2.2 Quantum-compilation and symplectic-algebra lead

**Background:** Pauli representations, exact compilation, sparse normal forms, proof-carrying optimization.

**Primary responsibility:** Papers A and B.

**Adversarial question:** is the abstract word/deletion model faithfully realized by the production compiler, and does the structural objective correspond to a meaningful compiler resource?

### 2.3 Information-based-complexity lead

**Background:** minimax decision theory, indistinguishability, sufficient representations, uncertainty quantification.

**Primary responsibility:** Paper C.

**Adversarial question:** which statements are classical consequences of indistinguishability, and which nontrivial work lies in constructing exact compiler fibers with solved target values?

### 2.4 Logic, provenance, and complexity lead

**Background:** Horn fixed points, provenance, monotone circuits, hitting set, retraction semantics.

**Primary responsibility:** Paper D.

**Adversarial question:** are cycles seed-founded under the least fixed point, and does the intervention problem really reduce to a finite proof-support antichain?

### 2.5 Skeptical editor and reproducibility lead

**Background:** mathematical peer review, claim-evidence auditing, executable artifacts, selective-journal triage.

**Primary responsibility:** all five papers.

**Adversarial question:** can a hostile reader identify the exact theorem, donor boundary, proof, executable check, limitation, and application consequence without reverse-engineering the repository?

## 3. Recursive research rounds

### Round 0 — baseline recovery

The first task was not theorem expansion but state recovery. The V2 surfaces contained two decisive defects that had already been repaired in a historical V3 publication state.

1. Paper D had previously conflated least and greatest fixed points. Unsupported positive cycles separate them. V3 correctly uses the least fixed point.
2. The non-quantum paper had previously used an invalid saturation move at an absent support point. V3 correctly appends a further copy of an existing support point.

The complete V3 directories, including verifier and submission-control artifacts, were recovered before new work began.

### Round 1 — theorem extraction

Each paper was assigned a theorem question rather than a prose question.

- A: what survives under composition and controlled objective-cone violation?
- B: exactly when does an abstract terminal budget become a production certificate?
- C: what is the minimax law for an arbitrary representation fiber?
- D: what is the complexity boundary between evaluation and optimal refutation?
- Non-quantum: can the first rank-silent diagonal be resolved analytically?

This round produced the five `MATHEMATICAL_EXTENSIONS_R4.md` addenda.

### Round 2 — hostile proof review

Every new result was checked against its nearest failure mode.

- A's direct-sum theorem is restricted to axis-separated alphabets; arbitrary alphabets may contain cross-coordinate letters and do not satisfy the stated equality.
- A's approximate theorem reports additive structural-objective loss; it does not imply fidelity, depth, or hardware guarantees.
- B's product lower theorem requires component lower witnesses and true independence.
- B's factor-five production interpretation remains unresolved because no realizing production terminal state is proved.
- C explicitly assigns generic midpoint/minimax arguments to donor mathematics; the compiler-specific contribution is the construction and exact solution of indistinguishable fibers.
- D keeps least-fixed-point semantics throughout and restricts the NP-hardness theorem to the declared seed-intervention problem.
- The non-quantum boundary step invokes an external Property-C theorem only at length 12 in rank two and does not infer `C_0(31)`.

### Round 3 — executable replay

The initial finite verifier exposed one ledger transcription error: along `s+c_4=25`, the formula

`c_1=2s-31+2c_4`

makes `c_1=19` in all three residual rows. The mathematical addendum was correct; the expected-data list in the first verifier was not. The superseding V2 verifier corrects the rows to

`(23,19,2,2)`, `(24,19,4,1)`, `(25,19,6,0)`

in `(s,c_1,c_2,c_4)` order and passes all checks.

### Round 4 — application engineering

Applications were admitted only when a theorem supplies an explicit bridge.

- finite-group normal forms -> exact search caps and modular preprocessing;
- certificate realization -> proof-carrying optimization and branch-and-bound budgets;
- fiber diameter -> architecture-independent lower bounds and valid uncertainty widths;
- Horn proof footprints -> exact impact recomputation and certified intervention;
- rank-forced repeated strata -> canonical-basis residual enumeration and block-monoid analysis.

Every application is labeled as a mathematical transfer route unless deployment evidence exists.

### Round 5 — selective-journal calibration

The final round separated mathematical correctness, standalone novelty, broad significance, and submission completeness. A paper can be theorem-correct but not yet suitable for a top-tier journal because its strongest interpretation depends on an unproved realization, an unresolved exact constant, or a missing overlap audit.

## 4. Paper A — compositional and robust zero-sum normal forms

### 4.1 New theorem package

1. **Axis direct-sum additivity**

   `zsf(H_1 direct_sum H_2; (A_1 x {0}) union ({0} x A_2))`

   `= zsf(H_1;A_1)+zsf(H_2;A_2)`.

2. **Homomorphic lower bound**

   For `phi:H->K`, `zsf(H;A)>=zsf(K;phi(A))`.

3. **Finite multiplicity formulation**

   The alphabet invariant is a finite integer optimization over multiplicities bounded by element orders, with exact nonzero-submultiset constraints.

4. **Approximate normal forms**

   If each semantic zero-sum deletion incurs at most `epsilon` per event or `delta` per deleted coordinate, support still descends to the exact alphabet budget with an explicit additive objective defect.

### 4.2 Mathematical value

The result is no longer only a one-instance support cap. It is compositional, computable for a frozen alphabet, and stable under controlled objective misspecification.

### 4.3 Remaining top-tier gate

The principal gate is production significance. The paper must either prove that the declared grammar faithfully captures a production-relevant compiler problem or present a broader theorem whose interest is independent of the motivating compiler.

## 5. Paper B — certificate realization and amplification

### 5.1 New theorem package

1. Terminal complexity is additive for heterogeneous independent shortening systems.
2. Intrinsic support is additive for independent compiler products with component lower witnesses.
3. An exact realization criterion identifies the four conditions required to transfer an abstract terminal lower witness to a production proof system.
4. Stronger sound proof languages have no larger terminal budget.
5. A direct labeled-support enumerator with fixed budget `B` has volume `Theta(n^B)`; reducing the verified budget from `B` to `K` removes a factor `Theta(n^(B-K))` in that declared architecture.

### 5.2 Mathematical value

The realization theorem turns a common abstraction error into a checkable condition. It also provides a modular theorem for composing independently verified certificate gaps.

### 5.3 Remaining top-tier gate

The attractive factor-five production separation remains unresolved. The paper should not be submitted with that interpretation until a production state realizes the abstract terminal word and survives every rule in the named production proof system. Without such a witness, the strongest route is to merge the framework with Paper A or demonstrate the criterion on several independent exact optimizers.

## 6. Paper C — exact information radius of compiler representations

### 6.1 New theorem package

For any finite representation `Phi:X->Y` and scalar target `T`, let `d_y` be the target diameter of fiber `Phi^{-1}(y)`.

1. deterministic absolute minimax radius is `d_y/2`;
2. integer-output radius is `ceil(d_y/2)`;
3. randomization does not improve worst expected absolute loss;
4. squared minimax risk is `d_y^2/4`;
5. every exactly valid interval has width at least `d_y`;
6. if a Boolean optimizer property differs inside one fiber, every randomized representation-only classifier has worst error at least `1/2`.

The existing pair-indistinguishable and high-order-parity families provide exact growing fibers inside the declared compiler model.

### 6.2 Mathematical value

The paper now states a general, exact representation theorem and then supplies nontrivial compiler fibers that separate value, structure, and unary-optimality decision. The applications to learned combinatorial optimization and uncertainty quantification follow directly from identical-input lower bounds.

### 6.3 Remaining top-tier gate

The theorem chain needs an independent hostile replay of the exact partition-family proofs and a final literature audit against hierarchical interaction models and information-based complexity. Subject to those checks, this is the strongest top-tier candidate in the portfolio.

## 7. Paper D — tractable evaluation, hard intervention

### 7.1 New theorem package

1. Set-valued least-fixed-point authority decomposes into one positive Horn closure per license.
2. A fixed refutation state is evaluated in linear time in the explicit rule-incidence size per license.
3. Direct refutation removes a target license exactly when it hits every inclusion-minimal finite proof footprint.
4. Minimum seed refutation is NP-complete even for an acyclic seed-to-intermediate-to-target rule graph.
5. Weighted intervention is the corresponding weighted hitting-set problem, while any proposed blocker remains linearly verifiable.

### 7.2 Mathematical value

The paper now has a sharp evaluation/intervention dichotomy rather than only a semantics layer. Least-fixed-point discipline also gives a principled answer to unsupported recursive agreement in multi-agent or evidence graphs.

### 7.3 Remaining top-tier gate

A primary-source overlap audit against database provenance, query resilience, and abduction is required. The paper also needs one fully worked domain instance demonstrating that rule caps and direct-refutation semantics answer a real provenance question rather than merely re-encode hitting set.

## 8. Non-quantum paper — expanded rank-forcing frontier

### 8.1 New theorem package

At the boundary `s+c_4=25`, the high-multiplicity subsequence has length 12. If it had rank at most two, the rank-two Property-C classification would force

`H=T^4`, `c_4=3`, `c_2=0`, `s=22`, `c_1=19`.

Therefore every residual sequence with `s>=23` and `s+c_4<=25` has a full-rank repeated stratum. The newly closed branches are

`(s,c_4)=(23,2),(24,1),(25,0)`.

In particular, every support-23 candidate now has three repeated support points forming a basis of `C_5^3`.

### 8.2 Mathematical value

This is an unconditional analytic advance over V3 and moves the first rank-silent diagonal from 25 to 26. It reduces the orbit structure of the residual exact search and gives a more constrained starting point for an atom-overlap theorem.

### 8.3 Remaining top-tier gate

The central exact threshold remains open in this packet. A top-tier resolution requires `C_0(31)`, an atom-overlap theorem excluding the residual four-atom corridor, or a comparably decisive inverse theorem. The current result is suitable as specialist structural progress, not as an exact-value announcement.

## 9. Cross-paper mathematical synthesis

The five papers share one theme: **a finite representation controls an exact optimization only through the transformations, information, or proof paths that the representation actually owns.**

- Paper A identifies the exact deletion invariant.
- Paper B identifies the realization boundary between an abstract invariant and a production certificate.
- Paper C quantifies what a representation cannot determine.
- Paper D identifies the finite proof paths that sustain authority and the interventions that hit them.
- The non-quantum paper reduces an exact factorization problem to a constrained finite residue by multiplicity and rank.

This synthesis is useful editorially: it supplies a coherent research program without pretending that the five manuscripts prove the same theorem or should be bundled into one submission.

## 10. Readiness ledger

| Paper | Proof status of new R4 mathematics | Standalone novelty | Reproducibility | Current editorial decision | Top-tier blocker |
|---|---|---|---|---|---|
| A | verified under explicit grammar and defect assumptions | moderate-to-strong specialist | executable finite checks plus written proofs | selective-specialist candidate | production relevance or broader abstraction theorem |
| B | verified; strongest numerical production claim deliberately unresolved | strong framework, incomplete flagship example | exact conditions and asymptotic replay | hold or combine | realizing production terminal witness |
| C | verified conditional on V3 family proofs | strongest in portfolio | exact formulas and finite replay | top-tier theory candidate after external audit | hostile proof replay and literature overlap audit |
| D | verified under least-fixed-point direct-refutation semantics | materially strengthened | finite reduction replay | strong specialist/broad-theory candidate | provenance overlap audit and worked application |
| Non-quantum | new boundary theorem verified using external Property C | genuine structural advance | arithmetic replay; donor theorem external | specialist note candidate | `C_0(31)` or decisive atom-overlap theorem |

## 11. Stop rule used in this campaign

Recursion stopped only when another pass no longer produced a defensible theorem without crossing one of four boundaries:

1. inventing a production realization not present in the repository;
2. promoting a finite computation to a universal proof;
3. claiming generic novelty for classical donor mathematics; or
4. declaring an open exact threshold solved without a complete argument.

The resulting branch contains substantial new mathematics for every paper and a precise ledger of what remains. It does not conceal unresolved flagship claims behind application language or editorial polish.