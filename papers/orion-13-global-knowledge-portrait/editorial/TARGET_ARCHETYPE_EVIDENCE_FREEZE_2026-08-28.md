# ORION-13 target, archetype, and evidence freeze — 2026-08-28

## Resolved submission profile

- **Primary target:** *Semantic Web Journal* (SWJ), full paper.
- **Fallback:** *Journal of Web Semantics*, subject to a fresh target-specific policy and fit check before any retargeted filing.
- **Dominant archetype:** bounded methods/measurement paper.
- **Secondary archetype:** small prospective comparison of deterministic decision rules.
- **Intended reader:** semantic-integration and knowledge-graph researchers who need to decide whether two already-structured scientific claims may be merged.
- **Scientific surface:** C5/C9 structured mapping only. Raw-text extraction, the expert atlas, downstream use, broader successor protocols, and universal coordinate necessity are excluded.

The manuscript's evidence progression is:

`mapping risk -> typed decision rule -> prospectively frozen case-ID-disjoint comparison -> retained nulls and abstentions -> boundary`

## Current official SWJ contract checked live

Checked 2026-08-28 against:

- <https://www.semantic-web-journal.net/authors>
- <https://www.semantic-web-journal.net/faq>

The official pages state that full papers are assessed for originality, significance, and writing quality; evaluation should be detailed enough to enable replication. A submission is one PDF containing all figures and tables, with 3--7 keywords. Submitted manuscripts and review materials are made public through the journal's open-review process. Relevant data and software should be sufficient for evaluation and replication, provided as one organized archive at a long-term stable URL that is not changed during a review phase. There is no strict page limit; the FAQ advises generally remaining below about 25 pages excluding references. The FAQ currently lists an APC of US$2,100 for submissions from 1 September 2024 onward.

The current SWJ authors page links to the Sage LaTeX template at
<https://uk.sagepub.com/sites/default/files/sage_latex_template_4.zip>.
On 2026-08-28 that URL redirected to `www.sagepub.com` and returned an HTML page titled `404 - Page Not Found`, not a ZIP archive. The present generic one-file PDF is therefore an audited review object, not a claim of template compliance.

FAQ Q28 permits generative AI only as acknowledged writing assistance. It requires the intellectual contribution to be human-written and disallows papers written extensively by generative AI, including entire paragraphs or pages and AI text only lightly polished by humans. This is a filing-time integrity constraint, not a copyediting detail.

## Evidence freeze

Author-supplied scientific evidence consists of:

- 32 initial structured public-reference cases;
- 32 prospectively frozen confirmatory cases with zero repeated case identifiers;
- two recurring source-locator--content-hash records across those sets;
- registered flat-predicate and exact-coordinate controls;
- a deterministic 10,000-resample paired bootstrap with seed `20260817`;
- a frozen confirmatory analysis;
- a standard-library-only structurally separate replay that imports none of the original analysis code.

The confirmatory result is 0.0000 versus 0.1875 false merges, paired difference -0.1875 with 95% interval [-0.34375,-0.0625], and false-split difference 0.0000 [0.0000,0.0000] versus the exact-coordinate control. All six prevented false merges are polarity contrasts. The exact-coordinate control abstains on 0.1875 of cases.

## Real blockers

1. No long-term stable immutable review-archive URL is bound.
2. The linked Sage LaTeX template is not retrievable as a ZIP from the official link.
3. Exact affiliation, ORCID, funding, conflicts, author contributions, and acknowledgements remain human-only filing inputs; only name and email were supplied.
4. The author must establish compliance with SWJ's human-writing rule. AI-generated paragraphs cannot be made compliant merely by light human polishing.
5. The current 32-case polarity-localized comparison against a deliberately weak baseline may not meet SWJ's significance threshold. The minimum scientific resolution is a target/editor fit decision backed by either a same-universe current structured comparator or a defensible retargeting; simulated review cannot waive this criterion.

Until these are resolved, the proper editorial terminal is `blocked_by_integrity_or_compliance`, not submission readiness.
