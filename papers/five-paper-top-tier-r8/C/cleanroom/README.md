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

## Completed execution and adverse cross-audit

LUNARC job `3542082` completed at implementation commit
`1298ebdc817acad021dd6ee29598bd6aa5c46ff0`; its sealed result SHA-256 is
`c9e6653ea5611cfcf61969f144998cb1538f04501157b43ef8ec32cf6dc628e9`.
The execution and receipt are valid engineering evidence. A post-execution
comparison with the frozen subject found a real definition mismatch in the
2-CNF global sign-type candidate and different endpoint tie-breaking. The
scientific terminal is therefore `C_FIBERGUARD_DISAGREEMENT__CANNOT_CHECK`,
not replay PASS. The completed receipt is preserved unchanged.

This successor corrects the under-specified four-bin sign convention and
frozen deterministic endpoint policy for diagnostic/framework purposes only.
The corrected full panels have **not** been executed, the correction is not an
independent replay, and duplicate submission of JOB-C-R8-1 is forbidden. See
`review/POST_EXECUTION_CROSS_AUDIT_JOB_3542082.json`.

The committed `R8_PACKET_COMMIT.json` now uses the non-self-referential v2
subject/publication binding. Before any dispatcher starts, the executor runs
the canonical packet validator, validates the source-ref observation frozen
inside the packet, resolves the scientific subject rather than the
packet-publication commit, and preserves the packet's engineering-only
authority boundary. A locally present mutable source ref must still equal the
frozen observation or validation fails; a checkout may omit that mutable ref
and then records `NOT_AVAILABLE_LOCALLY` rather than inventing current-ref
authority. The packet itself still grants neither execution nor LUNARC
authority.

The hardened executor additionally requires a separate external
`ORION.FiberGuardCleanroomExecutionAuthorization.v1` object. That object must
be issued after root review and bind the exact scientific subject, exact clean
implementation commit/tree, exact source-manifest digest, JOB-C-R8-1, and
explicit execution plus LUNARC grants. That authorization is a separate,
external reviewed object and is valid only for the exact final implementation
commit, tree, and source-manifest digest. The executed commit did not read the
reference artifact; this post-execution diagnostic successor necessarily did.

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
  job `3542082` is complete and must not be duplicated.
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
