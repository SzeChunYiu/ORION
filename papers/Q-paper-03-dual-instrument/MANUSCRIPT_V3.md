# Prospective Dual-Instrument Measurement of Scientific Frontier Decisions: A Three-Question Case Series

**ORION-Q3 Manuscript V3 — scientific/content draft**  
Parent scientific base: `main@c5ba39fef4f25c46de5fb69bf07f50530f4693ca`  
Replacement scientific-result cut: `codex/q-qg-nature-skills-publication-closure-20260821@ca561ada07301ee7e45fc10e195dce8f077ea50c`  
Claim authority: `CLAIM_LEDGER_V2.md`  
No result in this paper grants R6, novelty, physical-advantage, or companion-paper authority.

## Abstract

Research agents are increasingly evaluated on completed tasks with known answers, yet a live research programme often needs a different measurement: before the next scientific result exists, do two structurally different decision instruments identify the same responsibility and choose the same discriminating next experiment, and does that frozen judgment survive the later result? We report a prospective three-question case series from the ORION-Q/QG quantum-compilation programme. Each valid unit freezes the unresolved scientific question and the outputs of two heterogeneous instruments before the successor scientific outcome is available: a tool-capable LLM/host research diagnosis and a typed deterministic non-LLM controller over the same receipt-transcribed state. Scientific outcomes are then generated independently and scored only under a predeclared deferred map. The original V0 unit produced inter-instrument agreement on regime characterization and was later aligned with finite regime-characterization outcomes. In Q3-R1, both instruments correctly treated a point just outside a proved support-two objective cone as certificate silence and selected an exact falsification panel; the independently executed 53-row panel found zero support-two gaps, leaving sharpness open. In Q3-R2, both instruments agreed that doubling a SixLCU SELECT coefficient likely made the theorem-grade P0 boundary objective-scoped and selected a complete reweighted census. The later exhaustive n=1/n=2 census contained 39,489 instances and **zero P0/label mismatches**. Under the prospectively frozen scoring rule, both diagnoses were therefore misaligned on the frozen domain even though the chosen experiment was correct. This explicit case shows why inter-instrument agreement is not validation. Two originally proposed successor questions were retained as contaminated rather than retrospectively scored when result-oriented branches became visible before instrument freeze. The case series is too small and too programme-specific for a reliability estimate; its contribution is a fail-closed measurement protocol that keeps agreement, scientific correctness, contamination, abstention and later outcome binding distinct.

## 1. Introduction

Scientific-agent benchmarks increasingly test realistic research tasks, executable analyses and end-to-end workflows. ScienceAgentBench, AstaBench, SciAgentArena and HeurekaBench are direct donors for that broad problem. ScientistOne and related research-integrity systems make claim/evidence provenance and verification first-class. A second literature asks whether LLM judges can themselves be trusted; REFLECT (`arXiv:2605.19196`) finds substantial failure in judge evaluation of evidence-based research agents. These works make it untenable to treat one model's confident diagnosis as a self-validating measurement.

A related problem appears when scientific ground truth does not yet exist. ValueBlindBench (`arXiv:2604.25224`) explicitly studies agreement-gated evaluation before delayed ground truth becomes observable. We therefore do not claim that preregistering judgments before delayed outcomes, or later calibrating them, is new. Agreement-metric work (`arXiv:2606.00093`) further shows that abstentions, invalid outputs and aggregation choices materially change what an agreement statistic means.

Q3 studies a narrower object inside one evolving research programme. At a live frontier, before the successor result exists, the programme may have two different decision instruments:

1. a tool-capable LLM/host path that can reconstruct evidence, search, reason and return a scientific diagnosis;
2. a typed deterministic controller that consumes a structured manifest of the same declared question state and selects from a frozen diagnosis/move vocabulary.

The instruments can agree for good reasons, agree because their shared packet already encodes the same bias, disagree because one representation omits a key distinction, or abstain because its own interface cannot decide. None of those relations is scientific truth. The later scientific result is the external event that can score the already-frozen judgment.

Our central question is therefore not “which agent is better?” It is:

> Can a research programme freeze heterogeneous instrument judgments before a live scientific outcome, retain contamination and invalidity instead of repairing them away, and later separate agreement from outcome alignment without granting either instrument scientific authority?

The three valid units produce a useful asymmetry. All three show agreement on the primary responsibility/move coordinates. Two have aligned diagnoses under their deferred maps. The third has **agreement but diagnostic misalignment** while retaining move alignment. We report those three rows directly and do not convert them into a reliability percentage.

