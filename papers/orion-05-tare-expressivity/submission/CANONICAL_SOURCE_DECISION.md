# Canonical manuscript decision — ORION-05

**Decision.** The canonical manuscript is the LaTeX tree
`papers/orion-05-tare-expressivity/manuscript/` (`main.tex`, `sections/01`–`09`,
`bibliography.bib`). It is the single source from which
`submission/manuscript.pdf` is compiled.

**Superseded for submission purposes.** `MANUSCRIPT_V3_REFINED.md` (308 lines)
remains on disk as the research-side draft and as the object referenced by
`CLAIM_LEDGER_V3.md`. It is *not* the submission source.

**Why the LaTeX tree.**

1. It is the only form that compiles to a venue-submittable PDF. The Markdown
   draft has no bibliography, no float handling, and no section structure a
   journal can accept.
2. It already carries the architecture the review record asked for. The
   readiness record's repairs list separate Methods, Results, Discussion,
   Related Work, Limitations, Conclusion, Reproducibility, and
   Ethics/Resources sections; those are exactly the nine files in
   `manuscript/sections/`, and are absent from the Markdown draft.
3. It is strictly the later statement of the argument. The Markdown draft does
   not contain the static-evaluator benchmark result (zero error on 9,547
   compared instances) that the LaTeX Results section reports and that the
   underlying artifact records.

**Consequence for the claim ledger.** `CLAIM_LEDGER_V3.md` names
`MANUSCRIPT_V3_REFINED.md` as canonical. That line is now stale with respect to
submission. The ledger's *claims* (Q1V3-1 … Q1V3-6) are unchanged and continue
to bound this manuscript; only the pointer to the canonical file is superseded
by this decision. No claim was widened, narrowed, or re-evidenced here.

**Binding status.** No `SHA256SUMS` or content manifest in this paper covers
`manuscript/`. The three bindings under `rounds/*/result/` cover result
artifacts only, and are untouched. Editing the manuscript therefore required no
binding reconciliation, and the paper's content-binding state is unchanged at
`BOUND_PARTIAL / PASS`.
