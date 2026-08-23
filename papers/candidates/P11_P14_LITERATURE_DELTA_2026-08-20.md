# P11–P14 Literature Delta — 2026-08-20

**Status:** current-search donor subtraction for the publication-candidate package  
**Scope:** P11 state construction, P12 adaptive state/reasoning allocation, P13 responsibility-safe state reuse, P14 research-agent governance  
**Search date:** 2026-08-20

## Search method

The search was run as a venue-agnostic multi-source literature delta, following the `nature-academic-search` and `nature-ref-verifier` principles: atomic queries, recent-source discovery, primary paper/proceedings pages where available, identifier capture, and claim subtraction rather than citation accumulation.

Search concepts included:

- state representation + dynamic LLM reasoning;
- query-conditioned memory/user-state inference;
- long-horizon context compression;
- adaptive test-time compute allocation;
- certified answer/state reuse;
- stale agent memory and revision;
- agent provenance / proof-carrying actions;
- autonomous scientific research agents and exploration breadth.

The delta is deliberately adversarial: each item is recorded for what it **removes** from ORION’s novelty space before what it supports.

## P11 donor delta

### Xu et al. — predictive V-information

**Yilun Xu, Shengjia Zhao, Jiaming Song, Russell Stewart, Stefano Ermon.** *A Theory of Usable Information Under Computational Constraints.* ICLR 2020; arXiv:2002.10689.

**Owns:** computationally restricted usable information and the fact that computation can create predictive V-information.

**Subtraction:** P11 cannot claim that equal Shannon information may differ in usability, or that computation can make information more usable.

**Residual:** explicit location/cost of that work across compiler, state, decoder/search, cache/recovery and verifier.

### Wong et al. — state design effects

**Annie Wong, Aske Plaat, Thomas Bäck, Niki van Stein, Anna V. Kononova.** *State Design Matters: How Representations Shape Dynamic Reasoning in Large Language Models.* arXiv:2602.15858 (2026).

**Owns:** holding model parameters fixed while varying state granularity/structure/grounding and showing material reasoning effects; also explicitly notes that constructing a representation can itself induce useful reasoning.

**Subtraction:** “state representation matters to LLM reasoning” and “construction can induce computation” are not P11 novelty claims.

**Residual:** theorem-backed query-family rank/accessibility results, non-laundering controls, costed compiler/decoder substitution and optionality phase laws.

### QUMem — query-conditioned state inference

**Heng Wang, Yifei Li, Lingling Zhang, Pengyu Li, Xinyu Che, Xinyu Zhang, Zesheng Yang.** *QUMem: Personalized Memory for Query-Conditioned User-State Inference in LLM Agents.* arXiv:2608.16168 (2026-08-17).

**Owns:** query-conditioned user-state inference over typed episodic memory with planned multi-query retrieval.

**Subtraction:** conditioning memory/state on the current query is explicitly prior-owned and extremely current.

**Residual:** rank lower bounds for fixed readout families, no-answer-laundering, resource accounting and future-query option/recoverability laws.

### ACON — long-horizon context compression

**Minki Kang, Wei-Ning Chen, Dongge Han, Huseyin A. Inan, Lukas Wutschitz, Yanzhi Chen, Robert Sim, Saravan Rajmohan.** *ACON: Optimizing Context Compression for Long-horizon LLM Agents.* ICML 2026; arXiv:2510.00615.

**Owns:** optimizing observation/history compression for long-horizon agents and measuring memory/performance tradeoffs.

**Subtraction:** context compression and learned compression policies are not P11 primitives.

**Residual:** current accessibility versus future optionality/recoverability plus compiler/cache/materialize accounting.

## P12 donor delta

### Strategic Scaling of Test-Time Compute

**Bowen Zuo, Yinglun Zhu.** *Strategic Scaling of Test-Time Compute: A Bandit Learning Approach.* ICLR 2026.

**Owns:** learned/adaptive allocation of test-time compute across queries under finite resources, including query-difficulty/solvability adaptation.

**Subtraction:** P12 cannot claim adaptive inference-budget allocation.

### Adaptive Test-Time Compute Allocation with Evolving In-Context Demonstrations

**Bowen Zuo, Dongruo Zhou, Yinglun Zhu.** *Adaptive Test-Time Compute Allocation with Evolving In-Context Demonstrations.* Findings of ACL 2026, 35156–35173. DOI `10.18653/v1/2026.findings-acl.1754`.

**Owns:** adaptive placement of test-time compute and adaptive generation conditioning in one inference framework.

**Subtraction:** even “jointly adapt where compute is spent and how generation is performed” is not enough to distinguish P12.

### Adaptive Test-Time Compute Allocation for Reasoning LLMs via Constrained Policy Optimization

**Zhiyuan Zhai, Bingcong Li, Bingnan Xiao, Ming Li, Xin Wang.** *Adaptive Test-Time Compute Allocation for Reasoning LLMs via Constrained Policy Optimization.* arXiv:2604.14853 (2026).

**Owns:** constrained accuracy-under-average-compute optimization, oracle allocation and learned imitation of oracle actions.

**Subtraction:** oracle-regret and learned compute-allocation framing are crowded.

**P12 residual after subtraction:** the allocation variable must include a genuinely distinct, costed **state-construction action** plus downstream reasoning/search, with the compiler’s work/state/cache/recovery charged inside the same total resource boundary. The paper needs held-out regime crossovers and strict superiority over both adaptive-compute-only and adaptive-state-only baselines.

## P13 donor delta

### Safety as Computation — certified answer reuse

