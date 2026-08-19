# P1-X protected execution contamination/exclusion manifest V1

Date: 2026-08-19  
Base: `main@ae6ee89faa4ba5de8d03509753b406ef32eb5c7d`  
Protected identity freeze: `P1_X_PROTECTED_FREEZE_V1.json`  
Status: `FROZEN_BEFORE_PROTECTED_GOLD_GENERATION`

## Candidate/controller exclusions

Before protected execution, B1/B2/B3/P1-X controller code may use only:

- the frozen protocol/schema/baseline registry;
- the 200 `NON_AUTHORIZING_DEV` cases;
- candidate-visible fields of an execution case;
- runtime check responses requested through the common execution interface;
- generic Python standard-library computation.

Controllers may not read:

- `protected_gold` directly;
- protected result files or aggregate statistics;
- old P1 v2.2.4 result labels as target labels for this successor;
- the exact protected case terminal/revision answer before execution;
- hidden case-generation branches keyed on controller identity;
- any future manuscript wording as a scoring signal.

## Case-generation exclusions

Protected cases are generated only from:

- the precommitted namespace and identity grammar;
- frozen domain/archetype mechanics already represented in the dev generator;
- variant index 1..10;
- deterministic transformations independent of controller outputs.

The protected generator may not inspect controller predictions or protected aggregate performance while constructing later cases. All 400 cases are generated as one immutable bundle before analysis.

## Analysis exclusions

- Primary ESRD and margins are unchanged from the merged protocol.
- No case deletion, reweighting, new primary endpoint, margin relaxation, or comparator replacement after outcome access.
- B3 is an equivalence boundary and is not significance-tested against P1-X.
- Per-domain results and all null/harmful cases remain visible.

## Outcome-access chronology

1. identity/seed commitment: frozen;
2. contamination manifest: frozen;
3. controller + analysis implementations: freeze on dev/dummy data only;
4. independent dev hostile tests: pass;
5. protected outcome-access receipt is created;
6. protected bundle generated once;
7. all arms execute on the same bundle;
8. analysis/result objects are written immutably;
9. independent verification and novelty authority run afterward.

Terminal: `CONTAMINATION_EXCLUSIONS_FROZEN__PROTECTED_OUTCOMES_NOT_ACCESSED`.
