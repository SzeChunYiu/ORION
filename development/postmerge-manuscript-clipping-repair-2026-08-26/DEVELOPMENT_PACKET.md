# Post-merge manuscript clipping and CI-startup repair — development packet

**Date:** 2026-08-26  
**Base subject:** `origin/main@ef51b7b9263a72c725dc9d2045627b934b772a92`  
**Authority ceiling:** engineering, rendering, citation-integrity and package-custody repair only; no novelty, superiority, external-review, acceptance or top-tier authority.

**Protocol timing:** the failing workflow runs, exact geometry findings, retained
reference metadata and superseded-package states were inspected before the
corresponding repairs. This packet was materialized in the same uncommitted
worktree before its first commit. It is not a scientific preregistration and
does not retrospectively grant authority to any manuscript result.

## Atomic development questions

1. Can the clipping gate distinguish visible layout defects from the small
   glyph-ink protrusion PyMuPDF reports for clean pdfTeX line boxes?
2. Can current working manuscripts be audited without overwriting or relabeling
   journal-package PDFs explicitly frozen as `SUPERSEDED` historical receipts?
3. Can source changes force a clean, pinned P1–P15 rebuild and exact tracked-PDF
   binding before merge, rather than auditing stale committed bytes?
4. Can genuine `OFF_PAGE` and material `OVERFULL` text be repaired without
   shrinking it into unreadability or changing scientific values, terminals,
   adverse results or authority boundaries?
5. Can the two zero-job workflows, whose target PR/issue events are already
   closed, be removed rather than revived to pollute every push?
6. Can the P2 static audit read every bibliography declared by `main.tex`, and
   can four author lists be reconciled with the already-retained primary arXiv
   metadata without changing donor disposition or novelty claims?

## Incumbent mechanics and negative history

- Main run `32934193833` audited 19 PDFs and reported 73 findings: 70 new,
  three accepted debt and 12 stale baseline entries. All 19 `OFF_PAGE`
  findings are visible clipping; the baseline is not an admissible repair.
- Pre-merge run `32899742421` had the same result, so PR #1330 did not create
  the layout debt. Later source changes nevertheless left tracked PDFs stale.
- P2 and P3 journal-package closure records explicitly say `SUPERSEDED`.
  Those bytes are historical custody evidence and must not be overwritten.
- Run `32934193804` failed because its inline audit read only
  `bibliography.bib` although `main.tex` declares two bibliography resources.
- Runs `32934192936` and `32934192281` failed before job creation because
  deindented Python triple-quoted content escaped YAML `run: |` blocks.
- PR #1026 is merged and issue #101 is closed; both branch-specific one-shot
  workflows have passed the event for which they existed.
- On 2026-08-26, CI run `32937277155` reopened the startup gate when toolchain
  verification expected a TeX package that the job had not explicitly
  installed. The repair explicitly installs and verifies that package without
  weakening any version pin.
- On 2026-08-26, CI run `32938157749` built P1--P14, then failed while building
  P15 because pdfTeX font expansion encountered a non-scalable font. Its P15
  log also exposed a `21.35846pt` overfull line containing the full artifact
  ZIP SHA-256.
  The partial build artifact's geometry audit independently exposed one
  borderline P7 page-1 line at `+4.0pt`.

### 2026-08-26 reopen resolutions

- Missing PyMuPDF is handled at import time as an explicit fail-closed
  `CANNOT_CHECK`, never as a silent pass.
- P7 now places the bold `Formal artifacts:` label on its own line before the
  two unchanged artifact paths.
- P15 now uses scalable Latin Modern fonts and applies `\seqsplit` to the exact
  unchanged artifact ZIP SHA-256 so the receipt remains readable without
  altering a byte of the identifier.
- These are toolchain and layout-only repairs. Run `32938157749` remains a
  negative receipt, and no successor CI run is claimed to have passed here.

## Bounded saturation assessment

