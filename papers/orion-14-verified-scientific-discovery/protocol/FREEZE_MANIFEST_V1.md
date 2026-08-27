# Freeze Manifest — ORION-14 (V1)

**Protocol:** ORION-14.protected-authority.v1  
**Status:** DESIGN_FROZEN  
**Frozen by:** Protocol metrics agent (claude/p4-protocol-metrics)  
**Date:** 2026-08-16

## 1. Protocol freeze status

| Field | Value |
|---|---|
| `protocol_status` | `DESIGN_FROZEN` |
| `outcome_accessed` | `false` |
| `protocol_id` | `ORION-14.protected-authority.v1` |
| `paper_id` | `ORION-14` |

**Invariant:** The protocol design is frozen. No hypothesis, task family, baseline, ablation, metric, exclusion rule, statistical rule, safety margin, evaluator identity, or access policy may be changed without creating a new V2 protocol.

## 2. Execution bindings (remain UNBOUND)

| Binding | Value | Required for EXECUTION_FROZEN |
|---|---|---|
| `subject_revision` | UNBOUND | 40-char SHA commit hash |
| `dataset_revisions.public_claim_evidence` | UNBOUND | Release tag or content hash |
| `dataset_revisions.protected_attack_set` | UNBOUND | Content hash of the attack manifest |
| `dataset_revisions.clean_positive_set` | UNBOUND | Content hash |
| `model_provider_revisions` | UNBOUND | Provider/model/version mapping |
| `baseline_config_hashes` | UNBOUND | SHA-256 per baseline config |
| `evaluator_hash` | UNBOUND | SHA-256 of evaluator artifact |
| `split_hashes` | UNBOUND | Per-split content hash |
| `evaluation_epoch` | UNBOUND | ISO 8601 timestamp |

**All bindings remain UNBOUND.** The independent host must freeze these before `EXECUTION_FROZEN` promotion.

## 3. Metrics freeze

See `METRICS_REGISTRY_V1.json` (16 metrics: 2 primary, 14 secondary).

- **Primary:** `false_authority_promotion_rate`, `clean_authority_coverage`
- **Primary hypothesis:** H1 (superiority on false-promotion reduction)
- **Co-primary guard:** H2 (non-inferiority on clean coverage)
- **Secondary hypothesis:** H3 (correct CANNOT_CHECK accuracy)

## 4. Promotion checklist

To promote `DESIGN_FROZEN → EXECUTION_FROZEN`:

1. [ ] Record exact subject revision (40-char SHA).
2. [ ] Content-hash all datasets (public, protected, clean).
3. [ ] Content-hash all baseline configurations.
4. [ ] Content-hash the evaluator/guard artifact.
5. [ ] Freeze the evaluation epoch.
6. [ ] Generate the attack manifest (≥385 cases, ≥13 families).
7. [ ] Store attack gold labels in protected host custody.
8. [ ] Create the run manifest (`RUN_MANIFEST_SCHEMA_V1.json`).
9. [ ] Run the freeze checklist (`EXECUTION_FREEZE_CHECKLIST_V1.md`).
10. [ ] Update `execution_bindings` in `PROTOCOL_V1.json`.
11. [ ] Set `protocol_status = "EXECUTION_FROZEN"`.
12. [ ] Commit, PR, CI — **before** inspecting outcomes.

## 5. Outcome-access checklist

To access outcomes after execution:

1. [ ] Preserve the `EXECUTION_FROZEN` protocol artifact.
2. [ ] Record `outcome_accessed = true` (without changing frozen design).
3. [ ] Retain raw result JSONL as `result_manifest.jsonl`.
4. [ ] Archive all access telemetry (search, file, patch, evaluator).

## 6. Invalidating conditions

The final run cannot support the headline claim if:

- Final outcomes were inspected before required identities were frozen.
- Subject revisions are mixed across runs.
- Final gold/holdout leaked to the candidate.
- Evaluator/metric changed post-outcome without a new protocol version.
- Hidden/protected data cannot be tied to an auditable external custodian.
- Failed/null/harmful candidate observations are silently removed.
- Public benchmark search contamination is ignored where the protocol requires auditing.

## 7. Artifact inventory

| File | Description |
|---|---|
| `PROTOCOL_V1.json` | Protocol design, frozen |
| `STATISTICAL_ANALYSIS_PLAN_V1.md` | Statistical plan (H1/H2/H3, bootstrap, margins) |
| `METRICS_REGISTRY_V1.json` | 16 registered metrics with definitions |
| `PLOT_SPEC_V1.md` | 6 figures + 3 tables specification |
| `ATTACK_CASE_SCHEMA_V1.json` | Attack case schema |
| `CUSTODY_POLICY_V1.md` | Custody roles and rules |
| `THREAT_MODEL_V1.md` | Threat model |
| `EXECUTION_FREEZE_CHECKLIST_V1.md` | Checklist for execution freeze |