# ORION-23 — Empirical Software Engineering submission manifest

**Manuscript:** *Responsibility-Carrying State: Auditable Sufficiency, Reopen Contracts, and Safe State Reuse*
**Venue:** Empirical Software Engineering (Springer)
**Fallback:** Journal of Systems and Software
**Terminal:** `READY_TO_SUBMIT_SECOND_TIER`

---

## 1. Submission files

`manuscript/main.pdf` (6 pp), `manuscript/main.tex`, and `manuscript/sections/`.
The canonical prose is the `.md` files; the `.md.tex` files beside them are their
conversion and are what the build inputs.

## 2. Checks performed

- All six pages inspected as rendered.
- Rendered text carries **zero machine tokens**: four terminal identifiers were
  replaced with plain statements of what they mean, with no claim widened.
- Author block de-tokenised — it read `ORION-P13`, an internal identifier — and
  set to anonymous pending the filer's decision.
- Fixed a source typo the build exposed: the section heading read
  `ResponsibilityCarryingState`, contradicting the paper's own title.
- Binding reconciled last through `supersede_binding.py` (7 paths).

## 3. Build note, and a wrong PDF that was caught

The manuscript used the `markdown` LaTeX package, which needs `texlua` and a
cache matching its own version. No reachable host has any TeX distribution, and
the available engine ships an older `markdown` than the committed cache.

Left in that state the build **silently produced a plausible six-page PDF in
which every section rendered as the References list**. That is worse than no PDF,
so the shims that allowed it were removed and the loud failure restored. The
build now converts the canonical Markdown ahead of time and `\markdownInput`
inputs the conversion, so the source of truth is unchanged and the dependency is
gone.

## 4. What a human must still supply

1. Author names, order and affiliations, and whether to file single- or
   double-blind — EMSE permits either.
2. Journal submission account and the EMSE structured abstract, if required.
3. A data-availability decision consistent with the protected custody model.

## 5. Limitations carried into review

The empirical safety–cost authority is **withheld**: the outcome-entailment
adjudication supersedes the historical protected terminal, and empirical
safety–cost superiority is no longer claimed. The controlled sufficiency-debt
gate is permanently **not met**. The paper reports these as its own results
rather than as caveats, and the top-tier promotion route was closed by a stop
condition before the corpus budget was spent.
