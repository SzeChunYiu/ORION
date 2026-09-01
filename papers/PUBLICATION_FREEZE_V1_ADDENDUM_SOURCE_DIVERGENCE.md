# Addendum to PUBLICATION_FREEZE_V1: the frozen PDFs do not rebuild from source

Found immediately after the freeze landed, by two independent packaging passes
(ORION-05 and ORION-12) that hit the same defect class from different directions.

## What was found

`PUBLICATION_FREEZE_V1.json` binds each paper's `manuscript/main.pdf` by sha256.
Those digests are correct. What the freeze does **not** establish, and what a
reader would reasonably assume, is that the bound PDF is what the committed
LaTeX source produces.

For at least one paper it demonstrably is not. At `a9ba2ead1`, with a clean
working tree, ORION-05:

| artifact | title | author |
|---|---|---|
| `manuscript/main.pdf` | Support-Two Normal Forms for a Shared-Tag Pauli Compilation Grammar | `Anonymous authors` |
| `manuscript/main.tex` | Support-Two Exactness and Regime Geometry of Shared-Tag TARE Compilation | `Working framework draft` |

A clean build today yields a **differently titled** manuscript with a
**placeholder author**. The PDF hash nonetheless matches `journal_package/MANIFEST.json`
`canonical_pdf` exactly, so the binding is internally consistent and the
divergence is invisible to every digest check in the repository.

## Author blocks across the frozen twelve, read from source

| source `\author{...}` | papers |
|---|---|
| `Working framework draft` | ORION-05, -06, -07, -08, -10, -12, -13, -16 |
| `ORION-P14` (internal identifier) | ORION-24 |
| `Anonymous authors` (correct for double-blind) | ORION-14, ORION-19 |
| no `manuscript/main.tex` | ORION-03 |

**Eight of twelve frozen papers would rebuild with a placeholder in the author
field.** ORION-16's source title is `Formal Epistemic Structures and Mechanics
--- V5`, an internal versioned string rather than a paper title.

## Why this matters more than it looks

A digest freeze answers "have these bytes changed?". It does not answer "can
these bytes be produced again?". For submission the second question is the
binding one: the moment any manuscript is corrected, the PDF must be rebuilt,
and the rebuild will not reproduce the frozen artifact. For ORION-05 it would
change the paper's title.

This is also why the ORION-14 rebind deadlock
(`evidence/rebind-deadlock-v1/`) matters beyond ORION-14: the automation that
would surface this divergence, by rebuilding and comparing, cannot currently run
to completion.

## What this addendum does and does not change

It does **not** invalidate the freeze. The digests are accurate and the release
classes stand.

It **qualifies** the freeze: `PUBLICATION_FREEZE_V1.json` is a byte freeze, not
a reproducibility claim. No paper in scope should be filed until its PDF has
been rebuilt from committed source with the canonical author block from
`papers/AUTHOR_IDENTITY_V1.json`, and the rebuilt title has been reconciled
against the frozen one.

`grants_authority: NONE`

**Terminal:** `FREEZE_IS_BYTE_ONLY__8_OF_12_REBUILD_WITH_PLACEHOLDER_AUTHOR`
