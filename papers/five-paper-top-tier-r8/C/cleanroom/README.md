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

`R8_PACKET_COMMIT.json` also remains an unresolved placeholder. Exhaustive
execution and LUNARC submission are blocked until an exact packet commit is
bound and reviewed. No result from the reference artifact is read here.

## Components

- `fiberguard_cleanroom.py`: independent generators, dual exact solvers, fibre
  aggregation, deterministic witness selection, refinements, and third endpoint
  checkers.
- `build_manifest.py`: deterministic allowlisted source manifest.
- `run_replay.py`: fixture-only validation and identity-gated exhaustive entry
  point.
- `verify_receipt.py`: source-manifest and sealed-payload verification.
- `slurm/job_c_r8_1.slurm`: prepared 16-core, 32-GB, two-hour job; not submitted.
- `tests/`: primitive, hostile, identity, manifest, and receipt tests.

## Permitted local validation

After rebuilding `SOURCE_MANIFEST.json`, fixture validation is:

```text
python run_replay.py --mode fixtures --output NON_OUTCOME_VALIDATION.json
python verify_receipt.py --receipt NON_OUTCOME_VALIDATION.json
```

This path does not execute or summarize any complete scientific panel.
