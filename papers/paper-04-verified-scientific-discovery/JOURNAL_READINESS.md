# ORION-P4 journal-readiness plan — Verified Scientific Discovery

**Current terminal:** `CANNOT_CHECK` for live scientific authority benefit / not peer-review ready.  
**Execution status:** `BLOCKED_EXTERNAL_BINDINGS`; final evaluator/holdout/source/split identities remain unbound, and no independent-host protected run has been accepted.  
**Already present:** exact evidence binding, answer/check authority gates, local authority-laundering falsifier, protected evaluator concepts and existing hostile benchmark issue #59.

## 1. Novelty closure

- [x] Absorb ProvenanceGuard (arXiv:2606.18037): source-aware factuality, atomic claims and cross-source conflation are not novel.
- [x] Absorb claim-level auditability/AAR (arXiv:2602.13855): semantic provenance and auditability are not novel by themselves.
- [x] Absorb ProvenAI (arXiv:2606.26449): correctness, citation fidelity and behavioral influence are distinct coordinates.
- [x] Absorb Search-Time Contamination (arXiv:2606.05241 and prior STC work): browsing benchmark leakage is not an ORION novelty.
- [x] Absorb RewardHackingAgents (arXiv:2603.11337): evaluator locking, patch/access logging and held-out leakage detection are direct baselines/mechanisms.
- [x] Retain AttributionBench and CLAIM-BENCH as attribution/scientific claim-evidence baselines.
- [x] Absorb FIRE (arXiv:2411.00784) as the concrete iterative retrieve-or-verify comparison within the already-frozen baseline family.
- [x] Complete the dated 2026-08-16 nearest-work audit, including FactArena (arXiv:2601.02669), DeepSciVerify (arXiv:2605.27710), BenchGuard (arXiv:2604.24955), certified untrusted-agent gating (arXiv:2606.31023), and CheckThat! 2026 scientific claim-source retrieval (arXiv:2607.15875); record explicit `ADOPT/ADAPT/COMPOSE/DEFER/REJECT` dispositions in `literature/NEAREST_WORK_AUDIT_2026-08-16.md`.
- [ ] Re-run the nearest-work search within 14 days of final submission if submission occurs after 2026-08-30.
- [x] Preserve the residual as a **non-escalating authority transition**, not general provenance/fact checking.
- [x] NOVELTY_AUDIT_V1.md: per-claim novelty determination (NOVEL/EXTENSION/BASELINE/PRIOR_ART)
- [x] NOVELTY_CLOSURE_SUMMARY_V1.md: executive summary with novelty density analysis

## 2. Primary hypotheses

**H1 — false authority promotion:** full ORION reduces false scientific-authority promotion under provenance/checker/evaluator attacks relative to source-aware verification baselines.

**H2 — legitimate coverage:** the safety gain does not come only from blocking everything; full ORION retains useful authority/acceptance coverage on clean well-supported cases.

**H3 — correct CANNOT_CHECK:** under genuinely insufficient or compromised evidence, ORION chooses `CANNOT_CHECK/BLOCK` more accurately than confidence-threshold baselines.

- [x] Freeze false-promotion as the primary outcome and authority/coverage trade-off as a co-primary or key secondary outcome.
- [x] STATISTICAL_ANALYSIS_PLAN_V1.md: all 3 hypotheses, Wilson CIs, bootstrap, sample size (n≥385), multiplicity correction, stochastic repeats, exclusion rules, sensitivity analyses
- [x] METRICS_REGISTRY_V1.json: 2 primary + 12 secondary metrics, all registered with definitions, units, directions, and hypothesis mappings
- [x] FREEZE_MANIFEST_V1.md: all execution bindings UNBOUND, promotion checklist, invalidating events
- [x] PLOT_SPEC_V1.md: all 6 figures + 3 tables specified with exact metric mappings
- [x] test_protocol_freezing.py: 14 tests covering all protocol artifacts

## 3. External hostile benchmark — extend issue #59

Attack families:

- [x] correct claim citing wrong source;
- [x] source content substituted behind stable-looking ID;
- [x] semantically close sources swapped/conflated;
- [x] cited evidence that did not behaviorally influence the answer;
- [x] pooled evidence supports claim but assigned source does not;
- [x] checker accepts non-empty/restated answers;
- [x] checker authored/trained in same lane as answer;
- [x] post-hoc checker/evaluator introduced after candidate outcome;
- [x] benchmark metadata/question/answer encountered during search;
- [x] candidate modifies evaluator/metric/guard code;
- [x] candidate reads holdout labels or weakens tests;
- [x] genuinely insufficient evidence where abstention is correct;
- [x] clean positive cases so refusal-only systems are penalized.
- [x] ATTACK_MANIFEST_V1.jsonl: 39+ cases (3 per attack family), valid JSONL matching ATTACK_CASE_SCHEMA_V1
- [x] CUSTODY_MANIFEST_V1.json: content and provenance digests with custody summary
- [x] test_attack_manifest.py: schema validation tests

Custody design completed before execution:

- [x] policy requires evaluator/holdout identities to be frozen before candidate runs;
- [x] policy requires attack labels to remain hidden from the candidate;
- [x] policy requires protected access telemetry to be retained;
- [x] written human-adjudication rubric exists for ambiguous support/source relations;
- [x] policy requires exact content and provenance digests to be retained;
- [x] policy requires an independent host to generate at least part of the hostile set after method freeze.
- [x] THREAT_MODEL_V1.md updated with attack family descriptions

