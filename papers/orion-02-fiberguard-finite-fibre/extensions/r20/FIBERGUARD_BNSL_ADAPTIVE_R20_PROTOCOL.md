# FiberGuard R20 — prospectively frozen BNSL-2016 one-step adaptive discriminator

Date: 2026-08-27
Owner: #1533 under #1512
Status: DESIGN_FROZEN_BEFORE_SOLVER_OUTCOME_ACCESS

## Scientific question

On a genuinely untouched, non-SAT public algorithm-selection scenario with measured per-instance feature acquisition costs, does FiberGuard's exact finite-fibre adaptive refinement machinery achieve lower **robust total excess cost** than the exact best static feature-step representation?

This is a closed-world application-value test of the already-proved R12 deterministic adaptive theory. Generic value-of-information, finite decision-tree dynamic programming and Pareto pruning are donor-owned; no new theorem is claimed by this experiment.

## Frozen external subject

Repository: `coseal/aslib_data`

Commit: `551b22beef8df17de59286b4822ef720e0aa4d6f`

Scenario: `BNSL-2016`

Exact upstream Git blobs:

- `description.txt`: `e193c8a46d2b3b9fadfe1cb27bef16db8540bc29`
- `algorithm_runs.arff`: `33adc274ba3bd7d62875a5ee017d9b4b147e6ee8`
- `feature_values.arff`: `5d981d99a76395ad9828d0ff51f60ecb5fb7965f`
- `feature_costs.arff`: `09afa0572cc46269bfe03cfc2f008d5b95d2bf40`
- `feature_runstatus.arff`: `90e494a307c44f3978ca33c5a02e66d2fe4726f3`

The scenario metadata declares seven feature steps and eight deterministic algorithms. It supplies explicit per-instance feature-step costs and runstatus. `BNSL-2016` had no occurrence in the ORION tree when this protocol was frozen.

### Pre-freeze access boundary

Before this file was committed, the research session inspected only:

- upstream repository/scenario metadata and blob identities;
- `description.txt` to establish feature-step structure;
- `feature_costs.arff` to establish that meaningful state-dependent acquisition costs exist.

It did **not** inspect `algorithm_runs.arff` contents or `feature_values.arff` contents. No BNSL solver-performance outcome or representation fibre was known when the policy/gates below were frozen.

`MIP-2016` was considered and rejected before outcome access because its metadata exposes only one all-or-none feature step and therefore cannot discriminate adaptive acquisition.

## Aggregation convention

Use the same ASlib convention as FiberGuard R11:

1. algorithm runtime: median across repetitions;
2. algorithm runstatus: most frequent status, ties lexicographic;
3. non-`ok` algorithm runtime: PAR10 = ten times the scenario algorithm cutoff;
4. feature value: arithmetic mean across repetitions when all values are numeric; any missing observation remains explicit `?`;
5. feature-step runstatus: most frequent status, ties lexicographic;
6. feature-step cost: median across repetitions;
7. if a step has no finite recorded cost and its status is non-`ok`, charge the scenario feature cutoff; finite successful costs are never imputed or clipped.

All alternatives use the common statewise virtual-best-solver runtime `T*(x)` as oracle baseline.

## Exact representation family

A static representation is any dependency-closed set of declared feature steps. Its observed signature contains, step by step:

- step identity;
- observed step runstatus;
- every provided feature value, preserving missingness.

Every dependency-closed static set is exhaustively evaluated.

For static representation `J`, acquisition cost on state `x` is the recorded total `F_J(x)`. On each exact representation fibre `B`, one solver is chosen to minimize

`max_{x in B} [F_J(x) + T(a,x) - T*(x)]`.

The static robust value is the maximum fibre value.

## Frozen free-information base J0

`J0` is derived **only from the feature cost/runstatus tables**, not from solver outcomes or feature values:

