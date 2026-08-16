# ORION-P4 Data and Code Availability Statement

## Data Availability

The following data artifacts are available under the ORION repository at `papers/paper-04-verified-scientific-discovery/`:

**Publicly releasable (included in the repository):**
- Attack case schema (`protocol/ATTACK_CASE_SCHEMA_V1.json`)
- Protocol definition (`protocol/PROTOCOL_V1.json`)
- Threat model (`protocol/THREAT_MODEL_V1.md`)
- Custody policy (`protocol/CUSTODY_POLICY_V1.md`)
- Statistical analysis plan (`protocol/STATISTICAL_ANALYSIS_PLAN_V1.md`)
- Metrics registry (`protocol/METRICS_REGISTRY_V1.json`)
- Plot specification (`protocol/PLOT_SPEC_V1.md`)
- Freeze manifest (`protocol/FREEZE_MANIFEST_V1.md`)
- Public clean and public hostile attack cases (in `evidence/ATTACK_MANIFEST_V1.jsonl`, marked `PUBLIC_CLEAN` or `PUBLIC_HOSTILE`)
- Evidence content and provenance digests (in `evidence/CUSTODY_MANIFEST_V1.json`)
- Figure generation scripts (`figures/generate_figures.py`)
- SVG figure stubs (`figures/*.svg`)

**Under protected custody (not publicly released until campaign completion):**
- Protected hostile and holdout attack cases (labels and gold answers hidden)
- Candidate-run access telemetry (file, network, search, patch logs)
- Raw per-claim verdicts and authority transitions
- Evaluator and holdout identity artifacts

**Future release (upon campaign completion and protocol promotion to EXECUTION_FROZEN):**
- Full attack manifest with protected labels (delayed or partially withheld if disclosure would destroy future holdout value)
- Complete per-claim verdict CSV
- Configuration files for all baselines
- Clean-environment replay instructions for non-secret portions

## Code Availability

The ORION framework source code is available at `https://github.com/SzeChunYiu/ORION`. The code is version-controlled and all experimental configurations are hash-frozen at the evaluation epoch. The specific subject revision for this paper is `UNBOUND` until the protocol reaches `EXECUTION_FROZEN` status.

## Reproducibility

The reproducibility package at `reproducibility/` contains scripts to regenerate all safe-to-release figures and tables from the frozen summary data. Non-secret portions of the campaign can be replayed in a clean environment. The headline false-promotion result is independently reproducible by a separate reviewer or host with access to the protected custody artifacts.

## License

The ORION framework is distributed under the repository license. The reproducibility package and manuscript are part of the same distribution.