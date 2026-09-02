# Venue packages predate the current science and the current attribution

**Status:** `VENUE_PACKAGES_ARE_A_2026-08-27_SNAPSHOT__DECISION_REQUIRED`
**Date:** 2026-09-02
**Scientific authority delta:** `NONE`. This records a fact about the packages
and names the decision it forces. It promotes nothing and changes no manuscript.

## The fact

All three venue manuscripts were last touched on **2026-08-27**. Their working
manuscripts were last touched **2026-09-02**.

| paper | venue manuscript | last touched | working manuscript | last touched |
|---|---|---|---|---|
| ORION-16 | `submission/AIJ_MANUSCRIPT.tex` | 2026-08-27 | `manuscript/FINAL_V6.md` | 2026-09-02 |
| ORION-17 | `submission/AIJ_MANUSCRIPT.tex` | 2026-08-27 | `manuscript/FINAL_V5.md` | 2026-09-02 |
| ORION-18 | `submission/JAAMAS_MANUSCRIPT.tex` | 2026-08-27 | `manuscript/FINAL_V5.md` | 2026-09-02 |

The `submission/publication-ready-20260831/` PDF packages carry the same date in
their own directory name.

## What that snapshot excludes

Everything the donor-subtraction and surface work produced since:

- **The classical attribution.** Neither AIJ package nor the JAAMAS package cites
  any of the ~70 parent works named by `A6_DONOR_MATRIX_V2/V3/V4`, ORION-17's
  `DONOR_MATRIX_V1` or `COMPOSITION_LAW_PARENT_FINDING_V1`. That is why the
  ledgers added in #2111 and #2112 exist: the packages predate the results that
  identified those parents.
- **The adopted manuscripts.** `FINAL_V6` (ORION-16), `FINAL_V5` (ORION-17) and
  `FINAL_V5` (ORION-18) were all adopted after the snapshot.
- **The corrections.** ORION-18's abstract state-count fix (#2109) and ORION-22's
  duplicated passages (#2110) landed after it.

## They are also a different scope, not merely an older draft

This is the part that matters most, and it is easy to misread as staleness.

ORION-18's JAAMAS manuscript is built on **five scientific effect domains**: it
reports 25 source/target combinations, 160 shared-calculus versus ideal-product
equivalence cases, and a 17-case authority manifest. The working manuscript's X4
model is built on **thirteen donor families**: 3,072 distinct authority states,
39,936 evaluations, 169 ordered-chain compositions. These are different
enumerations, not the same result at two levels of detail.

ORION-16's venue manuscript carries **no quantitative result numbers in its body
at all**, while its working manuscript reports 155 full restorations, 1,055
proper-subset failures, and a 130,320-case enumeration.

Each package is **internally consistent about its own scope**. Nothing here says
they are wrong.

## The decision this forces

Submitting from `publication-ready-20260831` submits the **August result with the
August attribution**. That may be the right call — a smaller, fully frozen claim
is a legitimate thing to submit, and the packages are coherent. But it should be
a decision rather than a default, because two of its consequences are not
obvious:

1. the submitted paper would not contain the classical donor citations, so a
   reviewer would see it positioned almost entirely against work from its own
   year, and
2. the submitted result would be the smaller enumeration, while the repository's
   current science is the larger one.

The alternative is regenerating the venue packages from the current manuscripts,
which is a manuscript task, not a mechanical one: the `.tex` files are bound in
`CONTENT_MANIFEST_V1` and `SHA256SUMS`, so it means adopting successors, and the
larger enumeration would need its own venue-shaped presentation rather than a
paste of the working text.

## What this document does not claim

It does not claim the packages are defective, that the snapshot is wrong, or that
either route is better. It records that the two diverge, by how much, and since
when — so the choice is made deliberately.

Verified by comparing the last commit touching each file and the distinct
quantitative content of each body, excluding bibliographies and years.
