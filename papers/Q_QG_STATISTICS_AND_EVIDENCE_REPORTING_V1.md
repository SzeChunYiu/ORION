# ORION-Q / ORION-QG statistics and evidence-reporting audit V1

Date: 2026-08-21
Method: `nature-statistics` bounded audit.

The Q/QG portfolio is unusual because many central claims are exact theorems, exhaustive finite-domain checks, deterministic counterexamples, or deterministic synthetic benchmarks rather than conventional sampled experiments. The manuscript must therefore identify the **evidentiary unit** behind every number instead of using one generic language of `n`, significance or replication.

## Evidence classes

| Class | Meaning | Appropriate reporting | Inappropriate reporting |
|---|---|---|---|
| `PROOF` | mathematical argument plus explicitly bounded machine checks of finite lemmas | theorem assumptions, proof obligations, checker domain/count, independent verification | p values, CI as theorem evidence |
| `EXHAUSTIVE_DOMAIN` | every element of a stated finite domain evaluated | exact numerator/denominator, domain definition, zero/nonzero violations | treating configurations as random samples from a population |
| `EXACT_COUNTEREXAMPLE` | one or more exactly refereed witnesses falsify a universal/restricted claim | witness, exact costs, referee identity, why one row is logically decisive | diluting with aggregate accuracy |
| `FROZEN_PANEL` | deterministic or seeded finite panel, not necessarily sampled from a statistical population | panel construction, seed, counts, exact observed frequencies; uncertainty only if a prospectively justified sampling interpretation exists | generic generalization beyond the generator/panel |
| `PROSPECTIVE_CASE` | prediction/diagnosis frozen before outcome | custody order, number of independent tasks/subjects, exact matches/mismatches | post-hoc predictive-validity claims broader than the cases |
| `PAIRED_SYNTHETIC_EPISODES` | paired generated worlds evaluated under multiple policies | independent generating unit, paired differences, bootstrap/CI only when protocol defines them | treating repeated actions/probes within an episode as independent n |
| `TIMING_REPEAT` | runtime measurements | environment, cold/warm distinction, quantiles/distribution, descriptive uncertainty | using timing as scientific theorem authority |
| `REPLAY` | repeated execution to verify determinism | byte/digest equality, process/environment scope | treating repeated identical runs as independent evidence for scientific efficacy |

## Global reporting rules

1. `n` means the independent scientific or generated unit relevant to the inference; inner configurations/checker cases are denominators, not biological-style replicates.
2. Exact exhaustive zero violations are reported as `0 / N` over the complete stated domain, **not** as `p<...`.
3. An exact counterexample refutes a universal claim even if it is one row among thousands; no binomial framing is needed.
4. Seeded episodes support inference only to the registered generator/world distribution unless independent families or external tasks are available.
5. Re-running deterministic code twice establishes replay identity, not statistical replication.
6. Bootstrap intervals must preserve the registered independent unit (family/task/episode), not individual sub-observations.
7. Do not add inferential statistics post hoc merely to make a paper look empirical.
8. Every interval must be named correctly: confidence/bootstrap interval versus prediction interval versus deterministic range.
9. Effect size/magnitude precedes significance language where inference exists.
10. Missing inferential authority is solved by narrowing the claim, not by treating exhaustive internal states as sample size.

---

# ORION-01 statistics/evidence audit

## Load-bearing evidence

### R6N local support-dominance domains
- 536,870,912 R6M local configurations, complete stated combinatorial domain;
- 175,616 F3 letterwise cases, complete stated finite domain;
- 150,994,944 R6I local configurations, separate complete local domain.

**Reporting:** exact counts and zero violations.
**Do not:** describe `N≈688M` as a huge statistical sample or attach p values.

### Exact split and borrow witnesses
- `8<9` and `5<6` are exact counterexamples.

**Reporting:** deterministic witness/cost/referee.
**Do not:** average them with chemistry rows to produce an effect mean.

