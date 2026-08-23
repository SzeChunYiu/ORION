# Frontier Support/State Nearest-Work Ledger — 2026-08-20

Status: **FROZEN BEFORE FRONTIER OUTCOMES**

This ledger records the closest current work found before any Frontier-F1...F6 outcome. It is a novelty subtraction map, not a completeness claim.

## 1. State representation already matters

**State Design Matters: How Representations Shape Dynamic Reasoning in Large Language Models** — arXiv:2602.15858.

Owns: empirical evidence that state granularity/structure/spatial encoding materially affects dynamic LLM reasoning while model parameters are fixed.

Does not by itself own: exact same-information support-placement frontiers across representation/architecture/retrieval/tools/memory/search; certified task-sufficient compaction; compile-once multi-query amortization.

ORION consequence: never claim novelty for the generic sentence `state representation matters`.

## 2. Agentic test-time scaling through rollout representation

**Scaling Test-Time Compute for Agentic Coding** — arXiv:2604.16529.

Owns: compact structured rollout summaries for parallel/sequential test-time scaling in coding agents; strong SWE-Bench/Terminal-Bench improvements.

Gap retained: machine-verifiable task-sufficiency certificates; resource substitution between representation quality and model/retrieval/search capacity; answer-blind state compilation reused across multiple downstream queries.

## 3. Context compaction is active research

**CompactionRL** — arXiv:2607.05378.

Owns: RL training for long-horizon context compaction with improved coding-agent performance.

**Active Context Compression** — arXiv:2601.07190.

Owns: agent-controlled summarization/pruning with token savings on SWE-bench Lite.

**Parallel Context Compaction** — arXiv:2605.23296.

Owns: systems/throughput improvements and predictable compaction volume; explicitly notes summarization is lossy.

**LCM: Lossless Context Management** — arXiv:2605.04050.

Owns: deterministic hierarchical summary DAG plus lossless pointers/retrievability; strong long-context coding-agent results.

**State Compression in Two-Agent LLM Relays** — arXiv:2607.18265.

Owns: closed-world evidence that structured JSON handoffs preserve constraints much better than narrative summaries.

Gap retained: a task-specific *semantic sufficiency certificate* that proves future-relevant behavior/outcomes are unchanged by compaction in a bounded environment. `Lossless pointers to all raw history` is not the same object as `history may be deleted because the quotient state is sufficient for all declared future behavior`.

## 4. Context gathering / belief state

**The Context Gathering Decision Process** — arXiv:2605.07042.

Owns: POMDP framing for agentic context gathering, persistent predicate belief state, and an exhaustion gate; reports up to 11.4% multi-hop gain and up to 39% token savings.

Gap retained: explicit separation of observation-time scaling versus thinking-time/model scaling under exact coordinate-relevance controls; measured substitution frontier among the three.

## 5. Adaptive reasoning effort

**Ares: Adaptive Reasoning Effort Selection for Efficient LLM Agents** — arXiv:2603.07915.

Owns: per-step routing to the lowest adequate reasoning effort, reducing reasoning-token usage up to 52.7% with minimal task-success degradation.

Gap retained: interventions that choose whether to spend the next unit of budget on *new task state* versus internal reasoning, with exact observation accounting.

## 6. Retrieval and reasoning-intensive retrieval

**Compute Allocation for Reasoning-Intensive Retrieval Agents** — arXiv:2603.14635.

Owns: compute allocation across query expansion/reranking; stronger rerankers and deeper pools matter substantially.

**Retrieval as Reasoning / LLM-Wiki** — arXiv:2605.25480.

Owns: compiling external knowledge into agent-native structured Wiki pages and self-evolving retrieval structure.

Gap retained: same-task experiments where representation quality is varied while retrieval system is fixed, measuring `k*(q)` / reranker-scale substitution and downstream solve consequences.

## 7. Formal theorem proving retrieval

**LeanSearch v2** — arXiv:2605.13137.

Owns: global premise retrieval, strong retrieval metrics, and a controlled downstream prover loop where better retrieval improves proof success.

Gap retained: whether canonical proof-state/dependency coordinates reduce candidate depth or reranker/model strength required to recover the same premise groups.