**Cosimo Spera.** *Safety as Computation: Certified Answer Reuse via Capability Closure in Task-Oriented Dialogue.* arXiv:2603.21448 (2026).

**Owns/pressures:** certified reuse, provenance witnesses and pre-materialized reusable answers under a capability-closure view.

**Subtraction:** “certify state/answer reuse” and “attach provenance witnesses to reusable results” are not sufficient novelty claims for P13.

**Residual:** responsibility-relative state scope, explicit unsupported responsibilities/omissions, recoverability/reopen semantics under responsibility change, and a safety–cost comparison against confidence/provenance/always-reopen baselines.

### STALE — memory invalidation under implicit change

**Hanxiang Chao, Yihan Bai, Rui Sheng, Tianle Li, Yushi Sun.** *STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?* arXiv:2605.06527 (2026).

**Owns/pressures:** detecting that prior memories become invalid after later observations and measuring downstream behavior under implicit conflicts.

**Subtraction:** stale-memory detection and update-aware memory by themselves are not P13 contributions.

**Residual:** responsibility-specific sufficiency certificates and reopen decisions that distinguish “state is stale” from “state is current but insufficient for this new responsibility.”

### From Agent Traces to Trust

**Yiqi Wang, Jiaqi Zhang, Taotao Cai, Zirui Liu, Qingqiang Sun, Zequn Sun, Zhangkai Wu, Mingkai Zhang, Yanming Zhu.** *From Agent Traces to Trust: Evidence Tracing and Execution Provenance in LLM Agents.* arXiv:2606.04990 (2026).

**Owns/pressures:** execution/evidence provenance as a broad accountability layer, including memory lineage, audit and recovery.

**Subtraction:** provenance-bearing state is not P13 novelty.

### Proof-Carrying Agent Actions

**Zexun Wang.** *Proof-Carrying Agent Actions: Model-Agnostic Runtime Governance for Heterogeneous Agent Systems.* arXiv:2606.04104 (2026).

**Owns/pressures:** portable certificate-bearing agent actions and runtime governance.

**Subtraction:** portable certificates and explicit approval/evidence receipts are prior art near P13’s contract language.

**P13 residual after subtraction:** the paper must show that a compact state’s certificate is keyed to a **named downstream responsibility** and prospectively prevents unsafe reuse when responsibilities change, with explicit omissions, resource envelope, recovery/reopen conditions and external witness/authority separation. Efficacy must beat confidence-only/provenance-only controls without degenerating to always reopen.

## P14 donor delta

### SAGA — autonomous goal-evolving scientific agents

**Yuanqi Du et al.** *Accelerating Scientific Discovery with Autonomous Goal-evolving Agents.* arXiv:2512.21782 (2025; 2026 workshop records also exist).

**Owns/pressures:** recursive/outer-loop scientific-agent goal reformulation and autonomous scientific design workflows.

**Subtraction:** recursive or goal-evolving AI research itself is not ORION-RSE novelty.

### Tang & Yang — research-agent exploration breadth

**Yixuan Tang, Yi Yang.** *AI Research Agents Narrow Scientific Exploration.* arXiv:2605.27905 (2026-05-27).

**Owns/pressures:** direct comparative evaluation of research agents as scientific search systems, including exploration concentration and proximity to prior work.

**Subtraction:** P14 must not rely on a generic story that research agents need evaluation or may narrow exploration.

**Residual:** a matched governance intervention whose endpoints are scientific **dispositions**—false promotion/overclaim, donor-subsumption, protocol drift, negative-history use, correct inability-to-check and later-round reopening—subject to useful-discovery noninferiority.

## Cross-paper consequences

1. **P11 title/claim remains viable only with explicit donor subtraction.** The strong claim is not representation matters, query conditioning, compression or useful information; it is the measured cost/optionality frontier for state construction under bounded downstream access.
2. **P12 is a crowded allocation paper unless state construction is an independently costed action.** Current adaptive-compute papers already use constrained optimization, oracle allocation, learned policies and adaptive generation.
3. **P13 must distinguish responsibility scope from staleness, confidence and provenance.** Recent certified-reuse, stale-memory and provenance work makes this a mandatory discriminator, not optional related work.
4. **P14 must evaluate governance, not recursive research.** Current scientific-agent work already owns recursive/goal-evolving research and direct evaluation of research-agent exploration.

## Reference verification status

### Metadata independently checked in this delta

- Xu et al. — arXiv:2002.10689, authors/title/year matched.
- Wong et al. — arXiv:2602.15858, authors/title/year matched.
- QUMem — arXiv:2608.16168, authors/title/date matched.
- ACON — Microsoft Research lists ICML 2026; arXiv:2510.00615.
- Zuo, Zhou & Zhu — ACL Anthology lists Findings ACL 2026, pp. 35156–35173, DOI `10.18653/v1/2026.findings-acl.1754`.
- Tang & Yang — arXiv:2605.27905, authors/title/date matched.
- SAGA — arXiv:2512.21782; author list/version should be normalized from the final chosen record before submission because current public records show version-dependent author-list differences.
- STALE — arXiv:2605.06527.
- From Agent Traces to Trust — arXiv:2606.04990.
- Proof-Carrying Agent Actions — arXiv:2606.04104.
- Safety as Computation — arXiv:2603.21448.

### Submission-time action

Run one final citation-verification sweep over the manuscripts after the reference lists are consolidated. Replace preprints with archival versions where available; compare title, full author order, year, venue, pages and DOI field-by-field. A 2026 paper should never be promoted from a stale local citation if a peer-reviewed record has appeared.
