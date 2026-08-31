# ORION-07's evidence gate is met

Earlier in this session ORION-07's abstract was reported as saying the paper is not ready to submit. That reading was correct about the text and out of date about the tree.

## What the abstract said

> the frozen publication plan requires at least two of three additional frontier-question instances before standalone submission; the evidence gate remains open

## What the tree says

`check_q3_completion.py` on `main`:

```
Q3_COMPLETION_CHECK=PASS
VALID_PROSPECTIVE_SERIES=V0,Q3-R1,Q3-R2
CONTAMINATED_RETIRED_SLOTS=Q3-V1/QG-7d,Q3-V2/QG-15c
REPLACEMENT_INSTANCES_SCORED=2
REPLACEMENT_RESULTS_REPLAYED=2
D2_D3=ACCEPTED_FAIL_CLOSED_LIMITATIONS
AGGREGATE_RELIABILITY_AUTHORITY=FALSE
SCIENTIFIC_AUTHORITY=NOT_GRANTED_BY_CHECKER
```

The protocol's own paper gate has five conditions, and each is satisfied:

| condition | evidence |
|---|---|
| both replacements validly frozen | `VALID_PROSPECTIVE_SERIES=V0,Q3-R1,Q3-R2` |
| both independent outcomes exist | series includes both replacement slots |
| both scores produced from this map | `REPLACEMENT_INSTANCES_SCORED=2` |
| both scientific results replay | `REPLACEMENT_RESULTS_REPLAYED=2` |
| D2/D3 defects explicitly disposed | `D2_D3=ACCEPTED_FAIL_CLOSED_LIMITATIONS` |

The two originally contaminated slots remain visible in the audit, which the protocol requires rather than forbids.

## What is still not established, and must not be overstated

`AGGREGATE_RELIABILITY_AUTHORITY=FALSE` and `SCIENTIFIC_AUTHORITY=NOT_GRANTED_BY_CHECKER`. Passing the completion gate means the case series is **complete and replayable**, not that agreement between the two instruments is established as a general property. Three instances is a case series. The checker states plainly that it grants no scientific authority, and nothing here changes that.

So two distinct things were conflated in the original abstract sentence:

1. a **submission blocker** --- the instances did not yet exist. This is now cleared.
2. a **scientific limit** --- a three-instance series cannot support a general reliability claim. This stands.

## Consequence for the current text

The abstract was rewritten earlier to read: *a first measurement on a single frontier question; additional instances are required before the agreement measure can support a general claim.* That sentence remains accurate --- it matches `AGGREGATE_RELIABILITY_AUTHORITY=FALSE` --- and it no longer asserts the cleared submission blocker.

That outcome was luck rather than judgement. The rewrite was made to remove internal framing (`frozen publication plan`), not because the gate had been checked; the gate was only run afterwards. Had the two clauses been differently entangled, the same edit could have deleted a live limitation or preserved a dead one.

## Status change

ORION-07 is **content-ready by its own protocol**. Its remaining gaps are the ones shared with the rest of the corpus, not an open evidence gate.
