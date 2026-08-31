# ORION-08's source archive cannot be built from its current build input

**Terminal:** `SOURCE_ARCHIVE_BLOCKED__BUILD_INPUT_PREDATES_MANUSCRIPT`

## The intended step

`submission_tmlr/build_tmlr_source.py` takes `--cited-master <markdown>` and produces the TMLR source form. Assembling the missing source archive looks like a matter of running it.

## Why it must not be run as-is

The Markdown masters are stale relative to the LaTeX the paper actually renders from.

| source | last commit | carries this session's edits |
|---|---|---|
| `manuscript/main.tex` + `sections/*.tex` | 2026-08-30 | yes |
| `MANUSCRIPT_V3_REFINED.md`, `MANUSCRIPT_TYPED_SCOPED_SYNTHESIS_*.md`, `MANUSCRIPT_V3.md`, `MANUSCRIPT_V2.md` | 2026-08-27 | **no** |

The LaTeX carries two changes the Markdown does not: the Kubyshkina and Petrolo citation with its positioning paragraph, and the removal of the internal identifiers `Q2` and `Q4` from the introduction and related-work sections.

Running the build against any current Markdown master would therefore produce a source archive that

1. omits a reference the manuscript cites, and
2. **re-introduces internal catalogue codes into a double-blind submission**, undoing a repair already merged.

The archive would also disagree with the compiled PDF, which is the ORION-05 failure shape in a new place: two artifacts of the same paper stating different things, with nothing marking which is authoritative.

## There are four candidate masters and no record of which is canonical

`MANUSCRIPT_V2.md`, `MANUSCRIPT_V3.md`, `MANUSCRIPT_V3_REFINED.md` and `MANUSCRIPT_TYPED_SCOPED_SYNTHESIS_2026-08-23.md` all sit at the paper root. Nothing in `REPRODUCE.md` or the package names which is the cited master. Choosing one by filename plausibility is the kind of guess that produces a confidently wrong artifact.

## What would unblock it

Either regenerate the Markdown master from the current LaTeX, or retarget the build at the LaTeX directly. Both are real changes to the build path, not a parameter choice. Until one is made, ORION-08's package can hold a cover letter, an availability statement and a compiled PDF, but not a source archive that faithfully represents the manuscript.

## Note

This was caught before running the build rather than after merging its output. The check cost one command comparing commit dates and one grep for a citation key.
