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
