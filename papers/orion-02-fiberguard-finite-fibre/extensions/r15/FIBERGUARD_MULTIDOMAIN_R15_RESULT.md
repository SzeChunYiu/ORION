# FiberGuard R15 — untouched multi-domain catastrophe/tail result

Date: 2026-08-26

Prospective scientific protocol: `395466ed0ca7f0b98fc82763623d01aa08500063`

Frozen executor/workflow: `f919c37fcd2139efa9cbbe08a80814a433ff8301` / `7187a118bcbfaa8bfc11206609ebe101b3323167`

Schema-adapter result head: `9330a46bd527420f3a93929e4b2c735fcbacd60f`

Workflow run/job: `33016586575` / `98336275904`

Full result SHA-256: `bf5605831990322dcdbb11862c310e53ea15401fe37fa6852cdace575163baaf`

Artifact SHA-256: `830f7127b1250c1107375f9870ffd530bc86fdbb829396bb4434bc420095bb53`

Execution terminal:

`FIBERGUARD_MULTIDOMAIN_R15_PASS`

Scientific terminal:

`C_MULTIDOMAIN_CATASTROPHE_TAIL_VALUE_TWO_OF_THREE`

## Prospectively frozen custody

The three-domain registry, all Git blobs, both split schemes, quartile transform, support threshold, fallback, complete feature-step menus, lexicographic catastrophe/tail objective and success gate were fixed before any R15 aggregate result was read.

The first run stopped before aggregate output because ASP-POTASSCO used a performance-column name not anticipated by the parser. The fail-closed successor accepted exactly one non-identity/non-status performance column and bound the observed names:

- ASP-POTASSCO: `runtime`;
- CSP-Minizinc-Time-2016: `PAR10`;
- GRAPHS-2015: `runtime`.

The scenario registry, splits, arms, objectives and gates were unchanged. The failed preflight remains recorded as `PRE_AGGREGATE_SCHEMA_INCOMPATIBILITY`.

## Exact portfolio result

| Scenario | Source CV | Balanced hash | Scenario terminal |
|---|---|---|---|
| ASP-POTASSCO | PASS | PASS | PASS |
| CSP-Minizinc-Time-2016 | FAIL | FAIL | FAIL |
| GRAPHS-2015 | PASS | PASS | PASS |

The precommitted portfolio terminal is therefore two of three. No domain was removed from the denominator.

## ASP-POTASSCO

The catastrophe/tail arm selected the `Static` step in every fold on both splits.

| Split | Arm | Timeouts | Timeout rate | Worst-5% mean | Mean excess | Robust excess |
|---|---|---:|---:|---:|---:|---:|
| source CV | no features | 227 | 17.54% | 5996.14 | 683.73 | 5999.85 |
| source CV | all features | 227 | 17.54% | 5997.67 | 1019.84 | 6003.73 |
| source CV | catastrophe/tail | **156** | **12.06%** | **5965.58** | **359.81** | 5999.90 |
| hash | no features | 224 | 17.31% | 5996.25 | 669.44 | 5999.41 |
| hash | all features | 224 | 17.31% | 5997.71 | 1005.53 | 6003.73 |
| hash | catastrophe/tail | **153** | **11.82%** | **5966.02** | **345.92** | 5999.90 |

The primary arm passes every declared condition on both splits. Mean feature cost is `8.50`, versus `336.11` for all feature steps. Its supported-cell policy is used on about 55% of rows; the remainder use the training no-feature fallback.

This domain demonstrates a genuine failure-aware value regime: timeout count, empirical tail and mean all improve without claiming a lower robust maximum.

## CSP-Minizinc-Time-2016

| Split | Arm | Timeouts | Timeout rate | Worst-5% mean | Mean excess | Robust excess |
|---|---|---:|---:|---:|---:|---:|
| source CV | no features | 29 | 29% | **11985.34** | **1435.57** | 11999.94 |
| source CV | all features | 29 | 29% | 11985.48 | 1494.95 | 12000.03 |
| source CV | catastrophe/tail | 29 | 29% | 11985.36 | 1435.62 | 12000.03 |
| hash | no features | 30 | 30% | 11994.84 | 1554.88 | 11999.97 |
| hash | all features | **28** | **28%** | **11982.84** | **1374.25** | 12000.01 |
| hash | catastrophe/tail | 30 | 30% | 11994.84 | 1554.88 | 11999.97 |

