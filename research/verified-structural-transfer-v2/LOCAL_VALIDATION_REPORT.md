# Local validation report

## Scope

This report covers only the V2 productionization mechanics and deterministic known-answer fixtures. It is not external scientific evidence.

## Pre-integration run

Command:

```text
PYTHONPATH=src pytest -q
```

Result:

```text
52 passed
```

## Failures found during hostile construction

1. **P4 critical-defeater pre-emption.** The first wrapper scored all unresolved defeaters together, allowing a very cheap noncritical check to beat a lower-ratio action addressing an unresolved critical defeater. The wrapper now restricts action selection to the critical set whenever one exists. A hostile regression test freezes this behavior.
2. **P3 known-answer fixture error.** The intended consistent three-view affine cycle used the wrong inverse offset. The consistency checker correctly returned `OBSTRUCTION`; the fixture was repaired rather than weakening the checker. A separate deliberately corrupted three-view cycle remains an obstruction test.
3. **P5 exported-history aliasing.** The first append-only history returned shallow copies of nested retained payloads, so a caller could mutate an exported view and silently change future archive digests. History now deep-copies both stored and exported payloads, with a regression test that mutates returned structures and proves the retained archive is unchanged.

These are local engineering findings only.
