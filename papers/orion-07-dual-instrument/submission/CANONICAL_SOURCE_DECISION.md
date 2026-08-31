# Canonical manuscript decision — ORION-07

**Decision.** The canonical manuscript is the LaTeX tree
`papers/orion-07-dual-instrument/manuscript/` (`main.tex`, `sections/01`–`09`,
`bibliography.bib`). It is the single source for `submission/manuscript.pdf`.

**Superseded for submission purposes.** `MANUSCRIPT_V2.md`, `MANUSCRIPT_V3.md`,
and `MANUSCRIPT_V3_REFINED.md` remain on disk as the research-side drafts. They
are not the submission source.

**Why the LaTeX tree.** It is the only compilable form, it carries the section
architecture the review record required, and it is the only version that has
been reconciled against the prospective case-series ledger (see below).

**Ledger reconciliation performed in this pass.** The LaTeX manuscript was
stale relative to the paper's own ratified evidence. Specifically:

- The abstract and Limitations stated that the prospectively frozen publication
  plan still required additional frontier-question instances and that the gate
  "remains open".
- The Results section stated that no further benchmark series was present and
  that the result set was "exactly one scored question".

Both statements were false at this revision.
`CLAIM_LEDGER_PROSPECTIVE_CASE_SERIES_2026-08-23.md` records `n_valid = 3`
(V0, R1/QG-19, R2/QG-20), and `check_q3_completion.py` returns
`Q3_COMPLETION_CHECK=PASS` with both replacement instances scored and
independently replayed. The manuscript now reports the series it actually has.

This correction did not weaken any gate. The gate was satisfied by running the
prospectively frozen work, not by lowering the threshold. The two contaminated
candidate slots that the replacements displaced remain visible in the series
audit and are named in the manuscript.

**Claim ceiling unchanged.** The ledger's forbidden interpretations still hold
and are still honoured in the manuscript: no reliability estimate, no claim
that agreement validates diagnosis, no statistical independence between lanes,
no `first` claim. The manuscript additionally now reports the ledger's
`AGREEMENT_NOT_VALIDATION_COUNTEREXAMPLE_OBSERVED` finding, which lowers rather
than raises what the paper asserts.

**Binding status.** No content binding covers `manuscript/` in this paper, so
the edits required no reconciliation. Content-binding state is unchanged at
`BOUND_PARTIAL / PASS`.