## 2. Measurement contract

### 2.1 Unit of analysis

One unit is one prospectively frozen frontier question. Receipts, model calls, DP rows, compiler configurations and controller cycles are implementation evidence, not additional benchmark samples.

The valid series contains three units:

- V0: post-R6O responsibility diagnosis;
- Q3-R1 / QG-19: R6M objective-cone sharpness probe;
- Q3-R2 / QG-20: SixLCU P0 boundary under objective rescaling.

Two originally proposed candidate units, QG-7d and QG-15c, are retained as contaminated protocol events and are not counted as valid scored units.

### 2.2 Lane A: host/LLM instrument

Lane A is a tool-capable host research diagnosis. It may reconstruct evidence, reason over the frozen packet and choose a primary diagnosis and next move. For the replacement instances the executing model was GPT-5.6 Sol. The paper does not treat the model identity as the contribution, and V0 used the corresponding generic host/harness path rather than the exact same session/model execution.

### 2.3 Lane B: typed controller instrument

Lane B is deterministic over a frozen typed manifest. V0 used the ORION-Q campaign-control machinery. Q3-R1/R2 use a deliberately small question-specific typed controller whose rules are committed before the scientific analyzers. This is an **instrument class** comparison, not a claim that one byte-identical Lane-B program was repeated across all units.

The typed controller is non-LLM at decision execution, but the manifest/ontology is authored upstream. It is therefore not statistically or causally independent of Lane A.

### 2.4 Shared information and independence boundary

Both lanes receive the same named frontier question, declared evidence base, diagnosis vocabulary, move vocabulary and excluded future-outcome paths. Their representations differ: Lane A can reason from the human-readable/shared research packet; Lane B receives typed observations transcribed from that packet.

“Independent” in this manuscript means **separately frozen execution paths before outcome access**, not independent random samples or independent epistemic origins. Shared research history and packet construction can induce correlated errors. Q3-R2 demonstrates that this concern is real rather than theoretical.

### 2.5 Pre-outcome custody

For Q3-R1/R2, the sequence is mechanically auditable:

`question freeze -> shared packet -> Lane A -> Lane B manifest -> Lane B -> agreement receipt -> scientific analyzer/protocol -> scientific result -> deferred score`.

A workflow checks that the pre-outcome agreement commit predates the QG19/QG20 analyzer commits. The scientific analyzers contain no Q3 instrument imports.

### 2.6 Contamination rule

Immediately before instrument freeze, the target result surface is searched. If a result or result-oriented successor surface has become visible, the candidate is not backdated into a prospective test.

This rule invalidated the originally proposed QG-7d and QG-15c slots when public result-oriented branches were visible before Lane-A/Lane-B freeze. We did not open those branch result files for scoring. The two candidate instances remain in the audit ledger as `CONTAMINATED` and were replaced with new QG19/QG20 questions that had no result branches/artifacts at freeze time.

### 2.7 Deferred scoring

The instruments never score themselves. Each replacement protocol states, before outcome, which result terminal maps to which diagnosis/move alignment. `AGREE`, `PARTIAL`, `DISAGREE`, `CANNOT_CHECK`, and a later misalignment are admissible.

The scoring object is deliberately decomposed:

- inter-instrument responsibility relation;
- inter-instrument next-move relation;
- Lane-A responsibility alignment to later outcome;
- Lane-B responsibility alignment;
- Lane-A move alignment;
- Lane-B move alignment.

This decomposition prevents an agreed but wrong diagnosis from being hidden inside an “agreement score.”

## 3. V0: regime characterization

V0 asks what responsibility and next move follow after a shared-Tag TARE donor family is refuted by a second coupling regime.

Lane A diagnoses the missing object as representation/regime characterization and selects a regime-predicate computation as primary, with support-two closure complementary. Lane B identifies `RESP:REPRESENTATION_REGIME_UNCHARACTERIZED` and independently selects `COMPUTE:REGIME_CHARACTERIZATION`.

The pre-outcome relation is agreement on the scored responsibility and primary-move coordinates. Later scientific work provides the deferred check:

- R6Q finds an exact structural regime predicate on its registered finite domains;
- R6P closes the complementary support-two family on its registered domains.

V0 is therefore an `AGREE + DEFERRED_ALIGNED` unit under its frozen scoring contract. This statement is independently reconstructed by `replay_q3_v0.py` from the raw lane receipts and R6P/R6Q results.

