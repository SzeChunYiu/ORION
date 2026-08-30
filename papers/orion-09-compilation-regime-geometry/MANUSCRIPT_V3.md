# Compilation Regime Geometry: Exact Trade Mechanisms, Intrinsic Support, Objective Certificates, and Boundary Identifiability

**ORION-09 Manuscript V3 — current-main publication-synthesis draft**  
Scientific refresh cut: `main@c5ba39fef4f25c46de5fb69bf07f50530f4693ca`  
Foundation: `PUBLICATION_FOUNDATION_V3.md`  
Prior draft: `MANUSCRIPT_V2.md`

## Abstract

Algorithm selection and Instance Space Analysis already map structural regions in which different algorithms perform well. Quantum compilation can sometimes support a more strongly typed object because exact referees, constructive witnesses and machine-checked bounds are available. We call this investigative object a **compilation regime geometry**: a record of where a donor family is exact, which structural trades defeat it, what search/support bounds are intrinsic or merely certified by a proof system, how those bounds change with the objective, whether regime membership is representable in a chosen feature vocabulary, and whether prospectively frozen predictions survive new instances. We instantiate this template across several exact quantum-compilation models. For the shared-Tag R6M TARE grammar under its unit/raw-support objective, an all-`n` theorem bounds exact optima to frame support at most two even though progressively richer support-two subfamilies are exposed by exact counterexamples. For the distinct R6I rank-2 grammar, a later whole-system normalization proves the stronger and tight result `kappa_R6I=1`: every exact optimum is support one and support zero is infeasible. A separate objective-indexed theorem identifies a cone in cost-weight space where this support-one certificate remains valid; outside the cone the certificate is silent rather than refuted. A production conserved-syndrome analysis gives a useful but looser R6I support bound of five, demonstrating that a safe proof-derived ceiling need not equal intrinsic support. In SixLCU, the registered incumbent-exact boundary is theorem-grade and on its exhaustive `n=2` domain is expressible by one structural literal. In StabPrep, by contrast, a prospectively frozen `n=4` forecast is refuted and the frozen 13-feature representation contains mixed cells carrying opposite donor-exactness labels, imposing an irreducible 43/1,146 error floor within that vocabulary. Under a later prospectively frozen enlarged vocabulary that floor is `0` on the complete `n<=3` domain and exactly four features suffice (`k*=4`, proved), yet the compact law still fails to transfer to unseen `n=4` states, where it matches a shuffle null (`p=0.51`); the boundary law is therefore domain-local, not universal. These cases do not establish a universal phase diagram. They show why exact compiler studies should distinguish intrinsic expressivity, proof-system ceilings, objective-validity regions, named trade families, boundary representation and prospective falsification rather than collapsing them into one performance map.

## 1. Introduction

The premise that algorithm performance depends on problem structure is not new. Rice formalized the algorithm-selection problem in 1976, and modern Instance Space Analysis (ISA) explicitly constructs interpretable feature spaces and algorithm footprints that expose where methods are strong or weak. This literature is the primary conceptual parent for any attempt to describe “regions where a compiler works.”

The question in this paper is narrower but structurally different. In some quantum compiler families, the objects that determine a performance region are sufficiently finite or algebraic that we can ask questions stronger than “which method tends to win?” A donor failure can be represented by an exact feasible configuration with a cost ledger. A support restriction can be an all-`n` theorem. An objective perturbation can have an exact proof-validity cone. A classifier failure can be localized either to predicate complexity or to missing information in the chosen feature representation. And a forecast can be frozen before an exact referee is opened, making refutation as authoritative as confirmation.

We use **compilation regime geometry** as a name for this investigative record. It is deliberately not a claim that all compiler families admit a simple geometric phase diagram. A complete record may include a theorem, a finite exact map, a counterexample, a proof-system upper bound, an objective-indexed certificate, a prospective failure, or a proof that a feature vocabulary cannot determine the boundary.

The current ORION-QG programme supplies several cases with different outcomes. Shared-Tag TARE first appears to admit a compact trade map, then exact counterexamples repeatedly enlarge the named support-two subfamilies while an independent all-`n` theorem keeps the full support-two envelope exact. In a second R6I grammar, successive proof systems first produce loose support bounds and then a whole-system transformation collapses the intrinsic support number to one. SixLCU exhibits a theorem-grade simple boundary. StabPrep transfers the investigative template but refutes the hypothesis that natural low-order features should determine donor exactness.

These differences motivate the central thesis:

