# A Sharp Support-Two Normal Form for Shared-Tag TARE Quantum Compilation

**ORION-05 — recursive academic-paper-pipeline final editorial master**  
**Scientific cut:** exact intrinsic support number for the frozen R6M TARE-M2 grammar  
**Primary route:** Quantum / PRX Quantum stretch  
**Specialist fallback:** Theoretical Computer Science or npj Quantum Information  
**Authority:** `INTERNAL_REVIEW_PASS__BOUNDED_CLAIM / SUBMISSION_GATES_OPEN`

## Abstract

Auxiliary representation freedom can make a quantum compiler appear to require structures whose support grows with the system. We prove that this apparent complexity is unnecessary in a nontrivial shared-Tag Tag-and-Restore Encoding (TARE) family. For the frozen three-block TARE-M2 grammar under its declared support-count objective, the intrinsic uniform frame-support number is exactly two. Every admitted instance, at every qubit count, has an exact optimum in which each auxiliary frame Pauli acts on at most two qubits; and a complete support-one search has an exact counterexample with unrestricted optimum 5 and support-one optimum 6.

The all-size upper bound follows from a local exchange. Every active frame coordinate carries a two-bit class encoding its contribution to frame anticommutation and shared-Tag syndrome. A support-three-or-larger frame contains a nonempty proper zero-sum subset of at most two classes. Removing that subset preserves both symplectic constraints. At each removed coordinate the Restore cost can increase by at most two, while the frame-support refund is at least two, so total cost does not increase. Repetition yields a support-two optimum. The sharp support-two obstruction is not merely where the proof stops: it is the exact local pattern used by the optimum to trade a cheap frame coordinate against global Tag and Restore cost.

Independent finite enumerations reproduce the exchange inequalities and exact dynamic-programming comparisons, and a prospectively frozen structural prediction on a previously unread public benzene Hamiltonian is confirmed on all 15 registered matchings. These computations corroborate the theorem but do not supply its all-size authority. The result is specific to one grammar and objective. It does not establish a universal sparse-Pauli law, a fault-tolerant resource advantage, runtime superiority or quantum advantage. It establishes a sharp system-size-independent normal form for a coupled exact compilation problem.

## 1. Introduction

Quantum compilation often introduces auxiliary choices that are mathematically equivalent at the level of the represented operator but materially different under a resource objective. In block-encoding and unitary-partitioning settings, one may choose auxiliary Pauli frames, Tags, Restore factors, branch assignments and shared structure. More expressive representations can reduce cost, but they also enlarge the search space and obscure which degrees of freedom an optimum genuinely needs.

The relevant question is therefore not only whether an optimizer can search a rich family. It is whether the optimum has a smaller structural normal form:

> How large must an auxiliary frame support be to contain an exact optimum for every admitted instance?

We study this question for a frozen three-block shared-Tag TARE-M2 grammar. The grammar permits frame Paulis of arbitrarily large support. Local support is not obviously removable because a frame coordinate affects three coupled terms: its own weighted frame cost, the cheapest globally compatible shared Tag, and the local Restore strings. A coordinate that looks expensive locally can reduce the global Tag or make a common Restore factor available across blocks.

Let `kappa_R6M` be the smallest integer `k` such that every admitted instance has an exact optimum with every frame support at most `k`. Our main theorem is

`kappa_R6M = 2`.

The result has two logically independent parts. An all-size exchange proves support at most two is sufficient. An exact exhaustive obstruction proves support one is not uniformly sufficient. The theorem therefore identifies the intrinsic support scale rather than a loose ceiling from a particular search implementation.

The paper contributes:

1. a sharp support-two normal form for the declared grammar and objective;
2. a local exchange proof that preserves both frame and Tag symplectic constraints;
3. a complete support-one obstruction establishing sharpness;
4. a mechanistic interpretation of the support-two boundary;
5. independent bounded corroboration and a prospectively frozen public-Hamiltonian prediction, kept separate from theorem authority.

## 2. Compiler family and objective

An instance contains six target Pauli strings arranged in three ordered two-term blocks. Each block chooses two mutually anticommuting frame Paulis, assigns its target terms to those branches and marks one branch as the cheaper central multiplier. All three blocks share one Tag Pauli. A common orientation requires the Tag's symplectic relation to the first and second frame branches to agree across blocks and to differ between the two branches.

For target `P_jk` and chosen frame `R_jk`, the local Restore string is their Pauli product. The variable objective contains three components.

