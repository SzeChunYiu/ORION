# ORION-14 Execution Binding Manifest V1

## Current status: `EXECUTION_FROZEN` — launch authorized

Protocol `ORION-14.protected-authority.v1` is bound to one outcome-blind, independently generated campaign. The host prepared the final hidden set **before any candidate execution or protected outcome inspection**. The publication-authorizing campaign must use these exact identities or the run is void.

The execution freeze is now externally attested by a GitHub-verified `main` merge and green CI on that exact commit. The separate launch change may therefore add the campaign marker without changing any frozen scientific identity.

## Superseded pre-execution preparation

Host run `31967050382` was generated outcome-blind but is **void and never executed**. A recursive pre-run audit found that the harness omitted the eight protocol-frozen ORION ablations. Before any candidate saw that split, the harness was extended, the full 420-case public-seed preflight was rerun successfully with all ablations, and a fresh secret-seeded set was generated. No value from the superseded hidden set is admissible evidence.

## Final frozen execution bindings

| Binding | Frozen value |
|---|---|
| protocol | `ORION-14.protected-authority.v1` |
| subject Git commit | `46977ea104162c4cf64da8138a4c4759065fe6d4` |
| subject archive SHA-256 | `4605bfd7d658018a2759ab43d7dd444ab74200adb8f98a8de485677bd09d98c5` |
| public claim/evidence SHA-256 | `08305b3b895d93c2d34b1fefbab9f18642dbe14030bfb75c3370b27067d29502` |
| protected attack manifest SHA-256 | `23c7732118bf750b4f5b927aab271cf1e7ee1068d8dc1838ca5119d7e436b102` |
| clean-positive set SHA-256 | `3378b8a7932bc7f9c63c4642fa2b8c6af62d68077aac1ea688a9c72c9aacb8f0` |
| protected holdout set SHA-256 | `bcbe73d2fa4a6466776e509ed3d24fe26584eeb079a6c291b602ba23191b5787` |
| source snapshot SHA-256 | `3f49cc1b4e4b5aa1d5108d9831d9d547d0ffb458dce2f95c8ac084c7d6dd2a43` |
| candidate-visible manifest SHA-256 | `5a7d05be9fcc4febb4902a127e47d232a27de603343fbf492dc4b6f6020b2ce1` |
| split SHA-256 | `747213c60d7a6087a6f6fda5e25546acae5ee70ec1b5b9b7db3868f208213959` |
| baseline + ablation config SHA-256 | `efa50d3f4e1d76589f80a813e52805b01940409cf353c4826713935a87d8ca84` |
| executable harness bundle SHA-256 | `14a4c01442bd5f1d17eb4c7c443d94cbcf198e4e910a62d4126e6f35f27ad0c7` |
| host run manifest SHA-256 | `47a6085c810163f5db7d0b3382f04c2d369a08479b495334da4cabe9d109c567` |
| model/provider revision | `deterministic/no-LLM` |
| resource budget | `12.0` units; full ORION and every ablation use `9.0` |
| statistical repeats | `5` |
| evaluation epoch | `2026-08-16T19:22:06Z` |
| secret-seed commitment | `06af008c50929083e50676d0a760da6f7c7f3cd1b9c6150fb2a41ef875287aa4` |

The secret seed itself was not logged. The commitment identifies the hidden generation event without exposing a reconstruction key.

## Independent host / custody evidence

- final GitHub Actions host run: `31967352555`
- final host job: `95214444166`
- hosted runner region: `westus3`
- worker identifier: `2618f44d-b794-48f5-9fc7-d5743fabf243`
- token permission: repository contents read + metadata read only
- candidate-visible artifact: `p4-host-prep-public-31967352555`, artifact ID `9268846910`, ZIP SHA-256 `1b21853d1680bfc2da1dcd748730991a7c6ad87fa8a501d1f802e81c99d2ae4c`
- protected-custody artifact: `p4-host-prep-protected-31967352555`, artifact ID `9268847119`, ZIP SHA-256 `ac1de4e9d2748144a2b534c10a1a5c8f5c028c4ec03f2a9354b061c5fde512bc`
- current Actions retention: 90 days; permanent releasable archive is constructed only after the result/reproduction gate passes.

