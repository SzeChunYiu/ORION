# ORION 06–08: paper-specific top-tier closure contracts

## ORION-06 — Multi-agent bargaining selection
- `BAND`: B
- `CURRENT_TOP_TIER_READY`: false
- `BASELINE_PROMOTION_ALLOWED`: true
- `IDENTITY`: active_bounded
- `HARD_RETRACTION`: false
- `CURRENT`: Two stress lanes support a bounded claim; independent-cohort and mechanism evidence are still missing.
- `GAPS`: Selection gains may be environment- or seed-specific. || The causal role of the proposed selection rule is not isolated from exploration, reward scaling, or policy capacity. || Fairness, welfare, stability, and regret need a prespecified joint inferential hierarchy.
- `NEXT_EVIDENCE`: A1: consolidate all bargaining lanes under one immutable protocol schema. || A2: run selector-disabled and matched-exploration interventions. || A3: precompute environment-level power and multiplicity hierarchy.
- `PRIMARY_ENDPOINTS`: Social welfare at a preregistered fairness constraint. || Exploitability/regret or incentive-compatibility proxy under the declared game class. || Agreement stability/failure rate under protocol and population shift.
- `EXTERNAL_STATUS`: required_not_yet_credited
- `EXTERNAL_REPLICATION`: At least three bargaining environments from two codebases, with one codebase and final payoff families controlled by an external evaluator. || External evaluators define one protocol/payoff family and hold final seeds; any human study uses independent ethics review and preregistered exclusion rules.
- `CALIBRATION_UNCERTAINTY`: Use hierarchical bootstrap or mixed models over environments and seeds, paired where common random numbers are valid. || Report simultaneous uncertainty for welfare, fairness, and regret; specify one gatekeeping order rather than selecting the favourable endpoint.
- `CONTROLS`: Selection scores shuffled across agents. || Reward-scale transformation preserving strategic structure.
- `SUCCESS`: All primary endpoints pass on the independent codebase with welfare improvement and fairness/regret constraints satisfied. || Ablations identify a selection-specific mechanism rather than extra compute/capacity.
- `KILL`: Failure on the external environment, fairness degradation beyond the bound, or seed fragility blocks broad promotion. || If selection adds no value beyond matched exploration/capacity, recast as a benchmark result.
- `MANUSCRIPT_UNLOCK`: Only after independent-environment transfer, selector-specific ablation, hierarchical inference, and calibrated failure prediction pass; until then retain bounded claims.
- `FALLBACK`: Publish a carefully scoped multi-environment benchmark or negative mechanism study, preserving stress failures.

## ORION-07 — Ambiguity decomposition in tractography/clinical trajectories
- `BAND`: A
- `CURRENT_TOP_TIER_READY`: false
- `BASELINE_PROMOTION_ALLOWED`: true
- `IDENTITY`: active_top_tier_closure
- `HARD_RETRACTION`: false
- `CURRENT`: Strongest current lane, with significant primary results and negative controls; still single-cohort and single-pipeline bounded.
- `GAPS`: Single-cohort evidence cannot establish clinical or anatomical generality. || Ambiguity components may depend on tractography pipeline, acquisition, annotation, or patient mix. || Gold/reference uncertainty and inter-rater disagreement need explicit propagation.
- `NEXT_EVIDENCE`: A1: freeze patient-level analysis and preprocessing sensitivity matrix. || A2: assemble independent annotation/adjudication protocol. || A3: secure two external sites with one temporal holdout.
- `PRIMARY_ENDPOINTS`: External-site replication of the prespecified decomposition effect with multiplicity-controlled inference. || Incremental calibrated prediction or decision value beyond the strongest clinical/pipeline baseline. || Robustness of component interpretation across acquisition and tractography pipelines.
- `EXTERNAL_STATUS`: required_not_yet_credited
- `EXTERNAL_REPLICATION`: At least two external centres with distinct acquisition and tractography pipelines, one evaluated by investigators not involved in model development. || External sites retain patient identifiers, raw acquisition, preprocessing choices, and final outcomes; only de-identified frozen outputs enter the prespecified analysis.
- `CALIBRATION_UNCERTAINTY`: Use hierarchical site/patient models, false-discovery control for component families, and bootstrap uncertainty for incremental performance. || Report calibration slope/intercept, Brier/log score, calibration-in-the-large, and decision curves.
- `CONTROLS`: Negative anatomical regions or outcomes with no plausible association. || Patient-label permutation within site.
- `SUCCESS`: External replication passes at both sites with consistent direction and the prespecified hierarchical endpoint. || Incremental calibrated decision value survives pipeline and reference-uncertainty sensitivity.
- `KILL`: A site-direction reversal unexplained by a prespecified moderator, loss of calibration, or dependence on one pipeline blocks the broad claim. || If clinical net benefit is absent, retain a mechanistic/measurement paper only.
- `MANUSCRIPT_UNLOCK`: Only after multicentre external validation, patient-level inference, reference-uncertainty propagation, and decision utility pass; the present single-cohort claim stays bounded meanwhile.
- `FALLBACK`: Publish a strong single-cohort measurement/mechanism paper with transparent site and pipeline limitations if external utility does not replicate.

