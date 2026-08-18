# ORION-P1 claim and PDF audit

**Audit date:** 2026-08-18
**Subject:** `journal_package/manuscript.pdf`, content-bound by `SHA256SUMS`

| Claim | Evidence | Verdict |
|---|---|---|
| Historical V1 broad H1 | `results/P1-T2_baseline_ablation_results.json` | `NOT_SUPPORTED` / `UNDERPOWERED`; preserved as negative history |
| Powered mechanical necessity | primary and replication result JSON plus concordance | `SUPPORTED` in both pre-bound runs |
| Independent result reconstruction | two `INDEPENDENT_VERIFICATION.json` records | `PASS`; 40,348 rows/run, zero score/analysis mismatches, exact terminal match |
| Safety and selectivity | result gate vectors | zero unnecessary control reframes, sibling regressions, and forbidden mutations in both runs |
| Claim boundary | abstract, results, limitations, conclusion, claim ledger | bounded to the credential-free mechanical world family; no model-general/open-ended claim |
| Nearest-work absorption | 36-row matrix plus rounds A--H ledgers | donor structures credited and incorporated into parents/ablations |
| Compiled PDF | rendered 27-page manuscript | `PASS` |

## PDF review

The final PDF was compiled after BibTeX and two convergence passes, then every
page was rendered with Poppler. The review explicitly checked:

- no unresolved citations or cross-references;
- no blank or multi-page figure payloads;
- Figure 1's host/candidate authority boundary and Figure 2's paired primary/
  replication labels are legible;
- historical Table 1, failure Table 2, powered Table 3, and the three-page
  36-row nearest-work Table 4 fit within the page and remain readable;
- no figure was stranded after the bibliography;
- section order distinguishes historical V1 evidence from the powered
  successor; and
- page numbering, margins, captions, and bibliography render consistently.

The original Figure 1 artifact failed this audit because it was a malformed
three-page PDF whose included first page was blank. It was rebuilt from a
tracked single-page SVG before this audit passed. Figure 2's float placement
was also corrected before the final render.

## Remaining external operations

A permanent DOI and a venue-specific cover letter cannot be produced until an
archive and venue are selected. They are recorded as submission operations,
not as scientific-evidence gaps. Repository redistribution remains restricted
until the owner selects a license.
