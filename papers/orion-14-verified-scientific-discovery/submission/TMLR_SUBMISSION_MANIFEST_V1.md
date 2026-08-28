# ORION-14 — TMLR submission manifest

**Manuscript:** *When Verification Axes Can Support Scientific Claims: Identifiability, Attainability, and Non-Compensatory Promotion*
**Venue:** Transactions on Machine Learning Research
**Terminal:** `READY_TO_SUBMIT_SECOND_TIER`
**Built:** 2026-08-28

---

## 1. Files that constitute the submission

| file | role |
|---|---|
| `manuscript/main.pdf` | the submission PDF, 23 pages, TMLR style, anonymous |
| `manuscript/main.tex` | source root |
| `manuscript/sections/*.tex` | included sections, in the order set by `main.tex` |
| `manuscript/figures/`, `manuscript/tables/` | figures and tables as included |
| `manuscript/bibliography.bib` | references |
| `manuscript/tmlr.sty`, `manuscript/tmlr.bst` | venue style |
| `submission/TMLR_COVER_LETTER_V2.md` | note to the Action Editor |

Sections deliberately **excluded** from the submission build, retained on disk:
`P4_X_PROMOTION_AUTHORITY_SECTION` and `12-prospective-source-expansion` are
successor material outside the bounded claim, and
`10-freeze-and-custody-identifiers` is superseded by the custody subsection
inside Data and Code Availability.

## 2. Checks performed on this build

- Compiles with `tectonic` from `manuscript/main.tex`; PDF is 23 pages.
- **Zero undefined cross-references** in the rendered text.
- **Zero author-identifying strings**; the repository slug was removed from Data
  and Code Availability for double-blind review.
- Every page inspected visually as rendered, not judged from source.
- Section order verified in the rendered text: Introduction, Related work,
  Verification-axis identifiability, Non-escalating authority transition,
  Methods, Results, Ablation interpretation, Threat model, Broader impact,
  Conclusion, Data and code availability.
- Content binding reconciled after the final edit, via the sanctioned
  journal-package path; the paper reports zero binding violations.

## 3. What a human must still supply

These cannot be produced from the repository and are the remaining filing inputs:

1. **Author names, order and affiliations** for the camera-ready; the review copy
   stays anonymous.
2. **An OpenReview submission**, which mints the forum id currently stubbed as
   `XXXX` in `main.tex`, and the month/year currently stubbed as `MM`/`YYYY`.
3. **Confirmation of the TMLR submission checklist** on the OpenReview form.
4. **A decision on the repository release timing** — the manuscript promises
   release with a persistent identifier on publication.
5. **Conflict-of-interest and Action Editor exclusions**, if any.

## 4. Known limitations carried into review

Reported in the manuscript and not hidden here: the abstention-superiority
hypothesis is null; several axes are undetermined; comparator arms are
reimplementations rather than the original systems; and the natural-pair and
build-authority shortfalls are unresolved. None of these is repaired by this
packaging pass.
