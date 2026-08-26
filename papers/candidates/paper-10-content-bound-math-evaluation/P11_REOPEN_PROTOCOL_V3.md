# ORION-ORION-21 reopen protocol V3 — content-bound longitudinal evaluation and native proof-mechanism transfer

**Status:** prospective reopen protocol; historical ORION-20/ORION-21 bytes and terminals remain immutable.  
**Date:** 2026-08-20.  
**Paper identity:** ORION-ORION-21, Content-Bound Mathematical Evaluation (#471).  
**Historical source directory:** this directory retains its original `paper-10-*` path by preservation policy.

## 1. Why ORION-21 must reopen around a new residual

The historical technical note already established useful but bounded facts:

- the exact frozen Mathlib corpus identity;
- the V2 parser contamination and its explicit invalidation;
- corrected V2.1 coarse recurrence;
- exact native Lean receipts for eight prospectively selected files plus a planted-invalid control;
- mutation-sensitive receipt binding;
- the separation of source identity, native acceptance, statement faithfulness and scientific authority.

It also correctly concluded that **coarse source recurrence is not reusable tactic discovery or proof utility**, and that content-bound benchmark packaging/native checking are not standalone novelty.

ORION-21 should therefore not be “rescued” by rewriting the old result. A standalone reopen needs a new prospective discriminator that simultaneously satisfies the existing reopen triggers:

1. native proof-state/tactic/dependency representation;
2. TacMiner-class or stronger structural proof baseline;
3. downstream proof utility under a fixed prover loop;
4. multiple prospectively frozen later Mathlib revisions;
5. a residual not already owned by ORION-14/ORION-18/ORION-19/ORION-20 or current proof-mining/version-robustness work.

## 2. Current prior-work pressure

The final donor pass must structurally absorb at least:

- **LeanDojo / LeanDojo v2** — native repository tracing with proof states, tactics, premises and dependencies; source text is not a native proof trace;
- **TacMiner** (`arXiv:2503.24036`) — tactic dependence graphs, reusable tactic discovery and downstream utility/compression; source n-grams cannot be promoted over this baseline;
- **LeanSearch v2** (`arXiv:2605.13137`) and current premise/dependency retrieval systems — proof utility must be measured in a fixed downstream prover;
- **Formal Conjectures** (`arXiv:2605.13171`) — immutable benchmark/version discipline;
- **VeriSoftBench** (`arXiv:2602.18307`) — fixed repository context, realistic dependencies and repository-scale transfer;
- **Faults in Our Formal Benchmarking** (`arXiv:2606.29493`) — benchmark defects, harness drift, version drift and fork proliferation as first-class threats;
- **Lean Refactor** (`arXiv:2605.20244`) — version-aware proof refactoring and empirical zero-shot transfer across later Lean/Mathlib releases;
- current semantic-faithfulness evaluations — compilation/native acceptance is not statement meaning.

After this pressure, neither “version robustness” nor “proof-pattern mining” alone is a ORION-21 residual. The candidate residual below is their **measurement-science composition**: content-bound longitudinal comparability plus native-mechanism utility attribution.

## 3. Candidate strongest thesis

Freeze only after the donor and pilot rounds:

> Longitudinal Lean evaluation becomes scientifically interpretable when every task and result is bound to exact statement/source/dependency/toolchain identity and when proof mechanisms are evaluated from native proof-state/dependency traces rather than source-order proxies. Under this discipline, ORION-21 can distinguish genuine prover/mechanism transfer from benchmark revision drift and test whether learned proof abstractions retain downstream utility across module and repository revisions.

A stronger empirical form is allowed only if the protected experiment supports it:

> Native proof mechanisms learned at one frozen revision improve fixed-budget proof search on held-out modules and retain a measurable fraction of that advantage across later content-bound revisions, while task-id-only evaluation materially misattributes some score changes caused by benchmark/environment drift.

This is a target, not a present result.

## 4. Core object — `ContentBoundProofTask.v3`

Every longitudinal task instance must bind at least:

- logical task lineage id;
- repository URL and branch/tag context;
- exact Git revision;
- Lean version/toolchain;
- dependency manifest digest;
- source path and source-byte digest;
- theorem/statement span and normalized statement digest;
- imported environment/dependency-closure digest or reproducible closure manifest;
- native proof-state/expression representation version;
- allowed tactics/tools/search budget;
- candidate proof/attempt digest;
- verifier command/runtime identity;
- exit/acceptance receipt;
- statement-faithfulness/equivalence status as a separate coordinate;
- provenance linking the same logical task across revisions;
- explicit `NOT_COMPARABLE` reason when a content-bound pair cannot support a longitudinal score comparison.

A common string task id is never sufficient evidence that two revision instances are the same evaluation object.

## 5. Experiment A — longitudinal benchmark comparability audit

### 5.1 Question

When a Lean benchmark or repository evolves, how much apparent prover progress/regression is caused by:

1. genuine prover behavior change;
2. statement/formalization change;
3. dependency/API change;
4. toolchain/elaborator/tactic change;
5. evaluation-harness change;
6. task addition/removal/fork drift?

### 5.2 Revision freeze

Freeze one source revision `R0` and at least four later immutable revisions `R1...R4` **before result-bearing execution**. Prefer a preregistered calendar/commit-distance rule rather than hand-picking revisions with favorable results.

For Mathlib-coupled experiments, each revision uses its own exact declared compatible Lean toolchain and dependency manifest. Do not manually force a Mathlib snapshot onto an incompatible toolchain and call resulting breakage “proof transfer.”

Add at least one external Lean repository family if lineage can be established cleanly. A cross-repository generality claim requires >= 3 repository families.

### 5.3 Pairing and comparability states

For every logical task lineage across adjacent and longer revision gaps, compute a protected disposition:

- `EXACT_SAME_STATEMENT_ENV_COMPATIBLE`;
- `STATEMENT_EQUIVALENT_ENV_CHANGED`;
- `STATEMENT_CHANGED_EQUIVALENCE_SUPPORTED`;
- `STATEMENT_CHANGED_EQUIVALENCE_UNRESOLVED`;
- `DEPENDENCY/API_DRIFT`;
- `TOOLCHAIN/HARNESS_DRIFT`;
- `REMOVED_OR_SPLIT`;
- `NEW_TASK`;
- `NOT_COMPARABLE`.

Statement equivalence may use exact Lean equivalence witnesses where available; otherwise it remains `UNRESOLVED` or requires external semantic adjudication. Native compilation alone cannot promote equivalence.

### 5.4 Fixed-prover replay

Run frozen prover configurations on every admissible snapshot with matched declared budgets. At minimum compare:

- a fixed deterministic tactic/search baseline;
- a fixed retrieval-augmented Lean prover;
- a strong contemporary theorem-proving agent where exact version binding is feasible;
- the ORION-21 native-mechanism augmented prover from Experiment B.

Do not update model weights or prompts after observing later-revision protected outcomes.

### 5.5 Primary metrics

- **naive vs content-bound score difference** by revision;
- **comparability retention:** fraction of task lineages still valid for direct paired comparison;
- **false-progress / false-regression attribution rate:** score changes that disappear or change interpretation after content-bound filtering/decomposition;
- **leaderboard/ranking stability** under naive task-id versus content-bound paired evaluation;
- **drift cause distribution** by statement, dependency/API, toolchain/harness, and solver behavior;
- exact replay success and receipt determinism.

A high-impact positive would be a measurable, reproducible gap between naive “same task id” evaluation and content-bound longitudinal conclusions. If the gap is negligible, the positive scientific result is a bounded robustness finding rather than a fabricated drift problem.

## 6. Experiment B — native proof-mechanism transfer

### 6.1 Question

Does the corrected historical recurrence signal correspond to any **native structural mechanism with downstream proof utility**, and does that utility survive module/revision shifts?

### 6.2 Native trace corpus

At `R0`, extract a substantially larger trace corpus using a native repository tracer (LeanDojo-class or equivalent) with:

- proof states before/after tactics;
- tactics/actions;
- premises/dependencies;
- theorem/file/module lineage;
- exact source/runtime identity;
- failure/unknown extraction states.

Planning target before power/compute freeze:

- >= 10,000 successfully traced theorem proofs where licensing/runtime permits;
- broad top-module coverage;
- source/file/module holdouts;
- a whole-repository or external-project holdout if feasible;
- no later-revision protected proof traces used for training/tuning.

The exact final counts follow an outcome-blind availability/power rule, not a favorable-result rule.

### 6.3 Representations/baselines

Compare the same training/evaluation identities across:

1. historical coarse source-family Markov baseline;
2. source-token/action sequence model with equivalent visible information;
3. proof-state next-action model;
4. dependency-aware sequence/graph model;
5. **TacMiner-class tactic-dependence graph mining**;
6. premise/dependency retrieval baseline;
7. simple reusable macro/library baseline;
8. ORION-21 candidate content-bound native-mechanism representation;
9. ablations removing state, dependency edges, revision metadata or content binding.

If a donor architecture wins, absorb it; ORION-21 can still own the longitudinal measurement design if that residual survives.

### 6.4 Fixed downstream prover loop

The primary utility test inserts each representation/mechanism into the **same frozen proof-search loop**. Keep proposal model, search budget, timeout, premise access and native verifier fixed wherever the baseline mapping permits.

Primary outcomes:

- theorem proof success rate;
- paired success difference over fixed prover without learned mechanisms;
- proof-search node/evaluation count;
- wall time and token/model cost;
- proof length/compression only as secondary evidence;
- macro/mechanism invocation precision and useful-hit rate;
- invalid/failed mechanism application rate.

High n-gram or graph recurrence without downstream success remains descriptive only.

## 7. Experiment C — revision-retention of learned proof mechanisms

Train/mine mechanisms only from `R0`. Freeze them. Then evaluate the exact frozen mechanism set at `R1...R4` without rematerializing it from later proofs.

For task lineages judged longitudinally comparable, report:

- `lift(Ri) = success_augmented(Ri) - success_fixed(Ri)`;
- **retention ratio** `lift(Ri) / lift(R0)` with uncertainty where the denominator is stable;
- survival of individual mechanisms/macros;
- invalidation reason when a mechanism fails: renamed/moved premise, changed precondition/state shape, API/dependency drift, elaboration/toolchain drift, or genuinely nontransferable tactic logic;
- repair cost if a version adapter is allowed in a separately registered arm.

Compare against:

- source-sequence patterns;
- TacMiner-class mechanisms;
- version-aware retrieval/refactoring strategies where task semantics align;
- no-mechanism fixed prover.

A result that only survives because later revision metadata is used to retrieve revised proof strategies is **adaptation**, not zero-shot mechanism transfer; keep those arms separate.

## 8. Experiment D — external repository transfer

If A–C support a Mathlib result, test whether the evaluation discipline and/or native mechanisms transfer to repository-scale formal verification.

Candidate families include fixed-commit Lean repositories such as VeriSoftBench-style projects or other redistributable Lean developments with known history.

Freeze:

- project revision lineage;
- exact compatible toolchain per revision;
- train/tune/test project separation;
- dependency closures;
- no test-project traces in mechanism mining.

The widest paper claim requires replication outside one Mathlib lineage. Otherwise the conclusion stays Mathlib-specific.

## 9. Hostile controls

The final protocol must include at least:

- same task id, changed statement;
- same statement text, changed imports/dependency closure;
- same bytes, changed toolchain;
- same accepted proof, altered statement digest;
- stale success receipt replayed at a new revision;
- renamed/moved premise with equivalent content;
- API-compatible superficial change versus semantic statement change;
- proof that compiles using an unintended axiom/unsafe shortcut where the benchmark policy forbids it;
- harness that silently drops failed tasks;
- task lineage split/merge;
- later-revision trace leakage into `R0` mechanism training;
- source sequence recurrence that vanishes under proof-state/dependency analysis;
- native structural pattern that recurs but yields no downstream prover benefit.

Every control has a protected expected disposition and must be retained even if it defeats the preferred claim.

## 10. Statistics

Predeclare:

- paired task-level differences for solver success;
- clustered/bootstrap intervals over theorem/module/repository where appropriate;
- practical margin for downstream proof-success lift;
- practical margin for cross-revision retention;
- exact handling of disappeared/new/non-comparable tasks;
- multiplicity across revisions/baselines;
- no denominator changes after outcome access;
- tail reporting for catastrophic version-specific failures;
- compute-budget matching and sensitivity curves.

Do not report a pooled “all revisions” score that mixes incompatible task populations without explicit weighting and comparability accounting.

## 11. Figures and tables designed to make the contribution visually obvious

### ORION-21-A — longitudinal score decomposition

For each revision, show naive score change decomposed into:

- comparable-task solver behavior;
- statement/formalization drift;
- dependency/API drift;
- toolchain/harness drift;
- task population change.

A waterfall or stacked decomposition makes “benchmark changed” versus “prover changed” immediately visible.

### ORION-21-B — naive vs content-bound leaderboard

Two side-by-side rankings or rank trajectories across revisions. Highlight any ranking inversions attributable to comparability drift. If none occur, report the stability result.

### ORION-21-C — revision × module utility heatmap

Cells show native-mechanism proof-success lift over fixed prover. This exposes whether utility is concentrated in a few modules or survives broad transfer.

### ORION-21-D — transfer-retention curve

X = revision distance/time; Y = retained mechanism lift and raw mechanism survival. Include source-sequence and TacMiner-class baselines.

### ORION-21-E — source recurrence vs native utility scatter

Each candidate pattern/mechanism is a point. X = recurrence/coverage, Y = downstream proof-search utility. This directly tests the historical temptation to equate recurrence with useful tactics.

### ORION-21-F — failure-attribution Sankey

Mechanism/proof failures flow into statement drift, dependency/API drift, toolchain drift, nontransferable mechanism, search failure, or `UNRESOLVED`.

### ORION-21-G — receipt mutation matrix

Rows = source/statement/revision/dependency/toolchain/attempt mutation; columns = naive task-id store versus content-bound checker; show which substitutions are detected.

### Required tables

1. exact revision/repository/toolchain manifest;
2. task-lineage comparability counts;
3. fixed-prover and mechanism-augmented success with uncertainty/cost;
4. cross-revision retention per baseline;
5. all non-comparable/null/harmful cases and reasons;
6. nearest-work adoption/claim-strike matrix.

## 12. Negative-result-to-research rule

Historical and new adverse results remain immutable. ORION-21 converts them into new research only through a new frozen discriminator.

- **native mechanisms do not outperform source baselines:** investigate whether the historical recurrence is representationally sufficient, or whether the mechanism definition/search loop is wrong; do not call recurrence “utility.”
- **TacMiner-class baseline matches ORION-21:** absorb TacMiner and narrow ORION-21 to longitudinal content-bound measurement if that part remains useful.
- **cross-revision lift collapses:** localize drift causes and test version adapters in a new registered arm; the collapse itself becomes a maintenance/mechanism-survival result.
- **naive and content-bound rankings are identical:** retain the robustness result; do not manufacture score drift.
- **statement equivalence cannot be decided:** mark the lineage `UNRESOLVED/NOT_COMPARABLE` and measure the resulting coverage cost.
- **external repositories fail to replicate:** publish/narrow the Mathlib scope and identify which repository/dependency assumptions failed.

The scientific record stays truthful while every failure produces an explicit next ORION research object.

## 13. Widest claim ladder

### Rung 1 — identity discipline

> Content-bound receipts detect revision/source/statement/attempt substitutions that task-id-only evaluation cannot.

Already supported historically on a narrow control set.

### Rung 2 — longitudinal comparability

> Content-bound lineage analysis materially changes or decomposes conclusions from multi-revision Lean evaluation.

Requires Experiment A.

### Rung 3 — native mechanism utility

> Native proof-state/dependency mechanisms provide downstream proof-search value beyond source-order recurrence and strong structural baselines.

Requires Experiment B.

### Rung 4 — revision robustness

> A frozen native mechanism library retains measurable utility across prospectively frozen later revisions after content-bound comparability filtering.

Requires Experiment C.

### Rung 5 — cross-repository measurement result

> The same discipline distinguishes solver progress from benchmark/environment drift and preserves useful mechanism transfer across heterogeneous Lean repositories.

Requires Experiment D.

### Rung 6 — standalone flagship target

> ORION-21 establishes **content-bound longitudinal evaluation** as a practical measurement layer for evolving formal-proof systems: it binds claims to exact formal environments, separates benchmark drift from solver change, and quantifies the survival and utility of native proof mechanisms across revisions and repositories.

Rung 6 is the strongest defensible target. It is not granted by the historical note.

## 14. Freeze checklist

Before result-bearing execution:

- [ ] fresh primary-source saturation including Lean Refactor/version-drift work;
- [ ] exact residual/claim wording frozen;
- [ ] `R0...R4` revisions selected by outcome-blind rule;
- [ ] exact compatible Lean/toolchain/dependency manifests bound;
- [ ] task-lineage pairing algorithm and comparability rubric frozen;
- [ ] statement-equivalence authority/rules frozen;
- [ ] native trace extractor version/hash frozen;
- [ ] training/tuning/test and later-revision exclusions frozen;
- [ ] TacMiner-class and other strong baselines implemented/configured;
- [ ] downstream prover loop and budgets frozen;
- [ ] statistics/margins/multiplicity/denominators frozen;
- [ ] raw archive requires invalid/null/non-comparable cases;
- [ ] independent #283 replay plan frozen;
- [ ] ORION-14/ORION-18 authority boundary and ORION-19/ORION-20 ownership rechecked.

## 15. Standalone close condition

ORION-21 becomes a standalone paper only if at least one **new prospective residual** survives strong baselines and external verification. The preferred close package is:

- Experiment A supported longitudinal comparability result;
- Experiment B native-mechanism downstream utility over strong baselines;
- Experiment C prospective revision-retention evidence;
- ideally Experiment D external repository replication;
- exact raw receipts/manifests and reproducible figures;
- all adverse/null/non-comparable cases retained;
- fresh novelty/ownership review immediately before submission.

If the native-mechanism residual disappears but the longitudinal measurement result is strong, ORION-21 may still become a narrower evaluation/measurement paper. If both disappear, retain the current technical-note terminal rather than inflating publication count.