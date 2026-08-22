# ORION-Q MAX-R4E-A — authority-indexed abstraction router protocol

Date: 2026-08-22
Issue: #908
Parent: MAX-R4E #903 / MAX #679
Execution branch: `codex/orion-q-max-r4ea-authority-router-20260822`
Status: **FROZEN BEFORE PROTECTED ROUTER OUTCOME.**

## Scientific question

Can the QG-derived research operator

> choose the least-detailed representation/proxy whose earned authority contains the requested query, otherwise escalate or abstain

strictly improve ORION-Q's research-control policy on frozen real compiler-science receipts?

This is a mechanism calibration, not a held-out language-model or novelty claim.

## Frozen evidence bindings

The evaluator must bind exact committed receipts, never prose summaries:

- QG-31 query-indexed abstraction result;
- QG-28 715-orbit finite-size sufficient statistic;
- QG-15b SixLCU/StabPrep predicate-language result;
- QG-9 V6 R6I support-1 normalization result;
- MAX-R4B split-TARE majorization result;
- MAX-R4D H2O DUCC implementation-aware result.

If any required receipt is absent or its expected authority flags fail, return `CANNOT_CHECK`.

## Frozen query vocabulary

Queries are semantic capability tags, not family names:

- `ASYMPTOTIC_BULK_VALUE`
- `UNLABELED_LOCAL_DEFECT_SPECTRUM`
- `INDEXED_LOCAL_RESPONSE`
- `FULL_FINITE_OPTIMUM`
- `DONOR_OPTIMAL_LABEL`
- `SUPPORT_NORMAL_FORM`
- `COEFFICIENT_SUBNORMALIZATION`
- `TOTAL_COMPILED_RESOURCE`
- `FULL_CIRCUIT_OR_NOVELTY`

## Frozen route vocabulary and burden order

Burden is used only to choose among already-authorized routes; it is not a scientific cost claim across families.

1. `ONE_LITERAL_PREDICATE`
2. `SUPPORT1_NORMAL_FORM`
3. `COEFFICIENT_THEOREM`
4. `BULK45`
5. `SPECTRUM54`
6. `ORBIT715`
7. `INDEXED715`
8. `EXACT_RICH_STATE`
9. `IMPLEMENTATION_AWARE_RESOURCE`
10. `CANNOT_AUTHORIZE`

`CANNOT_AUTHORIZE` is not an optimization route and is selected only when the requested claim exceeds every supplied receipt.
`IMPLEMENTATION_AWARE_RESOURCE` is an escalation/research route: selecting it for `TOTAL_COMPILED_RESOURCE` does not itself authorize a total-resource result.

## Frozen cases

The evaluator constructs exactly ten cases from receipt flags. Each case contains only:
- query tag;
- candidate route contracts (`supports` set + burden rank + route kind `ANSWER|ESCALATE|ABSTAIN`);
- receipt identifiers/digests for evaluator use only.

Family names, expected route, terminal labels and ground-truth outcome are excluded from router input.

### Case semantics

1. TARE asymptotic bulk: `BULK45` authorized; a richer orbit-count route can also recover it but is avoidably rich.
2. TARE unlabeled local defect spectrum: `SPECTRUM54` authorized; `BULK45` unauthorized; a richer exact orbit/local-state route is authorized.
3. TARE indexed local response: `INDEXED715` is the frozen minimal response representation.
4. TARE full finite optimum: `ORBIT715` sufficient by QG-28; `BULK45`/`SPECTRUM54` unauthorized; QG-31 does not claim global minimality.
5. SixLCU donor-optimal label: `ONE_LITERAL_PREDICATE` authorized by the QG-15b zero-error K1D1 result; exact rich state also authorized.
6. StabPrep donor-optimal label in frozen 13-feature vocabulary: compact predicate route unauthorized because of mixed cells / `E_floor=43`; `EXACT_RICH_STATE` required.
7. R6I support-normal-form: `SUPPORT1_NORMAL_FORM` authorized all-n; exact rich state also authorized.
8. Split-TARE coefficient subnormalization: `COEFFICIENT_THEOREM` authorized by MAX-R4B; implementation-aware analysis is richer and avoidable for this query.
9. Split-TARE total compiled resource: `COEFFICIENT_THEOREM` unauthorized for the query; `IMPLEMENTATION_AWARE_RESOURCE` is the correct escalation route.
10. Full-circuit/R5/novelty claim from MAX-R4D receipt: supplied receipt explicitly lacks that authority; route must be `CANNOT_AUTHORIZE`.

## Baselines

### B0 conservative-richest
Among authorized non-abstention routes, choose the highest-burden route. If the claim exceeds all authority, abstain.

### B1 aggressive-smallest
Choose the lowest-burden non-abstention route offered, ignoring authority scope. If no route is offered, abstain.

### B2 authority-indexed
1. discard every route whose `supports` set does not contain the query;
2. choose the lowest-burden remaining route;
3. escalation routes count as correct routing but do not create scientific authority beyond the downstream verifier;
4. otherwise return `CANNOT_AUTHORIZE`.

B2 may inspect route contracts and query tags only. It may not inspect family names, case IDs, expected routes or gold labels.

## Frozen metrics

For each baseline report:
- correct-route count / 10;
- false-authority count;
- overcompression count;
- avoidable-rich-state count;
- compact-authorized opportunities captured;
- correct escalation/abstention count;
- TARE selected representation sizes for cases 1–4 as `[45|54|715|715]` where applicable;
- exact output-equivalence/binding checks where multiple authorized routes are supported by the same committed receipt.

A route is correct iff it is the lowest-burden route whose frozen contract contains the query, except case 10 where `CANNOT_AUTHORIZE` is correct.

`avoidable-rich-state` means the baseline selected a strictly higher-burden authorized route than the frozen minimum.
`overcompression` means a lower-burden route was selected whose authority does not contain the query.
`false-authority` means an `ANSWER` route was selected outside its authority scope; a wrong `ESCALATE` route counts as routing error/overcompression but not as an asserted scientific result.

## Positive terminal

`MAX_R4EA_AUTHORITY_INDEXED_ROUTER_PARETO_DOMINATES_STATIC_ABSTRACTION_POLICIES_ON_REAL_RECEIPTS`

requires:
- B2 correct-route count = 10;
- B2 false-authority = 0;
- B2 overcompression = 0;
- B2 avoidable-rich-state = 0;
- B2 captures every compact-authorized opportunity;
- B0 false-authority = 0 but has >=1 avoidable-rich-state use;
- B1 has >=1 false-authority or overcompression event;
- B2 correctly escalates StabPrep and total-resource cases and abstains on full-circuit/novelty case.

## Authority boundary

A positive establishes only a deterministic exact research-control mechanism on these frozen real receipts. It does **not** establish:
- held-out or cross-domain generalization;
- autonomous language-model skill selection;
- improved theorem discovery;
- general quantum-science superiority;
- novelty.

Successor MAX-R4E-B must remint/hold out cases and place the same operator into the protected skill-selection/admission machinery.