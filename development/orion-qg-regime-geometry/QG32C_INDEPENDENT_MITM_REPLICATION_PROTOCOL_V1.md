# ORION-QG QG-32c — independent exact meet-in-the-middle replication

Date: 2026-08-22
Parent programme: #740
Direct earned parent: QG-32 #911 (certified fixed five-probe upper bound only)
Primary candidate under replication: QG-32b #918 / draft PR #919 production lane, which returned NO for <=4 but whose frozen independent MILP timed out. QG-32b therefore has no exact-minimum authority.

## Status

**POST-RESULT INDEPENDENT REPLICATION. FROZEN BEFORE ANY QG-32c DECISION.**

The primary QG-32b production candidate is visible: exhaustive depth-4 search found no <=4 separator. This protocol does not treat that result as authority and does not reuse its search tree, memo table, branching order, or result receipt.

QG-32c asks only:

> Independently reconstructing the QG-32 observation problem from the already-earned QG-32 primitives, does any set of at most four indexed probes separate all 5,895 unresolved pairs inside the 92 joint bulk+spectrum classes?

Both outcomes are allowed:
- `QG32C_INDEPENDENT_REPLICATION_CONFIRMS_NO_FOUR_PROBE_SEPARATOR`
- `QG32C_INDEPENDENT_REPLICATION_FINDS_FOUR_OR_FEWER_SEPARATOR`

## Frozen independent method

1. Reconstruct from QG-32 generic primitives only:
   - 715 local-response orbit representatives;
   - 384 indexed probe coordinates;
   - 92 joint bulk+spectrum classes;
   - 5,895 unresolved orbit pairs;
   - physical-probe coverage bitsets.
2. Collapse identical coverage classes, retaining a deterministic representative probe.
3. Remove only coverage-dominated classes: if coverage(A) is a subset of coverage(B), A can never be required by a minimum-cardinality cover when B is available.
4. Enumerate **every unique union attainable with zero, one, or two retained probe classes**. Keep a deterministic witness for each union mask.
5. Exact meet-in-the-middle decision: a <=4 cover exists iff two enumerated half-unions have union equal to the complete 5,895-pair universe. Candidate lookup may use posting-list intersections as an exact filter, but every survivor is verified against the complete bitset.
6. If YES, serialize and independently recheck the <=4 physical probe witness against all 5,895 unresolved pairs and all 715 indexed identities.
7. If NO, the exhaustive 2+2 union decision is the lower-bound certificate `minimum >= 5`. Combined with QG-32's already-earned five-probe upper bound, this may authorize exact fixed minimum 5 for the indexed-identity query only.

## Independence discipline

The QG-32c solver must not import or read:
- `qg32b_four_probe_feasibility.py`;
- QG-32b production artifacts/receipts;
- QG-32b memo/search statistics;
- any QG-32b witness field.

The primary candidate may be compared to the QG-32c decision **only after** the QG-32c decision object is sealed.

## Verification

Production/replication lane: exact meet-in-the-middle 2+2 cover decision from QG-32 generic primitives.

Generic verifier: independently replay the returned decision certificate:
- YES: verify witness size <=4 and full coverage;
- NO: independently regenerate the complete half-union family and require no complement-cover pair exists, using a different half ordering/filter implementation.

Native ORION-Q: authorize only the fixed indexed-probe minimum/witness on the QG-32 observation problem.

Workflow requires deterministic replay and a self-consistent decision/witness tamper rejection.

## Hard boundaries

Always false:
- adaptive-tree optimality (QG-34 is separate);
- full finite-n optimum probes;
- hardware/measurement minimum;
- QG-28 global state minimality;
- novelty authority;
- physical quantum advantage.

## Promotion rule

If QG-32c independently returns NO and its verifier/native/replay/tamper gates are GREEN, QG-32b's production candidate and QG-32c replication together may support:

`QG32_FIXED_INDEXED_PROBE_MINIMUM_IS_FIVE__INDEPENDENTLY_REPLICATED`

This promotion is scoped only to exact indexed local-response identity after the frozen joint bulk+spectrum summaries.