The host mechanically proved that the candidate handoff contains exactly 420 opaque cases and only `case_id` + `candidate_visible`. The strings `protected_gold`, `attack_family`, `custody_class`, and `expected_authority_terminal` are absent.

## Final case allocation

- total cases: **420**
- attack families: **13**
- clean positives: **60**
- hostile cases: **360**
- post-run releasable hostile slice: **120**
- protected hostile slice: **120**
- protected holdout: **150** (30 clean + 120 hostile)
- mechanical gold: **420**
- ambiguous cases: **0**
- human-adjudication-rubric triggers: **0**

The written human-adjudication rubric remains frozen. This campaign does not claim human adjudication where none was required.

## Frozen comparators

The first six are the exact `AuthorityBenchmarkPanel.v1` IDs; the last three satisfy the wider issue-101 comparison list. All receive the identical candidate-visible packet and no protected gold.

1. `provenanceguard-style-source-routing`
2. `attributionbench-multisource-attribution`
3. `fire-iterative-retrieve-or-verify` (frozen mapping for current DeepSciVerify-style verification)
4. `claimbench-sciclaimhunt-scientific-evidence`
5. `provenai-citation-fidelity-influence`
6. `rewardhackingagents-search-contamination`
7. `citation-presence-format`
8. `pooled-evidence-nli-support`
9. `claim-level-auditability-provenance`

## Frozen ORION ablations

All variants are candidate-visible only and resource-matched to full ORION at 9.0 units.

1. `ablation-no-exact-content-binding`
2. `ablation-no-content-provenance-distinction`
3. `ablation-no-checker-lineage-independence`
4. `ablation-no-hostile-checker-battery`
5. `ablation-no-behavioral-influence`
6. `ablation-no-evaluator-protection-telemetry`
7. `ablation-soft-confidence` — prospectively fixed at PROMOTE iff at least 6/9 gates PASS
8. `ablation-no-search-contamination-block`

## Pre-outcome harness falsification

Three non-authorizing public-seed preflights are retained. The final relevant preflight is GitHub Actions run `31967314208`, which passed full ORION, all nine comparators, all eight ablations, five deterministic repeats, protected scoring, typed `AuthorityBenchmarkPanel.v1`, and an independent reproduction implementation. Its outputs are harness tests only, never publication evidence.

On that public test seed, each ablation preserved clean coverage at 1.0 and increased false-promotion rate relative to full ORION: 0.0833 for five single gates, 0.1667 for source/provenance collapse, 0.25 for evaluator-protection removal, and 0.9167 for soft confidence. Those values were inspected **before the final hidden split existed** and therefore informed no hidden-set tuning.

## Freeze promotion checklist

1. [x] Subject revision and archive hash recorded.
2. [x] Public/protected/clean/holdout/source identities content-addressed.
3. [x] Nine comparator + eight ablation configurations frozen in one config hash.
4. [x] Complete executable harness bundle content-addressed.
5. [x] Provider mapping frozen (`deterministic/no-LLM`).
6. [x] Public/protected/holdout split hash registered.
7. [x] Evaluation epoch frozen.
8. [x] 420-case / 13-family hidden manifest generated after complete harness preflight.
9. [x] Gold kept in protected host artifact; candidate handoff proven gold-blind.
10. [x] Host run manifest created and content-addressed.
11. [x] `PROTOCOL_V1.json` populated and set to `EXECUTION_FROZEN`, `outcome_accessed=false`.
12. [x] GitHub-verified `main` freeze commit `5019b41b0da0d0763981d6d72975485517f923b3`; signature reason `valid`, verified at `2026-08-16T19:43:38Z`; exact-main CI run `31968436593`, job `95217050050`, conclusion `success`.

## Launch authorization

The freeze merge itself contains no campaign trigger. Only after item 12 was externally evidenced was the separate launch change authored. That launch change may add `host/CAMPAIGN_TRIGGER_V1.txt`; it must not change the subject, hidden set, baseline/ablation config, executable harness, split or evaluation epoch.

## Invalidating events

Any frozen harness/config change, label leak, protected evaluator write, subject/hash mismatch, pre-attestation outcome inspection, or reuse of this split after an outcome-dependent subject repair voids the campaign.
