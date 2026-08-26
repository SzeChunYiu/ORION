# Exact Support Ceiling in Shared-Tag TARE Compilation: Counterexamples, an All-`n` Theorem, and the Limits of Closed-Form Regime Maps

**ORION-Q1 Manuscript V2 — publication-synthesis draft**  
Publication cut: `main@ca7df1055a43f97eaf8d142a62011c4c261af368`  
Claim authority: `CLAIM_LEDGER_V2.md` + `PUBLICATION_FOUNDATION_V2.md`

## Abstract

The TARE (Tag-and-Restore) block-encoding primitive leaves a nontrivial joint compilation space over auxiliary anticommuting frames, Tag structure, Restore assignments and branch placement. We ask an exact expressivity question for a frozen three-block shared-Tag TARE grammar under a raw support-count objective: **how much frame support can an exact optimum intrinsically require, and where do natural donor restrictions fail?** A complete local support-dominance analysis first shows that additional frame support cannot buy more Restore/factor savings than its direct cost, while exposing a specific Tag-coupling gap that prevents a naive global closure argument. Exact counterexamples then realize that gap. A common-anchor weight-one donor family is beaten by a split-anchor construction with cost 8 versus 9; the resulting enlarged family is itself beaten by a frame-for-Tag borrow with exact cost 5 versus 6. The central result is stronger than the original finite-panel story: a machine-checked exchange theorem proves that for **every qubit count and every instance of the frozen grammar/objective**, an exact optimum exists with all frame supports at most two, hence the unrestricted optimum equals the minimum over the full support-two family. The proof also localizes the support-two boundary: the exchange fails exactly at the registered weight-two coupling pattern, whereas support at least three is always reducible at non-increasing cost. A structural regime predicate is exact on 9,771 registered finite instances, and a prospectively frozen prediction on a previously unread public Benzene DUCC batch is confirmed on all 15 matchings. We do not promote those finite results to a universal closed form. Later companion counterexamples identify additional configurations *inside* the theorem-backed support-two family, refuting the original two-trade completeness interpretation while leaving the support theorem intact. Thus the durable result is an exact support ceiling plus counterexample-driven structure, not a brittle finite taxonomy. TARE itself and its donor compilation machinery receive no novelty credit.

## 1. Introduction

Block encoding linear combinations of Pauli operators is a central subroutine in quantum algorithms for simulation and linear algebra. The 2026 TARE construction of Schillo, Sturm and Quay (`arXiv:2601.05740`) removes the need for conventional ancilla state preparation by introducing Tag-and-Restore structure around Pauli terms. As with many compiler primitives, the construction exposes auxiliary degrees of freedom: one can choose anticommuting frames, assign targets to frame elements, choose the Tag structure, and place branches with different structural costs.

Those choices create two different scientific questions. An **optimization** question asks how to find a low-cost configuration. An **expressivity** question asks which restricted families are guaranteed to contain an exact optimum and which structural mechanisms make them fail. This paper addresses the second question for one precisely frozen grammar and objective.

The distinction matters because a successful heuristic can hide the boundary of the family it searches. A restricted donor family may appear exact on chemistry batches and large finite panels yet fail on a small adversarial instance. Conversely, the existence of such counterexamples does not imply that arbitrarily complex frames are required. The objective may have a structural support ceiling even when no small closed-form taxonomy is complete.

We study the R6M three-block TARE-M2 grammar with one shared Tag and the donor-owned all-three Restore common-factor rule, under a frozen raw support-count objective. The unrestricted optimum is computed by a proof-carrying exact dynamic program. The scientific sequence is deliberately counterexample-driven.

First, an exhaustive local analysis shows why high-support frames are expensive: the maximum possible Restore/factor saving from one unit of support does not exceed the corresponding frame cost. Crucially, the analysis declares rather than hides its coupling gap: removing a frame letter can change the Tag syndrome, so a global weight-one theorem does not follow.

Second, exact hostile instances realize that gap in two distinct ways. The first splits weight-one frames across anchors and pays for a spread Tag. The second spends a support-two frame on a cheap central branch to buy a cheaper Tag. Both are exact refutations of the then-current restricted family.

