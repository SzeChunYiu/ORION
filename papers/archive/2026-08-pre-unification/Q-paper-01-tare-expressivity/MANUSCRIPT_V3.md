# Exact Support Ceiling in Shared-Tag TARE Compilation: Counterexamples, an All-`n` Theorem, and the Limits of Closed-Form Regime Maps

**ORION-Q1 Manuscript V3 — full-text-donor-synchronized publication draft**  
Scientific cut: `main@ca7df1055a43f97eaf8d142a62011c4c261af368`  
Claim authority: `CLAIM_LEDGER_V2.md`, `PUBLICATION_FOUNDATION_V2.md`  
Donor-boundary authority: `TARE_FULLTEXT_DONOR_BOUNDARY_V3.md`

## Abstract

The TARE (Tag-and-Restore) block-encoding method of Schillo, Sturm and Quay explicitly leaves its auxiliary anticommuting family, ancilla size, control labels and non-unique Tag solutions open to user choice and optimization. We therefore do **not** claim those degrees of freedom as new. Instead, we ask an exact expressivity question about a frozen three-block shared-Tag analysis family built from those donor-exposed choices under a stated raw support-count objective: **how much frame support can an exact optimum intrinsically require, and where do natural restricted joint families fail?** A complete local support-dominance analysis first shows that additional frame support cannot buy more Restore/factor savings than its direct local cost, while exposing a Tag-coupling gap that prevents a naive global closure argument. Exact counterexamples then realize that gap. A common-anchor weight-one family is beaten by a split-anchor construction with cost 8 versus 9; the resulting enlarged weight-one family is itself beaten by a frame-for-Tag borrow with exact cost 5 versus 6. The central result is an all-`n` exchange theorem: for every qubit count and every instance of the frozen grammar/objective, an exact optimum exists with frame support at most two, so the unrestricted optimum equals the minimum over the full support-two family. The proof also localizes the support-two boundary: the registered weight-two coupling pattern can block the exchange, whereas support at least three is always reducible at non-increasing cost. A structural regime predicate is exact on 9,771 registered finite instances, and a prospectively frozen prediction on a previously unread public Benzene DUCC batch is confirmed on all 15 matchings. We do not promote those finite results to a universal closed form. Later exact companion counterexamples identify additional configurations *inside* the theorem-backed support-two family, refuting the original compact taxonomy while leaving the support theorem intact. The durable contribution is therefore an exact joint family/closure theory over donor-exposed compilation choices under a declared objective, not the discovery of those choices themselves.

## 1. Introduction

Block encoding linear combinations of Pauli operators is a central subroutine in quantum algorithms for simulation and linear algebra. TARE, introduced by Schillo, Sturm and Quay in 2026, replaces conventional ancilla state preparation with a Tag-and-Restore construction built around a pairwise anticommuting auxiliary Pauli family. The donor paper is explicit about its design freedom: the auxiliary `R_k`, ancilla count and control labels can be chosen by the user; the Tagging strings arise from a generally non-unique linear system and may be optimized for weight, depth or gate-count proxies. In its reported numerical comparisons, the authors instantiate that freedom by fixing a canonical anticommuting `R_k` family while independently minimizing the Tag-string weights.

Those donor facts matter for novelty. The question in this paper is **not** whether TARE has free auxiliary choices, and it is not the generic problem of optimizing Tag weight. We instead define a precise shared-Tag compilation family and structural objective and ask a different question:

> **Among all configurations admitted by the frozen analysis grammar, which restricted families are guaranteed to contain an exact optimum, and what exact coupling mechanisms make smaller families fail?**

This is an expressivity/closure problem rather than an invention-of-freedom problem. It is also objective-specific. The TARE donor itself motivates tailoring choices to hardware gates, circuit width and depth; our raw support-count objective is one controlled mathematical lens, not a universal TARE implementation cost.

The distinction lets us separate three scientific layers that otherwise become easy to conflate.

