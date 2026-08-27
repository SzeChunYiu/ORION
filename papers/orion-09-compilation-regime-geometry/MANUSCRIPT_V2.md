# Compilation Regime Geometry: Exact Trade Mechanisms, Objective Phases, and Boundary Identifiability Across Quantum Compiler Families

**ORION-09 Manuscript V2 — publication-synthesis draft**  
Publication cut: `main@ca7df1055a43f97eaf8d142a62011c4c261af368`  
Claim authority: `CLAIM_LEDGER.md`, `PUBLICATION_FOUNDATION_V2.md`, committed QG wave-1/wave-2 receipts

## Abstract

Compiler optimization is usually summarized by average cost reduction or by learned regions in which one algorithm outperforms another. We study a different object: an **exact or falsifiable regime geometry** that records why a donor compilation family is optimal, which elementary structural trades defeat it, what support/budget bounds delimit the exact search, how the geometry changes with the objective, and whether regime membership is even representable in a chosen structural vocabulary. We instantiate this programme on three quantum-compilation families with exact referees. In shared-Tag TARE compilation, an all-`n` theorem restricts the exact optimum to frame support at most two under the unit/raw-support objective, while a sequence of exact counterexamples reveals progressively richer support-two trade configurations and objective reweighting can introduce support-three optima. In a second SixLCU family, the incumbent-exact boundary is theorem-grade and, on the registered `n=2` domain, is expressible by a single structural literal. In a third stabilizer-state-preparation family (StabPrep), the regime-geometry template transfers—donor-optimal region, four exact trade classes, bounded search structure and prospective testing all remain meaningful—but the simple-boundary motif fails. A digest-stamped prospective `n=4` forecast is refuted, and a follow-up analysis proves that the failure is not merely insufficient predicate complexity: the frozen 13-feature vocabulary contains mixed cells with both donor-exact and donor-inexact labels, yielding an irreducible 43/1,146 classification floor. Thus the transferable result is not a universal phase diagram. It is a scientific template in which theorem, exact counterexample, finite regime map, objective phase, prospective confirmation/refutation and feature non-identifiability are first-class outcomes. The work is distinct from Instance Space Analysis and algorithm selection, which already map feature-dependent performance regions; our object is the mechanistic/compiler-expressivity structure underlying those regions.

## 1. Introduction

Optimization algorithms rarely have one universally best configuration. Their performance depends on instance structure, objective weights, hardware assumptions and the expressive power of the search family. The algorithm-selection literature has studied this dependence for decades. Rice's algorithm-selection framework and modern Instance Space Analysis (ISA) relate features of problem instances to algorithm footprints, strengths and weaknesses; recent work applies ISA directly to quantum optimization, including QAOA initialization and instance dependence. These are important donors for any paper that claims to map “regions where methods work.”

Quantum compilation has an additional opportunity. In carefully defined compiler families, the relevant search spaces can sometimes be enumerated exactly, restricted by machine-checked theorems, or attacked by explicit counterexamples. This allows a regime map to carry stronger semantics than a learned performance footprint. A boundary may be a theorem. A donor failure may have a minimal witness and a named trade mechanism. An objective perturbation may preserve the geometry by an exact constant-shift argument or destroy it by an explicit support-three counterexample. A proposed feature language may be shown incapable of representing the boundary at all because two instances with identical features have opposite labels.

We call this object **compilation regime geometry**. The term denotes an investigative structure, not a claim that all compiler families admit a simple phase diagram. A regime-geometry study asks:

1. Where is a donor/incumbent family exactly optimal?
2. What elementary structural trades create strict improvements, and can they be witnessed exactly?
3. What support/budget/sufficiency bounds delimit the exact search?
4. Can regime membership be decided from input structure without solving the full exact problem?
5. How does the answer change under objective reweighting?
6. Do prospectively frozen predictions survive new instances?
7. If the boundary is not predictable, is the issue model complexity or missing information in the chosen representation?

The last question becomes central in this paper. The programme begins with TARE, where a simple structural picture appears surprisingly effective. It transfers to SixLCU, which has an even simpler exact boundary. A third family, StabPrep, then refutes the tempting generalization: the natural feature vocabulary does not determine donor exactness, regardless of predicate budget within that vocabulary.

