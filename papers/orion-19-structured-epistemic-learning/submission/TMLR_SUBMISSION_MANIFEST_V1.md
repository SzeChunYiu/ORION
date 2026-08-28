# ORION-19 — TMLR submission manifest

**Manuscript:** *When Structure Is the Model: Exact Epistemic Coordinates, Cross-Domain Transfer, and the Limits of Neural Escalation*
**Venue:** Transactions on Machine Learning Research (audited in `TMLR_VENUE_AUDIT_V1.md`)
**Fallback:** Machine Learning (Springer)
**Terminal:** `READY_TO_SUBMIT_SECOND_TIER`

---

## 1. Submission files

`manuscript/main.pdf` (10 pp, TMLR style, anonymous, double-blind), `manuscript/main.tex`
with `sections/`, `figures/`, `tables/`, the generated macro and table files, and
`bibliography`. Cover material is this manifest plus the venue form.

## 2. Checks performed

- Rendered text carries **zero machine tokens** and **zero undefined references**.
- Anonymous: header reads *Under review as submission to TMLR / Paper under
  double-blind review*, with no author or repository identifier.
- Content binding reconciled after the final edit through `supersede_binding.py`,
  which records an immutable supersession rather than refreshing digests silently.

## 3. Build note

The paper ships `build_tmlr_pdf.sh`, which runs `reproduce_final.py`, an audit
pass and three `pdflatex` rounds with `bibtex`. **No TeX distribution with
`pdflatex` is available on any reachable host**, so the committed PDF is a
`tectonic` build of the same sources. Structure, section order and references are
identical; a filer with TeX Live should re-run the canonical script before
uploading.

## 4. What a human must still supply

1. Author names, order and affiliations for the camera-ready.
2. An OpenReview submission, which mints the forum id and the month/year fields.
3. Confirmation of the TMLR checklist.
4. Conflict-of-interest and Action Editor exclusions.

## 5. Limitations carried into review

The escalation result is procedural rather than architectural: the frozen
evidence never produced a residual requiring a richer learned model after
information and explicit-computation controls, which is not a finding that neural
models fail. The transport gate remains **not met**, with five `CANNOT_CHECK`
outcomes retained, and the reminting attack **succeeded**. The added
orbit-coverage analysis is diagnostic and changes no recorded number.
