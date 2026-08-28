# ORION-14 target-policy audit — TMLR — 2026-08-28

**Checked against current official TMLR/JMLR pages on 2026-08-28.**  
This is a packaging/editorial record, not journal acceptance authority.

## Acceptance decision axes

Official TMLR acceptance criteria ask whether the submission's claims are supported by accurate, convincing and clear evidence, and whether some members of the TMLR audience would be interested. TMLR explicitly states that a claims/evidence gap can be repaired either by adding evidence or by reducing the claim, and that significance/SOTA should not be used as an independent rejection criterion.

Implication for ORION-14: the bounded V2/V3/P4-X paper does not need a naturalistic successor merely to satisfy the formal TMLR acceptance rule. It does need claims to remain exactly within finite evidence and relevance to machine-learning/intelligent-system evaluation to be clear.

Official source: https://jmlr.org/tmlr/acceptance-criteria.html

## Scope / editor triage

TMLR accepts methodological and theoretical work and has no preference between them, provided the work is in scope and reviewer expertise exists. Action editors may desk-reject for lack of scope, anonymity, formatting violations, poor quality or low likelihood of meeting the acceptance criteria.

Implication for ORION-14: retain the research-agent / intelligent-system evaluation framing only where scientifically real. Do not manufacture a learning claim. Re-triage fit after revision.

Official sources:
- https://www.jmlr.org/tmlr/
- https://jmlr.org/tmlr/faq.html
- https://jmlr.org/tmlr/ae-guide.html

## Double blind and supplementary material

- TMLR uses double-blind review and the submission must be anonymized.
- Standard submissions must use the TMLR LaTeX stylefile/template.
- Authors may upload up to 100 MB of supplementary material in PDF or ZIP format.
- Supplementary material must also be anonymized.
- TMLR encourages anonymized data/code supplementary material when it improves reproducibility.
- TMLR permits public preprints, but the blinded submission must not link to an identifying version.

Implication for ORION-14: the blind manuscript should not point reviewers to the public repository owner. Use the neutral anonymous review-artifact plan in `submission/ANONYMOUS_REVIEW_ARTIFACT_MANIFEST_V1.md`; restore public identifiers after unblinding/publication as policy permits.

Official source: https://www.jmlr.org/tmlr/author-guide.html

## LLM assistance

Current TMLR policy permits LLMs as assistive tools, holds authors fully responsible for content, and requires authors who used ChatGPT/other LLMs to state that use explicitly in a first-page footnote. TMLR also states its expectation that the paper's ideas, claims and results are human-sourced.

Implication for ORION-14: a first-page disclosure is a filing requirement, but exact wording is fact-dependent and cannot be inferred or fabricated by this pipeline. Author must verify the actual use scope before the disclosure is inserted.

Official sources:
- https://www.jmlr.org/tmlr/editorial-policies.html
- https://www.jmlr.org/tmlr/faq.html

## Current target-compliance checklist

- [x] TMLR target retained for recursive evaluation rather than assumed accepted-fit.
- [x] Mandatory TMLR style is used by the manuscript source.
- [x] Author identity is not printed in the manuscript source.
- [x] Main manuscript availability text no longer exposes the public repository owner.
- [x] Anonymous supplementary artifact plan exists.
- [x] Exact anonymous ZIP review artifact materialized, deterministically rebuilt, checksum-bound and identity-scanned.
- [x] `MM`, `YYYY` and `XXXX` retained exactly as the current official template instructs for an initial under-review submission; the template labels them camera-ready-only replacements, so they are not release placeholders at this stage.
- [x] Actual LLM assistance in manuscript editing/review-package preparation is verified by this workflow and disclosed in an unnumbered first-page footnote.
- [ ] OpenReview profile/author/affiliation/ORCID/funding/conflict/ethics metadata supplied by humans at filing.
- [x] Final exact PDF passes page-level audit and package hash binding: 19 pages,
      SHA-256 `d9b8fbf3b9f16a7c35b478a810121d8803ae2d848a7817d0cff33e6d47126110`.

## Target terminal today

`TMLR_POLICY_FIT_PLAUSIBLE__ANONYMOUS_PACKAGE_DISCLOSURE_AND_PINNED_PDF_CLOSED__HUMAN_FILING_METADATA_ONLY`

This does not supersede the scientific/editorial concern ledger. It only closes the question of what TMLR currently requires.
