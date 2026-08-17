# Development packet — issue #285 fibre: freeze GlobalPositiveCertificate.v1

High-impact gate (`src/orion/development/protocol.py`). Executable copy: `orion.study.global_positive.packet.build_packet`.

## Atoms

1. `GP-A1` — Freeze a heterogeneous dimension schema that cannot be reduced to one mean score.
2. `GP-A2` — Freeze ≥4 task-family slots with split identities before any candidate outcome.
3. `GP-A3` — Implement non-compensatory admission (all dimensions, worst family, negative-history recurrence, CANNOT_CHECK blocks).
4. `GP-A4` — Hostile tests: scalar compensation, dropped failed family, missing CANNOT_CHECK dimension.
5. `GP-A5` — Baseline stubs that the certificate can score against once outcomes exist.

## Saturation

Bounded for **this engineering fibre** (schema + admission + tests), not for the scientific claim. Two literature rounds in `LITERATURE_MATRIX_V1.md` did not change the admission operator. Covered routes: current vocabulary, function-only, parent discipline, literature bridge, adversarial omission, freshness.

The scientific hypothesis `H-GP1` remains `CANNOT_CHECK` until unbound families are replaced by a successor freeze and multi-round outcomes exist.

## Basis challenge

Saturation could be false if:

- a 2026 continual-optimizer already uses non-compensatory protected Pareto admission with negative history and no self-certification;
- “worst family” is already the primary authority in agent-optimizer compounding work rather than a reporting extra;
- official baseline code becomes runnable and matches the residual exactly.

Missing parent domains that could still matter: constrained MOO with hard safety constraints in certification (avionics-style), statistical non-inferiority trials with multiple co-primary endpoints.

Reopen triggers: nearest-work hit on the residual composition; a bound multi-domain stream existing on `main`; `#209` closing (still does not by itself authorize `#210`).

## Implementation hypothesis

Admission is a fail-closed conjunction over frozen dimensions. Family means, weighted sums, and dropped families cannot authorize. Unbound slots stay `CANNOT_CHECK`. The published freeze hash is the identity of V1; retuned margins are a different object.

## Out of scope

- Binding real tasks (successor freeze)
- Running prospective candidates
- Claiming `GLOBAL_POSITIVE_SUPPORTED`
- Phase-4 programme operation