This negative result changes the field-level claim. We do not propose “simple compiler phase diagrams.” We propose a falsifiable framework in which **boundary identifiability itself is a property to measure**.

## 2. What is a compilation regime geometry?

For a compiler family `F`, objective `C`, exact referee `R`, donor family `D`, and a structural feature vocabulary `phi(x)`, we define a regime-geometry record with five scientific components.

### 2.1 Donor-optimal region

For an instance `x`, the donor is exact when

`C_D(x) = C_R(x)`.

The region may be specified by exhaustive enumeration, an exact theorem, or a bounded empirical panel. These authority types must remain distinct.

### 2.2 Elementary trade mechanisms

A donor-inexact witness is most informative when its improvement can be localized to a structural move—e.g. split an anchor, relocate a shared Tag, borrow support on a cheap branch, change a pivot/order, or introduce a global synthesis action. A trade class is not merely an outcome label; it should include a feasible witness and the cost ledger by which it beats the donor.

### 2.3 Sufficiency / search bound

A theorem or machine-checked bound can restrict the search independently of a closed-form regime taxonomy. This distinction is crucial in TARE: the exact optimum is theorem-bounded to support two even though the smallest named union of support-two subfamilies remains under refinement.

### 2.4 Boundary representation

A predicate `P(phi(x))` may classify donor exactness or trade membership. The representation can fail in three different ways:

- the chosen predicate is too simple;
- the feature vocabulary is insufficient but could be enlarged;
- the boundary is not determined by the frozen feature vector at all (mixed feature cells).

These failure modes are scientifically different.

### 2.5 Prospective falsification

Any proposed boundary/forecast may be frozen on unseen instances before exact truth is opened. A positive confirms only the registered domain; a refutation is a first-class result and should generate the next structural question without rewriting the old result.

## 3. Research discipline and authority types

The QG programme uses exact referees and pre-outcome protocol freezes where feasible. We distinguish:

- `PROVEN-ALL-N` / theorem-grade structural statements;
- exhaustive finite-domain statements;
- exact explicit counterexamples;
- machine-evidenced frozen-panel equalities;
- prospectively confirmed predictions;
- prospectively refuted predictions;
- forecast-only rows;
- open theorem links.

The distinction is not cosmetic. Cross-family synthesis is valid only if a theorem in one family is not rhetorically transferred into a finite result in another.

All QG receipts used here retain `NOT_R6`: the programme does not claim physical quantum advantage or the separate ORION R6 novelty authority.

## 4. Family I: TARE — exact support ceiling, expanding trade basis

The first regime-geometry instance is the R6M shared-Tag TARE grammar under the frozen raw support-count objective. Detailed mathematics is owned by companion ORION-01; here we use only the elements needed for the cross-family object.

### 4.1 Donor region and first two trades

The natural weight-one/common-anchor donor family is exact on many registered chemistry/finite rows but fails on a small exact counterexample. **Split trade:** weight-one frames on different anchors with a spread Tag achieve cost 8 versus donor 9.

After enlarging the donor family to admit split anchors, a second exact failure appears. **Borrow trade:** a support-two frame on a cheaper central branch purchases a cheaper Tag, giving exact cost 5 versus enlarged-family cost 6.

These counterexamples turn donor inexactness into named structural mechanisms rather than undifferentiated “optimizer wins.”

### 4.2 All-`n` support-two theorem

Companion theorem R6S proves that for every `n` and every target instance in the frozen R6M/raw-support setting,

`C_DP = C_D++`,

where `D++` contains the complete frame-support-≤2 family. Support ≥3 can be reduced at non-increasing cost by an exchange argument that preserves both anticommutation and Tag syndrome. Thus the exact search has a theorem-grade support ceiling even before the support-two taxonomy is complete.

### 4.3 Finite low-order regime map and prospective confirmation

An early structural predicate over the donor/split/borrow picture classifies donor exactness with zero error on 9,771 registered instances. A later prospectively frozen public Benzene DUCC subject is predicted before exact DP and matches on all 15 registered matchings.

