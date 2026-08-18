# P2 submission gate status — narrowed IP&M track

State as of **2026-08-18**.
Scientific scope receipt: `P2_NARROWED`.
Publication terminal: `PEER_REVIEW_READY` on that bounded claim.

Canonical scope receipt: `protocol/P2_NARROWED_PUBLICATION_TERMINAL_2026-08-17.md`.
Venue scope: `protocol/TARGET_JOURNAL_SCOPE_CHECK_2026-08-17.md`.
Current author-guide requirements: `notes/submission/IPM_SUBMISSION_REQUIREMENTS_2026-08-17.md`.

States are `DONE`, `DEFERRED`, `CANNOT_CHECK`, or `BLOCKED_ON`.

## Submission gate

| Item | State | Evidence / next condition |
| --- | --- | --- |
| Final scientific claim boundary | `DONE` | Narrowed to controlled mechanism evidence + bounded external stress tests. Matched external superiority is not claimed. |
| Target journal | `DONE` | IP&M selected for the narrowed methods / critical system-design claim surface. JASIST remains fallback after a larger use-oriented reframe. |
| Literature closure | `DONE` for readiness date | Dated primary-source freeze exists at `protocol/P2_LITERATURE_ASSIMILATION_FREEZE_2026-08-17.md`; no saturation is claimed. Re-run only if upload occurs after 2026-08-31. |
| Cover letter | `DONE` as draft / `BLOCKED_ON final metadata` | Narrowed IP&M draft exists. Author names, affiliations and corresponding-author details are intentionally not invented. |
| Supplement plan | `DONE` as plan / `BLOCKED_ON final assembly` | Plan enumerates evidence, licence exclusions, current venue constraints and future-work routes. |
| Current IP&M author-guide requirements | `DONE` | Official Guide for Authors recovered 2026-08-17: double-anonymized review; separate title page + anonymized manuscript; editable source; CAS LaTeX single-column template; abstract ≤250 words; 1–7 keywords; glossary; CRediT; generative-AI disclosure; submission checklist. |
| Title-page structure | `DONE` as template / `BLOCKED_ON human metadata` | `IPM_TITLE_PAGE_TEMPLATE.md`; identities/contact details/declarations require author input. |
| Abstract/keywords | `DONE` | Abstract is ~220 words after LaTeX normalization; 6 English keywords. |
| Glossary | `DONE` | `IPM_GLOSSARY.md`. |
| Generative-AI disclosure | `DONE` as truthful draft / `BLOCKED_ON author approval` | `GENERATIVE_AI_DECLARATION_DRAFT.md`; human authors must perform/approve the stated final verification. |
| Separate figure captions | `DONE` as companion | `IPM_FIGURE_CAPTIONS.md`; reconcile after any later caption edit. |
| Neutral manuscript compile | `DONE` | `journal_package/manuscript.pdf` is the checksummed 21-page canonical review PDF; the repository workflow compiles the same source. |
| Reference metadata + figure legibility | `DONE` | Citation/reference convergence, zero-overfull typography gate, and rendered inspection of every page passed. |
| Independent final PDF/claim proofread | `DONE` | Abstract, results, limitations, conclusion, tables, and figure pages were checked against the claim ledger and archived evidence. |
| CAS venue wrapper / final anonymization | `DEFERRED to filing operation` | Apply the current Elsevier CAS single-column wrapper and final identity-signal check together with author-supplied title-page metadata; this does not alter scientific readiness. |
| Author metadata | `BLOCKED_ON authors` | Automation must not infer authorship, affiliations, author order or corresponding-author details. |
| Permanent archive / DOI | `DEFERRED to filing operation` | Expiring Actions artifacts are now mirrored with hashes; mint a repository-independent DOI when the final deposit is made. |

## Scientific external routes — future work, not blockers for the narrowed paper

The following remain explicit `CANNOT_CHECK` / reopen triggers and must stay visible in the manuscript and archive:

1. a valid matched AutoResearchBench Wide ORION-vs-baseline campaign after the first OpenAIRE/Crossref attempt failed its prospective transport-validity gate;
2. matched multi-provider official Deep comparison;
3. official SAGE 200k corpus/evaluator;
4. final live-provider campaign and monetary/runtime/token ledger.

The scorer-native identity bridge is now demonstrated, but every DOI-crosswalk request in the matched campaign returned HTTP 400. Its byte-identical candidate projections and zero paired difference are invalid transport evidence, not scientific zeros.

## Reproducibility / integrity gate

| Item | State | Artifact |
| --- | --- | --- |
| Offline complete-gold regeneration | `DONE` | `scripts/run_offline_companion.py --check`; independent clean-CI reproduction already exists on main. |
| Result claim binding | `DONE` | `protocol/CLAIM_LEDGER_V1.json`, `scripts/check_claim_ledger.py`; result-bearing abstract/results/limitations/conclusion prose is evidence-bound. |
| P2 donor assimilation | `DONE` | `protocol/P2_DONOR_ASSIMILATION_LEDGER_V1.json`, `scripts/check_p2_assimilation.py`, hostile tests. |
| Bounded external result archives | `DONE` | MetaSyn, bounded AutoResearchBench Wide/Deep, and the failed OpenAIRE/Crossref matched campaign are retained with their authority limits and mirrored CI bundles. |
| Raw final live-provider archive | `DEFERRED / future work` | Not required for the narrowed paper because no live-provider superiority claim is made. Capture machinery remains available for a reopened prospective campaign. |
| Durable evidence mirror | `DONE` | The expiring MetaSyn and matched OpenAIRE/Crossref Actions artifacts have checksummed repository mirrors. A repository-independent DOI remains a filing operation. |

## Filing operations after `PEER_REVIEW_READY`

Only upload-time mechanics and human-supplied metadata remain:

1. final CAS single-column venue wrapper + double-anonymization check;
2. actual author/title-page/CRediT/funding/competing-interest metadata and approval of the generative-AI disclosure;
3. literature refresh if upload occurs after 2026-08-31;
4. repository-independent archive deposit / DOI.

External superiority is deliberately **not** on this blocker list. The paper has been shrunk instead of treating unavailable authority or null stress tests as positive evidence.

## Issue consequences

- #157 can terminate after branch CI verifies the runnable P2 closure artifacts.
- #279 can terminate at its allowed `CANNOT_CHECK / REFUTED_OR_SHRINK` path.
- #317 can terminate `P2_NARROWED`; saturation is not claimed.
- #318's P2 consumer tranche is complete, but the shared issue remains open for non-P2 obligations.
- #99 may close on this bounded `PEER_REVIEW_READY` terminal; maximal external superiority remains a follow-up programme.
