# ORION-RSE: Recursive Scientific Governance as a Falsifiable Decision Contract

**ORION-P14 · issue #669 · programme #670**  
**Evidence freeze:** 2026-08-21  
**Submission status:** peer-review package; controlled governance-contract superiority supported, real research-agent superiority open

## Abstract

Research agents can generate hypotheses, retrieve literature, design experiments and draft interpretations faster than they can reliably determine what those outputs scientifically warrant. We present **ORION-RSE**, a fail-closed recursive scientific-governance contract that separates research generation from claim promotion. ORION-RSE decomposes claims into falsifiable atoms, subtracts nearest-donor ownership before novelty promotion, freezes protected discriminators before outcomes, preserves null/negative/subsumed histories, distinguishes standalone from interaction-only evidence, records `CANNOT_CHECK`, separates evaluators from scientific authority, stops recursion when no material discriminator remains and reopens prior decisions only after material evidence or regime change. We evaluate the governance layer itself rather than claiming a new autonomous scientist. A first preregistered mixed-distribution benchmark is retained as **negative**: ORION-RSE made zero false promotions and retained 100% valid discoveries, but the strongest non-ORION comparator differed only on negative-history semantics, which occupied 1.8375% of the realized benchmark, so the registered ≥5% false-promotion and ≥8-point accuracy-separation gates could not pass. Root-cause analysis identified underweighted discriminator prevalence rather than a prediction disagreement. A fresh, independently frozen balanced-stratum successor then gives equal protected weight to clean support, legitimate reopening, retained negative history, donor subsumption, interaction-only evidence, `CANNOT_CHECK` and negative evidence. Across **6,720 protected cases**, full ORION-RSE achieves **0 false promotions, 1.000 disposition accuracy and 1.000 useful-discovery recall**. The strongest non-ORION comparator, an interaction-aware multi-review workflow, has **14.29% false promotions and 0.8571 disposition accuracy** while retaining full valid-discovery recall; its failure is specifically premature re-promotion of live negative history. Every registered ORION-RSE component ablation worsens protected decisions. The result supports a controlled superiority claim for the **governance contract**, not for autonomous research-agent performance. Blinded realistic research packets, matched frontier-agent baselines and longitudinal useful-discovery testing remain required for that broader claim.

## 1. Introduction

Scientific research is not equivalent to generating a plausible hypothesis or a positive result. A claim must be interpreted relative to prior work, the exact question frozen before observation, negative/null evidence, alternative explanations, resource constraints and the authority of the evaluator. Research agents amplify both opportunity and failure: they can produce more candidate studies, but they can also produce more false novelty, widened claims, post-hoc endpoints, forgotten negatives, donor duplication and confident closure when the evidence is non-identifying.

Autonomous and semi-autonomous systems already search literature, generate hypotheses, run code, design experiments and revise research artifacts. Recent work has moved toward goal-evolving scientific agents and direct evaluation of how research agents explore the scientific landscape. ORION-RSE does not claim that recursive research, reflection, debate, literature retrieval or multi-agent review are new.

Its question is narrower and experimentally sharper:

> **Can an explicit scientific-governance contract reduce false scientific promotion under matched information and decision resources without suppressing valid residual discoveries?**

ORION-RSE separates two responsibilities:

1. **candidate research generation** — propose claims, donors, experiments and interpretations;
2. **scientific governance** — decide what the evidence is authorized to establish, what is already donor-owned, what remains negative or non-identifiable, when recursion should stop and when prior decisions may reopen.

The candidate system cannot grant itself novelty or scientific authority merely because its own checks pass.

This paper contributes:

- a falsifiable governance lifecycle for research decisions;
- explicit scientific dispositions including `SUBSUMED`, `INTERACTION_ONLY`, `RETAIN_NEGATIVE` and `CANNOT_CHECK`;
- a matched-resource benchmark design that penalizes blanket abstention through useful-discovery recall;
- a preserved negative mixed-benchmark result and root-cause diagnosis;
- an independently frozen balanced-discriminator benchmark in which ORION-RSE strictly outperforms strong rule-based review baselines without losing valid discoveries.

## 2. Donor boundary and novelty

### 2.1 Research agents are prior-owned

Autonomous scientific agents already perform literature review, hypothesis generation, experiment design and iterative refinement. Goal-evolving systems such as SAGA explicitly pursue recursive scientific discovery. Work on research-agent exploration shows that agentic science should itself be evaluated for search behavior and concentration. The recent AI Scientist / co-scientist line likewise establishes that automated scientific workflows are a live systems area.

P14 therefore does not claim autonomous research or recursion as novelty.

### 2.2 Reflection, debate and review are prior-owned

