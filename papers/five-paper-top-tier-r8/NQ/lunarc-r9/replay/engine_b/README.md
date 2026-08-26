# NQ clean-room Engine B

Engine B is a structurally different SAT formulation of the exact
`k`-disjoint-zero-sum predicate in `C_5^3`. It starts from a local base-five
encoding and primitive componentwise addition. It does not open, import, or
copy existing NQ algorithms or result files.

## What is implemented

- exact `C_5^3` encoding and addition;
- a no-pruning SAT automaton for one to four disjoint nonempty factors;
- an independent literal-matrix `GL(r,5)` symmetry implementation for the
  frozen rank-at-most-two pre-census controls;
- a slow subset/partition reference for small controls;
- SAT witness and V2 byte-bound DIMACS/DRUP UNSAT certificate formats;
- a source-pinned external `drat-trim` packaging protocol and one materialized
  negative engineering control;
- canonical JSONL input records and coverage manifests;
- guarded parallel PySAT execution;
- deterministic source and receipt bindings;
- a local, version-pinned solver runtime specification;
- a CPU-only 32-core, 128-GB, 24-hour SLURM script.

## Authority

Public issue and programme text exposed expected early-constant counts before
implementation. Blinded independence is therefore not claimed. Local fixture
tests, the one externally checked DRUP control, and Engine B execution are
engineering evidence only. Full replay still requires Engine A agreement,
proof audit of census coverage, full byte-bound input partitions, and external
DRUP checking for every UNSAT record in a complete bundle.

The materialized external control proves only that the pinned checker can
verify the existing small negative fixture against an independently rebuilt
Engine-B DIMACS file. It does not run the 98,622- or 230,983-record censuses,
audit their partitions, or create scientific or paper authority.

`D_4(C_5^3)` remains OPEN. Partial support strata do not close it. Allocation
exhaustion is `CANNOT_CHECK_RESOURCE_BOUND`, never a theorem or counterexample.

No job is submitted from this directory before root review and a hash-bound
input bundle is supplied.

## Frozen two-engine discriminator

`../control_replay.py` runs the issue-mandated smallest complete discriminator
before any target census. It enumerates all 61 rank-two multisets of lengths
2--4 over the exact five-symbol alphabet declared in `../CONTROL_PROTOCOL.json`.
Every case is checked by Engine A, Engine B, and a tiny labelled-bin reference.
The receipt binds per-case status, representative digest, matrix-action orbit
digest, CNF digest, aggregate range digests, and any disagreement witness.

This control is intentionally engineering-only. It does not execute the
98,622- or 230,983-record censuses and cannot reach an issue-level scientific
PASS terminal.
