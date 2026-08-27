# ORION-09 publication foundation V2 — Compilation regime geometry

**Paper:** ORION-09  
**Publication cut:** `main@ca7df1055a43f97eaf8d142a62011c4c261af368`  
**Evidence waves included:** committed wave 1 + committed wave 2 only  
**Excluded:** open/unmerged QG-9/QG-16/QG-17 successor branches unless the publication cut is explicitly advanced  
**Status:** `FOUNDATION_REBUILT__WAVE2_MANUSCRIPT_SYNTHESIS_REQUIRED`

## 00 — Scope

### Field object
A **compilation regime geometry** for a compiler family/objective is a structured scientific object containing:

1. a donor/incumbent-optimal region;
2. explicit elementary trade mechanisms with exact/minimal witnesses where possible;
3. sufficiency or support/budget bounds delimiting the search space;
4. structural conditions/predicates for regime membership when such a representation exists;
5. objective dependence / phase structure;
6. prospectively frozen predictions and refutations;
7. an explicit statement when the natural feature vocabulary does **not** determine regime membership.

### Prior-art subtraction
- Rice-style algorithm selection and **Instance Space Analysis (ISA)** already own the broad idea of relating instance features to algorithm performance regions/footprints and automated selection.
- QAOA work has already applied ISA to quantum-algorithm parameter/initialization performance across instance classes.
- Quantum compilation/resource-estimation literature already owns resource-aware compiler optimization, architecture-aware compilation and empirical profiling.

ORION-09 therefore does **not** claim that feature-dependent performance regions or algorithm selection are new. Its residual is the **exact mechanistic regime object for compiler-family expressivity**, where boundaries can be theorem-grade, counterexample-defined or proven non-identifiable in a frozen vocabulary.

### Cross-paper ownership
- ORION-01 owns the detailed TARE support theorem/counterexamples.
- ORION-09 uses TARE only as the first regime-geometry instance and owns the cross-family synthesis.
- ORION-10 owns static forecasting/certification and its refutation/repair sequence.

## 01 — Research canon

### TARE family
1. The frozen TARE unit-cost/raw-support objective has an all-`n` support-two theorem: `C_DP=C_D++` for every `n`/instance under the R6M grammar.
2. The simple original two-trade map is not all-`n` complete; QG5 and QG7 exact counterexamples reveal additional support-two configurations.
3. QG7b B″ closes 10,481 registered finite instances with zero fifth-configuration candidates.
4. QG7c closes high-Tag support and three of four remaining shape classes but leaves the pinned comm-s2 consolidation link open; hostile realizations show no identity gap. Therefore the current all-`n` closed-form family identity remains **OPEN**, even though the support-two theorem is closed.

### Objective dependence
5. Under reweighted objective O1, chemistry donor exactness vanishes, the original two-trade identity fails on 4,484 structured-`n=2` instances and a support-three trade becomes exactly necessary on registered witnesses; the unit-cost support-two geometry is not objective-universal.
6. Under objective O2, a constant-shift lemma leaves the regime geometry invariant within the family. Thus objective perturbations can be geometry-changing or geometry-preserving for structural reasons.
7. QG8 (committed wave-2) derives an all-`n` support-two objective cone for the registered TARE family; boundary sharpness beyond its stated theorem remains separate.

### SixLCU family
8. The SixLCU second family instantiates the template with its own incumbent boundary; committed QG12 upgrades its P0 boundary to theorem grade for every admitted batch/`n` in the registered model.
9. Its donor-exact boundary is exceptionally simple in the registered natural vocabulary: QG15b finds exact separation with one literal (`maxg2 == -2`) on the 38,760-instance registered domain.

### StabPrep family
10. QG15 transfers the five-part template to stabilizer-state preparation with exact Dijkstra referees over complete state graphs through `n=4`.
11. The donor-exact region changes strongly with size; four trade classes are witnessed.
12. No strict registered subextension closes the global residue; bounded budget rules/normal-form structure survive instead.
13. The frozen low-order predicate ladder fails, and a digest-stamped prospective `n=4` forecast is refuted (regime 100/120; cost 67/120), with exact witnesses retained.
14. QG15b shows the failure is not merely insufficient predicate complexity: in the frozen 13-feature vocabulary, 12 mixed cells contain both labels, giving an irreducible 43/1,146 classification floor. The natural feature vocabulary does not determine the boundary.

