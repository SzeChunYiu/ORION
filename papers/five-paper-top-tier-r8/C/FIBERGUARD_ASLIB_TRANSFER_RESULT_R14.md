# FiberGuard R14 — prospective held-out transfer result

Date: 2026-08-26

Protocol/executable freeze: `8748860e3b305eff8e328169c3276e1616138f4f`

Exact parent: `6c23a3fe4ccf415bc3a73794878d72583ed48eb2`

Workflow run/job: `33013486450` / `98325541835`

Full result SHA-256: `2a31fd86f51df52190c646deea140d34536aa8c3e77edfb6ca8fb95c22ea6f07`

Artifact SHA-256: `6c6fc95843f0ef10ffb52970c96d782f6fd1e563e4b5026dd1385a015967a615`

Execution terminal:

`FIBERGUARD_ASLIB_TRANSFER_R14_PASS`

Scientific terminal:

`FROZEN_R14_ROBUST_TRANSFER_GATE_FAIL__MEAN_EXCESS_IMPROVES`

## Result in one sentence

The preregistered training-selected FiberGuard arm improves mean held-out total excess on both split schemes and strongly beats all-feature acquisition, but it exceeds the no-feature worst-case value on both schemes; therefore the frozen robust transfer claim fails.

This is a scientific adverse result, not an execution failure. The source, folds, group construction, quartile transform, support threshold, fallback, 513-candidate menu, tie rules, PAR10 convention and common-oracle loss were fixed in the prior commit before aggregate outcomes were read.

## Exact aggregate result

| Split | Arm | Robust total excess | Mean total excess | Median | p95 | Cell policy use | Fallbacks |
|---|---|---:|---:|---:|---:|---:|---:|
| source CV | no features | 12000.00 | 5448.3147 | 582.710 | 11999.97 | 100.00% | 0 |
| source CV | training-selected quartile/support-2 | **12002.23** | **3733.4218** | 75.135 | 11999.68 | 98.02% | 32 |
| source CV | R11 `{Pre,lobjois}` quartile/support-2 | 12370.14 | 1849.6915 | 14.470 | 11979.54 | 86.56% | 217 |
| source CV | R11 `{Pre,lobjois}` exact equality | 12370.14 | 5471.3180 | 749.540 | 12001.98 | 1.24% | 1594 |
| source CV | all features quartile/support-2 | 28904.57 | 5540.4253 | 770.365 | 12028.23 | 2.42% | 1575 |
| prefix-group | no features | 12000.00 | 5448.3147 | 582.710 | 11999.97 | 100.00% | 0 |
| prefix-group | training-selected quartile/support-2 | **12005.83** | **5049.6492** | 356.605 | 11999.96 | 98.51% | 24 |
| prefix-group | R11 `{Pre,lobjois}` quartile/support-2 | 12370.14 | 2537.5629 | 22.040 | 11998.83 | 81.41% | 300 |
| prefix-group | R11 `{Pre,lobjois}` exact equality | 12370.14 | 5471.4624 | 749.540 | 12001.98 | 1.24% | 1594 |
| prefix-group | all features quartile/support-2 | 28904.57 | 5590.8803 | 792.000 | 12028.23 | 1.98% | 1582 |

The primary arm reduces mean excess relative to no features by `1714.8929` (31.48%) under source CV and by `398.6654` (7.32%) under the group-disjoint control. Its worst-case excess is nevertheless `2.23` and `5.83` above the no-feature ceiling. It strictly beats the all-feature arm on every aggregate metric, but the preregistered gate required beating both extremes on both splits.

## Two distinct worst-case failure mechanisms

### Source-CV support failure

The source-CV worst row is `SAT_Competition2009/CRAFTED/ramseycube/Q3inK12.cnf`:

- selected arm: training-selected quartile/support-2;
- training cell support: 1, so the fallback `clasp1` is used;
- feature cost: `4.21`;
- `clasp1` PAR10: `12000`;
- statewise virtual-best runtime: `1.98`;
- total excess: `12002.23`.

Thus an unsupported cell plus positive acquisition cost pushes the row above the no-feature robust value.

### Group-split in-cell action drift

The prefix-group worst row is `SAT_Competition2011/SAT11/crafted/anton/SRHD-SGI/srhd-sgi-m62-q1327.5-n60-p15-s1351253.cnf`:

- the quartile cell is supported by seven training instances;
- the cell policy selects `mphaseSAT`;
- feature cost: `14.47`;
- selected-solver PAR10: `12000`;
- statewise virtual-best runtime: `8.64`;
- total excess: `12005.83`.

