# Latest-main science audit — 2026-08-29

**Assessed immutable main:** `87e2bcb330d243b7062ddba1ca26e426632edeab`  
**Purpose:** identify current-state facts that materially change the older
portfolio matrix before writing new science.  This audit creates no claim
authority.

## Reviewed latest state

The assessed main tip is the 108-branch modification sweep.  Its most important
scientific safeguard is negative: it recovered unique evidence path-by-path but
reverted an attempted ORION-11 adoption after discovering that the stale branch
removed the later R4 retraction.  The correct comparison surface is therefore
full claim rows and lost semantic lines, not filenames or claim text alone.

The same tip recovered bounded/theory packets for ORION-01/02/05/09/13/14/19/23,
ORION-25 trust-domain/cross-site evidence, and the ORION-24 Round-1 harvest.  No
recovered packet automatically upgrades a paper.

## Current-state corrections to the older disposition matrix

1. **PDF count:** merge #1731 added canonical CI-built PDFs for ORION-05/06/07/08/09/10/19.  The remaining no-PDF papers are the Markdown-only ORION-02 and ORION-04.  Open PR #1734 carries the documentation correction; this branch does not duplicate it.
2. **ORION-07:** current main contains scored QG19 and QG20 replacement instances and `MANUSCRIPT_V3.md`, a bounded three-question case series.  QG20 is an explicit agreement-with-wrong-diagnosis result.  The older `JOURNAL_READINESS.md` still says the extra-instance gate is blocked and therefore needs a claim-preserving reconciliation; no reliability percentage is authorized.
3. **ORION-19:** current main contains `manuscript/main.tex` and `manuscript/main.pdf`; the older matrix statement that the manuscript directory is empty is stale.  This fixes production state, not the unexecuted UT3 grid.
4. **ORION-02:** open PR #1732 shows that the R23 39/44 versus 32/44 control difference is not established as a paired win (exact McNemar p=0.0923; paired bootstrap interval includes zero).  The adverse 0.95 gate miss and R24 invalid-certificate terminal remain unchanged.
5. **Candidate content binding:** open PR #1733 repairs a writer/checker path-set asymmetry and re-pins the ORION-16 subject commit to a permanent main ancestor.  Any promotion depending on that binding must account for the PR rather than duplicate or bypass it.
6. **ORION-24:** Round-1 agent harvest bytes are present.  They remain same-researcher executions, not blinded external expert adjudication, and do not close R2/R3.

## Consequence for this package

All new work is additive under `papers/top_tier_gap_closure/`.  It does not edit
content-bound manuscripts, frozen protocols, evidence terminals or retraction
ledgers.  The paper-level matrix records immediate actions and dependencies but
asserts zero top-tier promotions.
