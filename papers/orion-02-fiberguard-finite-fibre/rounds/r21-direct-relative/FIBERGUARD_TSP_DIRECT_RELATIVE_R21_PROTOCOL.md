# FiberGuard R21 — prospectively frozen TSP direct-relative joint-route round

Date frozen: 2026-08-27

Parent programme: #1512 (Round 2 of at most three)

Status at this commit: **source identity, rights, split custody, policy language,
comparators, terminal predicates, and executor are frozen before any TSP-LION2015
algorithm-run, feature-value, feature-cost, feature-runstatus, or CV row is read**.

Round 1's BNSL-2016 null remains unchanged. This round does not tune BNSL, reuse
its subject, or alter any R11/R14/R15/R16/R18/R19/C-NBR/C-NBR2 record.

## 1. Scientific question

On a previously untouched non-SAT algorithm-selection subject, can a route that
models the **paired relative total loss** of one learned solver selector and one
fallback solver, using only information available before optional paid
acquisition, reduce out-of-fold total excess cost relative to the same
information-matched point router while retaining the registered paired-interval
semantics?

The experiment applies the already-proved R18 relative-loss and acquisition-
timing laws and the R19 legal joint-profile repair. It claims no new generic
conformal, k-nearest-neighbour, routing, or algorithm-selection theorem.

## 2. Permission-bearing immutable subject

Repository: `https://github.com/coseal/aslib_data.git`

Commit: `551b22beef8df17de59286b4822ef720e0aa4d6f`

Scenario: `TSP-LION2015` (travelling-salesperson algorithm selection; non-SAT)

The repository root `README.md` states `License: GPLv3`; its pinned Git blob is
`bbae808cc2f718b15b379b30ef6a9909933fc3d5`. The data are not vendored into
ORION. Execution retrieves the pinned revision and verifies every required Git
blob before parsing outcome rows.

| path | pinned Git blob | bytes |
|---|---|---:|
| `README.md` | `bbae808cc2f718b15b379b30ef6a9909933fc3d5` | 3,035 |
| `TSP-LION2015/readme.txt` | `54ad2771d1da0b04105b3bffa0bdd8b0b8d8eb72` | 1,226 |
| `TSP-LION2015/description.txt` | `923b7e0cb7cf354af398875f536717e21a8c7388` | 7,997 |
| `TSP-LION2015/algorithm_runs.arff` | `7ec9db6394c52a2b62d1c44fcd84df47b10ba7b9` | 3,990,796 |
| `TSP-LION2015/cv.arff` | `9d9bee231caaa9cfa017cb176999a36f04d163e5` | 531,764 |
| `TSP-LION2015/feature_costs.arff` | `d6649105f201e9155f5646ff5191e46a824a0ee3` | 1,091,481 |
| `TSP-LION2015/feature_runstatus.arff` | `259e00133d47da914d9cc9f7435f9c97a4346bb9` | 841,300 |
| `TSP-LION2015/feature_values.arff` | `8c62bc84e319d721691d7b1ef1326f1d08437641` | 47,853,407 |

Pre-freeze access was limited to the Git tree, root licence statement,
scenario readme, and `description.txt`. Those establish rights, source
identity, the four solvers, four feature steps, cutoffs, and aggregation
contract. No outcome/CV table header or row was read. `TSP-LION2015` had no
tracked occurrence in ORION at freeze time.

## 3. Frozen accounting

The source readme's TSP convention controls repeated algorithm runs. For each
instance/solver, if at least six of ten repetitions are `ok`, use the median of
all ten recorded runtimes; otherwise assign PAR10, `36,000` seconds. Require
exactly ten repetitions and the four declared solvers.

For feature values, aggregate a feature by the median of all finite repeated
values; any missing observation leaves that instance-feature missing. For each
feature step, aggregate recorded cost by the median of finite repetitions and
runstatus by most-common status with lexical ties. A selected non-`ok` step has
all of its provided features treated as missing but still pays its finite
recorded cost. Because the scenario declares no numeric feature cutoff, a
missing/nonfinite selected-step cost fails closed rather than being imputed.

For every state `x`, the common oracle is the statewise VBS runtime `C*(x)`.
The two paired total excess losses are:

`L(x) = cost(J_learned,x) + runtime(a_learned(x),x) - C*(x)`

`F(x) = cost({ubc_cheap},x) + runtime(a_fallback,x) - C*(x)`.

The direct relative target is `Delta(x)=F(x)-L(x)`. Positive Delta favours the
learned action. The `ubc_cheap` charge is common and sunk when routing occurs;
extra learned-step charges are paid only on learned paths. A post-acquisition
control charges the complete learned representation even on fallback paths.

## 4. Frozen ten-fold custody

Use exactly repetition 1 of the source `cv.arff`; require folds 1 through 10,
one fold per admitted instance, and equal instance sets across every table.
For outer test fold `t` (one-based, cyclic modulo ten):

- calibration fold: `t+1`;
- pair-selection fold: `t+2`;
- route-fit fold: `t+3`;
- learned-model training: the remaining six folds.

All ten outer folds execute. An instance's solver outcome is used as test data
exactly once. Transform parameters, learned actions, legal-pair choice, route
model, and interval radius for that test row use only the other nine folds in
their declared roles.

## 5. Frozen learned/fallback profile grammar

`ubc_cheap` is the pre-route information map. Numeric inputs are imputed from
learned-model training medians, standardized by training median/IQR (unit scale
when IQR is zero), and accompanied by one missingness indicator per feature.
Distance ties break by immutable instance identifier.

The learned representations are `ubc_cheap` plus each nonempty subset of
`{ubc_all,tspmeta,eax_probing}`: seven representations. For each, exact
k-nearest-neighbour portfolio selection uses `k in {1,3,5,9}`. It chooses the
solver with minimum mean training PAR10 among the k neighbours, lexical ties.
This gives 28 learned profiles.