First, a **local cost argument** can explain why extra frame support looks expensive while still missing a global Tag coupling. Second, a **restricted-family map** can be exact on thousands of instances and even a fresh subject yet remain vulnerable to a later exact counterexample. Third, an **all-`n` theorem** can close the support dimension even while the smallest interpretable union of named support-two mechanisms remains open to refinement.

We study the R6M three-block shared-Tag TARE-M2 analysis grammar under a frozen support-count objective with donor-owned Restore factoring. The unrestricted optimum is computed by a proof-carrying exact dynamic program. The research sequence is counterexample-driven.

1. We exhaustively verify local support-dominance inequalities and explicitly record the missing Tag-repair term.
2. An exact split-anchor witness refutes common-anchor weight-one closure: cost 8 versus 9.
3. An exact frame-for-Tag-borrow witness refutes the enlarged weight-one family: cost 5 versus 6.
4. We then prove the stronger statement: support above two never pays in the frozen R6M grammar/objective, for any `n`.
5. Finally, we keep compact finite/prospective regime predicates separate from that theorem. Later QG counterexamples refine the named support-two taxonomy without contradicting the all-`n` support envelope.

All TARE circuit identities, Tag/Restore construction, user-selectable `R_k`/control/ancilla choices, non-unique Tag optimization, anticommuting-unitary machinery and donor implementation claims receive zero novelty credit here. The candidate residual is the exact joint **closure structure** of one frozen analysis family over those donor-exposed choices.

## 2. Donor boundary and frozen analysis setting

### 2.1 What TARE already provides

For an operator `A = sum_k alpha_k P_k`, TARE pairs the target Pauli strings `P_k` with a pairwise anticommuting auxiliary family `R_k`. A unitary `Uanti` encodes the coefficient magnitudes on that family; `Tag` correlates branches with control states; `Restore` transforms each `R_k` into its corresponding target `P_k` with phase.

The donor theorem permits user choice of the anticommuting family `R_k`, the ancilla count and control labels. Its Tag linear system is generally non-unique, and the paper explicitly discusses optimizing Tag solutions for individual weight, row-wise maximum/depth or total weight/gate count. Therefore no ORION claim below is based on the premise that these freedoms were absent from TARE.

### 2.2 What this paper adds as an analysis object

We freeze a specific R6M analysis grammar: six non-identity target Paulis grouped into three two-target blocks `A,B,C`; each block chooses an ordered anticommuting frame pair `(R_j0,R_j1)`, a target assignment and a cheap central branch; the blocks share a Tag relation; Restore strings map frame representatives to targets.

This family is deliberately narrower than “all TARE implementations.” It is the mathematical object for which the exact DP, restricted families and theorem are defined.

### 2.3 Frozen structural objective

The registered objective combines:

- frame/Uanti support with multiplier 4 on non-central branches and 2 on the central branch;
- Tag cost proportional to Tag support;
- the donor-owned all-three Restore common-factor rule `F3`.

This is a **structural support-count objective**. It is not the TARE paper's universal circuit-cost function and does not directly imply physical qubit count, T count, logical depth, runtime or fault-tolerant space-time cost.

### 2.4 Exact referee and restricted families

The unrestricted optimum `C_DP` is computed by the committed proof-carrying exact dynamic program, itself bound to independent brute-force checks on registered domains.

We use:

- **D / R6L:** common-anchor weight-one frames;
- **D+:** weight-one frames with arbitrary anchors and exact minimum compatible spread Tag;
- **D++:** the full frame-support-≤2 family appearing in the all-`n` theorem;
- **B/B′/B″:** interpretable closed-form support-two subfamilies used for mechanism/regime explanation, not equivalents of D++.

The structural containments imply

`C_DP <= C_D++ <= C_D+ <= C_R6L`,

and each explicit borrow-family value is likewise a feasible upper bound on `C_DP`.

## 3. Local support dominance and its declared gap

The first analysis asks a one-qubit-local question: if a frame Pauli activates one additional letter, how much direct Uanti support cost is incurred and how much Restore/factor saving can that letter possibly generate?

The registered complete checks include:

