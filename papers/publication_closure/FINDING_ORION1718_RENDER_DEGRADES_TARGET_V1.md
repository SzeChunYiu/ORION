# Re-rendering ORION-17/18 degrades a reproducibility target

**Terminal:** `SELFREF_REMOVAL_BLOCKED__RENDER_DEGRADES_REPRODUCIBILITY_TARGET`

## The defect that cannot currently be fixed

ORION-17 and ORION-18 refer to themselves by catalogue number in rendered body text:

- `P7 shipped no such registry`
- `\section{Wider P7 claim (V4 wording)}`
- `P8 reuses evidence-backed permission graphs`
- `P8 therefore does not claim novelty merely for...`
- `\section{Wider P8 claim}`

The same class was repaired in ORION-06, -07, -08, -10 and -15.

## Why the obvious fix does not land

Editing the section files is safe on its own. Measured directly:

| state | result |
|---|---|
| source edited, **not** re-rendered | **1186 passed** |
| same edit, **after** re-render | **3 failed** |

The failure is `test_current_tree_is_classified_target_by_target[P7]` and `[P8]`, with one target moving `BOUND` to `PARTIAL` (`BOUND: 8` becomes `BOUND: 7, PARTIAL: 1`). The tests pass before the render workflow commits and fail after it.

**So the render, not the edit, is what degrades the target.** This is the same mechanism that turned main red at `c43863fc4` earlier, which was misdiagnosed at the time as a consequence of removing the internal overlay. The overlay removal did remove a needed declaration --- that repair in #1905 was correct and its declaration is still intact --- but it was not the whole cause. Re-rendering these two papers degrades a target regardless of what changed in the source.

## The false lead, recorded so it is not repeated

`main.tex` for both papers opens with a comment `% P7 manuscript entry point`. Excluding `main.tex` from the substitution and editing only `sections/*.tex` made the suite pass, which looked like a clean root cause: the checker keys on a comment marker. It was an artifact. That run had not yet been re-rendered. Once the render ran against the identical source, the same three tests failed. A passing suite immediately after a source-only change says nothing about a paper whose targets depend on its PDF.

## Consequence

Two mutually exclusive options, neither available without a decision:

1. **Re-render and accept the target regression** --- trades a reproducibility target for a surface repair.
2. **Fix the source and do not re-render** --- leaves source and PDF divergent, which is exactly the ORION-05 state that a curated PDF creates deliberately and that is a defect anywhere else.

Neither is an implementer's call. The branch carrying the repair is not merged, and both papers remain unchanged on main rather than half-fixed.

## What would resolve it

Identifying the specific target and why it is PDF-sensitive. The derived manifest could not be read on the test host --- `derive_manifest` there returns `9 CANNOT_CHECK + 1 BOUND` against a test expectation of `BOUND: 8, CANNOT_CHECK: 1, DEFERRED: 1`, because git metadata is unavailable in that context and the checker falls back to `CANNOT_CHECK`. Diagnosing further needs a host where the checker can resolve git state.
