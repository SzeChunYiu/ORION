# Prior attribution for ORION-16 and ORION-18 — written, verified, not yet adopted

**Status:** `PROPOSED_SUCCESSOR_MANUSCRIPTS__ADOPTION_REQUIRES_A_DELIBERATE_FREEZE_LIFT`
**Scientific authority delta:** `NONE`. No theorem, premise, bound or count is altered by
anything here.

## The defect

Neither manuscript contains a single citation. Measured, not estimated: across
`FINAL_V5.md` (ORION-16) and `FINAL_V3.md` (ORION-18) there are **zero** author–year
references, **zero** numbered references and **zero** DOIs.

For two formal papers this is submission-fatal on its own. It is worse than that here,
because the results are inherited. The donor subtraction in this directory's sibling
documents marks every one of the fifteen results across the two formal cores `DONOR` or
`SPECIALIZATION`, with none surviving. A formal paper whose every theorem is owned by an
established field, and which names none of those fields, cannot be sent to a referee.

ORION-18 is the less severe of the two: it has a *Donor-engulfment architecture* section
that attributes honestly to mechanism classes — "proof-carrying actions", "typed verifier
certificates", "principal-chain composition with bounded scope". What it does not do is name
a single source, so a reader cannot check any of it.

## What is here

| file | what it is |
|---|---|
| `ORION16_FINAL_V6_PROPOSED.md` | `FINAL_V5.md` plus a *Relation to prior work* section |
| `ORION18_FINAL_V4_PROPOSED.md` | `FINAL_V3.md` plus *Named sources for the donor mechanisms* |
| `../../candidates/CANONICAL_BIBLIOGRAPHY_V3_ADDENDUM.md` | entries 40–46, the sources the new text cites |

Each proposed successor changes its base in exactly one respect and says so in its own
header. No theorem, premise, boundary, envelope, bound or count is touched.

## Why they are here and not in `manuscript/`

Both paper directories are **frozen closed**. `CONTENT_MANIFEST_V1.json` for each is itself
digest-pinned by `test_frozen_v1_manifests_were_not_rewritten`, and the V1 binding check
requires `SHA256SUMS` and `bound_files` to cover every file in the paper. Adding a file to
`manuscript/` therefore fails two ways at once, and the manifest that would have to be
extended is the one that may not be rewritten.

That is the freeze working correctly, not a defect. Writing the successors into the frozen
directory and rebinding around the complaint would have been the same error as re-signing a
sealed manifest after its reveal: it would make the check green and destroy what the check
is for.

**Adoption is therefore an operator decision.** Lifting the V1 freeze for these two papers,
promoting the proposed files to `manuscript/FINAL_V6.md` and `manuscript/FINAL_V4.md`, and
rebinding is a deliberate act with a clear before and after. It is not something to slip in
alongside a prose edit.

## What was verified, and what was not

Every citation was checked against a primary or publisher record on 2026-09-01 rather than
recalled; the addendum carries the per-entry provenance table. One field is deliberately
missing — entry 41's volume and page range were not confirmed and are omitted rather than
reconstructed.

One donor is deliberately absent. Assurance-case notation is a plausible source for the
three-state blocker treatment, and it is not cited, because no primary record for it was
checked. An unverified citation would be worse than a missing one.

## What this does not do

It does not make either paper submittable. It removes one blocker of several, and the
subtraction result stands: read as separate theorems, nothing in either formal core
survives donor substitution. The contribution that remains is the composition, and the
proposed ORION-16 text says so in those words rather than implying more.
