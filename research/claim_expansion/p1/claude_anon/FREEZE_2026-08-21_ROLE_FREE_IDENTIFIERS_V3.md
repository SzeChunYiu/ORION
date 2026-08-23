# P1-U R6: role-free identifiers — prospective freeze, V3

**Supersedes V2, same day.** V1 and V2 stand unedited, and so do the two
precondition aborts they produced (`ROLE_FREE_RERUN_V1.json`,
`ROLE_FREE_RERUN_V2.json`). Neither scored an arm, so no outcome has been seen
at the time of writing this.

## What changed, and why

V2 fixed the right thing — the role check is a generalisation question and must
be held out — and specified the split as "by sorted episode id, alternating:
even indices fit, odd indices score". Run, it reported held-out informedness
**0.0 at every prefix length from 1 to 12**, and then aborted on V2's own
stratification guard:

```
fit = [adverse, unresolved]   score = [control, unresolved]
```

The reason is a property of the corpus worth writing down. Episode ids are
`R5-<QUERY>-A` and `R5-<QUERY>-C`, so the two members of a pair sort *adjacent*
to each other, and alternating over a sorted list therefore separates the roles
almost perfectly. The split was not random with respect to the thing being
tested; it was nearly anti-correlated with it.

V2's guard caught this rather than letting a one-role-per-side split report a
clean result, which is what it was written for. But the fix is a change to a
frozen parameter, so it is a supersession.

## Precondition 2, restated

Same statistic, same ceiling, same prefix range. Only the split changes:

**Stratify by role, then alternate within each role.** Sort the episode ids
within each role, take even positions for fitting and odd positions for scoring.
Every role is then present on both sides by construction, in as close to equal
proportion as its count allows.

The stratification guard from V2 is retained unchanged and still aborts the run
if any role is missing from either side. A guard that has been made redundant by
construction is exactly the kind that should stay, because "by construction" is
a claim about today's corpus.

The ceiling is unchanged: **held-out informedness `0.0` at every prefix length
from 1 to 12.**

## Everything else is unchanged

Precondition 1, the salt, the handle length, the eight anonymised surfaces, the
arms, the comparator, the corpus, the scoring functions, every evaluator
threshold, and the claim scope from V1 §5 all carry over exactly. No part of the
scoring path has been touched by any of the three versions.

## Anti-tuning, restated

Three supersessions in one day is a lot, and the reason each was permitted is
that **not one of them changed anything downstream of a scored arm** — all three
aborted in the preconditions, before the evaluator ran, and no outcome had been
observed when any of them was written. If a parameter is changed after an arm is
scored, that is a different act and this chain does not license it.
