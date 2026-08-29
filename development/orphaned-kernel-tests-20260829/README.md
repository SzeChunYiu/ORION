# Orphaned kernel tests — preserved, not runnable

**Status:** `CANNOT_CHECK_IMPLEMENTATION_ABSENT`. These five files are kept here so the work
survives; they are **not** under `tests/` because they would break collection immediately.

## What these are

Five test files, ~262 KB, **166 test functions**, found untracked in the working tree of this
Mac's ORION checkout on 2026-08-29 and absent from `origin/main`:

| File | Tests |
|---|---:|
| `test_process_receipt_v3_deadline_hostile.py` | 92 |
| `test_evidence_root_observation_hostile.py` | 25 |
| `test_evidence_nonblocking_output_v3.py` | 20 |
| `test_evidence_process_failure_v2.py` | 17 |
| `test_evidence_selector_lifecycle_v3.py` | 12 |

## Why they are not in `tests/`

All four collectable modules fail at import:

```
AttributeError: module 'orion.kernel.evidence' has no attribute 'EvidenceHelperHandoffState'
```

`EvidenceHelperHandoffState` does not exist on `main`, and a search of the 40
most-recently-updated `origin/*` branches found no `src/` definition of it either. So these
tests were written against a kernel API whose implementation was never committed, or was
committed and later reverted.

Placing them under `tests/` would fail collection on every run — a hard CI break, not a
soft one — so they live here instead.

## What would make them live again

They need `orion.kernel.evidence.EvidenceHelperHandoffState` and whatever else the handoff
state pulls in. If that implementation is recovered from another machine or an unpushed
branch, move these files back to `tests/unit/kernel/` and run them; they encode 166
assertions about non-blocking output, process failure, hostile root observation, selector
lifecycle, and hostile receipt deadlines that would otherwise have to be rewritten.

## Why this was preserved rather than deleted

The same checkout carried evidence-destroying regressions on the same day — 103 deleted
files under `orion-02/rounds`, `orion-21/experiments` and `orion-11/experiments`, all present
in both `HEAD` and `origin/main`, plus a ledger edit that dropped an adverse terminal. All
were reverted. Untracked work in that tree was, on the evidence, at real risk of quiet loss,
and 166 tests are too much to drop on the assumption that someone else has a copy.

No claim is made that these tests pass, or ever passed. They are preserved as unverified
prior work.
