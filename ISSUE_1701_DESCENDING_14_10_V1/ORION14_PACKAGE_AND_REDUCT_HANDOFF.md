# ORION-14 package and reduct handoff

## Bounded paper

The mature closeout at `a5c5225f039a51809f81a015e1aa3fab80bd1c9e`
records a simulated TMLR-ready package, but its source and PDF hashes do not match
live `main`:

| object | closeout | live `main` |
|---|---:|---:|
| `manuscript/main.tex` | `9f78c4ec...` | `797ffcf9...` |
| manuscript PDF | `9dbf69d3...` | `f3395eb0...` |

Therefore the old PDF and anonymous archive are **not current filing bytes**.
The scientific terminal remains bounded; the release package must be reconciled
and rebuilt against live bytes before any upload.

## Optional reduct

The additive branch
`claude/orion14-promotion-reduct-20260828` at
`bee9829ae05fb317e1d381d50c64b7f7d2a430a2` is recovery-ready
path-by-path.

It did **not** recover the requested 400-case table. A repository-wide size and
content search found no such committed table, so the requested reduct remains
`CANNOT_CHECK_ARTIFACT_ABSENT`. On the distinct committed 10-case bench it finds:

- ternary `k* = 3`;
- two reducts;
- core `{known_composition, prior_art_found}`;
- collapsing `null` into `false` destroys all sufficient sets.

This partial result is useful because it shows that `CANNOT_CHECK` is
load-bearing. It is not the 400-case upgrade and it is not a submission blocker.
