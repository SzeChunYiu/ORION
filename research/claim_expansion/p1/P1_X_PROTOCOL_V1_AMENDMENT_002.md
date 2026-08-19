# P1-X Protocol V1 Amendment 002 — candidate reopen-scope proposal binding

Date: 2026-08-19  
Parent: #529 / PR #540  
Status: `PRE_OUTCOME_SCHEMA_COMPLETENESS_REPAIR`  
Protected outcomes accessed before amendment: **NO**

## Defect found by dev-generator design

The `REOPEN_SCOPE_MISMATCH` archetype requires the controller to observe what reopen scope a candidate revision proposes and compare it with the protected affected/reopen scope. The initial schema exposed only candidate revision identifiers, so an over-broad or under-broad proposal could not be represented without inferring hidden intent.

## Repair

`candidate_visible.revision_proposals` is now mandatory and non-empty. Each proposal binds:

- `revision_id`;
- `candidate_class`;
- `proposed_reopen_set`;
- `declared_protected_invariants`.

Protected actual outcomes remain separately bound in `protected_gold.revision_evaluations`. This preserves the candidate-visible/protected-gold firewall while making scope fidelity directly testable.

## Scientific consequence

None. This amendment changes no domain, archetype, comparator semantics, hypothesis, practical margin, non-regression gate, donor boundary or protected result. It closes a representation hole before protected generation.

## Authority

Result state remains `CANNOT_CHECK`. No scientific or novelty claim is promoted.