Self-critique, reflection, researcher–reviewer separation, multi-agent debate and checklist/preregistration practices all provide prior art for adding review structure to generation. A paper that merely adds another critic agent would have little residual novelty.

### 2.3 Provenance, truth maintenance and authorization are prior-owned

Truth-maintenance systems preserve dependency-aware belief history; provenance systems bind claims to evidence; authorization systems separate capabilities from policy. ORION-RSE adopts these principles rather than renaming them.

### 2.4 Residual after subtraction

The live contribution is the **scientific-decision contract plus its evaluation**:

> Claim atomization, donor subtraction, protected freeze, explicit negative/subsumed history, non-identifiability, authority separation, recursion stops and material-change reopening are composed into a fail-closed research-governance lifecycle and evaluated on scientific disposition errors under matched information/decision budgets with useful-discovery noninferiority.

The object of study is not document quality or process verbosity. It is whether a system makes the correct **scientific promotion decision**.

## 3. ORION-RSE objects

### 3.1 Research atom

A research atom is a bounded claim/question carrying:

- parent claim identity;
- nearest donors/owners;
- protected discriminator;
- protocol/study identity;
- evidence receipts;
- resource envelope;
- evaluator identity;
- scientific authority owner;
- disposition;
- recursion stop/reopen conditions.

Atomization is an investigation unit, not automatic publication fragmentation.

### 3.2 Scientific dispositions

The contract distinguishes at least:

- `SUPPORTED_RESIDUAL` — positive bounded residual not fully donor-owned;
- `SUBSUMED` — positive observation but claimed novelty is already donor-owned;
- `INTERACTION_ONLY` — evidence supports only a joint interaction, not a standalone atom;
- `REDUNDANT_EQUIVALENT`;
- `OVERREACH_HARMFUL`;
- `NON_IDENTIFIABLE`;
- `CANNOT_CHECK`;
- negative/null terminal;
- `RETAIN_NEGATIVE` when new material does not justify reopening;
- reopen after a genuinely material evidence/regime change.

A positive observation is therefore neither necessary nor sufficient for positive scientific promotion.

### 3.3 Donor subtraction

Before novelty promotion, the system records the closest prior mechanisms and determines whether the candidate residual is adopted, adapted, composed, deferred or subsumed. This makes “positive result” and “novel contribution” separate coordinates.

### 3.4 Protected discriminator and protocol freeze

The claim is tested against an endpoint specified before protected outcomes. Material post-outcome changes require a new protocol identity. A negative result can motivate a new question, but cannot rewrite the old terminal.

### 3.5 Negative-history ledger

Null, negative, donor-subsumed and failed-preregistered outcomes remain first-class evidence. Reopening requires material new evidence or a changed regime, not a same-evidence reinterpretation.

### 3.6 Evaluator/authority separation

Candidate models, local tests and automated judges can evaluate evidence but do not automatically own scientific/novelty authority. The system records external ownership of the final promotion decision.

## 4. Lifecycle

The core lifecycle is

`question -> claim atoms -> donor subtraction -> protected discriminator -> protocol freeze -> execution/receipts -> scientific disposition -> recurse/stop -> later reopen if materially warranted`.

At every transition the system should be able to answer:

1. What changed?
2. What evidence supports the change?
3. Which prior work owns nearby territory?
4. What discriminator was frozen before outcomes?
5. What negative/subsumed evidence remains active?
6. What is the system *not* authorized to claim?

The lifecycle is fail-closed: `CANNOT_CHECK` is a legitimate scientific decision when evidence or authority is insufficient.

## 5. Benchmark design

P14 isolates governance from open-ended research generation. Every candidate policy receives the same synthetic research facts and the same fixed seven-check decision receipt. Protected gold is generated by an adjudication function that is not exposed as a terminal label.

Case facts cover:

- positive versus null observation;
- evidence integrity;
- whether the endpoint/protocol was frozen;
- identifiability;
- nearest-donor ownership;
- standalone versus interaction-only value;
- live negative/subsumed history;
- whether new evidence is materially independent/regime-changing.

### Compared policies

1. `RAW_POSITIVE` — promote any positive observation.
2. `REFLECTION_CHECKLIST` — additionally check evidence integrity, freeze and identifiability.
3. `DONOR_AWARE_REVIEW` — additionally subtract donor-owned positives.
4. `MULTI_REVIEW` — additionally detect interaction-only evidence.
5. `ORION_RSE_FULL` — additionally enforce negative-history/reopen semantics.
6. Component ablations: no donor subtraction, no freeze, no interaction handling, no negative history.

The strongest non-ORION baseline is selected by preregistered disposition accuracy rather than a post-hoc metric favorable to ORION.

