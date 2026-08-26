# FiberGuard R11 — exact decision-value discriminator on ASlib SAT12-ALL

## Scientific question

The earlier FiberGuard results prove that a lossy representation can hide target variation, and the R10 action-regret extension converts that ambiguity into a consequential finite-action decision quantity. The remaining application question is operational: **when feature acquisition and solver runtime are charged in the same physical unit, can a certified representation restriction reduce worst-case solver-selection excess cost after paying for the representation itself?**

This tranche answers that question on one frozen public algorithm-selection scenario. It is corpus-complete for the pinned scenario and does not claim unseen-instance generalization or learned-selector performance.

## Frozen external corpus

Repository: `coseal/aslib_data`

Commit: `551b22beef8df17de59286b4822ef720e0aa4d6f`

Scenario: `SAT12-ALL`

The audit content-binds the following upstream Git blobs before reading any outcome:

- `description.txt`: `2c3662ac80c9cc4eba2857c2d9a69209cb200b94`;
- `algorithm_runs.arff`: `4e27dcc3c40c76e8c754a66d465b156731a85080`;
- `feature_values.arff`: `a0da43a740da5faf28dae1892ecdcef42cb53f61`;
- `feature_costs.arff`: `4b0e5685712363ebb50d0dc5bd8e7c9532a6b2ea`;
- `feature_runstatus.arff`: `cfec4e2bf2d48b5868c40bd521be3a914311c0fe`.

The scenario declares a 1200-second algorithm cutoff and ten feature steps with dependencies. It contains explicit per-instance algorithm runtimes and explicit per-instance feature-step acquisition times, so the application does **not** require an arbitrary exchange rate between information and decision quality.

## Aggregation convention

Repeated observations follow the published ASlibScenario convention:

1. algorithm runtime: median across repetitions;
2. algorithm runstatus: most frequent status;
3. non-`ok` runtime: PAR10, i.e. ten times the cutoff;
4. feature value: mean across repetitions;
5. feature-step runstatus: most frequent status;
6. feature-step cost: median across repetitions.

Ties in status frequency are broken lexicographically only to make the frozen implementation deterministic.

## Exact representation family

Let the scenario feature steps be `S_1,...,S_p` with their declared dependency relation. A representation is any dependency-closed subset `J` of steps. For instance `x`, `phi_J(x)` contains the observed step runstatus and every feature value provided by the selected steps. Missingness is kept as an explicit symbol rather than imputed away.

Every dependency-closed subset is enumerated. No feature subset is selected after seeing its result and no stochastic search is used.

## Same-unit robust action value

Let `A` be the frozen SAT solver portfolio and let `T(a,x)` be the aggregated PAR10 runtime. Define the statewise oracle

`T*(x) = min_a T(a,x)`.

Let `F_J(x)` be the measured acquisition time of representation `J` on `x`. For a representation fibre `B`, one solver must be selected for the whole fibre. Its exact robust **total excess cost** is

`V_J(B) = min_{a in A} max_{x in B} [ F_J(x) + T(a,x) - T*(x) ]`.

The corpus-wide robust value is

`V_J = max_B V_J(B)`.

All terms are in the scenario's runtime unit and use one common statewise oracle baseline. This directly resolves the earlier Bellman/additive-baseline criticism: no absolute defer cost is mixed with regret and no post-hoc scalarization is introduced.

The audit also reports action-only regret by setting `F_J=0`, plus mean/median/p95 realized total excess under the robust fibre policy.

### Proposition — exact static optimum

On a finite frozen corpus and a finite dependency-closed feature-step menu, exhaustive evaluation of all `J` returns the exact robust static optimum `min_J V_J`.

This is elementary but operationally important: the result is not a learned feature selector or heuristic search over representations.

### Proposition — constant-size worst-fibre receipt

For `m=|A|` solvers, the exact value of any deterministic worst fibre is witnessed by at most `m` instances. Choose, for each solver, one state attaining its fibre-wise total excess maximum; the minimum over solvers on this witness set equals the full-fibre value. The executable audit materializes and checks this compressed receipt for every representation's worst fibre.

This instantiates the R10 action-regret witness-compression theorem on a real solver portfolio.

## Registered comparisons

The result record contains:

- no-feature global robust selector;
- all-feature-step robust selector;
- exact best dependency-closed static representation;
- single-best-solver mean PAR10;
- virtual-best-solver mean PAR10;
- the complete representation table;
- the mean-feature-cost versus robust-action-regret Pareto frontier;
- exact worst-fibre compressed witnesses.

The primary discriminator is **worst-case total excess after feature cost**. The mean metrics are secondary descriptive outcomes.

## Interpretation gates

A positive application result requires a strict reduction in robust total excess over both the no-feature and all-feature baselines on the frozen corpus. A null result is scientifically meaningful: it shows that representation ambiguity or solver diversity alone does not imply that feature acquisition has operational value.

Even a positive result grants only a corpus-complete static decision certificate. It does not establish:

- unseen-instance generalization;
- learned model accuracy;
- prevalence outside `SAT12-ALL`;
- superiority to every algorithm-selection method;
- production deployment value; or
- journal acceptance.

The adaptive answer/refine/defer controller remains a separate next step after the static same-unit discriminator is frozen.

## Reproducibility terminal

The workflow must fetch the exact upstream commit, verify every registered Git blob, execute the audit twice, require byte-identical JSON, and archive the result. The only success terminal is

`FIBERGUARD_ASLIB_SAT12_ALL_PASS`.
