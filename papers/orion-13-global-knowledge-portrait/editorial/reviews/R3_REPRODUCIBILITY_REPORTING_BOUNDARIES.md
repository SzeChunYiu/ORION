# Reviewer 3 — reproducibility, reporting, clarity, and boundaries

**Blind review object:** PDF SHA-256 `b843d9ef8cd399c3e186e3a05edca582a2bd9de08f3c22d192b7187b42ac4c19` (8 pages)

**Recommendation:** major revision; filing blocked pending compliance inputs.

The compact manuscript is readable, the two tables suffice, and raw-text/downstream exclusions are visible. The remaining issues are review-resource and policy requirements rather than typographic polish.

## R3-M1 — Immutable review archive is missing

SWJ asks for relevant data/software as one organized archive at a long-term stable URL that remains unchanged during a review phase. The manuscript correctly says that no such URL is currently asserted.

**Resolution test:** deposit the exact review ZIP at a long-term stable immutable URL, place that URL in the manuscript and cover letter, and bind its byte count and SHA-256 digest in the submission manifest.

## R3-M2 — Official template route is broken

The SWJ authors page points to a Sage LaTeX ZIP that currently resolves to an HTML 404 page. The generic article PDF is not evidence of target-template compliance.

**Resolution test:** obtain a working current template from the journal/publisher or written editor guidance accepting the present initial-submission format, then rebuild and audit the exact filing PDF.

## R3-M3 — SWJ generative-AI policy requires human authorship confirmation

FAQ Q28 permits acknowledged assistance but disallows papers written extensively by generative AI, including whole paragraphs or pages and lightly polished AI text. An acknowledgement cannot by itself establish compliance.

**Resolution test:** the human author rewrites where necessary, verifies every source and scientific statement, confirms the exact assistance disclosure, and provides an explicit filing attestation that the submitted intellectual prose satisfies Q28. This cannot be self-certified by the editing system.

## R3-M4 — Filing declarations are incomplete

Name and email are present, but exact affiliation, ORCID, funding, conflicts, contributions, and final acknowledgements are absent.

**Resolution test:** the human author supplies or explicitly marks not applicable every required field before filing.

## R3-M5 — Package and PDF identity must converge

The historical journal package points to an earlier PDF. The new narrowed manuscript needs a fresh deterministic build, visual audit, source closure, and exact submission-byte manifest.

**Resolution test:** two clean fixed-epoch builds are byte-identical; every page is inspected; source closure and package hashes match; the old package remains historical rather than being overwritten silently.