- **Frame cost.** Each frame coordinate above the weight-one baseline is charged by a branch multiplier `m` in `{2,4}`.
- **Tag cost.** The shared Tag contributes twice its support.
- **Restore cost.** At each coordinate, the three blockwise Restore letters receive the frozen common-factor rule: three equal nonidentity letters cost one; otherwise the ordinary local supports are added.

The unrestricted exact optimum is denoted `C_DP`. Let `C_D++` be the exact optimum after restricting every frame Pauli to support at most two while leaving every remaining choice exact. Let `C_D+` be the complete support-one optimum.

The exchange proof modifies one frame at a time and relies only on local conditions already present in the frozen grammar:

1. the modified frame stays nonidentity;
2. its anticommutation parity with its partner is preserved;
3. its symplectic parity with the common Tag is preserved;
4. target assignment, partner frames, other blocks and branch multipliers are unchanged;
5. Restore strings are re-evaluated under the original rule.

## 3. All-size support-two theorem

### 3.1 Two-bit coordinate classes

Take a feasible configuration containing a frame Pauli `R` of support at least three. Let `R'` be its anticommuting partner and `S` the common Tag. At each active coordinate `q`, define two bits:

- `alpha_q`, the local contribution to the symplectic parity between `R` and `R'`;
- `beta_q`, the local contribution to the symplectic parity between `S` and `R`.

The class `c_q=(alpha_q,beta_q)` lies in the four-element group `F_2^2`. Since `R` and `R'` anticommute, the sum of the first coordinates over the frame support is odd.

### 3.2 Small zero-sum subset

**Lemma 1.** Any multiset of at least three classes in `F_2^2` whose total first coordinate is odd contains a nonempty proper zero-sum subset of size at most two.

If the zero class occurs, that singleton can be removed. Otherwise, any repeated class gives a zero-sum pair. If neither occurs among three active coordinates, the three nonzero classes must all appear once; their first-coordinate sum is even, contradicting anticommutation. Larger supports force a repetition.

Removing the identified subset from `R` preserves both the frame anticommutation parity and the shared-Tag syndrome. Because the original support is at least three and at most two coordinates are removed, the frame remains nonidentity.

### 3.3 Restore penalty versus frame refund

At one coordinate, removing a frame letter changes only one of the three Restore letters. Under the frozen common-factor rule, the local Restore cost can rise by at most two. If the original triple did not receive the all-equal discount, changing one letter affects ordinary support by at most one and can only create, not destroy, a helpful discount. If the original triple was three equal nonidentity letters with cost one, destroying the discount yields a new local cost no greater than three.

Each removed frame coordinate refunds branch multiplier `m` in `{2,4}`. Therefore the local total change satisfies

`Delta C <= 2 - m <= 0`.

The selected subset has zero `beta` sum, so the Tag does not need repair and no hidden global charge appears.

### 3.4 Descent

Apply the exchange to any frame of support at least three. Total frame support strictly decreases and objective cost does not increase. Repeating terminates with every frame support at most two. Starting from an unrestricted optimum proves:

**Theorem 1.** For every admitted instance and every system size under the frozen grammar and objective,

`C_DP = C_D++`.

Thus `kappa_R6M <= 2`.

The proof is independent of finite extrapolation. It is also stronger than a statement that a production search happened not to use high support: it gives a transformation from any optimum containing high-support frames to an equally good support-two optimum.

## 4. Sharpness: support one is not enough

To prove `kappa_R6M=2`, support one must be tested as a complete family rather than as a hand-written donor menu. The exact support-one referee enumerates every anchor coordinate, all ordered local anticommuting Pauli pairs, both global label orientations, all target permutations, branch choices and the minimum compatible Tag.

On a registered exact two-qubit instance,

`C_DP = 5 < 6 = C_D+`.

The unrestricted optimum spends support two on the cheaper central frame branch. That additional local coordinate enables a globally cheaper Tag/Restore arrangement. Because the support-one family is exhaustive, the inequality is an exact obstruction, not a failure of one heuristic.

Combining the theorem and obstruction yields

`kappa_R6M = 2`.

## 5. The boundary is mechanistic

The two-bit exchange identifies the exact type of support-two pattern that cannot be simplified. At support two, four ordered class pairs fail the zero-sum deletion condition. In these patterns, a coordinate can be redundant for local frame anticommutation yet still carry shared-Tag syndrome. Deleting it breaks the global orientation relation.

The `5<6` optimum realizes precisely this trade. It pays one extra coordinate on a cheap frame branch to reduce a global coupled cost. Support two is therefore not merely the smallest value our proof reaches. It is the smallest support at which the grammar can express a real frame-for-Tag coupling currency.