Third, we close the stronger question. A later all-`n` exchange theorem proves that **support above two never pays** under the frozen R6M objective. The unrestricted dynamic-programming optimum therefore equals the optimum over the entire support-two family for every qubit count and target six-tuple in scope.

Fourth, we separate this theorem from the more ambitious problem of finding a compact closed-form taxonomy inside the support-two world. An early two-trade predicate is exact on its registered panels and passes a prospectively frozen fresh-subject test. Later companion work nevertheless finds exact configurations outside that closed form. We treat those later refutations as the correct scientific boundary: they do not weaken the support theorem; they show that **support complexity and regime-classification complexity are different objects**.

The resulting contribution is therefore narrower and stronger than “two trades characterize TARE.” It is:

1. complete local support-dominance evidence with an explicit coupling gap;
2. exact counterexamples showing how weight-one restrictions fail;
3. an all-`n` support-two expressivity theorem for the frozen grammar/objective;
4. a bounded finite/prospective regime map whose later refutations are retained rather than overwritten;
5. chemistry/public-subject evidence used as validation rather than as generality authority.

All TARE primitives, Tag/Restore identities, anticommuting partitioning, Clifford/symplectic machinery and donor factoring rules are treated as prior work. No receipt cited here grants physical quantum advantage or the separate R6 compiled-resource novelty authority.

## 2. Frozen setting

### 2.1 Pauli representation and instances

Local Pauli letters are represented as `I,X,Y,Z`; implementation receipts use the frozen bit representation and symplectic operations bound in the ORION-Q R6 protocols. An R6M instance contains six non-identity target Paulis on `n` qubits, grouped into three ordered blocks `A,B,C`, each with two targets.

For each block `j`, a compilation chooses an ordered anticommuting frame pair `(R_j0,R_j1)`, a target assignment/permutation, and which frame branch receives the cheaper central multiplier. A shared Tag Pauli `S` must satisfy the common label orientation required across the blocks. Restore strings map the chosen frame representative to its target.

### 2.2 Frozen structural objective

The registered objective combines:

- frame/Uanti support cost with multiplier 4 on a non-central branch and 2 on the central branch;
- Tag cost `2 w(S)`;
- donor-owned all-three Restore common-factor cost `F3`.

We emphasize the scope: this is a **structural support-count objective**, not a full hardware cost. Results do not directly imply gate count, T count, logical qubits, physical qubits, runtime or fault-tolerant space-time cost.

### 2.3 Exact referee

The unrestricted optimum `C_DP` is computed by the committed exact dynamic program `max_r6m_exact_three_tare2_shared_factor_dp.py`. Earlier R6 work binds this DP to independent brute-force checks on the registered domains and stores exact witnesses. In this paper, exact counterexample means that the relevant configuration/cost is checked under that frozen mathematical referee.

### 2.4 Restricted families

We use four family labels.

**D / R6L.** Weight-one anticommuting frames at a common anchor, with the donor restricted shared-Tag construction.

**D+.** Weight-one frames may use different anchors, with the exact minimum compatible spread Tag.

**D++.** Full support-two family: frame Paulis may have global support at most two, with the corresponding exact Tag relaxation. This is the family appearing in the all-`n` theorem.

**Borrow families.** `B`, and later companion enlargements `B′/B″`, are interpretable closed-form subfamilies that realize particular support-two coupling mechanisms. They are useful for regime explanation but are not interchangeable with the full `D++` family.

Structural containments give

`C_DP <= C_D++ <= C_D+ <= C_R6L`,

and every explicit borrow-family minimum is also an upper bound on `C_DP` because its members are feasible configurations.

## 3. Local support dominance: why high support looks unnecessary

The first analysis asks a one-qubit-local question. If a frame Pauli uses an additional non-identity letter, how much direct Uanti cost does that incur, and how much can the added letter possibly save in Restore/factor terms?

Three exhaustive registered checks support the exchange picture:

- R6M per-qubit support dominance: 536,870,912 configurations, zero violations, maximum saving/cost ratio 1.000;
- donor F3 letterwise monotonicity: 175,616 configurations, zero violations;
- separate R6I rank-2 local domain: 150,994,944 configurations, zero violations, maximum ratio 0.333.

