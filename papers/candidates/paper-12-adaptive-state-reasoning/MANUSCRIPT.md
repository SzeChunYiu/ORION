# Adaptive State–Reasoning Co-Design under Matched Total Compute

**ORION publication candidate ORION-22**  
**Issue:** #665 · shared accounting owner #664  
**Manuscript status:** complete protocol/theory draft; protected empirical terminal not yet earned  
**Evidence date:** 2026-08-20

## Abstract

Test-time scaling usually asks how much additional reasoning, search or sampling a system should perform. ORION-21 motivates a second test-time action: spend computation to construct a more accessible state before reasoning. ORION-22 studies the resulting two-axis decision problem under one matched total resource boundary. We formalize state-construction budget and downstream reasoning/search budget as jointly allocatable resources, define a full factorial of fixed/adaptive state and fixed/adaptive reasoning policies, and require every arm to pay the same compiler, state, model, search, verifier, cache and recovery costs. A simple controlled existence construction shows that when task families contain prospectively distinguishable access-limited and reasoning-limited regimes, no state-only or reasoning-only adaptive policy can be optimal on both, whereas a joint policy can allocate the same total budget to the resource that has value in the current regime. This proposition establishes possibility, not an empirical advantage. The protected ORION-22 benchmark is therefore designed as a crossed grid of access difficulty and reasoning depth with family holdout, matched budgets, oracle regret, time-to-first-verified-solution and regime-specific reporting. The strongest paper claim will be earned only if a frozen joint allocator strictly improves the verified quality–resource Pareto frontier over both one-axis adaptive baselines and survives at least one real LLM or verifier-backed search domain. At present no protected joint-allocation outcome exists; this manuscript records the full theory, protocol, negative-result logic and promotion conditions without inventing results.

## 1. Introduction

A growing class of inference systems allocates more computation to difficult test items: longer chains of reasoning, more samples, larger search trees, repeated verification or other forms of test-time scaling. This literature owns the primitive that computation should be allocated adaptively rather than uniformly. Separately, context selection, state design, retrieval and compression systems adapt what information a model sees. ORION-22 does not claim either primitive.

The scientific question is whether these actions should be optimized **together under one budget**. A task may be difficult because its relevant structure is poorly exposed in the current state, because substantial reasoning remains even after the relevant structure is exposed, because both are difficult, or because neither is. Spending all marginal compute on reasoning is wasteful in an access-limited task; spending it all on state restructuring is wasteful when the state is already sufficient but the search depth is large.

We therefore model inference as two stages:

`raw/current state -> optional state construction -> downstream reasoning/search -> verified outcome`.

Both stages consume resources. The allocator must decide prospectively—using only pre-outcome signals—how to divide a fixed envelope between them. The core comparison is not “better context versus more thinking” at different total costs. It is a matched-total-budget factorial:

1. fixed state + fixed compute;
2. fixed state + adaptive reasoning/search;
3. adaptive/compiled state + fixed reasoning/search;
4. joint adaptive state + adaptive reasoning/search;
5. oracle joint allocator as a diagnostic ceiling.

ORION-22 is deliberately fail-closed. A positive average that comes from extra total compute, protected-outcome tuning, arbitrary scalar weights or hidden compiler work is invalid. If joint allocation does not improve the frontier, that negative is the paper’s result.

## 2. Donor boundary

Prior work already owns:

- adaptive test-time compute, best-of-N, search and difficulty-conditioned reasoning budgets;
- rational metareasoning and value-of-computation formulations;
- dynamic context selection, retrieval and compression;
- cost-sensitive feature acquisition;
- compute-optimal allocation and anytime reasoning;
- oracle per-item budget allocation as an analysis device.

ORION-21 additionally establishes a controlled basis for treating state construction as a costed inference action. ORION-22’s residual is therefore:

> Under one explicit resource boundary, when do state construction and downstream reasoning substitute for one another, when are they complementary, and can a frozen policy identify those regimes prospectively?

No novelty claim is made for generic adaptive computation or generic context selection.

## 3. Formal problem

For task instance `i`, let:

- `R_i` be the current/raw state;
- `a_i` denote access difficulty—the resource required to expose task-relevant structure;
- `h_i` denote reasoning/search difficulty after that structure is accessible;
- `c_i` be resources spent on state construction;
- `r_i` be resources spent on downstream reasoning/search;
- `B_i` be the total allowed resource envelope;
- `Y_i(c_i,r_i)` be verified task quality/success.

