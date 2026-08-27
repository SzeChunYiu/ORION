# Execution Freeze Checklist — ORION-14 V2

**Campaign:** `ORION-14.protected-authority.v2` (additive post-repair campaign over base protocol `ORION-14.protected-authority.v1`)  
**Lifecycle:** `EXECUTION_FROZEN → EXECUTED → REPRODUCED → ARCHIVED`  
**Pre-outcome freeze:** outcome access was `false`; post-authorized-run outcome access is recorded only in result artifacts.

The earlier V1 420-case protected campaign remains valid evidence for its frozen subject `46977ea...`, but that subject predates the later authority support/influence/host-telemetry repair. The 39-case live GLM arm is exploratory only and is not publication-authorizing evidence because its live labels/denominators and hidden-family execution path failed a recursive audit. V2 therefore used a fresh post-repair split and never reused either outcome for tuning.

## Pre-outcome bindings

- [x] **1. Repaired subject fixed**
  - commit `f6e51b5c8f905382b8e2f5568d9035fc14241aa1`
  - archive SHA-256 `a617a30ba8ebce5f7f89ceca77dbde793a7c43f85b8b01300e8ec1ef40a1e0e4`
- [x] **2. Public-seed V2 harness falsification passed**
  - Actions run `31975709051`
  - 42 repaired-subject hostile authority tests passed
  - 420 cases; 10 comparator mechanisms; 8 ablations; 5 repeats
  - typed panel, H1 and H2 passed; independent reproduction passed
  - diagnostic only, never publication evidence
- [x] **3. Harness integrated on signed green main before hidden preparation**
  - verified merge `99aaaed87f0be20e6760b2531fbfc2d68f0f4bb4`
  - exact-main CI `31975792576`: success
- [x] **4. Fresh hidden set generated only after harness integration**
  - host trigger merge `7a50766e4b7da51e04bc27b9d7c4cc95d064ca47`, GitHub verified at `2026-08-16T22:17:24Z`
  - trigger exact-main CI `31975937550`: success
  - host run `31975937488`, job `95235321837`
- [x] **5. Candidate handoff mechanically label-blind**
  - exactly 420 opaque rows with only `case_id` + `candidate_visible`
  - no `attack_family`, `protected_gold`, `custody_class`, or `expected_authority_terminal`
  - `outcome_accessed=false` at host preparation
- [x] **6. Dataset and split identities frozen**
  - candidate manifest `c5df341a6bf63f83d2af17492c498d4d36a944ad6616097a630d8390b7bda331`
  - protected attack set `6b8b6243040163dfa582dbeb8896e2c68d6b263e3227b64e7bab199d8599897c`
  - clean positives `5fb704ef1702f1f4c6da6178530e26725f6c33a005799b128c13188f369a6cb0`
  - protected holdout `6d213ded7f3176ff470a87433bcb0b05a0fd9853595aa3bd0d07c0416bed0779`
  - public claim/evidence `0cb36a9ac9112fa7bf2ee43067598b0c3568636c1a0bbf8e2baac018bad7f35a`
  - source snapshot `d3b0ffe5f64d07747e2568c248feeef68231b35d4e66f637e6d00c8e3188b930`
  - complete split `3fe91b669643fa158f2f64c1e6ab70837afbb9b0582e297f1da6e1c3c696fcd9`
- [x] **7. Comparator/ablation configuration frozen**
  - config SHA-256 `df389938f0bf1d6ef9312c82c5cadeba9af60c9a8ce7c602c10996f73f85fd9e`
  - seven exact repaired-subject panel IDs, including DeepSciVerify, plus three auxiliary mechanisms
  - eight resource-matched ablations
- [x] **8. Executable harness frozen**
  - canonical harness SHA-256 `094f43cb320f8e8e3196049269b20ac22e7e94fa9890b80f27f38ef49f7c82ea`
  - binds generator, candidate, V1/V2 comparator layers, ablations, V1/V2 protected evaluator layers, independent reproducer layers and V2 config
- [x] **9. Run manifest and seed commitment frozen**
  - run-manifest SHA-256 `913ef0e78ba891434f44bd7ba4a250edbff656d4178577425bc581ca8cd59237`
  - seed commitment `5f39fae05fbe9ac00f7d9312b31df6c67e340e1cc70f0ff25f6435aad8419f60`; seed itself was not logged
- [x] **10. Evaluation epoch and resource policy frozen**
  - epoch `2026-08-16T22:17:32Z`
  - provider `deterministic/no-LLM`
  - 5 repeats; resource budget 12 units; full ORION/ablations use 9 units
- [x] **11. Independent custody artifacts retained separately**
  - public artifact `p4-v2-host-prep-public-31975937488`, ID `9271039558`, ZIP SHA-256 `59d1fee4a29f508c44de8d91f02a742158e0b179a0d3a47fc373b014ea0e3267`
  - protected artifact `p4-v2-host-prep-protected-31975937488`, ID `9271039728`, ZIP SHA-256 `3bdd9cf5a0b4dabf03bfff0b3583f5e1096f3dc770f99fbc1f8940ed99718f7e`
  - 420 mechanical-gold cases; 0 ambiguous; 0 human-rubric triggers
- [x] **12. Immutable V2 binding artifact recorded**
  - `PROTECTED_RUN_BINDINGS_V2.json`
  - at freeze: `status=EXECUTION_FROZEN`, `outcome_accessed=false`, `campaign_execution_authorized=false`
- [x] **13. GitHub-verified main freeze commit + green exact-main CI**
  - freeze PR #174 merged as `99bcacc82224089c34019ad82287754388dadbc5`
  - GitHub verification: `verified=true`, reason `valid`
  - exact-main CI `31976305223`: success
  - the freeze merge contained no `CAMPAIGN_TRIGGER_V2.txt`
  - launch was separately authorized only afterward.

## Authorized execution / post-run evidence

- [x] launch PR #177 merged as `6a5d454d8926d046f294f95c2be1c2386980e3e5` after freeze attestation;
- [x] protected campaign run `31976589735` completed all handoff/candidate/comparator/evaluator/reproduction/safe-bundle stages;
- [x] ORION `0/360` false promotions vs strongest frozen comparator mechanism `180/360`;
- [x] both systems `60/60` clean promotions and `0` clean false negatives;
- [x] H1 PASS; H2 PASS; H3 NOT_SUPPORTED;
- [x] actual execution telemetry: zero protected-identifier hits and zero external-IP connections;
- [x] independent headline reproduction passed;
- [x] exact publication source merge `846a0573fb881c5f9b6caa8e98aede2e51090fca` is signed/green;
- [x] permanent release tag `orion-p4-v2-peer-review-ready` targets that publication source;
- [x] archive merge `00c19ecd71071e1ad70a8820df4c198153e4da84` is GitHub-verified, ordinary CI `31979303114` passed, and TMLR audit `31979303109` passed.

## Frozen case allocation

- 420 total cases / 13 families
- 60 clean positives
- 360 hostile cases
- 120 post-run public hostile
- 120 protected hostile
- 150 protected holdout
- 420 mechanical gold / 0 ambiguous

## Invalidating events

Any outcome-dependent change to the frozen subject, hidden set, split, V2 comparator/ablation config, harness, epoch, or eligible-opportunity definitions would require a new campaign and could not reuse this split. No such invalidating event occurred in V2. Protected gold/raw traces remain outside the public release.
