# MAX-R6 native method-language gate — Erratum 1

Date: 2026-08-20
Applies to: `MAX_R6_NATIVE_METHOD_LANGUAGE_GATE_PROTOCOL.md`
Status: frozen before native N2 outcome execution.

## Defect

The frozen prose says `RESP:DONOR_CLOSURE_INCOMPLETE` predicts **at least one** of two unresolved donor conditions. `EpistemicRevisionResponsibilityHypothesis.v1`, however, represents a conjunction of registered discriminator predictions inside one hypothesis. Encoding both conditions in one hypothesis would therefore require both failures simultaneously and would be stronger than the frozen OR semantics.

## Correction

Operationally atomize the donor-incomplete category into two claim-relative responsibility hypotheses:

- `RESP:DONOR_GENERAL_M_INCOMPLETE`
  - predicts `R5H_CURRENT_ALPHABET_EXACT = YES`;
  - predicts `GENERAL_M_DONOR_OUTCOME = DOMINATES_OR_INCONCLUSIVE`.

- `RESP:DONOR_INTERFACE_UNRESOLVED`
  - predicts `R5H_CURRENT_ALPHABET_EXACT = YES`;
  - predicts `FOQCS_INTERFACE_ENVELOPE = UNRESOLVED`.

Both bind to the same generic revision mechanic:

`REV:ABSORB_DONOR`.

This is a representation correction only. It does not change any observed outcome, candidate revision, method-language hypothesis, interface hypothesis, or prospective subject state.

## Hostile consequence

Native N2 may identify method-language responsibility only if **both** donor-incomplete atomic hypotheses are defeated, in addition to the current-search and interface hypotheses being defeated.
