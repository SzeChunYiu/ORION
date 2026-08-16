# Five-paper journal-readiness audit — 2026-08-16

**Subject:** `SzeChunYiu/ORION@e96218032ad783164ee419e8a2a31b7688361b5c`  
**Authority:** research/planning audit. This document does not promote any external claim.

## Executive result

All five flagship papers have a coherent candidate residual after the existing nearest-work round, and the deterministic local falsifiers pass. None is yet `PEER_REVIEW_READY` because the external evidence gates remain `CANNOT_CHECK`.

The largest programme-level bottleneck is no longer missing architecture. It is prospective external evaluation, matched baselines, fresh gold/held-out data, statistical uncertainty, mechanism ablation and reproducible result artifacts.

A second bottleneck was manuscript asymmetry: Papers I and V had canonical manuscripts while Papers II–IV did not. This audit therefore treats manuscript completion as work that can be finished before external results, but results sections must remain explicitly open until the frozen studies run.

## Fresh nearest-work pressure discovered in this audit

### Paper I — Recursive Epistemic Reconstruction

New/updated closest work:

- **AREX: Towards a Recursively Self-Improving Agent for Deep Research** — arXiv:2607.21461. Constraint-wise auditing of provisional answers and targeted follow-up research means recursive follow-up/audit by itself is not a novelty claim.
- **SCION: Rethinking Scientific Discovery in an Agentic Era** — arXiv:2607.03863. Research Execution Plans make staged objectives, dependencies, verification checkpoints, artifacts, fallback conditions and memory explicit; staged/dependency-aware scientific orchestration is not novel.
- **Iris: Beyond Solution-Centric Search: Adaptive Inquiry and Knowledge Revision for Autonomous ML Engineering** — arXiv:2608.02143. An evolving information state with revisable claims and epistemic actions puts direct pressure on any broad "explicit evolving knowledge state" claim.
- **SciAgentArena** — arXiv:2606.12736. Provides about 200 real-world scientific-agent tasks with stepwise verification and exposes weakness on open-ended exploration; it is a candidate external benchmark family and a reminder that local synthetic success is insufficient.

Novelty consequence: Paper I should not claim recursive follow-up, structured research plans, dependency-aware orchestration, or an evolving information state as standalone novelty. The surviving candidate should be tested as the **composition** of explicit `K/W/M` separation, typed responsibility-targeted formulation/search-universe revision, dependency-directed invalidation/reopening, and recursively auditable mechanic contracts.

Primary blocker: fresh hidden-formulation/search-universe tasks against strong matched baselines, including ablations and current recursive-research/information-state agents.

### Paper II — Open-World Scientific Knowledge Discovery

New/updated closest work:

- **AutoResearchBench** — arXiv:2604.25256. Deep and Wide scientific-literature discovery remain extremely hard and provide a direct benchmark substrate.
- **SAGE: Benchmarking and Improving Retrieval for Deep Research Agents** — arXiv:2602.05975. On its scientific retrieval setting, BM25 can outperform LLM retrievers substantially; a strong lexical baseline is mandatory, not optional.
- **MetaSyn** — arXiv:2606.17041. Shows a retrieval ceiling does not imply inclusion/screening recall and supplies expert-curated positives/hard negatives and stage-attributed evaluation.
- **AgentSLR** — arXiv:2603.22327. End-to-end agentic systematic review automation is already being evaluated against expert-curated ground truth; full-workflow SLR automation is not an ORION novelty claim.
- **AI literature-review capability study in physics/astrophysics/cosmology** — arXiv:2607.25672. Human/AI selected-reference overlap was reported as very small in the controlled projects, reinforcing the need for recall/coverage evaluation rather than fluent synthesis scores.

Novelty consequence: agentic scientific search, SLR automation and retrieval sophistication are not novel. The surviving Paper-II candidate remains the governance combination: **earned route independence + question-conditioned cumulative read state + typed route-stop/task-stop separation + fail-closed coverage diagnostics + recall-first promotion against simple baselines**.

Primary blocker: frozen external Wide/Deep and complete-gold retrieval/screening experiments with provider/corpus versions, resource parity and stopping-error accounting.

### Paper III — Global Knowledge Portrait

New/updated closest work:

- **MUSE** — arXiv:2608.10974. Full-text cross-domain, source-grounded problem/solution/rationale structures mean source-grounded cross-domain structured knowledge is not novel.
- **SciSchema.org** — arXiv:2607.27955. Expert-annotated multidisciplinary scientific process schemas with parameters, conditions, measurements and provenance increase the baseline for structured scientific representation.
- **SCOPE and SCION (schema induction/fusion)** — arXiv:2607.21610. Evidence-linked conservative schema induction/fusion with benchmarked graph metrics puts pressure on generic schema-fusion novelty.
- **Executable Schema Contracts** — arXiv:2606.05415. Automatically discovered shared schema contracts, provenance-aware KGs and multi-source retrieval demonstrate another strong integration baseline.
- **SciER** — EMNLP 2024. Full-text scientific entity/relation extraction with an OOD split remains a useful semantic-extraction baseline.

Novelty consequence: source-grounded structured extraction, scientific schemas, schema induction/fusion and provenance-aware KGs are not sufficient novelty. The remaining candidate is the **typed distinction among referent/context/construct/measurement/representation hypotheses, explicit GLUE-versus-obstruction/pluralism, source-projection recoverability, and the ability for absorbed representations to reopen the relevance/search universe**.

