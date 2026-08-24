# P2 coherent single-snapshot provider qualification V15

## Question and chronology

V15 tests the minimal V14 repair: preserve commit `38b35218...` and replace only the incompatible inherited index hash with the bytes actually owned by that commit. V14's mismatch and exact terminal remain immutable.

V15 prospectively froze seven provider-metadata requests and a fail-closed custody boundary. After the provider gate, an implementation audit found that the V15 protocol had transcribed V14's candidate URL template incorrectly. `IMPLEMENTATION_CORRECTION_V15B.json` preserves this error and the exact V14 template; no candidate URL was executed, and no index or dataset body was read.

## Genuine positive source result

GitHub's official commit endpoint authenticates commit `38b35218...` and root tree `49f437c...`; its verification is **valid**. The exact provider tag `metadata-v1-final` points to the same commit. The non-truncated recursive tree has **169 entries / 140 blobs** and contains exactly one `index_v1.json` entry at blob `f4f5007...`, **22,135 bytes**, matching V14's coherent SHA-256 lineage. The same tree exposes **61 exact dataset CSV blobs**; their complete path/blob/size manifest has SHA-256 `fe93857d5566fd63c9f681939fc1bfd347d6ae9496a1a01f6edd09428ce3c30a`.

This is a real provider-authenticated state-expansion witness: the repaired source tuple is coherent and a finite same-snapshot dataset population exists. It does not establish seven eligible keyword-capable reviews or screening benefit.

## Rights and custody result

The historical snapshot's exact `LICENSE` blob is classified MIT (1,064 bytes; SHA-256 `f1e934ccb74b86e49caa93146e16d342c86885d06a4b8d087679c3ac5689bbad`). Current repository metadata reports CC0, but that current-state field is not bound to the historical commit. Neither generic root license evidence nor a valid commit signature supplies the required per-review CC-BY-4.0/CC0 adjudication.

The exact index attestation endpoint returns **404**. No provider predicate binds the V15 tuple, complete 61-blob manifest, exact rights, no-route-switch rule and outcome-blind independence. Independent source custody therefore remains **0/1**, so V15 stopped before index parsing, review CSV requests, census and performance.

## Widest defensible claim

The V14 repair target is provider-authenticated and content coherent: a validly signed commit and matching provider tag bind one tree containing the exact index entry and 61 dataset blobs. This supports source-state availability only. It does not authorize an eligible seven-review population, labels, class counts, models, rankings, metrics, performance or superiority.

## Exact terminal

`P2_V15_SIGNED_COHERENT_SINGLE_SNAPSHOT_PASS__INDEX_F4F5007_AND_61_DATASET_BLOBS_BOUND__V15_TEMPLATE_TRANSCRIPTION_FAIL_CLOSED_AND_V14_TEMPLATE_RESTORED_FOR_SUCCESSOR_ONLY__EXACT_ROOT_LICENSE_MIT_CURRENT_METADATA_CC0_NOT_BLENDED__ATTESTATION_404__INDEPENDENT_CUSTODY_NOT_CLOSED__STOP_BEFORE_INDEX_PARSE_CENSUS_PERFORMANCE`