The R6M statement can be summarized as: each extra support unit costs at least the maximum Restore/factor saving it can generate locally. This strongly suggests a sparse optimum.

But it is **not a global theorem**. The local check deliberately identifies a missing term: Tag repair. Removing a frame letter can change the Tag syndrome needed to realize the shared label constraint. The cost of repairing the Tag is coupled across blocks and is not controlled by the local inequality.

This declared gap is scientifically important because it points directly to the first counterexample.

## 4. Counterexample I: Tag-anchor splitting defeats common-anchor weight one

The frozen hostile panel `n2_b` provides the first exact failure. The common-anchor weight-one donor family has minimum cost 9. The unrestricted exact optimum is 8.

The winning construction keeps every frame weight one but places block `A` on one anchor and `B,C` on another. The shared Tag becomes the weight-two spread Tag `Y⊗Y`. The resulting configuration has exact cost 8.

A diagnostic family allowing weight-one frames with arbitrary Tag realizes the same cost, isolating the mechanism: the donor's common-anchor coupling, not high frame support, is the binding restriction.

This gives **Trade I: Tag-anchor splitting**. It refutes common-anchor weight-one closure without saying anything yet about support-two necessity.

D+ is then frozen to admit arbitrary per-block anchors while computing the exact minimum compatible spread Tag. It closes the registered first-regime panels and the exhaustive `n=1` domain.

## 5. Counterexample II: a cheap support-two branch buys a cheaper Tag

D+ is still not complete. In the registered structured-`n=2` search, 486 of 9,261 instances and 73 of 240 seeded random instances contain an exact gap. The minimal structured witness has

`C_DP = 5 < 6 = C_D+`.

The mechanism is qualitatively different. A frame Pauli uses support two, but it is placed on the **central branch**, where the additional support is cheaper. That extra frame support changes the Tag relation in a way that allows a weight-one Tag and lowers total cost.

The exact witness records the cost ledger `0+0+2+2+1=5`; the best D+ member costs 6. This is **Trade II: frame-for-Tag borrow**.

The counterexample refines the local-dominance intuition. Extra support is not intrinsically useful for its local Restore contribution; it is useful because of a global coupling to Tag cost. The right question is therefore not whether support two can help—it can—but whether support above two can ever buy a qualitatively new advantage.

## 6. Finite support-two closure

The D++ family permits arbitrary support sets up to global support two while preserving the exact grammar constraints. Before the all-`n` theorem was available, D++ was tested on the complete/frozen domains relevant to the two discovered trades:

- 4,096 exhaustive `n=1` instances;
- 9,261 structured `n=2` instances;
- seeded random `n=2–3` panels;
- five hostile panels;
- 30 recorded chemistry matchings.

D++ matches the unrestricted exact DP throughout those domains and closes all 559 then-critical borrow instances with re-verified witnesses.

This finite result is important historically but is not the final authority. The coupling term could, in principle, have produced a support-three or larger exception at higher `n`. The next step therefore required an actual theorem rather than larger panels.

## 7. Main theorem: support two is sufficient for every `n`

### 7.1 The theorem

For every qubit count `n`, every target six-tuple, every matching, every target permutation and every central choice in the frozen R6M shared-Tag grammar under the raw support-count objective,

**the unrestricted exact optimum is attained by a configuration whose frame Paulis all have global support at most two.**

Equivalently,

`C_DP = C_D++`

for all instances in scope.

The committed authority is `MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED__SUPPORT3_NEVER_PAYS__DXX_EQUALS_DP_ALL_N__NOT_R6`.

### 7.2 Proof shape

The proof classifies each qubit in the support of a high-support frame by two binary relations: its local symplectic relation to the partner frame and its relation to the Tag constraint. Because the selected frame anticommutes with its partner, the resulting multiset has odd parity in the relevant component.

A finite `F_2^2` pigeonhole/exchange lemma shows that when frame support is at least three, there exists a **proper subset of at most two support positions** whose aggregate parity preserves both the anticommutation relation and the Tag syndrome. Removing that subset therefore needs **zero Tag repair**—the coupling term that blocked the earlier local argument disappears.

A second complete local inequality bounds the corresponding increase in the donor F3 Restore term by the support/Uanti refund. The registered Lemma-E domain contains 18,432 cases and zero violations.