> **A compiler regime should be described by multiple authority-bearing coordinates—intrinsic family expressivity, certified search bounds, elementary trade witnesses, objective-indexed validity, boundary representation, and prospective falsification—rather than by one scalar performance surface.**

This thesis is compatible with ISA rather than competing with it. ISA supplies the mature language of instance-dependent performance footprints. ORION-09 asks which additional exact compiler objects can explain, delimit or falsify those footprints when the compilation problem permits stronger authority.

## 2. Regime-geometry record

For a compiler instance `x`, objective parameter `theta`, exact referee `R`, donor family `D`, candidate family hierarchy `F`, and structural feature map `phi(x)`, we track six distinct components.

### 2.1 Donor/incumbent exactness

The donor is exact when `C_D(x;theta)=C_R(x;theta)`. This statement may be theorem-grade, exhaustive on a finite domain, or observed on a frozen panel. Those evidence classes are not interchangeable.

### 2.2 Exact trade mechanisms

When the donor is inexact, a useful explanation is a feasible witness that isolates what the donor cannot express: an anchor split, a support borrow, a different pivot/order, a routing change, a global synthesis move, or another explicit structural edit. A trade class therefore requires both a semantic shape and a verified cost improvement.

### 2.3 Intrinsic support / expressivity number

For a family parameter such as Pauli-frame support, define the smallest bound `kappa` such that every exact optimum has a representative within that bound. A proven upper bound is not automatically `kappa`; tightness requires either an obstruction below the bound or independent infeasibility.

### 2.4 Proof-system or quotient-derived ceiling

A proof technique can certify a safe search ceiling larger than the intrinsic one. This is still useful: it transforms an unrestricted search into a bounded one. But its numerical value is a property of both the compiler and the proof abstraction, not necessarily the compiler alone.

### 2.5 Objective-indexed certificate region

A structural theorem can depend on cost weights. We therefore record the subset of objective space where the same proof certificate remains valid. Outside the proved region, “certificate unavailable” and “counterexample exists” are separate states.

### 2.6 Boundary representation and prospective falsification

A structural feature vocabulary may or may not determine regime membership. Candidate predicates should be tested prospectively when possible. If identical feature vectors carry both labels, no classifier using only that vocabulary can be exact on the registered domain; the right next question is representation enlargement, not merely model capacity.

## 3. Authority discipline

Throughout the paper we distinguish:

- all-`n` theorem / machine-checked proof;
- exhaustive finite-domain statement;
- exact counterexample;
- bounded frozen-panel observation;
- prospective confirmation or refutation;
- forecast-only row;
- open proof/sharpness link.

Every statement is indexed by its grammar and objective. No result is interpreted as physical quantum advantage. The detailed TARE theorem belongs to ORION-01; the layered forecast-certification result belongs to ORION-10. ORION-09 uses those objects only for cross-family synthesis.

## 4. R6M TARE: intrinsic ceiling two, taxonomy still refinable

The first case is the R6M three-block shared-Tag TARE grammar under its frozen unit/raw-support objective. The donor starts with common-anchor, weight-one anticommuting frame choices.

### 4.1 Split trade

An exact hostile instance gives cost 8 with weight-one frames split over different anchors and a spread Tag, while the common-anchor donor costs 9. The failure is therefore not “high support helps” but a coupling between anchor placement and the shared Tag.

### 4.2 Borrow trade

After the donor is enlarged to allow split anchors, a second exact witness has cost 5 while the enlarged weight-one family costs 6. A support-two frame on a cheap central branch purchases a cheaper Tag: the first intrinsic support-two mechanism.

### 4.3 All-`n` support-two theorem

R6S proves that under this exact grammar/objective every support-three-or-larger frame can be reduced at non-increasing cost while preserving the required anticommutation and Tag relations. Hence

`C_DP = C_D++`

for every `n` and target instance in scope, where `D++` is the full support-≤2 family.

This theorem closes **support complexity**, not the smallest explanatory named-family union inside support two.

### 4.4 Named support-two families remain falsifiable

An early donor/split/borrow predicate is exact on 9,771 registered finite instances and succeeds on a prospectively frozen 15-matching Benzene subject. Later exact counterexamples nevertheless reveal omitted support-two shapes: first an out-of-local-support phantom borrow, then a weight-two-Tag/phantom-borrow hybrid. Separately frozen B′ and B″ families repair their registered panels.

The later failures do not contradict `C_DP=C_D++`; they demonstrate that **intrinsic support and interpretable closed-form taxonomy are different coordinates**.

### 4.5 Objective dependence

