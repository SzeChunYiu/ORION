# ORION-QG Wave 3 frontier map — 2026-08-22

Branch: `codex/orion-qg-wave3-frontier-20260822`
Parent programme: #740
Status: **RESEARCH REGISTRATION / NO OUTCOME AUTHORITY.**

This document extends the ORION-QG knowledge map after the wave-1/wave-2 results already on `main`. It does not alter, reinterpret, or weaken any frozen predecessor protocol or receipt. It registers three orthogonal frontier objects whose experiments/theorems require their own pre-outcome freezes.

## 1. Why a third wave is scientifically justified

The programme has moved beyond the original question "does compilation regime geometry exist?" Several much sharper facts are now earned:

1. **R6I intrinsic support collapsed from the original rank-based bound to one.** QG-9 V6 proves `C_DP=C_cap1` for every n under the frozen unit objective, hence `kappa_R6I=1`. QG-6 separately finds a rewrite-relevant production syndrome rank of five. The mismatch `rank=5` versus `kappa=1` is evidence that a DP/conserved-state dimension need not be the minimal state needed for a normal-form theorem.
2. **TARE remains structurally unresolved at the last all-n links.** R6S proves support<=2; QG-7 found a fourth support-two mechanism; QG-7b enlarged the closed form to B'' on verified domains; QG-7c closed the weight>=3 Tag route and most normalization classes but left the pinned comm-s2 sector lemma-open. QG-18 separately asks whether TARE's intrinsic support number is one or two.
3. **Low-order regime boundaries are family-dependent.** SixLCU has an all-instance exact P0 boundary derived from low-order structure. StabPrep transferred the regime-geometry template but refuted a universal low-order-boundary motif. QG-15b sharpened that refutation: the frozen natural 13-feature vocabulary has mixed cells and cannot determine donor exactness at any predicate budget.
4. **Objective-indexed theorem regions exist, but certificate boundary and true phase boundary are not the same object.** QG-8 and QG-16 derive all-n polyhedral sufficient cones. QG-17 is frozen specifically to attack global sharpness outside the R6I support-one cone. A proof cone can be conservative.
5. **The programme now has enough exact families to ask structural meta-questions.** TARE, R6I, SixLCU and StabPrep provide positive and negative controls with different support, trade, predicate and state-complexity behavior.

The frontier should therefore move from collecting more examples toward explaining **what generates all improving moves, what information is minimally necessary to decide a regime, and how robust a certified regime is under parameter/stack drift**.

## 2. Cross-disciplinary review panel

The Wave-3 research map was stress-tested through four roles. These are reasoning lenses, not scientific authorities.

### A. Quantum-compilation theorist

Role: protect exact compiler semantics and distinguish local rewrite facts from all-n/global-optimum claims.

Main objection to a naive frontier: another list of TARE/StabPrep examples would be incremental. The next theory should explain whether the observed split/borrow/deletion/relocation moves form a complete primitive basis, and it must treat whole-system Tag relocation as a warning that purely local grammars can miss decisive moves.

### B. Discrete-optimization / algebraic-combinatorics reviewer

Role: subtract known mathematics and identify the strongest classical abstraction that could subsume the compiler behavior.

Main observation: universal test sets/Graver directions, circuit augmentation, discrete-convex exchange axioms, and normal-fan geometry are direct donor concepts. The scientifically interesting residual is not to rediscover those objects, but to determine whether the **exact quantum compiler fibers admit them with a stabilizing finite move orbit basis**, or to exhibit the semantic coupling that prevents such a representation.

### C. Formal-methods / automata reviewer

Role: distinguish a convenient hand feature vector from an exact sufficient state.

Main observation: QG-15b's mixed cells are a state-abstraction failure, not merely a predicate-search failure. The right next object is the coarsest exact continuation-equivalence quotient for regime labels/value, then a prospective interpretable vocabulary derived from that quotient. Myhill-Nerode, bisimulation, weighted-automata minimization and abstract interpretation are donor methods.

### D. Fault-tolerant/QRE systems reviewer

Role: ensure structural theorems remain scoped when compiler objectives are induced by uncertain hardware/QEC/resource models.

Main objection to binary `inside/outside` reporting: practical objective coefficients and stack maps move. The next object should quantify theorem **certificate margins**, propagate uncertainty sets through affine/piecewise-affine stack maps, and never launder a sufficient-cone margin into a true physical phase boundary.

### Panel convergence

All four reviewers converge on three non-duplicative Wave-3 lanes:

