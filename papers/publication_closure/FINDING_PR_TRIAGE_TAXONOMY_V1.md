# Triaging the PR backlog: four outcomes, and which are safe

Merging branches from this backlog sorts into four kinds. The distinction that matters is **which conflicts can be resolved mechanically and which need a human judgement about content**.

## The four outcomes

| outcome | test | action |
|---|---|---|
| **already landed** | merges clean, **zero net files** | close; content is on `main` |
| **clean with content** | merges clean, net files > 0, suite green | land |
| **`UA` conflicts only** | every conflict is *added by them*, and the paths are absent from `main` **and** from `main`'s deletion history | resolve by taking theirs; this adds files rather than resurrecting deleted ones |
| **`UU` / `AA` conflicts** | both sides modified the same file, or both added it with different content | needs a content decision per file; not mechanical |

## Applied so far

Landed: #1686 (ORION-25 chapters), #1691, #1679, #1375, #1298 (five arXiv packages), #1596.

Closed as already landed, zero net files: #1652, #1694, #1588, #1605, #1627, #1624.

`UU`/`AA`, unresolved: **#1693** (19 `UU` + 2 `AA`; the ORION-05/06/07/08/09/10/12 submission lane), **#1692** (11 `UU`), #1702, #1709, #1704, #1760, #1613, #1486, #1381, #1853.

Blocked on a frozen binding: **#1815** — merges textually clean, then fails binding-coverage on freeze-blocked ORION-16.

## Why the `UA` case is safe and the others are not

`UA` means the path does not exist on the merge base or on `main`, and the branch adds it. Taking the branch's version cannot overwrite a decision made on `main`, because `main` never expressed one. That is what made #1298's seventy-two conflicts resolvable in one pass --- but only after checking that the paths were absent from `main`'s deletion history, since a path `main` had **deliberately removed** would present the same way and taking theirs would silently revert the removal.

`UU` and `AA` are the opposite: both sides wrote the file. Resolving them requires reading both versions and deciding which claim is correct --- exactly the judgement that produced the ORION-14 availability decision, where the branch's wording was better than `main`'s and `main`'s carried a typo.

## Rate

Six branches landed and six closed out of roughly 120. The remainder is dominated by `UU`/`AA` cases, which do not batch. The largest of them, #1693, is a submission lane for seven papers.
