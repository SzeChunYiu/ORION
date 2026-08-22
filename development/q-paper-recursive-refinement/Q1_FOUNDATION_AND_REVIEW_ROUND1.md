# Q1 refinement round 1 — foundation, analogue calibration and review preflight

**Frozen manuscript:** `papers/Q-paper-01-tare-expressivity/MANUSCRIPT_SUBMISSION_DRAFT.md`  
**Stretch:** PRX Quantum  
**Fallback:** npj Quantum Information  
**Academic-method donor:** `ACADEMIC_PAPER_SKILLS_PIN.json`  
**Reviewer isolation:** `MUTUAL_BLINDNESS_NOT_GUARANTEED` — all three lenses are recorded separately, but this repository pass was produced in one orchestration context.

## 1. Foundation spine

### Question

How much auxiliary Pauli-frame support is intrinsically required to attain the exact optimum of the frozen three-block shared-Tag TARE-M2 compilation family as system size grows?

### Answer

The intrinsic uniform support number is exactly

`kappa_R6M = 2`.

Every admitted instance at every qubit count has an optimum with all auxiliary frame Paulis of support at most two, while an exact two-qubit instance proves that support one is not uniformly sufficient.

### Decisive evidence chain

1. **Analytic all-n upper bound.** The `F_2^2` zero-sum exchange preserves frame anticommutation and shared-Tag syndrome for support `>=3`; the local Restore penalty is at most 2 and never exceeds the frame refund.
2. **Exact sharpness witness.** The complete support-one family has `C_DP=5 < C_D+=6` on the frozen R6O `n=2` instance.
3. **Mechanistic identity.** The exact `w=2` parity obstruction of the proof is realized by the optimal frame-for-Tag trade.
4. **Independent machine corroboration.** The R6S local/class checks and fresh DP stress agree with the analytic result.
5. **Prospective finite-domain support.** The R6R benzene prediction was frozen before the exact result and is confirmed on all 15 matchings.

### Boundary

The theorem is for the declared R6M grammar and support-count objective. It is not a theorem for arbitrary TARE, arbitrary objective weights, arbitrary block encodings, or fault-tolerant physical resources. The finite R6Q two-trade classifier is not an all-n taxonomy; later QG work finds additional support-two subregimes.

### Meaning

The unrestricted representation permits auxiliary support growing with system size, yet optimal representation complexity has a constant coupling scale. This converts an apparently unbounded representation problem into an exact small-support normal form and exposes a concrete structural obstruction that explains why the constant is two rather than one.

## 2. Terminology ledger

| Canonical term | Use | Avoid / boundary |
|---|---|---|
| Tag-and-Restore Encoding (TARE) | donor method name | never imply introduced by ORION |
| R6M / three-block shared-Tag TARE-M2 family | frozen theorem family | do not shorten to “all TARE” |
| intrinsic uniform support number `kappa_R6M` | smallest support cap guaranteed to contain an optimum | distinguish from circuit gate locality |
| support-two normal form | theorem conclusion | not “two-qubit circuit” |
| shared Tag | global Pauli label operator in the frozen grammar | not a generic block-encoding ancilla |
| Restore cost `F3` | donor-owned local factor rule | do not imply novel primitive |
| `D+` | complete support-one family in the frozen objective | not arbitrary TARE baseline |
| `D++` | support-at-most-two family | not a new physical algorithm |
| coupling trade | structural exchange between frame/Tag/Restore costs | not physical entanglement trade |
| finite regime classifier | R6Q registered-domain result | not universal taxonomy |

## 3. Close-analogue calibration

This is a structural/evidence study only; no wording or distinctive figure design is copied.

### Analogue A — PRX Quantum, “Unitary synthesis with fewer T gates” (accepted 10 Aug 2026)

Observed transferable functions:

- opens with a broadly recognized synthesis problem and an explicit previous-best comparison;
- makes the main scaling improvement the abstract's central object;
- states the remaining lower-bound gap rather than implying closure of all synthesis;
- mechanism/proof technique is linked directly to the achieved bound.

Q1 adoption:

- lead with the intrinsic-complexity question before ORION/R6 vocabulary;
- make `kappa=2` the single abstract memory object;
- place grammar/objective boundary in the same high-level story rather than hiding it in limitations.

### Analogue B — PRX Quantum 2026 MCR compiler paper

Observed transferable functions:

