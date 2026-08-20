# ORION Frontier V2 — Nearest-Work Ledger (2026-08-20)

Status: ACTIVE HOSTILE NOVELTY SUBTRACTION

This ledger is intentionally adversarial. A concept is not ORION-owned merely because it appears in our vocabulary.

## 1. Usable information — prior-owned

**Xu et al., “A Theory of Usable Information under Computational Constraints,” ICLR 2020.** Predictive V-information explicitly models information usable by a restricted predictive family and observes that computation can create usable information.

Consequence: ORION cannot claim as novel that equal Shannon information can differ in computational usability, or that computation can transform inaccessible information into usable information.

Surviving gap: explicit accounting of the **cost and location** of that transformation—state compiler, decoder/model, search/inference, memory/cache, verifier—and online allocation among them.

## 2. State representation changes LLM reasoning — prior-owned

**Wong et al., “State Design Matters,” 2026.** Holds model parameters fixed while varying state granularity, structure and spatial grounding, showing large reasoning effects and noting that construction itself can induce useful computation.

Consequence: ORION cannot claim “state representation matters to LLM reasoning” as novelty.

Surviving gap: theorem-backed quantitative substitution/frontier results and active policies that decide *whether/how much to compile state* versus spend downstream inference/search compute.

## 3. Agent context compression — crowded

**ACON (2025/2026)** optimizes compression of agent observations/histories and reports substantial memory reductions while preserving performance.

**Agentic Context Engineering (ACE)** evolves context/playbooks online from execution feedback.

**Adaptive Context Elasticizer (ACE, 2026)** retains lossless raw history plus abstractions and dynamically selects raw/abstract/drop per decision step, explicitly addressing irreversible compression.

**Active Context Compression / Focus (2026)** lets an agent autonomously decide when to consolidate and prune context.

Consequence: ORION cannot claim active context management, reversible raw+compressed memory, or autonomous compression as new primitives.

Surviving gap: a resource theory that distinguishes current-task accessibility from future-task optionality/recoverability and gives exact or measured break-even laws for compile/cache/recompute/materialize policies.

## 4. Query-conditioned memory/state — prior-owned primitive

**QUMem (Aug 2026)** performs query-conditioned user-state inference from typed episodic memory with planned multi-query retrieval.

Task/query-conditioned pruning and evidence selection also appear in recent agent and multimodal systems.

Consequence: “condition representation on the current query” alone is not a novelty claim.

Surviving gap: exact representation-rank lower bounds for fixed query-agnostic readout families, no-answer-laundering controls, finite-sample nuisance penalties, and explicit cost/optionality accounting.

## 5. Program specialization / partial evaluation — classical prior

Partial evaluation specializes programs when some inputs are known at specialization time and has mature theory/systems literature from the 1980s–1990s onward.

Consequence: P11’s direct query compiler is conceptually related to specialization. ORION does not claim invention of specialization.

Surviving gap: treating **state representation itself** as the specialized object inside learning/agent inference and measuring how specialization trades against model capacity, sample burden, context, search and verification across ML/formal domains.

## 6. Adaptive test-time compute — prior-owned

Modern test-time scaling allocates additional reasoning/search budget based on problem difficulty and can outperform uniform allocation.

Consequence: ORION cannot claim adaptive inference-budget allocation by itself.

Surviving gap: joint allocation of two qualitatively different inference resources—state compilation and downstream reasoning/search—under one accounting boundary.

## 7. Causal/RL state sufficiency — prior-owned distinctions

Goal-conditioned abstraction, rate-distortion state abstraction, causal abstraction, predictive state representations and control sufficiency already establish that the state needed for prediction need not be the state needed for control/counterfactual tasks.

Consequence: P14 cannot claim the logical distinction between predictive, control and counterfactual sufficiency.

Surviving gap: an auditable multi-rung **sufficiency-debt benchmark** across procedural reasoning, theorem proving and agent repair, connected to the representation/compute frontier.

## 8. Proof-state theorem proving — prior-owned primitive

Modern Lean provers use proof states, compiler feedback, verifier-guided repair, snapshots and search. Macro-tactic mining and action abstractions also exist.

Consequence: ORION cannot claim “proof state helps theorem proving” or “compiler feedback helps repair.”

Surviving gap: incremental value beyond frozen history baselines, same-information feedback representation, abstraction granularity phase diagrams, and representation/search resource substitution under exact Lean receipts.

# Surviving programme claim-space

The strongest territory that survives current donor subtraction is:

> **Representation construction is an allocatable inference resource with measurable accessibility, memory, optionality and downstream-computation consequences.** A system may preserve raw state for recoverability, compile task-specific state for immediate accessibility, materialize universal state for low-latency multi-query reuse, or spend additional model/search/verification compute instead. The scientific object is the Pareto frontier and online policy among these resources, not the generic observation that context or representation matters.

This remains a programme hypothesis until real-system P13/P14/P15 executions pass. P11/P11B provide controlled theorem/result foundations only.
