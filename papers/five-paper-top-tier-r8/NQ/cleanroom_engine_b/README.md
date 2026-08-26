# NQ clean-room Engine B

Engine B is a structurally different SAT formulation of the exact
`k`-disjoint-zero-sum predicate in `C_5^3`. It starts from a local base-five
encoding and primitive componentwise addition. It does not open, import, or
copy existing NQ algorithms or result files.

## What is implemented

- exact `C_5^3` encoding and addition;
- a no-pruning SAT automaton for one to four disjoint nonempty factors;
- a slow subset/partition reference for small controls;
- SAT witness and hash-bound UNSAT-proof certificate formats;
- canonical JSONL input records and coverage manifests;
- guarded parallel PySAT execution;
- deterministic source and receipt bindings;
- a local, version-pinned solver runtime specification;
- a CPU-only 32-core, 128-GB, 24-hour SLURM script.

## Authority

Public issue and programme text exposed expected early-constant counts before
implementation. Blinded independence is therefore not claimed. Local fixture
tests and Engine B execution are engineering evidence only. Full replay still
requires Engine A agreement, proof audit of census coverage, and external DRUP
checking where UNSAT records occur.

`D_4(C_5^3)` remains OPEN. Partial support strata do not close it. Allocation
exhaustion is `CANNOT_CHECK_RESOURCE_BOUND`, never a theorem or counterexample.

No job is submitted from this directory before root review and a hash-bound
input bundle is supplied.
