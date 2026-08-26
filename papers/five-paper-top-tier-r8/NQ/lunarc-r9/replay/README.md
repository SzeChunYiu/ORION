# R9 NQ clean-room replay gate

This directory materializes the structurally independent CR-B predicate engine
and the frozen pre-census CR-A/CR-B discriminator required by issue #1383.

## Materialized

- CR-B uses independent integer encoding, CNF occurrence-bin variables, modular
  prefix-sum states, a separate small DPLL control solver, PySAT/DRUP production
  adapter, and a literal-matrix `GL(r,5)` rank-two symmetry implementation.
- The CR-B source tree imports no Engine-A module or canonicalizer.
- `control_replay.py` completes separate Engine-A, Engine-B, and labelled-bin
  reference passes before comparing their digest-bound outputs.
- The frozen five-symbol, length-2--4, rank-two grammar contains 61 cases:
  9 positive and 52 negative. All statuses and canonical representatives agree.
- The fail-closed receipt retains `science_terminal=CANNOT_CHECK`,
  `independence_terminal=CANNOT_CHECK`, and `full_census_executed=false`.

## Exact remaining blocker

The full D2/D3 replay is **not runnable yet**. CR-B still needs a separately
generated and audited full matrix/candidate/orbit manifest. It may parse shared
immutable input bytes, but it must not wrap Engine-A canonicalized candidates,
forbidden sets, or orbit manifests. The complete normalization/census argument,
98,622 and 230,983 denominator partitions, external DRUP checking, full-resource
authorization, and a new nonduplicate key are therefore still absent.

LUNARC job 3542994 already completed the bounded Engine-A pilot. Its payload
must not be resubmitted under a renamed key.

The rank-two control PASS is engineering conformance only. It is not one of the
issue-level scientific PASS terminals and grants no D2, D3, D4, novelty, paper,
or journal authority.
