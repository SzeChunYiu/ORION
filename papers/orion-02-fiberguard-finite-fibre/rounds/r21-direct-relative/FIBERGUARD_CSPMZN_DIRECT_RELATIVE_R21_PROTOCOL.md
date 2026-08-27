# FiberGuard R21 recovery — prospectively frozen CSP-MZN direct-relative route

Date frozen: 2026-08-27

Parent: #1512, Round 2 direct-relative/joint-route mechanism

Status at this commit: **source, rights, cost fallback, split custody, legal
profile grammar, gates, and executor are frozen before any CSP-MZN-2013
algorithm-run, feature-value, feature-cost, feature-runstatus, or CV row is
read**.

TSP-LION2015 stopped at its prospectively registered source/cost prerequisite:
21 `eax_probing` cells had missing cost under `presolved`, while the scenario
declares no numeric feature cutoff. That `CANNOT_CHECK` is permanent. It did
not fit a model, enumerate an outcome profile, or adjudicate the Round-2
mechanism. This recovery changes only the untouched subject, before accessing
its outcomes; it does not tune a result or start a different mechanism.

## Immutable permission-bearing subject

- repository: `https://github.com/coseal/aslib_data.git`;
- commit: `551b22beef8df17de59286b4822ef720e0aa4d6f`;
- scenario: `CSP-MZN-2013`, a non-SAT MiniZinc/CSP portfolio;
- licence: pinned root `README.md` blob
  `bbae808cc2f718b15b379b30ef6a9909933fc3d5` states GPLv3;
- data are retrieved and identity-checked, not vendored.

| path | Git blob | bytes |
|---|---|---:|
| `README.md` | `bbae808cc2f718b15b379b30ef6a9909933fc3d5` | 3,035 |
| `CSP-MZN-2013/readme.txt` | `55180a18d255fd01bf8c504794c85e1361e0b4de` | 2,824 |
| `CSP-MZN-2013/description.txt` | `fef9553ae42035d065325c4cf938ea77c4a55b11` | 6,476 |
| `CSP-MZN-2013/algorithm_runs.arff` | `874d8f4693b0c83bc82be55a77e4b3ef3ef5a0ea` | 3,716,780 |
| `CSP-MZN-2013/cv.arff` | `9cfeda3e75d6d6ac4aa1bfb11b1a9dabf06f658e` | 249,492 |
| `CSP-MZN-2013/feature_costs.arff` | `428ee0a211c9c35fd1962609428d586535215a4a` | 288,054 |
| `CSP-MZN-2013/feature_runstatus.arff` | `cb802dd046d9bafe21f0580cce1c70121332d828` | 267,637 |
| `CSP-MZN-2013/feature_values.arff` | `d98002d161b994d17b8155ca2e643cc29f17aec3` | 4,302,207 |

Pre-freeze access was limited to the upstream Git tree, root licence, scenario
readme, and `description.txt`. These state 4,642 CSP instances, 11 deterministic
solvers, a 1,800-second algorithm cutoff, `static` and `dynamic` feature steps,
and a numeric 900-second feature cutoff. No outcome/CV table header or row was
read. `CSP-MZN-2013` had no tracked ORION occurrence at freeze time.

## Accounting and pre-acquisition timing

Aggregate repeated solver runtime by median and runstatus by most-common value,
lexical ties. Non-`ok` becomes PAR10 = 18,000. Aggregate feature values by
median when all observations are finite; any missing value remains missing.
Aggregate step cost by median finite value and step status by most-common
value. A finite cost is always charged. If cost is missing/nonfinite and status
is non-`ok`, charge the registered 900-second feature cutoff; missing cost with
`ok` status fails closed.

The `static` step is acquired before routing and is common sunk cost. The
learned action additionally acquires `dynamic`; fallback avoids it. With the
statewise VBS runtime `C*`:

`L = cost(static,dynamic) + runtime(learned selector) - C*`

`F = cost(static) + runtime(fallback solver) - C*`

`Delta=F-L`; positive favours learned. A post-acquisition control charges
`dynamic` on fallback paths and must differ by exactly the avoided charge.

## Frozen split, models, and complete joint grammar

