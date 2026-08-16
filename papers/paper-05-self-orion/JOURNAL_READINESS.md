# ORION-P5 journal-readiness plan — Self-ORION

**Current terminal:** `CANNOT_CHECK` for governed self-improvement benefit / not peer-review ready.  
**Already present:** canonical manuscript, failure/issue state, invention-readiness gate, isolated change control, replay/fresh-transfer/protected assurance concepts, no self-merge, local hostile falsifier and readiness-gate failure history.

## 1. Novelty closure — major update required

- [ ] ADIAS (arXiv:2608.06410): persistent issue-centric state is explicitly non-novel.
- [ ] SAGE / Multi-Hypothesis Failure Attribution (arXiv:2606.31478): structured multi-hypothesis failure attribution and intervention-level routing are not novel by themselves.
- [ ] CausalFlow (arXiv:2605.25338): counterfactual/interventional causal responsibility and minimal repair pressure any broad causal-attribution claim.
- [ ] Learning from Failure (arXiv:2606.31270): diagnosing failed trajectories and converting them into agent improvements is not novel.
- [ ] PAST-Bench (arXiv:2608.04003): retained-experience improvement/pathway testing is a direct evaluation reference.
- [ ] SEVA (arXiv:2606.29713): repeated self-evolution can create benchmark specialists with cross-benchmark regression; fresh/harmful transfer must be a primary measurement.
- [ ] retain DGM (arXiv:2505.22954), ADAS (arXiv:2408.08435), direct self-edit and AlphaEvolve-like search as strong baselines.
- [ ] re-search continual/experiential learning, self-refinement, debugging/root-cause analysis, program repair and safe self-modification before submission.
- [ ] remove standalone novelty language around failure-driven learning, multi-hypothesis diagnosis or causal attribution if the fresh literature already provides it.

Recommended surviving residual: **persistent issue state + evidence-bound causal discrimination + invention readiness + replay AND independent fresh transfer + protected evaluator/assurance + immutable negative evolution history + no self-certification/merge authority**.

## 2. Primary hypotheses

**H1 — transferable improvement:** under hidden-cause development tasks, full Self-ORION produces more fresh-transfer improvement and less harmful transfer than matched self-edit/self-evolution baselines.

**H2 — attribution:** explicit competing causes/discriminators reduce false method changes relative to reflection or candidate-centric optimization.

**H3 — integrity:** protected assurance prevents evaluator/holdout/negative-history manipulation from being counted as improvement.

**H4 — governance cost:** the transfer/integrity gain remains useful after accounting for extra compute/time and conservative abstention.

- [ ] freeze H1 as primary unless a preregistered pilot justifies another choice.

## 3. Hidden failure-family benchmark

Construct development tasks with deliberately similar visible symptoms but different hidden causes:

- [ ] retrieval miss;
- [ ] routing/planning miss;
- [ ] implementation bug;
- [ ] environment/dependency failure;
- [ ] evaluator/metric bug;
- [ ] representation gap;
- [ ] measurement/specification gap;
- [ ] genuine method-basis gap.

Protocol:

- [ ] root-cause labels hidden from candidate systems;
- [ ] motivating failure/replay set separated from fresh-transfer set;
- [ ] at least one fresh domain/task/model axis differs from the motivating case;
- [ ] protected evaluator and holdout frozen before candidate generation;
- [ ] intervention budgets matched;
- [ ] negative/null/harmful variants retained;
- [ ] power/precision analysis performed before final N;
- [ ] human root-cause adjudication uses a frozen rubric where causal truth is not mechanically generated.

## 4. Baselines and ablations

Baselines:

- [ ] fixed coding/research agent with no self-improvement;
- [ ] direct self-edit agent;
- [ ] ADAS/meta-agent search;
- [ ] DGM-like archive/self-edit;
- [ ] ADIAS-like issue-centric optimization;
- [ ] SAGE-like multi-hypothesis failure attribution/reflection;
- [ ] CausalFlow-like counterfactual repair where runnable;
- [ ] failure-driven improvement baseline;
- [ ] evaluator-only/evolutionary search baseline.

Ablations:

- [ ] no persistent issue state;
- [ ] recurrence/reflection without causal discriminator;
- [ ] no invention-readiness gate;
- [ ] replay only, no fresh transfer;
- [ ] fresh transfer but no protected evaluator custody;
- [ ] delete/ignore negative variants;
- [ ] allow self-certification/promotion in an isolated safety ablation;
- [ ] equalized LLM/tool/time budgets.

## 5. Metrics

Primary:

- [ ] protected root improvement on fresh tasks;
- [ ] fresh-transfer success rate;
- [ ] harmful-transfer/regression rate.

Attribution/governance:

- [ ] root-cause attribution accuracy / macro-F1;
- [ ] false method-change rate;
- [ ] intervention success conditional on correct/incorrect attribution;
- [ ] evaluator/holdout/negative-history compromise rate;
- [ ] correct block/`CANNOT_CHECK` rate;
- [ ] recurrence of previously recognized failure classes;
- [ ] negative-history completeness;
- [ ] time/cost/tool calls to validated improvement.

Longitudinal:

- [ ] performance trajectory across improvement rounds on motivating benchmark;
- [ ] simultaneous trajectory on fresh/other benchmarks to expose specialist regression;
- [ ] issue-resolution time and number of interventions;
- [ ] archive diversity/duplicate-repair rate.

## 6. Required plots

- [ ] **Figure P5-1:** governed self-development loop with authority boundary and external host promotion.
- [ ] **Figure P5-2:** fresh-transfer improvement vs motivating-task replay improvement scatter; harmful-transfer quadrant highlighted.
- [ ] **Figure P5-3:** root-cause attribution confusion matrix by hidden failure family.
- [ ] **Figure P5-4:** performance across self-improvement rounds on motivating and fresh benchmarks (SEVA-style specialist-regression diagnostic).
- [ ] **Figure P5-5:** improvement vs integrity/safety frontier across baselines/ablations.
- [ ] **Figure P5-6:** cumulative recognized-failure recurrence over rounds with/without negative history.
- [ ] **Figure P5-7:** cost/time to protected validated improvement.
- [ ] **Table P5-1:** nearest-work mechanism/novelty disposition matrix.
- [ ] **Table P5-2:** baseline/ablation results with uncertainty.
- [ ] **Table P5-3:** all harmful/null interventions retained and categorized.

## 7. Manuscript work still missing

- [ ] add a full related-work section and bibliography to the canonical manuscript;
- [ ] shrink novelty language after SAGE/CausalFlow/Learning-from-Failure/PAST-Bench absorption;
- [ ] distinguish failure persistence, causal attribution, issue persistence and protected promotion as separate prior-art axes;
- [ ] convert evaluation proposal into a frozen Methods protocol before final run;
- [ ] add external Results/Discussion only from immutable artifacts;
- [ ] add statistical methods subsection;
- [ ] expand threat model for evaluator compromise, benchmark leakage and meta-overfitting;
- [ ] add reproducibility/data/code availability and compute/cost statement;
- [ ] final conclusion must not equate internal readiness with external promotion authority.

## 8. Reproducibility package

- [ ] frozen hidden-cause benchmark generator/cases;
- [ ] motivating/replay/fresh split identities;
- [ ] baseline implementations/configs;
- [ ] content-addressed candidate patches;
- [ ] sandbox and evaluator access logs;
- [ ] immutable issue/failure/evolution history;
- [ ] raw per-round results for motivating and fresh tasks;
- [ ] scripts regenerating every result plot/table;
- [ ] clean-environment replay of accepted and rejected candidates;
- [ ] independent external attestation/reproduction of the final promotion recommendation logic.

## Existing dependencies

- issue #8 owns the frozen live-provider research trial.
- issue #76 owns Phase-2 Shadow Self-ORION closure and already requires a consequential end-to-end development cycle.
- these are necessary evidence inputs but do not by themselves complete the paper-level nearest-work, statistical, ablation and manuscript gates above.

## Done definition

`ORION-P5 = PEER_REVIEW_READY` only when full Self-ORION demonstrates transferable protected improvement against current self-improvement baselines, harmful transfer/integrity outcomes are reported, no self-promotion authority is claimed, and all programme readiness gates pass.
