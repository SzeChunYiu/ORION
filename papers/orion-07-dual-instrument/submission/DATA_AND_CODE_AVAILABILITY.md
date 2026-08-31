# Data, code, and reproducibility — ORION-07

## Data availability

Each scored instance is a self-contained directory under
`papers/orion-07-dual-instrument/instances/` holding the frozen question, the
shared evidence packet, both lane receipts, the pre-outcome agreement record,
the deferred-outcome binding, the final score, and an independent replay
receipt. Digests are SHA-256 over file bytes at the submitted revision.

| Artifact | Supports | SHA-256 |
|---|---|---|
| `instances/Q3-R1-QG19/FINAL_SCORE.json` | Outside-cone sharpness instance: both lanes aligned with each other and with the deferred outcome | `7529c0f46c43cf166ade9eb33cf7cb5e6c8043edf52d8b7ec142d321b0e94644` |
| `instances/Q3-R2-QG20/FINAL_SCORE.json` | Boundary-invariance instance: both lanes aligned with each other, both scored not aligned on responsibility against the deferred outcome | `475a6b0f0843cb5a89c2095be4e51969b74d12a02c3211c0252aa4b2a0902604` |
| `CLAIM_LEDGER_PROSPECTIVE_CASE_SERIES_2026-08-23.md` | Ratified series ledger: three valid units, forbidden interpretations | `36cf899d5aa67c8fe371a14d22195c02dd1ee885c0e9ad7bf0ff1f206f1f88a8` |
| `Q3_REPLACEMENT_PROSPECTIVE_PROTOCOL_V2.md` | Prospectively frozen replacement protocol and content-readiness condition | `5c47a0c29cbd0cd8e441e45d3cbeb668024bbb6972431384e94a4485b63fa70b` |
| `Q3_CONTAMINATION_DISPOSITION_2026-08-22.md` | Disposition of the two withdrawn candidate slots | `2c5e268a601c03a38a99c2af4006018d14c79e05dc126068b19bb677b599342c` |

The V0 instance and the deferred-outcome bindings for all three units are
committed in the same tree.

## Code availability

Three checkers in `papers/orion-07-dual-instrument/` are the operative
verification path and are runnable without arguments:

- `check_q3_completion.py` — validates that every required instance file
  exists, that both lanes recorded no access to the scientific outcome before
  freezing, that the analyzer post-dates the pre-outcome anchor in version
  history, that each instance is scored, that no instance authorizes an
  aggregate reliability claim, that each independent replay is byte-identical,
  and that the contaminated slots remain visible.
- `check_q3_result_bindings.py` — confirms the scientific result digests.
- `replay_q3_v0.py`, `score_q3_replacements.py` — replay and scoring entry
  points.

## Reproducibility statement

1. Run `check_q3_completion.py`. It should print `Q3_COMPLETION_CHECK=PASS`,
   `VALID_PROSPECTIVE_SERIES=V0,Q3-R1,Q3-R2`,
   `CONTAMINATED_RETIRED_SLOTS=Q3-V1/QG-7d,Q3-V2/QG-15c`, and
   `AGGREGATE_RELIABILITY_AUTHORITY=FALSE`.
2. Run `check_q3_result_bindings.py` and confirm the two result digests.
3. Re-derive each instance's score from its lane receipts and its
   deferred-outcome binding.

A reproduction that recovers only the two aligned instances has not reproduced
this paper. The third instance, in which both instruments agreed and both were
wrong, is the result the benchmark exists to expose.

## Scope of the digests

The digests bind evidence and chronology. They establish that each decision was
recorded before its outcome was available and has not moved since. They do not
establish that either instrument is reliable, and the series is far too small
to support any such estimate.