This distinction also explains why a sharp normal form need not produce a tiny closed-form regime taxonomy. Later exact work finds additional support-two subfamilies beyond the first split and borrow mechanisms. Those counterexamples refine the interpretation inside the support-two envelope; they do not challenge the envelope theorem.

## 6. Corroboration and prospective evidence

Several bounded checks test the proof's executable interpretation.

- 18,432 complete local cost cases produce no violation of the Restore/refund inequality.
- 43,688 odd-`alpha` class tuples through support eight produce no support-three-or-larger failure and reproduce the exact support-two obstruction patterns.
- Seventy fresh `n=3,4` exact comparisons satisfy `C_DP=C_D++`.
- Two hundred ten seeded exchange descents match the predicted and observed cost changes at every step.

Before the all-size proof was completed, a structural regime prediction was frozen on a previously unread public benzene/cc-pVDZ DUCC2 Hamiltonian. The donor-exact regime and cost were committed before the unrestricted referee was opened, and all 15 registered matchings confirmed the prediction.

This forward-use evidence is scientifically useful, but its role is limited. The theorem proves the all-size normal form. The finite checks test code and transcription. The prospective subject shows that a structural model could be used before exact opening. None of the latter two is allowed to borrow the theorem's authority.

## 7. Public-Hamiltonian grounding

On thirty registered H4 and equilibrium-N2 matchings, the unrestricted, support-two, support-one and local donor costs coincide. These are an important no-value control: not every realistic instance exercises the support-two trade.

A separate H2O/cc-pVTZ DUCC subject contains 8,082 nonidentity Pauli terms on 20 qubits. A frozen structural compiler point reduces one registered cost coordinate from 8,078 to 4,972, approximately 38.45%, at relative normalization overhead `9.087e-6`. This observation is supporting implementation-aware evidence. It is not a complete logical-resource estimate and does not enter the proof.

## 8. Relation to prior work

TARE, Tag/Restore factoring, anticommuting unitary partitioning and auxiliary-frame freedom are donor-owned. Pauli-frame and binary-symplectic literatures already contain support-reducing transformations. Exact synthesis and restricted-family optimization likewise predate this paper.

The residual is narrower: the exact uniform optimum-support threshold for the declared shared-Tag TARE-M2 grammar and objective, including a proof that high support can always be removed and a complete obstruction below the threshold. The result is indexed by both grammar and objective. Reweighting can alter the balance between local frame refunds and global Tag/Restore costs; a separate proof is required before transferring the theorem to another resource model.

## 9. Limitations

The theorem applies to one six-slot grammar, one common-Tag structure and one frozen support-count objective. It does not establish a normal form for arbitrary TARE variants, general block encodings, full circuits or hardware-aware cost functions. It does not imply that a current implementation searches the support-two family in optimal time. The raw family remains polynomially large in a fixed-slot setting, but no production runtime complexity result is claimed.

The public-Hamiltonian cases are small in number and chosen for structural grounding rather than population inference. The prospective benzene result is one subject with 15 matchings, not an estimate of predictive reliability.

## 10. Reproducibility and availability

The release should bind the theorem and proof, complete support-one referee, exact obstruction witness, support-two evaluator, unrestricted referee used for bounded checks, exchange tests, public-Hamiltonian preprocessing and the prospectively frozen prediction record. The final paper must distinguish proof authority from machine corroboration in captions, abstract and conclusion.

## 11. Conclusion

The frozen shared-Tag TARE-M2 family permits auxiliary frame support that grows without bound, yet no exact optimum needs support greater than two. A parity-preserving local exchange removes every support-three-or-larger frame at non-increasing cost, while a complete support-one counterexample proves the threshold is sharp. The same support-two pattern that blocks the exchange is the pattern an optimum uses to trade local frame complexity for lower global Tag and Restore cost.

The result replaces an apparently unbounded auxiliary degree of freedom with a sharp constant-support normal form. Its value is structural and exact, but deliberately local to the stated compiler and objective.

---

## Editorial production note — not manuscript prose

Adoption must preserve `MANUSCRIPT_V3_REFINED.md`, `CLAIM_LEDGER_V3.md`, the exact theorem/obstruction distinction and the current submission-date novelty boundary. Rebuild the chosen Quantum/PRX/npj/TCS package, figures, references, archive, licence, anonymous/named surfaces and final PDF from the adopted bytes. No current production gate authorizes a broader quantum-resource or runtime claim.
