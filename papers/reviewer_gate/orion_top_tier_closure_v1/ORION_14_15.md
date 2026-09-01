# ORION 14–15: paper-specific top-tier closure contracts

## ORION-14 — Mechanistically interpretable program synthesis
- `BAND`: A
- `CURRENT_TOP_TIER_READY`: false
- `BASELINE_PROMOTION_ALLOWED`: true
- `IDENTITY`: active_top_tier_closure
- `HARD_RETRACTION`: false
- `CURRENT`: Three-seed robustness and stress evidence exist; independent synthesis-family replication and mechanism isolation remain.
- `GAPS`: Mechanistic interpretation may be a post-hoc correlate rather than causally used by synthesis. || Three seeds are weak for high-variance search and do not replace task-family replication. || Comparator access to types, examples, and search budget may be unequal.
- `NEXT_EVIDENCE`: A1: freeze DSL/task-family-disjoint benchmark and exact verifier. || A2: equalize comparator inputs and search budget. || A3: preregister mechanism-intervention predictions.
- `PRIMARY_ENDPOINTS`: Exact solution rate on DSL/task-family-disjoint external tasks. || Causal intervention effect predicted by the proposed mechanism. || Sample/search efficiency at matched exactness and verification.
- `EXTERNAL_STATUS`: required_not_yet_credited
- `EXTERNAL_REPLICATION`: At least two synthesis engines and three DSL/task families, with one engine/family implemented or curated outside the author team. || External curators retain the final DSL tasks and independently verify solutions; the clean-room engine does not reuse the original search implementation.
- `CALIBRATION_UNCERTAINTY`: Use paired bootstrap/randomization with family clustering and multiplicity control for solution, efficiency, and interventions. || Calibrate success/abstention predictions with proper scores and risk–coverage curves.
- `CONTROLS`: Random interpretation labels. || Capacity-matched auxiliary-head control.
- `SUCCESS`: External exact solve and efficiency endpoints pass against matched baselines. || Blinded intervention predictions are accurate and the mechanism effect reproduces in the second engine.
- `KILL`: If mechanism interventions do not produce predicted changes, withdraw causal-interpretability language. || If gains disappear under matched information/compute or on external DSLs, keep a bounded system result.
- `MANUSCRIPT_UNLOCK`: Only after independent engine/DSL transfer, matched comparators, prospective intervention prediction, and exact verification pass.
- `FALLBACK`: Publish a robust synthesis benchmark or correlational interpretation paper with causal language removed.

## ORION-15 — Controlled bargaining and adaptive fairness
- `BAND`: B
- `CURRENT_TOP_TIER_READY`: false
- `BASELINE_PROMOTION_ALLOWED`: true
- `IDENTITY`: active_bounded
- `HARD_RETRACTION`: false
- `CURRENT`: Primary, stress, scale, and preregistration lanes exist. Main now distinguishes intentional materialized omissions from unwired/missing observations; unwired cells are not outcomes and cannot support either success or adversity. Evidence remains bounded without protected longitudinal external evaluation.
- `GAPS`: The six-arm or policy comparison needs a single causal estimand and valid adaptive allocation inference. || Every endpoint cell needs a machine-checkable materialization status so unwired observations cannot be laundered into missing-at-random data, success, or adversity. || Fairness may improve while retention, welfare, resource use, subgroup harm, longitudinal persistence, or interference worsens.
- `NEXT_EVIDENCE`: A1: simulate the exact adaptive six-arm design under null and alternative. || A2: freeze multi-objective causal estimands, safety hierarchy, and per-cell materialization schema; fail closed on every unwired field. || A3: instrument interference, attrition, and intentional omission before outcome access.
- `PRIMARY_ENDPOINTS`: Causal effect on the preregistered fairness metric subject to welfare/retention non-inferiority. || Longitudinal harm and benefit distribution across prespecified groups. || Valid regret or allocation-efficiency endpoint under adaptive assignment and interference.
- `EXTERNAL_STATUS`: required_not_yet_credited
- `EXTERNAL_REPLICATION`: At least two independently governed populations/environments and one prospective temporal replication with frozen allocation and stopping rules. || An external operator controls enrolment, outcomes, and subgroup definitions; analysts receive masked arm labels until the analysis code passes simulation tests.
- `CALIBRATION_UNCERTAINTY`: Use randomization-aware or doubly robust estimators valid for adaptive allocation; cluster-robust uncertainty for interference. || Gate fairness by welfare/retention/harm non-inferiority and control multiplicity across arms/groups.
- `CONTROLS`: Non-adaptive control and fairness-unaware adaptive control. || Outcome-label delay/shuffle tests.
- `SUCCESS`: Fairness improves with welfare, retention, and harm gates satisfied in both external environments. || Adaptive inference achieves preregistered operating characteristics and external replay agrees.
- `KILL`: Any harm/welfare non-inferiority failure, invalid adaptive inference, unwired endpoint treated as observed, or dependence on a perfect-ceiling artefact blocks promotion. || If only governance machinery is validated, publish it separately from empirical superiority.
- `MANUSCRIPT_UNLOCK`: Only after protected external longitudinal evaluation, adaptive-design validity, multi-objective safety gates, and independent outcome adjudication pass.
- `FALLBACK`: Publish a bounded governance/design paper and preregistered negative campaign results without claiming elite empirical generality.
