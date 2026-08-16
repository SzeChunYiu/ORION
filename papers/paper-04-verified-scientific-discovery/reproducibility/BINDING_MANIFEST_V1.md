# ORION-P4 Execution Binding Manifest V1

## Current Status: DESIGN_FROZEN

The protocol `P4.protected-authority.v1` is currently in `DESIGN_FROZEN` status. All execution bindings are `UNBOUND`. The protocol must be promoted to `EXECUTION_FROZEN` before any candidate runs.

## Required Execution Bindings

| Binding | Current Value | Required for EXECUTION_FROZEN |
|---------|--------------|-------------------------------|
| subject_revision | UNBOUND | Git commit hash of the ORION kernel under evaluation |
| dataset_revisions.public_claim_evidence | UNBOUND | Content hash of the public claim-evidence dataset |
| dataset_revisions.protected_attack_set | UNBOUND | Content hash of the protected attack manifest |
| dataset_revisions.clean_positive_set | UNBOUND | Content hash of the clean positive cases |
| model_provider_revisions | UNBOUND | Provider name and model version strings |
| baseline_config_hashes | UNBOUND | Per-baseline configuration hashes |
| evaluator_hash | UNBOUND | SHA-256 of the evaluator artifact |
| split_hashes | UNBOUND | Hashes of public/protected/holdout splits |
| evaluation_epoch | UNBOUND | ISO 8601 timestamp of the freeze moment |

## Promotion Checklist

Following `research/paper-programme-v1/protocols/EXECUTION_FREEZE_CHECKLIST_V1.md`:

1. [ ] Subject revision is a real, immutable git commit on a protected branch
2. [ ] All dataset revisions are content-addressed hashes
3. [ ] Model provider and version are locked
4. [ ] Baseline configurations are hashed and frozen
5. [ ] Evaluator artifact is hashed and stored in protected custody
6. [ ] Public/protected/holdout split hashes are registered
7. [ ] Evaluation epoch is timestamped
8. [ ] Protocol JSON is updated to `protocol_status: "EXECUTION_FROZEN"`
9. [ ] All execution bindings are non-`UNBOUND` values
10. [ ] Outcome remains `outcome_accessed: false`

## Invalidating Events

The following events invalidate the current freeze and require a new protocol version:
- Candidate writes to the protected evaluator or holdout
- Attack labels leak before candidate completion
- Evaluator identity changes post-outcome
- Subject or evidence content cannot be reconstructed
- Baseline configurations change post-freeze