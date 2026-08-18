# P2 submission gate status — narrowed IP&M track

State as of **2026-08-17**.
Scientific terminal: `P2_NARROWED`.
Publication terminal remains open until the mechanical PDF/package checks pass.

Canonical scope receipt: `protocol/P2_NARROWED_PUBLICATION_TERMINAL_2026-08-17.md`.
Venue scope: `protocol/TARGET_JOURNAL_SCOPE_CHECK_2026-08-17.md`.
Current author-guide requirements: `notes/submission/IPM_SUBMISSION_REQUIREMENTS_2026-08-17.md`.

States are `DONE`, `DEFERRED`, `CANNOT_CHECK`, or `BLOCKED_ON`.

## Submission gate

| Item | State | Evidence / next condition |
| --- | --- | --- |
| Final scientific claim boundary | `DONE` | Narrowed to controlled mechanism evidence + bounded external stress tests. Matched external superiority is not claimed. |
| Target journal | `DONE` | IP&M selected for the narrowed methods / critical system-design claim surface. JASIST remains fallback after a larger use-oriented reframe. |
| Literature closure | `DEFERRED until actual submission date` | Dated primary-source freeze exists at `protocol/P2_LITERATURE_ASSIMILATION_FREEZE_2026-08-17.md`, but material stopping work appeared on 2026-08-13; no saturation is claimed. Re-run inside 14 days of submission. |
| Cover letter | `DONE` as draft / `BLOCKED_ON final metadata` | Narrowed IP&M draft exists. Author names, affiliations and corresponding-author details are intentionally not invented. |
| Supplement plan | `DONE` as plan / `BLOCKED_ON final assembly` | Plan enumerates evidence, licence exclusions, current venue constraints and future-work routes. |
| Current IP&M author-guide requirements | `DONE` | Official Guide for Authors recovered 2026-08-17: double-anonymized review; separate title page + anonymized manuscript; editable source; CAS LaTeX single-column template; abstract ≤250 words; 1–7 keywords; glossary; CRediT; generative-AI disclosure; submission checklist. |
| Title-page structure | `DONE` as template / `BLOCKED_ON human metadata` | `IPM_TITLE_PAGE_TEMPLATE.md`; identities/contact details/declarations require author input. |
| Abstract/keywords | `DONE` | Abstract is ~220 words after LaTeX normalization; 6 English keywords. |
| Glossary | `DONE` | `IPM_GLOSSARY.md`. |
| Generative-AI disclosure | `DONE` as truthful draft / `BLOCKED_ON author approval` | `GENERATIVE_AI_DECLARATION_DRAFT.md`; human authors must perform/approve the stated final verification. |
| Separate figure captions | `DONE` as companion | `IPM_FIGURE_CAPTIONS.md`; reconcile after any later caption edit. |
| Neutral manuscript compile | `BLOCKED_ON repository CI` | Compile narrowed `manuscript/main.tex` and retain PDF/log. This evidence-bound neutral compile precedes final CAS venue wrapping. |
| Reference metadata + figure legibility | `BLOCKED_ON compiled PDF` | Static identifier checks are not a substitute for visual inspection of the rendered paper. |
| Independent final PDF/claim proofread | `BLOCKED_ON compiled PDF` | Claim-ledger checks guard evidence drift but do not replace a final PDF read. |
| CAS venue wrapper / final anonymization | `BLOCKED_ON clean neutral PDF + author review` | Apply the current Elsevier CAS single-column template and remove/check direct and indirect identity signals before upload. |
| Author metadata | `BLOCKED_ON authors` | Automation must not infer authorship, affiliations, author order or corresponding-author details. |
| Permanent archive / DOI | `BLOCKED_ON deposit` | Recommended before public release. Mirror expiring raw external artifacts before retention windows lapse. |

## Scientific external routes — future work, not blockers for the narrowed paper

The following remain explicit `CANNOT_CHECK` / reopen triggers and must stay visible in the manuscript and archive:

1. matched AutoResearchBench Wide ORION-vs-baseline without the frozen arXiv scorer-native path;
2. matched multi-provider official Deep comparison;
3. official SAGE 200k corpus/evaluator;
4. final live-provider campaign and monetary/runtime/token ledger.

The exact Wide blockers remain `FROZEN_ADAPTER_REQUIRES_ARXIV`, `OFFICIAL_SCORER_ARXIV_ID_IOU`, and `NO_ARXIV_MATCHED_RUNNER_ON_MAIN`. They are not converted into scientific zeros.

## Reproducibility / integrity gate

| Item | State | Artifact |
| --- | --- | --- |
| Offline complete-gold regeneration | `DONE` | `scripts/run_offline_companion.py --check`; independent clean-CI reproduction already exists on main. |
| Result claim binding | `DONE` | `protocol/CLAIM_LEDGER_V1.json`, `scripts/check_claim_ledger.py`; result-bearing abstract/results/limitations/conclusion prose is evidence-bound. |
| P2 donor assimilation | `DONE` | `protocol/P2_DONOR_ASSIMILATION_LEDGER_V1.json`, `scripts/check_p2_assimilation.py`, hostile tests. |
| Bounded external result archives | `DONE` | MetaSyn plus bounded AutoResearchBench Wide/Deep evidence are retained with their authority limits. |
| Raw final live-provider archive | `DEFERRED / future work` | Not required for the narrowed paper because no live-provider superiority claim is made. Capture machinery remains available for a reopened prospective campaign. |
| Permanent repository-independent archive | `BLOCKED_ON deposit` | Do not let expiring workflow artifacts become the only copy of raw external evidence. The prior gate audit recorded MetaSyn raw Actions-artifact expiry at `2026-09-15T21:39:53Z`; mirror before that date or re-establish the raw evidence through a reproducible rerun where possible. |

## What now blocks `PEER_REVIEW_READY_NARROWED`

Only publication mechanics, human authorship inputs and dated freshness checks remain:

1. repository-CI compile of the narrowed evidence-bound manuscript with retained PDF/log;
2. reference metadata + figure-legibility audit on that PDF;
3. independent final PDF/claim proofread;
4. final CAS single-column venue wrapper + double-anonymization check;
5. actual author/title-page/CRediT/funding/competing-interest metadata and approval of the generative-AI disclosure;
6. literature refresh within 14 days of the chosen submission date;
7. preferably, permanent archive/deposit of durable reproducibility material, especially raw external artifacts with finite retention.

External superiority is deliberately **not** on this blocker list. The paper has been shrunk instead of treating unavailable authority or null stress tests as positive evidence.

## Issue consequences

- #157 can terminate after branch CI verifies the runnable P2 closure artifacts.
- #279 can terminate at its allowed `CANNOT_CHECK / REFUTED_OR_SHRINK` path.
- #317 can terminate `P2_NARROWED`; saturation is not claimed.
- #318's P2 consumer tranche is complete, but the shared issue remains open for non-P2 obligations.
- #99 remains the final publication wrapper until the PDF/package gates above pass; its scientific external-result blocker has been removed by the explicit final reframe.
