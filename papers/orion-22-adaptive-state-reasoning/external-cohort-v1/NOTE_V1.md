# ORION-22 external family availability v1

**Terminal: `AVAILABILITY_ONLY__FAMILY_CHOICE_NOT_MADE_HERE`.**

## What was open

ORION-22's outstanding item is the second-family transfer: one family — **E3
Defects4J** *or* **E2 OpenML** — chosen **before** protocol freeze, and required to
contain both zero-regret and positive-regret observation classes.

## Why I did not choose

The choice is a protocol act, not an acquisition act. Its scientific value comes
entirely from being made before the freeze; making it here, after looking at both
candidates, would destroy exactly the property it exists to provide. So both are
recorded as available and neither is selected.

## What is available

| family | status | anchor |
|---|---|---|
| E3 Defects4J | REACHABLE | `rjust/defects4j` pinned at `8c16da8230843cdc918eaf4ddb449637f02b83c6` (`git ls-remote`, no clone) |
| E2 OpenML | REACHABLE | API returns HTTP 200; concrete anchor OpenML-CC18 (study 99), **72 datasets / 72 tasks** |

Defects4J publishes **no GitHub Release object** — `releases/latest` returns none —
so the commit SHA above is the only stable anchor observed. Version identity should
be read from the repository's own version file at that commit, not from a Release.

## What I could not get

- `CANNOT_CHECK` — **whether either family contains both zero-regret and
  positive-regret classes.** That is an outcome property of running the regret
  analysis. Pre-checking it would require accessing outcomes, which would
  contaminate the pre-freeze choice this record deliberately leaves open. Not
  checked and not estimated.
- P12A superiority remains withheld under
  `P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json`. Nothing here touches it.
- Reachability is not suitability: neither family was checked against the P12B
  controlled-result scope.

No regret analysis was run and no observation class was scored.
