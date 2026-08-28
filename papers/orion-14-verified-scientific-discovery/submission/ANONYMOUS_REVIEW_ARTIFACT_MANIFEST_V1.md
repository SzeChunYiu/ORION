# ORION-14 anonymous review-artifact manifest V1

Tracking: #1609 / PR #1610  
Purpose: define the material to upload with the double-blind TMLR submission without exposing repository ownership, author identity, issue/branch history, or protected per-case gold.

This is an **internal packaging map**. Do not upload this file itself if its source paths or project labels would undermine anonymity. The blind package should use the neutral output names below.

## Blind-package contents

| Internal source | Blind output name | Purpose |
|---|---|---|
| `protocol/PROTOCOL_V1.json` | `protocol.json` | prospective study definition |
| `protocol/STATISTICAL_ANALYSIS_PLAN_V1.md` | `statistical_analysis_plan.md` | registered endpoints, margins and uncertainty rules |
| `protocol/METRICS_REGISTRY_V1.json` | `metrics_registry.json` | metric definitions |
| `protocol/THREAT_MODEL_V1.md` | `threat_model.md` | frozen attack/evaluation scope |
| `protocol/EXECUTION_FREEZE_CHECKLIST_V2.md` | `execution_freeze.md` | outcome-blind execution conditions |
| `protocol/PROTECTED_RUN_BINDINGS_V2.json` | `execution_binding.json` | subject/split/harness/evaluator binding |
| `host/BASELINE_CONFIGS_V2.json` | `comparator_definitions.json` | protocol-matched comparator and ablation definitions |
| `evidence/protected_v2/PUBLICATION_METRICS_V2.json` | `v2_publication_metrics.json` | V2 headline safe aggregates |
| `evidence/protected_v2/FAMILY_CONTRAST_V2.json` | `v2_family_contrasts.json` | V2 per-family public contrasts |
| `evidence/protected_v2/RESULT_ATTESTATION_V2.md` | `v2_result_attestation.md` | V2 result/custody statement |
| `evidence/protected_v2/LIVE_ARM_STATUS.md` | `excluded_live_arm_status.md` | adverse exploratory-arm disclosure |
| `evidence/protected_v3/FREEZE.md` | `v3_freeze.md` | V3 prospective construction/evaluation freeze |
| `evidence/protected_v3/IDENTIFIABILITY_V3.json` | `v3_identifiability.json` | registered nuisance-probe outputs |
| `evidence/protected_v3/PANEL_V3.json` | `v3_panel.json` | exact-axis panel result |
| `evidence/protected_v3/RESULT.md` | `v3_result.md` | bounded V3 interpretation and retained residuals |
| `reproducibility/BINDING_MANIFEST_V2.md` | `reproduction_binding.md` | binding of public reproduction inputs |
| `host/independent_reproduce_v2.py` | `reproduce_v2.py` | separate code path for V2 aggregate reproduction |
| `figures/generate_figures.py` | `generate_figures.py` | regenerate V2 paper displays from safe aggregates |
| `CLAIM_LEDGER_V4.md` | `claim_boundary_ledger.md` | theory/V2/V3/P4-X claim boundaries |
| `research/claim_expansion/p4/P4_X_FINAL_SCIENTIFIC_TERMINAL_V1.md` | `p4x_bounded_result.md` | P4-X bounded exact result and non-authorized claims |

## Identity scrub before upload

- [ ] remove repository owner/name and author-linked URLs;
- [ ] remove issue, PR, branch, workflow-run and developer-history references unless scientifically indispensable;
- [ ] remove local paths and usernames;
- [ ] retain hashes only when they bind scientific/reproducibility objects;
- [ ] ensure filenames are neutral and match the blind names above;
- [ ] scan file metadata and archive member metadata for author identity;
- [ ] verify no protected per-case gold, raw protected traces, secret seed, credentials or candidate-hidden fields enter the package;
- [ ] run a final text search for author names, account handles, email addresses and public repository URLs;
- [ ] generate `SHA256SUMS` for the exact blind package;
- [ ] record the final archive hash in the submission manifest.

## Scientific boundary

The anonymous review artifact is sufficient to audit the **released bounded claims** only. It does not turn local code-path separation into external replication; it does not expose protected per-case gold; and it does not supply naturalistic/external-comparator evidence that the manuscript explicitly withholds.

## Filing blocker

`ANONYMOUS_REVIEW_ARCHIVE_NOT_YET_MATERIALIZED`

Close only when the exact blind archive has been generated, identity-scanned, checksum-bound and attached through the target's review channel.
