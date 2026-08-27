# ORION-RSE: Recursive Scientific Governance as a Falsifiable Decision Contract

**ORION-24 · issue #669 · programme #670**  
**Evidence freeze:** 2026-08-21  
**Submission status:** peer-review package; controlled governance-conformance superiority supported, external research-agent validation open

## Abstract

Research agents can generate hypotheses, retrieve literature, design experiments and draft interpretations faster than they can reliably determine what those outputs scientifically warrant. We present **ORION-RSE**, a fail-closed recursive scientific-governance contract that separates research generation from claim promotion. ORION-RSE atomizes claims, subtracts nearest-donor ownership before novelty promotion, freezes protected discriminators before outcomes, retains null/negative/subsumed history, distinguishes standalone from interaction-only evidence, records `CANNOT_CHECK`, separates evaluator identity from scientific authority, stops recursion when no material discriminator remains and reopens prior decisions only after material evidence or regime change. We evaluate this governance layer rather than claiming a new autonomous scientist. A first preregistered mixed benchmark is retained as **negative**: full ORION-RSE made zero false promotions and retained every valid discovery, but the only residual discriminator against the strongest comparator occupied 1.8375% of the realized cases, so registered aggregate separation gates could not pass. We then show that this negative is uninformative about the contract rather than evidence against it: both failing gates read one quantity whose supremum over the protocol's own declared sampling support is 0.042326, below both the 0.05 and the 0.08 bar, so the seven-gate conjunction had a single reachable value before the seed was drawn. The terminal is retained verbatim and reclassified `CANNOT_CHECK`. A fresh balanced benchmark gives equal protected weight to seven scientific dispositions and yields 0 false promotions, 1.000 disposition accuracy and 1.000 useful-discovery recall for the full contract versus 14.29% false promotion and 0.8571 accuracy for the strongest interaction-aware multi-review baseline. That benchmark originally implemented the full policy through the same adjudication function used for gold, so we treat it as an internal semantic-discriminator result rather than independent validation. We therefore preregister a third **specification-separated** successor: 28 explicit gold cases are frozen in a separate adjudication artifact, the policy receives facts only, and the full implementation is independently coded. Full ORION-RSE is 28/28 correct with zero false promotions and full valid-discovery recall; `MULTI_REVIEW` is 24/28 with 14.29% false promotion, all six component ablations are worse, and two evaluations yield identical canonical SHA-256 `74032348…f01a63`. That benchmark's terminal is attainable in both directions — of the seven implementations its protocol admits in the graded slot, exactly one clears every gate — and the first benchmark's 0.05 and 0.08 bars, registered unchanged, are both met here at 0.142857. The resulting claim is strong but precise: **against the registered governance specification, the complete contract conforms strictly better than partial review contracts without suppressing valid promotion.** Whether the specification itself improves open-ended real science remains an external blinded-adjudication question.

## 1. Introduction

Scientific research is not equivalent to producing a plausible hypothesis or a positive result. A claim must be interpreted relative to prior work, the question frozen before observation, negative/null evidence, competing explanations, resource constraints and the authority of the evaluator. Research agents amplify both opportunity and failure: they can produce more candidate studies, but also more false novelty, widened claims, post-hoc endpoints, forgotten negatives, donor duplication and confident closure when evidence is non-identifying.

Autonomous and semi-autonomous systems already search literature, generate hypotheses, run code, design experiments and revise research artifacts. Goal-evolving scientific agents make recursive discovery an explicit system objective. Recent work also asks how research agents change the breadth of scientific exploration. ORION-RSE therefore does not claim autonomous research, recursion, reflection, debate or retrieval as new primitives.

Its question is narrower and more falsifiable:

> **Can an explicit scientific-governance contract make better claim-promotion decisions than strong partial review contracts under matched information and decision resources, while preserving valid discoveries?**

ORION-RSE separates candidate generation from scientific promotion. The candidate system may propose claims and evidence; it cannot grant itself novelty or scientific authority merely because its own checks pass.

The paper contributes:

