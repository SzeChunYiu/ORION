# ORION-RSE: Auditable Recursive Governance for Scientific Research Decisions

**ORION publication candidate P14**  
**Issue:** #669 · parent programme #670  
**Manuscript status:** complete methods/protocol draft; comparative benchmark terminal not yet earned  
**Evidence date:** 2026-08-20

## Abstract

Research agents can generate hypotheses, literature maps, experiments and plausible interpretations faster than they can reliably determine what those outputs scientifically warrant. We present ORION-RSE, a fail-closed research-governance architecture that treats claim promotion as a separate responsibility from research generation. ORION-RSE decomposes claims into falsifiable research atoms, subtracts nearest-work/donor ownership before novelty promotion, freezes protected discriminators and protocols, preserves positive, null, negative, donor-subsumed, interaction-only and non-identifiable outcomes, separates evaluator from scientific authority, stops recursion when no material discriminator remains, and reopens prior decisions when evidence or regime changes. Existing ORION implementation provides a verified substrate for these operations and preserves concrete histories in which an apparent positive was later donor-subsumed and a preregistered near-miss remained negative. These examples motivate the method but do not establish superiority. The paper therefore prospectively specifies a three-tier evaluation: fresh hidden-gold research-decision worlds, blinded realistic research packets across multiple domains, and longitudinal linked rounds testing whether retained negative/subsumed history improves later decisions. ORION-RSE is compared with a raw research agent, reflection/self-critique, multi-agent researcher–reviewer workflows, literature-RAG/experiment planning, preregistration/checklist control and component ablations under matched model, tool and resource budgets. The primary safety endpoint is false scientific promotion/overbroad-claim rate, constrained by prospectively frozen noninferiority on independently accepted useful discovery so blanket abstention cannot win. No protected P14 comparative result exists yet. Accordingly, this manuscript claims an auditable research-machine method and a frozen evaluation contract, not autonomous-scientist superiority.

## 1. Introduction

Scientific research requires more than generating an interesting result. A result must be interpreted relative to prior work, the frozen experimental question, negative and null evidence, alternative explanations, resource limits and the exact authority of the evaluator. Research agents complicate this process because they can produce many plausible claims and experiments quickly. Increased throughput can amplify familiar scientific failure modes: false novelty, claim widening, endpoint drift, donor omission, selective retention of positives, interaction misattribution, stale evidence reuse and confident closure when the evidence cannot decide.

Contemporary autonomous and semi-autonomous research systems already explore literature, generate hypotheses, design experiments, write code and revise scientific artifacts. P14 does not claim that recursive research agents, multi-agent review, reflection, preregistration or scientific-memory systems are new. Its question is narrower:

> Does a fail-closed recursive governance contract improve the **quality of scientific research decisions** under matched model, information, tool and compute budgets, without suppressing useful discovery?

ORION-RSE separates two responsibilities that are often conflated:

1. **candidate research generation:** propose claims, retrieve donors, design and execute tests, interpret observations;
2. **scientific promotion/governance:** decide what the evidence is allowed to establish, what is already donor-owned, what remains negative or non-identifiable, when recursion should stop, and when a prior decision must reopen.

The candidate research system cannot grant itself scientific or novelty authority merely because its internal checks pass. External gold, independent reviewers or explicit authority owners remain outside the candidate system.

## 2. Donor boundary

P14 absorbs, rather than claims ownership of, the following families:

- autonomous or goal-evolving scientific research agents;
- literature-RAG and experiment-planning agents;
- reflection, self-critique and multi-agent debate/reviewer workflows;
- preregistration, checklists and reproducibility practices;
- truth maintenance, belief revision and change propagation;
- provenance/evidence tracing;
- authorization/capability systems;
- abstention and uncertainty-aware agents;
- benchmark auditing and contamination/leakage controls.

