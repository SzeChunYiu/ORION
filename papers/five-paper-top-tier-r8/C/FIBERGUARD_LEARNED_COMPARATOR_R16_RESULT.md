# FiberGuard R16 — untouched learned-selector comparator result

Date: 2026-08-26

Prospective executable commit: `05186ccf3c0dd1ef84a2639f8dc02ec8ef21a3eb`

Workflow run/job: `33018700255` / `98343370948`

Full result SHA-256: `ba44da6354a0d8934d09898042d554638f631232fc6e337bd1ace904dafcb60e`

Artifact SHA-256: `8eba37ab9ca3e43e25da6f58fd36d1b7b1c1295bd26bc69126ba90a3d0586241`

Execution terminal:

`FIBERGUARD_LEARNED_COMPARATOR_R16_PASS`

Portfolio terminal histogram:

- `C_RF_REGRESSION_DOMINATES_FIBERGUARD`: 2 scenarios;
- `C_LEARNED_AND_FIBERGUARD_MIXED_NO_DOMINANCE`: 1 scenario.

## Result in one sentence

On exactly the FiberGuard-selected representation and feature cost, per-solver random-forest runtime regression failure-aware dominates the exact robust cell action on both registered splits in Bayesian-network structure learning and travelling-salesperson selection; mixed-integer programming is a tie/mixed case because FiberGuard selects no features in every fold.

This is a prospectively frozen adverse comparator result for the claim that the exact fibre action is itself the strongest operational selector. It does not affect the exact fibre/action-regret, conflict-certificate, profile-Bellman or randomized-minimax theorems.

## BNSL-2016

FiberGuard selects `basic+basic_extended` in 18/20 folds and `basic` in two. These steps have zero recorded acquisition cost in the scenario, so same-step comparison is exactly cost matched.

| Split | Arm | Timeouts | Timeout rate | Worst-5% mean | Mean excess |
|---|---|---:|---:|---:|---:|
| source CV | FiberGuard | 51 | 4.33% | 61,170.39 | 3,119.29 |
| source CV | RF regression, same steps | **36** | **3.05%** | **43,374.54** | **2,193.61** |
| source CV | RF classification, same steps | 52 | 4.41% | 62,239.55 | 3,170.46 |
| hash | FiberGuard | 47 | 3.99% | 56,714.08 | 2,895.50 |
| hash | RF regression, same steps | **34** | **2.88%** | **41,164.47** | **2,081.62** |
| hash | RF classification, same steps | 41 | 3.48% | 49,561.59 | 2,516.83 |

Regression satisfies the precommitted dominance predicate on both splits. Classification is worse on source CV and better on hash folds, so its relation to FiberGuard is split-sensitive.

The all-step regressor performs still better—22 timeouts and mean excess near 1,380 on both splits—after paying mean feature cost 15.57. This suggests the R15 representation-selection objective is overconservative for a learned runtime model in this scenario.

## MIP-2016

FiberGuard selects no features in all 20 folds. The same-representation RF arms therefore collapse exactly to the no-feature fallback by protocol; all four have 11 timeouts, 5.05% timeout rate, worst-five-percent mean 69,568.36 and mean excess 3,656.43 on both splits.

The terminal is mixed/no dominance rather than a learned or FiberGuard win.

The all-step regressor, which is outside the same-representation terminal, reduces timeouts from 11 to 7 and mean excess to 2,384–2,409 after mean feature cost 49.10. Again the exact catastrophe/tail representation selector chooses the coarse policy, while the learned runtime model extracts net value from the richer representation.

## TSP-LION2015

FiberGuard selects `eax_probing` in 18/20 folds and `ubc_cheap` in two.

| Split | Arm | Timeouts | Timeout rate | Worst-5% mean | Mean excess |
|---|---|---:|---:|---:|---:|
| source CV | FiberGuard | 64 | 2.06% | 15,703.06 | 815.89 |
| source CV | RF regression, same steps | **43** | **1.38%** | **10,958.08** | **578.62** |
| source CV | RF classification, same steps | 279 | 8.98% | 35,987.52 | 3,321.86 |
| hash | FiberGuard | 68 | 2.19% | 16,603.71 | 860.50 |
| hash | RF regression, same steps | **40** | **1.29%** | **10,272.99** | **544.10** |
| hash | RF classification, same steps | 271 | 8.73% | 35,987.24 | 3,224.07 |

Regression dominates FiberGuard on both splits. Oracle-action classification is decisively adverse, with roughly four times as many timeouts as FiberGuard. This is a useful hostile control: predicting the virtual-best class is not equivalent to minimizing runtime or failure-aware total excess.

The all-step regressor further reduces timeout rate below 0.9% and mean excess to 407–417, despite paying mean feature cost 52.81. Its robust maximum is worse because one high-cost row reaches the PAR10 ceiling, retaining the mean/tail versus maximum distinction established in R14–R15.

## Scientific interpretation

R16 supports four conclusions.

1. **FiberGuard's representation audit is not a complete action learner.** On the same selected representation, a smooth learned runtime map can outperform the exact minimax cell action out of fold.
2. **Representation and action learning must be separated.** The exact fibre object certifies what is possible for a fixed finite cell, while a learned regressor interpolates across training cells and may transfer better.
3. **Oracle-action classification is not a sufficient comparator.** It is unstable in BNSL and catastrophic in TSP under the frozen protocol.
4. **The exact representation selector may be overconservative for learned policies.** All-step regression is favorable in all three scenarios, although it sometimes worsens the maximum after feature cost.

The R11–R16 evidence therefore changes the candidate paper from “an exact robust selector beats learned methods” to a more defensible hybrid claim:

> Exact fibres provide representation-owned impossibility, safety and failure certificates; learned runtime models may supply the action map inside that audited information budget. Complete-corpus exactness, held-out maximum loss, failure-aware transfer and learned-action performance are distinct evidence classes.

## Manuscript authority

Admissible claims:

- exact finite fibre/action-regret and refinement theorems;
- positive complete-corpus static value on SAT12-ALL;
- adverse robust held-out SAT transfer with retained mean gains;
- failure-aware two-of-three non-SAT transfer;
- same-representation RF regression dominance in two of three untouched comparator scenarios;
- adverse oracle-classification control.

Forbidden claims:

- FiberGuard's robust cell action is superior to learned selectors;
- the fixed RF is the strongest current selector;
- all-feature regression has lower worst-case risk;
- source/hash folds establish domain-expert family independence;
- the results establish production value, external replication, novelty or journal authority.

## Next top-tier gate

Internal selector invention is now saturated. The next evidence must be externally anchored:

1. a configured or censor-aware selector such as an AutoFolio/SUNNY/survival-style baseline under identical folds, feature costs and failure metrics;
2. structurally independent reproduction of the R14–R16 aggregation, fitting and terminal logic;
3. domain-expert family splits or independently curated corpora;
4. an independent algorithms/ML review of the claim ledger and current primary-source subtraction;
5. manuscript synthesis that presents R16 as an adverse/narrowing comparator result, not a failed experiment to be omitted.

Until those gates pass, the theory can be journal-quality finite mathematics, but the broad learned-algorithm-selection application is not top-tier externally validated.