### R6S all-n theorem
- theorem authority comes from proof plus finite lemma checks (43,688 class tuples; 18,432 local inequality cases) and induction.

**Reporting:** theorem statement and assumptions first; checker counts as proof-assurance detail.

### R6Q finite predicate
- 9,771 registered instances across four panels.

**Reporting:** exact finite-domain confusion counts/zero observed error; identify how panels were generated.
**Do not:** call it population accuracy or universal classifier performance.

### R6R prospective Benzene
- scientific unit: one newly selected public subject, with 15 combinatorial matchings.

**Reporting:** one prospective subject; all 15 in-subject matchings agree.
**Do not:** write `n=15 independent chemistry systems` or infer a 100% population success rate.

---

# ORION-02 statistics/evidence audit

ORION-02's core object is a process/lineage, so conventional statistical inference may be unnecessary.

## Required denominators
- total number of eligible predecessor nodes/chains considered;
- counts by disposition `{positive, negative, donor-absorbed, cannot-check}`;
- number for which a successor was legally opened under the predeclared rules;
- number omitted from the figure/manuscript and why.

**Hard requirement:** the successor graph/census must be total over the declared programme scope or explicitly bounded; otherwise the case-study could cherry-pick attractive recoveries.

## Counterfactual/ablation reporting

If ORION-02 adds a comparison such as “without retained negative history the process repeats a dead end,” define:
- unit = registered research node/decision opportunity;
- predeclared policy variants;
- outcome = legally selected next move, duplicated search, or invalid promotion.

Do not invent a p value from a small lineage. Exact case counts and mechanism-level counterexamples may be more appropriate.

---

# ORION-03 statistics/evidence audit

## Current state

One original frontier instance exists; two additional instances are prospectively frozen but not yet executed. The publication gate already requires 2–3 additional questions.

## Independent unit

The **frontier research question** is the default unit. Multiple capability calls, messages, reasoning traces, controller states or later citations inside one question are not independent n.

## Primary reporting

For each question report separately:
- responsibility-layer relation: AGREE / PARTIAL / DISAGREE / CANNOT_CHECK;
- next-move relation;
- revision/abstention relation;
- later outcome alignment under the frozen scoring map.

With only a few prospective questions, report the case matrix and exact counts. Do not turn `3/3` or `4/4` into a reliability estimate with spurious precision.

## If a pooled summary is retained

Use it only as descriptive `x of N questions`, with N prominent. No general agent-reliability claim, no normal-theory CI, and no independence inflation from coordinates within the same question.

---

# ORION-04 statistics/evidence audit

ORION-04 mixes several synthetic study designs; each must keep its own independent unit and scale.

## N4-A unknown feasibility / typed VOI
- independent unit: generated episode (`n=300` paired episodes, per manuscript);
- policies evaluated on identical episode worlds.

Preferred reporting:
- paired mean utility difference to named comparator;
- episode-level bootstrap interval if/when regenerated from the frozen protocol;
- probes/episode and abstention as descriptive secondary measures.

Do not infer broad real-agent performance.

## N4-B stale receipt reopening
- unit: generated episode/round hierarchy as frozen by protocol; manuscript currently summarizes 200-episode regimes.
- pooled and per-regime effects must not treat all internal reopen attempts as independent.

If using intervals, preserve episode/regime pairing.

## N4-C interval Pareto
- independent unit: paired generated episode (`n=400` per manuscript);
- endpoint: scalarized regret.

Report mean regret difference and zero-regret fraction. The `2.3x` ratio is descriptive; include absolute values so ratio is not the sole effect measure.

## N4-D laundering chains
- unit: chain; current deterministic panel contains 200 hostile + 200 honest chains.

Because this is a constructed finite battery, report exact recall/FPR denominators by attack class. Do not present binomial generalization to arbitrary adversaries.

## N4-E experiment selection
- unit: episode;
- decoy probe fraction is secondary process measure.

Do not treat probes within one episode as independent observations.

