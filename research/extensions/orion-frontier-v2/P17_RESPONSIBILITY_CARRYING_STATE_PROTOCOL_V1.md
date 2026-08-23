# P17 Responsibility-Carrying State Protocol V1

Status: **FROZEN DESIGN / NON-AUTHORIZING**  
Date: 2026-08-20

## Candidate atom

A compiled state should travel with a machine-checkable **responsibility certificate** rather than being consumed as an unqualified summary.

The certificate does not prove its own scientific sufficiency. It binds external sufficiency/transport/verifier witnesses to the exact compiled bytes and tells downstream systems when use is allowed, when raw evidence must be reopened, and when the system must return `CANNOT_CHECK`.

## Required coordinates

`ResponsibilityCarryingState.v1` binds:

- source-state digest and identity;
- compiler/transform identity and digest;
- compiled-state digest;
- claimed responsibility contracts;
- one external witness identity per responsibility;
- witness status: `SUPPORTED`, `APPROXIMATE`, or `UNRESOLVED`;
- resource bound under which the witness applies;
- omitted-coordinate classes;
- raw-source availability;
- reconstruction/transport witness identity if recoverable;
- context coordinates required to remain unchanged;
- context coordinates that force reopening;
- authority owner distinct from compiler/evaluator;
- receipt digest.

## Consumption rule

For requested responsibility R:

1. exact compiled bytes must match the certificate;
2. R must be explicitly registered;
3. the external witness must be `SUPPORTED` under the requested resource bound;
4. required-same context must match or a complete transport witness must be supplied;
5. any reopen-trigger change returns `REOPEN_REQUIRED` when raw/reconstructable state exists, else `CANNOT_CHECK`;
6. missing responsibility or unresolved witness returns `CANNOT_CHECK`;
7. approximate support is never silently upgraded to exact support.

## Parents / nonclaims

Direct parents include statistical/decision sufficiency, RL state abstraction, proof-carrying code/plans/reasoning, typed provenance, P7 transport/reopen semantics, P14 sufficiency debt, and P15 raw-state recoverability.

Therefore this protocol does not claim invention of certification, proof-carrying computation, safe abstraction, or state sufficiency.

The research question is whether **responsibility-scoped certificates for dynamically compiled agent state** reduce harmful reuse and unnecessary raw-state reopening in real LLM/formal/scientific pipelines under matched budgets.

## Protected evaluation programme

Before any effectiveness claim, compare:

- unqualified compressed state;
- compressed state + confidence only;
- responsibility-carrying state with exact witness/reopen semantics;
- always-raw upper-cost control.

Measure unsupported-use errors, unnecessary reopen rate, task success, context/memory cost, verifier calls, and recovery latency. The evaluator and scientific authority remain distinct.
