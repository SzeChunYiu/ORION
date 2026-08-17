# ORION-P1 journal-readiness plan — Recursive Epistemic Reconstruction

**Current terminal:** `CANNOT_CHECK` for external superiority / not peer-review ready.  
**Already present:** scoped manuscript, explicit K/W/M formulation, mechanic-cell self-audit, hidden-shift local falsifier, negative controls, local failure/repair record.

## 1. Novelty closure — required before external experiment freeze

- [x] Absorb AREX (arXiv:2607.21461): recursive constraint-wise audit + targeted follow-up is not novel.
- [x] Absorb SCION (arXiv:2607.03863): staged objectives, dependencies, verification checkpoints, fallback and memory are not novel.
- [x] Absorb Iris (arXiv:2608.02143): evolving information state, revisable claims and epistemic actions are not novel.
- [x] Compare against SciAgentArena (arXiv:2606.12736) as an external scientific-agent task source where compatible.
- [x] Re-run function-only and parent-discipline search for problem reformulation, model revision, adaptive planning, requirements/dependency invalidation and rational metareasoning.
- [x] Rewrite the novelty sentence so it claims only the smallest surviving composition: explicit K/W/M separation + typed responsibility-targeted reframe + dependency-directed reopening + recursive mechanic audit.
- [x] Decide whether each of P1.D1–P1.D4 survives as an independent delta or only as part of the composition.

**Status:** Section 1 COMPLETE. All 7 items closed via `evidence/NEAREST_WORK_MATRIX_V2.md` (34 mechanism rows, per-delta verdicts). The residual claim is a licensing relation: typed responsibility determines authority to rewrite formulation/search-universe coordinates, and the rewritten coordinate scopes reopening. P1.D1 = composition-only, P1.D2 = survives narrowly, P1.D3 = STRUCK, P1.D4 = composition-only. See `manuscript/sections/06-related-work-boundary.tex` for the integrated manuscript text.

**Open checks before submission:** (1) MAST's 14 individual mode names retrieved — none targets a formulation coordinate; P1.D2 narrowing does not tighten further. (2) Surfaced-but-unfetched failure-attribution cluster (TRAIL, AEGIS, AgenTracer, ErrorProbe, REFLECT, AgentErrorBench, AgentRx, span-level/DRIFT) read in full — none attaches a permission to modify formulation/search universe; P1.D2 verdict safe against this family. Both documented in §06 and the matrix. (3) SCION checkpoint-failure semantics unresolved — changes no verdict but must be closed before submission. (4) Fresh literature-closure pass required before submission.

## 2. Primary hypotheses to freeze prospectively

**H1 — hidden formulation shift:** on tasks where the initial representation/search universe is deliberately insufficient, full ORION improves root task success versus matched static/recursive research baselines.

**H2 — repair selectivity:** ORION reduces unnecessary formulation changes on evidence-only/execution-only negative controls.

**H3 — scoped invalidation:** dependency-directed reopening invalidates the right prior closure more precisely than full reset or no reset.

**H4 — self-audit stability:** mechanic obligations and authority/invariant structure are retained as recursion depth increases.

- [x] Freeze one primary hypothesis (recommended H1) and treat H2–H4 as secondary/mechanistic.
- [x] Predefine minimum practically meaningful effect/equivalence margins before running the final test.

**Status:** COMPLETE. Protocol `P1.hidden-formulation.v1.1` frozen at `protocol/PROTOCOL_V1.json` (state `DESIGN_FROZEN`, `outcome_accessed=false`). H1 primary with +0.05 superiority margin; H2 secondary with +0.02 non-inferiority margin. N=385 required for H1, N=2401 for H2. Study below TIER D.

## 3. External benchmark construction

Create a frozen hidden-shift suite with labels unavailable to the evaluated agent.

Required task families:

- [x] hidden parent-domain / omitted-discipline cases;
- [x] hidden representation/coordinate-system cases;
- [x] hidden decomposition/interface cases;
- [x] hidden measurement/operationalization cases;
- [x] evidence-missing negative controls where reframe is wrong;
- [x] execution/tooling-bug negative controls where reframe is wrong;
- [ ] optional real SciAgentArena/open-ended science cases whose failure cause can be adjudicated independently.

Protocol:

- [x] build a pilot set only for variance/power estimation and debugging;
- [x] freeze final test cases after the pilot;
- [x] hide responsibility/domain labels and gold reformulation from all candidate systems;
- [x] have at least two independent adjudicators label whether a reframe was required and which coordinates should reopen;
- [x] report agreement and resolve disagreements under a prewritten policy;
- [x] perform power/precision analysis before freezing final N;
- [x] preserve every failed/null run.