## N4-F3 remint/transport
- unit: episode/world under registered regimes.
- exact tie in `REMINT_UNNECESSARY` is a first-right-of-refusal result; report exact equality rather than `ns` or “similar.”

## N1-C paired robustness result
The existing paired solve-rate delta and bootstrap interval may be reported if reproduced exactly from the frozen 128/registered unit structure described by the source protocol. Confirm the unit and bootstrap block before final manuscript insertion.

## Cross-study synthesis

**Forbidden:** pooling all ORION-04 episodes/chains into one overall p value or meta-effect.
**Allowed:** mechanism-level qualitative synthesis plus a table of study-specific effects/denominators.

---

# ORION-09 statistics/evidence audit

ORION-09 combines theorem-grade, exhaustive, finite-panel and prospective evidence.

## TARE
- support-two equality: theorem, no p value;
- QG7/QG7b witness counts: exact finite hostile-search observations;
- QG7c huge local domains: proof/checker denominators, not samples.

## SixLCU
If the stated boundary is exhaustive over 38,760 `n=2` instances, report it as an exact domain statement, not classification test-set accuracy.

## StabPrep
- complete state graph counts at each stated n should be identified as exhaustive finite state spaces where applicable;
- prospective `n=4` panel success/failure must retain its frozen panel construction and exact match counts;
- QG15b mixed cells prove non-identifiability **within the frozen feature vocabulary/domain**; no inferential p value is needed.

## Cross-family conclusion
Three compiler families are **three scientific cases**, not n=3 statistical samples from a defined compiler population. Do not compute a transfer success rate or confidence interval across families.

---

# ORION-10 statistics/evidence audit

## Forecast exactness battery

`9,545 / 9,546` exact comparisons plus one nonzero error is a deterministic benchmark observation.

The logically central statement is:
- one exact `10<11` counterexample refutes universal closed-form exactness;
- theorem-backed upper-bound/support layers survive.

Do not headline `99.9895% accuracy` or attach a confidence interval as if instances were IID population samples.

## Structured `n=2`
`9,261/9,261` should be described as exhaustive on the named structured slice.

## Fresh seeded panel
Report seed, generator and exact `239/240` or corrected-family counts. Generalization is to this generator only.

## Chemistry/library rows
Subject is the scientific unit when discussing external chemistry transfer; matchings within one subject are dependent combinatorial views.

## Timing
Fresh-panel cold per-instance timings and warm-cache timings are descriptive engineering measurements.

Required final details:
- hardware/runner environment;
- software versions;
- whether each timing is one observation or repeated measurement;
- cold-cache definition;
- medians/quantiles with raw timings if available.

Do not attach theorem authority to speedups, and do not compare cold forecast timing to warm DP timing.

---

# Figure/table statistical legend checklist

For every quantitative panel/table include, as applicable:
- independent unit and exact N;
- complete/exhaustive versus sampled/generated status;
- seed/generator for synthetic panels;
- paired versus unpaired design;
- definition of error bars/intervals;
- exact test/model and multiplicity policy **only if inferential statistics are used**;
- whether repeated executions are determinism checks rather than replicates;
- scope of any ratio or percentage;
- zero-denominator handling / CANNOT_CHECK state.

## Final statistical reviewer risks

### P0 blockers
- calling matchings or internal checker configurations independent experimental samples;
- using p values/CI to imply universality of theorem-like claims;
- hiding an exact counterexample inside an aggregate success percentage;
- pooling ORION-04 worlds or ORION-09 families as if exchangeable samples;
- ORION-03 reporting a reliability percentage without enough prospective frontier questions.

### ORION-11 repairable
- missing environment/raw timing details in ORION-10;
- missing explicit paired unit in ORION-04 bootstrap reports;
- ratios without absolute effects/denominators;
- using `significant` to mean scientifically important rather than statistical result.

The statistical closure criterion is **transparent evidence class + correct denominator + claim strength matched to design**, not the presence of a conventional significance test.
