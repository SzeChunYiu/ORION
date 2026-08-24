# P1 ScienceAgentBench LUNARC official public-base V1 — handoff

## Terminal

`P1_SAB_LUNARC_OFFICIAL_PUBLIC_BASE_SMOKE_PASS__EXACT_PINNED_DOCKERFILE_BOUND__IMAGE_AND_NODE_LOCAL_LAYERS_REMOVED__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED`

## Closed in this increment

- The exact 1,251-byte pinned public base Dockerfile, SHA-256
  `08045fc892652a6835adb808ee6db4dc5715ae64f65878eb0d0140e7d8c29a15`,
  built through Docker SDK `7.1.0` and Podman `5.8.2` on reviewed Slurm job
  `3533961`.
- Public Ubuntu and built-image identities, image size, Dockerfile/source
  hashes, bounded runtime package versions and build-log hash are recorded.
- Eight failed runtime discriminators and superseded clean receipt `3533859`
  are retained with their exact bounded receipts and repair reason.
- Container, built image, pulled base image, residual image list, runtime
  socket root and node-local job root all verified clean.
- Cleanup exceptions now fail the driver, and the batch finalizer independently
  requires null error, every per-object removal flag, an empty residual image
  list, no cleanup errors and both node-local roots removed. Hostile cleanup
  regressions pass.

## Not closed

- single-map ownership and package privilege-drop behavior are adapter-backed,
  not faithful multi-owner Docker semantics;
- upstream dependency resolution is mutable and the Miniconda URL is unhashed;
- no archive entry, task, prediction, gold/evaluator/rubric/result body or
  credential was opened;
- no official instance image or evaluator was run;
- zero official tasks and zero outcomes were opened;
- scientific authority delta remains `NONE`.

## Reproduction boundary

Use the exact files and hashes in this directory and the merged toolchain from
`development/p1-scienceagentbench-lunarc-runtime-v1-2026-08-24/`. Run only on
Slurm compute with graph/run roots under node-local `$TMPDIR`. Require every
credential-presence flag false, the exact PASS terminal, all image removals,
an empty residual image list, an empty cleanup-error list and node-local
directory removal.

Do not use this witness to authorize archive extraction, an official task,
evaluator access or a scientific claim.
