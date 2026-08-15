# Empty-lineage false saturation

## Observed

At exact `main` commit `3fdff9e252ee0869b52f0e8f04b55897b38757be`,
two flat `GrowthVector` records under one frozen `SaturationBasis`, each with
the default empty `evidence_lineage`, produced:

```text
BOUNDED_SATURATED 2 2 ('flat and independent under basis c142b4ab1c19',)
```

An initial probe requested a nonexistent `SaturationReport.flat_rounds`
attribute and failed with `AttributeError`. That was an instrument failure.
The corrected probe used `flat_streak` and reproduced the system failure.

## Failure

Pairwise disjointness treats `empty set intersect empty set = empty set` as
independence. But an empty lineage states that the evidential route is unknown
or absent; it is not evidence that two flat rounds used independent routes.
The current greedy disjoint-subset count therefore converts missing lineage
into maximum independence and can stop an empty-work driver after two rounds.

## Failure class

`MISSINGNESS_AS_INDEPENDENCE` + `FALSE_BOUNDED_SATURATION`.

## Later correction and residual

PR #27 changed the runtime verdict to `A_PRIORI_FRAME_FLAT`, fixed
`certifies_recall=False`, and states that the rule says nothing about kinds
outside the frame. That repairs the false recall/saturation authority. At
`5894ac7814d194b3c60d9655af87ef2d9828d56c`, the same empty-lineage probe now
returns:

```text
A_PRIORI_FRAME_FLAT 2 2 False True
```

The remaining defect is narrower: two unknown/empty lineages are still
reported as two independent rounds and are allowed to satisfy the budget-stop
heuristic. Missingness-as-independence therefore remains open even though the
stronger saturation claim has been withdrawn.

## Correct response

- An empty evidence/route lineage is ineligible for independence credit.
- Independence requires positively identified route/evidence lineages under a
  declared separation relation, not only set non-overlap.
- Distinguish `NO_GROWTH_OBSERVED`, `DEPENDENT_FLAT`, `CANNOT_CHECK_LINEAGE` and
  `BOUNDED_SATURATED`.
- Bind the stopping receipt to the exact search universe, route executions,
  evidence lineage and residual/reopen audit.

## General lesson candidate

Absence of a dependency label is not independence. Missingness must fail closed
whenever a safety or epistemic decision depends on knowing the missing relation.

## Residuals and reopen coordinates

- empty, partial, aliased and revoked lineages;
- route-label spoofing versus host-observed route execution;
- alternative live support sets and dependency-aware invalidation;
- saturation after basis/evaluator/search-universe change.
