# P6 public selective-revalidation protocol freeze

## Atomic question

Across 100 public first-parent change sets in each of three domains, does exact
reverse dependency closure avoid invalid certificate retention and save work
relative to full reset, while honestly retaining equivalence to the strongest
equal-information native dependency selector?

## Frozen public sources

- nf-core/rnaseq at `1f03b53ef799e298f60c813440e961e867017043`
  (MIT): scientific workflow `.nf`/`.config` artifacts and Nextflow include
  syntax.
- Mathlib4 at `dc84fcbe9e049439c1c36d6db290cc0565f77788`
  (Apache-2.0): `Mathlib/**/*.lean` artifacts and Lean import syntax.
- Gene Ontology at `97b20201b32a62e0ca8a07743743b8fdc1f2a1a1`
  (CC BY 4.0): ontology source artifacts and resolvable import declarations.

License file Git-blob identities are frozen. Execution retains commit IDs,
changed paths, graph hashes, counts and decisions, but no upstream source-file
contents.

## Estimand and comparators

The frozen-head artifact/import graph defines the estimand. For each repository,
the runner walks first-parent history and retains the first 100 commits whose
changed paths intersect that graph. Full reset selects every artifact. Native
dependency selection and P6 selective revalidation both select the changed
artifacts plus their reverse-transitive dependents. Equality is expected.

The endpoint is saved artifact revalidations versus full reset. A deterministic
contiguous 10-change block resampling supplies a lower-quantile sensitivity
analysis. It has no stochastic coverage guarantee: stationarity, mixing and a
justified block length are not established. Serial dependence remains explicit,
the inferential 95% gate stays `CANNOT_CHECK`, and there is no population claim.

## Construct boundary

This is a prospective replay of historical change sets against dependency
syntax parsed by ORION at the frozen head. It is not a checkout-by-checkout
native build/test or native-tool replay. Deleted paths and historical
dependencies absent from the frozen-head universe are excluded. Resolved,
unresolved and ambiguous imports are counted. The syntax closure is also the
gold, so zero error demonstrates conformance, not independent semantic
validation or novelty.

## Chronology and authority

An initial clean-main execution attempt was interrupted during nf-core graph
materialization because partial-clone `git show` issued one fetch per blob. It
created no result file and exposed no metric. This amended freeze adds one
detached exact-head checkout before parsing, allowing Git to batch missing head
blobs; the exact fetched SHA and materialized `HEAD` must both match.

This increment freezes the repaired protocol and runner and contains no outcome. A later
execution must start from clean `main`, bind committed bytes, use Python 3.12 and
Git 2.51.1, fetch each exact frozen commit SHA, and retain adverse, null and
zero-savings rows. Every attempted domain emits either an executed terminal or
a hashed `CANNOT_CHECK` failure receipt; one failed domain blocks every gate.

No issue box closes at freeze. Scientific authority delta: **NONE**. Independent
adjudication and protected custody remain `CANNOT_CHECK`; public Git history
cannot bypass either.