The candidate contribution is the **research-governance contract and its matched evaluation**: claim atomization, donor subtraction, protected freeze, negative-history retention, explicit scientific dispositions, authority separation, recursion stops and regime-change reopening, evaluated against scientific-decision endpoints rather than documentation volume.

## 3. ORION-RSE objects

### 3.1 Research atom

A research atom is a bounded claim/question with:

- parent claim identity;
- protected discriminator;
- nearest donors/owners;
- protocol/study identity;
- evidence receipts;
- resource envelope;
- evaluator identity;
- authority owner;
- status/disposition;
- recursion/reopen conditions.

Fine-grained atoms are research decomposition units, not automatic publication units.

### 3.2 Scientific dispositions

The system supports explicit outcomes such as:

- `SUPPORTED_RESIDUAL` / positive bounded residual;
- `SUBSUMED` — observation may be positive but the claimed novelty/residual is already donor-owned;
- `INTERACTION_ONLY` — an effect belongs to an interaction and cannot be decomposed into independent atom claims;
- `REDUNDANT_EQUIVALENT`;
- `OVERREACH_HARMFUL`;
- `NON_IDENTIFIABLE`;
- `CANNOT_CHECK`;
- negative/null terminal with live parent question;
- reopen-required after material regime/evidence change.

The exact registry vocabulary can evolve, but changing a label after protected outcomes cannot retroactively change the scientific history.

### 3.3 Donor/ownership map

Before novelty promotion, the system records the closest prior mechanisms and assigns `ADOPT`, `ADAPT`, `COMPOSE`, `DEFER` or `REJECT`-style relationships. A positive result does not automatically imply a novel contribution. If a strong donor fully owns the proposed layer, the atom is narrowed or subsumed.

### 3.4 Protected discriminator and protocol freeze

A claim is not tested against an endpoint chosen after results. The protocol records what observation would distinguish the candidate residual from strong alternatives. Material post-outcome changes require a new protocol identity.

### 3.5 Negative-history ledger

Negative, null, donor-subsumed and failed preregistered outcomes are retained as first-class evidence. Later work may reopen a question after a justified regime change, but it does not erase the old terminal.

### 3.6 Evaluator/authority separation

Local tests, model judges or candidate agents can evaluate evidence but do not automatically own scientific or novelty authority. The system records who may certify an operational check and who owns the external promotion decision.

### 3.7 Recursion stop and reopen

Recursion stops when the research question has no material unresolved discriminator, is donor-subsumed, non-identifiable under available evidence, blocked by an external dependency, or otherwise reaches a registered stop condition. It reopens when a material evidence, donor, environment, representation or responsibility change invalidates the previous basis.

## 4. ORION-RSE lifecycle

The candidate lifecycle is:

`question -> claim atoms -> nearest-work/donor subtraction -> protected discriminator -> protocol freeze -> execution/evidence receipts -> disposition -> recurse/stop -> later reopen if warranted`.

At every transition, the system must be able to answer:

1. what changed;
2. which evidence supports the change;
3. what prior work owns nearby territory;
4. what protected test was specified before outcomes;
5. what negative/null evidence remains active;
6. what the system is **not** authorized to claim.

This lifecycle is deliberately fail-closed. `CANNOT_CHECK` is a valid scientific outcome when evidence or authority is insufficient.

## 5. Existing substrate and motivating evidence

ORION currently contains:

- recursive atom-study calculus with explicit positive, negative, subsumed, interaction-only and non-identifiable dispositions;
- explicit recursion stop reasons;
- donor/ownership maps and saturation/no-material-change rounds;
- negative-history retention;
- bounded study packets;
- evaluator/authority separation;
- verified recursive-scientific-evolution closure machinery;
- Frontier V2 registry/scheduler examples of positive, negative and donor-subsumed children.

Two concrete development histories are especially relevant:

1. a controlled positive can later be marked donor-subsumed rather than promoted as novelty;
2. a preregistered near-miss can remain permanently negative rather than being retuned after the result.