Under a reweighted O1 objective, QG records an exact support-three witness: the unit-objective support-two theorem is not universal across weights. Under another objective O2, a constant-shift argument preserves regime membership exactly. The regime object therefore belongs to `(grammar, objective)`, not grammar alone.

## 5. R6I: intrinsic support collapses from loose proof bounds to one

The current-main refresh adds a particularly useful second TARE-like grammar because it separates **what the compiler intrinsically needs** from **what a proof system can certify**.

R6I uses two rank-2 dependent-triple blocks and a shared two-bit Tag under its frozen unit objective.

### 5.1 The proof ladder

Earlier local-edit proof systems progressively reduced conservative support bounds while preserving more of the existing Tag structure. The decisive V6 proof system changes the allowed proof move: after each rank-2 block is localized to one anticommuting core, it is allowed to rebuild/relocate the shared Tag rather than preserve the old columnwise syndrome representation.

That whole-system edit closes every remaining support-two configuration without increasing objective cost.

### 5.2 All-`n` support-one theorem and tightness

The committed QG9 V6 terminal is

`QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED`.

The proof establishes `C_DP=C_cap1` for every `n` in the frozen R6I grammar/unit objective. Support zero is infeasible. Therefore the intrinsic support number is exactly

`kappa_R6I = 1`.

The finite obligations used by the composition proof include a 2,880-row deletion domain, 6,912-row core-alignment domain, 576-row same-qubit Tag-rigidity check and 9,216-row distinct-qubit Tag lower-bound check; an independent generic verifier and native ORION-Q verifier both accept the theorem.

The scientific lesson is not merely a smaller number. The result shows that an earlier support-two “obstruction” can be an obstruction of the **rewrite language**, not of the compiler family. A proof system that freezes auxiliary structure may report a safe but non-tight ceiling.

## 6. QG6: conserved-syndrome rank as a safe but potentially loose ceiling

QG6 analyzes production transition tables through an additive conserved-syndrome quotient over `F_2`. Under named conditions, if active coordinates generate a `d`-dimensional additive syndrome and zero-sum proper-subset deletion is semantic-preserving and non-increasing in cost, then a support-minimal optimum has support at most `d`.

This principle exactly matches the R6M case: the production quotient has rank 2 per relevant frame slot, consistent with the independently proved support-two theorem.

R6I provides the critical negative control. Its production block-deletion quotient has rank 5, so the generic rank argument certifies a support ceiling of five. Yet QG9 V6 later proves `kappa_R6I=1`.

Thus syndrome dimension is useful without being intrinsic:

`safe proof-derived ceiling >= intrinsic support number`.

The gap measures what the proof abstraction fails to exploit—in R6I, whole-system Tag relocation and alignment structure. This is exactly the kind of distinction a regime-geometry record should preserve instead of reporting one “support complexity” number.

## 7. QG16: objective-indexed support-one certificate

Having proved `kappa_R6I=1` at the unit objective, QG16 asks where the same normalization remains non-increasing under a weighted objective

`C_theta = frame(t_c,t_nc) + t_tag * TagSupport + t_r * RestoreSupport`.

The machine-checked certificate is valid all `n` inside the cone

- `2*t_nc >= 5*t_r`,
- `t_c + t_nc >= 5*t_r`,
- `2*t_nc >= 2*t_r + 2*t_tag`,
- `t_c + t_nc >= 2*t_r + 2*t_tag`.

When `t_c <= t_nc`, two halfspaces suffice for the recorded certificate:

- `t_c + t_nc >= 5*t_r`,
- `t_c + t_nc >= 2*t_r + 2*t_tag`.

The unit objective lies on a registered boundary of this cone and an interior control also passes. Several frozen outside objectives correctly fall outside.

The semantics of an outside point are deliberately weak:

`THIS_PROOF_CERTIFICATE_DOES_NOT_APPLY`.

QG16 does **not** infer that support two is required outside the cone, and the global sharpness of the phase boundary remains open. This distinguishes a **proof-validity region** from an intrinsic phase boundary.

## 8. SixLCU: a theorem-grade simple boundary

A second compiler family, SixLCU, considers registered partition/factoring/index-encoding choices under a frozen `SELECT + PREP + WIDTH` structural objective. The incumbent boundary is theorem-grade in the admitted family.

On the registered exhaustive `n=2` domain of 38,760 instances, incumbent exactness is represented exactly by one literal in the frozen structural vocabulary:

`maxg2 == -2`.

SixLCU therefore supplies a clean case where the donor boundary is both exact and low-order in the chosen representation.

The scientific mistake would be to generalize from two favorable families.

## 9. StabPrep: the template transfers, feature determination does not

