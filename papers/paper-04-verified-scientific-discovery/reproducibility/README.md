# ORION-P4 Reproducibility Package

This directory contains the reproducibility artifact for ORION Paper IV: Non-Escalating Scientific Authority under Content-Bound Evidence and Protected Evaluation.

## Structure

```
reproducibility/
  README.md                    — this file
  BINDING_MANIFEST_V1.md       — execution bindings required for EXECUTION_FROZEN
  SCRIPT_INDEX.md              — scripts that regenerate figures/tables
evidence/
  ATTACK_MANIFEST_V1.jsonl     — attack case definitions (under protected custody)
  CUSTODY_MANIFEST_V1.json     — custody and freeze metadata
  AVAILABILITY_STATEMENT_V1.md — data/code availability statement
  CLAIM_LEDGER_V1.md           — mapping headline claims to evidence
  NOVELTY_AUDIT_V1.md          — novelty closure audit
figures/
  generate_figures.py          — script to regenerate all figures
  p4_1_authority_pipeline.svg
  p4_2_false_promotion.svg
  p4_3_coverage_frontier.svg
  p4_4_detection_by_attack.svg
  p4_5_attribution_vs_support.svg
  p4_6_cost_false_promotion.svg
protocol/
  PROTOCOL_V1.json             — frozen protocol artifact
  ATTACK_CASE_SCHEMA_V1.json   — attack case schema
  CUSTODY_POLICY_V1.md         — custody policy
  THREAT_MODEL_V1.md           — threat model
  STATISTICAL_ANALYSIS_PLAN_V1.md — statistical analysis plan
  METRICS_REGISTRY_V1.json     — metric definitions
  PLOT_SPEC_V1.md              — figure and table specifications
  FREEZE_MANIFEST_V1.md        — freeze status documentation
```

## Replay Instructions

### Prerequisites
- Python 3.11+
- `pip install -e '.[dev]'` from the ORION repository root

### Regenerate figures
```bash
cd papers/paper-04-verified-scientific-discovery
python figures/generate_figures.py
```

### Run protocol validation tests
```bash
pytest tests/ -k "P4" -v
```

### Run the protected campaign
```bash
python -m orion.benchmarks.campaign_runner \
  --manifest papers/paper-04-verified-scientific-discovery/evidence/ATTACK_MANIFEST_V1.jsonl \
  --output papers/paper-04-verified-scientific-discovery/results/ \
  --seed 20260816
```

## Protected Status

The attack manifest and gold labels are under protected custody. Public cases are marked `PUBLIC_CLEAN` or `PUBLIC_HOSTILE` in the custody class. Protected cases are marked `PROTECTED_HOSTILE` or `PROTECTED_HOLDOUT` and their labels are hidden from the candidate. See `CUSTODY_MANIFEST_V1.json` for the full split.

## Hash Verification

All evidence objects carry content hashes (SHA-256 of the content string) and provenance hashes (SHA-256 of the provenance metadata). The attack manifest has a top-level artifact hash computed as SHA-256 of the canonical JSON representation of each case (excluding the artifact_hash field). These hashes are frozen before candidate execution.