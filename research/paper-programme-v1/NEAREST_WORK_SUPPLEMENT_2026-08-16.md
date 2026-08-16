# Nearest-work supplement — 2026-08-16 flagship falsifier + journal-readiness round

This supplement records nearest work that materially changed the five-paper implementation or publication boundary after the V1 atlas was frozen. It follows the same rule: absorb the mechanism first, then shrink the ORION novelty boundary.

## Paper V — ADIAS: issue-centric self-improvement

**Work:** *Automated Design of Interactive Agentic Systems* (ADIAS), arXiv:2608.06410.

**Mechanism absorbed:** persistent issue-centric optimization. The durable object of improvement is the unresolved issue, with identity/lifecycle/evidence/intervention-outcome history carried across candidate generations.

**Disposition:** `ADAPT`.

**ORION implementation:** `src/orion/self_orion/issue_state.py` (`DevelopmentIssue.v1`). ORION keeps a stable issue identity, candidate/supported causes, discriminator evidence, failure episodes, interventions and lifecycle transitions. Harmful/null interventions remain attached to the issue.

**Removed from ORION novelty:** persistent issue identity/state for self-improvement is not claimed as novel.

## Paper V — structured/causal failure recovery is now nearest work

**Works:**
- *One Reflection Is Not Enough: Self-Correcting Autonomous Research via Multi-Hypothesis Failure Attribution*, arXiv:2606.31478.
- *CausalFlow: Causal Attribution and Counterfactual Repair for LLM Agent Failures*, arXiv:2605.25338.
- *Learning from Failure: Inference-Time Self-Improvement for Computer-Use Agents*, arXiv:2606.31270.
- *PAST-Bench: Benchmarking the Foundations of Recursive Self-Improvement in Personal Agents*, arXiv:2608.04003.
- *SEVA: Self-Evolving Verification Agent with Process Reward for Fact Attribution*, arXiv:2606.29713.

**Disposition:** `ADOPT/COMPOSE` as appropriate; exact executable-baseline mapping remains part of the external campaign.

**Removed/shrunk from ORION novelty:** failure-driven improvement, multi-hypothesis failure attribution, counterfactual causal attribution and retained-experience improvement cannot be standalone novelty claims.

**Surviving candidate:** persistent issue state + evidence-bound causal discrimination + invention readiness + replay and independent fresh transfer + protected assurance/evaluator custody + negative history + no self-certification/promotion. SEVA's cross-benchmark specialist regression strengthens the need to measure harmful/fresh transfer rather than replay performance alone.

## Paper IV — provenance/auditability/evaluator integrity

**Works/families absorbed:**
- ProvenanceGuard, arXiv:2606.18037;
- *From Fluent to Verifiable: Claim-Level Auditability for Deep Research Agents*, arXiv:2602.13855;
- ProvenAI, arXiv:2606.26449;
- search-time contamination, arXiv:2606.05241 and earlier STC work;
- RewardHackingAgents, arXiv:2603.11337;
- AttributionBench and CLAIM-BENCH.

**Disposition:** `COMPOSE`.

**Removed from ORION novelty:** source-aware factuality, semantic provenance/auditability, cited-vs-influential evidence decomposition, benchmark leakage detection and evaluator tampering detection are not ORION novelty claims.

**Surviving candidate:** a protected non-escalating scientific-authority transition requiring exact content/provenance + admissible checker lineage + evaluator/holdout integrity, with `CANNOT_CHECK/BLOCK` under unresolved prerequisites.

## Paper III — scientific semantic projection and structured integration

**Works/families absorbed:**
- MUSE, arXiv:2608.10974;
- SciSchema.org, arXiv:2607.27955;
- SCOPE/SCION schema induction and fusion, arXiv:2607.21610;
- Executable Schema Contracts, arXiv:2606.05415;
- SciER and scientific IE/discourse work.

**Disposition:** `ADAPT/COMPOSE`.

**Removed from ORION novelty:** source-grounded cross-domain structures, multidisciplinary scientific schemas, schema induction/fusion, provenance-aware shared-schema KGs and scientific IE are not sufficient novelty.

**Surviving candidate:** typed distinctions among referent, construct, context, measurement/operationalization and representation mappings; explicit GLUE-vs-obstruction/pluralism; source-projection recoverability; and reopening the relevance/search universe when an absorbed representation changes what should be searched.

The first exact atlas falsifier already showed that `SourceProjection` + `RepresentationMapping` alone left the text-to-scientific-meaning boundary implicit. `ScientificMeaningProjection.v1` remains the ORION representation for exposing that boundary, not a claim of inventing semantic parsing.

## Paper I — recursive research and evolving information state are now nearest work

**Works:**
- AREX, arXiv:2607.21461;
- SCION / *Rethinking Scientific Discovery in an Agentic Era*, arXiv:2607.03863;
- Iris / *Beyond Solution-Centric Search: Adaptive Inquiry and Knowledge Revision for Autonomous ML Engineering*, arXiv:2608.02143;
- SciAgentArena, arXiv:2606.12736, as an external evaluation family.

**Disposition:** `ADOPT/COMPOSE`.

**Removed/shrunk from ORION novelty:** recursive audit plus targeted follow-up, staged dependency-aware scientific plans, and explicit evolving information state/revisable claims are not standalone novelty claims.

**Surviving candidate:** explicit separation/co-evolution of `K/W/M` + typed responsibility-targeted formulation/search-universe revision + dependency-directed reopening of stale closure + mechanic-cell self-audit, tested specifically on hidden formulation/search-universe shifts and negative controls.

The earlier local failure remains important: singular responsibility was incorrectly treated as sufficient license for `REFRAME`; evidence/execution responsibility now routes to acquisition/execution repair rather than formulation rewrite.

## Paper II — external retrieval/SLR baselines have strengthened

**Works:**
- AutoResearchBench, arXiv:2604.25256;
- SAGE retrieval benchmark, arXiv:2602.05975;
- MetaSyn, arXiv:2606.17041;
- AgentSLR, arXiv:2603.22327;
- controlled AI-vs-human literature review in physics/astrophysics/cosmology, arXiv:2607.25672.

**Disposition:** `ADOPT` as benchmark/baseline evidence; `COMPOSE` for relevant retrieval/screening mechanisms.

**Removed from ORION novelty:** agentic literature search, end-to-end SLR automation and sophisticated retrieval are not novelty claims. Capture-recapture remains historical nearest work.

**Surviving candidate:** earned route independence, cumulative question-conditioned read state, typed route/task stopping, fail-closed coverage and recall-first promotion against strong simple baselines. SAGE makes the lexical baseline especially important; MetaSyn requires retrieval and screening error to be attributed separately.

## Publication consequence

The fresh 2026 literature does not collapse the five-paper programme, but it makes Papers I and V more compositional and raises the empirical bar for all five papers. No paper may promote a novelty or superiority statement solely because the local falsifier passes. The new per-paper `JOURNAL_READINESS.md` files and `JOURNAL_READINESS_STANDARD.md` define the remaining external programme.