At this point it would be tempting to treat the two-trade map as a field theorem. QG deliberately keeps that extrapolation open.

### 4.4 First closed-form refutation and B′

QG5 produces a fresh exact `n=3` instance where the original closed form predicts 11 but exact truth is 10. The support-two theorem remains exact: `C_D++=10`. The missing mechanism is an out-of-own-target-support phantom borrow omitted by the original B family. The separately frozen B′ enlargement repairs this row and the registered successor panels.

### 4.5 Fourth regime and B″

QG7 attacks B′ and finds 64 exact witnesses with

`C_D++ < min(C_D+, f_B′)`.

The new mechanism combines a weight-two Tag with phantom borrowing. QG7b freezes B″ and closes all 10,481 registered hostile/legacy instances with zero fifth-configuration candidates.

Yet this is still finite evidence. QG7c closes the high-Tag exchange and three of four residual shape classes all `n`, but a pinned `comm-s2` consolidation sector remains lemma-open. A hostile realization of the worst local patterns finds zero identity gaps, so the open state is **lemma-open, not currently counterexample-open**.

This distinction is characteristic of regime geometry: exact support complexity is solved, while the smallest explanatory closed form is not.

## 5. Objective geometry: the phase map belongs to `(family, objective)`

An apparent compiler regime can be an artifact of the objective used to price configurations. ORION-10 explicitly reweights the TARE structural objective.

### 5.1 O1: support-two world breaks

Under the registered O1 weights, chemistry donor exactness disappears on all 30 recorded matchings. The original two-trade identity fails on 4,484 structured-`n=2` instances. More importantly, ORION-10 records an exact `NEW_SUPPORT3` witness in which a support-three construction has cost 11 while the best support-two construction costs 13 and the simpler D+ family costs 23.

Thus the R6S support-two theorem is **objective-scoped**. It is exact under the unit/raw-support objective and not a universal property of the grammar under arbitrary weights.

### 5.2 O2: geometry is exactly invariant

A second objective adds a constant per-rotation price while every member of the compared family carries the same rotation count. A machine-checked constant-shift argument shows that every within-family cost is translated by the same amount. Regime membership and the original predicate therefore transfer exactly.

The pair O1/O2 yields the field-level conclusion: **objective changes can alter or preserve regime geometry for structural reasons that are themselves analyzable.**

### 5.3 Objective-indexed phase theorem

Committed wave-2 work derives an all-`n` support-two cone for the registered TARE family/objective weights. The theorem provides an exact region in weight space where the support restriction remains valid. Outside that cone, the proof certificate does not apply; absence of the proof is not itself evidence that support three is required. Sharpness beyond the proved statements remains a separate question.

## 6. Family II: SixLCU — a theorem-grade simple boundary

To test transfer, QG introduces a second compiler family rather than continuing to specialize TARE. SixLCU considers six-term LCU-style compilation with a finite family of set partitions, block factoring choices, and shared/dedicated index-ancilla encodings under a frozen `SELECT + PREP + WIDTH` structural cost.

The field-level question is the same: when is the incumbent exact, what structural trade defeats it, and how complex is the boundary?

Committed QG12 upgrades the registered P0 incumbent boundary to theorem grade for every admitted batch and `n` under the frozen model. This provides a second family in which the donor-optimal region can be characterized exactly rather than by learned average performance.

The more surprising result appears in QG15b. Under the registered natural feature language, SixLCU donor exactness is separated **exactly by one literal** on all 38,760 registered `n=2` instances:

`maxg2 == -2`.

Thus “simple boundary” is not merely a TARE accident; it transfers once.

But a two-family pattern is not yet a field law.

## 7. Family III: StabPrep — the template transfers, simple boundary does not

QG15 opens a third family: stabilizer-state preparation under a frozen gate/cost model, with an exact Dijkstra referee over complete stabilizer-state graphs containing 6, 60, 1,080 and 36,720 states at `n=1,2,3,4` respectively. The donor is a frozen greedy/echelon-style construction.

### 7.1 Template transfer

All five regime-geometry components remain meaningful.

