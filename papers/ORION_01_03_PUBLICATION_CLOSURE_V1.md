# ORION-01 / ORION-02 / ORION-03 publication closure V1

**Date:** 2026-08-31  
**Scope:** publication closure only; no new science unless a genuine scientific defect is found.

## Hostile-review basis

The closure used `SzeChunYiu/academic-paper-skills` at commit `a45568215d648e5d446a03980277d282b19e57d7` and four review lenses: claim-authority/scientific-method, adversarial claim/citation review, journal-package completeness, and computational reproducibility.

The hostile pass found publication-control defects, not a new scientific defect requiring new science: ORION-01 packages were still capable of verifying superseded R2 copies; ORION-02 and ORION-03 lacked equivalent V3 journal-package bindings; and ORION-03 retained a historical V2/R2 freeze surface that needed an explicit current V3 filing-status designation. The historical freeze is preserved rather than rewritten.

## Claim-authority disposition

No manuscript claim is strengthened by this closure. The canonical V3 manuscripts remain authoritative only through their V3 claim ledgers and existing submission-boundary/canonical-designation files. Negative results, `NOT CLAIMED`, `FORBIDDEN`, donor-owned, proof-system-relative, representation-relative, and fail-closed boundaries remain binding.

A bounded submission-date nearest-work screen was used as an overlap attack. Its negative outcome is non-authorizing: “not located in the bounded search” is not a novelty certificate, and donor mathematics or generic constructions remain donor-owned where the ledgers say so.

## Packages

- ORION-01A: `orion-01-certificate-realization/journal_package_A/` -> V3 source + V3 ledger.
- ORION-01B: `orion-01-certificate-realization/journal_package_B/` -> V3 source + V3 ledger.
- ORION-02: `orion-02-fiberguard-finite-fibre/journal_package/` -> V3 source + V3 ledger.
- ORION-03: `orion-03-typed-merge-falsification/journal_package/` -> V3 source + V3 ledger.

Every package verifies exact canonical bytes via Git blob IDs, supplies a reproducible PDF build, validates PDF structure/text, records SHA-256 receipts, and fails closed on source/ledger drift.

## Automated final gate

`.github/workflows/orion-01-03-publication-closeout.yml` pins the academic-paper-skills donor commit, runs its strict manuscript-surface audit on all four package sources, runs the fail-closed package verifiers, builds fresh PDFs, validates each PDF with `qpdf` and `pdftotext`, and reruns render-required verification. Branch pushes commit the validated PDF/checksum outputs back to the closure branch so the merged package contains the exact checked renders.

## Assurance boundary

Scientific and package closure does not fabricate filing metadata. Before an external submission, humans must confirm author/affiliation/ORCID data, target journal/style, conflicts and funding, publication licence, and any required archival DOI. Those fields cannot authorize broader scientific claims.
