# P1/P2 final rendered-byte closure lane — 2026-08-21

This is a read-only publication-evidence lane for issues #489 and #490.

## Why it exists

Current `main` contains manuscript/result writebacks newer than the historical saturation render receipts. In particular:

- P1's durable `research/saturation/p1/FINAL_SATURATION_AUDIT.md` still describes the older 27-page render and therefore cannot certify the current P1 manuscript bytes.
- P2's `research/saturation/p2/` directory does not contain the durable `FINAL_SATURATION_AUDIT.md` required by #490.

Neither condition is a scientific-result failure. They are rendered-byte/publication-integrity gaps.

## Frozen boundary

This lane does not edit manuscripts, results, protocols, thresholds, claim ledgers, comparators, or scientific terminals. It only regenerates the current P1/P2 PDFs from the exact PR head and records evidence needed for independent page inspection and subsequent bounded package rebinding.

## Exact-head checks

For each paper the workflow must:

1. compile the current manuscript with `latexmk`;
2. reject undefined citations/references and overfull boxes;
3. assert the already-supported bounded headline/boundary text remains present;
4. record `pdfinfo`, SHA-256, and exact subject commit;
5. render every PDF page to PNG for independent page-by-page inspection;
6. archive the PDF, log, metadata, digest and rendered pages;
7. run the repository journal-package checker without rewriting package bytes.

## Authority

A green workflow is necessary but not sufficient to close #489/#490. Closure additionally requires independent page inspection, durable audit writeback, rebinding of the inspected PDF/package bytes, and ordinary exact-head repository/package CI after that writeback.

No P1-U or P2-U superiority authority is granted by this publication lane; #649/#650 remain separate research programmes.