**Donor region.** Donor exactness drops markedly with instance size (the committed record describes a decline from roughly 83% to 17.5% across the tested progression).

**Trade classes.** Four exact improvement classes are isolated: ORDER, PIVOT, ROUTE, and GLOBAL, each with serialized witnesses. The minimal GLOBAL example appears already at `n=1`, where the donor costs 4 and the exact optimum 2 for the registered state.

**Bounds.** No strict registered subextension closes the global residual, unlike TARE's support-two theorem. Instead the study derives bounded structural quantities/normal-form information under the exact state-graph model.

**Boundary representation.** The frozen positive-conjunction predicate ladder cannot express the exact donor boundary; its best form retains nonzero error.

**Prospective falsification.** Before opening the exact `n=4` panel, QG15 digest-stamps a regime/cost forecast. It is then refuted: only 100/120 regime labels and 67/120 exact costs match.

The prospective failure is not hidden or repaired inside the same protocol. It becomes the next research question.

### 7.2 QG15b: from model-complexity failure to information failure

A failed low-order predicate can mean “use a richer classifier.” QG15b tests a stronger possibility: perhaps the chosen natural feature representation does not contain enough information to decide donor exactness at all.

For SixLCU, the answer is clean: one feature literal still separates the registered boundary exactly.

For StabPrep, the frozen 13-feature vectors contain **12 mixed feature cells**—identical feature vectors attached to both donor-exact and donor-inexact instances. These cells induce an irreducible error floor of 43/1,146 under the frozen vocabulary, independent of predicate budget.

This converts an empirical predicate failure into a representation theorem on the registered data: no classifier that uses only those frozen features can achieve zero error, because the mapping from feature vector to regime label is not a function.

The field-level conclusion is therefore negative and precise:

> **boundary-is-low-order is not a universal property of compilation regime geometry; whether the natural structural vocabulary determines regime membership is itself a family-dependent scientific question.**

## 8. Cross-family synthesis

The three families share an investigative grammar but not an outcome grammar.

| Component | TARE | SixLCU | StabPrep |
|---|---|---|---|
| exact donor/incumbent region | finite + theorem/bound components | theorem-grade registered boundary | exact finite state-graph labels |
| explicit trade mechanisms | split, borrow, phantom/hybrid support-two configurations | registered structural incumbent-breaking trades | ORDER/PIVOT/ROUTE/GLOBAL |
| global search bound | all-`n` support≤2 under unit objective | family-specific theorem structure | no strict subextension closure; finite exact Dijkstra + bounded structural rules |
| simple structural boundary | finite predicates; later subfamily refinement | yes, one literal in registered vocabulary/domain | **no in frozen vocabulary**; mixed cells |
| objective dependence | explicit O1 refutation / O2 invariance / support cone | objective fixed in current family study | cost model fixed in current family study |
| prospective forecast | confirmations and refutations | registered family evidence | explicit `n=4` refutation |

The table is intentionally heterogeneous. A theorem in TARE is not “equivalent evidence” to a finite Dijkstra panel in StabPrep. The commonality is the **questions and authority types**, not one scalar performance score.

## 9. Relation to Instance Space Analysis and algorithm selection

ISA explicitly studies how instance features relate to algorithm performance and constructs regions/footprints in which algorithms are strong or weak. It supports algorithm selection and has been applied to quantum optimization, including QAOA parameter initialization. ORION-09 therefore cannot claim novelty for the broad sentence “instance structure determines which method works.”

The difference is in the scientific object and evidence.

First, regime geometry treats **family expressivity** and exact feasibility as central. A trade witness is a concrete compiler configuration with a verified cost gap, not only an observed algorithm performance difference.

Second, global structure can be theorem-grade: the TARE support ceiling and SixLCU incumbent boundary are mathematical restrictions on the exact family, not learned boundaries from sampled runtimes.

Third, objective dependence can be proved or refuted by exact resource vectors/counterexamples rather than inferred from changes in a fitted footprint.

Fourth, the feature representation itself is attacked. The StabPrep mixed cells show that a particular natural feature vocabulary cannot decide the exact boundary regardless of classifier complexity.

