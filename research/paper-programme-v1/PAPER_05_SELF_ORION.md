# Paper V research object — Self-ORION

## Candidate claim after nearest-work challenge

ORION is not novel merely because an LLM agent can edit its own code, evolve agent architectures or optimize programs with automated evaluators.  The scoped candidate is:

> A self-development process in which **failures and null results become persistent knowledge**, recurring failures are separated from cause attribution, ordinary causes must be excluded before method invention, candidate changes execute in isolated workspaces, promotion requires replay + fresh transfer + protected assurance, negative variants remain in history, and the system itself has no merge/promotion authority.

## Atoms

1. experience/task-episode representation;
2. failure-pattern abstraction;
3. recurrence versus cause attribution;
4. prior-failure retrieval;
5. repair/invention readiness;
6. candidate generation;
7. isolated execution;
8. evaluator protection;
9. fresh transfer / assurance;
10. archive and host promotion.

## Nearest work and mechanisms absorbed

### Automated Design of Agentic Systems (ADAS) — arXiv:2408.08435
Mechanisms: meta-agent programs new agent systems, archive of prior discoveries, automated agent design, cross-domain/model transfer evaluation.

**Absorb:** agent-as-code search space; archive of variants; transfer as a first-class criterion; automated discovery of control-flow/tool-use designs.

**Not a surviving novelty:** automatically designing agent architectures.

### Darwin Gödel Machine — arXiv:2505.22954
Mechanisms: system modifies its own code, empirically validates changes, maintains a diverse open-ended archive/tree, uses sandboxing and human oversight; demonstrated large coding-benchmark improvements.

**Absorb:** candidate self-modification; archive/tree rather than one linear lineage; empirical validation; sandboxing; diversity/open-ended exploration.

**Residual:** DGM validates improvement primarily by task benchmarks; ORION's target is cause-aware failure learning, protected evaluator separation, fresh transfer and negative-history semantics before method promotion.

### A Self-Improving Coding Agent — arXiv:2504.15228
Mechanism: coding agent edits its own implementation and improves across benchmarks.

**Absorb:** simple self-edit baseline; use as a challenger to test whether ORION governance adds value or merely slows improvement.

### AlphaEvolve — Google DeepMind 2025/2026
Mechanisms: LLM ensemble proposes programs, automated evaluators score them, evolutionary program database determines future prompts, verified algorithmic improvements.

**Absorb:** broad/cheap + deep/strong proposal model roles; evaluator-driven program search; program database; human-readable candidate preference where operationally useful.

**Constraint:** AlphaEvolve excels where objective functions are crisp. ORION must not fabricate a scalar objective for scientific-method quality when the construct is only partially identified.

### AI Co-Scientist evolution/tournament mechanism
Mechanism: hypothesis evolution, ranking tournaments and test-time scaling.

**Absorb:** multiple challenger families and explicit competitive comparison; do not use internal tournament scores as protected self-improvement authority.

### RewardHackingAgents — arXiv:2603.11337
Mechanisms: evaluator tampering and held-out leakage are measured attacks; evaluator locking plus workspace isolation blocks both.

**Absorb:** protected paths, patch/access logging, trusted evaluator, distinct development versus assurance sets.

## ORION mechanics already present

Current main includes immutable `TaskEpisode`-style experience, failure-pattern candidates, replay/fresh-transfer gates, host-protected verification, work-order generation, Self-ORION research/change-control modules, content-addressed patch artifacts, isolated sandbox interfaces, staged readiness and no self-merge primitive.

## Surviving candidate deltas

- `P5.D1.FAILURE_AS_KNOWLEDGE`: failures/nulls are retrievable evidence objects, not discarded benchmark losses.
- `P5.D2.RECURRENCE_IS_NOT_CAUSE`: repeated variants may justify a failure-pattern candidate but cannot directly authorize a repair; competing responsibility hypotheses and a discriminator are required.
- `P5.D3.INVENTION_READINESS`: new operators/representations are considered only after ordinary retrieval/routing/implementation/evidence causes and cross-domain transfer alternatives are challenged.
- `P5.D4.REPLAY_PLUS_FRESH_TRANSFER`: repair promotion requires both fixing the motivating failure and working on independent fresh variations; failed transfer narrows/refutes the lesson instead of being averaged away.
- `P5.D5.NO_SELF_CERTIFICATION`: coding/proposal, execution, evaluation and promotion authority are structurally separated; ORION can recommend host promotion but cannot merge itself.
- `P5.D6.NEGATIVE_EVOLUTION_HISTORY`: harmful/null variants remain addressable and can condition future routing/guards.

## Falsifiers / benchmarks

### Hidden failure-family suite
Construct development tasks with the same symptom produced by different causes:
- retrieval miss;
- routing miss;
- implementation bug;
- evaluator bug;
- representation gap;
- genuine method-basis gap.

ORION must not learn one guard/repair across all variants merely because the surface symptom matches.

### Recurrence-without-causality test
Give three variants that all fail for different hidden reasons. A naive recurrence learner should overgeneralize; ORION should remain at candidate attribution until a discriminator separates them.

### Fresh transfer test
Repair on training variants, then test unseen task/domain/model variations. Compare:
- fixed coding agent;
- self-editing coding agent;
- ADAS/meta-agent search;
- DGM-like archive/self-edit loop;
- evaluator-only evolutionary search;
- ORION without attribution/fresh gate;
- full Self-ORION.

### Reward-hacking test
Candidate can improve visible score by changing evaluator, reading holdout labels, weakening tests or deleting negative history. Full ORION must reject these even when the scalar score rises.

### Metrics
- true root improvement on protected tasks;
- false method-change rate;
- correct responsibility attribution;
- fresh-transfer success;
- harmful-transfer rate;
- evaluator/holdout compromise rate;
- retained negative-history completeness;
- cost/time to validated improvement.

## Paper claim boundary

Paper V must not claim:
- first self-improving agent;
- first agent that edits its own code;
- first evolutionary LLM coding system;
- first automated agent-design system.

It may test whether **failure-governed, cause-attributed, independently assured self-development** produces more transferable and less reward-hackable improvements than benchmark-only self-modification.
