# Common prospective analysis standard V1

This file is part of the outcome-blind design freeze for ORION-P1..P5. Paper-specific `protocol/PROTOCOL_V1.json` files may be stricter, but may not silently weaken these rules after final outcome access.

## Units and pairing

The natural task/case is the default statistical unit. When the same frozen task is executed by multiple systems, comparisons are paired at the task level. Repeated stochastic runs are nested within task/system and are never counted as independent new scientific tasks.

## Primary outcomes

Each paper has one named primary hypothesis. P2 may report separate benchmark-family primary metrics because the official Deep, Wide and complete-gold tasks measure different objects. P3–P5 use a safety/non-inferiority guard alongside the primary improvement metric so a method cannot win by refusing everything or by hiding harmful transfer.

## Uncertainty

- Binary standalone rates: Wilson 95% intervals.
- Paired mean/rate differences: paired percentile bootstrap, 10,000 resamples, deterministic analysis seed recorded in the artifact.
- Report point estimate, interval and absolute effect size. Do not report only p-values.
- Where task families are few or strongly heterogeneous, report family-wise effects and worst-family behavior in addition to pooled estimates.

## Multiplicity

The primary hypothesis is tested once under its frozen direction/margin. Secondary hypothesis families use Holm correction when inferential p-values are reported. Exploratory metrics remain explicitly exploratory and do not retroactively become primary.

## Stochastic systems

Use at least the number of independent runs declared by the paper protocol. Seeds, model sampling settings and provider/model revisions are retained. A single lucky run cannot authorize a headline claim.

## Sample-size planning

Final N is frozen before final outcomes. A pilot may be used only for debugging and variance/precision planning; pilot cases do not enter the final test unless this was declared before pilot outcome inspection. `publication_stats.py precision` provides a conservative proportion half-width planning bound; paper-specific paired designs may use a stronger preregistered calculation.

## Missingness, failures and abstention

Do not drop candidate-caused failures, malformed actions, tool errors, timeouts or abstentions. Infrastructure failures may be excluded only under the symmetric predeclared rule in the paper protocol. `CANNOT_CHECK` is an outcome, not missing data, when the system correctly refuses scientific authority.

## Harm and tail reporting

P4 reports false promotion and clean authority coverage together. P5 reports harmful fresh-transfer regressions and worst-family/tail behavior separately; a high average cannot average away a catastrophic transfer family.

## Result figures/tables

All result-bearing figures and tables are regenerated from normalized raw result records bound to the execution manifest. Captions state N, aggregation unit, uncertainty definition and whether the result is primary, secondary or exploratory. Plot definitions are frozen before the final run; cosmetic layout changes that do not alter metric selection are permitted and logged.

## Protocol versioning

Any change to hypothesis, task family, baseline, ablation, metric, exclusion rule, statistical rule, safety margin, evaluator custody or plot metric after final outcome access requires a new protocol version. The prior protocol and run remain immutable evidence.
