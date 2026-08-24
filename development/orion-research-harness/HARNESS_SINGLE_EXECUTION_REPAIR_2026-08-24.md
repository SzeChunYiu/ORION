# Research-harness single-invocation repair

Date: 2026-08-24

Frozen base: `4ba814eebfbcc4cb9ec9de0618e0e6442c7f3799`

Status: **FROZEN BEFORE IMPLEMENTATION**

Authority: harness integrity only; no scientific result or publication claim.

## Atomic development question

Can each call to `service_local_request` invoke its local capability executor
exactly once, while preserving all other behavior?

The base implementation calls `execute_local` twice and records only the
second output. This leaves the first execution's side effects outside the
receipt.

## Incumbent and donor ceiling

The incumbent already has the required architecture: a content-addressed
request, a confined local executor, and an ingested result. The correct donor
ceiling is one *local invocation per service call* at this boundary: call the
executor once and record that result. This does not imply global exactly-once
semantics for a deterministic request, crash recovery, or transactional
rollback of arbitrary process side effects. A later call to
`service_local_request` may execute the same request again.

## Saturation assessment

- **Knowledge:** the defect is directly visible in the fixed-base source; no
  external literature is needed to determine the local control-flow repair.
- **Search universe:** all local capabilities pass through
  `service_local_request`; the discriminating test uses its file-write path.
- **Formulation:** an append-only `FILE_WRITE` request is a discriminating
  witness because duplicate execution produces two appended bytes while a
  single invocation produces one.

## Challenge to the saturation basis

A passing return-value test could miss duplicate execution when both calls are
deterministic. The hostile test must therefore observe an intentional side
effect. Timeout cleanup and retry behavior may expose different regressions, so
their existing tests remain in scope.

## Why prior checks missed it

Most tests assert the final recorded value, which is identical across the two
executions.

## Frozen implementation hypothesis

1. Remove the duplicate `execute_local` call.
2. Add a side-effect test proving one service call appends exactly once.
3. Do not adjudicate the interleaved timeout-policy definitions in this repair.

## Honest terminals

- `HARNESS_LOCAL_SERVICE_CALL_SINGLE_INVOCATION_VERIFIED`
- `HARNESS_LOCAL_REQUEST_DUPLICATE_EXECUTION_PERSISTS`
- `HARNESS_TIMEOUT_CONTRACT_REGRESSED`
- `HARNESS_REPAIR_CANNOT_CHECK`

## Reopen triggers

Reopen if one service call invokes a capability more than once or if result
ingestion no longer binds the sole returned output. Separately adjudicate the
two timeout-policy definitions and three timeout assignments already present
on the frozen base; this repair deliberately leaves that conflict untouched.

## Explicit non-claims

This repair supplies neither sandboxing, replay suppression, nor local or
remote exactly-once execution across repeated service calls. It does not
validate any existing scientific receipt produced through the defective path;
those results require replay after the repair.
