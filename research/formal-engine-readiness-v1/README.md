# Recursive engine formal-readiness audit V1

## Question

Can issue #2 — formalize the recursive reconstruction engine — be closed as formal completion on the current ORION state?

## Discriminator

A paper/spec may look complete while the executable mechanic audit still has open coordinates. V1 therefore separates:

1. **registered operator contract presence**;
2. **core proof-obligation guards**;
3. **recursive graph integrity**;
4. **independent formal closure of the registered mechanic surface**.

Only (4) authorizes `FORMALLY_CLOSED_REGISTERED_SURFACE`.

## Gate

`src/orion/benchmarks/formal_engine.py` evaluates the current runtime state rather than a frozen documentation claim.

### Contract-presence checks

Each canonical operator (`FRAME`, `SEARCH`, `ABSORB`, `RECONSTRUCT`, `DETECT`, `DIAGNOSE`, `REFRAME`, `REOPEN`, `SATURATE_BOUNDED`) must have:

- typed input identities;
- typed output identities;
- authority boundary;
- reopen triggers;
- empirical-open coordinates;
- canonical root ordering.

### Executable proof guards

V1 directly checks:

- SEARCH non-authority;
- ambiguous responsibility blocks high-impact revision;
- EVIDENCE responsibility is not a formulation rewrite;
- EXECUTION responsibility is not a formulation rewrite;
- METHOD change is outside local reframe;
- recursive child/dependency graph has no unknown or mixed/cyclic references.

These are necessary but not sufficient for formal closure.

### Independent closure

The readiness gate then reads `observe_current_mechanics_program()`. If any reachable mechanic still has open questions or is not `READY_FOR_BENCHMARK`, the status is `INDEPENDENT_VERIFICATION_OPEN` even if generic contracts are present.

This prevents three false closures already encountered in the project:

- generic envelopes being mistaken for step-specific answers;
- self-authored answer/check lanes being mistaken for independent verification;
- a green implementation test suite being mistaken for formal closure of the research method.

## Current expected result

The repository history has recently measured more than one thousand open independently unverified mechanic questions. The V1 test therefore expects:

`STRUCTURALLY_SOUND = true`

`FORMAL_ENGINE_STATUS = INDEPENDENT_VERIFICATION_OPEN`

not `FORMALLY_CLOSED_REGISTERED_SURFACE`.

The exact open-question count remains a live computed metric rather than a manually frozen headline number.

## Issue #2 consequence

Issue #2 should remain open until this gate itself returns `FORMALLY_CLOSED_REGISTERED_SURFACE`. The blocker is no longer vague: it is the remaining independently unverified mechanic coordinates, together with whatever checking-lane/host-evidence work the live kernel reports.

This status does not block using ORION. It blocks only the stronger claim that the entire registered recursive engine has achieved independent formal closure.
