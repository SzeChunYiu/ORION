# P3/P9/P11/P15 active-lifecycle repair

## Question

How can the paper programme identify exactly one current authority leaf per
claim without erasing negative history, treating repeated projections as new
measurements, or promoting a paper that has no protected result?

## Atomic audit

- P3 has five result artifacts with the same record identity and no external
  machine-readable leaf selection. Amendment 004 must be selected explicitly by
  content, never by date or filename.
- P9's T4 adverse result is reproducible. T3's scientific coordinates reproduce
  at 0/1344, but the current runner emits an additional environment-agreement
  block absent from the committed status artifact. That is a metadata amendment,
  not permission to overwrite the historical status.
- P11I is a positive r=7 successor. P11H remains an adverse r=3 boundary. Width
  scopes are disjoint and must be held as two leaves, not called universal
  supersession.
- P15 has no protected result. Its lifecycle state is `NO_SCIENTIFIC_RESULT`,
  not a failed H1 and not a positive inferred from retrospective tests.

## Frozen repair

1. Add content-bound lifecycle artifacts and validators.
2. Preserve every predecessor/result byte.
3. Require exactly one explicit active adjudicative leaf where a leaf exists.
4. Keep scoped historical/adverse leaves queryable.
5. Distinguish metadata amendments from scientific successor results.
6. Represent no-result and not-applicable lifecycle states without converting
   them to PASS or CANNOT_CHECK.

## Reopen triggers

Reopen if a digest changes, a filename/date heuristic selects authority, more
than one active leaf appears for one scope, P11 r=3 is hidden by r=7, P9 metadata
changes a frozen scientific coordinate, or P15 gains authority without a
prospectively frozen result.