V0 is one case. Its agreement is not a reliability estimate.

## 4. Q3-R1 / QG-19: certificate silence just outside a theorem cone

### 4.1 Frozen question

QG8 proves all-n support-two sufficiency for the R6M grammar inside the objective cone

`t_c >= 2 t_r` and `t_nc >= 2 t_r`.

Outside the cone, the certificate is explicitly silent; the theorem does not assert that support three is necessary.

Q3-R1 freezes

`O19 = (t_nc=4, t_c=3, t_tag=2, t_r=2, rho=0)`,

which lies one unit outside the central face and exactly on the noncentral face.

### 4.2 Frozen instruments

Both lanes select:

- diagnosis `R1_CERTIFICATE_SILENCE_SHARPNESS_OPEN`;
- move `M1_TARGETED_EXACT_OUTSIDE_CONE_PANEL`.

The pre-outcome responsibility and move relations are both `AGREE`.

### 4.3 Independent scientific outcome

Only after both lanes were frozen, QG19 instantiated the scientific protocol. It compares the unrestricted weighted exact DP with exact support-<=2 D++ on 53 frozen rows:

- 3 hostile n=1 rows;
- 2 hostile n=2 rows;
- 24 deterministic random n=2 rows;
- 24 deterministic random n=3 rows (seed `20260822`).

The result has **zero** rows with `C_DP < C_Dxx`. The n=1 exact DP is additionally checked against an independent brute-force path on all three hostile n=1 panels. Two complete workflow executions are byte-identical.

Terminal:

`QG19_ZERO_GAP_ON_FROZEN_PANEL__SHARPNESS_REMAINS_OPEN`.

The predeclared zero-gap branch maps to R1/M1. Both instruments therefore align on responsibility and move for this unit.

The scientific interpretation is deliberately limited: the 53 rows do not extend QG8's all-n cone. They show only that this newly frozen near-face panel did not expose a support-three requirement.

## 5. Q3-R2 / QG-20: agreement without diagnostic alignment

### 5.1 Frozen question

QG12 proves, under the equal-weight SixLCU objective `SELECT+PREP+WIDTH`, that the exact family equals the unary incumbent iff predicate P0 holds for every admitted instance/all n.

Q3-R2 changes only the structural objective:

`O20 = 2 SELECT + PREP + WIDTH`.

The unary incumbent remains cheaper than the binary incumbent for every admitted nonzero instance, so the comparison object remains well defined.

### 5.2 Frozen instruments

Before any QG20 analyzer/result exists, both lanes choose:

- diagnosis `S1_P0_BOUNDARY_OBJECTIVE_SCOPED`;
- move `N1_COMPLETE_REWEIGHTED_CENSUS`.

The reasoning is plausible: doubling SELECT changes the gain coefficients appearing in the original theorem's partition comparisons, so transferring P0 without retest would be unsafe.

The two instruments therefore agree on both responsibility and next move.

### 5.3 Complete independent scientific census

QG20 later recomputes the exact reweighted family over the same 203 set partitions with factorization enabled and shared width. The domain is complete for the registered low-order census:

- all `3^6 = 729` ordered n=1 instances;
- all `C(20,6) = 38,760` reorder-quotiented n=2 multisets;
- total `39,489` instances.

For every row, QG20 compares the **unchanged original P0 predicate** with whether the reweighted exact family equals the reweighted unary incumbent. Twenty-four deterministic rows are cross-checked through a second direct `member_components` implementation path.

Result:

- P0/label mismatches: **0**;
- n=1 P0 positives: 0; reweighted incumbent-exact positives: 0;
- n=2 P0 positives: 1; reweighted incumbent-exact positives: 1.

Two complete census executions are byte-identical.

Terminal:

`QG20_P0_ZERO_MISMATCH_ON_COMPLETE_N1_N2`.

### 5.4 Frozen-score consequence

The replacement protocol was explicit before outcome:

- mismatch -> strongest alignment with `S1_P0_BOUNDARY_OBJECTIVE_SCOPED`;
- zero mismatch -> finite-domain alignment with `S2_P0_STRUCTURALLY_INVARIANT_UNDER_SELECT_RESCALE`, while all-n invariance remains unproved;
- in both branches, running the complete census (`N1`) receives move credit.

Therefore the final Q3-R2 disposition is:

