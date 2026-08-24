# P7 public non-retrieval class-partition protocol freeze

## Atomic question

Can exact containment conform to 100 distinct directed class-partition
transitions constructed over two public non-retrieval subject domains, with no
retained false closure and both preserve and reopen decisions, while remaining
honest about equivalence to a partition-refinement oracle?

## Public sources and rights

The frozen public metadata are the seven class identifiers from UCI Zoo (DOI
`10.24432/C5R59V`) and the 26 letter classes from UCI Letter Recognition (DOI
`10.24432/C5ZP40`). UCI reports CC BY 4.0 for both. Execution is standard-library
only and does not download or redistribute observations, labels, or features.

## Design and construct boundary

Within each domain, the fine contract is the singleton partition of the public
class vocabulary. The runner deterministically enumerates 25 distinct
nontrivial bipartitions and evaluates both directions against the fine contract.
This yields exactly 50 unique directed contracts per domain. Identity is bound
to source partition, target partition, and direction—never a sample index.

An obligation is an unordered pair of labels separated by a partition. Exact
containment preserves only when all target obligations occur in the source.
The gold rule and implementation instantiate this same mathematical predicate,
so accuracy is an implementation-conformance check, not external construct
validation. A strongest-donor partition-refinement oracle receives identical
information and is expected to be extensionally equivalent. The reopen-only
comparator is explicitly a negative control, not a registered-bridge baseline.

The transitions are prospective constructions over public vocabularies, not
observed changes in either UCI dataset. Zoo and Letter Recognition provide two
subject domains but only one classification-partition structural family. Rows
are not independent replications and do not support population inference.

## Chronology and execution

This increment contains a frozen protocol and runner only—no result. A later
execution must start from clean `main`, prove committed byte equality, use
Python 3.12 with only the standard library, retain every directed transition,
and refuse overwrite. Adverse, null, failed, and equivalent results are retained.

## Authority

No issue box closes at freeze time. Scientific-authority delta: **NONE**.
Independent adjudication, protected custody, and external confirmation remain
`CANNOT_CHECK`; public metadata cannot bypass them.