### Field-level boundary
15. Therefore a 'simple boundary' is not part of the universal regime-geometry template. The transferable object is the **question of boundary representation/identifiability**, not the answer that it is low-order.
16. Every QG authority included here is `NOT_R6`; regime geometry does not itself prove physical resource advantage or donor novelty.

## 02 — Evidence table

| Field proposition | Evidence | Class | Status / boundary |
|---|---|---|---|
| TARE exact optimum lies in support≤2 all `n` | R6S | machine-checked theorem | `PROVEN_ALL_N`, frozen R6M/raw-support only |
| original TARE two-trade map is complete all `n` | QG5/QG7 | exact counterexamples | `REFUTED` |
| four registered TARE trade configurations suffice on current finite hostile panels | QG7b | finite exact/machine evidence | `SUPPORTED_BOUNDED`; all-`n` classification open |
| high-Tag weights are unnecessary in current classification chain | QG7c | all-`n` exchange component | theorem component; pinned comm-s2 link open |
| regime geometry depends on objective | ORION-10 O1/O2 | exact counterexamples + constant-shift theorem | `SUPPORTED` for registered objectives |
| TARE support-two phase has an objective cone | QG8 | machine-checked theorem | exact stated cone; global sharpness separate |
| SixLCU boundary is simple/feature-determined | QG12/QG15b | exact theorem/domain classification | `SUPPORTED` in registered model/vocabulary |
| StabPrep template transfers | QG15 | exact Dijkstra finite states + prospective holdout | `SUPPORTED_BOUNDED` through registered `n` |
| StabPrep donor-exact boundary is low-order in natural features | QG15/QG15b | exact mixed feature cells | `REFUTED` |
| StabPrep boundary is determined by frozen 13-feature vocabulary at any complexity | QG15b | mixed-cell lower bound | `REFUTED` on frozen vocabulary/domain |
| every compiler family has a simple exact regime predicate | StabPrep | counterexample to field motif | `REFUTED` |
| ISA/algorithm-selection feature maps are novel to ORION-09 | external donor literature | prior art | `DONOR_OWNED` |
| exact mechanistic regime-geometry template is externally novel | fresh search + paper cards | novelty proposition | `OPEN_UNTIL_SEARCH_CLOSES` |

## 03 — Argument map

### Tension
Compiler research often reports average improvements or learned/empirical algorithm-selection regions. But an optimization family can have qualitatively different structural reasons why a donor is optimal, why it fails and whether those failures can be predicted from input structure.

### Central question
Can compiler-family behavior be characterized as an **exact or falsifiable regime geometry** whose components survive transfer across distinct quantum-compilation families—and which components fail to transfer?

### Central answer
Three registered families support a common investigative template—donor region, trade/counterexample mechanisms, search-space bounds, boundary representation and prospective falsification—but they do **not** share the same geometry. TARE admits exact support and objective-phase structure; SixLCU has an unusually simple exact incumbent boundary; StabPrep transfers the trade/bound framework while refuting the idea that natural features must determine a simple boundary. The negative cross-family result is central: **boundary identifiability is itself a family-dependent property.**

### Evidence sequence
1. Define regime geometry and subtract ISA/algorithm-selection prior art.
2. TARE as first exact instance: theorem + counterexample-driven enrichment.
3. Objective perturbation: show geometry is indexed by `(family, objective)`.
4. SixLCU as independent transfer: theorem-grade simple boundary.
5. StabPrep as third transfer: trade/budget structure survives while simple-boundary motif fails.
6. QG15b: prove the StabPrep failure is a representation/identifiability issue in the frozen vocabulary, not just shallow predicate search.
7. Synthesize what transfers and what does not.

### Strongest alternative interpretation
**"This is Instance Space Analysis with hand-written features."** ORION-09 must distinguish empirical performance footprints from its exact mechanistic objects: explicit feasible-family containments, machine-checked support/budget theorems, exact counterexamples/witnesses, objective-phase conditions and lower bounds showing feature non-identifiability in a frozen vocabulary. ISA remains a required donor/analogue field.

