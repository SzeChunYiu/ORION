# Independent re-verification records

Outputs produced by the orchestrating session when re-running another author's committed
lane analyzer from scratch, to check that the committed receipt reproduces. These are
*evidence about the verification*, not lane deliverables: they grant no authority of their
own and never supersede the lane receipt they check.

- `QG9_V6_ORCHESTRATOR_REVERIFICATION.json` — re-run of
  `research/extensions/orion-qg/qg9_v6_support1_normalization.py` on the merged tree
  before PR #830 was merged. Reproduces `result_digest`
  `587b4b803cfafa1b08a949b28ba8a626bd7bc405ca03a30ccd09e99651d31a4f`, matching
  `QG9_V6_PROTECTED_RUN_RECEIPT_2026-08-21.json` byte-for-byte in that field, with
  `intrinsic_support_number = 1` and `all_gates = true`.

Other lanes' re-verifications in this session were confirmed by digest comparison at the
terminal and recorded in the merge commit messages and `QG_WAVE2_RECORD.md` rather than by
retaining their output files.