1. enumerate every dependency-closed step set;
2. retain sets whose exact total acquisition cost is zero on every corpus instance;
3. choose the retained set with the largest number of steps;
4. tie-break lexicographically by the sorted step tuple.

If no nonempty set is globally free, `J0=empty`.

This rule is frozen now; the identity of `J0` is an outcome of the acquisition table, not a manually selected representation.

## Frozen one-step adaptive policy language

The initial observation is `phi_J0`. On each initial fibre `B`, independently, the policy may choose exactly one of:

### ACT

Choose one solver for all states in `B`, paying only `F_J0(x)`.

### REFINE(q)

For one declared step `q` not already in `J0`:

1. acquire the dependency closure `K_q = closure(J0 union {q})`;
2. pay each state's exact total acquisition cost `F_Kq(x)` (not a cellwise maximum approximation);
3. observe the exact refined signature `phi_Kq`;
4. choose one robust solver separately on each attained refined child fibre;
5. stop. No second costly refinement is allowed in R20.

The exact local value of each root choice is computed statewise and then maximized over the states in `B`. The policy chooses the lowest-valued root choice with deterministic tie-break `ACT < REFINE(step lexicographic)`.

The corpus-wide adaptive value is the maximum over initial fibres of their exact chosen local value. Mean/median/p95 realized total excess are also reported under the robust policy.

## Registered comparators

Report all of:

1. no features;
2. all feature steps;
3. `J0` act-only;
4. exact best static representation over every dependency-closed set;
5. exact best static set in the restricted family `{J0} union {closure(J0 union {q})}`;
6. R20 one-step adaptive policy;
7. per-instance oracle-one-probe lower bound that may choose the best registered root option with hidden-state knowledge (descriptive lower bound only);
8. SBS and VBS portfolio summaries.

The primary comparator is item 4, the unrestricted exact best static representation.

## Primary terminals

Let `V_adapt` be R20 robust total excess and `V_static` the exact best-static robust total excess. Let `M_adapt` and `M_static` be corresponding mean realized total excess.

- `C_R20_BNSL_ADAPTIVE_MATERIAL_VALUE` iff `V_adapt <= 0.90 * V_static` and `M_adapt <= M_static`.
- `C_R20_BNSL_ADAPTIVE_STRICT_VALUE` iff `V_adapt < V_static` but the material gate above is not met.
- `C_R20_BNSL_ADAPTIVE_NULL` iff `V_adapt == V_static` within `1e-9`.
- `C_R20_BNSL_ADAPTIVE_ADVERSE` iff `V_adapt > V_static + 1e-9`.
- `CANNOT_CHECK_BNSL_DATA_OR_RESOURCE` on source mismatch, malformed/incomplete matrices, parser failure, or resource exhaustion.

Because the adaptive language does not contain arbitrary multi-step static acquisition, `ADVERSE` is logically possible and must be retained rather than repaired.

## Hostile and null controls

The executor must verify:

- exact upstream blob identity before reading outcomes;
- complete algorithm matrix for every admitted instance;
- `J0` depends only on acquisition tables;
- ACT-only adaptive value on every initial fibre equals the `J0` static policy value;
- every refined child is a subset of its parent fibre;
- state-dependent charges are added before taking a maximum;
- restricted one-probe static policies are contained in the adaptive language only when their root choice is constant across all `J0` fibres; no stronger containment is assumed;
- no adaptive policy receives solver outcomes or hidden instance identity as an observation;
- the oracle-one-probe arm is labelled oracle and never used as an ordinary baseline.

## Authority boundary

A positive result is corpus-complete closed-world evidence that exact adaptive acquisition has operational value on this pinned BNSL scenario. It does **not** establish unseen-instance generalization, learned-selector superiority, production deployment value, generic active-feature-acquisition novelty, or journal authority.

A null/adverse result consumes FiberGuard breakthrough Round 1 and sends #1512 to its distinct Round-2 direct-relative route mechanism without retuning this protocol.
