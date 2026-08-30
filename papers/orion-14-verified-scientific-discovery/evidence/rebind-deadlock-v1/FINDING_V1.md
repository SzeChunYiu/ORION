# ORION-14 cannot refresh its journal-package PDF: a tooling deadlock

Found while running the acceptance-readiness pipeline against ORION-14 for TMLR.
**Pre-existing, not introduced by the manuscript edits that surfaced it.**

## The deadlock

`repository-paper-rebind.yml` exists to render the manuscript and place the PDF
into `journal_package/`. Its render step succeeds. Its next step fails:

```
journal package check failed: [('P4', [
  'missing artifact is actually present: journal_package/manuscript.pdf',
  'SCAFFOLDING package contains a PDF: manuscript.pdf'
])]
```

The two sides are individually reasonable and jointly unsatisfiable:

- `journal_package/MANIFEST.json` declares `"package_status": "SCAFFOLDING"`.
- `journal_package/CLAIM_PDF_AUDIT.md` states the package **"stays `SCAFFOLDING`
  until an in-tree or DOI-bound PDF is present"**.
- The package checker rejects a PDF **while** the status is `SCAFFOLDING`.
- The rebind workflow's entire purpose is to put that PDF there.

So the PDF is required to leave `SCAFFOLDING`, and forbidden while in it. The
workflow has failed on **every run since 2026-08-19**, across three branches,
independent of any manuscript change.

## Why it matters now

ORION-14 is listed **READY TO SUBMIT** on the release dashboard. It is the only
paper in the portfolio that renders as a full TMLR submission. But its
journal-package PDF cannot be refreshed by the automation that exists to refresh
it, so any manuscript correction leaves the packaged PDF stale and trips
`test_no_package_becomes_staler_than_it_already_was`.

That is precisely the situation now: two correct source repairs (a double-blind
identity leak, and an undisclosed inference unit) are blocked from landing not by
their own merit but by this deadlock.

## What would resolve it, and what would not

**Would not:** flipping `package_status` away from `SCAFFOLDING` to make the
check pass. The status is a claim about release readiness, and the audit ties it
to a real condition (an in-tree or DOI-bound PDF). Editing the flag to satisfy a
checker inverts the direction of evidence.

**Would:** make the ordering explicit in the checker, so that a package may
receive a PDF *and be promoted in the same operation*, with the promotion
recorded. The check is currently written as an invariant over a static tree; the
operation it blocks is a transition. Alternatively, the rebind workflow should
promote the status as part of the same run, which is a deliberate release act
and belongs to whoever owns the package.

Either resolution is a release-authority decision, not a repair I should make
unilaterally while running a manuscript-hardening pass.

`grants_authority: NONE`

**Terminal:** `REBIND_DEADLOCK__SCAFFOLDING_FORBIDS_THE_PDF_IT_REQUIRES`