- 536,870,912 R6M local configurations, zero violations, maximum saving/cost ratio 1.000;
- 175,616 donor-F3 letterwise cases, zero violations;
- a separate 150,994,944-case R6I local domain, zero violations, used only as comparative support-dominance evidence.

For R6M, each local frame-support unit costs at least the maximum local Restore/factor saving it can buy. The result explains why sparse frames are favored.

It is **not** a global closure theorem. The analysis records the missing term before the first global counterexample is opened: changing a frame letter can change the shared Tag syndrome. Tag repair is globally coupled and not bounded by the local inequality.

That declared gap points directly to the first exact refutation.

## 4. Counterexample I: Tag-anchor splitting

On the frozen hostile panel `n2_b`, the common-anchor weight-one family has minimum cost 9 while the unrestricted exact optimum is 8.

The winning configuration keeps all frame Paulis weight one but places block `A` on one anchor and `B,C` on another. The shared Tag becomes a weight-two spread Tag `Y⊗Y`. A diagnostic weight-one-frame/arbitrary-Tag family realizes the same cost, isolating the failure to the common-anchor/Tag coupling rather than to high frame support.

This gives the first exact structural trade:

**Tag-anchor split:** relaxing common-anchor coupling allows a spread Tag and reduces total cost.

D+ is frozen after the refutation to admit arbitrary per-block anchors with an exact minimum compatible Tag. It closes the registered first-regime panels and the exhaustive `n=1` slice.

The scientific novelty is not “Tags can be optimized”—the donor already states that. It is the exact closure/refutation statement for this frozen joint family.

## 5. Counterexample II: frame-for-Tag borrow

D+ still fails. On the registered structured-`n=2` domain, 486/9,261 instances exhibit an exact gap, as do 73/240 instances in the seeded random panel. The minimal structured witness satisfies

`C_DP = 5 < 6 = C_D+`.

The mechanism is different. A support-two frame Pauli is placed on the cheap central branch. The extra frame support changes the shared Tag relation so that a cheaper weight-one Tag becomes available. The exact witness carries the registered cost ledger `0+0+2+2+1=5`; every D+ member costs at least 6.

This is **frame-for-Tag borrow**. The local dominance intuition remains correct about direct local benefit: the reason support two helps is the global Tag coupling.

The next question is therefore sharply localized: can support three or larger ever buy a qualitatively new advantage, or does support two contain every exact optimum?

## 6. Finite support-two closure

D++ admits the full frame-support-≤2 family under the same frozen grammar. Before the theorem was available, it was checked on:

- all 4,096 `n=1` instances;
- all 9,261 instances of the registered structured `n=2` slice;
- seeded random `n=2–3` panels;
- five hostile panels;
- 30 recorded H4/N2 chemistry matchings.

D++ matches `C_DP` throughout and closes all 559 then-critical borrow cases with re-verified witnesses.

This is strong finite evidence, but it is not the all-`n` result. The Tag coupling could in principle have produced a new support-three exception beyond those domains. The final step therefore requires a composition theorem rather than a larger benchmark.

## 7. Main theorem: support two suffices for every `n`

### 7.1 Statement

For every qubit count `n`, target six-tuple, matching, target permutation and central choice in the frozen R6M shared-Tag grammar under the raw support-count objective,

> **an exact optimum exists whose frame Paulis all have global support at most two.**

Equivalently,

`C_DP = C_D++`

for every instance in scope.

The committed terminal is `MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED__SUPPORT3_NEVER_PAYS__DXX_EQUALS_DP_ALL_N__NOT_R6`.

### 7.2 Proof shape

For a selected high-support frame Pauli, each support qubit is classified by two binary relations: its local symplectic relation to the partner frame and to the Tag constraint. Because the frame anticommutes with its partner, the resulting class multiset has odd parity in the relevant component.

An `F_2^2` zero-sum/pigeonhole lemma shows that at support at least three there is a **proper subset of at most two support positions** whose aggregate parity preserves both required relations. Removing that subset therefore requires **zero Tag repair**—precisely the coupling term missing from the earlier local argument.

The registered class check covers 43,688 odd-alpha tuples through the finite proof domain; the only failing shapes occur at support two. A separate complete 18,432-case local inequality has zero violations and bounds any donor-F3 increase by the released frame cost.

