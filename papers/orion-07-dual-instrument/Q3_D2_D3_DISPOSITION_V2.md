# Q3 D2/D3 disposition V2

**Decision:** accepted instrument limitations for the Q3 benchmark series; no in-place repair before final scoring.

This closes the Paper-Q3 submission-gate requirement to decide the disposition of D2/D3. It does **not** claim the defects are unimportant or repaired.

## D2 — well-formed successful LLM envelope with non-JSON content

Known behavior: a `success=true` `LLM_COMPLETE` receipt can satisfy the outer capability envelope yet contain non-JSON `content`, causing the recursive solve to terminate with an unstructured traceback rather than a typed scientific disposition.

### Q3 disposition

- D2 is an **instrument availability/structured-failure defect**, not an evidentiary positive/negative.
- If D2 occurs in a Q3 instance, that lane is `CANNOT_CHECK` / instrument-invalid under the prospectively frozen outcome space.
- The malformed receipt must not be interpreted as evidence and the instance must not be deleted from the series denominator.
- Q3 does not repair and rerun the same outcome-bearing instance under a changed instrument version.

## D3 — successful-malformed receipt pins deterministic identity

Known behavior: successful receipts are immutable, so a successful envelope containing malformed semantic content cannot use `retry-failed`; the deterministic request identity can remain pinned.

### Q3 disposition

- D3 is a **recoverability defect**.
- If encountered before an outcome-bearing lane freeze, the lane may be abandoned under a new experiment identity.
- If encountered after the lane has become outcome-bearing, the instance terminal is instrument-invalid/CANNOT_CHECK; no in-place archive/remint is allowed.
- The original bytes stay in the audit history.

## Why no repair in this paper

1. Benchmark V0 and the two clean replacement instances use the already-frozen instrument contract; none of their committed lane receipts exhibits D2/D3.
2. A code repair between benchmark instances would create an instrument-version confound unless the whole series were repeated prospectively.
3. D2/D3 halt or pin orchestration; they do not silently admit malformed content into scientific evidence under the declared result contracts.
4. The paper's claim is benchmark definition plus a small prospective case series, not defect-free harness reliability.

## Required manuscript limitation

The final Q3 manuscript must state that successful-but-semantically-malformed LLM receipts are an unresolved structured-failure/recovery limitation of the frozen harness version. It must not describe the instrument as defect-free, secure, or generally fault tolerant.

## Future repair route

A successor instrument version may add semantic validation before successful receipt commitment and a prospectively governed supersession/remint mechanism. Such a repair is outside Q3's current evidence and grants no retroactive improvement to this series.

**Gate disposition:** `Q3_D2_D3_ACCEPTED_LIMITATIONS__NO_IN_PLACE_REPAIR__INSTANCE_FAILS_CLOSED_IF_TRIGGERED`.