The allocator chooses `(c_i,r_i)` subject to the common accounting contract. In an exact controlled world a scalar primitive budget may satisfy `c_i+r_i <= B_i`. In real systems, `c_i` and `r_i` are resource vectors and comparisons are Pareto-based unless a legitimate cost vector is frozen prospectively.

The policy sees a pre-outcome signal `z_i` but not protected labels, verifier outcomes or hindsight difficulty.

### 3.1 Policy classes

- `FIXED_STATE_FIXED_COMPUTE`: constant `(c,r)` with no item adaptation.
- `FIXED_STATE_ADAPTIVE_COMPUTE`: `c=0` or canonical fixed-state cost; choose `r(z)`.
- `ADAPTIVE_STATE_FIXED_COMPUTE`: choose `c(z)`; downstream `r` fixed.
- `JOINT_STATE_COMPUTE`: choose both `c(z)` and `r(z)` within the same budget.
- `ORACLE_JOINT`: hindsight optimum under the same envelope; diagnostic only.

## 4. Controlled existence proposition

The following proposition is intentionally simple. It is a calibration theorem showing that joint allocation can have structural value; it is not evidence that real tasks satisfy the assumptions.

### Proposition 1 — strict value of joint allocation in a heterogeneous mixture

Consider two equally costly actions under budget `B=1`: state compilation `C` and extra reasoning `R`. Let tasks have a pre-outcome signal `z in {A,H}` that perfectly identifies one of two equiprobable regimes:

- access-limited regime `A`: success is 1 iff `C` is taken;
- reasoning-limited regime `H`: success is 1 iff `R` is taken.

A policy restricted to state adaptation only cannot spend its unit on extra reasoning and therefore fails all `H` tasks. A policy restricted to reasoning adaptation only cannot compile and therefore fails all `A` tasks. Each achieves at most `0.5` expected success. The joint policy `pi(z=A)=C`, `pi(z=H)=R` achieves expected success `1.0` at the same per-item budget.

More generally, if `P(A)=p`, the best state-only policy achieves at most `p`, the best reasoning-only policy at most `1-p`, and the joint signal-conditioned policy achieves `1` under perfect signal and deterministic action value.

### Interpretation

The proposition is not scientifically surprising; rational metareasoning already predicts that different computations can have different values in different states. Its role is to prevent a weaker ORION-22 design in which all tasks favor the same resource and joint allocation has no meaningful discriminator. The empirical problem is harder: construct prospectively frozen regimes, expose imperfect but fair pre-outcome signals, charge all resource axes, learn a policy on development families and test whether the value survives held-out families and real systems.

## 5. Controlled benchmark design

### 5.1 Two independent difficulty axes

Generate task families on a crossed grid:

- **access difficulty `a`** controls how much task-relevant structure is obscured by the initial state and how much compilation is required to expose it;
- **reasoning depth `h`** controls how much computation remains after the relevant state is accessible.

The grid must contain four true regimes:

| Access difficulty | Reasoning difficulty | Intended resource value |
|---|---|---|
| low | low | neither extra resource materially helps |
| high | low | compile-first |
| low | high | reason/search more |
| high | high | both may be required |

Access and reasoning factors are generated independently enough that one cannot be inferred trivially from the protected outcome.

### 5.2 Pre-outcome signals

Candidate signals include representation diagnostics, structural complexity measures, model uncertainty measured before extra computation, and task metadata that are available to **all** adaptive arms. Signals are frozen before protected evaluation. No arm may inspect protected verifier outcomes to decide its budget.

### 5.3 Primary arms and sanity controls

Required arms:

1. fixed state + fixed compute;
2. fixed state + adaptive compute;
3. adaptive state + fixed compute;
4. joint adaptive state + adaptive compute;
5. oracle joint;
6. random allocation;
7. simple prospectively frozen threshold rules.

### 5.4 Budget grid

Use a small interpretable grid of total budgets. In controlled worlds, define exact primitive units. In real systems, emit the shared resource vector from `P11_P14_RESOURCE_ACCOUNTING_SCHEMA_V1.md`.

Every arm receives the same envelope. Unused budget remains unused and recorded. It is not moved between axes after seeing an outcome.

## 6. Endpoints

### Primary scientific endpoints

- verified success at each total budget;
- strict Pareto dominance over the best one-axis adaptive arm;
- `joint_gain(B) = Q_joint(B) - max(Q_adaptive_state(B), Q_adaptive_reason(B))` at identical resource boundaries;
- resource/time to first verified correct solution;
- regret to `ORACLE_JOINT`.

### Secondary endpoints

