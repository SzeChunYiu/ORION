# ORION-16–ORION-18 literature seed — 2026-08-17

This is a **seed ledger**, not a completed nearest-work matrix. Full-text verification, mechanism decomposition and disposition belong in #334/#337/#340 and #318.

## ORION-16 — Formal Epistemic Structures and Mechanics

### Classical/formal parent domains

1. Hans van Ditmarsch, Wiebe van der Hoek, Barteld Kooi. *Dynamic Epistemic Logic*. Springer, 2007/2008. Parent pressure: knowledge-changing actions, action models, belief revision and formal transition semantics are established territory.
2. AGM / iterated belief-revision literature. Parent pressure: expansion, contraction, revision, epistemic entrenchment and iterated update are prior art; ORION-16 cannot claim generic belief-change formalisms.
3. Sena Bozdag. *A Semantics for Hyperintensional Belief Revision Based on Information Bases*. Studia Logica, 2021. Parent pressure: incomplete/inconsistent information bases and non-idealized belief revision already have formal semantics.
4. Hans van Ditmarsch, Didier Galmiche, Marta Gawek. *An Epistemic Separation Logic with Action Models*. Journal of Logic, Language and Information, 2022/2023. Parent pressure: local/compositional epistemic action semantics exist.

### Modern agent architecture/mechanism pressure

5. Theodore R. Sumers, Shunyu Yao, Karthik Narasimhan, Thomas L. Griffiths. *Cognitive Architectures for Language Agents* (CoALA), arXiv:2309.02427. Parent pressure: modular memory/action/decision architecture for language agents is not novel.
6. Haodi Fan, Zucong Lan. *From Cognitive Architectures to Language Agents: A Mechanism-Level Review of Lineage, Convergence, and Migration Gaps*, arXiv:2607.23942. Parent pressure: state/control/transition/persistence/failure/learning/resource-governance decomposition is already an explicit mechanism-level comparison framework.
7. Kunlun Zhu et al. *Where LLM Agents Fail and How They can Learn From Failures*, arXiv:2509.25370. Parent pressure: modular failure taxonomies, root-cause isolation and targeted recovery are established empirical mechanisms.
8. Zehong Wang et al. *Why Reasoning Fails to Plan: A Planning-Centric Analysis of Long-Horizon Decision Making in LLM Agents*, arXiv:2601.22311. Parent pressure: planning semantics and future-aware lookahead must be separated from generic reasoning.
9. Hanyu Wang et al. *PreFlect: From Retrospective to Prospective Reflection in Large Language Model Agents*, arXiv:2602.07187. Parent pressure: prospective critique plus execution-time replanning is not novel.

### ORION-16 residual to test

Do not claim novelty unless nearest-work saturation leaves a specific composition such as:

`typed responsibility/evidence obligation -> explicit mutation authority over epistemic coordinates -> dependency-scoped reopening -> recursively composable mechanic contract`.

Even this composition is only a candidate until #334/#287 close.

---

## ORION-17 — Epistemic Navigation in Open Worlds

1. Jia Ao Sun et al. *Search-on-Graph: Iterative Informed Navigation for Large Language Model Reasoning on Knowledge Graphs*, arXiv:2510.08825. Pressure: iterative observe-then-navigate graph reasoning is direct navigation prior work.
2. Jiawei Chen et al. *Evaluating the Search Agent in a Parallel World*, arXiv:2603.04751. Pressure: search-agent evaluation already identifies collection/coverage, evidence sufficiency and when-to-stop as bottlenecks; MPW-Bench supplies a dynamic evaluation environment.
3. Yixuan Tang, Yi Yang. *AI Research Agents Narrow Scientific Exploration*, arXiv:2605.27905. Pressure: scientific exploration breadth/concentration is a measurable failure mode; a navigation paper should measure whether nominal multiroute behavior really broadens exploration.
4. Claire McNamara, Lucy Hederman, Declan O'Sullivan. *The Initial Exploration Problem in Knowledge Graph Exploration*, arXiv:2602.21066. Pressure: orientation under scope uncertainty and ontology opacity is an existing conceptual navigation problem.
5. ORION-12 internal nearest work: AutoResearchBench, MetaSyn, SAGE, AgentSLR, systematic-review stopping, query diversification, capture-recapture and federated search. Pressure: route independence, route/task stopping and recall-first discovery are already ORION-12-owned.

### ORION-17 residual to test

The strongest current candidate is not generic navigation. It is:

`navigation over an evolving epistemic topology in which representation changes can alter reachability/frontier/route identity, while censored/open obligations remain distinct from stopping authority`.

A non-retrieval transfer domain is mandatory to show this is more than ORION-12 retrieval theory.

---

## ORION-18 — A Theory of Epistemic Authority for Autonomous Science

1. Xun Liu et al. *AgentAbstain: Do LLM Agents Know When Not to Act?*, arXiv:2607.10059. Pressure: agentic abstention is already a first-class evaluated capability; ORION-18 cannot claim novelty for knowing when not to act.
2. Ander Alvarez et al. *ProvenanceGuard: Source-Aware Factuality Verification for MCP-Based LLM Agents*, arXiv:2606.18037. Pressure: source-aware support, attribution and allow/block verification are direct authority/provenance neighbors.
3. Yiqi Wang et al. *From Agent Traces to Trust: Evidence Tracing and Execution Provenance in LLM Agents*, arXiv:2606.04990. Pressure: process-level evidence/provenance/audit is a broad established research programme.
4. Dynamic epistemic/deontic/action logic and belief-revision literature. Pressure: permission, obligation, informational action and revocation are mature formal concepts.
5. ORION-14 internal nearest work and protected V2 campaign. Pressure: ORION already owns a concrete, empirically supported non-compensatory scientific-authority transition; ORION-18 must not steal or dilute that claim.

### ORION-18 residual to test

The current hostile candidate is:

`a typed cross-capability authorization calculus for heterogeneous epistemic actions, with non-compensatory obligations, explicit CANNOT_CHECK/revocation, and prevention of cross-module authority laundering`.

The decisive comparison is against the existing independent ORION-11–ORION-15 authority gates, not against a weak confidence threshold.

---

## Cross-candidate literature rule

Every close work must be decomposed into atomic mechanics under #318. Whole-paper labels are insufficient. After each ADOPT/ADAPT/COMPOSE decision, recompute the candidate residual through #287. A candidate is allowed to collapse into ORION-11/ORION-12/ORION-14 or a technical companion if the literature shows that the abstraction itself is not a distinct publishable contribution.
