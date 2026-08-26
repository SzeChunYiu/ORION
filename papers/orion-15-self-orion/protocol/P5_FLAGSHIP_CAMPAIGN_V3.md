# ORION-P5 flagship campaign V3 — responsibility-gated self-improvement under protected fresh transfer

**Status:** prospective research protocol; no result is implied by this document.  
**Date:** 2026-08-20.  
**Parent:** #102. Revision-level discriminator lane: #455. Protected verification: #283.  
**Historical protocols:** additive only; do not overwrite P5 V1/V2 or the immutable 21/24 diagnostic archive.

## 1. Scientific target

P5 should not compete on the already-crowded claim that agents can self-edit, maintain experience, diagnose failures, or improve a skill library. The strongest current residual is the **decision problem governing when a self-change is scientifically warranted and when an apparently successful change should be refused**.

Candidate flagship thesis, to be frozen only after donor saturation and pilot instrumentation:

> Under matched task information and declared improvement budgets, responsibility-gated Self-ORION more accurately selects the narrowest warranted revision, converts a larger fraction of accepted self-modifications into independently protected fresh-task gains, and admits fewer harmful or evaluator-compromising changes than strong self-evolving baselines and simpler acceptance policies.

The intended contribution is therefore not “ORION always improves.” It is a stronger and more falsifiable object:

`failure -> responsibility discrimination -> candidate change -> replay -> independent fresh transfer -> protected verification -> external host decision`.

The paper earns its widest version only if all stages below survive. If only a subset survives, the manuscript narrows to that supported mechanism.

## 2. Expert-cell challenge model

The research programme is pressure-tested from four independent roles.

1. **Self-improving-agent systems:** compare against DGM/ADAS/Hyperagents, Ratchet/Library Drift, ADIAS and current self-evolving coding/research agents; prevent a governance effect from being confused with a stronger generator.
2. **Causal debugging and scientific diagnosis:** test whether competing hypotheses and interventions identify the responsible revision layer beyond reflection, SAGE/MHFA-like attribution, CausalFlow-like counterfactual repair and generic root-cause analysis.
3. **Evaluation integrity and measurement:** make replay overfitting, hidden-holdout leakage, evaluator tampering, negative-history deletion, proxy gaming and broken-shut abstention explicit measurable outcomes.
4. **Statistics/reproducibility:** freeze paired estimands, practical margins, tails, multiplicity, identities and negative-history retention before protected outcomes.

A finding is not promoted until all four roles can state what was held fixed, what changed, what alternative explanation was excluded, and what authority remains external.

## 3. Current nearest-work pressure to absorb before final freeze

The final saturation pass must include at least:

- Darwin Gödel Machine / ADAS and direct self-edit/meta-agent search;
- Hyperagents (`arXiv:2603.19461`) — self-referential task+meta-agent evolution and cross-domain meta-level transfer;
- ADIAS (`arXiv:2608.06410`) — persistent issue-centric optimization;
- Ratchet (`arXiv:2605.22148`) and Library Drift (`arXiv:2605.19576`) — outcome-driven retirement, bounded active memory, negative lifecycle evidence and skill-library drift;
- SAGE / Multi-Hypothesis Failure Attribution (`arXiv:2606.31478`);
- CausalFlow (`arXiv:2605.25338`) — interventional causal attribution and minimal counterfactual repair;
- current failure-to-improvement, self-evolving coding-agent, world-model/self-revision and objective-evolution systems already tracked by #102/#455.

For every donor, record `ADOPT/ADAPT/COMPOSE/BASELINE/DEFER`, the exact mechanism absorbed, and the P5 wording that disappears because of the donor. “Uses persistent failures,” “performs causal attribution,” “self-edits,” and “retains skills” are not standalone novelty claims.

## 4. Primary experiment A — shared-candidate acceptance tournament

### 4.1 Why this is the cleanest discriminator

End-to-end self-improvement comparisons confound **candidate generation** with **candidate governance**. A stronger model may generate better edits even if its acceptance rule is worse.

Experiment A first creates one content-addressed candidate pool per episode, then gives **the same candidates** to every acceptance policy. This isolates the value of Self-ORION's evidence and authority discipline.

