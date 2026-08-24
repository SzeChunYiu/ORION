# Open-world reference identification theorem

## Statement

Let `U` be a frozen candidate universe and let `R+` be an observed reference
alignment that asserts some positive equivalences.  If the source authority does
not additionally certify that `R+` is exhaustive over `U`, then for every
`x in U \ R+` the binary truth of `x` is not identified by `(U,R+)` alone.
Both `GLUE` and `OBSTRUCTION` remain observationally compatible.  Therefore
reference absence cannot by itself license an `OBSTRUCTION` label or a
single-valued harm score.

## Proof

Fix an unlisted candidate `x`.  One world contains a true equivalence at `x`
that the non-exhaustive reference omitted; another contains no equivalence at
`x`.  Both worlds produce the same observed candidate universe and positive
reference alignment.  They disagree on the binary truth of `x`.  Hence the
truth is not identified.  Calling `x` an obstruction adds a closed-world
exhaustivity axiom that is not present in the observations.  The identified set
is `{GLUE, OBSTRUCTION}` until an authoritative negative assertion or an
exhaustivity certificate removes one of the worlds.

## V3 audit witness

The immutable V3 join implementation assigns `GLUE` to an explicit equivalence
and assigns `OBSTRUCTION` in the residual `else` branch for any pair inside the
reference entity domains (`p3_cross_construct_successor.py`, lines 526--534).
The retained join receipt reports 1,399 explicit `GLUE` pairs and 116,515 such
residual `OBSTRUCTION` assignments.  These counts establish how the V3 binary
evaluation was constructed; they do not establish that all 116,515 absences
are source-certified negatives.

This does **not** alter the preserved V3 terminal.  It types V3 harm as
conditional on the V3 closed-world construction and prevents its obstruction
semantics from being transported silently into V4.

## Consequences for V4

1. A family is binary-scorable only if an authoritative source certifies an
   exhaustive frozen universe or supplies explicit negative/disjointness truth.
2. A positive-only reference may still certify observed `GLUE` cases, but its
   omissions must remain `{GLUE, OBSTRUCTION}` or `CANNOT_CHECK`.
3. Matcher nonselection cannot substitute for missing negative truth.
4. Comparator accuracy and harm are undefined on unlicensed omissions; a
   runnable comparator does not repair the missing estimand.
5. Pooling many omitted pairs does not create evidence.  The source family,
   not the pair count, remains the independent replication unit.

## Wider claim

The result is not specific to ontology matching.  It applies to any benchmark
whose annotations record discoveries but do not certify exhaustive negatives:
unlabelled candidates are partially identified, and point-valued evaluation is
necessarily assumption-conditioned.  The scientifically stronger target is an
**authority-aware identification envelope** that reports which conclusions are
identified by observations and which require an explicit closure axiom.

## Boundary

This is a formal non-identification result, not evidence that any particular
new OAEI family is non-exhaustive.  V4 must determine that from metadata and
rights without opening new-family outcomes.  Protected evidence, P3 coordinate
claims, and population transport remain `CANNOT_CHECK`.