## 8. Compiler outputs as compressed formal feedback

**Compile to Compress: Boosting Formal Theorem Provers by Compiler Outputs** — arXiv:2604.18587.

Owns: exploiting compiler failure-mode compression for local proof refinement and efficient verifier-guided search.

Gap retained: answer-blind reusable state compilation across multiple future questions/actions; cross-locus structural-support frontier; certified task-state compaction beyond compiler error classes.

## 9. Persisting proof state

**Keep the Proof State Live: Snapshotting for Efficient Tactic Search in Lean 4** — arXiv:2605.25556.

Owns: Lean proof-state snapshot/reuse and large wall-time speedups (reported 5.6–50x; mean 14x, median 9.7x).

ORION must not claim first proof-state snapshotting.

Gap retained: connect persistence to a general replay-tax / task-sufficient-state framework, and test whether a *minimal sufficient* state dominates full replay/full snapshot under quality and state-size accounting.

## 10. Externalization and harness engineering

**Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering** — arXiv:2604.08224.

Owns: the conceptual trend that cognition is externalized into memory, skills, protocols, and harnesses rather than weights alone.

Gap retained: a controlled quantitative Pareto frontier that moves fixed task structure between loci and measures which model/compute/retrieval/search resources are substituted.

## 11. System-level capability attribution

**Stop Reporting System-Level AI Reasoning as Individual Model Capability** — OpenReview AI4GOOD 2026.

Owns: critique of attributing system/harness/test-time-compute gains to a single model and proposes compute-normalized reporting.

Gap retained: causal experiments and resource frontiers rather than reporting standards alone.

## 12. Linear accessibility theory

**How Many Features Can a Language Model Store Under the Linear Representation Hypothesis?** — COLT 2026, PMLR 336.

Owns: formal separation between linear representation and linear accessibility in internal activations and nearly matching linear-compressed-sensing bounds.

Gap retained: external task representations/support placement, reasoning-system resource frontiers, state compaction and retrieval/search substitution.

## 13. Semantic invariance

**Semantic Invariance in Agentic AI** — arXiv:2603.13173.

Owns: metamorphic testing of semantically equivalent formulations across multiple large models and evidence that scale does not guarantee invariance.

Gap retained: machine-verifiable exact semantic equivalence classes/certificates in bounded procedural/formal environments and their connection to support placement/resource cost.

## 14. Distillation / reusable reasoning structure

**Structural Rationale Distillation via Reasoning Space Compression** — arXiv:2605.07139.

Owns: compact reusable high-level reasoning-path banks for teacher/student distillation.

**Improving Reasoning Capabilities in Small Models through Mixture-of-Layers Distillation...** — arXiv:2604.15701.

Owns: teacher stepwise-attention transfer into student models.

**SkillDroid: Compile Once, Reuse Forever** — arXiv:2604.14872.

Owns: compiling successful GUI trajectories into reusable parameterized action skills, reducing future LLM calls.

Gap retained for ORION F3: no-weight-update primary test where a compiler constructs an answer-blind *world/task state* once, the same state supports multiple unseen downstream queries, and the scientific endpoint is an amortized model/compute crossover rather than skill replay or rationale distillation.

## 15. Novelty-safe residuals

The most defensible currently unowned combinations are:

1. **Structural Support Frontier**: same task structure moved among representation/architecture/tool/memory/retrieval/search with native resource accounting.
2. **Certified task-sufficient state compaction**: prove/verify that a quotient state preserves all declared future task behavior, then measure reasoning-resource savings.
3. **Compile once, reason many**: answer-blind reusable state compilation with an amortized crossover against repeated large-model reasoning.
4. **Observation-time scaling**: choose between acquiring more state and generating more reasoning under one frozen resource policy.
5. **Representation–retrieval substitution**: structured task state reduces candidate depth/reranker strength for the same evidence/solve quality.
6. **Replay tax** as a cross-domain state-persistence quantity, while explicitly crediting Lean snapshotting for the formal-prover systems technique.

Any future literature hit that owns one of these exact combinations must narrow or retire the corresponding claim before outcome inspection where possible, and always before manuscript promotion.
