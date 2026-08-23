# P9/P10 Nearest-Work Ledger — 2026-08-20

Status: **CURRENT LITERATURE CHECKPOINT — REFRESH BEFORE MANUSCRIPT FREEZE**

## Purpose

Define what P9/P10 must beat conceptually so novelty is not based on a stale literature boundary.

## Test-time scaling

### Hariri et al. — Test-Time Scaling in Reasoning LLMs: Inference Regimes, Evaluation, and Reproducibility (arXiv:2608.04001)

Relevant boundary:
- distinguishes single-trajectory, leaf-level and prefix-level inference regimes;
- emphasizes protocol-matched compute accounting and reproducibility.

ORION consequence:
- a `reasoning tax` claim cannot use a vague single compute scalar;
- token count, candidate count, verifier/search calls and protocol structure must be separately exposed;
- novelty is not `more/less test-time compute`, but whether information-equivalent representation changes the compute frontier under matched regimes.

### Zhai et al. — Adaptive Test-Time Compute Allocation for Reasoning LLMs via Constrained Policy Optimization (arXiv:2604.14853)

Relevant boundary:
- compute allocation can itself be optimized across tasks.

ORION consequence:
- structural-state benefits must not be confounded with adaptive budget allocation;
- later work may study whether structured state also improves the *allocation policy*, but this is a separate claim.

## Formal theorem proving

### Yang et al. — LeanDojo / ReProver (arXiv:2306.15626; NeurIPS 2023)

Relevant boundary:
- proof-state/premise-aware learning and challenging Lean splits already exist.

ORION consequence:
- `we use proof state` is not novelty;
- P10 must focus on incremental information over exact tactic-history baseline, module-held-out invariance, information-equivalent controls, and/or matched-budget search consequences.

### Xin et al. — TacMiner: Automated Discovery of Tactic Libraries for Interactive Theorem Proving (arXiv:2503.24036)

Relevant boundary:
- tactic-dependence graphs can expose reusable tactic structure.

ORION consequence:
- standalone P10 structure novelty requires a faithful TacMiner-class comparator or an explicit `CANNOT_CHECK`.

### Kung et al. — LEAP: Supercharging LLMs for Formal Mathematics with Agentic Frameworks (arXiv:2606.03303)

Relevant boundary:
- strong gains from decomposition, iterative self-refinement and continuous Lean compiler interaction;
- formal proof utility is increasingly an agent/search result, not only a next-action prediction result.

ORION consequence:
- P10 one-step predictive gains do not imply prover utility;
- strongest proof claim must be verifier-backed search under matched Lean-call budgets.

### Li et al. — Self-Modifying Lean Proof Agents with Verifier-Grounded Benchmark Coevolution (arXiv:2607.17352)

Relevant boundary:
- proof workflows and structured proof context can themselves evolve inside a Lean-grounded verification loop.

ORION consequence:
- `structured context helps Lean agents` is insufficient novelty;
- ORION's differentiator must be causal/matched representation controls, invariant coordinates, or structural scale/compute substitution.

### Ma et al. — OProver (arXiv:2605.17283)

Relevant boundary:
- compiler feedback, retrieved verified proofs, repair trajectories and large-scale agentic training are strong modern baselines.

ORION consequence:
- P10 should avoid architecture leaderboard framing unless it can actually compete at that scale;
- mechanistic representation experiments can remain novel without claiming SOTA prover performance.

### Srinivasan & Patawar — LAMP (arXiv:2606.28841)

Relevant boundary:
- explicit structured domain knowledge at inference time can materially benefit a Lean multi-agent system.

ORION consequence:
- the novelty bar for `structure at inference helps formal proof` is already high;
- same-information serialization controls and scale/compute substitution are essential.

## Novelty conclusion

The following claims are too weak as P9/P10 headline novelty in 2026:

- structure helps LLM reasoning;
- native proof state helps theorem proving;
- verifier feedback helps Lean agents;
- more test-time compute improves reasoning;
- tactic structure transfers across proofs without stronger controls.

The materially stronger ORION directions are:

1. **information-equivalent computational accessibility** — same facts, different bounded computational risk;
2. **structural scaling substitution** — smaller model with structured state reaches a quality attained only by a larger same-information model at matched inference regime;
3. **representation-induced reasoning tax** — same model needs less protocol-matched inference compute under structured state;
4. **intervention-defined error decomposition** — distinguish information, representation, computation and search/verification limitations;
5. **restricted-class representation separation theorem** plus empirical LLM correspondence;
6. **P10 module-invariant proof coordinates** beyond tactic history;
7. **matched-budget verifier-backed search utility**;
8. **cross-domain replication** of the same structural advantage quantities in P9 and formal Lean mathematics.

Any closer work discovered later must update this ledger and may lower the allowed claim rung.