These cases demonstrate that the machinery can *represent* disciplined dispositions. They do not establish that ORION-RSE improves scientific decisions relative to strong research-agent baselines. That efficacy question is the protected P14 target.

## 6. Research question and hypotheses

### H1 — safety

Under matched information/model/tool/budget, ORION-RSE lowers false scientific promotion and unsupported claim widening relative to strong research-agent workflows.

### H2 — productivity constraint

The safety gain does not materially reduce independently judged useful residual/discovery rate beyond a prospectively frozen noninferiority margin.

### H3 — component causality

At least one core governance component—donor subtraction, protected freeze, negative history, authority separation, recursion stops or reopen semantics—has a measurable effect on scientific-decision errors beyond process overhead.

### H4 — longitudinal value

Retained negative/subsumed/reopen history improves a later research round when the regime, evidence or donor set changes, without causing stale over-transfer.

These are hypotheses, not current results.

## 7. Benchmark Tier A: hidden-gold research-decision worlds

A fresh generator must be created independently of cases already encoded in ORION’s rules. Earlier P1–P13 episodes may inform design patterns but cannot be direct scoring instances.

### 7.1 Required families

At minimum:

1. true standalone effect;
2. interaction-only effect;
3. donor-subsumed positive;
4. null child with a scientifically live parent;
5. leaky/corrupted benchmark yielding impossible performance;
6. post-hoc endpoint temptation;
7. unrelated infrastructure failure beside valid science;
8. regime change that should reopen an old negative/certificate;
9. non-identifiable case where `CANNOT_CHECK` is correct;
10. strong clean positive deserving bounded promotion.

### 7.2 Leakage controls

- remint atom names and disposition labels;
- use multiple lexical and structural templates per family;
- hide evaluator-only ownership/materiality/gold fields;
- keep candidate-system prompts free of the protected terminal vocabulary when it would leak the answer;
- generate protected identities after system development;
- freeze family counts and split rules before execution.

### 7.3 Candidate output

Each system produces:

- proposed claim;
- nearest-work/donor map;
- protected discriminator/experiment plan;
- interpretation of observations;
- final disposition and bounded allowed claim;
- negative/evidence ledger.

## 8. Benchmark Tier B: realistic blinded research packets

Prospectively assemble cases across at least three domains, for example:

- ML/AI experiments;
- formal mathematics/software verification;
- computational/scientific modelling or data analysis.

Each packet contains literature/source material, protocol, intermediate observations, failures, resource limits and possible donor conflicts. Candidate systems see identical public packets.

Independent reviewers receive anonymized outputs and judge scientific admissibility without system identity. Reviewers do not see the candidate system’s internal authority claims and cannot be the same model instance that generated the research.

Primary reviewer tasks:

- identify the strongest allowed claim;
- identify donor-subsumed/overbroad content;
- identify missing or mishandled negatives;
- judge whether `CANNOT_CHECK`/reopen is warranted;
- rate evidence completeness/reproducibility;
- identify useful residual discoveries.

## 9. Benchmark Tier C: longitudinal research

Use linked two-or-more-round problems.

Round 1 yields a mix of positive, null, negative or subsumed evidence. Round 2 changes a material condition: new data, new donor, revised environment, new measurement or changed question.

The central comparison is whether explicit historical negatives/subsumption/reopen conditions improve the round-2 decision versus baselines that summarize or discard history.

A good memory system must avoid two symmetric errors:

- **forgetting:** repeating disproven/subsumed work or re-promoting an old false claim;
- **over-transfer:** treating an old negative as permanent after a genuine regime change.

## 10. Systems and baselines

Use the same underlying frontier model where practical to isolate governance effects.

Required systems:

