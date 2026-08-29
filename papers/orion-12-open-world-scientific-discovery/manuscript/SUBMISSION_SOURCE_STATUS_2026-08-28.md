# ORION-12 current submission-source status — 2026-08-28

Tracking issue: #1609

This file is publication metadata for the current manuscript tree. The canonical manuscript entry point remains `main.tex`; this file is not included in the paper text.

## Scientific scope to preserve

The submission claim is the narrowed methods / critical system-design result:

- fail-closed route/read/stopping authority semantics and controlled mechanism behavior are supported in the frozen controlled setting;
- external Wide/Deep ORION-vs-baseline superiority is **not** supported by the present evidence and is not part of the submission claim;
- the TREC-COVID registered recall/cost superiority gate failed and remains visible;
- the favorable nDCG@10 result is secondary and must not be used to rescue the failed registered gate;
- future valid multi-provider superiority studies are successor science, not a hidden prerequisite of this narrowed manuscript.

## Historical package problem — resolved additively

`journal_package/MANIFEST.json` correctly marks the retained PDF as
historical/superseded. It remains unchanged as provenance. The new current
authority is `journal_package/current_revision/SUBMISSION_MANIFEST.json`, which
binds the target-adapted PDF, anonymous source and review archive.

## Closeout blockers

- [x] two clean target builds are byte-identical under the recorded source epoch;
- [x] the exact source/input closure is retained for the current PDF;
- [x] every page, figure, table, reference and final-page spill is visually audited;
- [x] the current-revision package is additive; historical PDF/manifest bytes are not relabelled;
- [x] the current CAS single-column adapter, title-page structure and companions are checked without inventing human metadata;
- [x] a 2026-08-28 literature refresh is recorded; the broad search is not a saturation certificate;
- [x] exact final review PDF, anonymous source and review-archive bytes are bound.

The current claim authority is the 105-row
`editorial/ATOMIC_CLAIM_LEDGER_2026-08-28.csv`, checked by
`scripts/check_current_atomic_claim_ledger.py`. The older
`protocol/CLAIM_LEDGER_V1.json` remains historical provenance for the discarded
long-form manuscript and is not a sentence ledger for this revision.

## Close criterion

`simulated_publication_ready_for_target`

Only human filing metadata, author approvals, upload and submission-ID capture
remain. Any byte change reopens the affected render and claim checks.
