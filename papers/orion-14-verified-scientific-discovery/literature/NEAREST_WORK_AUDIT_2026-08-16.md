# P4 nearest-work audit — refreshed 2026-08-17

Status: **SUBMISSION-LITERATURE SATURATION REFRESHED FOR THE CURRENT CLAIM BOUNDARY.**

This audit originated as the outcome-blind 2026-08-16 design audit and was refreshed on 2026-08-17 after the protected V2 result and readiness closure. The refresh does **not** reopen or retroactively edit `P4.protected-authority.v1`; new work is mapped only to baseline families, attack families, threat-model context, or novelty boundaries that were already frozen. If a newly found paper required a new primary metric, attack family, or authority rule, the correct response would be a new protocol version rather than editing the frozen V1 design.

The saturation stop rule for this refresh was functional rather than count-based: searches were repeated across scientific verification, provenance/research integrity, abstention/refusal, benchmark/evaluator auditing, protected evaluation/assurance, and contamination-resistant evaluation until additional hits either (a) mapped to an already represented mechanism family without changing the manuscript boundary or (b) were domain-specific neighbors with no direct P4 consequence. Six papers materially sharpened reviewer-facing boundaries and were added to the manuscript bibliography; one recent contamination-control benchmark was screened and explicitly deferred rather than added as padding.

## Disposition vocabulary

- `ADOPT`: use directly as a benchmark/baseline family or comparison target.
- `ADAPT`: reuse a mechanism or attack model with P4-specific bindings.
- `COMPOSE`: treat as an existing component that P4 combines; explicitly not standalone novelty.
- `DEFER`: relevant neighbor but not a justified V1 baseline/change.
- `REJECT`: not relevant enough or would violate the frozen design boundary.

## Audited nearest work

