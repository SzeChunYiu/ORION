# Concurrent ledger append race

## Observed

At exact `main` commit `3fdff9e252ee0869b52f0e8f04b55897b38757be`,
sixteen processes opened the same `LedgerStore`, synchronized at a barrier and
called `append`. The file-based reproduction produced three surviving lines,
thirteen failed worker processes and an invalid chain:

```text
process_exit_codes [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0]
line_count 3
verify ('line 2 has sequence 0, expected 1',)
```

The exact interleaving and number of surviving lines are nondeterministic; the
duplicate sequence-zero head and invalid replay are the stable failure.

The attack was re-run after concurrent PRs #27 and #28 at
`5894ac7814d194b3c60d9655af87ef2d9828d56c`; three lines survived and replay
again failed at duplicate sequence zero.

Earlier, an inline-stdin multiprocessing probe on macOS could not reload
`<stdin>` under spawn. A later command also used an interpreter without ORION
on `sys.path`. Both were instrument failures. Running the same barrier attack
from a real file with `PYTHONPATH=src` exposed the ledger failure.

## Failure

`append` separately replays the current head, constructs the next entry and
opens the file in append mode. Those operations are not one atomic
expected-head transition. Concurrent writers can all observe genesis and write
different entries with sequence zero. Hash chaining detects the corruption
afterward but does not prevent it or guarantee durable progress.

## Failure class

`NON_ATOMIC_COMPARE_AND_APPEND` + `DURABLE_STATE_FORK`.

## Correct response

- Append under an atomic expected-head/expected-revision compare-and-swap.
- Serialize the read-verify-write-critical section with a process-safe lock or
  transactional store, and define crash recovery and fsync/rename semantics.
- Reject stale writers without corrupting the accepted chain.
- Preserve idempotency keys so retries cannot duplicate side effects.
- Replay projections from the accepted event stream and bind them to an exact
  reducer/workflow version.

## General lesson candidate

A tamper-evident hash chain is not an atomic ledger. Detection after corruption
cannot substitute for a linearizable state-transition boundary.

## Residuals and reopen coordinates

- process death before/after write and before/after durability barrier;
- partial/torn writes and disk-full behavior;
- stale expected heads, retries and idempotency;
- multi-host storage, consistency proofs and external checkpoint witnesses.
