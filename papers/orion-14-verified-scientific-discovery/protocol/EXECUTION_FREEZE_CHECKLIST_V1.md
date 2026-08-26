# Execution Freeze Checklist — ORION-ORION-14 (V1)

**Protocol:** ORION-14.protected-authority.v1  
**Status:** `EXECUTION_FROZEN` / launch authorized by signed green freeze attestation  
**Promotion criteria:** all 12 items below are evidenced before the publication-authorizing candidate run starts.

A first hidden preparation (`31967050382`) is explicitly superseded and void because a pre-execution audit found that the harness omitted the protocol-frozen ablation arm. It was never executed. All values below refer only to the replacement final host preparation `31967352555`, generated after the complete harness preflight passed.

## Pre-freeze verification

- [x] **1. Subject revision recorded**
  - Git commit: `46977ea104162c4cf64da8138a4c4759065fe6d4`.
  - subject archive SHA-256: `4605bfd7d658018a2759ab43d7dd444ab74200adb8f98a8de485677bd09d98c5`.

- [x] **2. Dataset content hashes captured**
  - public claim/evidence: `08305b3b895d93c2d34b1fefbab9f18642dbe14030bfb75c3370b27067d29502`.
  - protected attack set: `23c7732118bf750b4f5b927aab271cf1e7ee1068d8dc1838ca5119d7e436b102`.
  - clean-positive set: `3378b8a7932bc7f9c63c4642fa2b8c6af62d68077aac1ea688a9c72c9aacb8f0`.
  - protected holdout: `bcbe73d2fa4a6466776e509ed3d24fe26584eeb079a6c291b602ba23191b5787`.
  - exact source snapshot: `3f49cc1b4e4b5aa1d5108d9831d9d547d0ffb458dce2f95c8ac084c7d6dd2a43`.

- [x] **3. Baseline and ablation configuration hashes captured**
  - complete config SHA-256: `efa50d3f4e1d76589f80a813e52805b01940409cf353c4826713935a87d8ca84`.
  - binds nine comparison mechanisms and all eight protocol-frozen ORION ablations.

- [x] **4. Evaluator/guard artifact hashed**
  - canonical executable harness bundle SHA-256: `14a4c01442bd5f1d17eb4c7c443d94cbcf198e4e910a62d4126e6f35f27ad0c7`.
  - binds generator, production candidate adapter, comparator runner, ablation runner, protected evaluator, ablation evaluator, independent reproducer and config.

- [x] **5. Model provider revisions frozen**
  - `deterministic/no-LLM`.

- [x] **6. Split hashes computed**
  - complete split SHA-256: `747213c60d7a6087a6f6fda5e25546acae5ee70ec1b5b9b7db3868f208213959`.
  - allocation: 30 public clean; 120 post-run public hostile; 120 protected hostile; 150 protected holdout.

- [x] **7. Evaluation epoch frozen**
  - `2026-08-16T19:22:06Z`.

## Run manifest preparation

- [x] **8. Attack manifest generated**
  - **420** cases across all **13** frozen families.
  - 60 clean positives + 30 per hostile family.
  - each protected case individually content-addressed.
  - `attack_label_visible_to_candidate=false` for all cases.
  - 420 mechanical-gold cases; 0 ambiguous cases.

- [x] **9. Gold labels stored in protected host custody**
  - final host run `31967352555`, job `95214444166`, worker `2618f44d-b794-48f5-9fc7-d5743fabf243` in `westus3`.
  - candidate-visible artifact `p4-host-prep-public-31967352555`, ID `9268846910`, ZIP SHA-256 `1b21853d1680bfc2da1dcd748730991a7c6ad87fa8a501d1f802e81c99d2ae4c`.
  - protected artifact `p4-host-prep-protected-31967352555`, ID `9268847119`, ZIP SHA-256 `ac1de4e9d2748144a2b534c10a1a5c8f5c028c4ec03f2a9354b061c5fde512bc`.
  - host validation proves candidate handoff contains exactly `case_id` + `candidate_visible` and no family/gold/custody/expected-terminal field.
  - human-adjudication rubric triggered on 0 cases; no human adjudication is falsely claimed for mechanical gold.

- [x] **10. Run manifest created**
  - run-manifest SHA-256: `47a6085c810163f5db7d0b3382f04c2d369a08479b495334da4cabe9d109c567`.
  - candidate manifest SHA-256: `5a7d05be9fcc4febb4902a127e47d232a27de603343fbf492dc4b6f6020b2ce1`.
  - secret-seed commitment: `06af008c50929083e50676d0a760da6f7c7f3cd1b9c6150fb2a41ef875287aa4`; seed itself was not logged.

## Freeze commitment

- [x] **11. Execution bindings recorded in `PROTOCOL_V1.json`**
  - all execution fields carry the exact final values above.
  - `protocol_status = EXECUTION_FROZEN`.
  - `outcome_accessed = false`.

- [x] **12. GitHub-verified `main` freeze commit + green exact-commit CI**
  - freeze PR: `#144`.
  - verified `main` merge commit: `5019b41b0da0d0763981d6d72975485517f923b3`.
  - GitHub signature verification: `verified=true`, reason `valid`, verified at `2026-08-16T19:43:38Z`.
  - exact-main CI run: `31968436593`; test job `95217050050`; conclusion `success`.
  - the freeze merge contains no `CAMPAIGN_TRIGGER_V1.txt`; therefore the protected candidate did not run before this attestation existed.
  - the separate launch change may now add the campaign trigger without modifying subject, hidden set, comparator/ablation config, evaluator harness, split or epoch.

## Sign-off / custody identities

| Role | Identity | Date | Signature / attestation |
|---|---|---|---|
| Protocol author | repository protocol V1 | 2026-08-16 | complete prospective design + execution bindings |
| Independent host | GitHub Actions run `31967352555`, job `95214444166` | 2026-08-16T19:22:06Z | content-addressed gold-blind host artifacts and SHA-256 commitments |
| Reviewer / freeze attestation | GitHub merge `5019b41b0da0d0763981d6d72975485517f923b3` + CI `31968436593` | 2026-08-16T19:43:38Z | GitHub signature valid; exact-main `pytest -q` green |

## Post-freeze conditions

- All 12 pre-run conditions were satisfied before the launch marker was authored.
- Any change to subject, hidden set, config, executable harness, split or epoch voids this freeze and requires a fresh hidden set.
- If the protected result exposes a subject defect, preserve that run; a repaired subject requires a new subject binding and newly generated hidden split.
- Any invalidating condition from `FREEZE_MANIFEST_V1.md` voids the run.
