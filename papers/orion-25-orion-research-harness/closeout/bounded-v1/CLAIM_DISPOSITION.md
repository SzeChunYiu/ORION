# ORION-25 bounded closeout disposition

## Current disposition

`CANNOT_CHECK`

The bounded scientific source is complete and its load-bearing numbers are
machine-bound to the frozen result records. The overall paper is not yet marked
`BOUNDED_PAPER_READY_TO_FILE`, because the recovered source has not been freshly
rendered into the exact final PDF, visually audited page by page, archive-bound,
and filed.

## What is earned

- All six registered committed-artifact corruptions were detected with no false
  promotion.
- All six registered semantics-preserving re-encodings were accepted with no
  false rejection; four changed serialized bytes.
- Detection was flat for chain lengths 1, 2, and 3 at one trust domain.
- Under one-domain compromise at fixed chain length 3, false promotion was 4/4
  for one domain and 0/4 for two or three cryptographic domains.
- Two stale valid artifacts remained acceptable after current-run termination,
  preserving the distinction between artifact validity and run liveness.
- Composition-side overhead and byte expansion are reported only at their
  measured four-case, 40-repeat scope.
- The 1,000-cell law sweep is retained as a cryptographic-independence result,
  not an organizational-custody result.

## What is not earned

This packet does not establish production-scale reliability, secure custody,
organizational independence, multiple-domain compromise resistance, production
Sigstore/TUF/in-toto superiority, or scientific warrant from signatures.

## Filing gate

A later commit may promote the paper to `BOUNDED_PAPER_READY_TO_FILE` only after
a deterministic rebuild of the recovered source, page-level visual inspection,
exact PDF and archive digest binding, licence verification, and filing metadata.