| Coordinate | Lane A | Lane B |
|---|---|---|
| inter-instrument responsibility relation | AGREE | AGREE |
| frozen diagnosis | S1 objective-scoped | S1 objective-scoped |
| responsibility alignment to deferred map | **false** | **false** |
| frozen primary move | N1 complete census | N1 complete census |
| move alignment | **true** | **true** |

This is the most important result in Q3. Agreement did not validate the diagnosis. At the same time, the instruments' shared decision to perform the discriminating census was productive: the experiment falsified their common expectation on the complete frozen n=1/n=2 domain.

We do not promote zero mismatches to an all-n weighted P0 theorem. The domain is exhaustive only for the stated n=1/n=2 construction and is highly label-imbalanced, with only one positive n=2 row.

## 6. Series synthesis

The complete valid series is intentionally shown row by row.

| Unit | Instrument responsibility relation | Instrument move relation | Lane-A responsibility alignment | Lane-B responsibility alignment | Lane-A move alignment | Lane-B move alignment |
|---|---|---|---:|---:|---:|---:|
| V0 | AGREE | AGREE | aligned | aligned | aligned | aligned |
| Q3-R1 / QG-19 | AGREE | AGREE | true | true | true | true |
| Q3-R2 / QG-20 | AGREE | AGREE | **false** | **false** | true | true |

We do **not** summarize this as “100% agreement,” “two-thirds diagnostic accuracy,” or “100% move accuracy.” With three live-programme questions, such rates invite a population interpretation that the design does not support. The table is the result.

Three observations survive.

First, heterogeneous execution paths can be frozen prospectively and compared without granting either path scientific authority.

Second, agreement is distinct from correctness. Q3-R2 is an explicit prospectively scored counterexample to using inter-instrument agreement as validation.

Third, a diagnosis can miss while the selected **discriminating experiment** remains good. This suggests a useful measurement separation between “what mechanism is responsible?” and “what next experiment will resolve the uncertainty?” The case series is too small to claim that move selection is systematically more robust than responsibility diagnosis; it only motivates that future hypothesis.

## 7. Contamination and failed prospective slots

The first planned expansion used QG-7d and QG-15c. Before their instrument outputs were frozen, public result-oriented successor branches became visible. We conservatively treated branch visibility itself as sufficient contamination risk and did not inspect result files for scoring.

Those candidate units were not deleted. Their audit terminals remain:

`Q3_INSTANCE_CONTAMINATED__OUTCOME_SURFACE_VISIBLE_BEFORE_INSTRUMENT_FREEZE`.

This creates a cost for the prospective standard: potentially interesting questions can become unusable. We consider that a feature of the measurement rather than a reason to backdate a freeze.

## 8. Known instrument defects D2/D3

The frozen harness has two known failure modes.

**D2.** A successful outer LLM capability envelope can contain semantically malformed/non-JSON content, producing an unstructured failure instead of a typed scientific disposition.

**D3.** Such a successful-malformed receipt can pin a deterministic request identity and prevent ordinary failed-retry semantics.

Q3 does not repair these between benchmark units. A repair would create an instrument-version confound unless the series were repeated prospectively. Instead, both are accepted fail-closed limitations: if triggered in an outcome-bearing Q3 unit, the lane/instance is instrument-invalid or `CANNOT_CHECK`, its bytes stay in history, and it is not repaired in place into a valid score.

Neither V0 nor Q3-R1/R2 triggered D2/D3.

## 9. Relation to current evaluation work

Q3 cedes broad scientific-agent benchmarking to ScienceAgentBench, AstaBench, SciAgentArena, HeurekaBench and related work. It cedes claim/evidence verification to ScientistOne and provenance/research-integrity systems. It cedes broad LLM-judge meta-evaluation to REFLECT and agreement-metric methodology to current judge-evaluation work.

Most importantly, ValueBlindBench already studies preregistered agreement gating before delayed ground truth. Q3 therefore makes no generic novelty claim for “agreement before outcomes.”

The candidate residual is narrower: a live research programme freezes a **tool-capable host diagnosis and a typed non-LLM controller decision on the same unresolved scientific frontier question before the successor scientific result exists**, preserves contamination/abstention, and later scores the frozen responsibility and move separately against independently generated science.

Even that sentence is a candidate novelty statement, not a proof of priority. The submission should avoid “first.”

## 10. Reproducibility and artifact custody

### V0

