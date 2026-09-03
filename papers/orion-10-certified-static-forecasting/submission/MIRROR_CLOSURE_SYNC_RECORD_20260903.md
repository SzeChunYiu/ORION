# Mirror closure-sync record — ORION-09+10 (2026-09-03)

Provenance note for the combined filing package in the paper mirror
(`v1-papers/orion-09-10-combined-certified-static-forecasting/SUBMIT_THIS/`).
This record changes no claim; `CLAIM_LEDGER_V4.md` authority is unchanged.

## What was synchronized and why

The mirror package carried the 2026-09-02 morning scholarly refinement
(academic-paper-pipeline 1.23.0) but predated the canonical Tier-B closure
(`7126a718d`, 2026-09-02 15:13Z: exact-count fix, full induction write-out,
S-M3 paragraph, abstract evidence-status correction). On 2026-09-03 the
closure artifacts were imported into the mirror package:

- Both manuscript PDFs, both source archives, the supplement, the verifier
  artifact and both route metadata files imported byte-exact from
  `submission/tier-b-final-20260901/`; the canonical package SHA256SUMS
  verified 31/31 before import.
- Register wording aligned with the closure ("predeclared fresh instance" ->
  "frozen fresh instance"); the 1.23.0 scholarly register is preserved.
- Supplement is now 11 pages (was 10; the additional page carries the
  induction write-out). Manifest page fields (journal 9 / arXiv 11) remain
  correct.
- `CLOSURE_UPDATE_20260902.md` added to the package tree as provenance,
  deliberately outside the SHA256SUMS/PACKAGE_MANIFEST payload, matching the
  canonical binding-contract shape.
- Mirror commit: `43ba4a47715010c37d7ccd2eac3c40bfc73aff43`. An earlier
  push attempt (`d0867db54`) set an incorrect repository root tree and was
  reverted the same session (main restored to `fa066b127`, then re-pushed
  correctly); the final state was verified against the full recursive tree
  (8,847 paths, sibling paper folders intact).

## Still open

Submission-day literature refresh and portal filing (Quantum; arXiv in filing
order) remain HUMAN_FILING_ONLY per `CLOSURE_UPDATE_20260902.md` section 6.