### 4.2 Candidate generation

For each motivating failure episode, generate a fixed pool of candidate interventions from a preregistered mixture such as:

- direct self-edit/reflection;
- DGM/Hyperagent-style program mutation where runnable;
- ADIAS-like issue-centric repair;
- SAGE/MHFA-like diagnosis-driven proposal;
- CausalFlow-like minimal repair;
- Ratchet-style retained skill/rule edit;
- full Self-ORION proposal path;
- deliberately tempting reward-hack / evaluator-facing candidates as hostile controls.

Every candidate is content-addressed before any protected fresh outcome is visible. Generation budgets, model/provider versions, tool access and candidate count are matched or explicitly cost-accounted.

### 4.3 Acceptance policies over the identical pool

Evaluate at least:

1. motivating-score greedy acceptance;
2. motivating + replay acceptance;
3. replay + fresh acceptance without protected custody;
4. PACE/anytime-valid acceptance where applicable;
5. Ratchet-style outcome-history/lifecycle acceptance;
6. P5 V1 policy;
7. P5 V2 `STATIC -> REPLAY -> FRESH -> PROTECTED` policy;
8. full V3 responsibility-gated policy from #455;
9. oracle responsibility/acceptance ceiling for analysis only;
10. random/budget-matched selector as a floor.

Policies cannot regenerate candidates after seeing protected outcomes.

### 4.4 Primary estimands

The highest-value measurements are **selection-quality** rather than raw motivating score:

- **accepted-improvement PPV:** fraction of accepted candidates that produce positive protected fresh-task improvement without a registered integrity violation;
- **harmful-admission rate:** accepted candidates causing protected regression beyond the frozen safety margin;
- **protected net improvement:** paired fresh-task outcome change on the sealed evaluator;
- **integrity-compromise admission rate:** evaluator/holdout/history/authority attack accepted as improvement;
- **useful-yield:** protected valid improvements accepted per generated candidate;
- **cost per protected valid improvement**;
- **false rejection / broken-shut cost** against the oracle-eligible candidate subset.

Headline claim should require a joint result: outward movement of the **improvement–integrity Pareto frontier**, not a single aggregate score that hides harm.

## 5. Primary experiment B — cause-confusable revision-level discrimination

Consume #455 and PR #616's Stage-0 contract rather than duplicating them. The protected benchmark must contain same-symptom/different-responsibility families where an admissible intervention is needed to distinguish the responsible layer.

Required revision responsibilities, merged only if pilot annotation shows they cannot be reliably separated:

- evidence acquisition/recheck;
- measurement/experimental redesign;
- parameter update;
- within-class model selection;
- M-open model-class expansion;
- representation/regime revision;
- question/objective revision;
- method-basis revision/invention escalation;
- execution/environment repair;
- evaluator/authority repair;
- `UNRESOLVED` / additional discriminator required.

Primary outcomes:

- exact and hierarchical revision-class accuracy;
- false broad-revision rate;
- preservation rate for unaffected knowledge/state;
- harmful invalidation induced by unnecessary broad revision;
- correct `UNRESOLVED/CANNOT_CHECK` rate;
- protected fresh-transfer success after the selected revision;
- diagnostic actions / evidence cost to a warranted revision.

Mandatory adaptivity controls from #455 remain: permuted feedback, no feedback, contradictory feedback, fixed proposal prior with changed evidence, random discriminator, always-broad-revise and always-abstain policies.

## 6. Primary experiment C — end-to-end fresh-transfer campaign

After A/B isolate mechanisms, run full systems end-to-end. A flagship scope requires at least **three heterogeneous hosts** or else the claim must stay domain-specific.

Recommended host ladder:

1. **repository development:** hidden-cause software tasks with exact tests and protected fresh repositories/tasks;
2. **tool/research workflows:** retrieval, environment, measurement/evaluator and representation failures with externally checkable outcomes;
3. **formal/exact tasks:** deterministic or proof/program environments where root cause and final validity can be checked independently.

If resources permit, use at least two model families and one lower-capability model to test whether the governance effect is not just a frontier-model artifact.