- `DUAL_HARNESS_LANE_A_RECEIPT.json`;
- `DUAL_HARNESS_LANE_B_RECEIPT.json`;
- `DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_RESULTS.json`;
- `MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json`;
- `MAX_R6Q_REGIME_PREDICATE_RESULTS.json`.

`replay_q3_v0.py` independently reconstructs the publication-level agreement and deferred alignment from these artifacts.

### Q3-R1

`instances/Q3-R1-QG19/` contains question freeze, shared packet, both lane receipts, pre-outcome agreement, experiment log, deferred outcome binding, final score and independent replay receipt. Scientific truth is in `QG19_OUTSIDE_CONE_SHARPNESS_RESULTS.json` and its analyzer/protocol.

### Q3-R2

`instances/Q3-R2-QG20/` contains the analogous chain. Scientific truth is in `QG20_SIXLCU_OBJECTIVE_SCOPE_RESULTS.json` and its analyzer/protocol.

The QG19/QG20 workflow executes each analyzer twice and requires byte-identical JSON/stdout. A separate completion workflow checks chronology, committed-result hashes, replay binding, scoring status, contaminated-slot retention and D2/D3 disposition.

The repository is publicly inspectable. Public visibility is not a reuse licence; a final archival DOI and explicit code/data licence should be inserted only after an actual authorized release.

## 11. Limitations

**Three valid units.** The study is a case series, not a reliability/calibration study. No kappa, confidence interval or population agreement rate is justified.

**Programme dependence.** All questions come from one exact-heavy quantum-compilation research programme. The benchmark does not establish transfer to empirical/noisy sciences.

**Shared upstream state.** The instruments are separately executed but share packet construction, ontologies and scientific history; correlated errors are expected and observed.

**Instrument-version heterogeneity.** V0 and the replacement units instantiate the same conceptual host-versus-typed-controller contrast but not one byte-identical controller/model implementation. The paper measures the protocol and case dispositions, not a fixed-model reliability parameter.

**Outcome asymmetry.** QG19 is a 53-row exact frozen panel, not a theorem. QG20 is complete for the registered n=1/n=2 domain but label-imbalanced and not an all-n theorem.

**Known D2/D3 defects.** Successful-but-semantically-malformed host receipts remain a structured-failure/recovery limitation.

**No scientific vote.** Agreement or disagreement between the instruments never changes the companion scientific result.

**Novelty is externally bounded.** Delayed-ground-truth agreement gating and judge validation already have strong prior art; Q3's residual is deliberately narrow.

## 12. Discussion

A useful scientific measurement need not make the evaluated system look consistently correct. Q3-R2 is more informative than a three-for-three success story would have been. Both instruments saw the same objective perturbation, both inferred that the old boundary was likely objective-scoped, and both chose the right way to test that belief. The complete low-order census then contradicted the frozen diagnosis.

This distinguishes two functions of a research-control instrument. A **responsibility diagnosis** proposes why the current frontier is unresolved. A **next-move decision** proposes which experiment will reduce that uncertainty. They can fail separately. In Q3-R2, the diagnosis missed under the frozen scoring map while the move generated decisive evidence.

The result also explains why agreement should be treated as a measurement coordinate rather than a gate that certifies truth. Two instruments can share an upstream representation and agree for the same mistaken reason. A later independent scientific result is necessary to distinguish corroboration from correlated error.

The contamination episodes add a second lesson. Prospective evaluation is a custody property, not a writing style. Once a target result surface becomes visible, a plausible narrative cannot restore blindness. Retiring the instance is scientifically cheaper than claiming prospectivity that no longer exists.

Future work should test the protocol on a substantially larger, predeclared question universe with stable instrument versions, genuine abstention events, noisy scientific outcomes and questions drawn from multiple domains. Only then would calibration or comparative reliability claims become meaningful.

## 13. Conclusion

We prospectively measured two heterogeneous research-decision instruments on three live scientific frontier questions and later bound their frozen judgments to independently generated outcomes. The instruments agreed on responsibility and primary move in all three cases, but one complete finite-domain experiment showed that **agreement did not imply a correct diagnosis**. The same case preserved a correct discriminating move, separating responsibility attribution from experiment selection.

The contribution is therefore not an agreement score or a claim that either instrument is reliable. It is a small, fail-closed case series showing how a research programme can preserve chronology, contamination, agreement, misdiagnosis, correct move selection and later scientific truth as different objects. That separation is the result Q3 is designed to measure.