- allocation classification accuracy relative to oracle choices;
- frequency of each state action and reasoning level;
- calibration of pre-outcome signals;
- compiler failures;
- wasted compile work;
- unused budget;
- regime-specific harms.

Policy value is primary. Mimicking oracle action labels without improving task outcomes is not a positive terminal.

## 7. Statistics and protected evaluation

The statistical plan follows the manuscript-statistics rules of transparent units, effect sizes and blocked generalization.

1. Hyperparameters and policy selection use development families only.
2. Primary test holds out complete task families or domains, not only random items.
3. Paired item comparisons are performed within family because all policies see matched tasks.
4. Headline uncertainty uses family/domain-block bootstrap or an exact paired procedure appropriate to the endpoint; the exact method is frozen before execution.
5. A noninferiority margin against adaptive-compute-only is frozen for regimes where compilation should not help, preventing a positive mean from hiding avoidable harm.
6. All four regimes are reported separately.
7. No p values, confidence intervals or sample sizes are inserted into the manuscript before the protected protocol supplies them.

## 8. Real-system programme

### 8.1 Open-weight LLM/procedural tasks

Consume the same-information ORION-19-U task family when runtime is available. State choices should include a raw/serialized view, structured state and one ORION-21-style compiled view if its semantics can be certified. Reasoning budgets should be a small frozen generation/search grid. The key question is whether compile-first can allow a smaller or shorter-reasoning configuration to match or beat think-more-only at the same total resource cost.

Model-scale sweeps are secondary; a scale increase cannot be used to give only one arm more total compute.

### 8.2 Formal/verifier-backed search

If ORION-20-U native state passes its source/coverage gates, compare history-only state, native proof state and a dependency-aware compiled state while varying tactic/search/verifier-call budget. Exact Lean verification is the final success measure.

If the native-state gate is negative, retain that result and switch to another exact verifier-backed procedural/search domain. Do not weaken the paper’s real-system requirement or silently replace a negative Lean result with a different claim.

## 9. Current results

### 9.1 What is earned

- The shared resource-accounting schema is specified.
- ORION-21 provides controlled evidence that state construction can materially change accessible representation/sample burden.
- The frozen ORION-22/Dual-Scaling protocol defines matched arms and a positive terminal requiring strict `joint_gain` at prespecified controlled budgets plus a real-system gate for any cross-domain claim.
- Proposition 1 shows by construction that heterogeneous access-limited and reasoning-limited regimes can create strict value for joint allocation.

### 9.2 What is **not** earned

There is currently **no protected ORION-22 empirical joint-allocation result**. No value for `joint_gain`, no confidence interval, no real-system crossover and no learned-policy superiority claim is authorized.

This negative/unknown state is first-class. The manuscript will not contain a synthetic “expected results” section written in the grammatical past tense.

## 10. Negative-result elimination programme

The goal is to eliminate alternative explanations and design failures through new frozen experiments, not to erase an unfavorable terminal.

### Failure mode A — joint policy wins only because it gets more compute

**Elimination:** audit every episode with the shared resource receipt; match compiler, reasoning, verifier, cache and recovery resources; report unused budget; reject any comparison with asymmetric stopping or tool rules.

### Failure mode B — all tasks prefer one resource

**Elimination:** use the crossed generator with independent access/reasoning factors. Before any learning, verify by oracle intervention that the four regimes are real: compile has positive marginal value in access-limited cells, reasoning has positive marginal value in depth-limited cells, both in the joint cell, neither in the easy cell.

### Failure mode C — pre-outcome signal is insufficient

**Elimination:** prespecify signal ablations: access-only, reasoning-difficulty-only, uncertainty-only and joint signal. Compare value, not hindsight classification. If all learned policies fail while oracle gain is large, conclude signal insufficiency rather than retuning protected labels.

### Failure mode D — policy class is insufficient

**Elimination:** compare a simple threshold allocator, a learned low-capacity allocator and a richer but frozen allocator on development data. If oracle gain exists and signals are predictive but all allowed policies fail, document policy-class regret and narrow the claim.

### Failure mode E — compilation is harmful in reasoning-limited regimes

**Elimination:** freeze noninferiority in cells where compilation should have zero value. A joint policy that improves average success by harming these cells fails the robust positive gate.

### Failure mode F — real-system crossover disappears

**Disposition:** retain the negative. The maximum claim becomes a controlled allocation law. Do not claim general adaptive state–reasoning co-design.

## 11. Planned figures

