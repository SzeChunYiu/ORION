# Program-frontier assumption failure

**Observed:** Shadow Self-ORION CI run 26 after the invariant wave.

## Failure

The development controller test assumed that `DEPENDENCIES` would be the next unresolved dimension for all 59 reachable mechanic cells. The actual audit reported only one dependency question because almost every child/top-level cell already carried an explicit structural parent dependency; the root workflow was the only missing case. The breadth-first scheduler therefore produced a mixed frontier rather than the predicted uniform wave.

## Diagnosis

Failure class: `DEVELOPMENT_CONTROLLER_EXPECTATION_OVERFIT`.

The implementation's observed state was correct; the test encoded the developer's forecast as if it were a system invariant. Forcing all cells to reopen dependencies merely to satisfy the test would have corrupted the program state.

## Repair

1. Preserve the failure rather than weakening the audit.
2. Add a typed dependency-plan layer for identity/version binding, preconditions, failure propagation, fallback and integrity/provenance.
3. For the root, derive structural dependencies from its declared child mechanics.
4. Preserve already-declared child/parent dependencies.
5. Update the controller test to assert the mechanically resulting next wave rather than the developer's prior expectation.

## General lesson candidate

Tests of adaptive/self-research controllers should distinguish invariant behavior from an expected next research topic. A predicted topic is an observation hypothesis, not a correctness condition. This remains a candidate lesson until it recurs or transfers beyond this case.
