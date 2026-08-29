# ORION 04–05: paper-specific top-tier closure contracts

## ORION-04 — Meta-learning latent task structure
- `BAND`: F
- `CURRENT_TOP_TIER_READY`: false
- `BASELINE_PROMOTION_ALLOWED`: false
- `IDENTITY`: successor_only
- `HARD_RETRACTION`: true
- `CURRENT`: Hard retraction remains authoritative; current recovery discrimination and calibration are below an acceptable baseline.
- `GAPS`: Task-family leakage and repeated-instance dependence are not excluded by a family-disjoint outer design. || Calibration does not beat the stated simple reference and cannot support confident latent-structure recovery. || No causal intervention shows that the recovered representation, rather than task identity or metadata, drives transfer.
- `NEXT_EVIDENCE`: A1: define immutable task-family grouping and leakage tests. || A2: replace example-level splits with nested leave-family-out evaluation. || A3: preregister calibration superiority and intervention endpoints.
- `PRIMARY_ENDPOINTS`: Outer-family AUROC/AUPRC for the preregistered recovery target. || Brier/log score and calibration slope that beat prespecified simple baselines. || Transfer benefit on held-out families attributable to the recovered factor under intervention.
- `EXTERNAL_STATUS`: required_not_yet_credited
- `EXTERNAL_REPLICATION`: At least two independent task ecosystems plus one externally controlled family-disjoint holdout, all evaluated by a frozen container. || External curators define task-family groupings and withhold generator metadata and final labels; authors cannot revise the representation after outer-holdout access.
- `CALIBRATION_UNCERTAINTY`: Report family-level bootstrap intervals, calibration slope/intercept, Brier/log score, and decision-curve consequences of miscalibration. || Use nested tuning and multiplicity correction across latent-factor candidates.
- `CONTROLS`: Family-label permutation. || Metadata-only and superficial-cue-only controls.
- `SUCCESS`: All primary endpoints pass at the family level on the external ecosystem, including calibration better than baseline. || Interventions isolate the latent factor from metadata and superficial task identity.
- `KILL`: Calibration no better than the simple baseline, outer-family AUROC below the preregistered useful threshold, or cue-only equivalence terminates the successor headline. || Any family leakage or post-hoc taxonomy change is a hard failure.
- `MANUSCRIPT_UNLOCK`: Only after a separately named leakage-safe successor passes external family-disjoint discrimination, calibration, intervention, and replay gates; ORION-04 remains retracted.
- `FALLBACK`: Publish the failed recovery and leakage taxonomy as a negative methods paper, including a benchmark designed to expose task-family shortcut learning.

## ORION-05 — NUTS–ABC emulation and benchmark validity
- `BAND`: F
- `CURRENT_TOP_TIER_READY`: false
- `BASELINE_PROMOTION_ALLOWED`: false
- `IDENTITY`: successor_only
- `HARD_RETRACTION`: true
- `CURRENT`: Hard retraction remains authoritative because the benchmark instrument and the claimed target are not aligned.
- `GAPS`: The benchmark observable/proxy does not faithfully identify the intended posterior or sampler property. || No frozen semantic contract maps NUTS, ABC, emulator outputs, and truth into commensurate endpoints. || Simulation-based calibration, posterior predictive checking, and misspecification stress are incomplete.
- `NEXT_EVIDENCE`: A1: write and test an estimand-to-observable contract. || A2: add SBC and posterior-predictive hard gates before benchmark aggregation. || A3: include deliberately invalid proxy and overconfidence controls.
- `PRIMARY_ENDPOINTS`: Simulation-based calibration rank uniformity/coverage under the declared estimand. || Posterior predictive validity and parameter-functional error against a trustworthy reference. || Accuracy–cost Pareto improvement under a frozen compute and simulator-call budget.
- `EXTERNAL_STATUS`: required_not_yet_credited
- `EXTERNAL_REPLICATION`: Independent replication across at least three simulator families, including one model and data-generating process withheld and implemented by an external inference group. || The external group controls one simulator, random seeds, truth parameters, and final posterior reference; only the benchmark interface is shared before freeze.
- `CALIBRATION_UNCERTAINTY`: Use SBC ranks, empirical coverage with exact intervals, proper posterior scores, and uncertainty propagation from emulator to posterior. || Report Monte Carlo standard errors and convergence diagnostics; distinguish Monte Carlo error from model bias.
- `CONTROLS`: A deliberately insufficient summary statistic must fail. || A proxy observable that is uncorrelated with the estimand must not score as valid.
- `SUCCESS`: All calibration, predictive-validity, and cost endpoints pass across simulator families and under misspecification. || Clean-room implementations agree within preregistered Monte Carlo tolerance.
- `KILL`: Any proxy/estimand mismatch, failed SBC, hidden convergence exclusion, or unpropagated emulator uncertainty blocks promotion. || Any result dependent on one simulator or one posterior reference remains bounded.
- `MANUSCRIPT_UNLOCK`: Only after a separately titled benchmark/inference successor passes semantic-contract, SBC, external-simulator, uncertainty, and replay gates; ORION-05 stays retracted.
- `FALLBACK`: Publish the obstruction basis and benchmark-instrument failure as a negative/resource paper with executable anti-pattern tests.
