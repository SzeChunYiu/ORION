# ORION-P4 Execution Binding Manifest V1

## Current status: `EXECUTION_FROZEN` — campaign not launched

Protocol `P4.protected-authority.v1` is now bound to one outcome-blind, host-generated campaign. The independent host preparation completed **before any candidate execution or outcome inspection**. The final publication-authorizing campaign must use these exact identities or the run is void.

## Frozen execution bindings

| Binding | Frozen value |
|---|---|
| protocol | `P4.protected-authority.v1` |
| subject Git commit | `46977ea104162c4cf64da8138a4c4759065fe6d4` |
| subject archive SHA-256 | `4605bfd7d658018a2759ab43d7dd444ab74200adb8f98a8de485677bd09d98c5` |
| public claim/evidence SHA-256 | `3ac0bdff2c79a56e82148ffee8478ea3320f8ed0013852ea964a8b1218a87d37` |
| protected attack manifest SHA-256 | `66d19d6e4b2756393e6a39539a388a8f312448538b180fd789c7dbd6a882c1eb` |
| clean-positive set SHA-256 | `6e3f56806e69e1ea0878d133601b0cb83b61ed8cd92954f3d1476c5523ea828d` |
| protected holdout set SHA-256 | `98ca603f002e4f8e7a34f1c514e1ecfc6722f51363a40ba86c6e81a40dc36c0a` |
| source snapshot SHA-256 | `1ba3008bb055565ea5818833c8fe1d65dca0ebb4e454c5a06f98d35025eb8cd8` |
| candidate-visible manifest SHA-256 | `8727b959493de2f7c1a9e7bde32af7b629ce2136214e6b41b497562926633b83` |
| split SHA-256 | `77bfdd211093a99f419d4e5f027d516f8cf399b97e8507b473605917f2b370d5` |
| baseline config SHA-256 | `85871602539250e2a749f451439e978c34de9300c4c17370a29a5010d3d422fb` |
| executable harness bundle SHA-256 | `2182da8c4bdccac6d344d51359db05914b6c12c1743d8b2daf8bb7777e514253` |
| host run manifest SHA-256 | `dea867f8de7f5e10699ce69a0bf91b2361cf2d9b056d2ff3a511d9018eb9fdb8` |
| model/provider revision | `deterministic/no-LLM` |
| resource budget | `12.0` units |
| statistical repeats | `5` |
| evaluation epoch | `2026-08-16T19:15:50Z` |
| secret-seed commitment | `01ba803a3a22a0c17494b044cd0310efb944a5033ed4756c8f4891f0b1a01388` |

The secret seed itself is not retained in the public ledger and was not printed by the host. The commitment is sufficient to identify the generated hidden set without exposing how to reconstruct it.

## Independent host / custody evidence

- GitHub Actions host-preparation run: `31967050382`
- host job: `95213700118`
- hosted runner region: `westus3`
- hosted worker identifier: `ee35bbd4-db17-4dc9-af28-15403a9ebb8b`
- runner token permissions: repository `contents: read`, metadata read only
- candidate-visible artifact: `p4-host-prep-public-31967050382`, artifact ID `9268766640`, uploaded ZIP SHA-256 `2a6f3802ae3741c1292c6fa3fe24320ed90a7a78f82ad3eb5325d7079ad1de22`
- protected-custody artifact: `p4-host-prep-protected-31967050382`, artifact ID `9268766928`, uploaded ZIP SHA-256 `47abca636250c4b260db7407113f654194196ab3beb0d32b634bb17879112bff`
- protected artifact retention: 90 days in GitHub Actions custody pending permanent release/archive construction after the result is accepted.

The host job mechanically proved that the candidate handoff contains exactly 420 opaque cases with only `case_id` and `candidate_visible`; the strings `protected_gold`, `attack_family`, `custody_class`, and `expected_authority_terminal` are absent. Per-case attack labels therefore remain host-only before execution.

## Frozen case allocation

- total cases: **420**
- attack families: **13**
- clean positives: **60**
- hostile cases: **360**
- post-run releasable hostile slice: **120**
- protected hostile slice: **120**
- protected holdout cases: **150** (30 clean + 120 hostile)
- mechanical-gold cases: **420**
- ambiguous cases requiring adjudication: **0**
- human-adjudication rubric triggered: **0**

The written human-adjudication rubric remains frozen for ambiguous support/source relations. This campaign does **not** claim that humans adjudicated mechanical cases; no case met the rubric trigger.

## Frozen baseline identities

The first six are the exact `AuthorityBenchmarkPanel.v1` comparator IDs; the final three satisfy the wider issue-101 comparison requirements. Every baseline receives the identical candidate-visible packet and no protected gold.

1. `provenanceguard-style-source-routing`
2. `attributionbench-multisource-attribution`
3. `fire-iterative-retrieve-or-verify` (also the frozen family mapping for current DeepSciVerify-style scientific verification)
4. `claimbench-sciclaimhunt-scientific-evidence`
5. `provenai-citation-fidelity-influence`
6. `rewardhackingagents-search-contamination`
7. `citation-presence-format`
8. `pooled-evidence-nli-support`
9. `claim-level-auditability-provenance`

## Pre-outcome harness falsification

Two **non-authorizing public-seed** end-to-end preflights completed before hidden-set generation:

- run `31966945234`: green;
- run `31966998998`: green after all nine comparison configs were frozen.

Each preflight exercised 420 generated cases, gold-blind handoff validation, five deterministic repeats, production `resolve_evidence_ref`, production `evaluate_hard_gates`, all baselines, protected scoring, the typed authority panel and an independent reproduction implementation. These runs are harness tests only and are excluded from publication evidence.

## Freeze promotion checklist

Following `research/paper-programme-v1/protocols/EXECUTION_FREEZE_CHECKLIST_V1.md`:

1. [x] Subject revision and exact archive hash recorded.
2. [x] Public/protected/clean/holdout/source dataset identities content-addressed.
3. [x] All baseline configurations frozen under one exact SHA-256 manifest.
4. [x] Entire executable evaluation harness bundle content-addressed.
5. [x] Provider mapping frozen (`deterministic/no-LLM`).
6. [x] Public/protected/holdout split hash registered.
7. [x] Evaluation epoch frozen.
8. [x] 420-case / 13-family hidden attack manifest generated after method freeze.
9. [x] Gold labels stored in separate protected host artifact; candidate handoff mechanically proven gold-blind.
10. [x] Host run manifest created and content-addressed.
11. [x] `PROTOCOL_V1.json` execution bindings populated and status set to `EXECUTION_FROZEN` with `outcome_accessed=false`.
12. [ ] Signed/timestamped `main` freeze commit and exact-commit green CI attestation. **No campaign launch marker exists until this final pre-run attestation is complete.**

## Invalidating events

Any of the following voids this hidden split and requires a fresh host-generated split under a new freeze:

- any frozen harness file or baseline config changes;
- candidate receives or reconstructs protected family/gold/custody data before completion;
- candidate can write the protected evaluator/holdout artifact;
- subject commit/archive differs from the binding above;
- evaluator/harness bundle hash differs from the binding above;
- outputs are inspected before the signed `main` execution-freeze commit and green exact-commit CI;
- a subject defect is repaired after outcome access and the same hidden split is reused.