1. a bounded research-governance lifecycle;
2. explicit dispositions including `SUBSUMED`, `INTERACTION_ONLY`, `RETAIN_NEGATIVE` and `CANNOT_CHECK`;
3. a matched-resource evaluation with useful-discovery recall so blanket abstention cannot win;
4. a preserved negative mixed benchmark, its root-cause diagnosis, and a mechanical determination that its two failing gates were unattainable under its own frozen sampling support;
5. a balanced semantic-discriminator benchmark;
6. a specification-separated successor that removes direct gold-function reuse and tests every core component through ablation.

## 2. Donor boundary and novelty

Autonomous/goal-evolving research agents own recursive hypothesis, literature and experiment generation. Reflection, self-critique, reviewer agents and multi-agent debate own iterative review as a primitive. Preregistration/checklists own prospective endpoint discipline. Truth-maintenance systems own dependency-aware belief history; provenance owns evidence lineage; authorization systems own separation of actor permission from operation.

ORION-RSE adopts these ideas. The live residual is the **scientific promotion contract plus its evaluation**:

> Claim atomization, donor subtraction, protected freeze, negative/subsumed history, interaction/non-identifiability dispositions, authority separation, recursion stops and material-change reopening are composed into one fail-closed decision lifecycle and compared with partial governance contracts on false-promotion, disposition and useful-discovery endpoints.

The object of study is the promotion decision, not document quality or process verbosity.

## 3. ORION-RSE contract

### 3.1 Research atom

A research atom carries a bounded claim/question, parent identity, nearest donors, protected discriminator, protocol identity, evidence/resource receipts, evaluator identity, authority owner, disposition and stop/reopen conditions. Atomization is an investigation unit, not automatic publication fragmentation.

### 3.2 Dispositions

The contract distinguishes:

- `SUPPORTED_RESIDUAL` — bounded positive residual not fully donor-owned;
- `SUBSUMED` — the apparent residual is donor-owned;
- `INTERACTION_ONLY` — evidence supports only a joint effect, not a standalone atom;
- `REDUNDANT_EQUIVALENT`;
- `OVERREACH_HARMFUL`;
- `NON_IDENTIFIABLE`;
- `CANNOT_CHECK`;
- negative/null outcomes;
- `RETAIN_NEGATIVE` when new material does not justify reopening.

A positive observation is therefore not identical to positive scientific promotion.

### 3.3 Donor subtraction

Before novelty promotion, the nearest prior mechanisms are recorded and the candidate residual is classified as adopted, adapted, composed, deferred or subsumed. “Positive evidence” and “novel contribution” are separate coordinates.

### 3.4 Protected freeze

The discriminator and terminal rules are specified before protected outcomes. A material post-outcome change requires a new protocol identity. A negative result may motivate a successor but cannot be rewritten.

### 3.5 Negative-history ledger and reopening

Null, negative and donor-subsumed outcomes remain active evidence. Reopening requires material new evidence or a changed regime, not a same-evidence reinterpretation.

### 3.6 Authority separation

Candidate models, tests and automated judges may evaluate evidence, but they do not automatically own scientific/novelty authority. Synthetic gold or blinded external adjudication owns the benchmark label; real publication claims remain externally governed.

## 4. Lifecycle

The core lifecycle is:

`question -> atoms -> donor subtraction -> protected discriminator -> protocol freeze -> execution/receipts -> disposition -> recurse/stop -> later reopen if materially warranted`.

At each transition the system records what changed, what evidence supports it, which donor owns nearby territory, what was frozen before outcome, what negative/subsumed history remains active and what is not authorized.

`CANNOT_CHECK` is a valid scientific disposition when evidence or authority is insufficient.

## 5. Evaluation contract

All compared policies receive identical case facts and identical fixed decision-check budgets. Candidate facts include positive/null observation, evidence integrity, protocol freeze, identifiability, donor ownership, interaction-only status, live negative history and material new evidence.

Registered policies:

1. `RAW_POSITIVE` — promote any positive observation;
2. `REFLECTION_CHECKLIST` — add evidence/freeze/identifiability checks;
3. `DONOR_AWARE_REVIEW` — add donor subtraction;
4. `MULTI_REVIEW` — add interaction-only handling;
5. `ORION_RSE_FULL` — add negative-history/material-reopen semantics;
6. component ablations.