Primary blocker: an independently annotated real cross-domain gold set measuring false merge, false contradiction, mapping, obstruction and recoverability—not only synthetic exact worlds.

### Paper IV — Verified Scientific Discovery

New/updated closest work:

- **ProvenanceGuard** — arXiv:2606.18037. Atomic claim decomposition, source-specific routing, support checking, attribution and cross-source conflation detection make source-aware factuality/provenance verification non-novel by itself.
- **From Fluent to Verifiable: Claim-Level Auditability for Deep Research Agents** — arXiv:2602.13855. Claim-level semantic provenance and auditability are explicitly proposed as first-class targets.
- **ProvenAI** — arXiv:2606.26449. Separates correctness, citation fidelity and behavioral influence; cited evidence and causally influential evidence are distinct.
- **Search-Time Contamination in Deep Research Agents** — arXiv:2606.05241. Public benchmark access during web search can inflate evaluation; contamination-aware logging/isolation is required.
- **RewardHackingAgents** — arXiv:2603.11337. Evaluator tampering and held-out leakage are benchmarked directly with patch/access telemetry and evaluator locking.
- **CLAIM-BENCH** — arXiv:2506.08235 / IJCNLP-AACL 2025. Scientific claim-evidence reasoning itself is a benchmarked task.

Novelty consequence: provenance, source-aware attribution, claim-level auditability, influence tracking, contamination detection and evaluator locking are not standalone ORION novelties. Paper IV's strongest remaining candidate is the **non-escalating authority transition** that requires content-bound evidence + admissible checker lineage + protected evaluator/holdout identity and returns `CANNOT_CHECK/BLOCK` when those conditions fail.

Primary blocker: the external hostile authority benchmark already represented by issue #59, extended with current nearest-work baselines and an explicit safety/coverage trade-off.

### Paper V — Self-ORION

New/updated closest work:

- **ADIAS** — arXiv:2608.06410. Persistent issue-centric self-improvement is already demonstrated and must remain outside ORION novelty.
- **SAGE: One Reflection Is Not Enough** — arXiv:2606.31478. Multi-hypothesis failure attribution and routing verified root causes to intervention levels means structured multi-hypothesis failure attribution is not novel by itself.
- **CausalFlow** — arXiv:2605.25338. Counterfactual/interventional responsibility scoring and minimal repairs directly pressure broad causal-attribution claims.
- **Learning from Failure: Inference-Time Self-Improvement for Computer-Use Agents** — arXiv:2606.31270. Failed trajectories are explicitly diagnosed and converted into agent improvements; "failure drives self-improvement" is not novel.
- **PAST-Bench** — arXiv:2608.04003. Tests whether retained experience actually improves later fresh-session behavior under matched retain/on-off conditions; useful for pathway-sensitive transfer evaluation.
- **SEVA** — arXiv:2606.29713. Iterative self-evolution produced benchmark specialists with cross-benchmark regressions, providing a concrete reason to treat fresh transfer/harmful transfer as first-class outcomes.
- **Darwin Gödel Machine / ADAS** remain strong self-editing/agent-design baselines.

Novelty consequence: persistent issue state, learning from failed trajectories, multi-hypothesis diagnosis and causal failure attribution should not be presented as standalone novelties. The surviving candidate must be tested as the **composition of issue persistence + evidence-bound causal discrimination + invention readiness + replay AND independent fresh transfer + protected evaluator/assurance + retained negative history + no self-certification/merge authority**.

Primary blocker: prospective hidden-cause development tasks and strong self-improvement baselines showing that these governance constraints improve transfer/integrity enough to justify their cost.

## Programme-wide remaining gates

1. **Literature closure:** rerun immediately before each submission because 2026 nearest work is moving quickly.
2. **External evidence:** all five papers require fresh tests against current strong baselines; local exact worlds establish semantics only.
3. **Ablation:** each claimed residual must be removed independently to show the effect is not coming from generic agent capability or extra compute.
4. **Statistics/uncertainty:** confidence intervals, effect sizes, multiple stochastic runs where relevant, power/precision planning and human-label agreement where relevant.
5. **Contamination/integrity:** frozen subject/evaluator/data identities; search-time leakage accounting for browsing agents; immutable negative/null results.
6. **Reproducibility:** clean-machine artifact, raw run manifests, scripts for every result figure/table and an independent reproduction of headline outputs.
7. **Reporting:** explicit limitations, threats to validity, safety/ethics, data/code availability, model/provider versions and cost/resource accounting.
8. **Journal fit:** final style/length/cover-letter work only after scientific closure; the scientific programme should not be distorted to fit a template prematurely.

## What can be completed before external runs

- manuscript scaffolding and related-work updates;
- explicit per-paper research questions/hypotheses;
- baseline and ablation matrix;
- frozen metric/plot/table specifications;
- dataset/annotation protocol specifications;
- artifact layout and run-manifest schema;
- preregistration/freeze documents;
- literature/claim-boundary updates.

## What cannot be completed without new evidence

- superiority claims;
- real-world construct validity;
- benchmark recall/coverage claims;
- cross-domain semantic integration adequacy;
- false-authority-promotion reduction;
- governed self-improvement/transfer benefit;
- final Results/Discussion conclusions.

Those items must remain `CANNOT_CHECK` until the experiments exist.
