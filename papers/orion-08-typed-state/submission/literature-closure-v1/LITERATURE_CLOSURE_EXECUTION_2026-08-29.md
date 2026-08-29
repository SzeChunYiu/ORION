# ORION-08 — execution of the 2026-08-29 literature-gate repairs

**Predecessor:** `LITERATURE_CLOSURE_2026-08-29.md`  
**Terminal:** `LITERATURE_CLOSURE_COMPLETE__V4_AND_MANUSCRIPT_BOUNDARY_UPDATED`  
**Scientific authority delta:** `NONE`

The predecessor pass correctly returned
`LITERATURE_CLOSURE_INCOMPLETE__MATRIX_SUPERSEDED`: it found a new nearest
parent and listed four concrete repairs required before submission. This note
records execution of those repairs. It does not rewrite the predecessor
terminal; it supersedes it after the requested changes are present.

## Repair checklist

1. **Nearest-work matrix V4: DONE.** `NEAREST_WORK_MATRIX_V4.md` is now the
   current matrix. V3 remains provenance. V4 includes arXiv:2608.25553,
   2605.06527, 2608.10509, 2607.20827, 2606.22528, and 2604.20911.
2. **Matched-budget/random-control priority claim removed: DONE.** V4 states
   explicitly that matched-budget verification and random-record controls are
   not ORION-08 novelty claims. The residual object is exact binding
   sufficiency and mechanism isolation.
3. **Manuscript boundary updated: DONE.**
   `manuscript/sections/05-related-work-boundary.tex` now distinguishes exact
   decision-sufficiency from sampled empirical rates and mechanism isolation
   from the nearest parent's measured behavioral consequence. It also names
   the recent stale-memory, provenance, and governance neighbors.
4. **Legacy ORION-04 matrix identity removed from the current surface: DONE.**
   V4 is headed ORION-08, and `README.md` points to V4. V3 is retained only as
   historical provenance.

The manuscript bibliography now contains all six V4 references.

### Version-label correction

The predecessor described the nearest parent as `arXiv:2608.25553v2 (2026-08-27)`.
The live arXiv record checked on 2026-08-29 exposes **v1, submitted 2026-08-26**.
V4 and the bibliography therefore cite the stable unversioned identifier
`arXiv:2608.25553` and do not carry the predecessor's version/date label forward.
This is bibliographic correction only; none of the comparison or claim-boundary
logic depends on the version suffix.

## Resulting claim boundary

The bounded literature claim is now:

> Recent work owns several neighboring primitives and controls: stale-memory
> revision, provenance-sensitive action, typed provenance graphs, long-context
> governance decay, and matched-budget verification with random-record
> controls. ORION-08 does not claim priority on those. Its residual bounded
> contribution is the exact fibre-based decision-sufficiency/mechanism object
> instantiated across six separately frozen exact-synthetic studies.

The independent transfer note remains deliberately weaker than a re-analysis.
Its episode-level fibre mapping is a falsifier/optional strengthening step, not
a prerequisite for this bounded literature gate.

## Remaining non-literature work

Editing the LaTeX source and bibliography necessarily makes the previously
byte-pinned `manuscript/main.pdf` stale under the repository's deterministic
render gate. A canonical CI rebuild/re-import is therefore required before
filing. That is a render-integrity step, not unresolved literature science.

Venue-specific figure/table selection and permanent archival requirements also
remain separate submission mechanics.

No experimental result, threshold, terminal, or external-validity claim changes
in this closure.