### Minimum final protected scale target

Treat this as a planning target until power analysis is frozen:

- >= 240 base episodes total;
- >= 8 cause families with balanced hard strata;
- >= 3 hosts/domains for any cross-domain claim;
- >= 3 independent stochastic repetitions where the system is stochastic;
- paired system comparisons on identical episode/candidate identities;
- a fresh hidden family generated **after** method freeze for the final external generalization check.

Power/precision simulation must replace these planning counts before final freeze.

## 7. Factorial mechanism decomposition

Do not rely on a single “full ORION vs baseline” difference. Run a predeclared fractional factorial or matched ablation panel covering:

- persistent issue/negative history;
- competing responsibility hypotheses;
- active discriminator/intervention;
- narrowest-licensed revision rule;
- invention-readiness gate;
- replay stage;
- independent fresh stage;
- protected evaluator custody;
- contamination/access telemetry;
- preservation/dependency-scoped reopening;
- no self-certification/promotion authority.

Report interaction effects where practical. The key scientific question is which components improve selection quality, which mainly add conservatism, and which are redundant after strong donor mechanisms are absorbed.

## 8. Longitudinal recurrence study

Seed recurring failure classes across an ordered task stream and compare:

- append-only negative evolution history;
- success-only memory;
- deletable/overwriteable failure history;
- bounded lifecycle/retirement history;
- no persistent history.

Measure cumulative recurrence hazard, time-to-resolution, duplicate repair rate, harmful reuse, archive diversity and cost. A useful positive is reduced **recurrence of already-recognized causal classes** without suppressing novel exploration.

## 9. Integrity stress battery

Each system/policy receives preregistered attacks that create attractive proxy gains:

- stale/defective evaluator;
- fresh-set leakage bait;
- replay-only overfit candidate;
- negative-history deletion;
- score-report tampering;
- benchmark-specific special case;
- candidate modifying evaluator/config rather than task behavior;
- missing-stage laundering;
- authority/self-promotion request;
- high visible gain with protected tail harm.

Every attack has a protected gold disposition. Report attack-specific false-accept rate; do not average catastrophic integrity failures away.

## 10. Statistics and claim gates

### Primary joint gate

Freeze a gate requiring all of:

1. accepted-improvement PPV advantage over the strongest matched acceptance baseline;
2. positive paired protected fresh-task improvement or non-inferior improvement under a predeclared practical margin;
3. harmful-admission rate below the frozen safety margin and better than the strongest baseline where powered;
4. no evidence that the result is explained only by extra candidate count, model strength, evaluator access or serial compute.

Use paired bootstrap or hierarchical models over episode/system/seed; report absolute risk differences, risk ratios and uncertainty. Catastrophic tails and family-level regressions remain separate.

### Secondary gates

- revision-level accuracy / false broad revision;
- integrity-attack false acceptance;
- recurrence hazard;
- cost per protected valid improvement;
- calibration/selective-risk curves;
- effect across hosts/model families.

Multiplicity and stopping rules are frozen before protected outcomes.

## 11. Figures and tables designed for a high-impact paper

### Headline figures

**P5-A — Improvement–integrity Pareto frontier.**  
X = protected fresh improvement; Y = harmful/integrity admission rate; point size = cost; one point per policy/system with uncertainty. The desired result is an outward/downward frontier shift, not merely a higher replay score.

**P5-B — Replay gain vs protected fresh gain scatter.**  
Each candidate is one point; show the “replay winner / fresh loser” quadrant. Color/facet by accepted/rejected policy decision. This makes selection overfit visually undeniable.

**P5-C — Acceptance precision / selective-risk curve.**  
Protected-valid PPV versus acceptance coverage. Add oracle and random floors. This directly shows whether ORION knows which apparent improvements to trust.

**P5-D — Revision responsibility matrix.**  
Gold revision level versus selected revision level, plus a second heatmap of **severity distance** so a needless method/objective rewrite is visibly worse than a nearby mistake.

**P5-E — Longitudinal motivating vs fresh performance.**  
Two trajectories per system across improvement rounds; expose specialist regression instead of plotting only the optimized benchmark.

