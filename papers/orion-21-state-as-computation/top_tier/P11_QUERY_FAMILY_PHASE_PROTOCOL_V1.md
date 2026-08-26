# P11 query-family placement/optionality phase protocol V1

**Programme:** #977  
**Purpose:** attack the remaining P11 claims with a stronger access-class comparison, explicit compiler cost, query diversity and a prospective compile/cache/materialize phase diagram on non-synthetic data.

## Chronology

This protocol is frozen before the V1 runner/outcome. It does not retune or replace `P11_REAL_LEARNED_COMPILER_V1`; the previous breast-cancer negative remains authoritative.

## Dataset and query family

Use scikit-learn handwritten digits only. Raw universal state dimension is `d=64` pixels.

Freeze ten binary query responsibilities before outcomes:

`q_j(x) = 1 iff digit(x) == j`, for `j=0,...,9`.

This gives a genuine future-query family over the same source state rather than one fixed classification responsibility.

Five-fold `StratifiedKFold(shuffle=True, random_state=20261121)` over the original ten-class labels. All transformations/models are fit on training folds only.

## Query-specific learned compiler

For each query `q_j` and fold:

- fit `StandardScaler` on training source state;
- fit `SelectKBest(f_classif, k=16)` on the binary training responsibility;
- compiled state is the selected 16 standardized source coordinates;
- archive selected feature indices;
- no test label or future-query outcome is visible to compiler selection.

The selector is donor-owned feature selection, not P11 novelty.

## Access/decoder attacks

Use identical hyperparameters between universal and compiled state.

1. **LINEAR:** `LogisticRegression(C=1, solver=lbfgs, max_iter=5000)`.
2. **RBF:** `SVC(C=1, kernel=rbf, gamma=scale)` — stronger nonlinear access attack.
3. **KNN:** `KNeighborsClassifier(n_neighbors=7, weights=distance)` — nonparametric/local access attack.

Report every query/fold/model cell. No model is allowed to retune `k` or hyperparameters after seeing results.

## Quality gate

For each query/access class, compare mean compiled vs universal balanced accuracy. A query is *quality-supported* for that access class when

`compiled_mean >= universal_mean - 0.02`.

Do not require every query/access class to pass. The scientific purpose is to locate access-class and responsibility dependence. The primary placement result requires:

- at least `8/10` queries quality-supported under LINEAR;
- at least one stronger access class (RBF or KNN) with at least `8/10` quality-supported;
- all ten queries reported.

If stronger access erases or reverses the compiled-state result, that is an authoritative boundary, not a failed implementation.

## End-to-end resource vector

For every query/fold record deterministic proxies:

- compiler fit inspections: `n_train * d`;
- compiler transform inspections: `n_eval * d`;
- universal stored-state floats/example: `d`;
- compiled stored-state floats/example/query: `k`;
- LINEAR coefficient/intercept count;
- RBF support-vector count and support-vector coordinate count;
- KNN stored training-vector coordinate count;
- prediction feature touches/example: state dimension for LINEAR/KNN, support-vector-coordinate count for RBF;
- cache count and recompilation count under phase scenarios.

Hosted wall-clock time is diagnostic only.

## Prospective phase diagram

Query diversity `U` is frozen on `1..10`; deployment query horizon `H` is frozen on

`[100, 500, 1000, 2500, 5000, 10000, 25000]`.

Use expected/frozen uniform responsibility use among the first `U` query identities. Compare two policies:

### UNIVERSAL

- store one shared 64-float state per example;
- no compiler fit;
- service each query using its universal downstream access model.

### COMPILE_CACHE

- fit/cache one 16-coordinate compiler for each of `U` responsibilities;
- store `16*U` state floats per example if all compiled states are materialized;
- charge every compiler fit and transform;
- service each query from its compiled model.

### Predeclared placement predictions

1. **State-memory crossover:** `COMPILE_CACHE` uses no more stored state than universal iff `16*U <= 64`, i.e. `U <= 4`.
2. **Compiler amortization:** for LINEAR feature-touch work, compiler fit cannot be treated as free. Compute the exact horizon where accumulated service-touch savings first exceed total training-fold compiler-fit inspections. Prediction: break-even grows linearly with `U`.
3. **Optionality penalty:** when a previously unseen responsibility arrives, `COMPILE_CACHE` incurs one new compiler fit/cache; UNIVERSAL does not reconstruct source state. Query diversity therefore creates a measurable specialization tax.

These predictions are frozen algebraically before protected test accuracy is scored.

## Recovery/drift attack

At phase midpoint, introduce one new responsibility not among the initial `U` where possible. Charge:

- COMPILE_CACHE: one compiler fit + one compiled-state materialization over evaluation examples;
- UNIVERSAL: zero state reconstruction, only the already-required downstream query model.

This is a placement/optionality cost, not a claim that the universal downstream predictor is already trained for every future label.

## Endpoints

- per-query/access-class compiled-universal balanced-accuracy delta;
- quality-supported query count per access class;
- query-specific selected-feature stability;
- deterministic model/state resource vector;
- state-memory crossover accuracy against the frozen `U<=4` prediction;
- LINEAR compiler-amortization break-even horizon per `U`;
- future-query compiler/recovery cost;
- Pareto dominance/non-dominance without post-hoc scalar weights;
- deterministic replay.

## Positive terminal

`P11_QUERY_FAMILY_PHASE_V1_SUPPORTED` requires:

- leakage/conformance checks pass;
- LINEAR quality-supported on at least 8/10 responsibilities;
- at least one stronger decoder class quality-supported on at least 8/10 responsibilities;
- the exact state-memory crossover matches `U<=4`;
- compiler cost is included and every break-even horizon is reported even when outside the frozen H grid;
- future-query specialization cost is nonzero for COMPILE_CACHE and zero state-reconstruction cost for UNIVERSAL;
- no protected result is omitted;
- deterministic replay.

A positive closes bounded stronger-decoder, resource-accounting and prospective phase-diagram obligations. It does not establish open-weight agent-system substitution or a universal computational-placement law.
