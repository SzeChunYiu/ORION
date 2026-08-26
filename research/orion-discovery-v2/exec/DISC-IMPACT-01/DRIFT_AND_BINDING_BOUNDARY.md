# Drift and binding boundary — DISC-IMPACT-01

## What a drift verdict means here

A binding names a file and a sha256. It is checked by hashing the file it names and comparing. Git ordering is **not** a verdict: a file can be committed after its binder and still hash-match. Ordering is recorded separately as `temporal_suspicion`.

## Checked

- bindings hashed and compared: **1450**
  - authority `{artifact, sha256}` bindings: 120
  - `SHA256SUMS` lines: 1330
- drifted (hash mismatch): **56**
- temporal suspicion only (artifact committed after its binder, hash still matches): **103**

  Those 103 are the argument for the method. Had commit ordering been used as the verdict, this audit would have emitted ~103 findings, of which 70 would be false: the artifact was committed after its binder and still hashes to the recorded value. Ordering suggests where to look; only the hash decides.
- web node identities recomputed: 90 (mismatch: 0)

## Could not check — this is not the same as clean

- bindings unresolvable or non-hex: **17**
- sha256-valued keys in authority files with no sibling path key: **11** — the file states a hash but never states which artifact it binds, so there is nothing to hash.
- nodes not bound to a file: 1 (synthetic constants, not files)

| binder | named artifact | reason |
|---|---|---|
| `papers/candidates/paper-06-formal-epistemic-structures-and-mechanics/SHA256SUMS` | `papers/candidates/paper-06-formal-epistemic-structures-and-mechanics/CLAIM_LEDGER_ADDENDUM_V2.md` | named artifact could not be resolved to a file (ambiguous_within_binder_subtree(2_hits)) |
| `papers/candidates/paper-06-formal-epistemic-structures-and-mechanics/SHA256SUMS` | `papers/candidates/paper-06-formal-epistemic-structures-and-mechanics/CLAIM_LEDGER_V3.md` | named artifact could not be resolved to a file (ambiguous_within_binder_subtree(2_hits)) |
| `papers/candidates/paper-06-formal-epistemic-structures-and-mechanics/SHA256SUMS` | `papers/candidates/paper-06-formal-epistemic-structures-and-mechanics/manuscript/FINAL_V3.md` | named artifact could not be resolved to a file (ambiguous_within_binder_subtree(2_hits)) |
| `papers/candidates/paper-06-formal-epistemic-structures-and-mechanics/SHA256SUMS` | `papers/candidates/paper-06-formal-epistemic-structures-and-mechanics/submission/P6_X2_CERTIFICATE_LIFTING_SECTION.tex` | named artifact could not be resolved to a file (unresolved_named_artifact_absent_from_named_location) |
| `papers/candidates/paper-06-formal-epistemic-structures-and-mechanics/SHA256SUMS` | `papers/candidates/paper-06-formal-epistemic-structures-and-mechanics/submission/P6_X_SUCCESSOR_SECTION.tex` | named artifact could not be resolved to a file (unresolved_named_artifact_absent_from_named_location) |
| `papers/candidates/paper-07-epistemic-navigation-open-worlds/SHA256SUMS` | `papers/candidates/paper-07-epistemic-navigation-open-worlds/submission/P7_X2_CLOSURE_CARRYING_SECTION.tex` | named artifact could not be resolved to a file (unresolved_named_artifact_absent_from_named_location) |
| `papers/candidates/paper-08-epistemic-authority-autonomous-science/SHA256SUMS` | `papers/candidates/paper-08-epistemic-authority-autonomous-science/submission/P8_X4_AUTHORITY_COMPOSITION_SECTION.tex` | named artifact could not be resolved to a file (unresolved_named_artifact_absent_from_named_location) |
| `papers/candidates/paper-08-epistemic-authority-autonomous-science/SHA256SUMS` | `papers/candidates/paper-08-epistemic-authority-autonomous-science/submission/P8_X4_DONOR_REFERENCES.md` | named artifact could not be resolved to a file (unresolved_named_artifact_absent_from_named_location) |
| `papers/orion-13-global-knowledge-portrait/evidence/public-reference-v1/SHA256SUMS` | `artifacts/PROVENANCE.env` | named artifact could not be resolved to a file (ambiguous_within_binder_subtree(2_hits)) |
| `papers/orion-13-global-knowledge-portrait/evidence/public-reference-v1/SHA256SUMS` | `artifacts/build/cases.jsonl` | named artifact could not be resolved to a file (unresolved_named_artifact_absent_from_named_location) |
| `papers/orion-13-global-knowledge-portrait/evidence/public-reference-v1/SHA256SUMS` | `artifacts/evaluation/summary.json` | named artifact could not be resolved to a file (ambiguous_within_binder_subtree(2_hits)) |
| `papers/orion-13-global-knowledge-portrait/evidence/public-reference-v1/SHA256SUMS` | `artifacts/frozen/PUBLIC_REFERENCE_FREEZE_MANIFEST_V1.json` | named artifact could not be resolved to a file (ambiguous_within_binder_subtree(2_hits)) |
| `papers/orion-13-global-knowledge-portrait/evidence/public-reference-v1/SHA256SUMS` | `artifacts/frozen/PUBLIC_REFERENCE_GOLD_V1.jsonl` | named artifact could not be resolved to a file (ambiguous_within_binder_subtree(2_hits)) |
| `papers/orion-13-global-knowledge-portrait/evidence/public-reference-v1.1-confirmatory/SHA256SUMS` | `artifacts/evaluation/PROVENANCE.env` | named artifact could not be resolved to a file (ambiguous_within_binder_subtree(2_hits)) |
| `papers/orion-13-global-knowledge-portrait/evidence/public-reference-v1.1-confirmatory/SHA256SUMS` | `artifacts/evaluation/SUMMARY.json` | named artifact could not be resolved to a file (ambiguous_within_binder_subtree(2_hits)) |
| `papers/orion-13-global-knowledge-portrait/evidence/public-reference-v1.1-confirmatory/SHA256SUMS` | `artifacts/frozen/PUBLIC_REFERENCE_FREEZE_MANIFEST_V1.json` | named artifact could not be resolved to a file (ambiguous_within_binder_subtree(2_hits)) |
| `papers/orion-13-global-knowledge-portrait/evidence/public-reference-v1.1-confirmatory/SHA256SUMS` | `artifacts/frozen/PUBLIC_REFERENCE_GOLD_V1.jsonl` | named artifact could not be resolved to a file (ambiguous_within_binder_subtree(2_hits)) |

