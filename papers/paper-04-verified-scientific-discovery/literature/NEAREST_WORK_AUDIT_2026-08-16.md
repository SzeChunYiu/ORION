# P4 nearest-work audit — 2026-08-16

Status: **PUBLIC-LITERATURE CLOSED FOR CURRENT DESIGN; EXECUTION CLAIMS REMAIN `CANNOT_CHECK`.**

This audit is outcome-blind and does not modify `P4.protected-authority.v1`. New work is mapped only to baseline families, attack families, or novelty boundaries that were already frozen. If a newly found paper required a new primary metric, attack family, or authority rule, the correct response would be a new protocol version rather than editing the frozen V1 design.

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

## Issue #101 Step-1 closure mapping

- ProvenanceGuard / source-aware factuality + conflation: **closed**.
- AttributionBench / multi-source attribution: **closed**.
- claim-level semantic provenance/auditability/AAR: **closed**.
- ProvenAI / correctness vs citation fidelity vs behavioral influence: **closed**.
- FIRE / iterative retrieve-or-verify: **closed** by direct primary-source audit and mapping to the frozen baseline family.
- CLAIM-BENCH / strongest scientific claim-evidence benchmarks: **closed**; DeepSciVerify and the 2026 claim-source retrieval work are also recorded as current neighbors.
- RewardHackingAgents / evaluator tampering + held-out leakage: **closed**.
- Search-Time Contamination / web benchmark leakage: **closed**.
- secure evaluation / trusted execution / assurance / independent verification: **closed at the design/nearest-work boundary** via BenchGuard plus certificate-gated untrusted-agent work; empirical independent P4 execution remains open.
- current 2026+ scientific fact-checking/provenance systems: **closed for the 2026-08-16 pre-execution audit** with FactArena, DeepSciVerify, ProvenanceGuard, BenchGuard, and the CheckThat! 2026 claim-source retrieval study.

All audited items have an explicit terminal disposition above. The residual novelty boundary remains: **a non-escalating scientific-authority transition requiring exact content/provenance binding, admissible checker lineage, and protected evaluator/holdout identity, with `CANNOT_CHECK/BLOCK` under unresolved prerequisites.** Provenance, attribution, fact-checking, auditability, contamination detection, benchmark auditing, and certificate-gated verification are not standalone P4 novelty claims.

## Reopen triggers

Reopen this audit before submission if any of the following occurs:

1. a post-2026-08-16 system directly implements the full protected non-escalating authority transition;
2. a new scientific-verification system materially dominates the frozen baseline families and can be mapped without changing the primary design;
3. a new evaluator-integrity result invalidates the custody assumptions in `CUSTODY_POLICY_V1.md`;
4. final submission occurs more than 14 days after this audit without a fresh search.
