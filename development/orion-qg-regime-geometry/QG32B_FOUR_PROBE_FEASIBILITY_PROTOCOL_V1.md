# ORION-QG QG-32b — exact four-probe feasibility above joint bulk+spectrum V1

Date: 2026-08-22
Issue: #918
Parent: QG-32 #911 / committed upper-bound-only result
Execution branch: `codex/orion-qg-qg32b-four-probe-20260822`
Status: **FROZEN BEFORE ANY QG-32b FOUR-PROBE OUTCOME.**

## Scientific question

QG-32 has certified a five-probe separating set above the exact joint bulk+spectrum summaries, but has no minimum authority.

Freeze the exact decision problem:

`EXISTS_P4 := exists P subset {0,...,383}, |P| <= 4, such that (A_joint(o), K_P(o)) is injective on all 715 orbit types.`

No outcome is predicted.

## Parent reconstruction

Before reading the QG-32 committed receipt, each computational lane must independently reconstruct:
- 715 local-Clifford orbit representatives;
- 384 indexed one-active probe responses;
- 92 joint `(bulk signature, unlabeled defect spectrum)` classes;
- 5,895 unresolved pairs inside those classes;
- pair/probe distinction relation.

Only after this reconstruction may it bind QG-32's committed upper-bound receipt and verify the certified five-probe separator.

## Production exact branch search

1. Collapse physical probes with identical unresolved-pair coverage.
2. Remove a coverage class if its covered-pair set is a strict subset of another retained class; this is safe for the existential `<=4` decision because the dominating class can replace it without increasing cardinality.
3. Represent unresolved-pair coverage as exact integer bitsets.
4. Run a complete depth-limited search with at most four selected coverage classes.
5. At each state choose an uncovered pair with the fewest candidate retained coverage classes.
6. Branch deterministically over candidates in descending uncovered-pair coverage, then canonical class index.
7. Use only admissible prunes: no-progress, memoized `(remaining_pairs, slots)`, and `ceil(remaining_pair_count / maximum_single_class_remaining_coverage) > slots`.

Production must return either:
- a physical <=4-probe witness that independently separates all 715 identities above joint summaries; or
- an exact `NO` after exhausting the decision search.

Serialize node count, memo hits, bound prunes, retained coverage-class count and a digest of the complete reconstructed coverage-class family.

## Generic independent exact feasibility

Generic ORION independently rebuilds the semantics from phase-free `F_2^2` / F3 primitives and does **not** import production branch state.

Its primary decision method is an independent binary feasibility MILP over its own collapsed coverage classes:
- every one of the 5,895 unresolved pairs must be covered;
- `sum x_p <= 4`;
- integrality exact;
- objective zero.

If the MILP proves infeasible, it confirms `NO`. If it returns a feasible point, generic must reconstruct and validate the physical witness. If the exact solver cannot decide within the protected budget, return `CANNOT_CHECK`; do not infer from production alone.

A later successor may replace the generic MILP with an exact meet-in-the-middle certificate if needed; no solver-timeout result earns authority.

## Native ORION-Q authority

### If `EXISTS_P4 = false`
QG-32's already certified five-probe separator plus QG-32b's exact no-four proof earns:

`MINIMUM_FIXED_PROBE_CARDINALITY = 5`

Scope only:
`joint bulk+spectrum summary -> complete indexed one-active local-response identity` on the frozen 715-orbit universe.

### If `EXISTS_P4 = true`
Authorize only:
- the explicit <=4 physical probe witness;
- its exact separation property.

No minimum authority is earned unless smaller cardinalities are separately closed.

## Tamper controls

Workflow must reject a self-consistent semantic tamper after recomputing digest:
- NO outcome: flip to YES and insert a bogus <=4 probe witness;
- YES outcome: delete or alter one witness probe / separation flag.

## Mandatory false in either outcome

- minimum probes for full finite-n optimum;
- minimum hardware measurements;
- adaptive decision-tree optimality;
- global QG-28 state minimality;
- generic set-cover/active-learning novelty;
- physical quantum advantage.

## Allowed terminals

- `QG32B_FOUR_PROBE_SEPARATOR_EXISTS__WITNESS_MACHINE_CHECKED`
- `QG32B_NO_FOUR_PROBE_SEPARATOR__FIVE_IS_EXACT_MINIMUM_MACHINE_CHECKED`
- `QG32B_GENERIC_NATIVE_DISAGREEMENT`
- `QG32B_CANNOT_CHECK`

## Donor subtraction

Depth-limited set-cover search and binary feasibility MILP are donor methods. Candidate value is only the exact TARE-specific fixed-probe cardinality closure and its query-scoped active-verification consequence.