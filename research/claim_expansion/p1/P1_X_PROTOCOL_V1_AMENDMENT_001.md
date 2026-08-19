# P1-X Protocol V1 Amendment 001 — per-revision protected outcome binding

Date: 2026-08-19  
Parent: #529 / PR #540  
Status: `PRE_OUTCOME_SCHEMA_COMPLETENESS_REPAIR`  
Protected outcomes accessed before amendment: **NO**

## Defect found by hostile protocol implementation

The frozen V1 research question and ESRD metric require evaluating whether each candidate revision:

- restores the target;
- preserves protected invariants;
- has the correct observed reopen scope; and
- possesses external authorization.

The initial `ScientificRevisionResponsibilityCase.v1` schema bound the global protected invariant set and exact gold reopen set, but it did **not** bind those outcomes per candidate revision. That made the preservation/scope components of ESRD under-specified for cases where multiple candidate revisions restore the visible target but differ in scientific admissibility.

## Repair

`protected_gold.revision_evaluations` is now mandatory and non-empty. Each candidate evaluation binds:

- `revision_id`;
- `candidate_class`;
- `restores_target`;
- `preserves_invariants`;
- `observed_reopen_set`;
- `authorized`.

The protocol validator now fails if this protected structure is absent, open-ended, or changes the boolean/reopen types.

## Scientific consequence

None. This amendment does not change:

- the five domain families;
- the eight archetypes;
- the B1/B2/B3/P1-X semantics;
- the ESRD definition;
- the `+0.10` practical margin;
- non-regression margins;
- the donor/novelty boundary;
- any protected outcome (none exists yet).

It closes an evaluation-specification hole **before** protected case generation and therefore remains within V1 rather than creating a post-outcome protocol version.

## Authority

Result state remains `CANNOT_CHECK`. This amendment creates no scientific result or novelty authority.