Primary safety endpoint: **false scientific promotion**.  
Productivity constraint: **useful-discovery recall among gold `SUPPORTED_RESIDUAL` cases**.  
Secondary: full disposition accuracy and component-specific correctness.

This dual endpoint prevents an always-abstain policy from winning.

## 6. P14A: preserved negative mixed benchmark

P14A used 20 held-out families × 400 cases with independently varied fact rates. Full ORION-RSE produced:

- false promotion: **0.000000**;
- useful-discovery recall: **1.000000**;
- disposition accuracy: **1.000000**;
- history/reopen accuracy: **1.000000**.

However, the strongest comparator `MULTI_REVIEW` produced:

- false promotion: `0.018375`;
- useful-discovery recall: `1.000000`;
- disposition accuracy: `0.981625`;
- history/reopen accuracy: `0.505051`.

The protocol required strongest-baseline false promotion ≥0.05 and ORION accuracy advantage ≥0.08. Both gates failed. Terminal:

`P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET`.

The result is permanently negative.

### 6.1 Root cause

`MULTI_REVIEW` already checks evidence validity, protocol freeze, identifiability, donor ownership and interaction-only effects. The only remaining distinction from full ORION-RSE is whether a live negative/subsumed history may be re-promoted without material new evidence.

In the realized independent mixture, that effective discriminator occupied only **1.8375%** of all protected cases after upstream filters. Consequently, the maximum aggregate accuracy separation available against `MULTI_REVIEW` was itself 1.8375 percentage points. P14A was therefore underpowered **by discriminator prevalence**, even though the systems made different decisions on nearly half of the relevant history cases.

The failure does not authorize changing P14A's ≥5% or ≥8-point thresholds. Instead it motivates a distinct benchmark question: when each scientific governance discriminator receives explicit protected weight, does the full contract outperform its nearest alternatives?

## 7. P14B: independently frozen balanced-discriminator benchmark

P14B was frozen after P14A's negative was committed. Fresh seed: `2026082115`. It contains **12 held-out families**, each with **80 cases in seven prospectively balanced strata**, for **6,720 cases** total:

1. `SUPPORTED_CLEAN`;
2. `SUPPORTED_REOPEN` — live negative history plus genuinely material new evidence;
3. `RETAIN_NEGATIVE` — same-evidence rereading of live negative history;
4. `SUBSUMED`;
5. `INTERACTION_ONLY`;
6. `CANNOT_CHECK` — one validity/freeze/identifiability defect;
7. `NEGATIVE`.

Case order and nuisance details are reminted within each family. All policies receive identical records and the same seven-check decision budget.

## 8. P14B results

Terminal:

`P14B_BALANCED_GOVERNANCE_SUPERIORITY_SUPPORTED`.

| policy | false promotion | disposition accuracy | useful-discovery recall |
|---|---:|---:|---:|
| **ORION_RSE_FULL** | **0.0000** | **1.0000** | **1.0000** |
| `MULTI_REVIEW` | 0.142857 | 0.857143 | 1.0000 |
| `DONOR_AWARE_REVIEW` | 0.285714 | 0.714286 | 1.0000 |
| `REFLECTION_CHECKLIST` | 0.428571 | 0.571429 | 1.0000 |
| `RAW_POSITIVE` | 0.571429 | 0.428571 | 1.0000 |

The strongest non-ORION comparator is `MULTI_REVIEW`. ORION-RSE therefore improves disposition accuracy by **+0.142857** while reducing false promotion by **14.2857 percentage points**, with **no loss in useful-discovery recall**.

The difference is scientifically interpretable. `MULTI_REVIEW` handles legitimate material reopening correctly but re-promotes all protected `RETAIN_NEGATIVE` cases; full ORION-RSE distinguishes the two. Its retained-negative accuracy is 1.0 versus 0 for the strongest comparator, while supported-reopen accuracy remains 1.0 for both.

Every registered component ablation lowers disposition accuracy. Full ORION-RSE uses the same seven-check decision receipt as every comparator. Two executions are byte-identical with SHA-256:

`784d57e694b9a96828e72bc5e80dfc9e533cf738b568e45a71ce9fd08d679e66`.

## 9. What the controlled superiority result means

P14B does **not** show that ORION-RSE is a better scientist than a frontier research agent. It shows something more primitive and directly falsifiable:

> Given the same research facts and the same decision-check budget, a governance contract that includes donor subtraction, protected freeze, interaction semantics and negative-history/reopen rules makes strictly fewer scientific disposition errors than strong partial-review contracts while preserving every valid positive promotion in the protected benchmark.

This is the causal substrate that a real-agent evaluation can build on. Without it, any open-ended “research agent superiority” result would be hard to attribute to governance rather than model quality, retrieval, extra compute or judge preference.

