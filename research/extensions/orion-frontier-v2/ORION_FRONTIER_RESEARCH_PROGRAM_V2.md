# ORION Frontier Research Program V2

Status: ACTIVE PROGRAMME / CLAIMS PROSPECTIVE UNLESS RECEIPTED
Frozen programme start: 2026-08-20
Base: main after bounded P9 and P10 merge (`6460410595a14cf9894c9acd450ab2b649a3b858`).

## Programme thesis

P9 established that information-equivalent coordinate systems can have radically different accessibility to restricted learners. P10 established broad source-level recurrence in formal proof behavior and froze a native-state escalation. The next programme does **not** merely repeat that "representation matters." It asks whether representation itself is a controllable computational resource.

The ambitious programme hypothesis is:

> An intelligent system can trade computation among **state compilation**, **model capacity**, **search/inference**, and **verification**. The optimal system need not reason over a fixed representation; it can actively construct a task-sufficient representation whose cost is justified by the downstream computation it eliminates.

This is intentionally a high claim ceiling. Each paper/rung below has independent hostile gates and can fail without collapsing the programme.

## Frontier A — P11: Query-Conditioned State Compilation

Question: how much representational dimension can be eliminated when the current query/goal is allowed to participate in state construction?

Core theorem target: for the size-s parity query family over d binary variables, every fixed query-agnostic representation supporting exact linear readout of every query has dimension at least `binom(d,s)`, whereas a query-conditioned compiler needs one scalar coordinate per active query.

Empirical target: under fresh seeds, a one-coordinate compiled representation should retain exact task accuracy while a universal query-agnostic feature bank pays a large finite-sample nuisance tax. The theorem—not the empirical tax—is the primary structural result.

Boundary: this is a lower bound for fixed representations plus linear readouts, not arbitrary nonlinear systems.

## Frontier B — P12: Accessibility Work

Existing predictive V-information already formalizes that equal Shannon information can differ in usable information under a restricted predictive family. ORION therefore does not claim ownership of that primitive fact.

New operational target: define and measure the **cost of creating usable information**.

For representation R, target Y, predictive family V, quality q, and compiler family C, estimate an accessibility-work profile:

`W(R -> Y; V, q) = min_{c in C} [cost(c) + min downstream_cost(f)]`

subject to `f(c(R))` achieving quality q.

The programme will separately account for:
- preprocessing/compiler operations;
- representation size / memory;
- model parameters or interaction degree;
- inference/search tokens;
- verifier/tool calls.

No universal conservation law is assumed. The first goal is an empirical/theoretical frontier, not a slogan.

## Frontier C — P13: Dual Scaling — Representation Allocation x Test-Time Compute

Current adaptive-compute work allocates inference budget across inputs. ORION will jointly allocate:
1. whether/how to re-represent the state; and
2. how much downstream reasoning/search compute to spend.

Primary comparison under one fixed total budget:
- uniform representation + uniform compute;
- adaptive compute only;
- adaptive representation only;
- joint representation/compute allocator;
- oracle allocator upper bound.

Strong outcome: the joint allocator strictly improves the accuracy-cost Pareto frontier and learns regimes in which state compilation substitutes for extra reasoning, versus regimes where the two are complementary.

## Frontier D — P14: Sufficiency Ladder

Representations will be certified against distinct task requirements rather than called simply "sufficient":
- predictive sufficiency;
- decision/control sufficiency;
- counterfactual/interventional sufficiency;
- verifier/repair sufficiency.

The benchmark asks where a representation that passes a lower rung fails at a higher one. The central metric is **sufficiency debt**: retained performance at rung L versus failure when reused at rung L+1.

This does not claim predictive-vs-control or predictive-vs-counterfactual separation as new theory; those distinctions have prior causal/RL foundations. Novelty must come from the cross-domain operational benchmark and measurable escalation failures.

## Frontier E — P15: Compile, Cache, or Recompute?

A fixed universal representation may be worth precomputing when many heterogeneous queries reuse the same state. Query-conditioned compilation may dominate for sparse or changing queries.

Measure the phase diagram over:
- number of queries per state;
- query diversity;
- compiler cost;
- cache/storage cost;
- downstream model/search cost.

Goal: identify the break-even regime between universal state materialization and on-demand state compilation. This connects representation learning to database indexing/cache economics without claiming database novelty.

## Frontier F — Formal-state application after P10 native execution

If P10 native-state incremental value is supported, test tactic/goal-conditioned proof-state compilers that expose only the coordinates relevant to a candidate proof action or repair query. Compare against full proof state, source history, and fixed state summaries under matched Lean/verifier budgets.

If P10 native state fails, this formal-state rung remains blocked rather than being rescued post hoc.

## Hostile novelty boundaries

Known adjacent territory that must be credited rather than claimed:
- predictive V-information / usable information;
- state design in dynamic LLM reasoning;
- task-conditioned pruning of agent tool output;
- goal-conditioned and hierarchical state abstraction in RL;
- causal abstraction and predictive-vs-control/counterfactual sufficiency;
- adaptive test-time compute allocation;
- proof-state snapshotting and proof-state-based theorem search.

The programme's intended new territory is the **joint resource theory and execution policy** linking representation construction cost to downstream capacity/search/verification cost, with exact controlled theorems and multi-domain executions.

## Research-cell roles

1. **Theory lead** — prove exact representation-dimension/accessibility results and attack hidden assumptions.
2. **Statistical lead** — freeze endpoints, uncertainty, fresh-seed replication, multiple-comparison boundaries.
3. **LLM systems lead** — exact model/runtime/token accounting and joint allocation experiments.
4. **Formal methods lead** — Lean state extraction, verifier-call accounting, leakage controls.
5. **Hostile reviewer** — nearest-work subtraction, counterexamples, adversarial controls, claim veto.
6. **Reproducibility lead** — content-addressed protocols/results, deterministic replay, fail-closed terminals.

No role may promote a result before its frozen gate passes.
