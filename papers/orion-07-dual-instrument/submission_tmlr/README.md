# SUPERSEDED lane — do not file from this directory

**Status (recorded 2026-09-03):** superseded. The ORION-07 filing surface is
`submission/publication-ready-20260831/` (arXiv + TMLR-journal routes, both built
on the canonical `manuscript/` identity; `journal/source.zip` includes the
official `tmlr.sty` (6560 B), `tmlr.bst` (26969 B), and `fancyhdr.sty` in
double-blind anonymous form).

This lane is the 2026-08-29 closeout generation (commit 71607dca7, #1719), built
from the Q3-cited Markdown via `build_tmlr_source.py`, and carries the
three-question case-series title — a different wrapper generation from the
canonical tree, not drifted prose of it (the canonical sections contain no
occurrence of the census numbers this wrapper reports). Its canonical-designation
record (`editorial/CANONICAL_SUBMISSION_DESIGNATION.md`) was reversed one day
later by `submission/CANONICAL_SOURCE_DECISION.md` (#1957, 2026-08-31: the
`manuscript/` LaTeX tree is the single canonical source, main's newer prose
kept), and the filing identity was finalized by bf2a35750 (2026-09-01,
"finalize canonical submission identity and route parity").

Bytes are preserved unchanged because `editorial/final_audit/SHA256SUMS` binds
them at these paths. Precedent: orion-08's superseded pandoc lane
(`papers/orion-08-typed-state/submission/superseded-tmlr-pandoc-lane/README.md`,
#2185).