1. Two-axis resource plane: compile budget × reasoning/search budget.
2. Controlled four-regime value heatmap.
3. Matched-total-budget Pareto curves for all policy classes.
4. Learned allocation map versus oracle with regime-specific errors.
5. Real LLM compile-first versus think-more crossing, if earned.
6. Formal/search replication or explicit negative terminal.

## 12. Discussion

ORION-22 reframes test-time inference as a portfolio of computations rather than a single “reasoning token” axis. This matters because upstream state construction and downstream reasoning can be substitutes, complements, or irrelevant depending on the source of difficulty.

The framing also prevents an important accounting error. Prompt shortening, retrieval, parsing, summarization and compilation can reduce downstream tokens while consuming substantial upstream work. Calling the downstream trace cheaper without charging that work is not a compute improvement. Conversely, a state transformation that is expensive once but reusable across a long horizon may be valuable after amortization. The correct comparison therefore depends on a declared decision contract or a Pareto surface, not an arbitrary universal exchange rate between tokens, bytes, verifier calls and wall time.

A successful ORION-22 would not imply that every task needs a learned allocator. Simple threshold rules may be sufficient in stable regimes. Nor would it imply that state and reasoning are always substitutes; some tasks may require both. The scientifically useful outcome is a prospective regime map and allocation rule whose failures are visible.

## 13. Limitations

1. Proposition 1 is an existence construction, not empirical evidence.
2. The controlled benchmark risks encoding its own desired regime geometry; oracle-intervention checks must verify the generator before policy training.
3. Real resource units are heterogeneous and should not be collapsed into a scalar without a legitimate downstream cost vector.
4. Policy generalization across task families/domains is untested.
5. ORION-22 depends on accurate compiler accounting from #664 and real-system runtime availability.
6. Adaptive policies can exploit leakage in difficulty signals; all signals need protected-outcome independence checks.
7. The current paper is not submission-ready until a protected empirical terminal and at least one real-system validation exist.

## 14. Reproducibility

Current frozen protocol substrate is recorded in the Frontier V2 branch/PR as `P13_DUAL_SCALING_PROTOCOL_V1.md`; numbering there predates the grouped publication remap and corresponds to the present ORION-22 scientific question. The publication issue #665 and #670 supersede the old standalone numbering while preserving bytes and history.

Every future run must emit `ORION.P11P14.ResourceReceipt.v1` records and preserve protected splits, policy versions, seeds, model identities and verifier/tool versions.

## 15. Data and code availability

No ORION-22 protected result dataset exists yet. Controlled generators and real-system task splits must be committed/versioned before protected execution. Evaluation code and machine-readable receipts should be released with the final paper package.

## 16. Claim ledger

| Claim | Status | Evidence required/available | Forbidden widening |
|---|---|---|---|
| state construction and reasoning are distinct allocatable actions | DEFINITION / ORION-21-supported framing | ORION-21 + resource schema | empirical joint advantage |
| heterogeneous regimes can make joint allocation strictly valuable | CONTROLLED EXISTENCE PROPOSITION | Proposition 1 | real-task law |
| frozen factorial is compute matched | PROTOCOL CLAIM | accounting audit required | assumed fairness |
| learned joint allocator beats both one-axis baselines | OPEN | protected controlled experiment | may not be stated now |
| crossover generalizes to LLM/formal task | OPEN | real-system protected test | may not be inferred from toy world |
| one universal scalar compute exchange rate exists | REJECTED | none | do not claim |

## 17. Publication decision

**Current decision:** complete theory/protocol manuscript, empirical gate open. ORION-22 should not be externally promoted on this package alone.

Minimum promotion package: independently replicated controlled joint-allocation advantage, exact matched-total-budget audit, one real-system validation, donor-complete baselines and task-family/domain holdout.

The strongest headline is earned only if a frozen joint policy prospectively identifies compile-first and think-more regimes at equal total budget and yields a strict Pareto improvement over both one-axis adaptive policies.

## References and donor notes

1. Russell, S. J. & Wefald, E. **Do the Right Thing: Studies in Limited Rationality.** MIT Press, 1991. [Foundational metareasoning donor; final edition metadata to verify.]
2. ORION Frontier V2 Nearest-Work Ledger (2026-08-20), adaptive test-time compute and dynamic context-selection donor sections.
3. ORION-21 manuscript in this package for state-construction theory and controlled accessibility evidence.

### Citation integrity note

A fresh external literature delta is mandatory before submission, particularly for 2025–2026 adaptive test-time scaling and context-selection systems. The external web search endpoint was unavailable during this drafting pass, so contemporary bibliographic metadata is not invented here.
