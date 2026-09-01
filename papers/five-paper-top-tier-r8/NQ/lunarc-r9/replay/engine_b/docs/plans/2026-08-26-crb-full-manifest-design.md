# CR-B full census manifest and partition design

## Boundary

This tranche freezes input identity only.  It does not read Engine-A aggregate
outputs, evaluate any `D_2`/`D_3` candidate, submit a LUNARC job, or claim an
independent replay terminal.  The two denominators exposed in the public issue
are treated as preregistered expected input counts, not as observations made by
this implementation.

## Objects

1. A digest-addressed enumeration of every literal matrix in `GL(3,5)`, using
   row-major base-five bytes in lexicographic matrix order.
2. A declared candidate plan for the 98,622 normalized length-19 records and
   the 230,983 structured length-25 records.
3. Contiguous half-open ordinal partitions fixed at 4,096 records before any
   full candidate stream is inspected.
4. A strict candidate-record format with byte-canonical JSON, exact ordinal and
   record-id bindings, sequence length/bin constraints, and matrix/orbit
   digests.  Result, survivor, SAT, UNSAT, and solver fields are not admissible.
5. A materializer that accepts only a complete ordinal stream, writes the
   frozen shards atomically, and emits byte/count/digest bindings.  Missing,
   duplicate, reordered, noncanonical, or extra records fail closed.

## Authority boundary

The committed declaration receipt has zero materialized candidate records and
terminal `NQ_CR_B_FULL_CENSUS_PARTITION_PLAN_FROZEN`.  Its replay authority is
`CANNOT_CHECK`.  A later byte-complete stream manifest would establish only
conformance to the preregistered ordinal plan.  Normalization completeness,
orbit completeness, predicate execution, external DRUP checking, Engine-A
agreement, `D_3`, novelty, and paper authority remain separate obligations.

