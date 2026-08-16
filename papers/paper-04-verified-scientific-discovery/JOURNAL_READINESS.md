# ORION-P4 journal-readiness plan — Verified Scientific Discovery

**Current terminal:** `CANNOT_CHECK` for live scientific authority benefit / not peer-review ready.  
**Already present:** exact evidence binding, answer/check authority gates, local authority-laundering falsifier, protected evaluator concepts and existing hostile benchmark issue #59.

## 1. Novelty closure

- [x] Absorb ProvenanceGuard (arXiv:2606.18037): source-aware factuality, atomic claims and cross-source conflation are not novel.
- [x] Absorb claim-level auditability/AAR (arXiv:2602.13855): semantic provenance and auditability are not novel by themselves.
- [x] Absorb ProvenAI (arXiv:2606.26449): correctness, citation fidelity and behavioral influence are distinct coordinates.
- [x] Absorb Search-Time Contamination (arXiv:2606.05241 and prior STC work): browsing benchmark leakage is not an ORION novelty.
- [x] Absorb RewardHackingAgents (arXiv:2603.11337): evaluator locking, patch/access logging and held-out leakage detection are direct baselines/mechanisms.
- [x] Retain AttributionBench and CLAIM-BENCH as attribution/scientific claim-evidence baselines.
- [x] Re-search assurance cases, provenance systems, secure evaluation, independent verification and scientific fact-checking immediately before submission.
- [x] Preserve the residual as a **non-escalating authority transition**, not general provenance/fact checking.

## 2. Primary hypotheses

**H1 — false authority promotion:** full ORION reduces false scientific-authority promotion under provenance/checker/evaluator attacks relative to source-aware verification baselines.

**H2 — legitimate coverage:** the safety gain does not come only from blocking everything; full ORION retains useful authority/acceptance coverage on clean well-supported cases.

**H3 — correct CANNOT_CHECK:** under genuinely insufficient or compromised evidence, ORION chooses `CANNOT_CHECK/BLOCK` more accurately than confidence-threshold baselines.

- [x] Freeze false-promotion as the primary outcome and authority/coverage trade-off as a co-primary or key secondary outcome.

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

Custody:

- [x] evaluator/holdout identities frozen before candidate runs;
- [x] attack labels hidden from candidate;
- [x] protected access telemetry retained;
- [x] human adjudication of ambiguous support/source relations with written rubric;
- [x] exact content and provenance digests retained;
- [x] independent host generates at least part of the hostile set after method freeze.

## 4. Baselines and ablations

Baselines:

- [x] citation presence/format check;
- [x] pooled-evidence NLI/support verifier;
- [x] AttributionBench-style attribution evaluator;
- [x] ProvenanceGuard-style source-aware verifier;
- [x] iterative retrieve-or-verify baseline;
- [x] claim-level auditability/provenance baseline where runnable.

Ablations:

- [x] no exact content binding;
- [x] no source/provenance identity distinction;
- [x] no checker lineage/independence gate;
- [x] no host-generated hostile battery;
- [x] no behavioral-influence coordinate;
- [x] no evaluator protection/telemetry;
- [x] confidence score instead of fail-closed authority lattice;
- [x] equalized verification budget.

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

## 6. Required plots

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

## 8. Reproducibility package

- [ ] frozen attack-case manifest with hidden labels stored under protected custody;
- [ ] exact source/evidence content snapshots/digests;
- [ ] baseline and checker configs;
- [ ] evaluator/holdout access logs;
- [ ] search trajectories for contamination audit;
- [ ] raw per-claim verdicts and authority transitions;
- [ ] scripts regenerating all figures/tables;
- [ ] clean-environment replay of non-secret portions;
- [ ] independent reproduction/hostile review of the headline false-promotion result.

## Existing dependencies

- issue #59 owns the external hostile authority/evaluator benchmark and should be treated as an execution dependency rather than duplicated.

## Done definition

`ORION-P4 = PEER_REVIEW_READY` only after issue #59 (or its successor frozen campaign) demonstrates a materially better safety/coverage trade-off than strong source-aware verification baselines, protected custody is intact, and all programme journal-readiness gates pass.
