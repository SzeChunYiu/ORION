# ORION-P1 journal-readiness plan — Recursive Epistemic Reconstruction

**Current terminal:** `CANNOT_CHECK` for external superiority / not peer-review ready.  
**Already present:** scoped manuscript, explicit K/W/M formulation, mechanic-cell self-audit, hidden-shift local falsifier, negative controls, local failure/repair record.

## 1. Novelty closure — required before external experiment freeze

- [ ] Absorb AREX (arXiv:2607.21461): recursive constraint-wise audit + targeted follow-up is not novel.
- [ ] Absorb SCION (arXiv:2607.03863): staged objectives, dependencies, verification checkpoints, fallback and memory are not novel.
- [ ] Absorb Iris (arXiv:2608.02143): evolving information state, revisable claims and epistemic actions are not novel.
- [ ] Compare against SciAgentArena (arXiv:2606.12736) as an external scientific-agent task source where compatible.
- [ ] Re-run function-only and parent-discipline search for problem reformulation, model revision, adaptive planning, requirements/dependency invalidation and rational metareasoning.
- [ ] Rewrite the novelty sentence so it claims only the smallest surviving composition: explicit K/W/M separation + typed responsibility-targeted reframe + dependency-directed reopening + recursive mechanic audit.
- [ ] Decide whether each of P1.D1–P1.D4 survives as an independent delta or only as part of the composition.

## 2. Primary hypotheses to freeze prospectively

**H1 — hidden formulation shift:** on tasks where the initial representation/search universe is deliberately insufficient, full ORION improves root task success versus matched static/recursive research baselines.

**H2 — repair selectivity:** ORION reduces unnecessary formulation changes on evidence-only/execution-only negative controls.

**H3 — scoped invalidation:** dependency-directed reopening invalidates the right prior closure more precisely than full reset or no reset.

**H4 — self-audit stability:** mechanic obligations and authority/invariant structure are retained as recursion depth increases.

- [ ] Freeze one primary hypothesis (recommended H1) and treat H2–H4 as secondary/mechanistic.
- [ ] Predefine minimum practically meaningful effect/equivalence margins before running the final test.

## 3. External benchmark construction

Create a frozen hidden-shift suite with labels unavailable to the evaluated agent.

Required task families:

- [ ] hidden parent-domain / omitted-discipline cases;
- [ ] hidden representation/coordinate-system cases;
- [ ] hidden decomposition/interface cases;
- [ ] hidden measurement/operationalization cases;
- [ ] evidence-missing negative controls where reframe is wrong;
- [ ] execution/tooling-bug negative controls where reframe is wrong;
- [ ] optional real SciAgentArena/open-ended science cases whose failure cause can be adjudicated independently.

Protocol:

- [ ] build a pilot set only for variance/power estimation and debugging;
- [ ] freeze final test cases after the pilot;
- [ ] hide responsibility/domain labels and gold reformulation from all candidate systems;
- [ ] have at least two independent adjudicators label whether a reframe was required and which coordinates should reopen;
- [ ] report agreement and resolve disagreements under a prewritten policy;
- [ ] perform power/precision analysis before freezing final N;
- [ ] preserve every failed/null run.

## 4. Baselines and ablations

Strong baselines:

- [ ] static ReAct/tool-use workflow;
- [ ] tree-search or AI-Scientist-style iterative research baseline;
- [ ] AREX-like recursive audit/follow-up baseline where runnable or a faithful protocol-matched implementation;
- [ ] SCION-like explicit plan/dependency baseline where runnable or a faithful protocol-matched implementation;
- [ ] Iris-like information-state/inquiry-revision baseline where runnable or a faithful protocol-matched implementation.

ORION ablations:

- [ ] no explicit W state;
- [ ] no explicit M state;
- [ ] generic retry instead of responsibility-targeted reframe;
- [ ] full reset instead of dependency-directed reopen;
- [ ] no mechanic-cell self-audit;
- [ ] equalized search/LLM budget for every comparison.

## 5. Metrics

Primary:

- [ ] root task success under frozen criteria;
- [ ] success on hidden-shift subset;
- [ ] unnecessary-reframe rate on negative controls.

Mechanistic:

- [ ] responsibility classification accuracy / macro-F1;
- [ ] reframe-target accuracy by coordinate family;
- [ ] reopen precision, recall and F1 over affected dependencies;
- [ ] stale-closure survival rate;
- [ ] time/cost/tool calls/tokens to resolution;
- [ ] invariant/authority violations;
- [ ] trace fidelity as recursion depth increases.

Statistics:

- [ ] paired tests where systems run on identical tasks;
- [ ] bootstrap or model-appropriate 95% intervals for primary rates/differences;
- [ ] effect sizes and practical margins;
- [ ] multiple-seed aggregation for stochastic systems;
- [ ] correction for multiple secondary comparisons.

## 6. Required plots

Freeze plotting code/spec before final outcome analysis.

- [ ] **Figure P1-1:** benchmark protocol diagram showing hidden cause, observable trace, allowed interventions and protected labels.
- [ ] **Figure P1-2:** root success by task family and baseline with uncertainty intervals.
- [ ] **Figure P1-3:** false-reframe rate vs hidden-shift success (selectivity frontier).
- [ ] **Figure P1-4:** reopen precision/recall or F1 by dependency depth.
- [ ] **Figure P1-5:** cost-to-success / success-cost Pareto frontier.
- [ ] **Figure P1-6:** invariant/trace error vs recursion depth.
- [ ] **Table P1-1:** nearest-work mechanism matrix.
- [ ] **Table P1-2:** full ablation table with delta and confidence interval.
- [ ] **Table P1-3:** failure taxonomy with representative blinded cases.

## 7. Manuscript work still missing

- [ ] update abstract/introduction to avoid implying recent agents keep all formulation state implicit;
- [ ] integrate AREX/SCION/Iris/SciAgentArena into related work and bibliography;
- [ ] convert evaluation section from proposal language to frozen protocol language before run;
- [ ] add external Results section populated only from immutable result artifacts;
- [ ] add statistical methods subsection;
- [ ] add reproducibility/data/code availability statements;
- [ ] add ethics/safety section covering expensive/repeated research, web/tool access and authority limits;
- [ ] update limitations after observing actual failure modes without deleting predeclared limitations;
- [ ] final claim ledger must map every abstract/conclusion claim to a table/figure/theorem/evidence artifact.

## 8. Reproducibility package

- [ ] versioned benchmark manifest and case generator/source list;
- [ ] frozen baseline configs/prompts;
- [ ] exact subject/model/provider/tool versions;
- [ ] raw traces and intermediate reframe/reopen decisions;
- [ ] evaluation/adjudication script;
- [ ] `make paper01-results` or equivalent to regenerate all result figures/tables;
- [ ] clean-environment reproduction instructions and expected runtime/cost;
- [ ] permanent archive snapshot/DOI for final artifact where possible;
- [ ] independent reproduction of headline result.

## Done definition

`ORION-P1 = PEER_REVIEW_READY` only when every item above and every gate in `research/paper-programme-v1/JOURNAL_READINESS_STANDARD.md` is complete, the external claim is no longer `CANNOT_CHECK`, and the final literature-closure pass leaves no unresolved nearest-work route.