| Work | Verification | Disposition | P4 consequence |
|---|---|---|---|
| ProvenanceGuard, arXiv:2606.18037 | primary arXiv record/full text checked | `ADOPT` | Strong source-aware verifier; cross-source conflation and source ownership are not P4 novelty. Maps to frozen `provenanceguard_like_source_aware_verifier`. |
| AttributionBench, Findings of ACL 2024, doi:10.18653/v1/2024.findings-acl.886 | primary publication metadata checked in existing bibliography | `ADOPT` | Direct attribution-evaluation baseline; attribution accuracy is separate from semantic support and authority. |
| AAR / claim-level auditability, arXiv:2602.13855 | primary arXiv record already bound in manuscript | `COMPOSE` | Semantic provenance/auditability is an existing component, not standalone novelty. |
| ProvenAI, arXiv:2606.26449 | primary arXiv record already bound in manuscript | `COMPOSE` | Correctness, citation fidelity and behavioral influence remain distinct coordinates; behavioral influence is not standalone novelty. |
| FIRE: Fact-checking with Iterative Retrieval and Verification, arXiv:2411.00784 | primary arXiv full text checked 2026-08-16 | `ADOPT` | Concrete implementation target for the already-frozen `iterative_retrieve_or_verify` family; no protocol change required. |
| CLAIM-BENCH, arXiv:2506.08235 | primary arXiv record checked | `ADOPT` | Scientific claim-evidence comprehension benchmark; does not establish protected scientific authority. |
| RewardHackingAgents, arXiv:2603.11337 | primary arXiv record already bound in manuscript | `ADAPT` | Evaluator tampering and held-out leakage are direct attack coordinates; P4 adds exact custody/binding rather than claiming tamper detection as novel. |
| Search-Time Contamination, arXiv:2606.05241 | primary arXiv record already bound in manuscript | `ADAPT` | Search leakage is an existing failure mode; P4's frozen contamination gate/telemetry composes it into authority admissibility. |
| BenchGuard: Who Guards the Benchmarks?, arXiv:2604.24955 | primary arXiv record checked 2026-08-16 | `COMPOSE` | Benchmark/evaluator infrastructure itself needs auditing. This supports independent review of the protected evaluator but is not a P4 outcome baseline. |
| Certified Speculative Execution for Untrusted AI Agents, arXiv:2606.31023 | primary arXiv record checked 2026-08-16 | `COMPOSE` | Certificate-gated acceptance of untrusted proposals is a strong parent-domain precedent for fail-closed gating; domain/task differs, so it is not a direct P4 baseline. |
| FactArena: Towards Comprehensive Stage-wise Benchmarking of Large Language Models in Fact-Checking, arXiv:2601.02669 | primary arXiv record checked 2026-08-16 | `DEFER` | Strong stage-wise fact-checking evaluation neighbor. It reinforces end-to-end evaluation but does not test protected evaluator/holdout authority transitions. |
| DeepSciVerify: Verifying Scientific Claim--Citation Alignment via LLM-Driven Evidence Escalation, arXiv:2605.27710 | primary arXiv full text checked 2026-08-16 | `ADAPT` | Strong current scientific claim-citation verifier with selective abstract-to-full-text escalation; maps inside the frozen iterative/scientific-verification baseline family. It is a comparison component, not evidence for P4's authority claim. |
| Scientific Claim-Source Retrieval Revisited: A Comparative Study of Style Transfer and Re-Ranking, arXiv:2607.15875 | primary arXiv record checked 2026-08-16 | `ADOPT` | Current CheckThat! 2026 claim-source retrieval evidence reinforces that source retrieval/ownership deserves a separate coordinate from semantic support. Fits existing source-aware baseline scope. |
| SciIntegrity-Bench, arXiv:2605.10246 | primary arXiv record checked 2026-08-17 | `ADAPT` | Makes honest acknowledgment of inability the correct outcome in academic-integrity dilemmas. It strengthens the case that refusal/abstention must be evaluated as a positive integrity behavior, while P4 remains narrower: authority escalation is gated by exact source/checker/evaluator prerequisites. |
| AgentAbstain, arXiv:2607.10059 | primary arXiv record checked 2026-08-17 | `ADAPT` | Paired should-act/should-abstain executable tasks show that abstention is distinct from generic task-solving ability. P4's `CANNOT_CHECK/BLOCK` terminals are therefore positioned as authority-specific abstention semantics, not a claim to general agentic abstention. |
| Automated Benchmark Auditing for AI Agents and Large Language Models, arXiv:2605.26079 | primary arXiv record checked 2026-08-17 | `COMPOSE` | Large-scale benchmark auditing finds specification, environment and grading defects that can materially alter rankings. Supports P4's insistence that evaluator/harness admissibility is itself part of evidence authority, not an invisible assumption. |
| Holistic Agent Leaderboard, arXiv:2510.11977 | primary arXiv record checked 2026-08-17 | `COMPOSE` | Standardized multi-benchmark harnessing plus trace inspection exposes benchmark-search behavior and evaluation-path artifacts. Reinforces search/evaluation telemetry and benchmark-integrity context; not a direct authority baseline. |
| INSPECT-AI / RIPE-O / RIPE-KG, arXiv:2608.07202 | primary arXiv record checked 2026-08-17 | `COMPOSE` | Provides a current research-integrity parent-domain example where provenance of the assessment process is represented explicitly and linked to expert assessments. P4 does not claim provenance ontologies or research-integrity KGs as novel. |
| Behavioral Integrity Verification for AI Agent Skills, arXiv:2605.11770 | primary arXiv record checked 2026-08-17 | `COMPOSE` | Formalizes declared-vs-actual capability mismatch as a typed integrity-verification problem. This is a useful parent-domain analogue for checking that authority artifacts and evaluator behavior match declared contracts; it is not a scientific-claim verifier. |
| SRE-Bench, arXiv:2608.11469 | primary arXiv record checked 2026-08-17 | `DEFER` | Strong contamination-controlled benchmark construction using private from-scratch instances, but the task domain is reverse engineering and the contribution is benchmark freshness rather than scientific-authority transitions. Screened as contamination-method context; not added to the P4 manuscript bibliography. |

## Saturation conclusions by reviewer-facing question