- **QG-19 / #862 — universal trade/test-set calculus.** Is there an objective-independent primitive move basis for a compiler family, and does it stabilize with n?
- **QG-20 / #863 — minimal regime state.** What is the coarsest exact compiler-state quotient that preserves regime/value decisions, and what information was absent from StabPrep's failed natural vocabulary?
- **QG-21 / #864 — certified regime robustness.** What exact parameter/stack uncertainty region preserves theorem authority, and how tightly can theorem margins be bracketed against true phase changes?

These lanes are deliberately orthogonal to QG-7d, QG-15c, QG-17 and QG-18. They may consume those results but do not replace them.

## 3. Wave-3 lane graph

```text
QG-7 / QG-7b / QG-7c ----\
QG-9 V6 / QG-13 ----------> QG-19 universal move/test-set basis
QG-8 / QG-16 -------------/               |
                                             +--> candidate complete move -> phase fan

QG-15 / QG-15b -----------> QG-20 exact regime-state quotient
exact compiler graphs ------/               |
                                             +--> QG-15c vocabulary design/control

QG-8 / QG-16 ----\
QG-17 sharpness ----> QG-21 certified robustness margins
QG-10 intervals ----/        |
QG-11 FT transfer ----------+--> hardware/QEC robustness tube
QG-14 composition ----------+--> compositional invalidation margin
```

### Anti-contamination rules

- QG-20 must not retrospectively modify a QG-15c feature freeze. If QG-15c has frozen first, QG-20 is explanatory/control evidence only; if QG-20 supplies candidate coordinates first, QG-15c must freeze them before outcome.
- QG-19 finite-n move saturation cannot self-promote to all-n stabilization.
- QG-21 certificate margins cannot be called true phase margins without separate sharpness/completeness evidence.
- No Wave-3 lane may alter the frozen QG-7/QG-8/QG-9/QG-12/QG-15/QG-16/QG-17 results/protocols.

## 4. Atomic knowledge gaps after Wave 2

The programme should not treat a high-level label such as "regime geometry solved" as closure while any load-bearing atomic gap below remains unqualified.

| Gap | Current state | Decisive next owner |
|---|---|---|
| TARE intrinsic support `kappa` | `1 or 2` | QG-18 |
| TARE B'' all-n exact classification | pinned comm-s2 normalization lemma open | QG-7d |
| R6I support-one cone global sharpness | certificate cone proved; true boundary open | QG-17, then QG-21 |
| Complete primitive trade basis | four TARE configurations known; no universal basis theorem | QG-19 |
| Move-basis stabilization with system size | untested | QG-19 |
| Why StabPrep natural features fail | mixed cells known; missing exact state coordinate unidentified | QG-20 |
| Minimal regime-state information | undefined/measured nowhere | QG-20 |
| Feature-determination after enlarged vocabulary | registered but not yet earned | QG-15c, informed by QG-20 under freeze discipline |
| Certified uncertainty radius of phase theorems | absent | QG-21 |
| True-boundary bracket vs proof-boundary | partial witness machinery only | QG-17 + QG-21 |
| Regime geometry without exact referee | interval calibration still required | QG-10/QG-10C |
| Structural-to-FT phase transfer | registered | QG-11 |
| Cross-subroutine certificate composition | registered | QG-14 |
| Scalable regime-state/test-set behavior across families | no theorem | QG-19/QG-20 successors |

## 5. Recommended execution order

The fastest way to push the frontier without manufacturing a new backlog is to resolve existing decisive residuals and start one bounded calibration in each Wave-3 axis.

### Tier 0 — close cheap/decisive active residuals

1. **QG-18 Q1 necessity hunt** on committed TARE support-two witnesses. A single `C_DP<C_cap1` witness decides `kappa_TARE=2`; if absent, the whole-system relocation theorem route becomes sharply motivated.
2. **QG-7d pinned comm-s2 last link.** It is already delimited by the exact failure census; this is the shortest route to an all-n finite TARE trade envelope or an explicit obstruction.
3. **QG-17 frozen sharpness scan.** The candidate generator and outside objectives are already frozen, so executing it supplies high-value witness hyperplanes for QG-21.

### Tier 1 — first Wave-3 calibrations

