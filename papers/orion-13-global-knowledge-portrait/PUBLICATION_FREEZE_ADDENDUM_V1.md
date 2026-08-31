# ORION-13 publication-freeze addendum V1

**Freeze date:** 2026-08-31  
**Status:** `CURRENT_EARNED_CEILING_FROZEN__EXTERNAL_SEMANTIC_JUDGMENT_SUCCESSOR_ONLY`

This addendum is part of the frozen ORION-13 paper-content packet. It records the
ceiling the paper's readiness record and checkers already establish, and grants no
authority beyond them.

## Earned scientific ceiling

The submission terminal is `READY_TO_SUBMIT_SECOND_TIER`, target Semantic Web
Journal with the Journal of Web Semantics as fallback.

The canonical manuscript is the LaTeX tree `manuscript/`, designated in
`submission/CANONICAL_SOURCE_DECISION.md`. It compiles to 45 pages with 0 undefined
references and 0 overfull boxes. `check_bounded_publication_track.py` reports
`P3_BOUNDED_PUBLICATION_TRACK: PASS`, `tests/test_paper_manuscript_integrity.py`
passes with the three-valued boundary surviving in both abstract and conclusion, and
`tests/test_journal_package_render_closure.py` passes across 9 tests. The audited
claim delta is `scientific_authority_delta = NONE`.

## Frozen boundary

The readiness record carries **one condition that is verifiable but not verifiable
by the paper itself**, and this freeze restates it rather than resolving it. On the
submitting branch every ORION-13-specific CI step passed — claim wiring and
manuscript inputs, tracked package checksums, canonical PDF compile, and rebuild
versus superseded historical package authority. The job failed only at its final
cross-paper step, which validates the P1–P5 package inventory across all five papers
and fails on a `hash mismatch for manuscript/main.tex` in P1, which is ORION-11.
That failure is inherited from another lane and is not ORION-13's to fix.

The package invariants the CI asserts still hold: status `SUPERSEDED`, submission not
authorized, historical PDF role unchanged, binding status unchanged. Content binding
is `BOUND_PARTIAL / PASS`.

Where true semantic judgment exceeds machine-readable metadata, the paper marks the
outcome undetermined rather than self-labelling it. A study whose gold comes from an
external semantic authority rather than from stable identifiers and declared
relations is successor work, and must not retroactively promote the present bounded
mapping result.

## Frozen content surface

The content packet consists of the canonical LaTeX tree named above,
`check_bounded_publication_track.py` and the two passing test modules, the journal
package with its render closure, the submission directory (venue decision, manifest,
cover letter, availability statement), and this addendum. The ORION-13 claim is about
scientific identity authority for recoverable cross-domain integration; it does not
own the vocabularies it maps between.
