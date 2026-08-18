# P10 technical-note claim ledger

| ID | Bounded claim | Evidence/checker | Authority | Status |
|---|---|---|---|---|
| P10-C1 | The exact Mathlib sample contains 457 files, 31 top-module labels and 5,655,364 bytes at commit `e72c1e277f31441626621f7d0c7207862fc25569`. | `benchmark/MATHLIB_CORPUS_V2_MANIFEST.json`; `benchmark/check_mathlib_corpus_v2.py` | Revision-bound source identity | `SUPPORTED` |
| P10-C2 | V2 is invalid because 1,289/4,861 projected trajectories crossed an intervening top-level command. | `results/PARSER_CONTAMINATION_AUDIT_V2.json`; `results/INVALIDATION_V2.md` | Hostile parser audit | `SUPPORTED_NEGATIVE` |
| P10-C3 | Corrected V2.1 yields leave-top-module Markov-minus-unigram `0.1046`, bootstrap interval `[0.0863,0.1223]`, with 151/518 cross-module bigram/trigram patterns in every frozen null's significant lower tail. | `results/MATHLIB_TRANSFER_V2_1.json`; null distributions; deterministic generator/tests | Revision-bound source-projection evidence | `SUPPORTED` |
| P10-C4 | All eight prospectively frozen exact native Lean receipt subjects are accepted and the planted invalid proof is rejected. | `results/MATHLIB_NATIVE_RECEIPTS_V1.json` (`1aed4fbfb7e9b83eda08bfe19b4d4348dcdbffba82b1db567d05a61aaa8c5b90`); byte-identical replay; `benchmark/run_native_verification_v1.py` | Named native runtime only; no claim for the other 449 files | `SUPPORTED` |
| P10-C5 | Statement, source-revision, source-byte and attempt substitutions invalidate typed receipt binding; a task-id-only result store cannot detect revision drift. | `framework/tests/test_math_eval.py`; framework test suite | Executable hostile controls | `SUPPORTED` |
| P10-C6 | Source identity, native acceptance, statement faithfulness and scientific authority are distinct gates. | Typed `MathEvaluationEnvironment`; technical note nonclaims; P4/P8 ownership map | Structural/programme boundary | `SUPPORTED` |
| P10-C7 | No standalone P10 novelty residual remains after constructive saturation. | `SATURATION_LEDGER_2026-08-18.md`; `MERGE_DISPOSITION.md` | Dated bounded review judgment | `SUPPORTED_BOUNDED` |

## Forbidden promotions

- A digest match must not be described as proof correctness.
- A Lean exit status must not be described as statement faithfulness or
  scientific truth.
- High n-gram coverage/Markov accuracy must not be described as discovered
  tactics or downstream proof utility.
- The invalidated V2 artifact supports no empirical claim.