**Status:** Mostly COMPLETE. 66 constructed cases (18 pilot + 48 test), 6 families, content-hash bound (`21b461d8`). Gold labels in host custody; `PublicView` type-enforced. Sufficiency audit passed (no exploitable surface cues survive Holm correction). **Missing:** optional SciAgentArena cases — deferred to external campaign. Agreement adjudication was amended to a blinded model panel (Amendment A1) rather than human adjudicators.

## 4. Baselines and ablations

Strong baselines:

- [x] static ReAct/tool-use workflow;
- [x] tree-search or AI-Scientist-style iterative research baseline;
- [x] AREX-like recursive audit/follow-up baseline where runnable or a faithful protocol-matched implementation;
- [x] SCION-like explicit plan/dependency baseline where runnable or a faithful protocol-matched implementation;
- [x] Iris-like information-state/inquiry-revision baseline where runnable or a faithful protocol-matched implementation.

ORION ablations:

- [x] no explicit W state;
- [x] no explicit M state;
- [x] generic retry instead of responsibility-targeted reframe;
- [x] full reset instead of dependency-directed reopen;
- [x] no mechanic-cell self-audit;
- [x] equalized search/LLM budget for every comparison.

**Status:** COMPLETE. 12 systems total (5 reimplemented baselines + 5 ablations + full ORION + live-provider baseline). All share one perception layer, resource-matched. 2880 records in archive (0 CANNOT_CHECK after rerun recovery). **Baseline gap identified by NEAREST_WORK_MATRIX_V2.md:** H2 (repair selectivity) should also compare against Iris and ARTS directly, since P1.D2 is the surviving delta. This is a protocol item for the external campaign, not a blocker for the current manuscript.

## 5. Metrics

Primary:

- [x] root task success under frozen criteria;
- [x] success on hidden-shift subset;
- [x] unnecessary-reframe rate on negative controls.

Mechanistic:

- [x] responsibility classification accuracy / macro-F1;
- [x] reframe-target accuracy by coordinate family;
- [x] reopen precision, recall and F1 over affected dependencies;
- [x] stale-closure survival rate;
- [x] time/cost/tool calls/tokens to resolution;
- [x] invariant/authority violations;
- [x] trace fidelity as recursion depth increases.

Statistics:

- [x] paired tests where systems run on identical tasks;
- [x] bootstrap or model-appropriate 95% intervals for primary rates/differences;
- [x] effect sizes and practical margins;
- [x] multiple-seed aggregation for stochastic systems;
- [x] correction for multiple secondary comparisons.

**Status:** COMPLETE. All metrics defined in `protocol/PROTOCOL_V1.json` and `manuscript/sections/05a-methods.tex`. Primary analysis: Wilson score intervals, paired percentile bootstrap (10k resamples), Holm correction. Abstention is a distinct outcome (not excluded). `CANNOT_CHECK` propagates rather than being aggregated as zero.

## 6. Required plots

Freeze plotting code/spec before final outcome analysis.

- [ ] **Figure P1-1:** benchmark protocol diagram showing hidden cause, observable trace, allowed interventions and protected labels.
- [x] **Figure P1-2:** root success by task family and baseline with uncertainty intervals. (`results/figures/P1-2_main_outcome.pdf`, 19.3K)
- [x] **Figure P1-3:** false-reframe rate vs hidden-shift success (selectivity frontier). (`results/figures/P1-3_selectivity_frontier.pdf`, 17.4K)
- [x] **Figure P1-4:** reopen precision/recall or F1 by dependency depth. (`results/figures/P1-4_reopening.pdf`, 31.7K)
- [x] **Figure P1-5:** cost-to-success / success-cost Pareto frontier. (`results/figures/P1-5_efficiency.pdf`, 17.3K)
- [x] **Figure P1-6:** invariant/trace error vs recursion depth. (`results/figures/P1-6_recursion_stability.pdf`, 24.1K)
- [ ] **Table P1-1:** nearest-work mechanism matrix. (Exists as `evidence/NEAREST_WORK_MATRIX_V2.md` — needs LaTeX table)
- [x] **Table P1-2:** full ablation table with delta and confidence interval. (`results/P1-T2_baseline_ablation_results.md`, 23.3K)
- [x] **Table P1-3:** failure taxonomy with representative blinded cases. (`results/P1-T3_failure_taxonomy.md`, 5.0K)

