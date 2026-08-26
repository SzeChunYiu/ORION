# ORION Negative-Results Revival Backlog V1

**Date:** 2026-08-17  
**Status:** SATURATION_COMPLETE  
**Operator Directive:** Fix ALL negative/non-positive results in all papers + all failing tests. ORION-style: root cause → understand mechanism → saturate literature → design mechanic improvement → re-test. Never tune outcomes positive; global positivity is earned via mechanic improvement.

## Doctrine

A negative is **INTERMEDIATE**, never terminal. For each negative:
1. **Attribute failure to ONE stage** (never diffuse)
2. **Identify the matching revival lever** (mechanic improvement — retrieval, execution, evaluation access, sample size, experimental design)
3. **Survey the literature** for the strongest known fix
4. **Design a concrete experiment** someone could run next week

**Forbidden:** Tuning outcomes positive, loosening gates, rewording prose to soften a null.

---

## NEGATIVE #001: P1 H2 Non-Inferiority Underpowered

| Field | Value |
|-------|-------|
| **Paper** | P1 — Recursive Epistemic Reconstruction |
| **Claim ID** | P1.H2 — Unnecessary-reframe non-inferiority at +0.02 margin |
| **Current Verdict** | `UNDERPOWERED` / `NOT_CERTIFIABLE` |
| **Evidence Artifact** | `papers/orion-11/protocol/PROSPECTIVE_POWER_V1.md` (48 TEST cases, 16 controls) |
| **One-Stage Attribution** | **Sample size** — The +0.02 margin is 5-7x tighter than the narrowest achievable CI upper bound at n=16 controls. Even with zero unnecessary reframes in both systems (diff=0), the 95% CI upper bound is +0.074 to +0.147. Near-zero power. |
| **Root Cause** | Protocol design specified an overly tight margin for the available control sample size. The H1 superiority test (32 hidden-shift cases) is adequately powered, but H2's margin is mechanically unreachable. |
| **Revival Lever** | **Sample expansion ONLY** — Expand controls to 30+ cases (TIER_B, n=385). Margin relaxation is FORBIDDEN (outcome tuning). The frozen +0.02 margin stays. If H2 stays unreachable at full expansion, it is documented as CORRECTED-with-power-analysis, not margin-relaxed. Rationale: p1-expand is already building the assisted +337-case pipeline → n=385 (TIER_B). |
| **Re-Test Plan** | **Staged expansion (margin FROZEN at +0.02):** <br>1. Expand the suite by +337 cases to pre-declared n=385 (TIER_B) — in flight (p1-expand) <br>2. Stage gates are QUALITY gates only (schema conformance, family balance, dedup, hand-review pass-rate) — never outcome-direction gates (sequential peeking is forbidden) <br>3. Frozen tier rule stays byte-identical; no protocol amendment to the margin <br>4. Execute the full campaign on the expanded suite; assess H2 ONCE at final n=385 under the original +0.02 margin <br>5. If H2 remains unreachable at n=385, report the achieved CI bound honestly and record H2 as `UNDERPOWERED_AT_MAX_PLANNED_N` — never widen the margin |
| **Literature Survey** | — "Sample size calculation in clinical research" (Springer 2024): https://link.springer.com/article/10.1007/s43994-024-00153-x — power/precision fundamentals <br>— "A systematic approach to adaptive sequential design" (J Biopharm Stat 2024): https://www.tandfonline.com/doi/full/10.1080/10543406.2024.2358796 — adaptive stopping alternatives <br>— FDA Adaptive Designs Guidance: https://www.fda.gov/media/78495/download — regulatory view on interim analyses <br>— "Bayesian Statistics in Confirmatory Clinical Trials" (BMC 2024): https://link.springer.com/article/10.1186/s12874-024-02235-0 — Bayesian stopping rules <br>— Sample Size Calculator (ClinCalc): https://clincalc.com/stats/samplesize.aspx — quick validation |
| **Est. Effort** | L — staged suite expansion to n=385 (margin relaxation is NOT a path) |
| **Dependency** | None — can proceed independently |
| **Issue Link** | #98 (P1 journal readiness) |

---

## NEGATIVE #002: P2 Deep Probe — 0/600 Title Hits

