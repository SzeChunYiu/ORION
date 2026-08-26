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

## Exact observed result

Workflow run `33003294882` completed successfully and executed the complete audit twice with byte-identical full JSON. The archived full result has SHA-256

`7c0778836101d5fe44b024e302c3fc0848faf5a994fc1e51b80831d82fd5e652`.

The frozen corpus contains 1,614 instances, 31 solvers, 115 raw features, ten feature steps and 513 distinct dependency-closed feature-step representations. The solver table contains 50,034 instance-algorithm measurements, of which 23,086 are `ok` and 26,948 are timeouts under the scenario convention.

The single best solver is `mphaseSATm`, with mean PAR10 `3079.8857496902106`. The virtual-best solver mean is `241.317614622057`, leaving a mean oracle gap of `2838.5681350681534` and confirming substantial portfolio decision value before feature costs are considered.

### No-feature baseline

With no acquired features, all 1,614 instances form one fibre. The exact robust action regret and total excess are both `12000`, the PAR10 ceiling. Mean total excess is `5448.314665427509`, median `582.71`, and p95 `11999.97`.

Although the fibre contains 1,614 states, its exact worst-case value is witnessed by only seven instances. This is a direct empirical instantiation of the action-regret witness-compression theorem.

### All-feature baseline

Using all ten feature steps almost eliminates action ambiguity: robust action-only regret is `11.53`. But acquisition cost is not free. Mean feature cost is `180.4930421313507`, and one instance incurs `16906.55` of recorded aggregate feature acquisition. Consequently the all-feature robust total excess is `16906.55`, *worse* than acquiring no features despite the excellent action-only representation.

This is the key negative control: optimizing prediction/identifiability or action regret alone does not optimize the operational decision objective once information acquisition is charged.

### Exact optimal static representation

Exhaustive search over all 513 dependency-closed representations selects exactly

`{Pre, lobjois}`.

Its measured statistics are:

- mean feature acquisition: `22.74003097893432`;
- maximum feature acquisition: `1712.0`;
- 1,595 representation fibres;
- maximum fibre size: 20;
- robust action-only regret: `11.529999999999998`;
- **robust total excess: `1712.0`**;
- mean total excess: `23.01433705080545`;
- median total excess: `2.08`;
- p95 total excess: `16.450000000000045`.

Relative to no features, the exact robust total excess is reduced by `10288`, from `12000` to `1712`, a ratio of `0.14266666666666666`. Relative to all features, it is reduced by `15194.55`. Mean total excess improves by `5425.300328376703` versus no features and by `157.75294299876085` versus all features.

The worst fibre contains 20 instances, yet its exact value is witnessed by only three:

1. `SAT-Race-2010-CNF/software-verification/post/zfcp-2.8-u2-nh.cnf`;
2. `SAT_Competition2009/CRAFTED/Difficult/contest05/sabharwal/grid-pebbling-sat-grid-pbl-0300.sat05-1341.sat05-1341.reshuffled-07.cnf`;
3. `SAT_Competition2011/SAT11/application/jarvisalo/smtqfbv-aigs/smtlib-qfbv-aigs-ext_con_032_008_0256-tseitin.cnf`.

The real operational certificate is therefore small even though the underlying corpus is large.

### Exact descriptive frontier

The mean-feature-cost versus robust-action-regret Pareto frontier has only four representations:

1. no features: `(0, 12000)`;
2. `Pre`: `(6.332831474597274, 11891.99)`;
3. `Basic + Pre`: `(19.0196468401487, 216.88)`;
4. `Pre + lobjois`: `(22.74003097893432, 11.53)`.

The frontier exposes a sharp phase change. `Pre` alone is cheap but leaves nearly worst-possible robust action ambiguity; adding `Basic` removes most of that ambiguity; replacing `Basic` with `lobjois` reaches the full all-feature action-regret floor at far lower acquisition cost and far lower robust total excess.

## Scientific interpretation

The primary discriminator is positive: the exact static representation `Pre + lobjois` strictly beats both preregistered extremes under the same-unit robust total-excess objective.

Three conclusions are supported on the frozen corpus:

1. **representation insufficiency is decision-relevant**: no features leave the portfolio at the PAR10 robust ceiling;
2. **more information is not monotonically better after acquisition cost**: all features minimize ambiguity but have worse robust total cost than no features because one acquisition path is extremely expensive;
3. **FiberGuard's decision-aware refinement object can identify a sparse operational representation**: two feature steps attain the all-feature robust action-regret floor while reducing robust total excess by more than an order of magnitude relative to both naive extremes.

The result is stronger than a prediction-accuracy demonstration because the target is the downstream solver action and the feature price is the benchmark's measured acquisition time, not an arbitrary regularization coefficient.

## Registered comparisons

The committed result summary records:

- no-feature global robust selector;
- all-feature-step robust selector;
- exact best dependency-closed static representation;
- single-best-solver and virtual-best-solver mean PAR10;
- the complete run's content digest;
- the mean-feature-cost versus robust-action-regret Pareto frontier;
- exact worst-fibre compressed witnesses.

The complete 513-representation table remains in the content-bound workflow artifact and is reproducible from the pinned external corpus.

## Remaining top-tier gate

This result closes the **same-corpus operational-value** question. It does not close generalization. Exact equality fibres can become very fine on continuous feature vectors, so a top-tier ML/algorithm-selection claim additionally requires a prospectively frozen train/test or leave-family-out policy in which the representation and solver-decision rule are fit without access to held-out runtimes.

The next C tranche should therefore use the scenario's registered cross-validation/family metadata where available, or a prospectively committed group split, and compare:

- no features;
- all features;
- `Pre + lobjois` frozen from this corpus-complete result;
- a training-only representation chosen from the 513-step menu;
- a standard learned algorithm-selection baseline.

The R11 corpus-complete result must not be retuned in response to held-out outcomes.

## Authority boundary

The positive result grants a corpus-complete static decision certificate. It does not establish:

- unseen-instance generalization;
- learned model accuracy;
- prevalence outside `SAT12-ALL`;
- superiority to every algorithm-selection method;
- production deployment value; or
- journal acceptance.

The adaptive answer/refine/defer controller remains a separate extension after the static generalization discriminator is frozen.

## Reproducibility terminal

The workflow fetches the exact upstream commit, verifies every registered Git blob, executes the audit twice, requires byte-identical JSON, verifies fail-closed authority flags and archives the full result. The success terminal is

`FIBERGUARD_ASLIB_SAT12_ALL_PASS`.
