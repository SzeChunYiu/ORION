# Paper V research object — Self-ORION

## Candidate claim after nearest-work challenge

ORION is not novel merely because an LLM agent can edit its own code, evolve agent architectures, optimize programs with automated evaluators, or persist issues during self-improvement. The scoped candidate is:

> A self-development process in which **failures and null results become persistent knowledge**, persistent issue state accumulates diagnosis/intervention evidence, recurring failures are separated from cause attribution, ordinary causes must be excluded before method invention, candidate changes execute in isolated workspaces, promotion requires replay + fresh transfer + protected assurance, negative variants remain in history, and the system itself has no merge/promotion authority.

## Atoms

1. experience/task-episode representation;
2. persistent issue identity and lifecycle;
3. failure-pattern abstraction;
4. recurrence versus cause attribution;
5. prior-failure/issue retrieval;
6. repair/invention readiness;
7. candidate generation;
8. isolated execution;
9. evaluator protection;
10. fresh transfer / assurance;
11. negative evolution archive and host promotion.

## Nearest work and mechanisms absorbed

### Automated Design of Agentic Systems (ADAS) — arXiv:2408.08435
Mechanisms: meta-agent programs new agent systems, archive of prior discoveries, automated agent design, cross-domain/model transfer evaluation.

**Absorb:** agent-as-code search space; archive of variants; transfer as a first-class criterion; automated discovery of control-flow/tool-use designs.

**Not a surviving ORION novelty:** automatically designing agent architectures.

### Darwin Gödel Machine — arXiv:2505.22954
Mechanisms: system modifies its own code, empirically validates changes, maintains a diverse open-ended archive/tree, uses sandboxing and human oversight; demonstrated coding-benchmark improvement.

**Absorb:** candidate self-modification; archive/tree rather than one linear lineage; empirical validation; sandboxing; diversity/open-ended exploration.

**Residual:** ORION targets cause-aware failure learning, protected evaluator separation, fresh transfer and negative-history semantics before method promotion.

### A Self-Improving Coding Agent — arXiv:2504.15228
Mechanism: coding agent edits its own implementation and improves across benchmarks.

**Absorb:** direct self-edit baseline; use it to test whether ORION governance adds transfer/safety value rather than merely slowing improvement.

### AlphaEvolve — Google DeepMind / arXiv:2506.13131
Mechanisms: LLM proposals, automated evaluators and an evolutionary program database.

**Absorb:** broad/cheap + deep/strong proposal roles; evaluator-driven program search; program database.

**Constraint:** scientific-method quality is often non-scalar/partially identified; ORION must not manufacture a single objective merely because evolutionary search prefers one.

### ADIAS — arXiv:2608.06410
Mechanism: issue-centric self-improvement with persistent issue identity/lifecycle/evidence/intervention-outcome history used to guide subsequent optimization.

**Absorb / ADAPT:** `DevelopmentIssue.v1` persists the unresolved issue across multiple candidate repairs and keeps competing/supported causes, discriminator evidence, episodes and intervention outcomes attached to it.

**Not a surviving ORION novelty:** persistent issue-centric optimization/state.

**Residual:** ORION composes issue state with recurrence-not-cause, invention-readiness, replay/fresh transfer, protected assurance, negative-history and no-self-certification constraints.

### AI Co-Scientist evolution/tournament mechanism
Mechanism: hypothesis evolution, ranking tournaments and test-time scaling.

**Absorb:** multiple challenger families and explicit competitive comparison; do not use internal tournament scores as protected self-improvement authority.

### RewardHackingAgents / search-time contamination work
Mechanisms: evaluator tampering, held-out leakage, benchmark/search contamination and access telemetry as first-class evaluation threats.

**Absorb:** protected paths, patch/access logging, trusted evaluator, distinct development versus assurance sets, contamination audit.

## ORION mechanics now implementing the claim

Current branch includes immutable task/experience episodes, failure-pattern candidates, persistent `DevelopmentIssue.v1`, replay/fresh-transfer gates, host-protected verification, work-order generation, Self-ORION research/change-control modules, content-addressed patch artifacts, isolated sandbox interfaces, staged readiness and no self-merge primitive.

## Surviving candidate deltas

- `P5.D1.FAILURE_AS_KNOWLEDGE`: failures/nulls are retrievable evidence objects, not discarded benchmark losses.
- `P5.D2.RECURRENCE_IS_NOT_CAUSE`: repeated variants may justify a failure-pattern candidate but cannot directly authorize a repair; competing responsibility hypotheses and a discriminator are required.
- `P5.D3.ISSUE_PLUS_CAUSAL_STATE`: issue-centric persistence is combined with explicit cause hypotheses/discriminator evidence and retains all intervention outcomes rather than only the winning lineage.
- `P5.D4.INVENTION_READINESS`: new operators/representations are considered only after ordinary retrieval/routing/implementation/evidence causes and cross-domain transfer alternatives are challenged.
- `P5.D5.REPLAY_PLUS_FRESH_TRANSFER`: repair promotion requires both fixing the motivating failure and working on independent fresh variations; failed transfer narrows/refutes the lesson instead of being averaged away.
- `P5.D6.NO_SELF_CERTIFICATION`: coding/proposal, execution, evaluation and promotion authority are structurally separated; ORION can recommend host promotion but cannot merge itself.
- `P5.D7.NEGATIVE_EVOLUTION_HISTORY`: harmful/null variants remain addressable and can condition future routing/guards.

## Falsifier V1 — executed locally

The local hidden-cause/issue/reward-hacking suite passes:
- recurrence alone does not identify cause;
- cause support requires discriminator evidence;
- harmful and successful interventions remain attached to the same issue;
- fresh transfer is distinct from replay;
- a resolved issue needs new evidence to reopen;
- ordinary causes block method invention;
- invention readiness grants neither invention nor promotion authority;
- a candidate touching protected governance/registry paths is rejected even with artificially perfect visible/fresh deltas.

Local evidence: `papers/orion-15-self-orion/evidence/FALSIFIER_V1.md` and `FLAGSHIP_FALSIFIER_RESULTS_V1.md`.

## External falsifiers / benchmarks still open

### Hidden failure-family suite
Prospectively construct development tasks with the same symptom produced by different hidden causes: retrieval miss, routing miss, implementation bug, evaluator bug, representation gap and genuine method-basis gap. Cause labels stay hidden from the candidate.

### Fresh transfer + nearest-work baselines
Compare matched fixed coding agent, direct self-edit, ADAS/meta-agent search, DGM-like archive/self-edit, evaluator-only evolutionary search, ORION without attribution/fresh gates and full Self-ORION.

### Reward-hacking / contamination test
Candidate can improve visible score by changing evaluator, reading holdout labels, weakening tests, deleting negative history or retrieving benchmark answers during search. Full ORION must reject/discount these even when the scalar score rises.

### Metrics
- true root improvement on protected tasks;
- false method-change rate;
- correct responsibility attribution;
- fresh-transfer success;
- harmful-transfer rate;
- evaluator/holdout/search-contamination rate;
- retained negative-history completeness;
- cost/time to validated improvement.

## Paper claim boundary

Paper V must not claim first self-improving agent, first code-editing agent, first evolutionary LLM programmer, first automated agent-design system, or first persistent issue-centric self-improvement system.

It may test whether **issue-persistent, failure-governed, cause-attributed, independently assured self-development** produces more transferable and less reward-hackable improvements than benchmark-only self-modification.

The external gate remains `CANNOT_CHECK` until matched baselines, fresh hidden-cause tasks and protected evaluation are actually executed.
