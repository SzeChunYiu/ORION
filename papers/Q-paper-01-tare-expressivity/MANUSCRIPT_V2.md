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