| Field | Value |
|-------|-------|
| **Paper** | P2 — Open-World Scientific Discovery |
| **Claim ID** | P2 Deep official LLM title-judge success |
| **Current Verdict** | `CANNOT_CHECK` — candidate generation failed |
| **Evidence Artifact** | `papers/orion-12/evidence/external_results/DEEP_OFFICIAL_ARCHIVE_V1.json` (0/600 hits; judge control 9/9 PASS) |
| **One-Stage Attribution** | **Candidate generation** — The keyless public-arXiv probe's retrieved titles never contain reference titles as substrings. Judge is functional (control passed 9/9). Failing stage is the probe's retrieval/candidate-builder, not the evaluation. |
| **Root Cause** | **Hypothesis:** The AutoResearchBench Deep task retrieves by **question embedding** from public arXiv rather than by title. Reference papers may be: (1) absent/weakly-indexed in public arXiv search; (2) not surfaced by question-based retrieval; (3) the probe uses the wrong retrieval field for candidate extraction. |
| **Revival Lever** | **Regenerate candidates with corrected retrieval** — Needle-question lexicon echoing in wrong titles. 36 items shipped empty candidate lists. Revival = fix retrieval (question vs title-based lookup), NOT re-scoring. Judge is already validated. |
| **Re-Test Plan** | 1. ✅ **COMPLETED (PR #266):** Judge-independent string overlap diagnostic <br>2. Evidence: `DEEP_ZERO_HIT_STAGE_ATTRIBUTION_2026-08-17.json` <br>3. Results: 564 items with refs+cands, 10,850 candidate titles <br>4. Exact match: 0 / Substring match: 0 / Token≥0.5: 8 <br>5. Even perfect matcher recovers 8/564 → candidate generation is failing stage <br>6. 36 items shipped empty candidate lists <br>7. **Next:** Regenerate candidates with corrected retrieval (question vs title-based lookup) |
| **Literature Survey** | — "Scientific Paper Retrieval with LLM-Guided Semantic-Based Ranking" (EMNLP 2025): https://aclanthology.org/2025.findings-emnlp.108/ — semantic vs lexical retrieval <br>— "Classifying and Addressing the Diversity of Errors in Retrieval-Augmented Generation Systems" (arXiv 2024): https://arxiv.org/html/2510.13975v1 — RAG error taxonomy <br>— "Candidate Generation Is the Real Bottleneck in RAG" (LinkedIn): https://www.linkedin.com/posts/naman-goyal1_rag-genai-retrieval-activity-7406336776489041920-426V — candidate generation focus <br>— "Evaluating Precision and Recall at Retrieval Time in RAG Systems" (ResearchGate): https://www.researchgate.net/publication/397055775 — retrieval evaluation |
| **Est. Effort** | M — diagnostic + fix |
| **Dependency** | None — diagnostic-only |
| **Issue Link** | #99 (P2 journal readiness) |

---

## NEGATIVE #003: P2 External Superiority — Baselines Unexecuted

| Field | Value |
|-------|-------|
| **Paper** | P2 — Open-World Scientific Discovery |
| **Claim ID** | P2.H1 — ORION vs matched baselines on Wide/Deep |
| **Current Verdict** | `CANNOT_CHECK` — execution missing |
| **Evidence Artifact** | Issue #157 |
| **One-Stage Attribution** | **Execution** — Baseline implementations exist (BM25, dense, hybrid, one-pass RAG, agentic single-route) but were never run against frozen ORION trajectories. |
| **Root Cause** | Resource/scheduling gap. Protocol exists (PROTOCOL_V1.json) but the full execution campaign with all baselines was never completed. |
| **Revival Lever** | **Execute frozen campaign:** <br>1. Bind exact post-#148 subject commit, dataset/evaluator hashes, baseline configs, seeds, budgets <br>2. Run complete-gold matched BM25/dense/hybrid/RAG/single-route/ORION <br>3. Run frozen ablations <br>4. Run official Wide where adapter permits; archive scorer inputs/outputs <br>5. Run Deep official only if valid judge credential exists; retain `CANNOT_CHECK` otherwise <br>6. Run MetaSyn ID-only/retrieval-screening evidence where valid <br>7. Generate P2-2..P2-7 and Tables P2-2/P2-3 from archived raw results |
| **Re-Test Plan** | 1. Verify PR #148 is merged and exact-head CI is green <br>2. Confirm frozen complete-gold companion exists <br>3. Confirm AutoResearchBench Wide adapter exists <br>4. Bind execution bindings: subject_revision, dataset_revisions, model_provider_revisions, evaluator_hash <br>5. Execute baselines in parallel where possible <br>6. Archive all raw results with SHA-256 checksums <br>7. Run generation scripts for all figures/tables <br>8. Populate manuscript Results/Discussion only from immutable artifacts <br>9. Independent offline headline reproduction |
| **Literature Survey** | N/A — execution problem, not a knowledge gap |
| **Est. Effort** | M — campaign execution |
| **Dependency** | PR #148 merge (precondition) |
| **Issue Link** | #157 (P2 closure), #99 (P2 journal readiness) |

---

## NEGATIVE #004: P3 Real Cross-Domain Adequacy — `CANNOT_CHECK`

| Field | Value |
|-------|-------|
| **Paper** | P3 — Global Knowledge Portrait |
| **Claim ID** | End-to-end cross-domain semantic adequacy (raw-text → extraction → mapping → utility) |
| **Current Verdict** | `CANNOT_CHECK` — deliberately narrowed |
| **Evidence Artifact** | `papers/orion-13/evidence/PUBLIC_REFERENCE_ROUTE_STATUS_V1.md`; PR #264 merged 2026-08-17 |
| **One-Stage Attribution** | **Scope narrowing** — The 32-case public-reference result (prospectively replicated) supports **only** the structured mapping calculus on already-pinpointed cases. It does NOT establish: raw-text extraction, strongest model/RAG/schema baselines, eight-family construct validity, recoverability of generated portraits, or downstream scientific utility. Those remain `CANNOT_CHECK`. |
| **Root Cause** | Resource constraints + explicit scope contraction. The zero-budget public-reference route (MUSE/SciFact/SciSchema pins) was executed as a narrower alternative to the original end-to-end protocol. PR #264 generated publication artifacts but explicitly scoped them to the mapping-only result. |
| **Revival Lever** | **Execute original Step 3 end-to-end study:** <br>1. Build real multi-domain gold dataset (≥3 disciplines, 8 case families) <br>2. Annotate: referent/entity judgment, construct identity, measurement equivalence, temporal/state context, polarity/modality/attribution/discourse, mapping relation, GLUE/OBSTRUCTION/UNRESOLVED, recoverability target <br>3. Run extraction precision/recall evaluation <br>4. Execute nearest strong baselines: long-context synthesis, RAG, flat-schema, SCOPE/SCION, provenance-aware schema-contract <br>5. Run semantic-coordinate ablations <br>6. Evaluate downstream utility (answer correctness using reconstructed portrait) <br>7. Generate P3-1..P3-7 and Tables P3-1..P3-3 |
| **Re-Test Plan** | 1. Write annotation handbook **before** final labeling <br>2. Sample cases spanning materials, physics, psychology, biology, engineering <br>3. At least two independent annotators on shared subset <br>4. Report agreement **per coordinate**, not aggregate <br>5. Freeze adjudication before test-system outputs are examined <br>6. Run ORION vs baselines with frozen resources <br>7. Archive gold, projections, mappings, portraits with checksums <br>8. Generate all figures/tables from immutable artifacts <br>9. Independent replay of headline mapping/obstruction results |
| **Literature Survey** | — "A Semantic Mapping of Cultural Heritage Ontologies" (ACM 2024): https://dl.acm.org/doi/fullHtml/10.1145/3657054.3657077 — cross-domain mapping <br>— "Cross-Domain Semantic Fidelity Evaluation for Meaning-to-Text" (ACL 2026): https://aclanthology.org/2026.gem-main.41.pdf — semantic fidelity <br>— "Towards Semantic Big Graph Analytics for Cross-Domain Knowledge Discovery" (ResearchGate): https://www.researchgate.net/publication/331244209 — semantic methods <br>— "Online Knowledge Integration for 3D Semantic Mapping: A Survey" (arXiv 2024): https://arxiv.org/html/2411.18147v1 — knowledge integration <br>— "Abstract Meaning Representation for Cross-AI Domain Knowledge" (IOS Press): https://ebooks.iospress.nl/pdf/doi/10.3233/FAIA251751 — AMR foundations |
| **Est. Effort** | L — requires gold dataset + baselines + evaluation |
| **Dependency** | Expert annotation team OR alternative pinned external resource |
| **Issue Link** | #100 (P3 journal readiness) |

---

## NEGATIVE #005: P4 Authority Protection — No External Hostile Battery

| Field | Value |
|-------|-------|
| **Paper** | P4 — Verified Scientific Discovery |
| **Claim ID** | P4 H3 — False authority promotion vs baselines |
| **Current Verdict** | `CANNOT_CHECK` — Issue #59 is the gate |
| **Evidence Artifact** | Issue #59; `FLAGSHIP_FALSIFIER_RESULTS_V1.md` |
| **One-Stage Attribution** | **Execution** — Local falsifier passed (authority-laundering suite exercises exact evidence fingerprints, content substitution, weak checker, same-lane, chronology), but the external hostile authority battery has never been executed on the exact final subject. |
| **Root Cause** | Infrastructure + execution gap. Issue #59 has explicit protocol but requires protected evaluator infrastructure and frozen benchmark that don't yet exist at execution scale. |
| **Revival Lever** | **Execute Issue #59 campaign:** <br>1. Source-aware claim/attribution benchmark (ProvenanceGuard-style, AttributionBench, CLAIM-BENCH/SciClaimHunt) <br>2. Cited-but-non-influential evidence cases <br>3. Evaluator tampering and held-out leakage tests <br>4. Search-time benchmark contamination audit <br>5. False scientific-authority promotion measurement <br>6. Correct `CANNOT_CHECK` as primary outcome coordinate <br>7. Evaluator/holdout access telemetry frozen prospectively <br>8. Protected evaluator outside candidate custody |
| **Re-Test Plan** | 1. Freeze exact subject commit, dataset/evaluator hashes, split identities <br>2. Construct attack battery: correct claim/wrong source, evidence-ID substitution, content/provenance identity, weak/non-discriminating checker, same-lane verification, cited-but-not-influenced, benchmark contamination, evaluator tampering, holdout leakage <br>3. Execute ORION vs nearest-work baselines under matched resources <br>4. Measure: claim correctness, source attribution, support/contradiction F1, cross-source conflation detection, evidence-substitution detection, evaluator-tamper/leakage detection, false authority-promotion rate, correct CANNOT_CHECK rate <br>5. Archive raw results, evaluator decisions, access logs with checksums <br>6. Generate P4-1..P4-7 and Tables P4-1..P4-3 <br>7. Independent reproduction of headline authority-protection results |
| **Literature Survey** | — "The Invisible Hijack: Understanding AI Authority Laundering" (NeuralTrust) — authority as security hole <br>— "Laundering AI Authority with Adversarial Examples" (ResearchGate) — four attack surfaces <br>— "LLM agents security duality: a comprehensive survey" (Springer) — authority amplification via tools <br>— "Risk-Adjusted Harm Scoring for Automated Red Teaming" (arXiv): https://arxiv.org/html/2603.10807v1 — red-teaming methods <br>— FinSafetyBench — bilingual red-teaming for LLM safety <br>— RewardHackingAgents — search-time contamination protections |
| **Est. Effort** | L — requires benchmark + baselines + protected execution |
| **Dependency** | Issue #59 executor + protected evaluator infrastructure |
| **Issue Link** | #59 (P4 hostile authority benchmark) |

---

## NEGATIVE #006: P5 Governed Self-Improvement — No Fresh Transfer Evidence

| Field | Value |
|-------|-------|
| **Paper** | P5 — Self-ORION |
| **Claim ID** | H1 — Transferable improvement vs baselines |
| **Current Verdict** | `CANNOT_CHECK` — structural only |
| **Evidence Artifact** | Issue #102; Readiness gate self-certification failure preserved |
| **One-Stage Attribution** | **Execution** — All governance structures exist (persistent `DevelopmentIssue.v1` state, invention readiness gate, replay/fresh separation, protected assurance, no self-merge authority), but NO hidden-cause fresh-transfer campaign has been executed with matched baselines on the exact final subject. |
| **Root Cause** | Infrastructure + execution gap. V2 protocol (STATIC→REPLAY→FRESH→PROTECTED) exists and is merged, but requires hidden-cause benchmark, protected evaluator infrastructure, and baseline implementations that don't yet exist at scale. |
| **Revival Lever** | **Execute Issue #159 campaign:** <br>1. **Hidden-cause benchmark (8 families):** retrieval miss, routing/planning miss, implementation/code bug, environment/dependency/tool failure, evaluator/metric bug, representation gap, measurement/specification gap, genuine method-basis gap <br>2. Root-cause labels hidden from candidates <br>3. Motivating/replay set separated from fresh-transfer set <br>4. Protected split/evaluator frozen before candidate generation <br>5. **Matched baselines:** fixed-agent, direct-self-edit, ADAS/meta-agent, DGM archive/self-edit, ADIAS issue-centric, SAGE multi-hypothesis, CausalFlow counterfactual, failure-driven improvement, evaluator-only/evolutionary <br>6. Protected evaluator/holdout outside candidate custody <br>7. Negative-history retention: every harmful/null variant preserved <br>8. Archive raw per-round motivating + fresh results |
| **Re-Test Plan** | 1. Freeze exact subject commit, four split hashes, provider/model revisions, evaluator/epoch/custody <br>2. Construct hidden-cause tasks across all 8 families (minimum 10 per family) <br>3. Separate motivating set (for replay) from fresh-transfer set (independent axis: task/domain/model/environment) <br>4. Run ORION full system vs all baselines with matched resources <br>5. Measure: protected fresh-task improvement, fresh-transfer success, harmful-transfer/regression, root-cause attribution accuracy, false method-change rate, evaluator/holdout/negative-history compromise, recurrence of recognized failures <br>6. Preserve negative evolution history: rejected/harmful alternatives <br>7. Archive content-addressed patches, sandbox/evaluator/access logs <br>8. Generate P5-1..P5-7 and Tables P5-1..P5-3 <br>9. Independent external attestation/reproduction of promotion-recommendation logic |
| **Literature Survey** | — Stanford CS329A — Self-Improving AI Agents: https://cs329a.stanford.edu/ — graduate course <br>— "SIA: Self Improving AI with Harness & Weight Updates" (arXiv): https://arxiv.org/html/2605.27276v2 — test-time training <br>— "Revision History for Self-Improving Agents" (OpenReview): https://openreview.net/revisions?id=IUltZSgLMm — experience-driven improvement <br>— "Toward Self-Improving Agents" (Salesforce) — AI-based evaluation layer, ~20% improvement <br>— "Self-Improving AI Agents: How They Work (and Don't)" (Prefactor): https://prefactor.tech/learn/self-improving-agents — risks/policy drift <br>— "Self-Improving AI Agent Pipeline 2026" (FutureAGI) — 3-stage pipeline, synthetic users <br>— ADIAS — issue-centric self-improvement (nearest work, absorbed) <br>— SAGE — multi-hypothesis failure attribution (nearest work, absorbed) <br>— CausalFlow — counterfactual repair (nearest work, absorbed) |
| **Est. Effort** | XL — requires hidden-cause benchmark + protected infrastructure + baselines |
| **Dependency** | Issues #8 (live-provider) and #76 (Phase-2 closure) |
| **Issue Link** | #102 (P5 journal readiness), #159 (P5 closure) |

---

## NEGATIVE #007: CI Flakiness — P3 Atlas Workflow

| Field | Value |
|-------|-------|
| **Paper** | N/A (infrastructure) |
| **Claim ID** | CI stability for P3 public-reference workflows |
| **Current Verdict** | `FLAKY` — 4 recent failures on `P3 public-reference atlas` workflow |
| **Evidence Artifact** | CI run logs (2026-08-17) |
| **One-Stage Attribution** | **Infrastructure** — The `P3 public-reference atlas` workflow shows intermittent failures during PR #264 development, while the evaluation workflow remains stable. Likely cause: race condition or resource contention in atlas regeneration step. |
| **Root Cause** | **Hypothesis:** The atlas generation step (figure/table creation + checksum verification) has non-deterministic ordering or resource contention that causes intermittent failures. The evaluation workflow (which runs the actual atlas build) is stable, suggesting the flakiness is in the publication artifact generation, not the core evaluation. |
| **Revival Lever** | **Audit and harden the atlas workflow:** <br>1. Identify the flaky step (likely figure/table generation or checksum verification) <br>2. Add retry logic with exponential backoff <br>3. Add deterministic ordering (e.g., sort files before processing) <br>4. Separate regeneration-check from regeneration in workflow <br>5. Verify failures are not evidence-dependent (run on same commit multiple times) <br>6. Add explicit resource limits/requests to prevent contention |
| **Re-Test Plan** | 1. Reproduce flaky failure on `main` <br>2. Check CI logs for exact failure step and error message <br>3. Inspect workflow YAML: `.github/workflows/p3-public-reference-atlas.yml` <br>4. Inspect generation script: likely in `scripts/` or `src/orion/papers/p3/` <br>5. Identify non-deterministic operation (file glob order, parallel writes, hash computation) <br>6. Add sorting/locking/retry as appropriate <br>7. Run workflow 10x on same commit to verify stability <br>8. Document fix in workflow comments |
| **Literature Survey** | N/A — infrastructure problem |
| **Est. Effort** | S — diagnostic + fix |
| **Dependency** | None — independent fix |
| **Issue Link** | N/A (infrastructure) |

---

## REVIVAL PRIORITY QUEUE

| Priority | Negative | Value × Feasibility | First Step |
|----------|----------|-------------------|------------|
| **1** | **#007 — CI Flakiness** | H × H | Audit workflow logs + add deterministic ordering |
| **1** | **#001 — P1 H2 Power** | H × H/M | Staged expansion to n=385, margin FROZEN (in flight: p1-expand) |
| **2** | **#003 — P2 Baselines** | H × M | Verify PR #148 merge, execute frozen campaign |
| **2** | **#002 — P2 Deep Probe** | M × M | Diagnostic DONE (0 exact/0 substring/8 token≥0.5 of 564) → regenerate candidates with corrected retrieval |
| **3** | **#005 — P4 Authority** | H × L | Build Issue #59 infrastructure + benchmark |
| **4** | **#004 — P3 End-to-End** | H × L | Build multi-domain gold dataset + baselines |
| **5** | **#006 — P5 Self-Improvement** | H × XL | Close #8/#76, then build hidden-cause benchmark |

**Rationale:** Priority = (publishability impact) × (feasibility). Items 1-2 can be executed immediately without external resources. Items 3-5 require substantial infrastructure and/or external benchmarks.

---

## TERMINOLOGY

| Term | Definition |
|------|------------|
| `CANNOT_CHECK` | Required evidence does not exist. No scientific claim is authorized. Distinct from `NEGATIVE` (evidence exists but shows no effect). |
| One-stage attribution | Failure attributed to exactly one stage (e.g., "sample size", "execution", "candidate generation"). Never diffuse multi-stage attribution. |
| Revival lever | Concrete mechanic improvement (retrieval, execution, evaluation access, sample size, experimental design) — NOT outcome tuning. |
| Est. Effort | S (small, <1 day), M (medium, 1-3 days), L (large, 1-2 weeks), XL (extra-large, >2 weeks) |
| Dependency | What must land first (e.g., PR merge, issue closure, infrastructure build) |

---

## REVISION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| V1 | 2026-08-17 | Initial saturation sweep. 7 negatives catalogued with one-stage attribution, revival levers, literature survey, re-test plans. |
| V1.1 | 2026-08-17 | Doctrine-compliance pass: removed the margin-relaxation path from NEGATIVE #001 (lever/re-test/effort/priority/next-steps) — revival is sample expansion ONLY, margin FROZEN at +0.02. Folded in the executed Deep zero-hit diagnostic (exact 0 / substring 0 / token≥0.5 8 of 564; artifact `DEEP_ZERO_HIT_STAGE_ATTRIBUTION_2026-08-17.json`, PR #266) — candidate generation confirmed as the single failing stage. |

---

## NEXT STEPS

1. **Review and prioritize** — Team lead reviews this backlog, confirms priority queue
2. **Execute top items** — CI flakiness fix + P1 staged expansion (margin frozen) (parallel, independent)
3. **Execute P2 items** — Deep candidate regeneration (diagnostic complete) + baselines execution (after PR #148)
4. **Plan infrastructure items** — P4/P3/P5 require external resources; plan staggered execution
5. **Per-negative revival** — Each completed revival updates this document with VERDICT_CHANGE and new evidence artifacts

**Doctrine reminder:** A revived positive must be earned via genuine mechanic improvement, never by margin relaxation, baseline weakening, or prose rewording. The strongest fix is the one that survives the strongest nearest work.