Use repetition 1 of upstream `cv.arff`, require folds 1..10 and one admitted
fold per instance. For outer test fold `t`, cyclically use `t+1` for independent
calibration, `t+2` for legal-pair selection, `t+3` for direct-relative fitting,
and the remaining six folds for learned-action training. All ten folds execute.

Inputs are imputed by model-training medians, scaled by model-training
median/IQR using NumPy linear quantiles (unit scale at zero IQR), and augmented
with missing indicators. Stable distance ties follow lexical instance order.
The learned selector uses `static+dynamic` and k-nearest-neighbour portfolio
selection for `k in {1,3,5,9}`: choose the solver with minimum mean training
PAR10 among neighbours, lexical ties. These are four learned profiles.

Every one of the 11 declared solvers is a fallback profile. All `4*11=44`
legal learned/fallback pairs are exhaustively evaluated per fold. A 9-nearest-
neighbour direct-relative regressor fitted on the route-fit fold uses only
`static` inputs. On pair-selection data, its point route chooses learned iff
predicted Delta is nonnegative. Select the joint pair lexicographically by:
selected-action timeout count, mean loss, p95 loss, maximum loss, mean
acquisition, learned name, fallback name. Every tuple/profile digest remains
in the receipt. Diagonal or separate marginal pairing has no authority.

## Paired interval, comparators, and controls

On the independent calibration fold, use the absolute residual
`|Delta-Delta_hat|` and split-conformal radius at
`ceil((n+1)*(1-0.10))`. The primary route chooses learned only if the lower
relative interval endpoint is nonnegative; an upper endpoint at most zero or
an interval crossing zero routes fallback. This is marginal exchangeability
authority, never deterministic/pathwise or shifted-domain safety.

Registered arms, all using the fold-selected legal pair, are: always fallback,
always learned, point-relative (primary strongest information-matched
non-oracle comparator), distance-only uncertainty route, deterministic
rate-matched random route, post-acquisition same route, statewise oracle route,
and corpus SBS/VBS summaries.

Hostile gates require complete Cartesian enumeration, pre-route measurability,
no test leakage, exact timing identity, common-oracle sign preservation, one
loss per test instance/arm, shuffled-label nonauthority, and unchanged R19
fixtures: full legal-pair value 0 versus diagonal-only 50, and pre/post timing
values 5 versus 10.

## Disjoint outcome gates

Use the same frozen 20,000-resample instance-cluster paired bootstrap as the
TSP protocol, with seed text
`ORION02_R21_CSPMZN_DIRECT_RELATIVE_BOOTSTRAP_V1`. Terminals, in precedence
order, are:

1. `CANNOT_CHECK_CSPMZN_DIRECT_RELATIVE_SOURCE_OR_RESOURCE` for source,
   schema, matrix, split, cost, parser, or resource failure;
2. `C_R21_CSPMZN_DIRECT_RELATIVE_NO_CERTIFIED_LEARNED_COVERAGE` below 1%
   certified learned test coverage;
3. `C_R21_CSPMZN_DIRECT_RELATIVE_JOINT_ROUTE_VALUE` when primary mean is at
   least 5% below point-relative, paired 95% upper endpoint is below zero,
   timeouts are no worse, empirical interval coverage is at least 90%, and
   certified-learned sign error is at most 10%;
4. `C_R21_CSPMZN_DIRECT_RELATIVE_STRICT_BUT_NOT_MATERIAL` for a strict mean
   improvement without every material gate;
5. `C_R21_CSPMZN_DIRECT_RELATIVE_NULL` for equality within `1e-9`;
6. `C_R21_CSPMZN_DIRECT_RELATIVE_ADVERSE` otherwise.

Execute twice byte-identically and bind source SHA-256, every fold, every legal
pair, every out-of-fold row, controls, and authority fields. Any positive result
is bounded historical out-of-fold evidence on the pinned subject. It is not
production value, deterministic safety, unseen-domain transfer, generic
selector superiority, external independence, novelty, journal authority, or
submission authorization. Null/adverse/no-coverage is permanent Round-2
evidence and triggers the predeclared distinct Round 3.