Repeated non-increasing exchanges strictly reduce a well-founded support measure. Induction eliminates every support-three-or-larger frame from an optimum.

### 7.3 Why support two is the boundary

The four support-two class patterns that defeat the subset lemma are exactly those in which removing the locally commuting support position would force a Tag-syndrome change. They match the weight-two borrowing mechanism exposed empirically earlier.

At support three and above the proper parity-preserving subset always exists. The theorem therefore explains not just a cap but the mechanism by which the cap arises.

### 7.4 What the theorem does not say

It is not a theorem about:
- all TARE constructions;
- all hardware-aware objectives;
- R6I or other TARE grammars;
- all Tag ranks;
- physical circuit advantage.

It also does not claim that a particular compact union of named support-two subfamilies is universally complete.

## 8. Bounded regime predicate and prospective confirmation

After support complexity is closed, a cheaper interpretability question remains: can one decide which small support-two subfamily contains the optimum without solving the full exact family?

R6Q freezes

`P1(t) := [C_R6L(t)=C_D+(t)] AND [f_B(t) >= C_R6L(t)]`

for donor exactness. Across its registered four panels—9,261 structured `n=2`, two 240-instance seeded panels and 30 chemistry matchings—the predicate has zero observed classification errors (9,771 instances). The associated two-trade closed form also holds throughout those panels.

This is finite-domain evidence, not a theorem.

R6R then selects a previously unread public Benzene DUCC subject by a precommitted eligibility rule. Predictions are digest-stamped before the unrestricted DP is opened. All 15 registered matchings are predicted donor-exact at cost 9 and all 15 agree with exact truth.

The scientific unit is one new subject with 15 dependent combinatorial matchings; the result is a bounded prospective confirmation, not 15 independent external systems and not a universal accuracy estimate.

## 9. Later exact counterexamples refine the taxonomy, not the theorem

The prospective positive is followed by stronger hostile work.

### 9.1 Phantom borrow outside the original B family

A fresh seeded `n=3` row gives

`C_DP=10 < 11=C_R6L=C_D+=f_B`,

while `C_D++=10` remains exact. The missing support-two configuration uses a phantom borrow whose home lies outside that block's own target support. A separately frozen B′ family repairs the registered row/panels.

### 9.2 Weight-two-Tag + phantom-borrow hybrid

QG7 then finds 64 exact witnesses satisfying

`C_D++ < min(C_D+, f_B′)`.

The new support-two shape combines a weight-two Tag with phantom borrowing. A separately frozen B″ family closes its registered finite successor panels; the current all-`n` smallest-family classification still has an open consolidation link.

These results are the reason the title does not advertise a universal two-trade taxonomy. **The all-`n` support envelope is closed; the smallest explanatory closed form inside that envelope remains falsifiable.**

## 10. Chemistry and public-subject evidence

On the frozen H4 and equilibrium-N2 subjects, all 30 registered matchings satisfy the same exact optimum across the donor, D+, D++ and unrestricted DP under this structural objective. The bounded predicate explains these rows as cases where the registered split/borrow gains do not pay.

The Benzene prospective subject contributes 15 additional within-subject matchings under the precommitted public-source selection rule. The protected stretched-N2 discriminator is unread in every Q1 receipt.

These cases show that the exact counterexamples do not imply donor configurations are poor on the recorded chemistry batches. They do not establish representative chemistry performance or end-to-end simulation advantage.

## 11. Relation to the TARE donor and other compiler work

The full TARE text is the primary ownership boundary.

Schillo, Sturm and Quay already make the anticommuting `R_k`, ancilla count and control labels user-selectable; they already note that the non-unique Tag solutions can be optimized for weight/depth/gate-count proxies. Their numerical comparison fixes one canonical `R_k` family and independently minimizes Tag weights. Q1 therefore does not claim any of those design freedoms.

The residual is narrower:

> **Given a frozen shared-Tag family/objective built from donor-exposed choices, characterize exact joint family closure, produce exact witnesses when restricted families fail, and prove the smallest support envelope currently authorized by the evidence.**