1. strong raw research LLM/agent;
2. reflection/self-critique loop;
3. multi-agent researcher + reviewer/debate workflow;
4. literature-RAG + experiment planning workflow;
5. preregistration/checklist-only workflow;
6. ORION-RSE full;
7. ORION-RSE ablations:
   - no donor subtraction;
   - no protected freeze;
   - no negative history;
   - no authority separation;
   - no recursion stops;
   - no reopen semantics.

Comparator prompts/workflows should be strong, not straw men. ORION vocabulary cannot be used as the scoring key.

## 11. Matched resource accounting

More governance can mean more computation. Therefore every system reports:

- model/checkpoint/version;
- input evidence and context;
- web/literature access;
- tool access;
- token/generation budget;
- search/experiment budget;
- reviewer/evaluator calls;
- number of reflection/debate/research passes;
- wall time;
- external tool calls.

The P11–P14 shared resource schema is used where applicable. If ORION-RSE spends more compute, that overhead is visible; it cannot be hidden as “method.”

## 12. Endpoints

### 12.1 Primary safety endpoint

**False scientific promotion / overbroad-claim rate.** A promotion is false when the final claim exceeds protected gold or independent allowed-claim adjudication, including false novelty, ignored donor ownership, unsupported causal/general claims, invalid endpoint drift or promotion under non-identifiability.

### 12.2 Co-primary productivity constraint

**Independently accepted useful residual/discovery rate** must be non-inferior within a prospectively frozen margin.

This prevents an always-abstain system from winning the safety metric.

### 12.3 Secondary endpoints

- false novelty rate;
- donor-subsumption detection;
- interaction-only classification;
- post-hoc protocol/endpoint drift;
- material negative evidence retained;
- correct `CANNOT_CHECK`/reopen;
- reproducibility/evidence completeness;
- reviewer agreement;
- research cost/time/tokens/tool calls;
- later-round decision improvement.

No opaque composite score is primary.

## 13. Statistical plan

### 13.1 Exact hidden-gold tier

Use paired comparisons because systems evaluate the same cases. Report family-block rates and uncertainty. Depending on frozen sample size, use exact paired methods or paired/bootstrap confidence intervals. Do not pool families in a way that hides a failure mode.

### 13.2 Realistic blinded tier

Use multiple independent reviewers where feasible. Report inter-rater agreement, adjudicated labels and paired system comparisons on the same packets. The adjudication procedure, conflict rule and reviewer eligibility are frozen before protected scoring.

### 13.3 Longitudinal tier

Prespecify round-2 utility endpoints and prohibit tuning on protected round-2 outcomes. Analysis distinguishes benefit from retained history and harm from stale over-transfer.

### 13.4 Multiple claims

Freeze one safety primary and one productivity constraint. Secondary endpoints are reported with uncertainty and multiplicity-aware interpretation rather than used to rescue a failed primary.

No p values, margins or sample sizes are inserted into this manuscript before benchmark freeze.

## 14. Hostile controls

A positive P14 result is invalid if:

- benchmark cases are copied from ORION development episodes;
- evaluator rewards ORION terminology instead of scientific correctness;
- ORION-RSE receives more web/tool/model budget;
- final judge is the same candidate model instance;
- donor lookup is stronger for one arm;
- useful discovery is not measured, allowing blanket abstention;
- negative-history retention increases documentation but does not improve later decisions;
- recursion produces more bureaucracy without a decision benefit;
- protocol freeze is only nominal and endpoints change after outcomes.

## 15. Negative-result elimination programme

“Elimination” here means testing and removing alternative explanations. A failed protected terminal is retained.

### N1 — safety by abstention

Freeze useful-discovery noninferiority. Report promotion coverage and correct positive promotion. If ORION-RSE is safer only because it claims less, superiority fails.

### N2 — safety by extra compute

Match resource envelopes. Run equal-budget and equal-quality/cost frontiers. If governance only helps with substantially more compute, report the overhead and narrow the claim.

### N3 — vocabulary leakage

Generate fresh worlds with reminted identities, paraphrased structures and evaluator-only gold. Score semantic scientific dispositions rather than token labels.