4. **QG-19 on R6I n=2..3 first.** Build an exact lifted semantic fiber and ask whether known local/relocation moves appear as primitive kernel directions. Stop immediately on representation mismatch rather than forcing an IP encoding.
5. **QG-20 on the complete bounded StabPrep graph.** Compute `E_label` before inventing any new human feature vocabulary. Map the 12 QG-15b mixed cells to exact distinguishing state/suffixes.
6. **QG-21 on QG-8/QG-16 only.** Reconstruct exact facets, calculate rational slacks/uncertainty containment, and bind equality controls. Add QG-17 witness-side true-boundary brackets only after QG-17 has an outcome.

### Tier 2 — transfer only after calibration earns it

7. QG-19 R6M/TARE move-basis stabilization and relation to the four known configurations.
8. QG-20 R6M/R6I regime-state quotients and asymptotic growth questions.
9. QG-21 QG-11/QG-14 stack/composition uncertainty transport.

## 6. New research hypotheses — falsifiable, not claims

### H19 — finite primitive compiler move basis

For at least one exact ORION-QG compiler family there exists a finite orbit set of semantics-preserving primitive moves, independent of linear objective coefficients, such that a feasible state is globally optimal iff no feasible move in the set improves it.

Falsifiers: context-dependent moves not representable by a fixed kernel/test set; new primitive orbit classes keep appearing with n; no exact lifted fiber preserves the semantics.

### H20 — regime labels require less state than exact values

For at least one family, the coarsest exact state quotient preserving donor/regime labels is strictly smaller than the quotient preserving exact residual values. StabPrep's 13 natural features are too coarse, but the full optimizer state may be unnecessarily fine.

Falsifiers: `E_label` is essentially as large as `E_value`, or quotient size grows so rapidly that no meaningful compression is observed on exact domains.

### H21 — theorem authority has a useful nonzero robustness tube

For practically relevant objective/stack uncertainty sets, at least one ORION-QG phase theorem remains valid over a nontrivial certified neighborhood, and the certificate margin can be bracketed against explicit outside witnesses without false authority continuation.

Falsifiers: the operating points sit on/near certificate facets; stack nonlinearities make a single structural coefficient enclosure unusably loose; composition introduces hidden couplings that invalidate positive local margins.

## 7. Donor map / literature anchors

The following are **mandatory prior-art absorptions**, not novelty support:

- J. E. Graver, *On the foundations of linear and linear integer programming I*, Mathematical Programming 9 (1975): universal integer-program test-set/Graver-basis foundation.
- S. Onn, *Nonlinear Discrete Optimization* and later circuit/Graver-walk work, including arXiv:2410.00656: augmentation/test directions and modern Graver/circuit perspective.
- K. Murota, *Discrete Convex Analysis*: M-convex exchange/local-to-global optimality machinery.
- Classical Myhill-Nerode, bisimulation, weighted-automata minimization and abstract-interpretation quotients: state-minimization machinery for QG-20.
- Multi-parametric/robust optimization and sensitivity analysis: critical regions, normal fans, uncertainty-set containment and dual-norm margins for QG-21.
- qstack (arXiv:2605.16595), AutoQuREO (arXiv:2608.12936), Harvest (arXiv:2608.03315), Microsoft/current QRE stacks: full-stack/FT composition and resource-estimation donors for QG-11/QG-21 transfer.

The novelty question for each Wave-3 lane is narrower: does the **frozen quantum compiler semantic object** admit a useful exact instantiation of these donor abstractions, with a proof-carrying result or first-class refutation not already supplied by the donor literature?

## 8. Claim and safety boundary

- `NO_OUTCOME_AUTHORITY`: this map contains questions/protocol directions, not scientific results.
- `NOVELTY_NOT_AUTHORIZED`: absence of a known close parent is never internal novelty authority.
- No physical quantum advantage follows from a compiler normal-form, resource-estimator, FT-transfer or composition result.
- Protected existing ORION task branches/artifacts are untouched by this Wave-3 registration.
- The protected stretched-N2 subject remains sealed and is not a QG subject.

## 9. Definition of progress

Wave 3 is successful even if one or more hypotheses are refuted. A high-value terminal is any of:

1. a theorem that reduces a previously global compiler question to an exact finite move/state/margin object;
2. a minimal counterexample proving such compression is impossible under the frozen representation;
3. a new missing semantic/coupling coordinate localized by an exact refutation;
4. a prospective calibration with zero false certification and explicit CANNOT_CHECK outside earned coverage.

The programme should continue to prefer **theorem, exact counterexample, bounded saturation with an honest ceiling, or CANNOT_CHECK** over an attractive but unqualified frontier narrative.