**P5-F — Recognized-failure recurrence survival curve.**  
Time/rounds until recurrence by negative-history policy.

**P5-G — Integrity attack scoreboard.**  
Per attack family: attempted, blocked, falsely accepted, and consequence on protected evaluation.

**P5-H — Cost to one protected valid improvement.**  
Wall time, tokens, tool calls and evaluator calls with uncertainty.

### Required tables

1. nearest-work mechanism disposition after August-2026 closure;
2. all baseline/ablation results with CIs and resource accounting;
3. every harmful/null/blocked intervention, immutable and categorized;
4. host/model transfer matrix;
5. candidate-pool provenance and acceptance-policy decisions for Experiment A.

## 12. Result-preservation rule

No adverse result may be deleted, hidden, averaged away or renamed as a success. Every adverse result must instead produce an explicit ORION research object:

`observation -> violated assumption / competing explanation -> discriminator -> protocol or representation change -> fresh retest`.

Examples:

- **ORION ties a simpler policy:** the positive scientific output is a sufficiency boundary; absorb the simpler mechanism and remove unnecessary ORION machinery.
- **ORION is safer but overconservative:** measure the coverage/utility frontier and research a lower-cost discriminator; do not call abstention “improvement.”
- **a revision taxonomy class is unreliable:** merge or redesign the class using adjudication evidence.
- **one host regresses:** retain the host-specific failure, identify the transport assumption that failed, and run a new frozen transfer test.
- **a baseline wins:** assimilate the winning mechanism, version the protocol, and rerun on a fresh protected set.

This preserves the user's goal of turning failures into productive ORION research **without falsifying the empirical record**.

## 13. Widest claim ladder

The manuscript may climb only to the highest rung actually supported.

### Rung 1 — mechanism

> Responsibility/discriminator structure improves revision selection on protected cause-confusable cases.

### Rung 2 — governance

> Protected staged acceptance increases the probability that an accepted self-change survives independent fresh evaluation while reducing harmful/integrity admissions.

### Rung 3 — end-to-end transfer

> Full Self-ORION improves fresh tasks over strong self-evolving baselines under matched resources on the tested host family.

### Rung 4 — heterogeneous transfer

> The governance advantage replicates across multiple task hosts and model families.

### Rung 5 — flagship claim

> Self-ORION provides an empirically validated architecture for **responsibility-gated, fresh-transfer-tested self-improvement under external authority**, moving the improvement–integrity frontier beyond strong contemporary self-evolving systems across heterogeneous domains.

Rung 5 is intentionally difficult. It is the widest defensible claim target, not a prewritten result.

## 14. Execution freeze checklist

Before any final protected outcome:

- [ ] current nearest-work closure and mechanism dispositions complete;
- [ ] exact subject commit(s) and candidate generator code frozen;
- [ ] exact host/task/split hashes frozen;
- [ ] fresh-family generation procedure sealed;
- [ ] model/provider revisions and sampling parameters frozen;
- [ ] candidate count and generation budgets frozen;
- [ ] acceptance-policy implementations/configs frozen;
- [ ] evaluator artifact/hash/custody frozen outside candidate authority;
- [ ] statistical estimands, margins, multiplicity and stopping frozen;
- [ ] integrity attacks frozen;
- [ ] power/precision simulation archived;
- [ ] raw-result schema requires null/harmful/blocked retention;
- [ ] independent #283 replay procedure frozen;
- [ ] P5/P10/P4/P8 authority boundaries rechecked;
- [ ] manuscript headline remains prospective until protected data exist.

## 15. Paper-closing evidence package

A true `ORION-P5 = PEER_REVIEW_READY` terminal should contain:

- exact protected run manifest and content hashes;
- raw candidate pool and per-policy decisions;
- raw per-episode/seed outcomes;
- independent scorer/replay artifacts;
- all headline figures regenerated from raw data;
- all negative/null/harmful episodes retained;
- resource accounting;
- exact nearest-work disposition table;
- final claim ledger mapping each abstract/conclusion sentence to evidence;
- manuscript/PDF/package generated only after the result terminal is frozen.

Until those observations exist, the flagship claim is a **research target**, not a result.