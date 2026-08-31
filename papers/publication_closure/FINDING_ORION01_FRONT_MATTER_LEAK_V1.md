# ORION-01 prints internal provenance and a tooling commit hash on page one

**Severity:** highest front-matter leak found in this corpus.

## What both PDFs render

`journal_package_A/main.pdf`:

```
Alphabet-Davenport Normal Forms for Multi-Tag Quantum Compilation
Paper A --- hardened manuscript V2
Scientific cut: Paper-A/A1 parents plus R2 theorem package
Workflow cut: academic-paper-skills@188e83e639571c435344630ae68fdc66072650d2
```

`journal_package_B/main.pdf` renders the same shape with `Paper B` and its own parent list.

Three distinct classes in four lines: an internal paper label with a version (`Paper A --- hardened manuscript V2`), internal provenance naming parent artifacts (`Paper-A/A1 parents plus R2 theorem package`), and **a git commit hash of the authoring tooling repository**. The last is the sharpest: it publishes an identifier of internal infrastructure in the first thing a reviewer reads.

## Corrections to the recorded status

Two records disagree with the tree.

- The readiness table entry for ORION-01 reads *no LaTeX source, cannot be built or edited at all*. The paper has no `.tex`, which is true, but it has two Markdown master manuscripts, two journal packages, and **two compiled PDFs**. "Cannot be built" is wrong.
- `JOURNAL_PACKAGE_STATUS_V1.md` records `Current PDF exists: OPEN --- no PDF` for both papers. The PDFs were added on 2026-08-29; that document was last committed 2026-08-28. The status document is stale, not the tree.

ORION-01 is a `SPLIT_TWO_THEORY_PAPERS` lane: Paper A on Alphabet-Davenport normal forms, Paper B on exact certificate complexity versus intrinsic support.

## The fix is feasible, and it is not a one-line edit

The banner is in `journal_package_{A,B}/SOURCE.md` and in the master manuscripts `theory-{A,B}-MANUSCRIPT_V2.md`. Four constraints bind the change:

1. `verify_package.py` binds `SOURCE.md` to the master manuscript **by sha256**. Editing either without the other, or without updating the recorded digest, fails the verifier.
2. Two test files reference this paper: `tests/unit/publication/test_five_theory_hardening_r2.py` and `test_five_theory_publication_wave.py`.
3. Neither `pandoc` nor `pdflatex` is installed on the test host, so the PDF cannot be rebuilt there.
4. `.github/workflows/orion01-v3-bounded-package.yml` does carry build steps and is `workflow_dispatch`, so a rebuild path exists in CI.

Editing the source without rebuilding would leave the PDFs still printing the banner while the source no longer contains it --- the ORION-05 divergence shape, and the exact failure this corpus already has a guard against.

## Why this was not attempted in the same pass as its discovery

The change touches a hash binding, two master documents, two packages, two tests, and a CI render. Two main breakages earlier in this session came from multi-step binding changes made immediately after finding the problem. The path above is verified; executing it is a separate piece of work.
