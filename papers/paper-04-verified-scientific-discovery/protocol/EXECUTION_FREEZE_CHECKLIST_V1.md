# Execution Freeze Checklist — ORION-P4 (V1)

**Protocol:** P4.protected-authority.v1  
**Status:** `EXECUTION_FROZEN` / launch blocked pending exact-main attestation  
**Promotion criteria:** all 12 items below must be evidenced before the publication-authorizing candidate run starts.

## Pre-freeze verification

- [x] **1. Subject revision recorded**
  - Git commit: `46977ea104162c4cf64da8138a4c4759065fe6d4`.
  - deterministic subject archive SHA-256: `4605bfd7d658018a2759ab43d7dd444ab74200adb8f98a8de485677bd09d98c5`.
  - this is the only subject accepted by the frozen campaign.

- [x] **2. Dataset content hashes captured**
  - public claim/evidence: `3ac0bdff2c79a56e82148ffee8478ea3320f8ed0013852ea964a8b1218a87d37`.
  - protected attack set: `66d19d6e4b2756393e6a39539a388a8f312448538b180fd789c7dbd6a882c1eb`.
  - clean-positive set: `6e3f56806e69e1ea0878d133601b0cb83b61ed8cd92954f3d1476c5523ea828d`.
  - protected holdout set: `98ca603f002e4f8e7a34f1c514e1ecfc6722f51363a40ba86c6e81a40dc36c0a`.
  - exact source snapshot: `1ba3008bb055565ea5818833c8fe1d65dca0ebb4e454c5a06f98d35025eb8cd8`.

- [x] **3. Baseline configuration hashes captured**
  - complete nine-system baseline config SHA-256: `85871602539250e2a749f451439e978c34de9300c4c17370a29a5010d3d422fb`.
  - the exact six `AuthorityBenchmarkPanel.v1` baseline IDs plus citation-format, pooled-support and auditability comparators are frozen in that config.

- [x] **4. Evaluator/guard artifact hashed**
  - canonical executable-harness bundle SHA-256: `2182da8c4bdccac6d344d51359db05914b6c12c1743d8b2daf8bb7777e514253`.
  - the bundle binds generator, production candidate adapter, baseline runner, protected evaluator, independent reproducer and baseline config.

- [x] **5. Model provider revisions frozen**
  - mapping: `deterministic/no-LLM`.
  - no provider API/model drift is possible inside this campaign.

- [x] **6. Split hashes computed**
  - complete public/protected/holdout split SHA-256: `77bfdd211093a99f419d4e5f027d516f8cf399b97e8507b473605917f2b370d5`.
  - allocation: 30 public clean; 120 post-run public hostile; 120 protected hostile; 150 protected holdout.

- [x] **7. Evaluation epoch frozen**
  - `2026-08-16T19:15:50Z`.

## Run manifest preparation

- [x] **8. Attack manifest generated**
  - independent host generated **420** cases across all **13** frozen families after method/harness preflight.
  - 60 clean positives and 30 cases for each of the 12 hostile families.
  - each protected case is individually content-addressed.
  - `attack_label_visible_to_candidate=false` for every case.
  - mechanical-gold cases: 420; ambiguous cases: 0.

- [x] **9. Gold labels stored in protected host custody**
  - independent host run `31967050382`, job `95213700118`.
  - candidate-visible artifact ID: `9268766640`.
  - protected artifact ID: `9268766928`.
  - candidate handoff contains exactly `case_id` + `candidate_visible`; host validation proves protected gold/family/custody/expected-terminal fields are absent.
  - the written human-adjudication rubric was not triggered because the host generated zero ambiguous cases; no human adjudication is claimed for mechanical gold.

- [x] **10. Run manifest created**
  - run-manifest SHA-256: `dea867f8de7f5e10699ce69a0bf91b2361cf2d9b056d2ff3a511d9018eb9fdb8`.
  - candidate manifest SHA-256: `8727b959493de2f7c1a9e7bde32af7b629ce2136214e6b41b497562926633b83`.
  - secret-seed commitment: `01ba803a3a22a0c17494b044cd0310efb944a5033ed4756c8f4891f0b1a01388`; seed itself is not public.

## Freeze commitment

- [x] **11. Execution bindings recorded in `PROTOCOL_V1.json`**
  - all former `UNBOUND` execution fields now carry the exact values above.
  - protocol status is `EXECUTION_FROZEN`.
  - `outcome_accessed` remains `false`.

- [ ] **12. Signed/timestamped `main` freeze commit + green exact-commit CI**
  - the freeze PR must merge to `main` as a GitHub-verified commit.
  - CI must pass on that exact `main` commit.
  - the campaign launch marker is intentionally absent from this freeze change, so no candidate run can start before this final attestation.
  - after merge + green CI, a separate launch change records the merge SHA/CI run, checks this box, and only then adds the launch marker.

## Sign-off / custody identities

| Role | Identity | Date | Signature / attestation |
|---|---|---|---|
| Protocol author | repository protocol V1 | 2026-08-16 | prospective design already frozen; execution-binding commit pending merge |
| Independent host | GitHub Actions run `31967050382`, job `95213700118`, worker `ee35bbd4-db17-4dc9-af28-15403a9ebb8b` | 2026-08-16T19:15:50Z | content-addressed host artifacts and SHA-256 commitments recorded above |
| Reviewer | exact-main CI / merge attestation | pending | item 12 intentionally open until verified main commit exists |

## Post-freeze conditions

- No result/outcome inspection is permitted before item 12 is complete.
- Any change to subject, hidden set, baseline config, executable harness bundle, split or epoch voids this freeze and requires a fresh hidden split.
- If a protected run reveals a subject defect, preserve the failed run; any repaired subject must be evaluated under a new subject binding and newly generated hidden split.
- If any invalidating condition from `FREEZE_MANIFEST_V1.md` §6 is triggered, the run is void.
