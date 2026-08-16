# Phase-2 terminal receipts V1

This document defines the retained artifacts required after the live research, consequential Shadow-development, and hostile authority gates. These receipts are process evidence only. They do not grant Phase-2 closure, self-merge, or Governed Self-ORION authority.

## Gate E — frozen failure replay

Before repair/replay outcomes are inspected, the host/external evaluator writes `FrozenFailureIndex.v1`. It is content-addressed and binds the exact Phase-2 subject/epoch plus every important A–C failure by:

- durable failure identity;
- failure class;
- source failure artifact SHA-256.

`FailureReplayReceipt.v1` must cover that frozen set exactly. Each failure must take exactly one path:

1. `REPAIRED_REPLAYED_FRESH_TRANSFER`: retained negative history + discriminator + recurrence probe + replay artifact + fresh-transfer artifact; or
2. `RETAINED_BLOCKING_FIBRE`: retained negative history + discriminator + recurrence probe + blocking-fibre artifact + explicit reopen condition.

`UNNOTICED_RECURRENCE` is structurally invalid. Producer and verifier process lineages must differ. The persisted campaign audit also checks that failure IDs/classes/source-artifact hashes agree exactly with the frozen index.

## Gate F — exact final integration

The external integration handoff retains four independent artifact families.

### Final repository subject

`RepositorySubjectAttestation.v1` binds the exact integration commit, Git tree and SHA-256 content identity of every tracked object. The terminal receipt's integration commit/tree must reproduce from this attestation.

### Exact CI evidence

`FinalCIEvidence.v1` binds:

- CI run identity;
- exact head commit;
- workflow identity;
- exact test command;
- executed job count;
- SUCCESS / FAILURE / CANCELLED;
- producer/verifier process lineage.

A terminal-ready campaign requires independent lineage and `SUCCESS`. The CI head must equal the integration commit.

### Complete paper-programme snapshot

`Phase2PaperProgrammeSnapshot.v1` freezes six repository prefixes: the complete `research/paper-programme-v1/` tree and each of the five canonical `papers/paper-*` trees. The snapshot is generated from `RepositorySubjectAttestation.v1` and must contain **every tracked file** under those prefixes at the exact integration commit. The terminal audit independently derives the expected entry set from the final subject and requires exact equality, so newly added protocol/manuscript assets are automatically included and a caller cannot satisfy Gate F with a cherry-picked paper or ledger subset.

### External evidence manifest

The exact protected `ExternalEvidenceManifest.v1` file is content-bound into the final integration receipt. The normal manifest loader still checks its typed subject/evaluator/epoch/record semantics.

`FinalIntegrationReceipt.v1` binds all four families plus the Gate-E replay receipt. It is independently verified and may be `PASS`, `FAIL`, or `CANNOT_CHECK`; only `PASS` can advance terminal audit.

## Restart-safe audit

The full audit remains offline with respect to providers/evaluators:

```bash
python -m orion.benchmarks phase2-campaign-status \
  --binding /protected/phase2-binding.json \
  --live-trial /protected/orion-shadow-live-trial.json \
  --baseline-bundle /protected/simple-baseline.json \
  --development-trial /protected/shadow-development-trial.json \
  --authority-trial /protected/authority-trial.json \
  --authority-benchmark /protected/authority-benchmark.json \
  --failure-index /protected/frozen-failure-index.json \
  --failure-replay /protected/failure-replay.json \
  --final-subject-attestation /protected/final-subject.json \
  --ci-evidence /protected/final-ci.json \
  --papers-claim-ledger /protected/paper-programme-snapshot.json \
  --final-integration /protected/final-integration.json \
  --external-observations /protected/phase2-observations.json \
  --external-manifest /protected/external-evidence.json
```

The non-skippable terminal progression is:

`earlier A–C gates -> COMPLETE_FAILURE_REPLAY -> VERIFY_FINAL_INTEGRATION -> HAND_BACK_EXTERNAL_EVIDENCE -> READY_FOR_TERMINAL_AUDIT`

The final two external observations must cite the exact `FailureReplayReceipt.v1` and `FinalIntegrationReceipt.v1` artifact hashes. `READY_FOR_TERMINAL_AUDIT` remains a host/external review state and does not self-issue `PHASE_2_SHADOW_SELF_ORION_CLOSED`.
