# The open-PR backlog is 120, and three earlier counts of it were wrong

## The number

```
gh api "search/issues?q=repo:SzeChunYiu/ORION+is:pr+is:open&per_page=1" -q .total_count
120
```

Cross-checked: `gh pr list --limit 200` returns 120 and stops, so the list is saturated rather than truncated at that limit.

## Three wrong counts, same cause

| reported | command | what it actually was |
|---|---|---|
| 7 | `gh pr list --limit 10` | the first 10 rows, minus a few already-merged |
| 20 | `gh pr list --limit 20` | the first 20 rows |
| 40 | `gh pr list --limit 50` | the first 50 rows |
| **120** | `search/issues ... total_count` | the count |

`gh pr list --limit N` answers *"show me up to N"*. It never says whether more exist. Each figure was reported as a total, and each was corrected only because the next command happened to use a larger limit. Nothing in the output signalled truncation --- that is what made the error repeatable.

A total needs a command that returns a count, not a page.

## What this means for the work

A backlog of 120 open pull requests cannot be triaged one at a time inside a work loop. The ones examined so far, using a merge check verified by exit status rather than by piped output, split into four kinds:

- **already landed** --- merging yields zero net files (#1652, #1694, both now closed);
- **landable after reconciliation** --- merges clean, one or two binding digests stale (#1686, landed via #1948 and supplying ORION-25's missing chapter files);
- **blocked on a frozen binding** --- merges textually clean, then fails binding-coverage on a freeze-blocked paper (#1815);
- **genuinely conflicting** --- (#1656, #1658, #1709, #1693).

Only a handful have been checked. The proportions above should not be extrapolated to 120.

## The pattern this session kept repeating

Every measurement error here has the same shape: a command that answers a narrower question than the one asked, whose output looks like an answer to the broader one. `pr list --limit N` for a total. `merge-tree | grep '<<<<<<<'` for conflicts, missing binary ones. `git merge | head` for merge success, discarding exit status. `find | head -1` for the current artifact, returning a superseded one. `grep 'hardened manuscript'` for a banner, missing `bounded manuscript`.

None of these produced an error message. Each returned a plausible value.
