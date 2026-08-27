# ORION-05 Round-2 production benchmark execution packet

This packet executes the prospectively frozen protocol committed before any
benchmark outcome. It is a CPU-only, open-subject comparison and does not open
or alter protected Task-3/P9 evidence.

## Exact execution model

- site: LUNARC `hep` CPU partition;
- account: `hep2023-1-3`;
- one node, one Slurm task, 16 logical CPUs, 32 GiB, one-hour outer limit;
- Python 3.11.5 and NumPy 2.4.6 from the existing LUNARC software tree;
- at most 16 fresh single-process attempts, each affinitized to one allocated
  logical CPU and with BLAS/OpenMP thread counts fixed to one;
- frozen 120-second solver limit per attempt;
- new result directory, restrictive umask, raw attempts retained and final
  files made read-only.

The deployment is an exact Git archive of the runner commit. `SOURCE_COMMIT.txt`
and the two required environment variables bind the staged bytes to that
commit. The script refuses a pre-existing result directory.

## Authority

The runner may emit only one of the three predeclared R12 terminals. Timings are
machine-specific. The exact-cost/witness gates control correctness. The result
cannot establish generic TARE, physical-resource, novelty, external-review,
venue, or submission authority.

## Post-execution disposition

Attempt 1 (job `3549585`) completed all 120 measurement children but failed in
the post-measurement environment receipt because the exact source archive had
no `.git` directory. Its raw bytes and scheduler failure are retained without
a round terminal. A defect-only source-binding repair was committed before a
new run root was created.

Attempt 2 (job `3549607`) completed successfully and emitted
`ORION05_R12_EXACT_BUT_NO_PRODUCTION_VALUE`. The unrestricted referee completed
the six full-subject cells, while the support-two lane timed out on all six at
the frozen 120-second limit. `EXECUTION_CUSTODY.json`, the two immutable attempt
directories, and `ATTEMPT1_ATTEMPT2_COMPARISON.json` bind the failure, result,
and the post-terminal comparison. Round 2 is consumed adversely; no threshold
or exposed-subject retuning is permitted.