## 10. Required real-agent evaluation

The broad paper programme requires three additional tiers before claiming superiority over research agents.

### Tier A — fresh hidden-gold decision worlds

P14B supplies a controlled version; future cases should add more semantic diversity, indirect donor conflicts and resource/tool failures without leaking ORION labels.

### Tier B — blinded realistic research packets

Prospectively assemble research packets across multiple domains, e.g. ML experiments, formal/software verification and computational science. Candidate systems receive identical literature/source packets, tools and model budgets. Independent blinded reviewers adjudicate the maximum scientifically admissible claim, donor overlap, negative-evidence handling, `CANNOT_CHECK` and useful discoveries.

Required comparators include a strong raw research agent, reflection/self-critique, researcher–reviewer multi-agent workflow, literature-RAG + experiment planning, preregistration/checklist control and ORION component ablations.

### Tier C — longitudinal research

Round 1 creates positive, null, negative and subsumed history. Round 2 changes evidence, donor set or regime. The evaluation must distinguish two symmetric errors:

- **forgetting** old negative/subsumed evidence and repeating false work;
- **over-transfer** of an old negative after a genuine material regime change.

Useful-discovery noninferiority remains co-primary so safety cannot be purchased through blanket abstention.

## 11. Resource accounting and authority

Every candidate workflow must report model/checkpoint, input evidence, web/literature access, tool access, generation tokens, search/experiment budget, reviewer/evaluator calls, number of research/reflection passes and end-to-end latency. ORION-RSE cannot hide extra compute as “governance.”

Final scientific authority must remain external to the candidate research system. Exact synthetic gold or blinded independent review can own evaluation; a candidate model cannot certify its own novelty merely by invoking the ORION vocabulary.

## 12. Relation to current research-agent work

Goal-evolving and autonomous scientific systems demonstrate that agents can recursively generate and refine research. Recent work also reports that AI research agents may narrow scientific exploration, making evaluation of research *behavior* and not only output quality increasingly important. ORION-RSE attacks a complementary problem: **scientific admissibility governance**.

Its novelty is not another research-agent architecture. It is the explicit separation of generation from promotion and the preservation of negative/donor-subsumed history as active constraints on future decisions. That distinction is empirically necessary in P14B: the strongest interaction-aware review baseline still fails the retained-negative discriminator while preserving valid reopening.

## 13. Limitations

1. P14B is a symbolic/controlled decision benchmark, not natural-language open-ended research.
2. The full contract implements the same adjudication concepts used to construct protected gold; realistic evaluation must prevent vocabulary or rule leakage.
3. Balanced strata are appropriate for testing component discrimination but do not estimate natural real-world prevalence. P14A is retained to show why prevalence and discriminability must be reported separately.
4. Seven-check costs are matched by construction; real workflows have heterogeneous token, retrieval, experiment and reviewer costs.
5. Human or independent model adjudicators may disagree on real novelty and scientific admissibility.
6. Longitudinal value of negative-history retention is not yet demonstrated on realistic scientific work.
7. ORION-RSE may reduce productive risk-taking if its reopen/materiality criteria are poorly calibrated; useful-discovery noninferiority is therefore mandatory in real evaluation.
8. No claim of autonomous-scientist superiority is authorized by the current controlled result.

## 14. Conclusion

ORION-RSE treats research governance as a decision system that can itself be falsified. The paper does not ask whether an agent can produce more research text; it asks whether a governance contract prevents scientifically invalid promotion without suppressing valid discoveries. A first mixed benchmark is preserved as negative because its decisive history discriminator was too rare for the registered aggregate gates. A separately frozen balanced benchmark then shows exact controlled superiority: zero false promotions and perfect valid-discovery recall versus a 14.29% false-promotion rate for the strongest partial-review comparator. The result identifies the key residual mechanism—**negative-history and material-reopen governance on top of validity, donor and interaction checks**—and establishes a concrete contract for the next step: matched, blinded evaluation against real research-agent workflows.

## References

- Du, Y. et al. *Accelerating Scientific Discovery with Autonomous Goal-evolving Agents (SAGA).* arXiv:2512.21782, 2025/2026 versions.
- Tang, Y. & Yang, Y. *AI Research Agents Narrow Scientific Exploration.* arXiv:2605.27905, 2026.
- Recent AI Scientist / AI co-scientist systems establish autonomous scientific workflow generation as a donor-owned research direction; final typesetting should normalize the exact primary publication records used by the target venue.
- Doyle, J. *A Truth Maintenance System.* Artificial Intelligence 12(3):231–272, 1979.
- de Kleer, J. *An Assumption-Based TMS.* Artificial Intelligence 28(2):127–162, 1986.
