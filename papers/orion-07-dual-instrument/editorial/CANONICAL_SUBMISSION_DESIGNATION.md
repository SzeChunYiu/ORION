# Canonical submission designation

> **SUPERSEDED 2026-08-31 by `submission/CANONICAL_SOURCE_DECISION.md` (PR #1957,
> 023864fa8).** That later decision designates the `manuscript/` LaTeX tree as the
> single canonical source for `submission/manuscript.pdf` — #1957 landed the
> Wave-1 branch artifacts "keeping main's newer prose", so the designations on
> this page (including "the `manuscript/` LaTeX tree is removed by this closeout")
> did not survive: the tree was never removed, and its title has been
> "Controller--Host Agreement on Live Research Decisions: A Receipted Benchmark
> and First Measurement" since 3a1a83178 (2026-08-27). The filing package
> `submission/publication-ready-20260831/` (bf2a35750, 2026-09-01) finalizes that
> identity for both routes and includes the official TMLR assets in
> `journal/source.zip`. This lane's bytes are retained unchanged because
> `editorial/final_audit/SHA256SUMS` binds them. Do not file from
> `submission_tmlr/` — see `submission_tmlr/README.md`.
> Supersession recorded 2026-09-03 (tier-B filing-surface closure pass).

**Canonical scientific manuscript source:** `papers/orion-07-dual-instrument/submission_tmlr/main.tex`  
**Canonical bibliography:** `papers/orion-07-dual-instrument/submission_tmlr/references.bib`  
**Canonical review PDF:** `papers/orion-07-dual-instrument/submission_tmlr/main.pdf`  
**Canonical anonymous supplement:** `papers/orion-07-dual-instrument/submission_tmlr/anonymous-review-supplement.zip`  
**Canonical clean source archive:** `papers/orion-07-dual-instrument/submission_tmlr/anonymous-source.zip`

The root Markdown drafts, historical package objects and `manuscript/` LaTeX tree are provenance or superseded working material. They are not submission sources and must not be filed. The superseded `manuscript/` LaTeX tree is removed by this closeout to eliminate a competing build target.

The canonical source uses the official TMLR style at commit `7bf90efe3a0debbba703c05c43f3ff7e4d4a2992` and hides hyperlink borders. Exact final byte bindings live only in the private final-audit manifest.