Knowledge saturation is bounded to the exact failing workflow logs, the
geometry auditor, all affected PDFs and source lines, TeX logs, render-closure
records, retained P2 literature JSON, primary arXiv metadata, and existing
repository build/manifest tooling. No scientific donor or literature
saturation is claimed.

Search-universe saturation is limited to right-edge clipping, reproducible
source-to-PDF binding, active-versus-superseded PDF custody, YAML startup
validity, and P2 bibliography/resource metadata. Page design, venue formatting,
submission rights, reviewer access and external validation remain separate.

Formulation saturation is fail-closed: a green render gate proves only that the
selected exact PDFs built and contain no detected clipping. It cannot prove
scientific validity or submission readiness.

## Challenge to the saturation basis

The basis is false and must reopen if a clean pinned pdfTeX log reports an
overfull box below the chosen glyph-ink tolerance; if a package marked
`SUPERSEDED` is actually the registered current submission object; if any
affected terminal/hash/value changes during layout repair; if a CI rebuild is
not byte-reproducible; or if external primary metadata contradicts the retained
arXiv records used for P2.

## Miss hypotheses

1. Page-number-sensitive baselines made a rebuilt historical PDF look like new
   debt while simultaneously hiding the old location.
2. PR path filters watched PDFs but not TeX/Markdown/BibTeX sources, so
   `[skip ci]` source or derived-artifact updates bypassed the gate.
3. Text extraction preserved off-page characters, allowing content checks to
   pass while readers saw truncated hashes and terminals.
4. PyMuPDF glyph-ink bboxes extend a few points beyond valid TeX line boxes;
   treating every such extension as an overfull box creates false positives.
5. Inline multi-line Python strings were reviewed as Python but not as YAML
   indentation, so workflows failed before guards or branch filters applied.
6. A static audit hard-coded one `.bib` file instead of following the TeX
   declaration, masking both valid citations and incorrect author fields.

## Frozen implementation hypothesis

> If the gate clean-builds all 15 working manuscripts under a pinned pdfTeX
> environment, excludes only packages carrying an explicit `SUPERSEDED` state,
> tolerates at most four points of renderer-level glyph-ink protrusion, fails on
> every material or off-page finding, and requires tracked PDF bytes to equal
> the clean rebuild, then source/PDF drift and visible clipping will fail before
> merge without erasing historical custody evidence.

The YAML hypothesis is that deleting both obsolete, already-resolved one-shot
workflows eliminates their zero-job startup failures without reviving moving-ref
writeback behavior.
The P2 hypothesis is that parsing the union of TeX-declared bibliography files
produces 39 retained entries with zero missing citations or evidence records,
while primary-author correction changes citation integrity only.

## Frozen hostile tests

- a 3.3 pt glyph-ink protrusion beside eight 540 pt justified lines is ignored;
- a 12 pt margin overflow remains `OVERFULL` and a 73 pt extension remains
  `OFF_PAGE`;
- a superseded journal package is skipped while its working manuscript remains
  selected;
- missing or malformed current-PDF discovery fails `CANNOT_CHECK`;
- all remaining edited workflows pass `actionlint` and every embedded shell block passes
  `bash -n`;
- the two obsolete workflow files are absent; the exact P2 static-audit step reports two bibliography files, 39 entries and
  zero missing citations/metadata;
- local and CI geometry audits retain all adverse/null/`CANNOT_CHECK` text and
  show zero off-page findings;
- the clean CI rebuild must differ-fail until its exact PDF bytes are committed,
  then pass byte binding on the next run.

## Reopen triggers

Reopen on any nonzero clipping finding, stale baseline entry, unreadable PDF,
undefined citation/reference, action startup failure, clean-rebuild byte drift,
visual truncation, unreviewed scientific text change, manifest/checksum failure,
or newer external metadata conflict. Layout repair may issue a successor PDF;
it may not rewrite a frozen historical execution receipt or promote a bounded
result.