## ORION-08 — Audit-aware sequential decisions / DRIP
- `BAND`: B
- `CURRENT_TOP_TIER_READY`: false
- `BASELINE_PROMOTION_ALLOWED`: true
- `IDENTITY`: active_bounded
- `HARD_RETRACTION`: false
- `CURRENT`: The bounded DRIP mechanism retains supported directional contrasts; main now contains both the exact Holm-controlled sign family and all 12 paired bootstrap mean intervals, with the manuscript narrowed where intervals contain zero. Adversarial calibration and external selection robustness remain open.
- `GAPS`: The scoped-versus-never mean comparison remains statistically undetermined in the committed paired intervals even though directional sign tests can survive Holm correction. || Directional paired signs and paired mean effects answer different estimands; neither may be rhetorically substituted for the other, and the primary comparator hierarchy is not yet externally validated. || Audit-trigger probabilities, expected value, and catastrophic regret need calibration under adversarial cost, relocation, and evidence-quality distributions.
- `NEXT_EVIDENCE`: A1: independently reproduce the merged Holm family and all 12 paired bootstrap intervals from the frozen records, then verify exact table/PDF transcription and estimand separation. || A2: freeze the primary comparator hierarchy and sealed scenario generator before external outcomes. || A3: add conditional calibration, abstention, and catastrophic-regret gates.
- `PRIMARY_ENDPOINTS`: Paired expected utility/regret of the preregistered scoped policy against the primary comparator hierarchy. || Family-wise controlled evidence that the policy improves the declared primary decisions without relying on a non-surviving contrast. || Calibration and proper-score performance of audit/relocation-risk predictions.
- `EXTERNAL_STATUS`: required_not_yet_credited
- `EXTERNAL_REPLICATION`: External evaluators generate at least two scenario banks with distinct cost, relocation, evidence-quality, and adversarial processes; one bank remains sealed. || Scenario generators, seeds, and final outcomes are controlled outside the author team; policy code is containerized and thresholds frozen before release.
- `CALIBRATION_UNCERTAINTY`: Report paired mean effect sizes and bootstrap confidence intervals beside the exact directional sign tests; do not let sign significance upgrade a mean effect whose interval contains zero. || The exact Holm family on main is controlling for directional paired signs; preserve all 12 rows, the exact-tie negative control, and the two mean-undetermined contrasts.
- `CONTROLS`: Policy labels permuted across paired outcomes. || A zero-information audit channel.
- `SUCCESS`: The preregistered primary contrast and family-wise hierarchy pass on both external banks. || Calibration and regret remain acceptable under adversarial shift without retuning.
- `KILL`: If the scoped-versus-never primary contrast remains undetermined, the manuscript cannot claim general superiority over never auditing. || Multiplicity failure, selection on the sealed bank, or adversarial catastrophic regret blocks promotion.
- `MANUSCRIPT_UNLOCK`: Only after the merged multiplicity and paired-uncertainty surfaces are jointly revalidated from frozen records, every estimand keeps its correct directional/null/undetermined reading, and calibrated adversarial evidence is independently replicated; current claims remain bounded.
- `FALLBACK`: Publish the policy-comparison benchmark and null/indeterminate contrasts with a narrower decision-analysis claim.
