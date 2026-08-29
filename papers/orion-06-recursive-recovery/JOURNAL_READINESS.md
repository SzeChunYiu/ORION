# ORION-06 journal-readiness record

**Current terminal:** `INTERNAL_REVIEW_PASS__METHOD_CLAIM / SUBMISSION_GATES_OPEN`.

## Review cycle 1 — blockers found

- **ORION-02-R1, blocking:** the V1 draft mixed the method contribution with companion scientific claims, creating publication-overlap and ownership ambiguity.
- **ORION-02-R2, blocking:** the novelty sentence asserted that no published pipeline preserved negatives/receipts at this granularity without a submission-date hostile literature closure.
- **ORION-02-R3, major:** programme chronology replaced conventional Methods/Results architecture, forcing readers to infer which protocol features were prespecified and which observations were outcomes.
- **ORION-02-R4, major:** limitations and alternative explanations were effectively compressed into the claim-boundary paragraph.
- **ORION-02-R5, moderate:** infrastructure details were over-weighted relative to the methodological inference they support.

The `ORION-02-R*` strings above are historical review-finding identifiers from the pre-canonical Q2 naming and are retained as provenance; the paper identity is ORION-06.

## Repairs

- Restricted **ORION-06** to the executable negative-recovery methodology; companion-paper results are case-study evidence with explicit ownership boundaries.
- Replaced unverified `first/no published pipeline` language with a dated-literature-search obligation.
- Added separate Methods, Results, Discussion, Related Work, Limitations, Conclusion, Reproducibility, and Ethics/Resources sections.
- Added a claim ledger that distinguishes a demonstrated implementation property from a comparative methodology-effectiveness claim.
- Added the caution that complete receipts make a result attributable/replayable, not scientifically valid by themselves.

## Review cycle 2

**Contribution validity:** PASS as a methods/provenance paper.  
**Claim–warrant alignment:** PASS after removing statistical/general novelty claims.  
**Whole-paper continuity:** PASS.  
**Reproducibility/reporting:** PASS at manuscript level.  
**Cross-paper overlap:** PASS against companion-paper boundaries.  
**Target-journal compliance:** UNRESOLVED; no exact venue/article type selected.

## Current-head science update — 2026-08-29

The additive theorem packet `theory/claim-preserving-recovery-v1/` closes a formal gap without widening the empirical claim. Its controlling terminal is:

`CLAIM_PRESERVING_CAUSAL_COVERAGE_PROVED__CROSS_DOMAIN_RECOVERY_UNTESTED`.

The theorem establishes necessary causal-ancestor coverage for same-identity repair, a no-repair certificate when a failed load-bearing predicate has no admissible repair ancestor, a minimum weighted causal-coverage lower bound, and safe dominance pruning. It also formalizes that changing question/population/estimand/protocol semantics/primary metric/threshold/protected corpus/terminal semantics creates a different claim identity rather than repairing the failed one.

This strengthens the paper's formal recovery contract. It does **not** establish cross-domain productivity or superiority over naive retry, donor repair, debugging tools, or research agents.

## Submission-gate update — 2026-08-29

- **Independent replay:** CLOSED for the two registered ORION-06 headline generators — both replay targets match under canonicalized JSON, and the replay harness is two-sided (unmodified -> `MATCH`, perturbed -> `DIFFERS`, missing generator -> `CANNOT_CHECK`).
- **Receipt-index byte integrity:** CLOSED — 40/40 indexed digests match, with 0 missing and 0 mismatched.
- **Receipt-index-to-final-claim coverage:** `CANNOT_CHECK` — byte integrity does not establish that every final manuscript claim is mapped to an indexed receipt; a claim-to-receipt mapping must be generated against the final submission text.
- **Render inspection:** CLOSED for the currently committed PDF — clipping audit reports one manuscript audited with zero findings. This does not replace a final venue-specific rebuild.
- **Compile gate:** OPEN and venue-dependent; rebuild after venue/style selection.
- **Literature/donor refresh:** OPEN by design until submission date.

## Remaining submission gates

- run the hostile literature/donor refresh at submission and narrow the residual if a close parent is found;
- generate and verify the final **claim-to-receipt** mapping (the 40/40 byte-integrity check is already closed);
- perform the final venue-specific compile/render after source/style selection;
- archive the final evidence snapshot if required by the venue.

No remaining gate licenses stronger claims about methodology effectiveness. A cross-domain Lean/mathlib + Defects4J + exact-ORION recovery benchmark remains a separately named successor, not a prerequisite for filing the bounded methods/provenance paper.
