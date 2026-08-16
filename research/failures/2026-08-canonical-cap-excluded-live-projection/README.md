# Canonical resource cap rejected the live mechanics projection

## Observed

During the Task-2 hostile standards review, after rebasing the protected branch
onto `origin/main` `ebb93fddb2931a39fe57c222edce628813a0fd97`, the
canonical codec's one-mebibyte input/output cap excluded ORION's actual seed:

```text
current_program_cells():       59 cells
typed canonical seed:          1,196,301 bytes
typed empty-record projection: 1,196,785 bytes
configured limit:              1,048,576 bytes
projection_hash(...):          CanonicalizationError
```

The focused fixtures all passed because their one-cell projections were much
smaller than the real program.

A separate post-fix hostile probe supplied a syntactically near-canonical
7,200,110-byte payload containing 800,000 `["null"]`-shaped arrays. The byte
precheck admitted it, then the post-parse node limit rejected it after 0.175 s;
the local process reported 255,787,008 bytes peak RSS. This is an environment-
specific resource-amplification observation, not a cross-platform bound.

## Failure class

`VALID_STATE_REJECTED_BY_RESOURCE_POLICY` + `FIXTURE_SCALE_BLIND_SPOT`.

## Correct response

- Keep an explicit finite cap; do not remove resource bounds.
- Raise the byte cap to eight mebibytes. This is about seven times the current
  live seed and remains paired with the independent 100,000-node and 128-depth
  limits.
- Test `projection_hash` against `current_program_cells()`, not only synthetic
  one-cell fixtures.
- Keep hostile numeric-token rejection before Python integer conversion and
  retain a byte precheck before JSON parsing.

## General lesson candidate

A safety limit is part of the valid-state specification. A bound that rejects
the system's live canonical state is not protective correctness; it is a
denial of the intended transition surface. Resource bounds need both hostile
oversize tests and representative valid-scale tests.

## Residuals and reopen coordinates

- set an explicit decoder memory budget and decide whether a streaming/preflight
  structural limit is required before exposing canonical decode to less-trusted
  storage or transport;
- revisit the bound when the decomposition approaches either 80% of the byte
  cap or 80% of the node cap;
- if larger projections become normal, evaluate chunked/Merkle commitments
  rather than increasing an in-memory parser limit without bound.
