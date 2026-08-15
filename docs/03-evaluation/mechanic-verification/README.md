# Mechanic verification planning

ORION distinguishes a verification **plan** from verification **evidence**.

Systems-engineering practice commonly binds requirements to explicit verification methods such as inspection, analysis, demonstration and test, with objective closure artifacts. ORION adopts the transferable mechanism rather than assuming every research mechanic is verified by the same test family.

For every mechanic, V0 creates a minimum verification matrix with separate obligations for:

1. specification completeness/waivers (`ANALYSIS`);
2. hostile or known-answer failure-path behavior (`TEST`);
3. real interface/handoff conformance (`TEST`);
4. any empirical improvement/transfer claim (`FRESH_TRANSFER`).

These obligation identifiers may satisfy the mechanic-cell question "how will this be verified?" They do **not** represent PASS evidence. Later verification receipts must retain the exact obligation, evaluator, artifact/evidence identity, scope and result.

The first three stages deliberately mirror engineering verification discipline while preserving ORION's scientific authority boundary: a software unit test can establish implementation behavior, but cannot by itself create scientific truth or fresh-task improvement authority.

## Research lineage

The V0 transfer was informed by NASA systems/software verification guidance, including requirement-verification matrices and the distinction among inspection, analysis, demonstration and test; software guidance additionally motivates interface, hostile/stress, resource and operational-condition checks. NIST software-verification guidance provides a complementary source family emphasizing multiple testing/analysis techniques rather than a single universal method.

## Open coordinates

- step-specific acceptance predicates;
- calibration of empirical performance metrics;
- protected evaluator identity;
- which obligations require independent rather than same-context evidence;
- formal proof obligations for mechanics with mathematical semantics;
- evidence retention and supersession rules.
