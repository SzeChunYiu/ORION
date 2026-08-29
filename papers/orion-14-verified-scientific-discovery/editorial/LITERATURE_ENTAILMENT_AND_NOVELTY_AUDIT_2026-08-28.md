# ORION-14 literature entailment and novelty audit — 2026-08-28

Tracking: #1609 / PR #1610  
Purpose: current-source audit for the Wave-1 recursive `academic-paper-pipeline`.  
Rule: source existence and topical similarity are not enough; the cited primary source must entail the proposition assigned to it. A bounded search can fail to locate a collision but cannot certify novelty.

## Current primary-source entailment

| Citation | Primary record checked | Manuscript proposition | Disposition |
|---|---|---|---|
| AttributionBench (2024) | ACL Anthology `2024.findings-acl.886` | automatic attribution evaluation is a distinct benchmarked problem | ENTAILS |
| ProvenanceGuard (2026) | arXiv:2606.18037 v2 | source-aware factuality targets cross-source conflation | ENTAILS |
| CLAIM-BENCH (2025) | arXiv:2506.08235 | scientific claim-to-evidence extraction/validation is benchmarked separately | ENTAILS |
| Scientific Claim-Source Retrieval Revisited (2026) | arXiv:2607.15875 | identifying a claim's underlying source is a retrieval problem distinct from generic semantic support | ENTAILS |
| Provenance Sensitivity audit (2026) | arXiv:2607.20827 | evidence can be relevant yet unauthorized to determine an agent action; source authority can be varied while task/proposition are held fixed | ENTAILS |
| Partial Evidence Bench (2026) | arXiv:2605.05379 | correct access control can coexist with unsafe overclaiming when evidence is outside the authorized view | ENTAILS |
| AuthGraph (2026) | arXiv:2605.26497 | execution provenance can be structurally aligned against an authorization graph at tool/parameter-source level | ENTAILS |
| FAVA (2026) | arXiv:2607.27267 | evidence-backed permission graphs plus formal pre-action authorization are existing work | ENTAILS |
| Cryptographically Verifiable Authorization (2026) | arXiv:2607.21325 | principal/request/context/policy bindings are an explicit formal authorization research direction | ENTAILS |
| AAR / claim-level auditability (2026) | arXiv:2602.13855 | claim-level auditability and semantic provenance are explicit research-agent evaluation/design targets | ENTAILS |
| ProvenAI (2026) | arXiv:2606.26449 | citation fidelity and behavioral influence are independently measurable layers | ENTAILS |
| INSPECT-AI / RIPE-KG (2026) | arXiv:2608.07202 | research-integrity assessment provenance is represented as an auditable knowledge object | ENTAILS |
| Behavioral Integrity Verification (2026) | arXiv:2605.11770 | declared-vs-actual capability/integrity is formalized and measured for agent skills | ENTAILS |
| Certified Speculative Execution (2026) | arXiv:2606.31023 | untrusted agent proposals can be held behind a trusted certificate/check before effectful acceptance | ENTAILS |
| FIRE (2024/2025) | arXiv:2411.00784 v2 | retrieval and verification can be iterated rather than fixed to one evidence pass | ENTAILS |
| DeepSciVerify (2026) | arXiv:2605.27710 | scientific claim-citation verification can escalate from abstract to fuller evidence when initial evidence is insufficient | ENTAILS |
| FactArena (2026) | arXiv:2601.02669 | stage-wise fact-checking evaluation separates pipeline stages rather than only end-to-end verdicts | ENTAILS |
| RewardHackingAgents (2026) | arXiv:2603.11337 | evaluator tampering and held-out leakage are explicit agent-benchmark integrity dimensions | ENTAILS |
| Search-Time Contamination (2026) | arXiv:2606.05241 | web-searching research agents can retrieve benchmark material during inference and inflate evaluation | ENTAILS |
| BenchGuard (2026) | arXiv:2604.24955 | benchmark specifications/environments/evaluation logic can themselves contain consequential defects | ENTAILS |
| Automated Benchmark Auditing (2026) | arXiv:2605.26079 | automated auditing finds specification/environment/ground-truth/grading defects that alter capability assessment | ENTAILS |
| Holistic Agent Leaderboard (2025) | arXiv:2510.11977 | standardized harnessing and trace inspection expose evaluation artifacts including benchmark searching | ENTAILS |
| SciIntegrity-Bench (2026) | arXiv:2605.10246 | academic-integrity scenarios can make honest acknowledgement of inability the correct behavior | ENTAILS |
| AgentAbstain (2026) | arXiv:2607.10059 | paired executable tasks benchmark when agents should act versus abstain | ENTAILS |

