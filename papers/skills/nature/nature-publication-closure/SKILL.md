---
name: nature-publication-closure
description: Close an academic manuscript for filing without changing its scientific authority; resolves source precedence, venue and anonymity rules, reproducibility, package identity, and repository mirrors.
---

# Publication closure

Use this skill after the science is bounded and before any paper is called
submission-ready. It complements writing, polishing, reviewer, statistics,
citation, reference-verification and data-availability skills. It never grants a
scientific claim.

Read `references/closure-contract.md` completely. Then:

1. Resolve one current claim authority and one reader-facing manuscript source.
2. Build an atomic claim/evidence/limitation table, including every null,
   negative, withdrawn, indeterminate and blocked result.
3. Audit abstract, introduction, results and conclusion against that table.
4. Bind an exact venue, article type, requirement URL/access date and artifact
   audience before applying identity rules.
5. Produce and verify the complete filing object: source, PDF, supplements,
   availability/declarations, venue forms, inventory and checksums.
6. Emit one machine-readable current closure state. Mark every contradictory
   visible predecessor historical or point it to the superseding state.
7. Verify any mirror by comparing content, not by asserting that a copy ran.

Stop fail-closed if a requested paper is unhandled, the active authority is
ambiguous, a claim is not supported by bound evidence, a venue requirement is
unknown, or the package/mirror bytes do not match their declaration.

Classify each unresolved item before assigning status:

- `CURRENT_CLAIM_BLOCKER`: the bounded paper lacks evidence for a present claim;
- `PACKAGE_BLOCKER`: a repository-controlled filing artifact or check is missing;
- `HUMAN_FILING_ONLY`: only an author/editor/portal action remains; or
- `SUCCESSOR_SCIENCE_ONLY`: the work belongs to a broader future claim and does
  not block the bounded paper.

Only the first two classes block repository-side package completion. Never turn
the last class into a demand for optional broader experiments.

Required output semantics:

- `READY_TO_FILE` means the repository-controlled filing package passes all
  checks. Portal-only author confirmations, account state and submission IDs are
  listed separately and never synthesized.
- `PACKAGE_COMPLETE__PORTAL_INPUTS_PENDING` is preferred when human-controlled
  metadata remains.
- `CANNOT_CHECK` is an outcome, not a euphemism for success or failure.
- Missing prerequisite artifact *classes* are not observations of attempted
  cases. Report what the denominator actually counts.

For every material closure, preserve a reviewer-audit record and a command that
recomputes the package checks from a clean tree.