### Unpaired sha256 keys

| binder | key |
|---|---|
| `papers/orion-22-adaptive-state-reasoning/P12_ACTIVE_CLAIM_AUTHORITY_V1.json` | `adjudication_sha256` |
| `papers/orion-22-adaptive-state-reasoning/P12_ACTIVE_CLAIM_AUTHORITY_V3.json` | `active_claim_leaf.scope.locked_environment.uv_lock_sha256` |
| `papers/orion-22-adaptive-state-reasoning/P12_ACTIVE_CLAIM_AUTHORITY_V4.json` | `active_claim_leaf.scope.locked_environment.uv_lock_sha256` |
| `papers/orion-22-adaptive-state-reasoning/P12_ACTIVE_CLAIM_AUTHORITY_V5.json` | `active_claim_leaf.scope.locked_environment.uv_lock_sha256` |
| `papers/orion-23-responsibility-carrying-state/P13_ACTIVE_CLAIM_AUTHORITY_V1.json` | `adjudication_sha256` |
| `papers/orion-23-responsibility-carrying-state/P13_ACTIVE_CLAIM_AUTHORITY_V3.json` | `active_claim_leaves.[].result.byte_identical_replay_core_sha256` |
| `papers/orion-24-orion-rse/P14_ACTIVE_CLAIM_AUTHORITY_V1.json` | `active_claim.result_sha256` |
| `papers/orion-24-orion-rse/P14_ACTIVE_CLAIM_AUTHORITY_V1.json` | `active_claim.replay_sha256` |
| `papers/orion-24-orion-rse/P14_ACTIVE_CLAIM_AUTHORITY_V1.json` | `prospective_external_validation.protocol_sha256` |
| `papers/orion-24-orion-rse/P14_ACTIVE_CLAIM_AUTHORITY_V1.json` | `prospective_external_validation.preflight_sha256` |
| `papers/orion-24-orion-rse/P14_ACTIVE_CLAIM_AUTHORITY_V1.json` | `prospective_external_validation.validator_sha256` |

## Deliberate, counted exclusions

- `development/**/SHA256SUMS*`: **137** digest files excluded. `development/` is not one of the artifact classes the job names. The count is stated so the exclusion is auditable rather than an unjustified absence claim.
- `CONTENT_MANIFEST_V1.json` `bound_files` entries carry no `sha256`; identity is delegated to `digest_file`. The manifests are therefore audited *through* their digest files, and the delegation is recorded per manifest in the receipt.

- `_polarity/DRIFTED_*` is a deliberately mutated copy of a real claim ledger, kept as evidence of the positive control. Nothing in the repository binds it. It must not be picked up by a future digest regeneration; it is not a paper artifact.

## Detector validation

- negative control (unmutated copy): expected CLEAN, observed **CLEAN**
- positive control (same file, 47 bytes appended): expected DRIFT, observed **DRIFT**
- discriminates: **True**

Both controls run through `check_binding`, the same function that produced every verdict in this audit — not a re-implementation.

## Authority boundary

This job registers obligations and reports drift. It updates no claim, edits no file outside its own exec directory, and makes no commit. Every obligation whose target is a theorem is marked `authority-gated` in the matrix.