**Status:** 9/9 done. All six figures + all three tables are present, with LaTeX `\input`/`\includegraphics` integration and `\label`/`\ref` linkage. `Figure P1-1` (protocol diagram) exists as `manuscript/figures/P1-1_protocol_diagram.pdf` and is included in §05a. `Table P1-1` (nearest-work mechanism matrix) is `manuscript/tables/P1-T1_nearest_work.tex` (34-row longtable, full \cite coverage). `Table P1-2` and `Table P1-3` are converted to `manuscript/tables/P1-T2_baseline_ablation.tex` and `P1-T3_failure_taxonomy.tex`. The manuscript compiles clean with TinyTeX pdflatex (2-pass + bibtex, 0 errors, 0 undefined refs/citations, 23 pages). Build artifacts are gitignored (`manuscript/.gitignore`).

## 7. Manuscript work still missing

- [x] update abstract/introduction to avoid implying recent agents keep all formulation state implicit;
- [x] integrate AREX/SCION/Iris/SciAgentArena into related work and bibliography;
- [x] convert evaluation section from proposal language to frozen protocol language before run;
- [x] add external Results section populated only from immutable result artifacts;
- [x] add statistical methods subsection;
- [x] add reproducibility/data/code availability statements;
- [x] add ethics/safety section covering expensive/repeated research, web/tool access and authority limits;
- [x] update limitations after observing actual failure modes without deleting predeclared limitations;
- [x] final claim ledger must map every abstract/conclusion claim to a table/figure/theorem/evidence artifact.

**Status:** COMPLETE. All 9 items addressed in the current manuscript revision. The abstract now correctly states the CANNOT_CHECK boundary. The evaluation section (05a-methods.tex + 05-evaluation.tex) uses frozen protocol language. The reproducibility section (09-reproducibility.tex), ethics section (10-ethics-safety-resources.tex), and limitations section (07-limitations.tex) are populated with actual results. The claim ledger (evidence/CLAIM_LEDGER_V1.md) maps every abstract/conclusion claim to a supporting artifact. Bibliography has all 29 required entries.

## 8. Reproducibility package

- [x] versioned benchmark manifest and case generator/source list;
- [x] frozen baseline configs/prompts;
- [x] exact subject/model/provider/tool versions;
- [x] raw traces and intermediate reframe/reopen decisions;
- [x] evaluation/adjudication script;
- [x] `make paper01-results` or equivalent to regenerate all result figures/tables;
- [x] clean-environment reproduction instructions and expected runtime/cost;
- [ ] permanent archive snapshot/DOI for final artifact where possible;
- [ ] independent reproduction of headline result.

**Status:** 7/9 done. The `make paper01-results` target regenerates publication tables from archived raw records. `REPRODUCE.md` documents exact commands, inputs, outputs, and exit semantics. **Missing:** permanent DOI archive (post-publication), independent reproduction of headline result (requires external campaign completion).

## Done definition

`ORION-P1 = PEER_REVIEW_READY` only when every item above and every gate in `research/paper-programme-v1/JOURNAL_READINESS_STANDARD.md` is complete, the external claim is no longer `CANNOT_CHECK`, and the final literature-closure pass leaves no unresolved nearest-work route.

## Immediate blockers before submission

1. ~~**Figure P1-1 (protocol diagram):**~~ DONE — `manuscript/figures/P1-1_protocol_diagram.pdf`, included in §05a-methods.
2. ~~**Table P1-1 (nearest-work matrix):**~~ DONE — `manuscript/tables/P1-T1_nearest_work.tex`, included via `\input` in §06.
3. ~~**Figure/table LaTeX infrastructure:**~~ DONE — graphicx/booktabs/tabularx/caption/longtable/array/ragged2e in `main.tex`; figures + tables all `\label`/`\ref`-linked; manuscript compiles clean.
4. ~~**MAST mode-name check:**~~ DONE — all 14 mode names retrieved from full text (Appendix A); none targets a formulation/search-universe/representation/decomposition/measurement coordinate; P1.D2 not narrowed further. Recorded in §06 and the matrix. No remaining open check can move the P1.D2 verdict.
5. ~~**Surfaced-but-unfetched cluster:**~~ DONE — TRAIL, AEGIS, AgenTracer, AgentErrorBench, ErrorProbe, AgentRx, REFLECT and span-level/DRIFT all retrieved and read; none attaches a permission to modify the formulation or search universe on the basis of the diagnosed error type; P1.D2 safe against the failure-attribution family. Recorded in §06 and the matrix.

**Remaining pre-submission checks (no longer blockers):**
6. SCION checkpoint-failure semantics — a failed REP verification checkpoint's re-open semantics (reopen completed stages vs fall forward) unresolved; changes no verdict (EviGraph independently establishes dependency-directed reopening), but must be closed because SCION is a required protocol-matched baseline.
7. Fresh literature-closure pass before submission — the nearest-work atlas and bibliography require one more closure pass, including the SCION bib-title correction (now fixed: "in the Agentic Era").