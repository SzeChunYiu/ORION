# P6 public selective-revalidation result packet

Date: 2026-08-24
Execution source: `main@573e69d232a20bf62f1a18095d3bdc9b35924f0d`

## Development question

Can the frozen P6 protocol execute over at least three licensed public Git
domains and at least 100 change sets per domain while retaining the strongest
registered comparator, descriptive savings, mutations, and all adverse
boundaries?

## Frozen inputs

The unchanged protocol fixes exact commits and license blobs for:

1. `nf-core/rnaseq` (MIT), scientific workflow;
2. `leanprover-community/mathlib4` (Apache-2.0), formal mathematics;
3. `geneontology/go-ontology` (CC-BY-4.0), versioned ontology.

The live runner acquired each exact commit, materialized it once, walked the
first-parent history, and retained the first 100 eligible change sets. No result
row was selected or removed by outcome.

## Fail-closed review contract

`check_p6_public_selective_revalidation_result_v1.py` binds the result bytes,
internal receipt, protocol bytes and semantics, runner bytes, clean-main source
commit, exact historical Git blobs, dataset order, acquisition receipts, 300
unique commit rows, selector hashes/counts, savings arithmetic, mutation totals,
and exact authority terminals. It rejects Boolean/float aliases, extra keys,
source drift, custody/superiority escalation, and import-audit arithmetic drift.
Exact per-domain graph, acquisition-receipt, and ordered retained-row digests
prevent a rebound attacker from substituting fabricated histories or moving
outcomes between rows while preserving aggregates. Duplicate JSON keys are
rejected at every nesting level so first-wins and last-wins consumers cannot see
different authority states.

## Result and authority boundary

The data and comparator-execution tasks are satisfied. Savings versus full reset
are positive, but the parsed native-syntax comparator exactly ties the proposed
selector. This is a donor-equivalence result, not superiority.

There are 188 unresolved imports/includes. Actual repository-native build/test
or dependency-tool replay, semantic target-obligation confirmation,
simultaneous 95% inference, independent adjudication, and protected custody are
all outside this result and remain `CANNOT_CHECK`. The public-data run cannot be
used as a workaround for those requirements.

The validator authenticates the exact retained runner output; it does not
independently reconstruct the three upstream repositories offline. Thus it does
not create independent provenance or native semantic confirmation.

## Reopen routes

- execute repository-native dependency/build/test tools at compatible historical
  revisions and retain tool/version/environment receipts;
- resolve or formally classify every currently unresolved import/include;
- freeze a comparator whose selection predicate is independently implemented;
- obtain independent replication/adjudication and protected outcome custody;
- predeclare a population and dependence-aware inferential design if population
  claims are wanted.
