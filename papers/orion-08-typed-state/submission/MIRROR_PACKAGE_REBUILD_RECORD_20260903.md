# Mirror package rebuild record — ORION-08 (2026-09-03)

Provenance note for the TMLR/arXiv publication package in the paper mirror
(`v1-papers/orion-08-typed-state/SUBMIT_THIS/`). This record changes no claim;
`CLAIM_LEDGER` authority is unchanged.

## What was rebuilt and why

The mirror package (built 2026-09-02 10:39Z) predated the canonical science
merge #2130 (2026-09-02 15:33Z), so the upload-facing PDFs did not carry the
current manuscript state. On 2026-09-03 the package was rebuilt from the
post-#2130 canonical source with a three-way merge: canonical science content,
the package's scholarly register, and regenerated bindings.

- Journal route: 10-page anonymous TMLR build.
- arXiv route: 12-page named build (page count updated from 11 to 12 in the
  arXiv metadata comments field).
- All four archives rebuilt deterministically (fixed 1980-01-01 mtimes,
  `zip -X`), manifests regenerated, SHA256SUMS recomputed.
- Digest self-check on the manifest payload passed 30/30; live fetch-back of
  SHA256SUMS and the journal PDF matched the staged bytes.
- Mirror commit: `fa066b127573cd31e69ca43e08ddb359fa92e849`.

## Deliberate scope boundaries

- #2158 (`experiments/split-ratio-invariance-v1/`) is a registered but
  unexecuted protocol; registrations of untested predictions are not results
  and are not added to the manuscript or package.
- #2185 filing-surface edits (`submission/FILING_SURFACE.md`,
  superseded pandoc lane) are repository-side records, not package members.
- The stale-PDF clipping-audit binding is cleared through PR #2210
  (regenerated digest on the new head).
- Portal filing remains HUMAN_INPUTS_REQUIRED; no automated filing.
