# ORION-P4 journal-readiness plan — Verified Scientific Discovery

**Current terminal:** `CANNOT_CHECK` for live scientific authority benefit / not peer-review ready.  
**Already present:** exact evidence binding, answer/check authority gates, local authority-laundering falsifier, protected evaluator concepts and existing hostile benchmark issue #59.

## 1. Novelty closure

- [ ] Absorb ProvenanceGuard (arXiv:2606.18037): source-aware factuality, atomic claims and cross-source conflation are not novel.
- [ ] Absorb claim-level auditability/AAR (arXiv:2602.13855): semantic provenance and auditability are not novel by themselves.
- [ ] Absorb ProvenAI (arXiv:2606.26449): correctness, citation fidelity and behavioral influence are distinct coordinates.
- [ ] Absorb Search-Time Contamination (arXiv:2606.05241 and prior STC work): browsing benchmark leakage is not an ORION novelty.
- [ ] Absorb RewardHackingAgents (arXiv:2603.11337): evaluator locking, patch/access logging and held-out leakage detection are direct baselines/mechanisms.
- [ ] Retain AttributionBench and CLAIM-BENCH as attribution/scientific claim-evidence baselines.
- [ ] Re-search assurance cases, provenance systems, secure evaluation, independent verification and scientific fact-checking immediately before submission.
- [ ] Preserve the residual as a **non-escalating authority transition**, not general provenance/fact checking.

## 2. Primary hypotheses

**H1 — false authority promotion:** full ORION reduces false scientific-authority promotion under provenance/checker/evaluator attacks relative to source-aware verification baselines.

**H2 — legitimate coverage:** the safety gain does not come only from blocking everything; full ORION retains useful authority/acceptance coverage on clean well-supported cases.

**H3 — correct CANNOT_CHECK:** under genuinely insufficient or compromised evidence, ORION chooses `CANNOT_CHECK/BLOCK` more accurately than confidence-threshold baselines.

- [ ] Freeze false-promotion as the primary outcome and authority/coverage trade-off as a co-primary or key secondary outcome.

## 3. External hostile benchmark — extend issue #59

Attack families:

- [ ] correct claim citing wrong source;
- [ ] source content substituted behind stable-looking ID;
- [ ] semantically close sources swapped/conflated;
- [ ] cited evidence that did not behaviorally influence the answer;
- [ ] pooled evidence supports claim but assigned source does not;
- [ ] checker accepts non-empty/restated answers;
- [ ] checker authored/trained in same lane as answer;
- [ ] post-hoc checker/evaluator introduced after candidate outcome;
- [ ] benchmark metadata/question/answer encountered during search;
- [ ] candidate modifies evaluator/metric/guard code;
- [ ] candidate reads holdout labels or weakens tests;
- [ ] genuinely insufficient evidence where abstention is correct;
- [ ] clean positive cases so refusal-only systems are penalized.

Custody:

- [ ] evaluator/holdout identities frozen before candidate runs;
- [ ] attack labels hidden from candidate;
- [ ] protected access telemetry retained;
- [ ] human adjudication of ambiguous support/source relations with written rubric;
- [ ] exact content and provenance digests retained;
- [ ] independent host generates at least part of the hostile set after method freeze.

## 4. Baselines and ablations

Baselines:

- [ ] citation presence/format check;
- [ ] pooled-evidence NLI/support verifier;
- [ ] AttributionBench-style attribution evaluator;
- [ ] ProvenanceGuard-style source-aware verifier;
- [ ] iterative retrieve-or-verify baseline;
- [ ] claim-level auditability/provenance baseline where runnable.

Ablations:

- [ ] no exact content binding;
- [ ] no source/provenance identity distinction;
- [ ] no checker lineage/independence gate;
- [ ] no host-generated hostile battery;
- [ ] no behavioral-influence coordinate;
- [ ] no evaluator protection/telemetry;
- [ ] confidence score instead of fail-closed authority lattice;
- [ ] equalized verification budget.

## 5. Metrics

Primary:

- [ ] false authority-promotion rate overall and by attack family;
- [ ] authority/acceptance coverage on clean positives;
- [ ] safety-coverage trade-off/AURC-like summary chosen prospectively.

Secondary:

- [ ] claim correctness;
- [ ] source attribution accuracy;
- [ ] support/contradiction F1;
- [ ] cross-source conflation detection;
- [ ] content-substitution detection;
- [ ] cited-but-non-influential detection;
- [ ] evaluator-tamper/holdout-leakage detection;
- [ ] search-time contamination detection;
- [ ] correct `CANNOT_CHECK` rate;
- [ ] cost/latency/tool calls.

## 6. Required plots

- [ ] **Figure P4-1:** authority pipeline showing proposal-only content, evidence binding, checker admissibility, protected evaluation and non-escalating terminal states.
- [ ] **Figure P4-2:** false authority-promotion rate by baseline with confidence intervals.
- [ ] **Figure P4-3:** authority coverage vs false-promotion frontier.
- [ ] **Figure P4-4:** block/detection rate by hostile attack family.
- [ ] **Figure P4-5:** source accuracy vs semantic-support accuracy, highlighting cross-source conflation.
- [ ] **Figure P4-6:** cost/latency vs false-promotion trade-off.
- [ ] **Table P4-1:** attack battery and protected custody/freeze properties.
- [ ] **Table P4-2:** baseline/ablation results.
- [ ] **Table P4-3:** `CANNOT_CHECK`/false-positive/false-negative failure analysis.

## 7. Manuscript work missing

- [ ] create canonical full manuscript under `manuscript/`;
- [ ] formalize authority states and exact evidence/check/evaluator prerequisites;
- [ ] explicitly distinguish correctness, citation, source attribution, influence and authority;
- [ ] add ProvenanceGuard/AAR/ProvenAI/STC/RewardHackingAgents/CLAIM-BENCH related work;
- [ ] write benchmark Methods before running the final battery;
- [ ] add Results only from immutable protected artifacts;
- [ ] add security/threat model and limitations;
- [ ] add ethics/governance section describing external authority custody;
- [ ] add data/code availability and reproducibility statements.

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
