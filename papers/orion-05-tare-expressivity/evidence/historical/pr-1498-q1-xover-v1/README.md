# ORION-05 historical custody: PR #1498 Q1-XOVER V1

This directory is an **additive historical evidence archive**, not a new
experiment and not a positive-result successor.  The `raw/` subtree materializes
all 14 files added by PR #1498 head
`272f2a1aa7b63d409fc460b35bb89e4aa8b5dcbb`, byte for byte.  The same head is
kept reachable by the lightweight tag
`archive/orion-01-05/pr-1498-head-272f2a1aa7b6`.

The controlling historical observation remains:

> `RUN_INCOMPLETE`: on the frozen sampled panel and machine budget, 372/372
> old direct-D++ cells at n<=5 completed exactly, while 12/12 sampled n=6 cells
> timed out at 600 seconds per cell.

Nothing here rewrites the raw receipt, its P6=false field, either LUNARC log, or
the recorded timeouts.  The archive also preserves the later authority
correction already bound by the ORION-05 R11 status:

- registered P6 did not predict zero timeouts;
- the evaluator added an unregistered `timeouts == 0` clause;
- its structural clause iterated the n<=6 panel, not the named n=8/n=12
  chemistry/fresh collections; and
- therefore P6=false is not authority for a general prediction refutation.

The archived runner executed the legacy `r6p.dxx_search` 4^(2n)-table direct
D++ implementation.  It did **not** execute the later sparse O(n^9) solver.
Accordingly this archive cannot establish a general positive crossover, refute
the sparse O(n^9) theorem, or establish production acceleration/resource value.

## Source-archive limitation retained

The sole archived `source.tar.gz` has SHA-256
`c00eab9252826426b3f44ee50978722af84b8cf6a0861458baedd33d9aec959d`.
It matches `SUBMISSION.run1.json` (job 3544037), but it does not match the run-2
hash `5dcaab...` in `SUBMISSION.json` (job 3544067).  The run-2 source archive is
not one of the 14 donor files and is not materialized here.  Both logs remain
present; this limitation is recorded rather than repaired or silently blurred.

## Verification

`ORION05_PR1498_CUSTODY_V1.json` binds, for every raw file, the donor commit,
original and archived paths, Git mode, Git blob, SHA-256, and byte count.
`verify_orion05_pr1498_custody_v1.py` checks those bindings, the archive tag,
the exact donor diff, the adverse coverage counts, the timeout/coverage defects,
the source-archive limitation, both run logs, and the no-promotion policy.  It
does not rerun the science.
