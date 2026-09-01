# Four long-lived pull requests: superseded, and merging them would revert main

**Status:** `TRIAGED_AGAINST_MAIN__RECOMMEND_CLOSE_AS_SUPERSEDED`
**Scientific authority delta:** `NONE`. This is queue hygiene, not a scientific result.

Of the sixty open pull requests, thirty-eight are on codex-lane branches and thirty-four of
those are drafts. The four non-draft ones are all far behind and all `CONFLICTING`:

| PR | opened | commits behind main | mergeable |
|---|---|---|---|
| #1760 | 2026-08-29 | 341 | CONFLICTING |
| #1704 | 2026-08-28 | 373 | CONFLICTING |
| #1613 | 2026-08-28 | 501 | CONFLICTING |
| #1602 | 2026-08-28 | 510 | CONFLICTING |

Their CI is red, and that red is misleading. The six failures they share
(`test_p1_tables_check_mode`, `test_p3_confirmatory_receipt`,
`test_mechanical_arm_record_supersession`, `test_p5_metric_supersession`) were measured on
2026-08-28 against a main that has since been repaired. Run against today's `main` in a
clean worktree: **20 passed.** Nothing is wrong with the code those runs were testing.

## What is actually in them

File-by-file against `origin/main`:

| PR | files | already on main | not on main |
|---|---:|---:|---|
| #1760 | 21 | 21 | — |
| #1704 | 36 | 34 | two one-off transplant/cleanup workflows |
| #1613 | 67 | 65 | `manuscript.pdf` and one history PDF |
| #1602 | 63 | 63 | — |

File existence is not content equality, and checking only the former would have given the
wrong answer. At blob level:

- **#1760** — 20 of 21 byte-identical; `validate_science_gap_register.py` differs.
- **#1602** — 60 of 63 byte-identical; three ORION-01 registry files differ.

## The differences run the wrong way

For every differing file, **main is ahead of the pull request**, and the delta is main's.

`validate_science_gap_register.py` on main is #1760's version plus a widening committed on
2026-08-29 that adds eight boundary tokens, with a comment recording that ORION-05 and
ORION-09 stated genuine limits without containing a literal "not", that 23 of 25 registered
boundaries already passed, and that no token was removed. Merging #1760 would delete that.

#1602's three files were last touched on `main` on **2026-09-01** — four days after the pull
request — by *"ci: scope ORION-01 custody to replay dependencies"*, and the diffs going
PR → main are net-additive (+25/−8, +8/−2, +4/−0).

#1613's two missing files are PDFs, and ORION-14's journal package now renders its PDF in
CI: `journal_package/history/SHA256SUMS_PRE_CI_RENDER_2026-09-01.txt` records that change.

## Recommendation

**Close all four as superseded.** They carry nothing main lacks, and the three of them with
a real delta carry an *older* version of it, so merging would revert work landed since. A
rebase would be expensive and would produce an empty change.

The one thing worth extracting first is #1704's two workflows,
`transplant-orion01-pr1602-evidence.yml` and `cleanup-accidental-ignore-issue.yml`. They
are scaffolding for a transplant that has already happened, so they are probably also spent,
but that is a judgement about intent rather than about content and it is left to whoever
wrote them.

## Why this was worth doing

A red, conflicting, months-behind pull request looks like unfinished work. These four look
like four outstanding tasks on a board that is trying to reach zero. They are not tasks.
Three of them are traps: a reviewer who resolved the conflicts in the PR's favour would
quietly undo a boundary-token widening and a CI custody fix.
