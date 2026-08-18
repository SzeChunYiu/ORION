# P7 prospective evaluation V1 — open-world epistemic atlas benchmark

**Candidate:** Epistemic Navigation in Open Worlds  
**Status:** protocol draft, **not frozen / not result-bearing**  
**Owners:** #338, #353; donor constraints from #337/#352  
**Rule:** representation change is rewarded only when required by the hidden task structure; unnecessary reframing and useless breadth are explicit errors.

## 1. Research question

Does explicit navigation over an epistemic atlas—orientation, partial observation, chart/objective change, support transport/reopening and fail-closed stopping—produce correct decisions on tasks that cannot be faithfully handled as navigation inside one fixed chart, while reducing to strong fixed-chart behavior on negative controls?

## 2. System/baseline classes

### B0 — fixed-chart graph search
Deterministic BFS/shortest-path or equivalent exact fixed-chart baseline on symbolic graph families.

### B1 — iterative informed fixed-chart navigator
A Search-on-Graph-style adapter where feasible: local observation and iterative route choice, but no chart/objective transformation.

### B2 — belief-space / information-gathering policy
POMDP/value-of-information style baseline on families with explicit partial-observation probabilities or finite belief sets.

### B3 — representation/model-change baseline
Planning abstraction/world-model/goal-evolution donor adapter appropriate to the family, but without P7's explicit support/closure transport gate.

### B4 — P1+P2 composition
Native ORION reframe responsibility plus route/task stopping/coverage, using exact fixtures once available.

### P7 — atlas navigator
Tracks active chart, orientation, routes, obligations, coverage/censoring, partial maps, support transport, reopen/`CANNOT_CHECK` and stopping authority.

A baseline may be `CANNOT_CHECK` if no faithful adapter exists; the reason must be recorded prospectively.

## 3. Exact-ground-truth benchmark families

### F1 — hidden useful branch in fixed chart
A goal is reachable without representation change but requires exploration beyond a deceptive local branch.

**Purpose:** fixed-chart control; reframe should not be necessary.

### F2 — initial orientation / scope revelation
The initial chart is partially opaque: route/action meaning is not defined until a scope/ontology-revelation action occurs.

**Ground truth:** ordinary route ranking before orientation is invalid or under-specified.

### F3 — unknown coverage with extension ambiguity
Visible histories have paired admissible completions differing on mandatory completion.

**Ground truth:** history-only `TASK_STOP` is unauthorized.

### F4 — certificate-free but non-ambiguous control
No syntactic closure-certificate object is present, but the frozen admissible class has only one completion under another structural constraint.

**Ground truth:** do not infer ambiguity from certificate absence by definition.

### F5 — censored route
An unavailable route retains a mandatory unresolved obligation while all executed routes are locally stopped.

**Ground truth:** route stop may hold; task stop does not.

### F6 — deceptive route diversity
Multiple nominal routes share a common critical failure source but return different visible outputs.

**Ground truth:** observed output diversity does not establish structural route independence.

### F7 — topology/ontology change required
No solution state is reachable in the initial representation, but an authorized reframe produces a chart with a reachable solution.

**Ground truth:** chart change is required.

### F8 — unnecessary reframe negative control
The initial chart already contains a valid route to the goal.

**Ground truth:** reframing adds cost/risk and should not be rewarded.

### F9 — partial support transport
A prior closed obligation depends on support objects only partly mapped into the new chart.

**Ground truth:** prior closure reopens or becomes `CANNOT_CHECK`.

### F10 — evidence survives, closure does not
Content-bound evidence remains semantically valid after an objective change, but the old closure scope does not satisfy the transformed objective.

**Ground truth:** retain evidence; reopen closure.

### F11 — world-model revision without chart change
Transition probabilities/model parameters change while state vocabulary and obligation semantics remain fixed.

**Ground truth:** treat as intra-chart model revision; do not force an inter-chart reframe merely because the world model changed.

### F12 — exploration-concentration trap
Many cheap actions elaborate one local semantic region while one structurally distinct route reveals a new relevant region.

**Ground truth:** useful breadth is measured by new relevant structural regions/obligations, not raw route/query count.