Primary safety endpoint: false scientific promotion. Productivity endpoint: useful-discovery recall among gold `SUPPORTED_RESIDUAL` cases. Secondary: full disposition accuracy and component-specific correctness. This prevents an always-abstain system from winning.

## 6. P14A — preserved negative mixed benchmark

P14A used 20 held-out families × 400 cases with independently varied fact rates. Full ORION-RSE produced:

- false promotion `0.000000`;
- useful-discovery recall `1.000000`;
- disposition accuracy `1.000000`;
- history/reopen accuracy `1.000000`.

The strongest comparator, `MULTI_REVIEW`, produced:

- false promotion `0.018375`;
- useful-discovery recall `1.000000`;
- disposition accuracy `0.981625`;
- history/reopen accuracy `0.505051`.

The protocol required strongest-baseline false promotion ≥0.05 and accuracy separation ≥0.08. Both gates failed. Terminal:

`P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET`.

This terminal is permanent.

### 6.1 Root cause

After validity, freeze, identifiability, donor and interaction checks, the only difference between `MULTI_REVIEW` and full ORION-RSE is live negative history without material new evidence. In the realized random mixture, that effective discriminator occupied only **1.8375%** of all cases. The maximum possible aggregate accuracy gap was therefore also 1.8375 points.

The result identifies a benchmark-design problem: natural/random mixtures may underweight the decision boundary being tested. P14A is not retuned; it motivates a new balanced question.

### 6.2 What the negative established, and what it did not

The statement above is about the draw that happened. The stronger and more damaging statement is about every draw the protocol admits, and we make it here rather than leave the terminal to be read as a comparative finding.

Both failing gates read one quantity. `MULTI_REVIEW` reproduces the gold adjudication except where a positive is a same-evidence rereading of a live negative history; over the 144 fact states the generator can emit, that exception is a single state, and it is also `MULTI_REVIEW`'s only false promotion. So `strongest_baseline_false_promotion_ge_0_05` reads its frequency and `accuracy_gain_ge_0_08` reads `1 − (1 − that frequency)` — the same number, which is why the receipt prints `0.018375` for both.

The eight case facts are independent Bernoulli draws whose rates are each monotone in a different declared uniform, and each family's draw is mixed half-and-half with a fixed base. The state's prevalence is therefore a product whose extrema over the declared box sit at corners, and the box's **supremum is 0.042326** — below both the 0.05 and the 0.08 bar. Exercised over five registered admissible worlds spanning the declared ranges, ending at the extremal corner, the best reachable value is 0.040250, giving attainment margins of **−0.009750** and **−0.039750**, and no world satisfies either gate. The remaining five gates are satisfied by every admissible world, three of them because the graded `ORION_RSE_FULL` arm is the gold function it is scored against (0 divergent points of 256). The seven-gate conjunction therefore had **one reachable value** before the seed was drawn.

The instrument was not incapable in general. Re-opening the declared sampling ranges and nothing else — same seed, same nine arms, same seven thresholds, same terminal expression — moves the terminal to the positive branch in three of three registered capability worlds, with two distinct terminals observed and no inert case. The pass region is live; it lies outside the set of runs the preregistration admits.

P14A's terminal, seed, thresholds and receipt are retained verbatim and nothing is relabelled positive. Its **evidential disposition is `CANNOT_CHECK`**: the gates recorded a measurement the frozen protocol could not take, not evidence against the governance contract. The adjudication is `P14_GATE_ATTAINABILITY_ADJUDICATION_V1.json`, produced by `verify_p14_gate_attainability_v1.py` over instruments that reload the shipped generator and reproduce its committed `full_result_sha256` before any verdict is read.

The general lesson we take from it is that a threshold is a claim about a distribution: freeze the threshold and the support of the statistic it reads together, or an outcome has been frozen rather than a test.

## 7. P14B — balanced semantic discriminator

P14B uses a fresh seed and 12 held-out families with seven equal strata: clean support, legitimate material reopening, retained negative history, donor subsumption, interaction-only evidence, `CANNOT_CHECK` and negative evidence. There are 6,720 protected cases total, with the same seven-check decision receipt for every arm.

Full ORION-RSE yields:

- false promotion **0**;
- disposition accuracy **1.0000**;
- useful-discovery recall **1.0000**.