StabPrep studies stabilizer-state preparation under a frozen Clifford gate/cost model with exact Dijkstra referees over complete state graphs containing 6, 60, 1,080 and 36,720 states for the registered `n=1..4` progression.

### 9.1 Exact trade classes

The donor is a frozen greedy/echelon construction. Exact witnesses identify four structural improvement classes: ORDER, PIVOT, ROUTE and GLOBAL. Thus the trade-mechanism component of regime geometry transfers to a compiler with very different search semantics.

### 9.2 Prospective forecast refutation

A regime/cost forecast is digest-stamped before the registered `n=4` exact referee is opened. It is refuted: 100/120 regime labels and 67/120 exact costs match. The protocol records the failure rather than changing the predictor post outcome.

### 9.3 Frozen-vocabulary non-identifiability

A follow-up study asks whether the boundary merely needs a larger predicate. For SixLCU, one literal still separates the boundary exactly. For StabPrep, however, the frozen 13-feature representation contains 12 **mixed cells**: identical feature vectors attached to both donor-exact and donor-inexact instances.

Those mixed cells impose an irreducible 43/1,146 classification floor for any classifier using only that frozen vocabulary. The result is representational, not universal: donor exactness is **not a function of these features on this domain**.

### 9.4 Enlarged vocabulary: floor 0 with a four-feature law, and its limit

The enlargement question is now answered on the frozen domain. Under a prospectively frozen enlarged vocabulary (L3, 127 features) the fibre floor is `0` over all 1,146 instances of the complete `n<=3` domain (1,109 cells, 0 mixed). Two guards separate this from a near-injectivity artifact: the realized cell structure confined the floor to `[0, 37/1146]` before any label was read, and the exact structure-free null for the full map is `7.06e-07` with `0/20,000` permutation hits.

The law is compact: the minimum number of frozen features whose projection still attains floor `0` is exactly four (`k*=4`), proved by exhaustive refutation of all 127 singletons, 8,001 pairs and 333,375 triples together with the verified witness `{15,30,39,42}` (523 cells, compression 0.456, structure-free null `1.44e-120`). Each witness coordinate is individually necessary.

Two adverse findings are recorded alongside it. **The mechanism attribution is not supported:** any two of L3's three blocks already attain floor `0`, the pre-revival pair V2 + donor-path attains it with no sign-aware feature at all, and the minimal witness contains zero sign-aware coordinates; the conversion did not require the new block. **The compact law does not transfer:** on unseen `n=4` states it leaves 32/120 cross-validation errors, equal to the parent cell-lookup baseline, against a shuffle-null mean of 32.41 and empirical `p=0.51`. The combined statement is that a compact four-feature law determines donor-exactness on `n<=3` and does not transfer to `n=4`.

## 10. Cross-family synthesis

The current cases expose several logically independent coordinates.

| Object | R6M | R6I | SixLCU | StabPrep |
|---|---|---|---|---|
| intrinsic/proved support | all-n ceiling ≤2 under unit objective | **exact `kappa=1`** under unit objective | family-specific theorem structure | no analogous support coordinate used |
| safe but loose proof ceiling | R6M syndrome rank 2 matches support2 | QG6 rank 5, loose versus `kappa=1` | not current focus | not current focus |
| objective certificate | unit support2; reweighting can break | **QG16 support1 cone**, sharpness open | objective fixed in current study | objective fixed in current study |
| exact trade witnesses | split/borrow/phantom/hybrid | proof-system obstructions + Tag-relocation normalization | registered structural trades | ORDER/PIVOT/ROUTE/GLOBAL |
| compact boundary | finite named-family predicates, still refinable | not central current result | exact one-literal boundary | impossible in frozen 13-feature vocabulary |
| prospective falsification | confirmations + later closed-form refutations | future objective sharpness open | bounded registered evidence | explicit n=4 refutation |

Three lessons follow.

**First, intrinsic expressivity and proof complexity differ.** R6I's `kappa=1` coexists with a sound syndrome-rank ceiling of five.

**Second, objective dependence must be typed.** A certificate cone identifies where a proof remains valid; outside it, one must not infer the opposite theorem.

**Third, simple boundary representation is not guaranteed.** SixLCU is feature-determined in one literal; StabPrep is not feature-determined in its registered natural vocabulary.

## 11. Relation to Instance Space Analysis and algorithm selection

ISA remains the primary conceptual ancestor for feature-conditioned performance regions. ORION-09 does not claim that mapping such regions is new.

The additional object introduced here is a **compiler-specific authority decomposition**. A regime record can contain:

- an exact feasible transformation explaining a strict cost gap;
- a theorem about family expressivity;
- a looser proof-derived search bound;
- an objective-space certificate with explicit outside semantics;
- a representation-level impossibility statement caused by mixed feature cells;
- a prospectively frozen refutation.

These objects can explain or constrain a performance footprint, but they do not replace ISA or general algorithm selection.

The paper therefore claims a reusable *template for exact compiler studies*, not a general theory that all instance spaces possess low-dimensional exact boundaries.

## 12. Reproducibility and artifact authority

The V3 cross-family paper binds its load-bearing claims to committed receipts and independent verifiers. The newly imported current-main objects are:

- `research/extensions/orion-qg/QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json`;
- `research/extensions/orion-qg/QG16_R6I_SUPPORT1_PHASE_RESULTS.json`;
- `research/extensions/orion-qg/QG6_SYNDROME_DIMENSION_RESULTS.json`.

They are added to the previously bound TARE R6S/QG5/QG7, SixLCU and StabPrep receipts. QG17 is excluded because the refresh cut contains a protocol but no result receipt.

The final submission package should include a machine-readable paper manifest giving path, content digest, evidence class and manuscript claim for every load-bearing artifact. Source is publicly inspectable in the repository; a reuse licence and permanent archive identifier must not be claimed until actually established.

## 13. Limitations

**Framework, not universal field law.** Four registered compiler/grammar cases illustrate the template; they are not a statistical sample of all compilers.

**Structural objectives.** Results concern frozen structural cost functions, not full hardware space-time cost or physical quantum advantage.

**Grammar specificity.** R6M support2 and R6I support1 are statements about distinct grammars. They must not be merged into one generic TARE support theorem.

**Certificate versus intrinsic boundary.** QG16's outside-cone region is not known to require larger support. Global phase-boundary sharpness is open.

**Proof-abstraction looseness.** QG6 syndrome dimension gives sufficient bounds under stated conditions and can be highly non-tight, as R6I demonstrates.

**Feature-vocabulary scope.** StabPrep's mixed-cell result proves non-identifiability only within the frozen 13-feature representation/domain.

**Closed-form TARE taxonomy.** R6M support complexity is theorem-closed, but the smallest named support-two union remains under successor proof work.

**Current frontier.** QG7d/QG15c/QG17 and later lanes are successor research. They do not automatically reopen this manuscript unless they falsify a V3 headline or materially change its nearest-work boundary.

## 14. Discussion

The strongest cross-family lesson is that “the regime” is not one thing.

For R6M, a theorem determines the exact support envelope while named explanatory subfamilies remain open to counterexample. For R6I, changing the proof language—from fixed auxiliary structure to whole-system Tag relocation—shrinks the certified bound all the way to the tight intrinsic value one. QG6 then supplies a useful negative lesson: an automatically extracted conserved-syndrome dimension can be safe and mechanistically meaningful yet still be far from tight. QG16 adds another distinction: even an exact structural theorem at one objective can become a **conditional certificate** over a region of objective space without telling us what happens outside.

SixLCU and StabPrep separate a different axis. In one family, the exact incumbent boundary is represented by a single literal. In the other, the registered natural features provably fail to determine the label. The right response to the latter is not a larger classifier on the same information; it is a representation question.

These cases support a practical research workflow. Start with the strongest donor. Demand exact witnesses when it fails. Search for a theorem that bounds the full family independently of a convenient closed form. Distinguish a safe proof-derived ceiling from intrinsic tightness. Index the theorem by objective. Test the boundary representation itself. Finally, freeze predictions before opening exact truth so both success and failure can refine the geometry.

This workflow is more conservative than a single learned phase map, but that conservatism is the point: every apparent simplification remains falsifiable at the authority level where it was earned.

## 15. Conclusion

Compilation regime geometry is best treated as a typed record of exactness, mechanism and uncertainty rather than a universal low-dimensional phase diagram. In the current quantum-compiler cases, it distinguishes an R6M all-`n` support-two envelope from a still-refinable named trade basis; proves a tighter R6I intrinsic support number of one after whole-system Tag relocation; separates that intrinsic value from a looser syndrome-rank ceiling; derives an objective cone where the support-one proof remains valid; identifies a theorem-grade one-literal SixLCU boundary; and records a StabPrep boundary that cannot be represented exactly by its frozen natural features.

The transferable claim is therefore not that every compiler has a simple regime map. It is that exact compiler studies can ask, and separately answer, **which family is expressive enough, which proof bound is tight, which objective preserves the certificate, which structural feature language determines the boundary, and which prospective prediction survives falsification.**
