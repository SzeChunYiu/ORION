# What the V1 freeze currently costs, measured

The frozen-manifest question was first raised for ORION-16, where a title suffix and a placeholder author could not be repaired. That framing understated it. The freeze blocks repairs in **abstracts**, on papers whose science is closed.

## Blocked defects, in the papers' own first pages

Extracted from the rendered PDFs, so this is what a reviewer reads:

| paper | first-page text | defect |
|---|---|---|
| ORION-21 | `ORION-21 does not claim that representation ...` | refers to itself by catalogue number |
| ORION-22 | `ORION-22 asks: Under one matched total budget ...` | same |
| ORION-23 | `ORION-23 asks: Can a compact state carry a ...` | same |
| ORION-20 | `... negative P9/P10 and ORION-Q results remain immutable` | internal codes and programme name |
| ORION-16 | `--- V5` in title; `Working framework draft` as author | version label and placeholder author |

All five bind `manuscript/main.tex` in a frozen `CONTENT_MANIFEST_V1.json` with `subject_commit_status: BOUND`, so the file cannot be edited by any supported route. The checker refuses regeneration outright: *"frozen CONTENT_MANIFEST_V1.json no longer describes the V1 subject; bind additive files in CONTENT_MANIFEST_V2.json"* — and an abstract edit is a modification, not an addition, so V2 offers no path either.

## What is not blocked

The equivalent defects in ORION-06, -07, -10, -15, -17 and -18 were repaired precisely because those papers are editable. The same class of defect is fixable in half the corpus and unfixable in the other half, decided entirely by binding state rather than by anything about the papers.

## Why this is not a cosmetic complaint

A paper whose abstract opens `ORION-22 asks:` is not submittable as it stands. The abstract is the most-read text in a submission and often the only text a desk editor reads in full. The freeze is therefore not merely preserving history on these five papers; it is holding them at a state that cannot be submitted.

## The decision this needs

Three options, none of which an implementer should choose unilaterally:

1. **Amend freeze policy** to permit a narrow manuscript-surface class — title, author block, abstract wording — with an auditable record of each change, leaving scientific content frozen.
2. **Render submissions from an unbound source**, keeping the frozen tree as the historical record and treating the submission copy as a derived artifact.
3. **Accept the defects** and do not submit these five.

Option 3 is the current de-facto state. Nothing here argues the freeze is wrong: it is behaving exactly as designed, and that design is what makes the historical record trustworthy. The point is only that its cost is now measurable, and it is five papers rather than one.