### N4 — donor-search advantage

Give identical retrieval/web access and source packets. Where donor retrieval itself is evaluated, separate retrieval quality from disposition quality.

### N5 — self-judging bias

Candidate systems cannot provide final gold. Use exact contracts or blinded independent review. Where model judges are unavoidable, use models/processes isolated from generation and test judge sensitivity.

### N6 — negative history as dead weight

Tier C must measure a later-round decision benefit. If retained negatives do not improve future decisions, negative-history superiority is not claimed even if bookkeeping is better.

### N7 — recursion overhead with no utility

Ablate recursion stops and decomposition depth. Measure cost and final disposition quality. If simpler workflows achieve equal scientific decisions with less overhead, narrow ORION-RSE to the components that survive.

### N8 — donor subtraction suppresses legitimate novelty

Include clean positive families and realistic cases where a real residual exists. Measure false subsumption as a productivity error. Donor subtraction must reduce false novelty without collapsing legitimate residual discovery.

## 16. Current results

### 16.1 What is established

ORION implements the target governance objects and has executable histories demonstrating positive, negative, donor-subsumed and fail-closed outcomes. It can preserve negative terminals and separate local evaluation from external authority.

### 16.2 What is not established

There is **no protected P14 comparative benchmark result** showing that ORION-RSE outperforms raw agents, reflection, multi-agent review, literature-RAG or preregistration/checklist workflows. There is no earned effect size, confidence interval or useful-discovery noninferiority result.

Therefore the current paper is a methods and evaluation-contract manuscript. Any sentence implying empirical superiority is forbidden until the benchmark runs.

## 17. Planned figures

1. **ORION-RSE lifecycle:** claim -> donor subtraction -> protected discriminator -> experiment -> disposition -> recurse/stop/reopen.
2. **Controlled benchmark error matrix:** system × failure family.
3. **False promotion vs useful discovery frontier.**
4. **Component ablations:** donor subtraction, freeze, negative history, authority, stop, reopen.
5. **Longitudinal value:** round-2 decision quality with/without retained history.
6. **Realistic blinded review:** allowed-claim correctness across domains.

## 18. Planned tables

1. ORION-RSE objects, authority boundaries and donor precedents.
2. Exact benchmark families and protected discriminators.
3. Full-system versus baseline/ablation outcomes.
4. Blinded reviewer agreement and allowed-claim accuracy.
5. Cost/overhead accounting.

## 19. Discussion

ORION-RSE treats scientific restraint as an explicit computational responsibility. This differs from adding another self-critique pass. The system records what would discriminate a claim, what prior work already owns, what negative evidence remains active, and who is allowed to promote the claim. The intended benefit is not more verbose reasoning but fewer scientifically invalid transitions from observation to claim.

The method also makes negative results useful without making them permanent dogma. A negative terminal stays in history, preventing accidental repetition or retroactive retuning, while explicit reopen conditions allow new evidence or regime changes to revive the question. This symmetry—remember enough to avoid forgetting, reopen enough to avoid stale over-transfer—is central to the longitudinal evaluation.

The strongest risk is bureaucratic conservatism. A system can trivially lower false claims by refusing to promote anything. That is why productivity is a co-primary constraint and why clean-positive benchmark families are required. A useful research machine must both reject unsupported claims and preserve genuine discoveries.

## 20. Limitations

1. ORION-RSE is currently evaluated only as an implemented governance substrate and development history, not through the protected comparative benchmark.
2. Exact benchmark worlds may reward rule-following without transferring to realistic science; the blinded tier is mandatory.
3. Independent expert adjudication is expensive and itself imperfect.
4. Matching heterogeneous research-agent compute is difficult and requires transparent resource vectors.
5. Donor/novelty judgments can be genuinely contested; `CANNOT_CHECK` may be the correct result.
6. Governance components may interact, making single ablations hard to interpret.
7. The method cannot guarantee truth or novelty; it governs evidence-to-claim transitions under bounded information.
8. Rapid 2025–2026 research-agent development requires a final external baseline/literature refresh before execution and submission.

