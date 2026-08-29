# ORION 19–20: paper-specific top-tier closure contracts

## ORION-19 — Clinical decision support in intensive care
- `BAND`: B
- `CURRENT_TOP_TIER_READY`: false
- `BASELINE_PROMOTION_ALLOWED`: true
- `IDENTITY`: active_bounded
- `HARD_RETRACTION`: false
- `CURRENT`: One real eICU-like cohort with three seeds/stress exists; single-site/single-governance evidence caps the claim.
- `GAPS`: Single-cohort development cannot establish transportability or clinical utility. || Calibration, threshold utility, subgroup safety, and temporal drift need stronger evaluation. || Missingness, treatment-policy confounding, and outcome-definition portability are unresolved.
- `NEXT_EVIDENCE`: A1: freeze intended use, target/horizon, and variable availability audit. || A2: construct site-portable data dictionary and extraction tests. || A3: preregister calibration/net-benefit/subgroup hierarchy.
- `PRIMARY_ENDPOINTS`: External-site discrimination and calibration for the locked clinical target. || Net benefit/decision utility at preregistered thresholds compared with standard care/baselines. || Safety non-inferiority for prespecified patient subgroups and missingness strata.
- `EXTERNAL_STATUS`: required_not_yet_credited
- `EXTERNAL_REPLICATION`: At least two external ICU cohorts from independent health systems plus a prospective or silent-deployment temporal evaluation where feasible. || External clinical investigators control cohort extraction, coding maps, outcomes, and final analysis; site-specific recalibration is a separate prespecified secondary lane.
- `CALIBRATION_UNCERTAINTY`: Report site-specific and hierarchical AUROC/AUPRC, calibration slope/intercept, proper scores, and confidence intervals. || Use decision-curve analysis with prespecified thresholds; correct multiplicity for primary subgroups and endpoints.
- `CONTROLS`: Label-time leakage and post-outcome variable controls. || Simple prevalence/age/acuity baselines.
- `SUCCESS`: Locked-model external calibration and net benefit pass at both sites, with subgroup safety margins satisfied. || Workflow evaluation shows actionable lead time and acceptable alarm burden.
- `KILL`: Single-site-only evidence, failed calibration, no net benefit, or subgroup harm blocks promotion. || Any temporal leakage or post-hoc target/horizon change is a hard failure.
- `MANUSCRIPT_UNLOCK`: Only after independently governed multicentre, temporal, calibrated, decision-utility, and subgroup-safety validation pass.
- `FALLBACK`: Publish a transparent single-cohort methods paper or external-validation protocol with no deployment claim.

## ORION-20 — Causal tensor decompositions
- `BAND`: A
- `CURRENT_TOP_TIER_READY`: false
- `BASELINE_PROMOTION_ALLOWED`: true
- `IDENTITY`: active_top_tier_closure
- `HARD_RETRACTION`: false
- `CURRENT`: Three positive cohorts and permutation/cross-model checks exist; DRG constituent consistency, provenance, and identifiability require closure.
- `GAPS`: Constituent definitions or mappings may vary across cohorts and create artificial factors. || Causal interpretation may exceed what tensor identifiability and observational interventions support. || Permutation controls do not replace negative-control outcomes/exposures and external causal validation.
- `NEXT_EVIDENCE`: A1: freeze and independently audit constituent maps and provenance. || A2: write assumption-to-test identifiability matrix. || A3: add negative-control outcome/exposure and mapping perturbations.
- `PRIMARY_ENDPOINTS`: Cross-cohort recovery/stability of preregistered factors after constituent-map audit. || Causal or predictive endpoint under explicit identifiability assumptions and negative controls. || External-cohort improvement over matched baselines with uncertainty at the cohort level.
- `EXTERNAL_STATUS`: required_not_yet_credited
- `EXTERNAL_REPLICATION`: At least one new external cohort and one independent reanalysis of an existing cohort, with constituent mapping and outcomes controlled externally. || External analysts implement the mapping and at least one comparator from the frozen specification; authors cannot alter factor number or labels after outcome unblinding.
- `CALIBRATION_UNCERTAINTY`: Report uncertainty in factors, loadings, factor number, mapping, and downstream effects; avoid treating estimated factors as fixed. || Use calibration/proper scores for predictive components and sensitivity/e-values or partial-identification bounds for causal components where appropriate.
- `CONTROLS`: Permutation/random factor controls. || Negative-control outcomes and exposures.
- `SUCCESS`: Constituent provenance and consistency pass independent audit. || Factors and causal endpoints replicate in the new cohort and survive identifiability/mapping sensitivity.
- `KILL`: Mapping inconsistency, label/provenance leakage, failed negative controls, or reliance on untestable identification without sensitivity blocks causal promotion. || If factors are stable but causal evidence fails, recast as descriptive representation work.
- `MANUSCRIPT_UNLOCK`: Only after DRG/constituent provenance closure, explicit identifiability, new-cohort replication, uncertainty propagation, and negative-control success pass.
- `FALLBACK`: Publish a multi-cohort descriptive tensor resource with causal language removed if identification does not survive.