This distinction also separates Q1 from generic quantum compiler optimization and static resource estimation. The paper's primary object is family expressivity under one declared mathematical cost, not a universal optimizer or hardware-cost predictor.

A final submission must use the current TARE title/version and rerun the nearest-work search shortly before submission. We make no unsupported “first” claim.

## 12. Reproducibility and evidence classes

Load-bearing artifacts include:

- `MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json` — exhaustive local checks;
- `MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json` — split/borrow discovery history;
- `MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json` — finite support-two closure;
- `MAX_R6S_ALL_N_COMPOSITION_RESULTS.json` — all-`n` theorem;
- `MAX_R6Q_REGIME_PREDICATE_RESULTS.json` — finite regime predicate;
- `MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json` — prospective Benzene result;
- named QG5/QG7/QG7b receipts — later closed-form boundary evidence.

The final paper must label these evidence classes separately: proof, exhaustive finite domain, exact counterexample, frozen panel, prospective case and replay. Deterministic replay is a reproducibility check, not an independent efficacy replicate.

The source repository is publicly inspectable. Because no root reuse licence is yet bound to this publication cut, the final manuscript must not call ORION “open source” until an authorized owner explicitly chooses and records the applicable licence(s). A permanent archive identifier must likewise be inserted only after an actual deposit.

## 13. Limitations

**Donor freedom is not novelty.** TARE already exposes and discusses optimizing major auxiliary choices. Q1's claim begins only at exact family/closure characterization under our frozen analysis objective.

**Grammar/objective scope.** `C_DP=C_D++` is an R6M/raw-support theorem, not a theorem about all TARE compilations or hardware cost models.

**No physical-resource conclusion.** Structural support count is not a complete physical resource metric.

**Compact regime map remains open.** The full support-two family is theorem-exact, but later exact witnesses refute successive smaller closed-form unions.

**Finite predicate and one prospective subject.** Zero observed error on the registered panels and 15/15 Benzene matchings do not establish population accuracy or universality.

**Chemistry representativeness.** H4, equilibrium N2 and Benzene are named cases rather than a representative workload sample.

**No separate R6 novelty authority.** Every imported receipt retains its bounded/`NOT_R6` authority.

## 14. Discussion

The main result is easiest to misread if optimization freedom, restricted-family closure and support complexity are collapsed into one idea.

TARE already says that its auxiliary choices can be tailored. Q1 asks what the joint design space implies **exactly** once a grammar and objective are frozen. The early local inequality predicts sparsity but cannot close the family because Tag repair is global. The 8-versus-9 and 5-versus-6 witnesses then identify two exact failure mechanisms. The all-`n` theorem resolves a deeper question: those couplings can make support two useful, but they can never make support three or larger necessary under this objective.

The later QG counterexamples expose another layer. A small named support-two taxonomy can be exact on thousands of rows and one prospectively chosen subject yet still miss a valid support-two configuration. That does not weaken the theorem; it tells us that **support complexity and explanatory taxonomy have different logical authority**.

This separation is the durable contribution. It tells a compiler researcher what can safely be compressed into a theorem, what must remain a finite rule, and where an exact counterexample should reopen the interpretation without rewriting prior evidence.

## 15. Conclusion

TARE explicitly offers substantial freedom in its auxiliary frame, control and Tag choices. Under a frozen shared-Tag R6M analysis grammar and raw support-count objective, those freedoms generate exact coupling effects that defeat natural weight-one restrictions: split anchors can justify a spread Tag, and a cheap support-two branch can buy a cheaper Tag. Yet the same grammar has an exact global ceiling: support above two never needs to appear in an optimum.

Finite structural predicates and a prospectively confirmed Benzene case provide useful regime evidence inside that support-two world, while later exact counterexamples show why no current small closed-form taxonomy should be promoted to a universal theorem. The result is therefore intentionally asymmetric and tightly scoped: **the support ceiling is closed all `n`; the smallest explanatory support-two regime map remains open to counterexample-driven refinement.**