Applying the exchange reduces total frame support without increasing cost. Induction on a lexicographic measure of cost and total support eliminates every support-three-or-larger frame from an optimal solution.

The theorem is exact for the named grammar/objective. It does not cover R6I, other cost weights, other Tag ranks or other compilation grammars.

### 7.3 The exact support-two boundary

The exchange has four failing class tuples at support two. They are not artifacts: they are exactly the pattern in which the locally commuting qubit also carries the relevant Tag relation, so removing it forces the Tag syndrome to flip. That is the registered weight-two borrow mechanism.

At support three and above, the parity lemma guarantees a proper zero-sum subset; the obstruction cannot persist in the same way. This makes the theorem more explanatory than a bare cap: it identifies **why support two is the boundary** for this objective.

### 7.4 Consequence for support-three necessity

An earlier open question asked whether some optimum might intrinsically require support at least three. Under the frozen R6M/raw-support objective, the theorem refutes that possibility. A support-three necessity claim is therefore false in this scope.

Different objectives can change this conclusion; companion QG work explicitly finds such objective-dependent counterexamples. That belongs to the regime-geometry paper, not to this theorem.

## 8. Bounded regime predicate and prospective confirmation

Having proved the support ceiling, one may still ask for a cheaper structural classifier that predicts which subfamily contains the optimum.

R6Q freezes a predicate

`P1(t) := [C_R6L(t)=C_D+(t)] AND [f_B(t) >= C_R6L(t)]`

for donor exactness. On its four registered panels—9,261 structured `n=2`, two 240-instance seeded panels, and 30 chemistry matchings—the predicate has zero classification error, covering 9,771 instances. The corresponding simple two-trade identity also holds throughout those panels.

This is **finite-domain evidence**, not an all-`n` theorem.

A separate prospective test then selects a previously unread public Benzene DUCC subject under a pinned library/eligibility rule. The prediction is recorded and digest-stamped before the unrestricted DP is opened. All 15 matchings are predicted donor-exact at cost 9 and all 15 match the later exact referee.

The prospective result matters because it tests the predicate beyond the data that produced it. It remains one frozen subject and does not license universality.

## 9. Later counterexamples: why the theorem must be separated from the regime map

After the 15/15 prospective confirmation, companion QG work continues to attack the closed form.

### 9.1 QG5: one missing borrow shape

A fresh seeded `n=3` row yields

`C_DP=10 < 11=C_R6L=C_D+=f_B`.

The support-two family remains exact at `C_D++=10`, as guaranteed by the theorem. The failure is therefore inside the support-two world: the closed-form borrow family omitted a phantom borrow whose home lies outside the block's own target support.

An enlarged `B′` family repairs that row and the registered successor panels.

### 9.2 QG7: a fourth configuration

A subsequent frozen hostile search finds 64 exact witnesses for which

`C_D++ < min(C_D+, f_B′)`.

The new shape combines a weight-two Tag with a phantom-borrow support-two frame. A separately frozen `B″` family closes the current finite hostile panels, but the current publication cut still leaves one all-`n` consolidation lemma open for the smallest named-family identity.

These results are not a failure of Q1. They clarify its strongest claim. **Support complexity is closed; compact regime classification remains an open/refutable research object.** QG1 owns the detailed later classification programme.

## 10. Chemistry and public-subject evidence

The original frozen chemistry batches contain 15 matchings each for H4 (`n=8`) and equilibrium N2 (`n=12`). On all 30 recorded matchings, the donor/D+/D++/DP costs coincide under the registered objective. The structural predicate explains these rows by showing that the split and borrow advantages are not profitable in the recorded instances.

The later Benzene prospective subject adds 15 more matchings under a deterministically selected public source. The protected stretched-N2 discriminator remains unread in every receipt used for Q1.

These results establish that the counterexample-driven mechanisms do not imply that donor configurations are usually wrong on the recorded chemistry subjects. They do **not** establish practical chemical simulation advantage or end-to-end compiler superiority.

## 11. Relation to current quantum compilation work

TARE itself is donor-owned (`Schillo, Sturm & Quay, 2026, arXiv:2601.05740`). More broadly, modern quantum compilation research already includes automated resource-aware compilation, architecture-aware profiling, circuit synthesis, and compilation-driven resource estimation. Q1 should therefore not be positioned as a generic compiler optimization paper.

