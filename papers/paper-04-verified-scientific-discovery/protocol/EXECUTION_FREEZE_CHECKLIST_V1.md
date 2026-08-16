# Execution Freeze Checklist — ORION-P4 (V1)

**Protocol:** P4.protected-authority.v1  
**Status:** DESIGN_FROZEN → EXECUTION_FROZEN  
**Promotion criteria:** All 12 items below must be verified and signed off by the independent host.

## Pre-freeze verification

- [ ] **1. Subject revision recorded**
  - Record the exact 40-char SHA commit hash of the subject (candidate system) under test.
  - The revision must be the same across all evaluation runs.
  - No code changes after the freeze timestamp.

- [ ] **2. Dataset content hashes captured**
  - `dataset_revisions.public_claim_evidence`: Release tag or content hash (SHA-256) of the public claim–evidence corpus.
  - `dataset_revisions.protected_attack_set`: Content hash of the full attack manifest JSONL.
  - `dataset_revisions.clean_positive_set`: Content hash of the clean positive evaluation set.

- [ ] **3. Baseline configuration hashes captured**
  - SHA-256 per baseline configuration (config file or serialised parameters).
  - Each baseline must be pinned to a specific revision.

- [ ] **4. Evaluator/guard artifact hashed**
  - SHA-256 of the evaluator or guard artifact (binary, container image, or script).
  - The evaluator identity must match the registered identity in the custody policy.

- [ ] **5. Model provider revisions frozen**
  - Record the exact provider/model/version mapping for every LLM call in the evaluation.
  - If provider APIs are versioned, record the API version.

- [ ] **6. Split hashes computed**
  - Per-split content hash (SHA-256) for every data partition: train, validation, test, holdout, hostile.

- [ ] **7. Evaluation epoch frozen**
  - ISO 8601 timestamp marking the start of the evaluation epoch.
  - No evaluation runs outside this epoch are accepted.

## Run manifest preparation

- [ ] **8. Attack manifest generated**
  - ≥385 cases across ≥13 attack families (see `ATTACK_CASE_SCHEMA_V1.json`).
  - All required fields populated: `case_id`, `attack_family`, `candidate_visible`, `protected_gold`, `evidence_objects`, `expected_authority_terminal`, `custody_class`.
  - `attack_label_visible_to_candidate`: `false` for all cases.

- [ ] **9. Gold labels stored in protected host custody**
  - Attack gold labels are stored by the independent host.
  - The candidate system never has access to gold labels during evaluation.
  - Custody transfer is logged and auditable.

- [ ] **10. Run manifest created**
  - `RUN_MANIFEST_SCHEMA_V1.json` describes the evaluation run structure.
  - All runs are parameterised by the frozen bindings.

## Freeze commitment

- [ ] **11. Execution bindings recorded in PROTOCOL_V1.json**
  - Update `execution_bindings` block in `PROTOCOL_V1.json` with all captured hashes, revisions, and timestamps.
  - Every field must transition from `UNBOUND` to a concrete value.

- [ ] **12. Protocol status promoted to EXECUTION_FROZEN**
  - Set `protocol_status = "EXECUTION_FROZEN"` in `PROTOCOL_V1.json`.
  - Commit the frozen protocol artifact to a signed, timestamped commit.
  - CI passes on the frozen protocol commit.
  - **No outcome inspection before this commit.**

## Sign-off

| Role | Name | Date | Signature |
|---|---|---|---|
| Protocol author | | | |
| Independent host | | | |
| Reviewer | | | |

## Post-freeze conditions

- Outcomes must not be inspected before the `EXECUTION_FROZEN` commit is created.
- Any change to the frozen bindings requires a new protocol version (V2).
- If any invalidating condition from `FREEZE_MANIFEST_V1.md` §6 is triggered, the run is void.