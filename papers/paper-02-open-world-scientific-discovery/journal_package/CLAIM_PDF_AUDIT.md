# ORION-P2 independent claim / PDF audit

Audit subject: `153065a65441d2f17cb122dffa464d31786635e0` plus the
checksummed final package. This is a publication audit, not a new issue #283
scientific-verification record.

| ID | Claim boundary | Artifact | Status |
| --- | --- | --- | --- |
| P2.OFFLINE | 390-task complete-gold recall 0.979487 vs 0.666667 | `evidence/offline_results/RESULTS_SUMMARY_V1.json` | BOUNDED (`TIER_B_committed`, mandatory underpowered label, no H1 promotion) |
| P2.METASYN | 86-review ID-only retrieval/screening probe | `evidence/external_results/METASYN_ID_ONLY_PROBE_V1.json` | BOUNDED |
| P2.DEEP | Official Deep title judge, 600 tasks, hit rate 0.000 after 9/9 control | `evidence/external_results/DEEP_OFFICIAL_ARCHIVE_V1.json` | BOUNDED negative diagnostic |
| P2.WIDE.OPENAIRE | 400-row matched OpenAIRE/Crossref campaign | result + receipt + mirrored artifacts | CANNOT_CHECK: 400/1,200 provider calls failed; zero paired effect is invalid for science |
| P2.H1 | External ORION-vs-strong-baseline discovery superiority | `evidence/CLAIM_LEDGER_V2.md` | CANNOT_CHECK / not claimed |
| P2.NARROWED | Fail-closed route/read/stopping authority and controlled mechanism behavior | attestation + machine ledger + manuscript | BOUNDED |
| P2.PDF | Canonical review manuscript | `journal_package/manuscript.pdf` | SUPPORTED |

## Rendered-PDF inspection

- 21 US-letter pages; no encryption, JavaScript, or form content.
- LaTeX/BibTeX converged with no unresolved citation/reference warning.
- The zero-tolerance typography gate reports zero overfull boxes.
- Every page was rendered; the title/abstract, formalism, main results table,
  limitations, availability/reproducibility text, references, pipeline diagram,
  recall/query curve, route-contribution plot, overlap matrix, and stopping-
  failure plot were inspected at readable resolution.
- No clipping, overlap, blank included page, displaced caption, or unreadable
  table/axis label was found.
- The new OpenAIRE/Crossref paragraph matches its immutable result and receipt
  and calls the campaign `CANNOT_CHECK`, not a valid negative result.

Machine-checked ledger: `protocol/CLAIM_LEDGER_V1.json` via
`scripts/check_claim_ledger.py --check`. This audit does not promote the offline
delta, bounded probes, or invalid Wide campaign into external superiority.