This failure is not caused by unseen representation support. A supported training cell transports the wrong robust action to the held-out group.

The exact supported/fallback decomposition confirms the distinction. Under source CV, the fallback subset has maximum `12002.23`, while supported rows have maximum `12000.20`. Under the prefix-group split, fallback rows stay at `12000`, while supported rows attain `12005.83`.

## Exact equality fibres do not transport

The R11 exact `{Pre,lobjois}` signature is seen in outer training for only `20/1614` held-out rows (`1.24%`) under either split. It therefore falls back on `1594/1614` rows. Every held-out row is worse than the no-feature policy after feature cost, and mean excess increases by about `23` seconds-equivalent.

This is a direct empirical warning against treating near-singleton complete-corpus fibres as transferable representations. The R11 complete-corpus certificate remains exact for its pinned finite corpus; it does not become a generalization certificate.

## Quantization recovers mean value, not robust value

Training-only quartiles make `{Pre,lobjois}` operational on many more held-out rows:

- source CV: 93.56% signatures seen, 86.56% supported-cell actions used;
- prefix groups: 89.71% signatures seen, 81.41% supported-cell actions used.

Mean total excess falls by 66.05% and 53.42% relative to no features. However robust total excess is `12370.14` on both splits because a low-support/fallback row combines a solver timeout with `417.60` feature cost. This arm is also a post-selected R11 control, not an independent transfer claim.

## Full acquisition is decisively adverse

All-feature quartile acquisition has maximum feature cost `16906.55` and robust total excess `28904.57`. It is worse than no features in mean excess on both splits and uses a supported cell policy on only 39 source-CV rows and 32 prefix-group rows. This is the registered cost-erasure control: richer information is not operationally better after acquisition cost.

## Split sensitivity and leakage

The source CV assigns 1297 of 1614 instances to path-prefix groups that occur in multiple folds: 93 of 408 declared prefix groups cross source folds. The outcome-blind prefix-group construction has zero crossing groups, balanced fold loads of 161–162, and largest group size 119.

The primary mean improvement shrinks from 31.48% under source CV to 7.32% under the group-disjoint control. This does not prove that path prefixes are true scientific families; it does show that the apparent transfer magnitude is sensitive to a stricter structural split.

## Robust-objective diagnosis

Outer-training robust selection chose no feature steps in 4/10 source-CV folds and 8/10 prefix-group folds; the remaining folds chose only `Pre`. The worst-case objective correctly recognizes that a single held-out timeout can erase a large average benefit. At the same time, the small positive feature charge on such a row makes strict improvement over a no-feature PAR10 ceiling impossible.

This result therefore separates two claims that R11 alone could not distinguish:

1. **average decision value survives to held-out rows** under the frozen quantized policies;
2. **worst-case transfer does not survive** under the frozen static action and fallback rules.

The second claim controls manuscript authority.

## Manuscript disposition

Admissible statement:

> On pinned SAT12-ALL, exact full-corpus static optimization finds a highly favorable sparse representation. Under a prospectively frozen ten-fold transfer audit, training-only quantization preserves substantial mean benefit, but strict robust improvement fails on both the source folds and a group-disjoint control. Exact equality fibres almost never recur, and full acquisition is cost-dominated.

Forbidden statements:

- FiberGuard is robustly validated on unseen instances;
- exact representation fibres generalize;
- source CV establishes family independence;
- the R11 full-corpus optimum is an unbiased transfer estimate;
- the result establishes superiority to learned selectors;
- the result establishes deployment, novelty or journal authority.

## Next scientific gate

The frozen result rules out simply promoting the R11 static policy. The next application must address the two observed failure channels without retuning R14:

1. a **support-aware route/abstain policy** that explicitly charges the fallback or portfolio schedule relative to the same oracle;
2. a **tail/robust objective declared before evaluation**, retaining timeout count and catastrophic excess separately rather than converting an average win into safety;
3. a standard learned algorithm-selection baseline trained and evaluated on the same outer folds;
4. an independently curated or domain-expert family split beyond the path-prefix control;
5. an independent rerun of the exact aggregation and feature-cost conventions.

R12/R13 adaptive or randomized policies may now be tested only as successor arms. Expected randomization cannot be described as pathwise protection, and any route-to-exact-solver cost must be expressed relative to the same statewise oracle.

## Authority

This is prospectively frozen finite out-of-fold evidence on one public historical scenario. It is stronger than the same-corpus R11 result and is a meaningful negative robust-transfer result. It does not establish external replication, true family independence, current production value, learned-selector performance, generic generalization, novelty, venue judgment, or journal readiness.