- **"Is this just provenance or source-aware factuality?"** Closed by AttributionBench, ProvenanceGuard, AAR, ProvenAI, INSPECT-AI/RIPE-KG, and the claim-source retrieval line. P4 explicitly composes these rather than claiming them.
- **"Is this just fact checking or evidence escalation?"** Closed by FIRE, CLAIM-BENCH, FactArena, DeepSciVerify, and the scientific claim-source retrieval work. P4's empirical object remains the authority terminal after those components.
- **"Is `CANNOT_CHECK` just generic refusal?"** Closed more explicitly by SciIntegrity-Bench and AgentAbstain. They establish refusal/abstention as a distinct evaluation target; P4's H3 null is retained and P4 claims only authority-specific non-escalation.
- **"Who verifies the benchmark/evaluator?"** Closed by BenchGuard, Automated Benchmark Auditing, HAL, RewardHackingAgents, and certified speculative execution as parent-domain pressure. P4's contribution is the exact frozen custody/admissibility composition and protected execution, not automated benchmark auditing itself.
- **"What about declared-vs-actual integrity and process provenance?"** Closed by Behavioral Integrity Verification plus INSPECT-AI/RIPE-KG and AAR. These strengthen the contract/provenance parent domain without displacing P4's scientific-authority transition.
- **"What about contamination-resistant evaluation?"** Closed by Search-Time Contamination as the direct deep-research failure mode; HAL and SRE-Bench were also screened. SRE-Bench is deliberately deferred because it changes benchmark construction, not the P4 authority mechanism.

## Issue #101 Step-1 closure mapping

- ProvenanceGuard / source-aware factuality + conflation: **closed**.
- AttributionBench / multi-source attribution: **closed**.
- claim-level semantic provenance/auditability/AAR: **closed**.
- ProvenAI / correctness vs citation fidelity vs behavioral influence: **closed**.
- FIRE / iterative retrieve-or-verify: **closed** by direct primary-source audit and mapping to the frozen baseline family.
- CLAIM-BENCH / strongest scientific claim-evidence benchmarks: **closed**; DeepSciVerify and the 2026 claim-source retrieval work are also recorded as current neighbors.
- RewardHackingAgents / evaluator tampering + held-out leakage: **closed**.
- Search-Time Contamination / web benchmark leakage: **closed**.
- abstention/refusal as a positive integrity behavior: **closed for the authority-specific boundary** via SciIntegrity-Bench and AgentAbstain; no general abstention superiority is claimed.
- secure evaluation / trusted execution / assurance / independent verification: **closed at the design/nearest-work boundary** via BenchGuard, Automated Benchmark Auditing, HAL, Behavioral Integrity Verification, and certificate-gated untrusted-agent work.
- research-integrity provenance parent domain: **closed for the submission boundary** via INSPECT-AI/RIPE-O/RIPE-KG plus AAR/ProvenAI.
- current 2026+ scientific fact-checking/provenance systems: **closed through the 2026-08-17 saturation refresh** with FactArena, DeepSciVerify, ProvenanceGuard, BenchGuard, INSPECT-AI/RIPE-KG, and the CheckThat! 2026 claim-source retrieval study.

All audited items have an explicit terminal disposition above. The residual novelty boundary remains: **a non-escalating scientific-authority transition requiring exact content/provenance binding, admissible checker lineage, and protected evaluator/holdout identity, with `CANNOT_CHECK/BLOCK` under unresolved prerequisites.** Provenance, attribution, fact-checking, auditability, abstention benchmarking, contamination detection, benchmark auditing, behavioral-integrity auditing, research-integrity provenance, and certificate-gated verification are not standalone P4 novelty claims.

## Reopen triggers

Reopen this audit before submission if any of the following occurs:

1. a post-2026-08-17 system directly implements the full protected non-escalating authority transition;
2. a new scientific-verification system materially dominates the frozen baseline families and can be mapped without changing the primary design;
3. a new evaluator-integrity result invalidates the custody assumptions in `CUSTODY_POLICY_V1.md`;
4. final submission occurs more than 14 days after this refresh without a fresh search.