### Durable conclusion
The transferable contribution is not a universal phase diagram. It is a disciplined way to ask which compiler choices are exactly necessary, which structural trades delimit donor optimality, how the answer changes with objective, and whether the boundary is even representable in the natural feature language.

## 04 — Section contracts

### Title / Abstract
Headline cross-family transfer **and** the major negative: boundary simplicity does not transfer. Avoid presenting ORION-09 as a TARE sequel.

### Introduction
Position against:
- algorithm selection / ISA;
- quantum compiler optimization/profiling;
- resource-aware compilation;
- exact circuit/stabilizer synthesis.
Research gap is exact *mechanistic* regime characterization and falsifiable cross-family transfer.

### Field definition
Treat 'regime geometry' as a definition/framework unless a specific theorem is cited. Do not turn the definition itself into novelty evidence.

### TARE Result
Compress ORION-01 mathematics; cite companion. Show only the evidence needed for the field object: exact support ceiling, trade ladder, objective dependence and current open closed-form link.

### SixLCU Result
Show second-family transfer and exact boundary theorem. Explain why its boundary is simple under the registered features.

### StabPrep Result
Make the refutations prominent: subextension nonclosure, prospective forecast failure, no-clean-predicate result and mixed feature cells.

### Cross-family synthesis
A table should classify each field component as `theorem`, `finite exact`, `prospective confirmed`, `prospective refuted`, `non-identifiable in vocabulary`, or `open` for each family. Do not use one averaged score.

### Discussion
Explain three layers:
1. invariant investigative template;
2. family/objective-specific mathematics;
3. representation-dependent boundary complexity.

## 05 — Figure contract

1. **Figure 1 — Regime-geometry object:** donor region, trades, sufficiency bound, boundary representation, objective axis, prospective falsification.
2. **Figure 2 — TARE discovery ladder:** D -> D+ -> B/B′ -> B″ inside theorem-backed D++, with refutation arrows and exact support ceiling separated from closed-form family completeness.
3. **Figure 3 — Objective phase:** O0/O1/O2 and the theorem/conterexample outcomes; no smoothing across objectives.
4. **Figure 4 — Cross-family transfer matrix:** TARE / SixLCU / StabPrep × five template components.
5. **Figure 5 — Boundary complexity:** SixLCU exact one-literal boundary versus StabPrep mixed-cell non-identifiability under the frozen vocabulary.

All quantitative panels regenerate from committed QG receipts; diagrams may be schematic only when explicitly labeled as such.

## 06 — Related-work / novelty search contract

Required donor cards before final novelty sentence:

- Rice/algorithm selection + modern Instance Space Analysis methodology;
- quantum ISA/QAOA instance dependence;
- exact quantum synthesis/Clifford/stabilizer optimization nearest work;
- resource-aware/compiler profiling work current through submission;
- TARE donor and Pauli/block-encoding optimization stack.

Novelty wording must be residual:

> exact/witness-carrying compiler-family regime characterization with theorem/counterexample/representation-failure components,

not:

> mapping where algorithms work best from instance features.

## Expert reconciliation

### Quantum-compilation theorist
Do not seek one universal trade taxonomy. ORION-09 is strongest when the objective/family dependence is an empirical/theoretical result rather than an embarrassment.

### Algorithm-selection / ISA reviewer
ISA is direct conceptual prior art for feature-to-performance regions. ORION-09 must articulate exact mathematical mechanisms/witnesses and boundary non-identifiability as the differentiator.

### Formal-methods reviewer
Each cross-family cell needs authority typing. The phrase 'theorem' cannot leak from TARE or SixLCU into StabPrep finite-state evidence.

### Experimental-design reviewer
Prospective refutations are valuable and must be as visually prominent as confirmations. Do not train/reselect predicates after observing the held-out outcome without labeling the successor study.

### Journal editor
The paper should be built around the cross-family surprise: the framework transfers, **simple boundary structure does not**. That is more publishable than a catalogue of QG lanes.

## Next gate

Before `MANUSCRIPT_V2`:

1. synchronize `CLAIM_LEDGER` to committed wave-2 evidence;
2. build donor Paper Cards for ISA/algorithm selection and nearest exact-compilation work;
3. freeze the five-figure evidence contract;
4. resolve whether the target is primarily quantum information, quantum software/compilation or algorithms/operations research, because the Introduction and related-work burden differs materially.