- identifies a structural transformation rule missing from current compiler simplifications;
- shows why the rule enlarges the reachable optimization space;
- follows the structural contribution with quantitative compiler evaluation.

Q1 adoption:

- make the proof obstruction / optimizer mechanism correspondence a principal figure and result, not a historical R6 anecdote;
- use chemistry/prospective examples as confirmation of structural understanding, not the novelty anchor.

### Analogue C — PRX Quantum, “How to Fault-Tolerantly Realize Any Quantum Circuit with Local Operations” (2025)

Observed transferable functions:

- theorem statement has broad operational consequence visible from the abstract;
- proof result and overhead consequence are separated clearly;
- scope is broad enough that readers can understand what changes without knowing internal implementation nomenclature.

Q1 adaptation:

- translate R6M language into a reader-facing compiler-family definition before internal labels;
- make the polynomial direct-normal-form consequence visible as a corollary, while explicitly refusing to call it a production-DP speedup.

### Rejected analogue transfer

- Do not imitate the broadness of “any quantum circuit.” Q1 does not have that scope.
- Do not invent a fault-tolerant resource consequence to resemble the accepted papers.
- Do not add unrelated chemistry benchmarks merely to increase figure count.

## 4. Editorial triage simulation — PRX Quantum

**Posture:** `SEND_TO_REVIEW_POSITIONING_RISK`

### Strengths

- exact all-n theorem with a sharp lower-bound witness;
- short analytic mechanism rather than empirical extrapolation;
- proof boundary equals an optimizer-realized coupling mechanism;
- reproducible exact/machine evidence and honest later counterexample disclosure;
- clearly inside quantum compilation/block-encoding theory.

### Main editorial risk

The current first page still asks the editor to accept that this specific shared-Tag TARE-M2 family is important enough for PRX Quantum's exceptionality bar. The theorem is strong; the breadth/consequence story is less developed than the mathematics.

### Minimum valid repair

`CLARIFY_OR_RESTRUCTURE`, not new experiments:

1. frame the paper as an exact result about **intrinsic representation complexity** in a nontrivial block-encoding compiler family;
2. add a compact “why the theorem matters” paragraph that distinguishes representation complexity from gate locality and explains the reduction from arbitrary support to constant support;
3. make the proof-obstruction/optimal-trade identity a main visual/evidence object;
4. include a PRX-style popular summary written for a quantum-information reader outside TARE;
5. keep the PRX stretch claim as `exceptional_insight`, not `exceptional_quantum_advantage`.

## 5. Reviewer lens 1 — VALIDITY

**Overall:** strong technical case; no central technical blocker identified from the frozen materials.

### Q1-R1-V1 — definition/proof interface

- Class: `MAJOR_REPAIRABLE`
- Claim: the theorem covers every admitted target/matching/permutation/central choice.
- Evidence: analytic proof + frozen grammar definition.
- Concern: the manuscript should make explicit, in one proposition/assumptions block, which feasibility constraints are invariant under the coordinate-zeroing exchange. A skeptical reader should not need to infer that no hidden grammar condition changes.
- Resolution test: a short lemma/assumption checklist showing that the exchange preserves nonzero frame, anticommutation, common Tag labels and leaves all other block choices unchanged.
- Repair: `CLARIFY_OR_RESTRUCTURE`.

### Q1-R1-V2 — `O(n^12)` corollary wording

- Class: `CLAIM_RECALIBRATION`
- Claim: polynomial-size direct normal-form family.
- Concern: readers may mistake the candidate-count corollary for a computational-complexity result.
- Existing defense: manuscript already says this is not a production-DP speedup.
- Resolution test: retitle the section as a representation-count corollary and repeat the non-algorithmic boundary in the first sentence.
- Repair: `CLARIFY_OR_RESTRUCTURE`.

## 6. Reviewer lens 2 — POSITIONING / SIGNIFICANCE

**Overall:** plausible PRX Quantum exceptionality through structural insight; fallback npj QI is strong.

### Q1-R1-P1 — nearest-work equivalence search

- Class: `MAJOR_REPAIRABLE`
- Concern: the novelty map searches TARE/support/Pauli-frame language, but the paper should explicitly discuss whether an equivalent normal-form theorem could be phrased as symplectic support reduction, local Clifford simplification, or unitary-partitioning sparsification.
- Evidence pointer: `NOVELTY_RESEARCH_2026-08-22.md` + final refresh.
- Resolution test: related-work table listing nearest mechanism and the exact missing theorem/consequence for each route.
- Repair: `CLARIFY_OR_RESTRUCTURE` plus final literature refresh.