## 21. Reproducibility and benchmark release

The final P14 package must release:

- benchmark generators and template families;
- protected split/freeze hashes after evaluation is complete or through a leakage-safe release process;
- baseline prompts/workflows and model identities;
- ORION-RSE configuration and ablations;
- resource receipts;
- evaluator contracts;
- anonymized reviewer protocol and adjudication rules;
- machine-readable final dispositions and negative-history ledgers.

Earlier ORION episodes used as design templates must be labeled and excluded from protected scoring.

## 22. Data and code availability

Existing ORION governance machinery and verified RSE artifacts are repository code/research records. The fresh P14 benchmark does not yet exist as a protected executed dataset. It must be generated, frozen and released according to the leakage rules above before empirical promotion.

## 23. Claim ledger

| Claim | Status | Evidence | Forbidden widening |
|---|---|---|---|
| ORION-RSE defines auditable recursive governance objects | IMPLEMENTED/METHOD | ORION registry/RSE substrate | superiority claim |
| negative/subsumed histories can be represented and retained | IMPLEMENTED + CASE HISTORY | repository histories | measured future benefit |
| evaluator/authority separation is encoded | IMPLEMENTED/METHOD | RSE/governance substrate | external authority magically guaranteed |
| ORION-RSE reduces false promotion | OPEN | Tier A/B protected benchmark | may not be stated now |
| useful discovery is non-inferior | OPEN | co-primary protected analysis | no blanket safety claim |
| negative history improves later rounds | OPEN | Tier C | may not be inferred from retention alone |
| full system beats strong research-agent baselines | OPEN | matched comparison | no autonomous-scientist superiority |

## 24. Publication decision

**Current decision:** complete methods/protocol manuscript, not yet an empirical research-machine superiority paper.

Minimum external promotion package:

- fresh hidden-gold controlled benchmark;
- matched strong research-agent baselines;
- ORION-RSE ablations;
- at least one blinded realistic tranche;
- false-promotion reduction subject to useful-discovery noninferiority;
- longitudinal negative-history/reopen test;
- reproducible benchmark/protocol release.

If governance reduces false claims only by suppressing useful discovery or spending substantially more compute, the strongest P14 claim fails and the paper must narrow to the method/components that survive.

## References and donor notes

1. Doyle, J. **A Truth Maintenance System.** *Artificial Intelligence* 12(3):231–272 (1979). DOI `10.1016/0004-3702(79)90008-0`.
2. de Kleer, J. **An Assumption-Based TMS.** *Artificial Intelligence* 28(2):127–162 (1986). DOI `10.1016/0004-3702(86)90080-9`.
3. Alchourrón, C. E., Gärdenfors, P. & Makinson, D. **On the Logic of Theory Change: Partial Meet Contraction and Revision Functions.** *Journal of Symbolic Logic* 50(2) (1985). [Final page/DOI metadata to verify.]
4. Du, Y. et al. **Accelerating Scientific Discovery with Autonomous Goal-evolving Agents.** arXiv:2512.21782 (2025), as recorded in ORION’s canonical bibliography; archival status must be refreshed.
5. Tang, Y. & Yang, Y. **AI Research Agents Narrow Scientific Exploration.** arXiv:2605.27905 (2026), as recorded in ORION’s canonical bibliography; archival status must be refreshed.
6. ORION canonical bibliography and donor-assimilation ledgers for current agent governance, provenance, abstention, authorization and research-agent donors.

### Citation integrity note

The live external academic/web search endpoint was unavailable during this drafting pass. Before benchmark freeze and submission, run the full academic-search/reference-verification workflow to update strong research-agent baselines, peer-reviewed replacements, DOIs and any 2026 donor that could narrow the claim.
