# ORION-05 journal-readiness record

**Current terminal:** `INTERNAL_REVIEW_PASS__BOUNDED_CLAIM / SUBMISSION_GATES_OPEN`.

This record follows the same separation used by Paper 1: manuscript quality, evidence authority, reproducibility, and submission operations are different gates.

## Review cycle 1 — blockers found

- **ORION-01-R1, blocking:** V1 said the all-`n` support-two theorem was open even though R6S is now committed.
- **ORION-01-R2, blocking:** V1 elevated a two-trade closed form that QG-5 and QG-7 later refuted at `n=3` and in adversarial hybrid panels.
- **ORION-01-R3, major:** Methods and Results were interleaved, making it difficult to distinguish grammar definitions, referee guarantees, finite-domain evidence, and all-`n` theorem status.
- **ORION-01-R4, major:** the conclusion/claim boundary was stale relative to QG-5b/QG-7/QG-7b/QG-7c.
- **ORION-01-R5, moderate:** programme-history and authority prose interrupted the scientific argument instead of being concentrated in Related Work, Limitations, and Reproducibility.

## Repairs

- Reframed the paper around the durable support-two theorem rather than the obsolete two-trade completeness claim.
- Added the full refutation ladder: split, central borrow, out-of-support phantom borrow, and split+borrow hybrid.
- Separated Methods, Results, Discussion, Related Work, Limitations, Conclusion, Reproducibility, and Ethics/Resources.
- Added an explicit status taxonomy: exact counterexample, complete-domain machine check, finite-panel evidence, and all-`n` machine-checked theorem.
- Preserved V1 and its original claim ledger as history instead of rewriting their provenance.

## Review cycle 2 — skeptical reread

**Scientific validity:** PASS for the bounded unit-objective R6M claim.  
**Claim–warrant alignment:** PASS after removing global two-trade completeness.  
**Methods/evidentiary credibility:** PASS at manuscript level; exact referee and receipt provenance are visible.  
**Reproducibility/reporting:** PASS at manuscript level; commands and canonical receipts are indexed in `REPRODUCE.md`.  
**Internal consistency:** PASS against current main through `c5ba39fef4f25c46de5fb69bf07f50530f4693ca`.  
**Target-journal compliance:** UNRESOLVED because no exact venue/article type is selected.

## Remaining submission gates

- fresh hostile literature/novelty closure dated at submission;
- independent replay of the final cited receipt set on the submission commit;
- compile/render and inspect the final PDF after venue formatting;
- permanent archive/DOI if required by the selected venue.

These are submission operations. They do not authorize a stronger scientific claim.