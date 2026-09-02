# ORION-01 publication-freeze addendum V2 (successor routing/status record)

**Date:** 2026-09-02
**Status:** `ROUTING_AND_STATUS_SUCCESSOR__SCIENCE_CEILING_UNCHANGED`
**Supersedes:** `PUBLICATION_FREEZE_ADDENDUM_V1.md` (2026-08-27) for publication routing and
audit-status bookkeeping only. Every scientific ceiling, frozen boundary, adverse result,
and content-surface rule in V1 remains binding and unchanged; V1 is not edited. This
addendum grants no new claim authority (`paper_authority_delta = NONE`).

## 2026-09-02 decisions recorded

1. **Venue re-route (issue SzeChunYiu/ORION-paper#78, decision (b)).** ORION-01 is re-routed
   to a quantum-information-and-computation class journal venue, with the arXiv `quant-ph`
   preprint posted first. This supersedes for routing only the 2026-09-01 *Quantum*
   resolution in `submission/tier-b-closure-20260901/VENUE_RESOLUTION.md` (retained as
   history). ORION-05 files separately as the companion paper rather than being absorbed;
   see item 4.
2. **Finding B-F4 closed by narrowing (2026-09-02).** The V2-era abstract phrase "arbitrarily
   loose as a description of the compiler it certifies" was already absent from all V4
   surfaces; on 2026-09-02 the V4 abstract was further narrowed so the claim matches the
   one-rule rank-only scope and cites the corollary's true-by-construction status
   explicitly. Corollary 5 and its proof were not touched. No claim was widened.
   - Old: "We then formalize the same binary deletion rule as a rank-only
     certifiable-support calculus and compare its budget with intrinsic optimal support
     under fixed objectives and fixed support statistics."
   - New: "We then formalize the same binary deletion rule as a rank-only
     certifiable-support calculus whose only transition is that deletion rule, and compare
     its budget with intrinsic optimal support under fixed objectives and fixed support
     statistics."
   - Old: "The separation is relative to the declared proof language and does not imply a
     lower bound for richer systems, a production-compiler transfer, or a physical quantum
     advantage."
   - New: "Because the calculus contains exactly one rule, the exactness of its budget holds
     by construction within that one-rule system rather than as a bound over alternative
     certificate rules. The separation is therefore relative to the declared one-rule proof
     language and does not imply a lower bound for richer systems, a production-compiler
     transfer, or a physical quantum advantage."
   Also added to §13 (single-author cross-cutting requirement): "This work belongs to a
   single-author research programme using AI assistance, so the verification described here
   is author-side throughout and lacks the independent perspective of multi-author or
   externally replicated work."
   Consequence: `submission/tier-b-final-20260901/` PDFs are stale against
   `MANUSCRIPT_V4.md` and must be re-rendered before filing (parent-lane build step).
3. **Audit-header statuses recorded (2026-09-02).** Additive dated V4-status headers were
   prepended to `INDEPENDENT_PROOF_REVIEW_V1.md` (all A-F1..A-F9, B-F1..B-F7 closed in V4;
   B-F4 closed 2026-09-02 by item 2) and `NOVELTY_AUDIT_V1.md` (contribution-demotion,
   A1-phrasing, B4-scoping and naming recommendations closed in V4; §5 external
   verification items open by design). Audit bodies unchanged.
4. **ORION-05 companion filing and merge-coverage audit.** ORION-05 files separately with
   its own ledger; coverage of its V4 claims by ORION-01's V4 surfaces is audited in
   `papers/orion-05-tare-expressivity/MERGE_COVERAGE_AUDIT_20260902.md`. This supersedes for
   routing only the 2026-09-01 absorption terminal in `CLAIM_LEDGER_V4.md`'s submission
   rule and `submission/tier-b-closure-20260901/ORION05_MERGE_COVERAGE_AUDIT.md`; static-
   evaluator and regime-refutation records remain owned by the merged ORION-09/10 object.
5. **QIC-class filing artifacts (2026-09-02).** `COVER_LETTER_QIC_V1.md` and
   `SUBMISSION_CHECKLIST_QIC.md` (this directory) were created; portal facts remain
   `HUMAN_FILING_ONLY` placeholders.

## Files touched on 2026-09-02

- `papers/orion-01-certificate-realization/MANUSCRIPT_V4.md` (abstract narrowed; §13 sentence added)
- `papers/orion-01-certificate-realization/INDEPENDENT_PROOF_REVIEW_V1.md` (header only)
- `papers/orion-01-certificate-realization/NOVELTY_AUDIT_V1.md` (header only)
- `papers/orion-01-certificate-realization/COVER_LETTER_QIC_V1.md` (new)
- `papers/orion-01-certificate-realization/SUBMISSION_CHECKLIST_QIC.md` (new)
- `papers/orion-05-tare-expressivity/MERGE_COVERAGE_AUDIT_20260902.md` (new)
- `papers/orion-05-tare-expressivity/PUBLICATION_FREEZE_ADDENDUM_V2.md` (new successor)
