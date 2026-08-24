# Foundations V2 startup and coordination audit

## Exact repository base

- repository: `SzeChunYiu/ORION`
- base branch: `main`
- base commit: `eba4a67e8607cdef96a2bb038d685a9a5d548599`
- foundations branch: `codex/orion-foundations-v2-local-derivations`
- parent issue: #1220

The base was read after the P1 coordination notice. No earlier SHA is treated as
current repository state.

## Protected P1 execution lane

PR #1218 and the LUNARC RR1 one-tuple science job are owned by the P1 execution
lane. The foundations lane does not edit, merge, rebase, supersede, execute, or
submit them.

The following PR #1218 paths are explicitly outside this branch:

```text
development/p1-scienceagentbench-protected-rr1-one-tuple-finalizer-freeze-v1-2026-08-24/BODY_FREE_EXPORT_MANIFEST_V1.json
development/p1-scienceagentbench-protected-rr1-one-tuple-finalizer-freeze-v1-2026-08-24/DEVELOPMENT_PACKET.md
development/p1-scienceagentbench-protected-rr1-one-tuple-finalizer-freeze-v1-2026-08-24/FINALIZER_CONTRACT_V1.json
development/p1-scienceagentbench-protected-rr1-one-tuple-finalizer-freeze-v1-2026-08-24/FINALIZER_OUTPUT_SCHEMA_V1.json
development/p1-scienceagentbench-protected-rr1-one-tuple-finalizer-freeze-v1-2026-08-24/HANDOFF_V1.md
development/p1-scienceagentbench-protected-rr1-one-tuple-finalizer-freeze-v1-2026-08-24/SHA256SUMS
development/p1-scienceagentbench-protected-rr1-one-tuple-finalizer-freeze-v1-2026-08-24/SYNTHETIC_VALIDATION_RECEIPT_V1.json
development/p1-scienceagentbench-protected-rr1-one-tuple-finalizer-freeze-v1-2026-08-24/protected_rr1_one_tuple_finalizer_v1.py
development/p1-scienceagentbench-protected-rr1-one-tuple-finalizer-freeze-v1-2026-08-24/validate_protected_rr1_one_tuple_finalizer_v1.py
```

Published P1 head `5b6976ed` is recorded as **NO-GO** on live Slurm formats and
custody/integrity paths. This foundations tranche does not import it as evidence,
repair it, run it, or infer the amended immutable OID under parallel audit.

## Changed-path boundary

This tranche is restricted to new paths under:

```text
src/orion/foundations/
tests/foundations/
research/orion-foundations-v2/
.github/workflows/orion-foundations.yml
```

No paper directory, P1 research object, result receipt, active authority,
publication package, execution finalizer, or shared registry is changed.

## Local execution environment

- Python: 3.13
- dependencies used by the theorem core: Python standard library only
- test runner: pytest
- network access during local derivation: none
- protected data/outcomes: none
- model or LLM judge calls: none
- external scientific adjudication: none

This environment is sufficient for exact finite proofs, constructive
countermodels, deterministic fixed-point computation, and algebraic derivations.
It is not sufficient for external authority, naturalistic generalization, or
large protected campaigns.
