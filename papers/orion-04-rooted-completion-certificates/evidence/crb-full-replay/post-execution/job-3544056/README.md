# ORION-04 CR-B full replay — failed job 3544056

This is the additive, byte-bound failure record for the one CR-B submission that
used nonduplication key
`741454d7d6b513ccd80d2aa9a78d2a9f5076fe8075341d0ecc8e95566ecc28ea`.
It preserves the failure; it does not turn it into a scientific result.

## What actually ran

LUNARC job `3544056` ran for `08:08:42` on node `cx08` with 48 allocated
CPUs and 192 GiB requested memory. It built the pinned `drat-trim` source, then
entered census generation. The job stopped with exit `1:0` while constructing
the generation receipt:

```text
TypeError: value is not canonical JSON: float
```

The exact defect is pre-outcome bookkeeping: `crb_census.py` records wall time
using `round(..., 3)`, which produces a float, while the frozen
`engine_b.py` canonical serializer accepts only strings, integers, booleans,
nulls, lists, tuples, and dictionaries.

Control flow implies that the D2 generator returned its frozen count and its
stream writer returned before this error was reached. That is diagnostic only:
the D2 bytes were node-local, no receipt or digest was durably copied, and the
scratch directory disappeared after the allocation. The D3 outcome is masked:
it may have completed, mismatched, or reached the internal generation budget
before the same receipt bug replaced its terminal. Phase 2 SAT execution,
positive-witness evaluation, Phase 3 external DRUP checking, and Phase 4 durable
copy did not run.

## Why PR #1503 cannot simply be submitted now

The remote submission registry binds job `3544056` to the same nonduplication
key that PR #1503 calls unused. The job checkout was
`2273e7a6936180bce50fb5caf446c4ae5d21b549`, not PR #1503's later authorized
commit `20365f254807015d8db46a370f006f8be462b3f8`. The core scientific engine,
authorization packet, source manifest, submit script, and job script are
byte-identical between those commits, but the replay-source manifest is not.
Thus the exact current-root commit did not execute, yet its declared one-attempt
subject key has already been consumed. A fresh checkout-local registry could
miss that fact because the registry is untracked; this receipt forbids treating
that implementation gap as permission for a duplicate run.

The following PR #1503 statements are now stale and are superseded only at the
execution-status layer:

- `current_key_seen_in_prior_attempt=false`;
- `status=AUTHORIZED_NOT_SUBMITTED`;
- `...EXECUTION_PENDING`.

## Authority ceiling

Terminal:

```text
NQ_CRB_FULL_REPLAY_JOB_3544056_FAILED_CENSUS_RECEIPT_SERIALIZATION__D2_D3_AUTHORITY_CANNOT_CHECK
```

Accordingly:

- full D2/D3 replay authority: **not established**;
- D2 and D3 numerical authority: **CANNOT_CHECK**;
- #1516 replay prerequisite: **not satisfied**;
- #1522 theory-mining gate: **closed**;
- D4: **OPEN**, with zero D4 rounds consumed;
- external independence and journal authority: **false**.

No protected Task-3 path is touched.

## Shortest honest successor

Preserve this attempt and key, fix the float receipt bug with success and
post-D2 failure-path tests, checkpoint and hash Phase 1 before Phase 2, add a
durable first-failure/environment trap, and replace the checkout-local
nonduplication guard with a globally bound prior-attempt record. Then rebuild
all affected manifests and obtain a new explicit one-attempt authorization.
The successor must not reuse this key and must still complete both denominators,
independently evaluate every positive witness, externally check every UNSAT
DRUP proof, and retain raw-byte ledgers before it can satisfy #1516.
