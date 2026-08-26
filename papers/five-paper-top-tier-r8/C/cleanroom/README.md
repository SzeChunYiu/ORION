# JOB-C-R8-1 clean-room replay preparation

This directory contains an additive, structurally independent implementation of
the three finite FiberGuard panels described in the R8 manuscript. It never
imports the reference implementation.

## Authority boundary

The body of GitHub issue 1379 exposed frozen verdicts before this output was
sealed. `BLINDING_BREACH_ISSUE_BODY` is therefore permanent for this lane. The
implementation may be used for engineering review, but it cannot supply a
blind independent comparison or a replay PASS. The independence terminal is
`CANNOT_CHECK`; a later truly blinded external worker is required.

The committed `R8_PACKET_COMMIT.json` now uses the non-self-referential v2
subject/publication binding. Before any dispatcher starts, the executor runs
the canonical packet validator, requires the exact frozen source ref, resolves
the scientific subject rather than the packet-publication commit, and
preserves the packet's engineering-only authority boundary. The packet itself
still grants neither execution nor LUNARC authority.

The hardened executor additionally requires a separate external
`ORION.FiberGuardCleanroomExecutionAuthorization.v1` object. That object must
be issued after root review and bind the exact scientific subject, exact clean
implementation commit/tree, exact source-manifest digest, JOB-C-R8-1, and
explicit execution plus LUNARC grants. That authorization is a separate,
external reviewed object and is valid only for the exact final implementation
commit, tree, and source-manifest digest. No result from the reference artifact
is read here.

## Components

- `fiberguard_cleanroom.py`: independent generators, dual exact solvers, fibre
  aggregation, deterministic witness selection, refinements, and third endpoint
  checkers.
- `build_manifest.py`: deterministic allowlisted source manifest.
- `run_replay.py`: fixture-only validation and identity-gated exhaustive entry
  point with exact source-allowlist, external-authorization, clean HEAD/tree,
  and provenance gates.
- `verify_receipt.py`: exact manifest, payload-schema, authority, identity,
  authorization, and provenance verification.
- `slurm/job_c_r8_1.slurm`: prepared 16-core, 32-GB, two-hour job using an
  external run directory so logs/results cannot dirty the authorized checkout;
  not submitted.
- `tests/`: primitive, hostile, identity, manifest, and receipt tests.

## Permitted local validation

After rebuilding `SOURCE_MANIFEST.json`, fixture validation is:

```text
python run_replay.py --mode fixtures --output NON_OUTCOME_VALIDATION.json
python verify_receipt.py --receipt NON_OUTCOME_VALIDATION.json
```

This path does not execute or summarize any complete scientific panel.

## Execution contract

The SLURM script must be submitted from an external run directory whose
`logs/` subdirectory already exists. `ORION_REPOSITORY` must name the exact
clean checkout and `FIBERGUARD_EXECUTION_AUTHORIZATION` must name the reviewed
external authorization object. Submit only after both the canonical v2 packet
validator and the external exact-checkout authorization pass in the clean
checkout. A full checkout is accepted. A quota-constrained sparse checkout is
accepted only in cone mode with the single exact path
`papers/five-paper-top-tier-r8`; required packet, publication-binding,
preserved-predecessor, and validator files must all be materialized and match
their committed Git blobs. Any different sparse pattern fails closed.
Execution does not cure `BLINDING_BREACH_ISSUE_BODY`, change
independence from `CANNOT_CHECK`, compare against frozen outcomes, or confer
scientific, novelty, or publication authority.
