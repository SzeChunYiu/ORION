# ORION-01: correcting the front-matter finding

The previous record (`FINDING_ORION01_FRONT_MATTER_LEAK_V1.md`) called the V2 banner the highest-severity leak in the corpus. That judgement was made without establishing which generation is current, and it is wrong in two directions.

## What is actually true

ORION-01 has two generations:

| generation | location | front-matter banner |
|---|---|---|
| V2 | `theory-{A,B}-MANUSCRIPT_V2.md`, `journal_package_{A,B}/` | `Paper A --- hardened manuscript V2`, `Scientific cut:`, `Workflow cut: academic-paper-skills@188e83e6...` |
| **V3 (current)** | `v3-bounded-closeout-2026-08-29/` | `ORION-01 Paper A --- bounded manuscript V3`, `Status: candidate successor...` |

**Both leak.** V2 leaks a tooling commit hash; V3 leaks the catalogue number `ORION-01` and its own version label. Removing the V2 banner, as done in the preceding change, addressed the superseded generation. The current generation was not touched, and still carries a banner.

## The decisive line, which changes the paper's status

V3's front matter states:

> Status: candidate successor to the frozen V2 text; no external review or submission authority claimed

**ORION-01 disclaims submission authority in its own rendered front matter.** It is not a packaging-gap paper. Like ORION-22's enforced `top_tier_submission_allowed: false`, its status is declared in the artifact rather than inferable from its completeness.

Neither V3 PDF carries an author line.

## Three probe failures in one investigation

1. `.github/workflows/orion01-v3-bounded-package.yml` was counted as having "3 build steps" by grepping for `pandoc|pdflatex|build.sh`. That count says a build exists; it does not say **what** is built. The workflow builds V3, not the V2 files that were edited.
2. The workflow was dispatched and returned success. Success meant *the V3 artifacts already match* --- it committed nothing. A green run was read as evidence the rebuild had happened.
3. V3 was then checked for a banner by grepping `hardened manuscript|Workflow cut|Scientific cut` and reported **clean**. V3's banner says `bounded manuscript`. The probe was built from V2's wording and could not see V3's.

Each failure has the same shape: a check derived from what was already believed, rather than from reading the artifact.

## Disposition

The V2 de-bannering stands --- it is a real removal from a real file, all bindings reconciled, 1186 tests passing. It is simply less important than claimed. The V3 banner and the missing author line remain, and the submission-authority disclaimer means neither is the paper's binding constraint.
