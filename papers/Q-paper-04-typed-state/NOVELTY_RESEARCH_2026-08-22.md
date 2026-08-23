# Q4 fresh novelty research — 2026-08-22

Purpose: hostile related-work/novelty map for the typed-state paper. This is a bounded search statement, not a novelty certificate.

## Major positioning change

The 2026 literature makes several primitives in Q4 **non-novel in the broad**:

- typed/provenance-aware agent memory;
- stale-memory detection/update;
- scoped/provenance-grounded retrieval;
- value-of-information for agent information acquisition;
- governed/versioned persistent memory.

Q4 should therefore not be sold as “typed memory for agents.” Its residual question is narrower and more experimentally testable:

> **When a scientific decision-maker receives the same visible partial information, does explicitly typed/scoped epistemic state change decision quality compared with consuming the same information as an untyped or decision-agnostic memory?**

The paper's strongest existing feature is matched-information mechanism isolation across six different research-state operations, not the invention of any one memory primitive.

## Closest/current literature threats

### Typed memory representation

Zhengda Jin et al., **“Mitigating Provenance-Role Collapse in Long-Term Agents via Typed Memory Representation,”** arXiv:2605.25869 (MemIR, 2026).

MemIR explicitly argues that flat unstructured agent memory causes provenance-role collapse and introduces a typed intermediate representation separating evidence, retrieval cues and truth-bearing claims, with provenance-scoped utilization. It reports gains on LoCoMo and BEAM-100K.

This is a direct threat to broad Q4 language such as “typing agent memory is new.” Q4's differentiation must come from **scientific decision state, matched-information ablations, scoped failure applicability/transport obligations, and decision-coupled acquisition**, not from typed memory per se.

### Stale-memory revision

Hanxiang Chao et al., **“STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?”** arXiv:2605.06527 (2026), introduces a 400-scenario/1,200-query benchmark for state resolution, premise resistance and implicit policy adaptation when later evidence invalidates earlier memory.

Haofei Sun and Lin He, **“When Memory Updates but Behavior Does Not: Repairing Implicit Stale Dependencies in Personalized Agent Responses,”** arXiv:2608.01619 (2026), further studies state-to-draft auditing and stale-dependency repair.

Therefore Q4's stale-receipt study should be framed specifically around **scope-bound scientific failure applicability** and exact matched-information controls, not general stale-memory handling.

### Value of information is an established decision-theoretic agent tool

Yijiang River Dong et al., **“Value of Information: A Framework for Human–Agent Communication,”** ACL 2026, applies classical VoI to agent clarification decisions across multiple real domains.

VoI itself is classical and agentic VoI is now explicit in current literature. Q4's N4-A/N1-C results can test how **typed priors/scoped state alter VoI decisions**, but cannot claim to introduce VoI-based agents.

### Provenance-grounded / governed persistent memory

2026 work including Eywa, governed shared-memory architectures, bitemporal/typed memory operators, and emerging persistent-memory specifications already treats scope, temporal supersession, provenance, versioning and validation state as first-class agent-memory concepts.

Q4 should not claim these database/governance primitives in general.

## Residual contribution that still looks defensible

The present Q4 evidence remains distinctive in combination:

1. **same visible facts, different epistemic representation/policy** rather than an information-asymmetry comparison;
2. multiple scientific-decision primitives tested under one frozen first-right-of-refusal discipline;
3. failure receipts carry explicit applicability scope rather than merely timestamps/current-vs-stale labels;
4. proof/certificate transport is evaluated along a full transformation chain with stronger-oracle laundering controls;
5. interval uncertainty is coupled to Pareto decision ambiguity rather than generic memory accuracy;
6. information acquisition is scored by downstream decision value, including constructed high-entropy decoys;
7. every family contains a regime where the mechanism should tie/lose or a hostile shortcut should be punished.

This package is better described as **typed epistemic mechanics for research decisions** than as an agent-memory architecture.

## Current publication ceiling

The synthetic suite provides good mechanism isolation but is not enough for a top-tier claim about scientific agents. The closest literatures now include real-domain memory/VoI benchmarks, so Q4 requires a real research-decision validation layer.

A top-tier successor should ask the same matched-information question on prospectively frozen **real scientific decisions**, preferably across multiple programmes and at least one external/open corpus.

See `TOP_TIER_UPGRADE_PROTOCOL_2026-08-22.md`.

## Recommended paper thesis

> Typed/scoped state is not valuable merely because it stores more information. Across controlled research-decision tasks, the same information can produce different decisions depending on whether applicability, provenance, uncertainty and decision relevance are represented explicitly. The synthetic suite isolates six such mechanisms; a prospective real-domain study is required to establish transfer to scientific workflows.

## Claims to avoid

- first typed agent memory;
- first provenance-grounded memory;
- first stale-memory handling;
- first use of value of information in LLM/agent systems;
- general security from full-chain receipt transport;
- general advantage of typed memory on real agents;
- any implication that the deterministic `LLM_PROXY` arms measure actual frontier LLM performance.