ISA is therefore a direct conceptual donor and a natural comparison framework; ORION-09's residual lies in **exact mechanistic characterization, proof/counterexample authority, and representation-level boundary falsification**.

## 10. Relation to quantum compilation and resource estimation

Modern quantum compiler work includes exact and heuristic circuit synthesis, hardware-aware mapping, Pauli/circuit optimization, and compilation-driven logical/physical resource estimation. These systems often optimize broader cost stacks than the structural objectives used here. ORION-09 does not claim a universal quantum compiler or full-resource phase diagram.

Instead, each family is intentionally small enough that its structural optimum can be refereed exactly or bounded tightly. This permits a different kind of result: a theorem/counterexample map explaining **why a restricted compilation family is or is not sufficient**.

## 11. Reproducibility and data contract

The paper must ship a cross-family evidence manifest. At minimum it should bind:

- TARE R6S/ORION-10/QG7/QG7b/QG7c receipts and protocols;
- SixLCU QG12/QG15b receipts;
- StabPrep QG15/QG15b exact-state and prospective receipts;
- independent generic verifier results where registered;
- publication-cut commit and exact content digests.

Each figure/table cell should carry an authority class (theorem, exact finite, prospective confirmation, prospective refutation, representation lower bound, open). A final reader should be able to reproduce the source number or witness without traversing narrative lane names.

## 12. Limitations

**Three families are not a universal field sample.** The paper demonstrates a transferable investigative template on three constructions. It does not establish that every quantum compiler has a useful regime geometry.

**Structural objectives.** The families use frozen structural cost models; physical runtime/space-time/error-rate conclusions require separate resource models.

**Feature dependence.** The StabPrep non-identifiability result is relative to the frozen 13-feature vocabulary and registered domains. A richer path/schedule-aware representation may restore determinacy.

**TARE closed-form endgame remains open.** The all-`n` support ceiling is proved, but the smallest explicit D+/B′/B″-style closed form retains one open consolidation link at this publication cut.

**Objective phases are scoped.** The proved TARE support cone and O1/O2 findings do not establish global sharpness across arbitrary objectives.

**No R6/physical advantage authority.** Every included research receipt retains its registered bounded/`NOT_R6` status.

## 13. Discussion

The central result emerged by repeatedly refusing two easy conclusions.

The first easy conclusion is that a successful finite classifier is a theorem. TARE's original predicate and a prospective fresh-subject confirmation looked convincing, yet later exact counterexamples revealed additional support-two configurations. The exact support theorem survived because it had different authority.

The second easy conclusion is that a failure of a simple classifier means “fit a more complex classifier.” StabPrep shows why that may be wrong. If the same feature vector contains both labels, more classifier capacity cannot recover the missing distinction; the representation must change.

Together these cases suggest a hierarchy of regime questions:

1. **Does the donor fail?** Find an exact counterexample.
2. **Why does it fail?** Identify the structural trade and witness.
3. **How large must the exact family be?** Seek support/budget/sufficiency theorems.
4. **Can the regime be predicted from structure?** Freeze a feature/predicate and test it prospectively.
5. **If prediction fails, is the boundary complex or unrepresented?** Test mixed feature cells / representation sufficiency.
6. **Does the geometry survive objective changes?** Derive a phase or exact counterexample.

A regime geometry is therefore closer to a **scientific model of a compiler family's failure modes** than to a leaderboard. The model is valuable precisely because refutation changes its structure.

## 14. Conclusion

Across TARE, SixLCU and stabilizer-state preparation, a common exact-analysis template transfers: identify the donor-optimal region, construct and referee trade witnesses, bound the exact search, test structural boundary rules, vary the objective, and freeze prospective predictions. What does not transfer is equally important.

TARE admits a theorem-grade support ceiling but an evolving support-two taxonomy. SixLCU admits a strikingly simple exact boundary in its registered vocabulary. StabPrep supports the same trade/bound analysis while refuting the assumption that natural structural features must determine donor exactness at all.

The durable field claim is therefore not that quantum compiler families have simple phase diagrams. It is that **compiler-family regimes can be treated as exact, falsifiable scientific objects—and boundary simplicity, objective robustness, and even representability should be measured rather than assumed.**