Strongest non-ORION `MULTI_REVIEW` yields:

- false promotion **0.142857**;
- disposition accuracy **0.857143**;
- useful-discovery recall **1.0000**.

Both systems correctly allow genuinely material reopening; only full ORION-RSE retains negative history when no material new evidence exists. Every registered component ablation is worse. Two runs match SHA-256 `784d57e694b9a96828e72bc5e80dfc9e533cf738b568e45a71ce9fd08d679e66`.

### 7.1 Circularity disposition

The original P14B harness defines `ORION_RSE_FULL` by directly invoking the same decision function used as protected gold. Therefore P14B demonstrates that the chosen semantics distinguish full from partial contracts, but it is too circular to serve as implementation-independent evidence of conformance. We preserve the result and lower its evidentiary role rather than hiding the objection.

## 8. P14C — specification-separated conformance benchmark

P14C is the paper's **sole central empirical authority**. That is a deliberate
narrowing, not a summary of everything run. P14A is a measurement whose gates
were unreachable under its frozen support, so it licenses no comparative reading
in either direction, and P14B is retained as diagnostic because it reused gold it
had a hand in producing. Neither carries the empirical claim; P14C does, and the
active authority record binds its terminal
(`P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED`) to the result
receipt rather than to either predecessor.

P14C was frozen after the circularity issue was identified. It does not alter
P14A or P14B.

### 8.1 Independent artifacts

- `P14C_ADJUDICATION_CASES_V1.json` contains **28 explicit frozen cases** and expected dispositions: four variants for each of the seven semantic strata.
- `run_p14c_specification_separated_governance_v1.py` implements every policy independently from the case table.
- Before a policy call, the harness strips `gold_disposition`, `rationale`, `case_id` and `stratum`; the policy receives only factual booleans.
- Precedence variants test donor-over-interaction/history, interaction-over-history, validity failure and negative evidence.
- Six ablations separately remove evidence-integrity, freeze, identifiability, donor, interaction and negative-history checks.

The inference unit is the stratum, not the case. The 28 cases are four
precedence variants of each of seven semantic strata, so they are not 28
independent draws and no interval is computed as if they were. Accuracy over
them is a conformance count against a frozen specification: it says a policy
handled every registered variant, not that it would handle a sampled population
at that rate.

The explicit case specification is internal to the programme, not a human external-adjudication dataset. P14C therefore evaluates **conformance to a separately frozen specification**, not truth about open-ended science.

### 8.2 Results

Terminal:

`P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED`.

| policy | disposition accuracy | false promotion | useful-discovery recall |
|---|---:|---:|---:|
| **ORION_RSE_FULL** | **1.0000** | **0.0000** | **1.0000** |
| `MULTI_REVIEW` | 0.857143 | 0.142857 | 1.0000 |
| `DONOR_AWARE_REVIEW` | 0.714286 | 0.285714 | 1.0000 |
| `REFLECTION_CHECKLIST` | 0.571429 | 0.428571 | 1.0000 |
| `RAW_POSITIVE` | 0.428571 | 0.535714 | 1.0000 |

Full ORION-RSE correctly handles all retained-negative and supported-reopen cases. All six component ablations lower disposition accuracy. The gold field is absent from every policy input. Two independent evaluations generate identical canonical SHA-256:

`74032348de7e6508b6c1827aabcf1bf9d354d30b9c6f81c8259fdb3535f01a63`.

### 8.3 Gate attainability, and P14A's thresholds read here

P14C's terminal is asked the question §6.2 asks of P14A's, over the coordinate P14C leaves free. P14A sampled the discriminator's prevalence; P14C fixes it by composition — four cases per semantic stratum makes the `RETAIN_NEGATIVE` share exactly `4/28 = 0.142857` in every admissible table, against P14A's ceiling of `0.042326` for the same quantity. What remains free is the implementation in the graded slot, and the protocol registers seven of them: the full contract and its six single-component ablations.

Over that register the full contract clears all eight gates and every ablation fails at least one, so the conjunction prints **two** distinct terminals rather than one. `accuracy_advantage_ge_0_10` is refutable: it fails for the donor, interaction and negative-history ablations. `strongest_baseline_false_promotion_ge_0_10` is a benchmark-difficulty precondition and holds in every admissible table by construction, which is the property P14A's corresponding gate lacked — there, the same certificate was unsatisfiable.