## Fresh nearest-neighbor pressure

The 2026 authorization literature is closer to ORION-14 than the earlier manuscript framing acknowledged. In particular:

1. **Partial Evidence Bench** already owns the idea that an agent can comply with access restrictions yet overstate completeness when material evidence is outside its authorized view.
2. **AuthGraph** already owns a structural provenance-versus-authorization comparison for tool actions and parameter sources.
3. **FAVA** already owns evidence-backed permission graphs checked by formal authorization before effectful execution.
4. **Cryptographically Verifiable Authorization** already frames authorization as a relation binding principal, request, execution context, policy, and evidence.
5. **Provenance Sensitivity** already directly distinguishes relevant evidence from evidence authorized to determine an action.

Therefore ORION-14 must **not** claim novelty for provenance-aware authorization, evidence-backed authorization, generic permission graphs, the relevance/authorization distinction, or generic abstention.

## Residual contribution after subtraction

The surviving contribution is narrower:

- a formal **measurement boundary** for exact-terminal verification axes using fibrewise Bayes risk, target factorization, terminal attainability, nuisance identifiability, and panel resolution;
- a protected finite result showing that the frozen non-compensatory scientific-promotion relation has 0/360 false promotions where the strongest frozen mechanism proxy has 180/360, while preserving the V2 H3 saturation failure;
- a distinct V3 result interpreted only as terminal/interface attainability;
- P4-X's donor-complete pressure test: after provenance, verification, custody, artifact/version/epoch handling and generic authorization are granted, the target-bound scientific-promotion relation remains distinct on the registered exact contracts, while an information-equivalent typed product ties exactly and therefore defeats any centralization/unique-expressivity claim.

## Bounded collision search

Fresh 2026 searches were run over combinations of:

- research-agent verification / scientific claims / provenance;
- authorization-limited evidence;
- benchmark auditing / abstention / evaluation integrity;
- formal and cryptographic agent authorization;
- scientific claim verification and source/evidence alignment.

Adjacent current work includes forward-looking research-judgement evaluation, provenance-attribution benchmarks, and audit-closed AI-scientist infrastructure. None located in this bounded pass combines the exact ORION-14 residual above: an attainability/identifiability theory for verification axes with the V2/V3/P4-X scientific-promotion experiments and the donor-complete typed-product boundary.

Disposition: `NOT_LOCATED_IN_BOUNDED_CURRENT_SEARCH__NOT_NOVELTY_CERTIFICATE`.

## Manuscript action taken

`manuscript/sections/02-related-work.tex` was revised to absorb Partial Evidence Bench, AuthGraph, FAVA and cryptographically verifiable authorization explicitly. The revised paragraph says these works consume generic authorization novelty and states the narrower residual question.

## Remaining literature gate

- [x] current primary records checked for every citation used by the revised Related Work section;
- [x] generic authorization novelty subtracted;
- [x] current adjacent/nearest-neighbor search executed;
- [ ] bibliography metadata normalization/full-author cleanup where needed;
- [ ] final 48-hour submission-date search if filing occurs materially after 2026-08-28.

Literature terminal: `CURRENT_POSITIONING_SUPPORTED_WITH_BOUNDED_NONCOLLISION__FINAL_FILING_REFRESH_PENDING`.
