# ORION-P11 reproduction guide

This guide reproduces the evidence used by the bounded peer-review manuscript. It does not execute the prospective multi-revision V3 campaign.

## 1. Repository-only readiness

From the ORION repository root:

```bash
python3 papers/candidates/paper-10-content-bound-math-evaluation/check_technical_note_ready.py
python3 papers/candidates/paper-10-content-bound-math-evaluation/check_p11_peer_review_ready.py
```

The first command checks the historical evidence package. The second checks the submission package and required claim-boundary language.

## 2. Result-bearing source artifacts

The manuscript's numerical claims come from immutable committed artifacts:

- corpus identity: `benchmark/MATHLIB_CORPUS_V2_MANIFEST.json`;
- invalidated V2 result: `results/MATHLIB_TRANSFER_V2.json`;
- contamination audit: `results/PARSER_CONTAMINATION_AUDIT_V2.json`;
- invalidation record: `results/INVALIDATION_V2.md`;
- corrected V2.1 result: `results/MATHLIB_TRANSFER_V2_1.json`;
- corrected null distributions: `results/MATHLIB_TRANSFER_V2_1_NULL_DISTRIBUTIONS.json`;
- native receipts: `results/MATHLIB_NATIVE_RECEIPTS_V1.json`.

The paper intentionally retains V2 and V2.1 as separate protocol/result generations.

## 3. Historical source-analysis replay

Use the exact commands and scripts already bound by the historical `TECHNICAL_NOTE.md`, `JOURNAL_READINESS.md`, and benchmark directory. The peer-review package does not silently replace those commands with a new analysis.

The readiness checker must continue to report the exact corrected result hashes recorded in the historical package.

## 4. Native Lean replay

Native replay requires the exact upstream Mathlib checkout and the recorded Lean toolchain. The committed command is:

```bash
python3 papers/candidates/paper-10-content-bound-math-evaluation/benchmark/run_native_verification_v1.py \
  --mathlib-checkout /path/to/mathlib4 \
  --lake /path/to/lean-4.34.0-rc1/bin/lake \
  --runtime-adapter /path/to/orion_p10_readlink_self.so
```

Recorded runtime:

- Lean `4.34.0-rc1`;
- release commit `3447a668783dbce1a8fdb97101dd067687b2b418`;
- native receipt SHA-256 `1aed4fbfb7e9b83eda08bfe19b4d4348dcdbffba82b1db567d05a61aaa8c5b90`.

The runtime adapter is sandbox compatibility only. Its source and binary digests remain recorded in the historical readiness file.

## 5. What a successful replay means

A successful native replay means the named exact files are accepted by the named Lean environment and the receipt bytes match the expected identity. It does not establish statement faithfulness, informal mathematical intent, or scientific authority.

## 6. Missing inputs

The historical `HF_MATHLIB_TACTICS_SAMPLE.json` input is unavailable. It is not reconstructed, guessed, or replaced. The abandoned Phase-2B question is not part of the peer-review manuscript.

## 7. Prospective work

`P11_REOPEN_PROTOCOL_V3.md` and `benchmark/CONTENT_BOUND_PROOF_TASK_V3_SCHEMA.json` define future multi-revision/native-mechanism experiments. They are cited as future work only and are not required to reproduce the current manuscript's claims.
