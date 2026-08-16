# Individually-green PRs, red main (stale pre-merge CI)

**Observed:** three times on 2026-08-15/16, in one session.

| # | PRs merged | Result |
|---|---|---|
| 1 | #22 into a main carrying the kernel | 17 kernel tests failed, zero overlapping files |
| 2 | #30 | grade/apply disagreement (fixed in-PR) |
| 3 | #36 + #37 | 4 failures, **including #36's own new tests** |

## Mechanism

`.github/workflows/ci.yml` runs `on: pull_request`, which tests the merge commit
**as of the moment CI ran**. `main` is unprotected
(`repos/SzeChunYiu/ORION/branches/main/protection` → 404), so nothing requires a
branch to be current with `main` before merging. When `main` advances after a
PR's CI completes, that green result is stale — and merging is still permitted.

So each PR was green against a `main` that no longer existed. The merge produced
a combination **no CI run had ever evaluated**.

## Failure class

`STALE_PREMERGE_VERIFICATION`. Not a conflict: git had nothing to report in any
of the three cases, and in incident 1 the two changes shared no files at all.
The collision is semantic — two lanes evaluating the same contract against
different effective states, with the optimistic evaluation reported.

This is the same class as `GRADE_APPLY_DISAGREEMENT`
(`research/failures/2026-08-graded-but-unapplied-verification/`), one level up:
there, two subsystems disagreed about a record's effective state; here, two
lanes disagree about the repository's.

## What did work

Merge, then immediately re-run the full suite on the updated `main` and fix
forward. Applied 3/3 times, each repaired within one commit. It works because
the window is short and one lane is watching.

## What was deliberately not done

Enabling branch protection with strict (up-to-date-required) status checks would
close the hole mechanically. It was **not** enabled, because with two or more
lanes pushing frequently it forces a rebase on every PR whenever `main` moves,
which can deadlock progress more expensively than the failure it prevents. That
is a governance trade-off for the operator, not a lane decision, and it is
recorded here rather than taken silently.

## Guard

Any lane merging another lane's PR must re-run the full suite on the updated
`main` **immediately**, before starting new work, and fix forward in the same
work window. A green PR check is evidence about a `main` that may no longer
exist.

Corollary for reviewers of this repository: when a PR's tests fail after merge,
check whether the PR's own new tests fail too. In incident 3 they did, which
localizes the fault to a stale expectation rather than to the change under
review — in that case two attacking predicates that rejected their own positive
fixtures, so the attacks they demonstrated never ran.
