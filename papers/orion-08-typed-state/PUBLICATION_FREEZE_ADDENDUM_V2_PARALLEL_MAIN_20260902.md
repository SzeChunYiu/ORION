<!-- PRESERVED PARALLEL RECORD (merge, 2026-09-02): this V2 addendum was authored
independently on main (32ca02d79) while the Tier-B lane wrote its own V2 for the
same date. The lane's PUBLICATION_FREEZE_ADDENDUM_V2.md (status
CURRENT_EARNED_CEILING_EXTENDED__REAL_DATA_EXECUTED__BOUNDED_TRANSFER_ONLY,
the strictly narrower transfer bound) governs the filing; this record is retained
verbatim for provenance. No frozen state in either document is regressed. -->

# ORION-08 publication-freeze addendum V2 (additive successor to V1)

**Date:** 2026-09-02
**Status:** `CURRENT_EARNED_CEILING_FROZEN__EXACT_SYNTHETIC_PLUS_BOUNDED_REAL_DATA`
**Supersedes:** the scope sentence of `PUBLICATION_FREEZE_ADDENDUM_V1.md` only. Every authority statement in V1 (terminal `READY_TO_SUBMIT_SECOND_TIER`, target venue TMLR, `scientific_authority_delta = NONE`, retained negatives at equal prominence) is unchanged and re-asserted here. No state regresses; no flag moves.

## Why V2 exists

V1 (2026-08-31) recorded the frozen boundary as "exact-synthetic unchanged" with the
real-system study named as "successor addendum". The governing authority is now
`CLAIM_LEDGER_V4.md`, whose entries O8V4-9, O8V4-10 and O8V4-11 record three
**executed** bounded real-data observational studies that the canonical manuscript
(`manuscript/`, per `submission/CANONICAL_SOURCE_DECISION.md`) reports:

- five OpenML-CC18 datasets (held-out typed-refinement transfer, including the
  retained negative fraction of the oracle-achievable gap on three of five datasets);
- twelve Defects4J projects, 597 faults (helps on ten of twelve; one genuine
  unexplained failure and one no-value project retained);
- 1,533 WorkflowHub records (held-out regret 0.1076 to 0.0137; biconditional
  contrast `CANNOT_CHECK_NO_CONTRAST` because every stratum predicts value).

V1's scope sentence therefore described the state at its own freeze date, not the
current content surface. This addendum records the widened *content* surface without
widening any *claim*: all three studies enter under the descriptive/bounded terms of
O8V4-9..11 ("REAL DATA; SAME-DISTRIBUTION IDENTITY CHECK; NOT EXTERNAL VALIDATION",
"DESCRIPTIVE BOUNDED TRANSFER; NO GENERALIZATION OR SUPERIORITY CLAIM",
"SINGLE-CORPUS RESULT").

## Frozen boundary (V2)

- Scope is exact-synthetic mechanism isolation **plus** the three bounded real-data
  studies above, with their adverse and `CANNOT_CHECK` outcomes retained at equal
  prominence. No deployment claim, no novelty claim, no transfer-superiority claim,
  no rule predicting when transfer will succeed (per the O8V4-13 forbidden list).
- The preserved family-wise multiplicity analysis
  (`analysis/familywise-multiplicity-v1/`) is an exact sign test over published
  win/loss counts with Holm-Bonferroni adjustment across the twelve synthetic
  comparisons. It retains every zero-excluding row and upgrades **no** registered
  disposition; the registered estimand for the twelve comparisons remains the
  unadjusted paired mean, and family-wise-corrected mean-bootstrap claims remain
  forbidden. The manuscript now states this analysis in both directions (protecting
  nulls and positives) instead of one.

## Content surface note

The filing surface is `submission/tier-b-final-20260901/` built from the canonical
LaTeX tree. `submission_tmlr/` is a superseded build lane (its build script pins a
superseded title token) and is marked as such in `submission_tmlr/README.md`; it must
not be used for filing.
