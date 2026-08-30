# An adverse revival attempt was deleted from the working tree

## What was found

`papers/orion-02-fiberguard-finite-fibre/rounds/r23-density-backoff-revival/ORION02_REVIVAL_ATTEMPT_LEDGER_V1.jsonl`
carried an **uncommitted working-tree modification deleting 8 lines** — the whole
of revival attempt 2, `ORION02-REVIVAL-002-R24-ARM-CONDITIONAL-BOUNDARY-FIBRES`,
from its prospective registration through to its terminal:

```
"scientific_terminal": "C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID"
"status": "COUNTED_ADVERSE_CERTIFICATE_INVALID"
"attempt_ordinal": 2, "remaining_attempts": 98
```

#1701 requires the opposite of this:

> Recover R24 result: coverage 44/44 but certificate invalid, 20/44 strict
> held-out violations; lexical control also 44/44.
> Preserve both as counted adverse revival attempts.

The deletion removed a counted adverse outcome and rolled the attempt budget back
from 98 to 99 by omission. Nothing was staged and nothing was committed, so this
never reached a branch.

## The lines were genuine

Before restoring, all three custody receipts the deleted rows cite were confirmed
present on `origin/main`:

- `ORION02_R24_CUSTODY_3550275.json`
- `ORION02_R24_INFRASTRUCTURE_FAILURE_3550259.json`
- `R24_VERIFIER_PARENT_SUMMARY_AMENDMENT_A.json`

The ledger was restored from `HEAD`; it is back to 13 rows with 8 R24 references,
and the working tree is clean.

## Why nothing caught it

The ledger is append-only by intent and **sealed by nothing**. It appears in no
`SHA256SUMS` anywhere in the repository. An append-only record of adverse
outcomes with no seal can be truncated silently, and a truncation that removes an
adverse result is indistinguishable from that result never having happened.

## The guard, and the version of it that would have missed this

`check_revival_ledger_integrity_v1.py` checks four properties. The fourth is the
one that matters, and **the first version of this checker did not have it and
returned OK on the exact damage above.**

The first version checked that every counted attempt's receipt exists, that
ordinals are gap-free, and that `remaining_attempts` is consistent. Delete the
last attempt and the surviving ordinals are `[1]`, which is gap-free; its receipt
exists; the arithmetic is consistent. **End-truncation is invisible from inside
the ledger.** It is visible only from outside: the removed attempt's custody
receipts are still on disk and nothing cites them.

Adding that check then produced **two false positives** — custody receipts from
rounds R21 and R22, which predate the ledger and are prior work rather than
removed attempts. The orphan scan is now floored at the ledger's earliest cited
round, which still catches an end-truncation because the removed attempt's round
sorts after the ones that survive.

Both defects were found by testing the checker against the real tree and against
the specific damage, not by reading it.

## Validation

| case | expected | result |
|---|---|---|
| real tree, unmodified | exit 0, silent | exit 0, silent |
| the exact damage (R24 rows deleted) | exit 1 | exit 1, names the orphaned receipts |
| ledger absent | exit 3 | exit 3 `CANNOT_CHECK` |

Exit 3 is distinct from 0 deliberately: "no ledger found" is not "the ledger is
fine".
