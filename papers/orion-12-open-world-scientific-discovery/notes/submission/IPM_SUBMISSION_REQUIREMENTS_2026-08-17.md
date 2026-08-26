# IP&M submission requirements — checked 2026-08-17

Authoritative source: current ScienceDirect *Information Processing & Management* Guide for Authors (ISSN 0306-4573), checked 2026-08-17.

## Review and file model

- Peer review is **double anonymized**.
- Upload a **separate title page** containing author details and an **anonymized manuscript** without author names or affiliations.
- Editable source files are required. For LaTeX, submit `.tex` sources; a PDF alone is not an acceptable source file.
- IP&M points LaTeX authors to Elsevier's template and specifically to the **CAS LaTeX Single-Column Template**.
- The online system builds the reviewer PDF from the uploaded editable files.

## Front matter

- Abstract: concise/factual and **no more than 250 words**.
- Keywords: **1–7**, in English.
- Current ORION-12 abstract is approximately 220 words after LaTeX-command normalization.
- Current ORION-12 manuscript has 6 English keywords.

## Double-anonymized title page

The separate title page must carry, at minimum:

- article title;
- all author names;
- affiliations with full postal addresses/country;
- acknowledgements;
- declaration of interest;
- corresponding-author full address and email.

The live submission checklist additionally asks for corresponding-author phone/contact details. These values are author-supplied and must never be inferred by automation.

## Manuscript structure / companion files

- Provide definitions of field-specific terms in a **separate glossary list**.
- Corresponding authors must provide a **CRediT contribution statement** for co-author roles.
- Tables must remain editable text, be cited, numbered and captioned.
- For LaTeX submissions, figure captions should be supplied separately in addition to being associated with the manuscript figures.
- References cited in text must appear in the reference list and vice versa.
- Check spelling/grammar and permissions for any third-party copyrighted material.

## Generative-AI disclosure

The current IP&M guide requires authors to declare generative-AI use in manuscript preparation. The disclosure is placed in a new section before the references. AI tools may not be listed as authors. Human authors remain responsible for verifying, editing and taking responsibility for the final content.

This ORION-12 closure lane used OpenAI ChatGPT for research support, source checking, code/manuscript review and submission-package preparation. A truthful disclosure draft is stored in `GENERATIVE_AI_DECLARATION_DRAFT.md`; the human authors must review/approve the wording before submission.

## ORION-12 compliance status

| Requirement | Status |
| --- | --- |
| IP&M scope fit | `DONE` — narrowed methods / critical system-design paper |
| Double-anonymized reviewer manuscript | `READY_FOR_FINAL_ANONYMIZATION` — repository author line is only a non-identifying working placeholder, but final submission source/PDF must remove it and be checked for indirect identifiers |
| Separate title page structure | `DONE` as template; author-supplied identities/contact details remain input |
| Abstract ≤250 words | `DONE` (~220 words) |
| 1–7 English keywords | `DONE` (6) |
| Editable LaTeX source | `DONE` |
| CAS LaTeX single-column venue wrapper | `TO_APPLY_AT_FINAL_UPLOAD` — journal encourages its template; neutral source remains the evidence-bound canonical manuscript until the final venue wrapper is generated/checked |
| Separate glossary | `DONE` as submission companion draft |
| CRediT | `DONE` as template; author-role mapping remains author input |
| Generative-AI disclosure | `DONE` as truthful draft; final human approval required |
| Separate figure captions | `DONE` as submission companion |
| Reference/citation compile gate | repository `p2-manuscript` workflow |
| Visual PDF inspection | required after successful workflow artifact |

## Submission-day non-code inputs

The following cannot be legitimately filled by repository automation and are not scientific-result blockers:

1. final author order, names, affiliations and corresponding-author contact details;
2. author-approved CRediT roles, acknowledgements, funding and competing-interest declarations;
3. author-approved generative-AI disclosure wording;
4. final anonymization check against indirect identity leakage;
5. literature refresh within 14 days of the actual submission date;
6. the live Editorial Manager metadata fields and any requirement changed after this 2026-08-17 check.

These are explicit operator inputs, not reasons to invent additional experiments or relabel `CANNOT_CHECK` external evidence.