Protected-run evidence still required:

## 4. Baselines and ablations

Baselines:

- [x] citation presence/format check;
- [x] pooled-evidence NLI/support verifier;
- [x] AttributionBench-style attribution evaluator;
- [x] ProvenanceGuard-style source-aware verifier;
- [x] iterative retrieve-or-verify baseline;
- [x] claim-level auditability/provenance baseline where runnable.
- [x] baseline_runner.py: 6 baseline strategies, 526 lines

Ablations:

- [x] no exact content binding;
- [x] no source/provenance identity distinction;
- [x] no checker lineage/independence gate;
- [x] no host-generated hostile battery;
- [x] no behavioral-influence coordinate;
- [x] no evaluator protection/telemetry;
- [x] confidence score instead of fail-closed authority lattice;
- [x] no search-time contamination block.

Resource matching:

- [x] equalized verification/evidence budget across variants and strong baselines.
- [x] ablation_runner.py: 8 ablation wrappers, resource-matched, 391 lines

Campaign:

- [x] campaign_runner.py: JSONL manifest runner with CLI and multiprocessing
- [x] test_baseline_runner.py: comprehensive tests for baselines, ablations, and campaign runner

## 5. Metrics

Primary:

- [x] false authority-promotion rate overall and by attack family;
- [x] authority/acceptance coverage on clean positives;
- [x] safety-coverage trade-off/AURC-like summary chosen prospectively.

Secondary:

- [x] claim correctness;
- [x] source attribution accuracy;
- [x] support/contradiction F1;
- [x] cross-source conflation detection;
- [x] content-substitution detection;
- [x] cited-but-non-influential detection;
- [x] evaluator-tamper/holdout-leakage detection;
- [x] search-time contamination detection;
- [x] correct `CANNOT_CHECK` rate;
- [x] cost/latency/tool calls.

## 6. Required plot/table specifications

The checked items in this section mean the figure/table specification or template exists. They do **not** mean protected-result values have been produced; result-populated outputs remain blocked by the protected run above.

- [x] **Figure P4-1:** authority pipeline showing proposal-only content, evidence binding, checker admissibility, protected evaluation and non-escalating terminal states.
- [x] **Figure P4-2:** false authority-promotion rate by baseline with confidence intervals.
- [x] **Figure P4-3:** authority coverage vs false-promotion frontier.
- [x] **Figure P4-4:** block/detection rate by hostile attack family.
- [x] **Figure P4-5:** source accuracy vs semantic-support accuracy, highlighting cross-source conflation.
- [x] **Figure P4-6:** cost/latency vs false-promotion trade-off.
- [x] **Table P4-1:** attack battery and protected custody/freeze properties.
- [x] **Table P4-2:** baseline/ablation results.
- [x] **Table P4-3:** `CANNOT_CHECK`/false-positive/false-negative failure analysis.

## 7. Manuscript work missing

- [x] create canonical full manuscript under `manuscript/`;
- [x] formalize authority states and exact evidence/check/evaluator prerequisites;
- [x] explicitly distinguish correctness, citation, source attribution, influence and authority;
- [x] add ProvenanceGuard/AAR/ProvenAI/STC/RewardHackingAgents/CLAIM-BENCH related work;
- [x] write benchmark Methods before running the final battery;
- [ ] add Results only from immutable protected artifacts;
- [x] add security/threat model and limitations;
- [x] add ethics/governance section describing external authority custody;
- [x] add data/code availability and reproducibility statements.
- [x] CLAIM_LEDGER_V1.md: 15 claims mapped to evidence paths
- [x] AVAILABILITY_STATEMENT_V1.md: 3-tier data/code availability
- [x] NOVELTY_AUDIT_V1.md: per-claim novelty determination
- [x] NOVELTY_CLOSURE_SUMMARY_V1.md: executive summary
- [x] generate_figures.py: regenerates all 6 SVGs from publication_svg helpers
- [x] manuscript integrity tests (3 tests) passing

## 8. Reproducibility package

- [ ] frozen attack-case manifest with hidden labels stored under protected custody (ATTACK_MANIFEST_V1.jsonl created; hidden labels live in protected custody per CUSTODY_MANIFEST_V1.json)
- [ ] exact source/evidence content snapshots/digests (CUSTODY_MANIFEST_V1.json)
- [x] baseline and checker configs (baseline_runner.py configs)
- [ ] evaluator/holdout access logs (prospective; PROTECTED_HOLDOUT custody)
- [ ] search trajectories for contamination audit (prospective; logged during campaign)
- [ ] raw per-claim verdicts and authority transitions (campaign output JSONL, post-execution)
- [x] scripts regenerating all figures/tables (generate_figures.py — 6 SVGs)
- [ ] clean-environment replay of non-secret portions
- [ ] independent reproduction/hostile review of the headline false-promotion result (post-campaign, per issue #59)

## Existing dependencies

- issue #59 owns the external hostile authority/evaluator benchmark and should be treated as an execution dependency rather than duplicated.

## Done definition

`ORION-P4 = PEER_REVIEW_READY` only after issue #59 (or its successor frozen campaign) demonstrates a materially better safety/coverage trade-off than strong source-aware verification baselines, protected custody is intact, and all programme journal-readiness gates pass.