P14A's two frozen bars are then registered verbatim and read on this benchmark:

| P14A gate, threshold unchanged | reachable interval here | realized | verdict |
|---|---|---|---|
| `strongest_baseline_false_promotion_ge_0_05` | [0.142857, 0.142857] over admissible tables | 0.142857 | **met** |
| `accuracy_gain_ge_0_08` | [0.000000, 0.142857] over admissible subjects | 0.142857 | **met** |

The 0.08 bar sits strictly inside its interval, so it could have gone either way and did not have to pass. The question P14A's gates encoded is therefore answered affirmatively at P14A's own thresholds, under P14C's protocol identity, with no threshold, seed, case or result of P14A edited. P14A's terminal stands; it is classified, not overturned.

One honest residual: `full_discovery_recall_one` is satisfied by all seven registered subjects, because an ablation removes a check and a policy reading fewer facts promotes more rather than fewer. No registered implementation abstains, so that gate carries no refutation capacity over this register and its pass is not evidence that the contract preserves valid discovery. It is named as such in the adjudication receipt.

### 8.4 Strongest current claim

P14C closes the direct implementation-circularity objection. The strongest evidence-backed statement is:

> **Against an explicit adjudication specification frozen separately from the policy implementation, the full ORION-RSE decision contract conforms to every registered governance case and strictly outperforms the registered partial-governance implementations without reducing valid promotion.**

This is stronger than a self-call conformance test and weaker than external scientific validity. The distinction is essential.

## 9. Required external validation

A broad claim that ORION-RSE improves real research requires new evidence.

### Tier A — blinded realistic research packets

Prospectively assemble packets across multiple domains, e.g. ML experiments, formal/software verification and computational science. Candidate workflows receive identical literature/source packets, tools and model budgets. Independent blinded adjudicators determine the maximum admissible claim, donor overlap, negative-evidence handling, `CANNOT_CHECK` and valid discoveries.

Comparators should include a strong research agent, reflection/self-critique, researcher–reviewer multi-agent workflow, literature-RAG + experiment planning, preregistration/checklist control and ORION component ablations.

### Tier B — longitudinal history

Round 1 creates positive, null, negative and subsumed history. Round 2 changes evidence, donor set or regime. Evaluation must catch both forgetting old negatives and over-transferring old negatives after genuine material change.

Useful-discovery noninferiority remains co-primary so safety cannot be purchased by blanket abstention.

### P14D — frozen acquisition contract; preflight blocked

The Tier-A path is operationalized by the frozen fail-closed acquisition
contract `P14D_BLINDED_EXTERNAL_VALIDATION_ACQUISITION_PROTOCOL_V1.md` (bound in
`P14_ACTIVE_CLAIM_AUTHORITY_V1.json` under `prospective_external_validation`).
Its intake validator rejects missing packets, self-authored custody, unblinded
labels, unequal resources and stale digests; until every required artifact
passes, the only admissible terminal is `P14D_EXTERNAL_ACQUISITION_BLOCKED`.
The committed preflight `P14D_EXTERNAL_ACQUISITION_PREFLIGHT_V1.json` records
`execution_authorized=false` with all eight required artifacts absent
(packet register, common-resource manifest, blinded assignment manifest,
external-adjudicator custody attestation, frozen adjudication rubric,
independent adjudications, protected-output register, replay receipt) and no
trusted external custody verifier configured, so no external-validation
authority exists. The active bounded result remains P14C
(`P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED`).

### Scope binding — consolidated lifecycle-contract safety

Under issue #1086 decision D7 (portfolio disposition
`papers/ISSUE_1086_PORTFOLIO_DISPOSITION_V1.json`, binding artifact
`papers/orion-23-responsibility-carrying-state/P13_P14_CONSOLIDATION_SCOPE_BINDING_V1.json`),
ORION-24 is consolidated with ORION-23 into one machine-verifiable lifecycle-contract
safety scope. What this manuscript supports is the machine-verifiable layer:
specification-separated policy conformance, fail-closed acquisition
preflights, and the registered governance cases. Broader correct-governance or
social-responsibility claims — that the governance policy is the *correct* one
for real organizations — remain **CANNOT_CHECK**: they require two independent
experts plus a tie-break/custodian, which no artifact in this repository
provides. On the present evidence ORION-24 is **not** a separate paper at the 75+
bar; the external campaign that could change this (30–50 pinned repositories
from at least five unrelated organizations) is OPEN and must derive gold only
from the objective facts enumerated in
`papers/orion-23-responsibility-carrying-state/P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md`
(object/hash existence, ancestry, tag/signature, test exit, timestamp order)
and must never use ORION itself as an external subject.