### F13 — harmful breadth negative control
Structurally diverse routes exist but all additional regions are irrelevant after a valid closure/discharge condition.

**Ground truth:** do not maximize breadth for its own sake.

## 4. Non-retrieval transfer domains

At least two are required for a strong P7 paper claim:

1. **symbolic scientific design** — representation/objective transformation changes reachable designs;
2. **dynamic ontology/workflow diagnosis** — a changed state/ontology definition alters reachable diagnoses or interventions.

Optional third domain:

3. **goal-evolving optimization** — SAGA-style objective change with explicit evidence/closure transport accounting.

Literature retrieval remains useful but does not count as the sole P7 transfer result because P2 owns that domain.

## 5. Instance schema

Every instance serializes:

```text
instance_id
family
version/exhaustive_index/seed
chart_set
active_chart
nodes/relations/labels
route definitions + critical assumption signatures
coverage/censoring contracts
orientation state
obligations/objectives + satisfaction semantics
visible observation interface
hidden world completion(s)
partial chart/objective maps
support sets for certified obligations
evidence identities
budget/cost model
allowed reframe actions + authority requirements
ground-truth task-stop status
ground-truth transport/reopen decisions
negative-control flags
```

## 6. Primary metrics

### Task/closure correctness
- root-task success;
- premature `TASK_STOP` rate;
- unnecessary non-stop/refusal after valid closure;
- calibrated `CANNOT_CHECK`.

### Navigation
- relevant frontier discovery;
- structural route-independence error;
- dead-end recovery/revisit correctness;
- useful structural breadth;
- redundant local elaboration.

### Reframe/transport
- required-reframe success;
- unnecessary-reframe rate;
- support-transport false-positive rate;
- unnecessary reopening rate;
- evidence-retention correctness after chart/objective change;
- intra-chart vs inter-chart classification correctness.

### Resource
- actions/queries;
- chart transformations;
- cost/time under deterministic simulator accounting.

## 7. Primary hypotheses

### H1 — fixed-chart conservativity
On F1/F8/F11/F13, P7 should not improve correctness by gratuitous reframing; it should match strong fixed-chart/donor behavior and report any overhead.

### H2 — extension-aware stopping
On F3/F5, P7 avoids unauthorized global stopping while preserving local resource-stop decisions.

### H3 — support/closure transport
On F9/F10, P7 makes the exact retain-evidence/reopen-closure decision more reliably than a representation-change baseline that transports state without explicit support/obligation semantics.

### H4 — representation-required transfer
On F7 and at least one non-retrieval domain, atlas-enabled navigation succeeds on pre-frozen instances where every admissible fixed-chart policy lacks a solution path.

### H5 — breadth calibration
On F12/F13, P7 expands exploration when structurally useful and avoids useless dispersion.

A separate P7 paper requires H3 or a comparably strong cross-chart result plus non-retrieval transfer. H4 alone is too close to established representation-change expressivity.

## 8. Benchmark construction discipline

- hidden topology/objective/support labels are generated/frozen before policy execution;
- paired ambiguous completions share identical visible histories by construction;
- chart maps and support obligations are explicit machine-readable objects;
- no benchmark instance is removed because a strong donor baseline solves it;
- negative controls remain in the headline table;
- each family reports separately before any aggregate;
- protocol changes after result visibility create a new benchmark version and new prospective run.

## 9. Statistics

Use exhaustive counts for small symbolic families. For sampled larger generators, freeze seeds/distribution and report intervals by family. Do not use one pooled success number to hide stop/reframe/transport tradeoffs.

## 10. Promotion/failure criteria

### Supports separate P7 candidate
- distinct cross-chart support/closure transport result beyond P1+P2 and donor baselines;
- at least one non-retrieval exact-ground-truth transfer family;
- low unnecessary-reframe rate on negative controls;
- no novelty dependence on generic graph search, replanning, goal evolution or representation learning.

### Merge/strike pressure
- P1+P2 or a planning abstraction/world-model donor reproduces all atlas decisions;
- only benefit is greater search breadth or more frequent reframing;
- no evidence/closure transport discriminator remains;
- positive results occur only in retrieval/P2-like tasks.

## 11. Current result authority

`NO_RESULT`. This file defines a prospective evaluation only.