The primary arm chooses no features in 19/20 folds and `base` in one source-CV fold. It fails strict tail/mean improvement on source CV and fails all three primary conditions on the hash split. The all-feature arm is better on the hash split, but not on source CV; this split-sensitive small panel is retained as an adverse domain rather than tuned away.

The exact negative result is informative: the representation menu has only two dependency-closed choices, and the frozen selection rule appropriately defaults almost entirely to the coarse policy.

## GRAPHS-2015

| Split | Arm | Timeouts | Timeout rate | Worst-5% mean | Mean excess | Robust excess |
|---|---|---:|---:|---:|---:|---:|
| source CV | no features | 183 | 3.20% | 230.65M | 11.56M | 999.999999M |
| source CV | all features | 165 | 2.88% | 167.79M | 8.41M | 1000.009084M |
| source CV | catastrophe/tail | **145** | **2.53%** | **97.46M** | **4.89M** | 1000.000002M |
| hash | no features | 164 | 2.86% | 163.76M | 8.21M | 999.999994M |
| hash | all features | 161 | 2.81% | 153.60M | 7.70M | 1000.011092M |
| hash | catastrophe/tail | **150** | **2.62%** | **115.08M** | **5.77M** | 1000.005424M |

The primary arm passes all declared timeout/tail/mean conditions on both splits. It uses sparse subsets built mainly from `cheap_pattern`, `distance_pattern` and `lad_features`; no fold selects every step. Mean feature cost is `392–451`, versus `1117` for all features.

The separately registered robust-selection arm is stronger on timeout, tail and mean in this domain, but this does not invalidate the primary terminal: the predeclared catastrophe/tail arm beats both extremes on both splits. The result also confirms the R15 theorem boundary—major tail/mean gains coexist with a slightly worse maximum because positive feature cost is added to a PAR10-ceiling row.

## Cross-domain interpretation

Three statements are supported:

1. **Failure-aware representation selection transfers beyond SAT in two distinct domains.** ASP and graph matching both improve selected-solver timeout rate, worst-five-percent empirical mean and overall mean on source and outcome-blind hash folds.
2. **The method is not universally beneficial.** MiniZinc/CSP is a clean adverse domain under the same frozen protocol.
3. **Robust maximum remains a different estimand.** Even positive domains do not obtain a lower maximum than no features; their value is catastrophe-count and finite-tail/mean reduction.

The result therefore narrows rather than broadens the FiberGuard headline. It supports exact representation-aware **risk decomposition and failure-aware selection**, not universal worst-case transfer safety.

## Manuscript-admissible statement

> In a prospectively frozen three-domain ASlib study, an exact timeout-first, tail-aware FiberGuard selector improved selected-solver timeout rate, worst-five-percent empirical excess and mean excess on both registered splits in answer-set programming and graph matching, while failing without retuning in MiniZinc/CSP. Together with the adverse SAT robust-transfer result, these findings show that representation cost and failure risk must be reported separately from complete-corpus fibre exactness.

Forbidden upgrades include distribution-free CVaR, family-independent generalization, learned-selector superiority, production deployment value, universal benefit, external reproduction, novelty certification or journal authority.

## Next top-tier gates

The internal theory/application package is now strong enough for an external replication and comparator phase, not another post-outcome in-sample optimization. Required next evidence is:

- a standard learned algorithm-selection baseline under the same folds, costs and timeout/tail metrics;
- an independently implemented replay of aggregation, quantization, policy fitting and gates;
- domain-expert family splits or independently curated corpora;
- current primary-source subtraction against cost-sensitive algorithm selection and active feature acquisition;
- a manuscript synthesis preserving R11 positive complete-corpus, R14 adverse robust transfer and R15 two-of-three failure-aware transfer as separate evidence classes.

The exact results do not themselves grant top-tier or journal authority.