Every one of the four declared solvers is a legal fallback profile. The legal
joint grammar is the complete Cartesian product: `28 * 4 = 112` pairs per
outer fold. Pairing learned and fallback arms by index or separate marginal
selection is forbidden. The executor independently constructs and hashes both
a Cartesian-product enumeration and a nested-loop enumeration and requires
identity.

For each pair, a 9-nearest-neighbour direct-relative regressor is fitted on the
route-fit fold using only `ubc_cheap` inputs and that pair's exact Delta values.
On the pair-selection fold, the point route chooses learned iff predicted
Delta is nonnegative. Select the legal pair by the lexicographic tuple:

1. selected-action timeout count;
2. mean total excess;
3. p95 total excess;
4. maximum total excess;
5. mean acquisition cost;
6. learned-profile name;
7. fallback-solver name.

Every pair's tuple and loss-profile digest is retained. No hyperparameter or
pair is selected from calibration or test outcomes.

## 6. Direct paired interval and routes

For the selected pair, calibrate the absolute direct-relative residual
`|Delta - Delta_hat|` on the independent calibration fold. With
`alpha=0.10`, use the split-conformal nearest-rank radius at
`ceil((n_cal+1)*(1-alpha))`; if this rank exceeds `n_cal`, the radius is
infinite. The interval is `[Delta_hat-q, Delta_hat+q]`.

The primary `direct_relative_certified` route chooses learned only when the
lower endpoint is nonnegative. It chooses fallback when the upper endpoint is
nonpositive and uses fallback by default when the interval crosses zero.
Thus no marginal learned-action certificate is substituted for a joint
relative comparison. The claim ceiling is marginal split-conformal authority
under exchangeability, not deterministic/pathwise safety or distribution
shift.

## 7. Registered comparators and hostile controls

All use the same fold-selected legal pair and the same common oracle:

1. `always_fallback`;
2. `always_learned`;
3. `point_relative` — same route predictor, learned iff point prediction is
   nonnegative; this is the primary strongest information-matched non-oracle
   comparator;
4. `uncertainty_only` — learned iff nearest route-fit distance is no greater
   than the calibration median distance;
5. `random_rate_matched` — deterministic SHA-256 order, with exactly the
   primary route's learned count in each fold;
6. `post_acquisition_same_route` — primary decisions, but complete learned
   acquisition is charged on fallback paths;
7. `oracle_route` — statewise minimum of paired L and F, descriptive lower
   bound only;
8. SBS and VBS corpus summaries.

Hostile checks additionally require:

- a diagonal-only/marginal pairing cannot replace the 112-pair enumeration;
- route decisions are constant on attained pre-route observations;
- no test outcomes enter any fitted object;
- the primary and post-acquisition losses differ exactly by avoided extra
  feature charge on fallback paths;
- common-oracle subtraction preserves every paired sign;
- R19's same-marginals/different-joint-value (`0` versus `50`) and acquisition-
  timing reversal fixtures remain green;
- shuffled direct-relative labels cannot be promoted as a valid receipt;
- every baseline receives one and only one realized test loss per instance.

## 8. Frozen paired uncertainty and disjoint terminals

Pool the ten out-of-fold primary-minus-point-relative paired differences.
Report a deterministic 20,000-resample instance-cluster percentile bootstrap
95% interval. The RNG seed is the first 64 bits of
`SHA-256("ORION02_R21_TSP_DIRECT_RELATIVE_BOOTSTRAP_V1")`. The interval is a
finite paired uncertainty summary, not a distribution-free theorem.

Terminal predicates are evaluated in this mutually exclusive order (`tol=1e-9`):

1. `CANNOT_CHECK_TSP_DIRECT_RELATIVE_SOURCE_OR_RESOURCE` on identity, schema,
   matrix, split, cost, dependency, parser, or resource failure;
2. `C_R21_TSP_DIRECT_RELATIVE_NO_CERTIFIED_LEARNED_COVERAGE` when fewer than
   1% of test rows take the certified learned route;
3. `C_R21_TSP_DIRECT_RELATIVE_JOINT_ROUTE_VALUE` iff primary mean is at least
   5% below point-relative mean, the paired 95% upper endpoint is below zero,
   primary timeout count is no worse, empirical paired-interval coverage is at
   least 90%, and empirical sign error on certified learned routes is at most
   10%;
4. `C_R21_TSP_DIRECT_RELATIVE_STRICT_BUT_NOT_MATERIAL` when primary mean is
   strictly lower than point-relative mean but the material gate is not met;
5. `C_R21_TSP_DIRECT_RELATIVE_NULL` when the two means are equal within tol;
6. `C_R21_TSP_DIRECT_RELATIVE_ADVERSE` otherwise.

The no-coverage terminal takes precedence so a zero-use router cannot be
called positive or null.

## 9. Frozen outputs and authority boundary

Emit source byte/Git-blob/SHA-256 identities; parser and matrix audits; fold
membership digests; all 112 pair-selection tuples per fold; selected pairs;
paired interval/sign coverage; action/timeout/acquisition counts; per-arm mean,
median, p95, maximum and bootstrap interval; one out-of-fold row per instance;
all hostile-control verdicts; and one of the terminals above. Execute twice and
require byte-identical canonical JSON.

A positive result would be bounded historical out-of-fold evidence on this
pinned TSP scenario. It would not establish production value, unseen-domain
transfer, deterministic route safety, generic learned-selector superiority,
external independence, novelty, journal authority, or submission readiness.
A null/adverse/no-coverage result is permanent Round-2 evidence and sends
#1512 to the already-declared distinct Round 3 safe learned proposal ordering.