## 10. Resource accounting

Every workflow should report model/checkpoint, evidence access, web/literature access, tool access, generated tokens, experiment/search budget, reviewer/evaluator calls, number of research/reflection passes and end-to-end latency. ORION-RSE cannot hide extra compute as “governance.”

Final scientific authority remains external to candidate workflows.

## 11. Relation to current research-agent work

Goal-evolving and autonomous scientific systems establish open-ended generation as a donor-owned direction. Research on scientific-exploration behavior shows that evaluation should consider what agents choose to explore, not only whether they can produce plausible papers. ORION-RSE studies a complementary layer: **scientific admissibility governance**.

Its distinctive mechanism is active negative/subsumed history plus material-reopen semantics on top of validity, donor and interaction checks. That is exactly where the strongest partial comparator fails in both P14B and the specification-separated P14C cases.

## 12. Limitations

1. P14A–C are controlled symbolic decision benchmarks, not natural-language open-ended science.
2. P14C removes direct gold-function reuse but the adjudication specification is still internally authored; external validity remains open.
3. Balanced strata test discrimination, not real-world prevalence; P14A shows why prevalence and discriminability must be reported separately, and why a threshold must be frozen together with the support of the statistic it reads.
4. One P14C gate, `full_discovery_recall_one`, is satisfied by every implementation the protocol registers in the graded slot, so its pass is a property of the ablation register rather than evidence about the contract.
4. Decision costs are matched abstractly; real workflows have heterogeneous token, retrieval, experiment and reviewer costs.
5. Human or independent-model adjudicators may disagree on novelty and admissibility.
6. Longitudinal value of negative-history retention is not yet demonstrated on realistic scientific work.
7. Poorly calibrated reopen/materiality criteria could suppress productive risk-taking; useful-discovery noninferiority is therefore mandatory.
8. No claim of frontier autonomous-research superiority is authorized.
9. The P14D external-acquisition preflight is blocked (all eight required artifacts absent, no trusted external custody verifier), so no external-validation authority exists; and under issue #1086 decision D7 the paper's supported scope is narrowed to machine-verifiable lifecycle contracts — broader correct-governance and social-responsibility claims are CANNOT_CHECK (two independent experts plus tie-break/custodian required), and ORION-24 is not a separate 75+ paper on the present evidence.

## 13. Conclusion

ORION-RSE treats scientific governance as a decision system that can itself fail. The paper preserves two important boundaries: P14A's aggregate gates were unreachable under its own frozen sampling support, so its terminal is a measurement that could not be taken rather than a comparative negative, and P14B is semantically informative but directly reuses its adjudication function for the full policy. P14C then removes that implementation circularity with a separately frozen case specification and independent policy implementation. The complete contract conforms to all registered cases, makes zero false promotions and preserves every valid promotion, while the strongest partial review contract fails the retained-negative boundary. The next claim frontier is external rather than synthetic: **blinded realistic packets, independent adjudication and longitudinal research history under matched resources.**

## References

- Du, Y. et al. *Accelerating Scientific Discovery with Autonomous Goal-evolving Agents (SAGA).* arXiv:2512.21782.
- Tang, Y. & Yang, Y. *AI Research Agents Narrow Scientific Exploration.* arXiv:2605.27905, 2026.
- Autonomous AI Scientist / AI co-scientist systems are donor-owned background for scientific-workflow generation; final venue preparation should normalize exact primary publication metadata.
- Doyle, J. *A Truth Maintenance System.* Artificial Intelligence 12(3):231–272, 1979.
- de Kleer, J. *An Assumption-Based TMS.* Artificial Intelligence 28(2):127–162, 1986.