### Q1-R1-P2 — PRX consequence breadth

- Class: `PUBLICATION_CRITERIA_BLOCKER` for the stretch target only; nonblocking for npj QI.
- Criterion: exceptional insight / broad and lasting QIST impact.
- Concern: the theorem is currently presented as a strong exact result inside one frozen six-target grammar. The manuscript has not yet demonstrated that the normal-form principle transfers beyond that grammar; later QG evidence exists but is intentionally excluded from Q1 ownership.
- Resolution test for PRX without adding QG science: show clearly that (a) the unrestricted support can scale with `n`, (b) the exact optimum provably has a constant coupling scale, (c) the obstruction is a genuine compiler trade, and (d) this changes how this whole TARE compiler family should be optimized/understood. If an editor still requires cross-family generality, this is target fit rather than a missing Q1 theorem.
- Cheapest repair: `CLARIFY_OR_RESTRUCTURE`; if still judged too narrow, `CHANGE_TARGET_OR_ARTICLE_TYPE` to npj QI.

## 7. Reviewer lens 3 — REPRODUCIBILITY / BOUNDARY / READABILITY

**Overall:** reproducibility unusually strong for a theory/compiler paper; presentation can become easier to evaluate.

### Q1-R1-R1 — main visual evidence absent

- Class: `MAJOR_REPAIRABLE`
- Concern: the manuscript has a figure plan but the central proof mechanism is text-heavy. A reader should be able to see the support descent and the support-two obstruction without reconstructing `F_2^2` cases mentally.
- Resolution test: Figure 1 or 2 shows unrestricted-to-support-two descent, preserved parities, and the failing `w=2` pattern that corresponds to the exact counterexample.
- Repair: `CLARIFY_OR_RESTRUCTURE` + `FIGURE_AUDITOR`.

### Q1-R1-R2 — data/code availability

- Class: `CLARITY_OR_REPORTING`
- Concern: the repository paths are listed, but the submission manuscript should contain normal Code/Data Availability text rather than only internal reproduction notes.
- Resolution test: explicit statements naming code/results repository and what is needed to reproduce theorem sanity checks and finite panels.
- Repair: `CLARIFY_OR_RESTRUCTURE`.

## 8. Editor synthesis

### Open decision-relevant risks

1. `Q1-R1-P2` — PRX breadth/exceptionality is the only stretch-target publication blocker; it is primarily a positioning/target-fit risk, not a scientific-validity failure.
2. `Q1-R1-V1` — proof-interface assumptions should be made locally explicit.
3. `Q1-R1-P1` — nearest-work comparison should be presented as an exact theorem-delta table.
4. `Q1-R1-R1` — central structural figure needed.
5. `Q1-R1-R2` — standard availability section needed.

### Do not waste effort on

- another random/chemistry sweep that does not test a new theorem implication;
- importing QG support-one/objective-cone results into Q1;
- claiming fault-tolerant savings without end-to-end accounting;
- expanding the paper around ORION's chronological R6 discovery history.

## 9. Round-one engineering scores

These are prioritization signals only.

| Dimension | Score /10 | Rationale |
|---|---:|---|
| problem_and_question | 9.2 | precise and falsifiable |
| contribution_clarity | 9.1 | sharp theorem, but R6M nomenclature still appears early |
| claim_evidence_alignment | 9.6 | analytic proof + exact lower bound |
| technical_rigor | 9.4 | strong exact structure and corroboration |
| novelty_positioning | 8.2 | bounded search strong; equivalence table can improve |
| significance_or_field_advance | 7.7 | central PRX risk is scope/consequence |
| generality_and_boundaries | 8.3 | all-n within family, explicit external limits |
| reproducibility_and_availability | 8.8 | unusually strong internal package; journal-style availability pending |
| figure_data_statistics_quality | 7.0 | figure plan exists but central visuals not rendered |
| writing_and_evaluability | 8.3 | theorem-first, still technical in first page |
| venue_fit | 7.6 | strong npj QI; PRX stretch depends on exceptionality framing |

**Mean:** 8.47/10.

### Round-one terminal

- PRX Quantum: `CONTINUE_REFINEMENT__POSITIONING_RISK`
- npj Quantum Information: `READY_AFTER_REPAIRABLE_PRESENTATION_CLOSURE`

No new Q-era scientific experiment is requested by this round.
