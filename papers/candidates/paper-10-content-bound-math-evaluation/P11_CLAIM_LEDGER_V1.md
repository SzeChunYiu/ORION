# ORION-P11 claim ledger V1 — peer-review package

**Paper:** *Bytes, Builds, and Meaning: Content-Bound Evaluation for Evolving Lean Repositories*  
**Historical evidence directory:** `papers/candidates/paper-10-content-bound-math-evaluation/`  
**Disposition:** bounded evaluation-methods / experience paper. Historical P10 numbering is preserved in source paths; programme identity is P11 by #471.

| ID | Manuscript claim | Exact evidence | Status | Forbidden promotion |
|---|---|---|---|---|
| P11-C1 | The frozen source sample contains 457 files, 31 top-module labels and 5,655,364 bytes at Mathlib commit `e72c1e277f31441626621f7d0c7207862fc25569`. | `benchmark/MATHLIB_CORPUS_V2_MANIFEST.json`; `benchmark/check_mathlib_corpus_v2.py` | `SUPPORTED` | No claim that this is all of Mathlib or representative of all Lean repositories. |
| P11-C2 | V2 is scientifically invalid because 1,289/4,861 projected trajectories crossed intervening top-level commands (26.52%; 3,903 leaked boundaries). | `results/PARSER_CONTAMINATION_AUDIT_V2.json`; `results/INVALIDATION_V2.md` | `SUPPORTED_NEGATIVE` | V2 numerical outputs support no positive recurrence/transfer claim. |
| P11-C3 | V2.1 prospectively repairs the registered contamination class and leaves no recognized top-level command inside a projected proof body on the frozen corpus. | V2.1 projector/tests; `results/MATHLIB_TRANSFER_V2_1.json` | `SUPPORTED` | No claim that the projector is a Lean parser or native trace. |
| P11-C4 | Corrected leave-top-module Markov-minus-unigram is `0.1046`, module-bootstrap 95% interval `[0.0862935,0.1223224]`; 151 bigrams and 518 trigrams fall in the significant lower tail of every frozen null seed/family. | `results/MATHLIB_TRANSFER_V2_1.json`; `results/MATHLIB_TRANSFER_V2_1_NULL_DISTRIBUTIONS.json` | `SUPPORTED` | No reusable-tactic, semantic-mechanism or proof-utility claim. |
| P11-C5 | All eight prospectively selected native Lean subjects are accepted; the planted invalid proof is rejected; two complete replays produce byte-identical receipt archives. | `results/MATHLIB_NATIVE_RECEIPTS_V1.json`; native runner; receipt SHA-256 `1aed4fbfb7e9b83eda08bfe19b4d4348dcdbffba82b1db567d05a61aaa8c5b90` | `SUPPORTED` | Applies only to the eight exact subjects and named Lean runtime, not the other 449 files. |
| P11-C6 | Statement, source-revision, source-byte and candidate-attempt substitutions invalidate content-bound matching; a task-id-only store can reuse stale `SUCCESS` after revision drift. | `framework/tests/test_math_eval.py`; typed evaluation environment | `SUPPORTED` | No claim that cryptographic hashing alone guarantees correctness or meaning. |
| P11-C7 | Artifact identity, extraction validity, native acceptance, statement faithfulness and scientific authority are distinct evidence coordinates. | C2–C6 plus typed environment and programme authority boundary | `SUPPORTED_STRUCTURAL` | Native compilation does not establish statement meaning or scientific truth. |
| P11-C8 | The empirical case demonstrates that a fully machine-checkable upstream corpus can still yield an invalid downstream scientific measurement when the extracted unit of analysis is wrong. | C2 plus exact upstream source identity | `SUPPORTED` | This is an evaluation-method finding, not evidence that Lean itself accepted an invalid proof. |
| P11-C9 | Current nearest work already owns native proof-state tracing, repository/version packaging, tactic mining, and statement-faithfulness evaluation; P11 does not claim these components individually. | `SATURATION_LEDGER_2026-08-18.md`; updated manuscript related-work section | `SUPPORTED_BOUNDED` | Do not claim content hashes, pinned versions, native checking, proof-state traces, or tactic mining as ORION inventions. |
| P11-C10 | The package is peer-review-ready as a bounded methods/experience paper whose result-bearing claims are C1–C9; prospective multi-revision/native-mechanism experiments remain future work. | submission manuscript; this ledger; `P11_REPRODUCE.md`; `P11_JOURNAL_READINESS.md` | `PACKAGE_CLAIM` | Peer-review-ready does not mean accepted, independently reproduced, or empirically supported at V3 claim rungs 2–6. |

## Abstract/conclusion authority

The abstract may state C1–C8. The conclusion may state C7–C8 and the bounded methodological implication. Neither may state that P11 discovers reusable tactics, establishes theorem faithfulness, proves Mathlib-wide native validity, or demonstrates cross-revision mechanism transfer.

## Historical preservation

The historical files `TECHNICAL_NOTE.md`, `CLAIM_LEDGER.md`, `JOURNAL_READINESS.md`, V2/V2.1 results, and invalidation artifacts are not superseded or rewritten by this package. P11 publication identity is an additive projection over those immutable artifacts.
