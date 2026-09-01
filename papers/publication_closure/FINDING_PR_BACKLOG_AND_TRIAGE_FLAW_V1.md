# The open-PR backlog, and why the first triage of it was wrong

## The backlog

**Twenty pull requests are open**, totalling roughly seventy thousand added lines --- more paper work than this session produced.

| PR | added | subject |
|---|---|---|
| #1691 | 11,996 | ORION-23/24 pilot-target live-Git acquisition |
| #1815 | 7,374 | applies `academic-paper-skills` across 23 bounded paper objects (draft) |
| #1853 | 6,988 | top-tier refinement across ORION-01–25 |
| #1679 | 4,468 | Wave 3 close-out, three papers |
| #1702 | 4,419 | recover ORION-09/10/13/15 |
| #1709 | 3,958 | close ORION-25 and descend |
| #1692 | 3,716 | Wave 1 upgrade: ORION-14/16/17/19/23 |
| #1704 | 3,649 | ORION-01 bounded Paper 1 freeze |
| #1760 | 3,236 | top-tier science-gap closure |
| #1693 | 2,483 | **Wave 1 submission lane: ORION-05/06/07/08/09/10/12** |

An earlier report in this session said seven. That figure came from `gh pr list --limit 10` and was a truncation read as a total.

## The triage was not reliable

Each branch was checked with `git merge-tree ... | grep -c '^<<<<<<<'` and all fifteen tested returned **zero conflicts**. That check counts **text conflict markers only**. It does not report binary conflicts.

Merging #1702 for real produces a **binary conflict** on `papers/orion-11-recursive-epistemic-reconstruction/manuscript/main.pdf`. Every one of these branches is 118–258 commits behind main, and the papers carry committed PDFs, so binary conflicts on rendered artifacts should be expected as the normal case rather than the exception.

## A worse error in the same pass

The real merge was run as:

```
git merge --no-edit -q FETCH_HEAD 2>&1 | head -2
echo "merged $b; files vs main: $(git diff --name-only origin/main..HEAD | wc -l)"
```

Piping through `head` discards the exit status, and the `merged` message is printed unconditionally. The merge conflicted and never committed, so `HEAD` still pointed at main, the diff was legitimately zero, and the branch pushed for testing was **byte-identical to main**. The suite then returned 1186 passed --- a true statement about main and no evidence at all about the merge.

The same mistake occurred twice in one sitting: once merging #1854 and #1885 together, once on #1702. Both times a conflicted merge was reported as successful and the resulting green run was read as validation.

## What a correct check requires

- test `git merge` by exit status, not by piped output;
- confirm the merge commit actually advanced `HEAD` past main;
- verify a file unique to the branch is present after merging;
- treat committed PDFs as expected binary conflicts on any branch this far behind.

## Consequence

No claim about which of these twenty branches is mergeable currently stands. The backlog is real and large, and re-triaging it needs the checks above. #1815 remains the one whose blocking reason is established by measurement rather than assumption: it merges textually clean and then fails ten binding-coverage tests, one of them on freeze-blocked ORION-16.