The residual studied here is more specific: **an exact characterization of how much auxiliary frame support the frozen TARE grammar needs**, together with exact coupling counterexamples that explain why narrower donor families fail.

The distinction from learned/empirical algorithm-selection work is also important. A zero-error regime predicate on a finite panel is not the main theorem; the theorem is the support bound. This separation is what lets later predicate counterexamples improve the scientific picture without invalidating the exact result.

A final submission should refresh the primary-source nearest-work search and freeze the novelty sentence only after reading the strongest located donors. This draft therefore avoids a “first” claim.

## 12. Reproducibility

The paper's load-bearing artifacts are:

- `MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json` — local support-dominance checks;
- `MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json` — exact split/borrow discovery history;
- `MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json` — finite support-two closure;
- `MAX_R6S_ALL_N_COMPOSITION_RESULTS.json` — all-`n` theorem;
- `MAX_R6Q_REGIME_PREDICATE_RESULTS.json` — finite predicate;
- `MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json` — prospective 15/15 Benzene test;
- companion QG5/QG7/QG7b receipts for the later classification boundary.

Protocols under `development/orion-q-max-r0/` and `development/orion-qg-regime-geometry/` bind the corresponding pre-outcome definitions. The final publication package should provide deterministic replay/check commands, exact source/receipt digests, and a figure/table regeneration path. A DOI or permanent archive identifier should be added only after an actual deposit.

## 13. Limitations

**Grammar/objective scope.** The theorem is not a theorem about all TARE constructions. It is specific to the frozen R6M grammar and raw support-count objective.

**No physical-resource conclusion.** Support count is a structural compiler objective. Physical resource impact requires a separate hardware/compilation model.

**Closed-form classification remains open.** The support-two family is exact all `n`, but the smallest interpretable named-family union remains under active companion study.

**Finite predicate.** The zero-error R6Q classifier and 15/15 prospective Benzene result are bounded evidence. Later exact counterexamples refute universal extrapolation.

**Chemistry scope.** The named H4/N2/Benzene batches are not a representative sample of all Hamiltonians or workloads.

**No R6 novelty authority.** Every cited R6/R6Q/QG receipt retains its registered `NOT_R6` or bounded-authority restriction.

## 14. Discussion

The scientific arc illustrates a useful separation between three kinds of statement.

A **local mechanism statement** can explain why a sparse structure should be favored while still missing a global coupling. A **restricted-family statement** can be exact on large finite panels and a fresh subject while still admitting a later counterexample. An **all-`n` theorem** can close one structural dimension—support—without closing the entire interpretable taxonomy of optima.

Confusing these layers would have produced two opposite errors. After the early panels, one could have overclaimed that the two observed trades were complete. After QG5/QG7, one could have overreacted and said the support-two theory failed. Neither is correct. The counterexamples live inside the theorem's permitted family and therefore refine the regime map rather than refute the support ceiling.

This distinction makes negative results productive. The exact 8-versus-9 split witness says which donor restriction failed. The 5-versus-6 borrow witness identifies the intrinsic support-two boundary. The later 10-versus-11 and fourth-regime witnesses identify missing *subfamily* configurations while leaving the all-`n` family theorem intact.

The resulting view of compilation is therefore not “find one clever heuristic.” It is to separate **family expressivity**, **support complexity**, and **regime classification** so each can be tested with the right authority.

## 15. Conclusion

Natural weight-one TARE restrictions can fail by exact global couplings even when local support costs strongly favor sparsity. Two explicit counterexamples show how: split anchors can justify a spread Tag, and a cheap support-two branch can buy a cheaper Tag. Yet those exceptions do not proliferate into arbitrary frame complexity. For the frozen shared-Tag R6M grammar under its raw support-count objective, frame support two is an exact all-`n` ceiling.

Finite predicates and prospective chemistry/public-subject tests can map useful subregions of that support-two world, but later exact counterexamples show that compact closed-form regime completeness is a separate and still refutable question. The durable result is thus intentionally asymmetric: **the support ceiling is closed; the smallest explanatory regime map remains open to counterexample-driven refinement.**
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
