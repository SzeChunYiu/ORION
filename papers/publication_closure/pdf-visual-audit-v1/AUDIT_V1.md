# Visual audit of exact manuscript PDFs — batch 1

Progress against the #1701 box "all exact PDFs have been visually audited".
**5 of 22** manuscript PDFs audited as **rendered pages**, not extracted text, so
layout and rendering defects are visible.

| paper | KB | verdict |
|---|---|---|
| ORION-03 typed-merge-falsification | 62 | clean |
| ORION-08 typed-state | 197 | clean |
| ORION-11 recursive-epistemic-reconstruction | 509 | clean |
| ORION-14 verified-scientific-discovery | 739 | clean, **submission-formatted** |
| ORION-22 adaptive-state-reasoning | 152 | clean (see paper-local audit) |

No placeholders, unresolved references, missing-figure boxes, or internal-path
leakage in any of the five.

## The finding worth reporting is what these abstracts do voluntarily

Every one of the five states a limit or a non-claim **in the abstract**, where a
referee reads it first, rather than burying it in limitations:

- **ORION-03** — refuses a performance reading of its own headline: *"The
  evaluator's zero unsafe merges and zero needless rejections are not
  detector-performance measurements; because it authorizes exactly the
  parent-authorized set, those values are analytic consequences of the formal
  semantics."* It also independently reproduces the corpus figures verified
  separately this session: *"46 hybrid cases occur among 1,962 third-party
  OpenSSL-derived merge tasks."*
- **ORION-08** — declines a result it could have claimed: *"its advantage over
  never reopening at all is not separated from zero at this sample size and we
  do not claim it"*, plus *"LLM-labeled controls are deterministic proxies;
  chain identifiers are not cryptographic security."*
- **ORION-11** — reports the numbers that **refute** its own comparative
  readings: a faithful comparator also reaches 1.0000, *"so no comparative
  mechanism-necessity margin is claimed"*, and costed ordering *"costs 1.82
  times a faithful Active-VOI comparator against a preregistered gate requiring
  below 0.80, so no comparative economy residual is claimed either."*
- **ORION-14** — carries intervals throughout (*paired difference 1.0, 95% CI
  [1.0, 1.0]*; *0.375, domain-stratified 95% bootstrap [0.3275, 0.4225]*) and
  reports a zero: *"76/80 publication-archive-revision bridges but zero eligible
  natural pairs."*
- **ORION-22** — discloses a **withheld** superiority claim with its reason, and
  puts its preregistered critical negative in the abstract: *"its price and
  distribution-shift axes are both BROKEN."*

## ORION-14 is submission-formatted

Alone among the five it renders as a live submission: `Under review as
submission to TMLR` header, `Anonymous authors / Paper under double-blind
review`, and a real citation apparatus. The others render as working drafts.
That is a packaging difference, not a science difference, and it is the concrete
gap between "bounded paper complete" and "filed".

## Method note

A cheap structural pre-check was attempted first (page counts from the raw
stream, Spotlight text index) and **discarded**: it returned `pages=0` and
`no-text-index` for all 22 identically, which is the signature of a broken probe
rather than 22 identical papers. Rendered-page reading is the method that works.

**Remaining:** 17 of 22. `grants_authority: NONE`.

**Terminal:** `PDF_VISUAL_AUDIT_5_OF_22__NO_DEFECTS_FOUND`

---

# Batch 2 — 8 of 22 audited

| paper | KB | verdict |
|---|---|---|
| ORION-06 recursive-recovery | 133 | clean |
| ORION-12 open-world-scientific-discovery | 469 | clean |
| ORION-25 orion-research-harness | 376 | clean, partially submission-formatted |

Still no placeholders, unresolved references, missing-figure boxes, or
internal-path leakage in any PDF audited.

## The pattern holds, and strengthens

- **ORION-06** names its own submission gate in the abstract: *"A fresh
  literature closure remains a submission gate for any novelty statement about
  the methodology itself."* It also refuses the general reading: *"The evidence
  is a one-programme case study, not a statistical evaluation of
  research-methodology effectiveness."*
- **ORION-12** enumerates its own failures in the abstract — *"six locked gates
  fail and the full candidate loses to its frozen u4 donor"*, *"V10 fails four
  gates"*, *"only 4/7 reviews support it"*, *"Independent custody remains 0/3"* —
  and **ends on** *"open-world benefit remains unconfirmed."*
- **ORION-25** titles its opening section **"Scope and nonclaims"**, and closes
  it with *"The framework grants no scientific truth, novelty, publication,
  deployment or adoption authority."*

## Submission formatting is the discriminator, not science quality

Of eight audited, the split is now clear:

- **ORION-14** — full submission render: TMLR header, `Anonymous authors / Paper
  under double-blind review`, citation apparatus.
- **ORION-25** — partial: `Anonymous Authors` and numbered citations `[4, 5, 6,
  10]`, but no venue header.
- **The other six** — `Working framework draft` + a date. No anonymisation, no
  venue, no bibliography rendered on page 1.

Every one of the eight is scientifically disciplined about its own limits. What
separates them is packaging. That is the actionable finding for the #1701
"bounded paper ready to file" boxes: the science is not the blocker.

**Remaining:** 14 of 22.

**Terminal (batch 2):** `PDF_VISUAL_AUDIT_8_OF_22__NO_DEFECTS__PACKAGING_IS_THE_GAP`
