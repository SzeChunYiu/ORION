# Hostile Novelty Review Matrix V1

Status: **ACTIVE REVIEW CONTRACT**
Frozen: 2026-08-20

## Purpose

Prevent a superficially exciting P9/P10 result from surviving because of information leakage, unequal compute, benchmark artifacts, weak baselines, or post-outcome claim movement.

## Review roles

### A. Information-equivalence adversary

Attempts to prove the structured arm contains more usable facts than the same-information arm.

Blockers:
- answer-correlated field names/order;
- extra domain labels;
- unequal numerical precision;
- omitted failures/history in control arm;
- canonicalization that itself solves the task;
- noninvertible same-information renderer.

### B. Compute-accounting adversary

Attempts to explain gains by hidden compute.

Blockers:
- structured arm receives more generated tokens/candidates;
- tool calls not priced/accounted;
- verifier calls differ across compared search arms;
- context preprocessing uses an unreported model;
- retries or repair loops unique to one arm.

### C. Memorization/domain adversary

Attempts theorem/task family, module, namespace, template or lexical leakage.

Tests:
- domain identity attacker;
- duplicate and near-duplicate clustering;
- symbol renaming;
- source/path stripping;
- template-family held-out analysis;
- contamination ledger for pretrained models where auditable.

### D. Scaling-law adversary

Attempts to show the claimed scaling shift is an interpolation or threshold artifact.

Tests:
- observed-grid-only primary comparison;
- multiple target qualities frozen before outcomes;
- uncertainty on crossing points;
- report failures to cross target;
- no extrapolated crossing beyond tested model sizes for primary claim;
- replicate qualitative direction on second family only after primary family locked.

### E. Formal-methods adversary

P10-specific attacks:
- non-native state proxy presented as Lean state;
- post-tactic/future information leakage;
- theorem identity in dependencies;
- elaboration-changing semantic transformations;
- verifier substitutions;
- stale Mathlib/toolchain;
- proof search arms with unequal action vocabulary or stopping policy.

### F. Nearest-work adversary

Attempts to invalidate novelty by finding an existing result that already establishes the same claim under equal or stronger controls.

Before manuscript freeze, refresh at minimum:
- state representation/reasoning papers;
- test-time scaling and compute accounting;
- structured prompting/state-machine agents;
- theorem-proving systems using native proof state and compiler feedback;
- LeanDojo/ReProver lineage;
- TacMiner and tactic-library mining;
- current agentic Lean systems.

Novelty language must be revised rather than rationalized if a closer predecessor is found.

### G. Statistics adversary

Attacks:
- pooling hides domain reversal;
- one domain drives entire effect;
- cherry-picked q threshold;
- bootstrap unit wrong;
- multiple comparisons ignored;
- missingness correlated with outcome;
- calibration claims unsupported.

Required:
- item-paired estimates;
- held-out domain/module block uncertainty;
- worst-domain performance;
- heterogeneity table;
- complete missingness accounting;
- all preregistered primary and secondary endpoints retained.

### H. Mechanism adversary

Challenges any interpretation that representation rather than simpler confounders caused the result.

Competing explanations to test:
1. shorter prompt;
2. more explicit answer hints;
3. easier lexical matching;
4. better tokenization;
5. positional/order cue;
6. hidden retrieval;
7. exact tool solving rather than representation;
8. architecture-specific formatting prior.

A mechanism claim must survive plausible competing explanations or be weakened to an empirical association.

## Revolutionary-claim gate

The phrase-level thesis that representation changes the scale/compute frontier is permitted only if:

1. same-information equivalence is mechanically validated;
2. structured advantage is positive on preregistered held-out domains;
3. at least one scale or inference-budget substitution is observed on-grid;
4. matched-compute accounting passes;
5. hostile formatting/symbol/order controls pass;
6. domain-block uncertainty supports the effect;
7. nearest-work review finds the exact result materially distinct;
8. all negative/null arms remain visible.

Cross-domain language additionally requires independent support in P9 and P10 or another prospectively chosen domain. P10 one-step prediction alone cannot satisfy a reasoning-performance scaling claim.

## Required reviewer output

Each reviewer returns one of:

- `GREEN` — gate passed;
- `BOUNDED_GREEN` — narrower claim supported;
- `RED` — claim blocked by counterexample;
- `CANNOT_CHECK` — required evidence unavailable.

Any `RED` blocks the affected rung. `CANNOT_CHECK` cannot be silently treated as green.
